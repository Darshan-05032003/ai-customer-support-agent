#!/usr/bin/env python3
"""
Data-driven intent discovery from AmazonHelp customer messages.

Analyzes 162k customer messages to identify natural support intent categories.
"""

import sys
from pathlib import Path
import json
import numpy as np
import pandas as pd
from collections import Counter
import re

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import MiniBatchKMeans
    from sklearn.metrics import silhouette_score
except ImportError:
    print("Installing scikit-learn...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "scikit-learn"])
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import MiniBatchKMeans
    from sklearn.metrics import silhouette_score


def load_customer_messages(path):
    """Load all customer messages."""
    messages = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            record = json.loads(line)
            messages.append(record)
    return messages


def normalize_text(text):
    """Normalize text for analysis."""
    text = text.lower()
    text = re.sub(r'@\w+', '', text)  # Remove mentions
    text = re.sub(r'http\S+', '', text)  # Remove URLs
    text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
    return text.strip()


def extract_keywords(texts, top_n=100):
    """Extract top keywords using TF-IDF."""
    vectorizer = TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 2),
        min_df=5,
        max_df=0.7,
        stop_words='english'
    )

    tfidf_matrix = vectorizer.fit_transform(texts)

    # Get average TF-IDF scores
    scores = np.asarray(tfidf_matrix.mean(axis=0)).flatten()
    feature_names = vectorizer.get_feature_names_out()

    # Get top features
    top_indices = scores.argsort()[-top_n:][::-1]
    top_keywords = [(feature_names[i], scores[i]) for i in top_indices]

    return top_keywords, vectorizer, tfidf_matrix


def cluster_messages(texts, vectorizer, tfidf_matrix, k_values=[8, 10, 12, 15]):
    """Try multiple cluster counts and evaluate."""
    results = {}

    for k in k_values:
        print(f"  Clustering with k={k}...")

        kmeans = MiniBatchKMeans(
            n_clusters=k,
            random_state=42,
            n_init=10,
            batch_size=1000
        )

        labels = kmeans.fit_predict(tfidf_matrix)

        # Silhouette score
        silhouette_avg = silhouette_score(tfidf_matrix, labels, sample_size=5000)

        # Cluster sizes
        cluster_sizes = Counter(labels)

        results[k] = {
            'model': kmeans,
            'labels': labels,
            'silhouette': silhouette_avg,
            'cluster_sizes': cluster_sizes
        }

        print(f"    Silhouette: {silhouette_avg:.3f}")
        print(f"    Cluster sizes: {sorted(cluster_sizes.values())}")

    return results


def extract_cluster_examples(texts, labels, k, num_examples=10):
    """Extract representative examples from each cluster."""
    clusters = {}

    for i in range(k):
        cluster_indices = np.where(labels == i)[0]

        if len(cluster_indices) > 0:
            # Get examples closest to center
            selected = np.random.choice(cluster_indices, size=min(num_examples, len(cluster_indices)), replace=False)
            examples = [texts[idx] for idx in selected]

            clusters[i] = {
                'size': len(cluster_indices),
                'examples': examples
            }

    return clusters


def analyze_text_patterns(messages_df):
    """Analyze common patterns in customer messages."""
    texts = messages_df['text'].tolist()

    print("\n" + "=" * 70)
    print("TEXT PATTERN ANALYSIS")
    print("=" * 70)

    # Common starting phrases
    print("\nMost common message starts:")
    starts = []
    for text in texts:
        if text.strip():
            start = text.split()[0] if text.split() else ""
            if len(start) > 2:
                starts.append(start.lower())

    for word, count in Counter(starts).most_common(20):
        print(f"  {word:20s}: {count:>6,}")

    # Question vs statement analysis
    questions = sum(1 for t in texts if '?' in t)
    statements = len(texts) - questions

    print(f"\nQuestion vs Statement:")
    print(f"  Questions (with ?): {questions:,} ({100*questions/len(texts):.1f}%)")
    print(f"  Statements: {statements:,} ({100*statements/len(texts):.1f}%)")

    # Message length distribution
    lengths = [len(t.split()) for t in texts]
    print(f"\nMessage length (words):")
    print(f"  Min: {min(lengths)}, Max: {max(lengths)}, Mean: {np.mean(lengths):.1f}, Median: {np.median(lengths):.0f}")


def main():
    print("=" * 70)
    print("PHASE 4 - DATA-DRIVEN INTENT DISCOVERY")
    print("=" * 70)

    # Load messages
    print("\nLoading customer messages...")
    messages = load_customer_messages("data/processed/amazonhelp_customer_messages.jsonl")
    print(f"Loaded {len(messages):,} customer messages")

    # Create DataFrame
    messages_df = pd.DataFrame(messages)

    # Normalize text
    print("\nNormalizing text...")
    normalized_texts = [normalize_text(text) for text in messages_df['text']]

    # Analyze patterns
    analyze_text_patterns(messages_df)

    # Extract keywords
    print("\n" + "=" * 70)
    print("KEYWORD/PHRASE ANALYSIS")
    print("=" * 70)

    top_keywords, vectorizer, tfidf_matrix = extract_keywords(normalized_texts, top_n=150)

    print("\nTop 50 keywords/phrases by TF-IDF:")
    for keyword, score in top_keywords[:50]:
        print(f"  {keyword:40s} {score:.4f}")

    # Clustering
    print("\n" + "=" * 70)
    print("INTENT CLUSTERING")
    print("=" * 70)

    print("\nTesting multiple cluster counts...")
    results = cluster_messages(normalized_texts, vectorizer, tfidf_matrix, k_values=[8, 10, 12, 15])

    # Choose best based on silhouette score
    best_k = max(results.keys(), key=lambda k: results[k]['silhouette'])
    print(f"\nBest silhouette score: k={best_k} ({results[best_k]['silhouette']:.3f})")

    # Extract examples from best clustering
    best_result = results[best_k]
    clusters = extract_cluster_examples(normalized_texts, best_result['labels'], best_k, num_examples=15)

    print(f"\n" + "=" * 70)
    print(f"FINAL CLUSTERING: {best_k} CLUSTERS")
    print("=" * 70)

    for cluster_id in sorted(clusters.keys()):
        cluster_info = clusters[cluster_id]
        print(f"\nCluster {cluster_id}: {cluster_info['size']:,} messages ({100*cluster_info['size']/len(messages):.1f}%)")
        print(f"  Examples:")
        for ex in cluster_info['examples'][:5]:
            print(f"    - {ex[:100]}")

    # Save discovery report
    discovery_report = {
        'total_messages_analyzed': len(messages),
        'k_values_tested': list(results.keys()),
        'silhouette_scores': {k: results[k]['silhouette'] for k in results.keys()},
        'best_k': best_k,
        'best_silhouette': results[best_k]['silhouette'],
        'cluster_sizes': {i: clusters[i]['size'] for i in clusters.keys()},
        'top_keywords': [(kw, float(score)) for kw, score in top_keywords[:100]],
        'methodology': 'TF-IDF + MiniBatchKMeans with silhouette evaluation',
        'seed': 42
    }

    with open("reports/intent_discovery_technical.json", 'w') as f:
        json.dump(discovery_report, f, indent=2)

    print("\n✓ Discovery report saved to reports/intent_discovery_technical.json")
    print("=" * 70)
    print("\nNext: Manually review clusters and define taxonomy based on this analysis.")


if __name__ == "__main__":
    main()

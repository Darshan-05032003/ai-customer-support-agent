#!/usr/bin/env python3
"""
Intent discovery from AmazonHelp customer messages using sampling.

Uses TF-IDF and keyword analysis on a representative sample.
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from collections import Counter, defaultdict
import re
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.loaders import load_raw_data, validate_raw_data, get_brand_tweets


def normalize_text(text):
    """Simple text normalization for analysis."""
    text = text.lower()
    text = re.sub(r'@\w+', '', text)  # Remove mentions
    text = re.sub(r'http\S+', '', text)  # Remove URLs
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
    return text.split()


def extract_customer_messages_sample(df, brand_name="AmazonHelp", sample_size=5000):
    """Extract customer messages involved with brand conversations (sampled)."""

    # Get brand tweets
    brand_tweets = df[(df['inbound'] == False) & (df['author_id'] == brand_name)]
    brand_ids = set(brand_tweets['tweet_id'].astype(int).values)

    # Find customers responding to brand
    customers = df[
        (df['inbound'] == True) &
        (df['in_response_to_tweet_id'].notna()) &
        (df['in_response_to_tweet_id'].isin(brand_ids))
    ]

    print(f"Total customer messages in {brand_name} conversations: {len(customers):,}")

    # Sample
    if len(customers) > sample_size:
        sampled = customers.sample(n=sample_size, random_state=42)
        print(f"Using sample of {sample_size:,} for analysis")
    else:
        sampled = customers

    return sampled['text'].tolist()


def analyze_keywords(messages, top_n=100):
    """Extract common keywords and phrases."""

    all_words = []
    bigrams = Counter()
    trigrams = Counter()

    for msg in messages:
        tokens = normalize_text(msg)
        all_words.extend(tokens)

        # Bigrams
        for i in range(len(tokens) - 1):
            bigrams[' '.join(tokens[i:i+2])] += 1

        # Trigrams
        for i in range(len(tokens) - 2):
            trigrams[' '.join(tokens[i:i+3])] += 1

    word_freq = Counter(all_words)

    # Filter common stopwords
    stopwords = {'order', 'amazon', 'help', 'the', 'a', 'an', 'and', 'or', 'is', 'are', 'was', 'were', 'to', 'for', 'with', 'on', 'my', 'i', 'me', 'please', 'thanks', 'thank', 'you', 'your'}

    filtered_words = {w: c for w, c in word_freq.most_common(top_n * 2) if w not in stopwords and len(w) > 2}
    filtered_bigrams = {p: c for p, c in bigrams.most_common(top_n) if len(p.split()) == 2}
    filtered_trigrams = {p: c for p, c in trigrams.most_common(top_n) if len(p.split()) == 3}

    return {
        'top_words': dict(sorted(filtered_words.items(), key=lambda x: x[1], reverse=True)[:50]),
        'top_bigrams': dict(sorted(filtered_bigrams.items(), key=lambda x: x[1], reverse=True)[:30]),
        'top_trigrams': dict(sorted(filtered_trigrams.items(), key=lambda x: x[1], reverse=True)[:30]),
    }


def discover_intent_candidates(messages, keywords_data):
    """Discover intent candidates based on keyword patterns."""

    intent_patterns = {
        'order_status': {
            'keywords': ['order', 'status', 'shipped', 'delivery', 'when', 'track', 'where'],
            'examples': []
        },
        'late_delivery': {
            'keywords': ['late', 'delayed', 'not', 'arrived', 'missing', 'received', 'where'],
            'examples': []
        },
        'missing_damaged_item': {
            'keywords': ['missing', 'damaged', 'broken', 'not', 'received', 'incomplete', 'wrong'],
            'examples': []
        },
        'refund_return': {
            'keywords': ['refund', 'return', 'money', 'back', 'exchange', 'wrong', 'defective'],
            'examples': []
        },
        'payment_billing': {
            'keywords': ['payment', 'charge', 'card', 'billing', 'amount', 'price', 'cost'],
            'examples': []
        },
        'account_login': {
            'keywords': ['account', 'login', 'password', 'access', 'email', 'verify', 'confirm'],
            'examples': []
        },
        'subscription_service': {
            'keywords': ['prime', 'subscription', 'membership', 'cancel', 'subscribe', 'service'],
            'examples': []
        },
        'product_information': {
            'keywords': ['product', 'available', 'stock', 'size', 'color', 'specs', 'details'],
            'examples': []
        },
        'shipping_address': {
            'keywords': ['address', 'ship', 'delivery', 'location', 'change', 'update', 'zip'],
            'examples': []
        },
        'technical_issue': {
            'keywords': ['app', 'website', 'error', 'not', 'working', 'problem', 'issue'],
            'examples': []
        },
    }

    # Classify messages by intent
    unclassified = []

    for msg in messages[:500]:  # Analyze first 500 for examples
        tokens = normalize_text(msg)
        token_set = set(tokens)

        best_intent = None
        best_score = 0

        for intent, patterns in intent_patterns.items():
            score = sum(1 for kw in patterns['keywords'] if kw in token_set)
            if score > best_score:
                best_score = score
                best_intent = intent

        if best_intent and best_score > 0:
            intent_patterns[best_intent]['examples'].append(msg[:100])
        else:
            unclassified.append(msg)

    return intent_patterns, unclassified


def main():
    print("=" * 70)
    print("PHASE 2 - INTENT DISCOVERY (SAMPLE-BASED)")
    print("=" * 70)

    # Load data
    print("\nLoading dataset...")
    df = load_raw_data()
    validate_raw_data(df)

    # Extract customer messages
    print("\nExtracting customer messages...")
    messages = extract_customer_messages_sample(df, "AmazonHelp", sample_size=5000)

    print(f"Sample size: {len(messages):,} messages")
    print(f"Avg message length: {np.mean([len(m) for m in messages]):.0f} chars")

    # Analyze keywords
    print("\nAnalyzing keywords...")
    keywords_data = analyze_keywords(messages)

    print("\nTop keywords:")
    for word, count in list(keywords_data['top_words'].items())[:20]:
        print(f"  {word:20s} {count:>4d}")

    # Discover intents
    print("\nDiscovering intent candidates...")
    intents, unclassified = discover_intent_candidates(messages, keywords_data)

    # Report
    print("\n" + "=" * 70)
    print("DISCOVERED INTENTS")
    print("=" * 70)

    total_classified = sum(len(p['examples']) for p in intents.values())
    print(f"\nTotal classified examples: {total_classified}")
    print(f"Unclassified: {len(unclassified)}")

    for intent_name, data in sorted(intents.items()):
        count = len(data['examples'])
        if count > 0:
            print(f"\n{intent_name}:")
            print(f"  Examples: {count}")
            if data['examples']:
                print(f"  Sample: {data['examples'][0][:80]}...")

    # Save taxonomy
    taxonomy = {
        "version": "1.0",
        "brand": "AmazonHelp",
        "discovery_method": "sample_based_keyword_analysis",
        "sample_size": len(messages),
        "intents": []
    }

    for intent_name, data in sorted(intents.items()):
        if len(data['examples']) > 0:  # Only include intents with examples
            intent_obj = {
                "id": intent_name,
                "name": intent_name.replace('_', ' ').title(),
                "keywords": data['keywords'],
                "example_count": len(data['examples']),
                "sample_messages": data['examples'][:3]
            }
            taxonomy['intents'].append(intent_obj)

    # Export taxonomy
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)

    taxonomy_path = output_dir / "intent_taxonomy.json"
    with open(taxonomy_path, 'w') as f:
        json.dump(taxonomy, f, indent=2)

    print(f"\n✓ Taxonomy saved to {taxonomy_path}")
    print(f"✓ {len(taxonomy['intents'])} intents discovered")


if __name__ == "__main__":
    main()

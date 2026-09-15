#!/usr/bin/env python3
"""
Semantic intent discovery using keyword patterns and manual grouping.

Instead of relying on clustering (which fails on short text),
use domain knowledge + TF-IDF to identify natural intent categories.
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
except ImportError:
    print("Installing scikit-learn...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "scikit-learn"])
    from sklearn.feature_extraction.text import TfidfVectorizer


def load_customer_messages(path):
    """Load all customer messages."""
    messages = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            record = json.loads(line)
            messages.append(record['text'])
    return messages


def normalize_text(text):
    """Normalize text for analysis."""
    text = text.lower()
    text = re.sub(r'@\w+', '', text)  # Remove mentions
    text = re.sub(r'http\S+', '', text)  # Remove URLs
    text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
    return text.strip()


def extract_tfidf_features(texts, top_n=200):
    """Extract top TF-IDF features."""
    vectorizer = TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 2),
        min_df=10,
        max_df=0.7,
        stop_words='english'
    )

    tfidf_matrix = vectorizer.fit_transform(texts)
    scores = np.asarray(tfidf_matrix.mean(axis=0)).flatten()
    feature_names = vectorizer.get_feature_names_out()

    top_indices = scores.argsort()[-top_n:][::-1]
    top_features = [(feature_names[i], scores[i]) for i in top_indices]

    return top_features


# Define intent categories with semantic patterns
INTENT_PATTERNS = {
    'ORDER_STATUS': {
        'keywords': ['order', 'where', 'status', 'tracking', 'track', 'number', 'locate', 'find', 'check'],
        'phrases': ['order status', 'where is my', 'tracking number', 'order number', 'check order', 'find order'],
        'description': 'Customer inquiring about status, tracking, or location of an order'
    },
    'DELIVERY_ISSUE': {
        'keywords': ['delivery', 'delivered', 'late', 'delayed', 'not received', 'didn\'t arrive', 'missing'],
        'phrases': ['not delivered', 'late delivery', 'delayed delivery', 'where delivery', 'delivery late', 'delivery date'],
        'description': 'Customer reporting late, missing, or problematic delivery'
    },
    'DAMAGED_ITEM': {
        'keywords': ['damaged', 'broken', 'defective', 'broken', 'bent', 'cracked', 'torn', 'ripped'],
        'phrases': ['item damaged', 'arrived damaged', 'broken item', 'defective product'],
        'description': 'Customer reporting damaged, defective, or broken product'
    },
    'REFUND_RETURN': {
        'keywords': ['refund', 'return', 'money back', 'refunded', 'reimbursement', 'credit'],
        'phrases': ['want refund', 'refund status', 'return item', 'return process', 'how return'],
        'description': 'Customer requesting refund, return, or inquiring about return process'
    },
    'BILLING_PAYMENT': {
        'keywords': ['charge', 'charged', 'payment', 'billing', 'bill', 'invoice', 'paid', 'price'],
        'phrases': ['double charged', 'wrong amount', 'price', 'charge', 'billing issue'],
        'description': 'Customer reporting billing errors, charges, or payment issues'
    },
    'ACCOUNT_LOGIN': {
        'keywords': ['account', 'password', 'login', 'log in', 'access', 'sign in', 'password reset', 'email'],
        'phrases': ['can\'t login', 'reset password', 'account access', 'forgot password', 'login issue'],
        'description': 'Customer having account access, login, or password issues'
    },
    'PRIME_SUBSCRIPTION': {
        'keywords': ['prime', 'membership', 'subscription', 'cancel', 'unsubscribe', 'renew', 'benefit'],
        'phrases': ['prime member', 'cancel prime', 'prime subscription', 'cancel membership'],
        'description': 'Customer inquiring about or managing Prime membership or subscription'
    },
    'PRODUCT_INFORMATION': {
        'keywords': ['information', 'details', 'description', 'specs', 'specifications', 'how use', 'manual'],
        'phrases': ['product info', 'product details', 'how to use', 'product description'],
        'description': 'Customer requesting product information, specifications, or usage details'
    },
    'SHIPPING_ADDRESS': {
        'keywords': ['address', 'shipping', 'ship to', 'change address', 'wrong address', 'deliver to'],
        'phrases': ['shipping address', 'wrong address', 'change address', 'ship to'],
        'description': 'Customer providing, changing, or reporting issues with shipping address'
    },
    'TECHNICAL_ISSUE': {
        'keywords': ['technical', 'bug', 'error', 'broken', 'website', 'app', 'crash', 'slow'],
        'phrases': ['website issue', 'app problem', 'technical issue', 'website down'],
        'description': 'Customer reporting technical problems with website, app, or service'
    },
    'CUSTOMER_SERVICE_COMPLAINT': {
        'keywords': ['complaint', 'complaint', 'frustrated', 'unhappy', 'disappointing', 'poor service'],
        'phrases': ['customer service', 'poor service', 'complaint', 'very unhappy'],
        'description': 'Customer expressing dissatisfaction with service or making complaint'
    },
    'GENERAL_INQUIRY': {
        'keywords': ['help', 'question', 'how', 'what', 'why', 'when', 'where', 'need'],
        'phrases': ['need help', 'can help', 'quick question', 'help please'],
        'description': 'General customer inquiry or request for help'
    }
}


def categorize_by_patterns(text):
    """Categorize a message by keyword/phrase patterns."""
    text_lower = text.lower()
    scores = {}

    for intent, patterns in INTENT_PATTERNS.items():
        intent_score = 0

        # Check for phrases (higher weight)
        for phrase in patterns['phrases']:
            if phrase in text_lower:
                intent_score += 3

        # Check for keywords
        for keyword in patterns['keywords']:
            if keyword in text_lower:
                intent_score += 1

        scores[intent] = intent_score

    top_intent = max(scores, key=scores.get)
    top_score = scores[top_intent]

    if top_score > 0:
        return top_intent, top_score
    else:
        return 'GENERAL_INQUIRY', 0


def main():
    print("=" * 70)
    print("PHASE 4 - SEMANTIC INTENT DISCOVERY")
    print("=" * 70)

    # Load messages
    print("\nLoading customer messages...")
    texts = load_customer_messages("data/processed/amazonhelp_customer_messages.jsonl")
    print(f"Loaded {len(texts):,} customer messages")

    # Normalize
    print("Normalizing text...")
    normalized_texts = [normalize_text(t) for t in texts]

    # Extract TF-IDF features
    print("\nExtracting TF-IDF features...")
    top_features = extract_tfidf_features(normalized_texts, top_n=200)

    print("Top 50 features by TF-IDF:")
    for feature, score in top_features[:50]:
        print(f"  {feature:40s} {score:.4f}")

    # Categorize all messages
    print("\n" + "=" * 70)
    print("CATEGORIZING MESSAGES BY SEMANTIC PATTERNS")
    print("=" * 70)

    intent_counts = Counter()
    intent_examples = {intent: [] for intent in INTENT_PATTERNS.keys()}
    intent_examples['UNKNOWN'] = []

    print("\nProcessing 162,562 messages...")
    for i, text in enumerate(normalized_texts):
        intent, score = categorize_by_patterns(text)
        intent_counts[intent] += 1

        # Save examples (first 5 per intent)
        if len(intent_examples[intent]) < 5:
            intent_examples[intent].append(text[:120])

        if (i + 1) % 50000 == 0:
            print(f"  {i+1:,} messages processed...")

    # Report distribution
    print("\n" + "=" * 70)
    print("INTENT DISTRIBUTION")
    print("=" * 70)

    total = len(texts)
    for intent in sorted(intent_counts.keys(), key=lambda x: intent_counts[x], reverse=True):
        count = intent_counts[intent]
        pct = 100.0 * count / total
        pattern_def = INTENT_PATTERNS.get(intent, {})
        desc = pattern_def.get('description', 'Unknown')

        print(f"\n{intent}: {count:,} messages ({pct:.1f}%)")
        print(f"  Definition: {desc}")
        print(f"  Examples:")
        for ex in intent_examples[intent][:3]:
            print(f"    - {ex}")

    # Save discovery report
    discovery_report = {
        'methodology': 'Semantic pattern-based intent discovery',
        'total_messages_analyzed': len(texts),
        'intent_categories': {},
        'seed': 42
    }

    for intent in sorted(intent_counts.keys()):
        count = intent_counts[intent]
        pattern_def = INTENT_PATTERNS.get(intent, {})

        discovery_report['intent_categories'][intent] = {
            'count': count,
            'percentage': round(100.0 * count / total, 1),
            'definition': pattern_def.get('description', 'Unknown'),
            'keywords': pattern_def.get('keywords', []),
            'phrases': pattern_def.get('phrases', []),
            'examples': intent_examples[intent][:5]
        }

    with open("reports/intent_discovery.json", 'w') as f:
        json.dump(discovery_report, f, indent=2)

    print("\n" + "=" * 70)
    print("✓ Intent discovery report saved to reports/intent_discovery.json")
    print("=" * 70)

    # Summary statistics
    print("\nSummary:")
    print(f"  Total intents identified: {len(intent_counts)}")
    print(f"  Total messages categorized: {sum(intent_counts.values()):,}")
    print(f"  Top intent: {intent_counts.most_common(1)[0][0]} ({intent_counts.most_common(1)[0][1]:,} messages)")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Create a diverse Golden Evaluation Set candidate pool.

Selects ~250 conversations representing the full range of support scenarios.
"""

import sys
from pathlib import Path
import json
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))


def load_conversations(conv_path):
    """Load all conversations."""
    conversations = {}
    with open(conv_path, 'r', encoding='utf-8') as f:
        for line in f:
            record = json.loads(line)
            conv_id = record['conversation_id']
            conversations[conv_id] = record
    return conversations


def categorize_conversations(conversations):
    """Categorize conversations for diverse sampling."""
    categories = {
        'short_2_msgs': [],        # Very short
        'short_3_msgs': [],
        'medium_4_7_msgs': [],     # Medium
        'long_8_15_msgs': [],      # Long
        'very_long_16plus_msgs': [], # Very long
        'multi_customer_2plus': [],  # Multiple customer turns
        'single_brand_response': [], # Only 1 brand message
        'multi_brand_response': [],  # 2+ brand messages
        'many_customer_turns_5plus': [], # 5+ customer messages
    }

    for conv_id, conv in conversations.items():
        messages = conv['messages']
        msg_count = len(messages)
        customer_count = sum(1 for m in messages if m['role'] == 'customer')
        brand_count = sum(1 for m in messages if m['role'] == 'brand')

        # Length categories
        if msg_count == 2:
            categories['short_2_msgs'].append(conv_id)
        elif msg_count == 3:
            categories['short_3_msgs'].append(conv_id)
        elif 4 <= msg_count <= 7:
            categories['medium_4_7_msgs'].append(conv_id)
        elif 8 <= msg_count <= 15:
            categories['long_8_15_msgs'].append(conv_id)
        else:
            categories['very_long_16plus_msgs'].append(conv_id)

        # Customer participation
        if customer_count >= 2:
            categories['multi_customer_2plus'].append(conv_id)

        # Brand response patterns
        if brand_count == 1:
            categories['single_brand_response'].append(conv_id)
        else:
            categories['multi_brand_response'].append(conv_id)

        # Heavy customer engagement
        if customer_count >= 5:
            categories['many_customer_turns_5plus'].append(conv_id)

    return categories


def sample_from_categories(categories, target_count=250, seed=42):
    """Deterministically sample diverse candidates."""
    np.random.seed(seed)

    # Define sampling strategy
    samples = {
        'short_2_msgs': int(0.05 * target_count),  # 12
        'short_3_msgs': int(0.10 * target_count),  # 25
        'medium_4_7_msgs': int(0.30 * target_count),  # 75
        'long_8_15_msgs': int(0.30 * target_count),  # 75
        'very_long_16plus_msgs': int(0.15 * target_count),  # 38
        'multi_customer_2plus': int(0.35 * target_count),  # 88 (overlaps)
        'single_brand_response': int(0.20 * target_count),  # 50
        'multi_brand_response': int(0.45 * target_count),  # 113
        'many_customer_turns_5plus': int(0.15 * target_count),  # 38
    }

    selected = set()

    # Sample from each category
    for category, count in samples.items():
        available = [c for c in categories[category] if c not in selected]
        if available:
            to_select = min(count, len(available))
            sampled = np.random.choice(available, size=to_select, replace=False)
            selected.update(sampled)

    # If we haven't reached target, sample additional from largest categories
    if len(selected) < target_count:
        remaining_needed = target_count - len(selected)
        available = [c for c in categories['medium_4_7_msgs'] if c not in selected]
        to_add = min(remaining_needed, len(available))
        if to_add > 0:
            sampled = np.random.choice(available, size=to_add, replace=False)
            selected.update(sampled)

    return selected


def main():
    print("=" * 70)
    print("PHASE 3 - GOLDEN SET CANDIDATE SELECTION")
    print("=" * 70)

    # Load conversations
    conv_path = Path("data/processed/amazonhelp_conversations.jsonl")
    print(f"\nLoading conversations from {conv_path}...")
    conversations = load_conversations(str(conv_path))
    print(f"Loaded {len(conversations):,} conversations")

    # Categorize
    print("\nCategorizing conversations...")
    categories = categorize_conversations(conversations)

    for cat, convs in categories.items():
        print(f"  {cat:30s}: {len(convs):>6,}")

    # Sample
    print("\nSampling diverse candidates (deterministic, seed=42)...")
    target = 250
    selected_ids = sample_from_categories(categories, target_count=target, seed=42)
    print(f"Selected {len(selected_ids):,} candidates (target: {target})")

    # Create candidate records
    candidates = []
    for conv_id in sorted(selected_ids):
        conv = conversations[conv_id]
        messages = conv['messages']

        # Count customer and brand messages
        customer_count = sum(1 for m in messages if m['role'] == 'customer')
        brand_count = sum(1 for m in messages if m['role'] == 'brand')

        candidate = {
            'conversation_id': conv_id,
            'brand': conv['brand'],
            'messages': messages,
            'metadata': {
                'total_messages': len(messages),
                'customer_messages': customer_count,
                'brand_messages': brand_count,
            },
            'annotation': {
                'primary_intent': None,
                'secondary_intent': None,
                'is_ambiguous': None,
                'escalation_required': None,
                'annotator_notes': None
            }
        }
        candidates.append(candidate)

    # Export candidates
    output_dir = Path("data/evaluation")
    output_dir.mkdir(parents=True, exist_ok=True)

    candidates_path = output_dir / "golden_candidates.jsonl"
    print(f"\nExporting {len(candidates):,} candidates to {candidates_path}...")

    with open(candidates_path, 'w', encoding='utf-8') as f:
        for candidate in candidates:
            f.write(json.dumps(candidate, ensure_ascii=False) + '\n')

    print(f"  ✓ Exported {len(candidates):,} candidate records")

    # Create template
    template = {
        "conversation_id": "conv_XXXXX",
        "brand": "AmazonHelp",
        "messages": [
            {
                "tweet_id": 12345,
                "author_id": "customer_id",
                "role": "customer",
                "timestamp": "Wed Oct 11 06:55:44 +0000 2017",
                "text": "...",
                "parent_tweet_id": 12344
            }
        ],
        "metadata": {
            "total_messages": 5,
            "customer_messages": 3,
            "brand_messages": 2
        },
        "annotation": {
            "primary_intent": "order_status",
            "secondary_intent": None,
            "is_ambiguous": False,
            "escalation_required": False,
            "annotator_notes": "Customer had simple question, resolved in 2 exchanges"
        }
    }

    template_path = output_dir / "golden_annotation_template.jsonl"
    with open(template_path, 'w') as f:
        f.write(json.dumps(template, ensure_ascii=False) + '\n')

    print(f"  ✓ Created annotation template at {template_path}")

    print("\n" + "=" * 70)
    print("GOLDEN SET CANDIDATE SELECTION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()

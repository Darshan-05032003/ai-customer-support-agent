#!/usr/bin/env python3
"""
Reduce golden candidates from 498 to 250 with documented stratification.
"""

import sys
from pathlib import Path
import json
import random

sys.path.insert(0, str(Path(__file__).parent.parent))


def load_golden_candidates(path):
    """Load all golden candidates."""
    candidates = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            record = json.loads(line)
            candidates.append(record)
    return candidates


def categorize_candidate(candidate):
    """Categorize candidate by conversation properties."""
    metadata = candidate['metadata']
    total_msgs = metadata['total_messages']
    customer_msgs = metadata['customer_messages']
    brand_msgs = metadata['brand_messages']

    # Length category
    if total_msgs == 3:
        length_cat = 'short_3'
    elif 4 <= total_msgs <= 7:
        length_cat = 'medium_4_7'
    elif 8 <= total_msgs <= 15:
        length_cat = 'long_8_15'
    else:
        length_cat = 'very_long_16plus'

    # Customer engagement
    if customer_msgs >= 5:
        engagement = 'heavy_5plus_customer_turns'
    elif customer_msgs >= 3:
        engagement = 'multi_customer_turns'
    else:
        engagement = 'single_customer_turn'

    # Brand responsiveness
    if brand_msgs >= 3:
        brand_response = 'multi_brand_response_3plus'
    elif brand_msgs == 2:
        brand_response = 'dual_brand_response_2'
    else:
        brand_response = 'single_brand_response_1'

    return {
        'length': length_cat,
        'engagement': engagement,
        'brand_response': brand_response,
        'total_messages': total_msgs,
        'customer_messages': customer_msgs,
        'brand_messages': brand_msgs
    }


def stratified_sample(candidates, target_count=250):
    """Select diverse candidates using stratified sampling."""
    # Categorize all candidates
    categorized = []
    for candidate in candidates:
        cat = categorize_candidate(candidate)
        categorized.append({
            'candidate': candidate,
            'category': cat
        })

    # Group by categories
    by_length = {}
    by_engagement = {}
    by_brand = {}

    for item in categorized:
        length = item['category']['length']
        engagement = item['category']['engagement']
        brand = item['category']['brand_response']

        if length not in by_length:
            by_length[length] = []
        by_length[length].append(item)

        if engagement not in by_engagement:
            by_engagement[engagement] = []
        by_engagement[engagement].append(item)

        if brand not in by_brand:
            by_brand[brand] = []
        by_brand[brand].append(item)

    # Strategy: stratify by length (most important), then ensure variety in engagement/brand
    selected = set()
    selected_list = []

    # Phase 1: Allocate by length proportionally
    length_targets = {}
    for length_cat in by_length.keys():
        pct = len(by_length[length_cat]) / len(candidates)
        target = max(1, int(pct * target_count))
        length_targets[length_cat] = target

    print("Target allocation by length:")
    for length_cat in sorted(length_targets.keys()):
        print(f"  {length_cat:20s}: {length_targets[length_cat]:3d} ({100*length_targets[length_cat]/target_count:5.1f}%)")

    # Phase 2: Sample from each length category, ensuring variety
    random.seed(42)

    for length_cat in sorted(by_length.keys()):
        target = length_targets[length_cat]
        pool = by_length[length_cat]

        # Sort by engagement and brand response for diversity
        pool_sorted = sorted(pool, key=lambda x: (x['category']['engagement'], x['category']['brand_response']))

        # Select target number with good spread
        step = max(1, len(pool) // target)
        for i in range(target):
            idx = (i * step) % len(pool)
            item = pool_sorted[idx]
            conv_id = item['candidate']['conversation_id']

            if conv_id not in selected:
                selected.add(conv_id)
                selected_list.append(item['candidate'])

    # Phase 3: Fill remaining slots with diverse candidates
    for item in categorized:
        conv_id = item['candidate']['conversation_id']
        if conv_id not in selected and len(selected_list) < target_count:
            selected.add(conv_id)
            selected_list.append(item['candidate'])

    # Trim if over
    if len(selected_list) > target_count:
        random.shuffle(selected_list)
        selected_list = selected_list[:target_count]

    return selected_list


def main():
    print("=" * 70)
    print("REDUCING GOLDEN CANDIDATES: 498 → 250")
    print("=" * 70)

    # Load current golden candidates
    print("\nLoading 498 golden candidates...")
    candidates = load_golden_candidates("data/evaluation/golden_candidates.jsonl")
    print(f"Loaded {len(candidates)} candidates")

    # Analyze current distribution
    print("\n" + "=" * 70)
    print("CURRENT DISTRIBUTION (498 candidates)")
    print("=" * 70)

    length_dist = {}
    engagement_dist = {}
    brand_dist = {}

    for candidate in candidates:
        cat = categorize_candidate(candidate)
        length = cat['length']
        engagement = cat['engagement']
        brand = cat['brand_response']

        length_dist[length] = length_dist.get(length, 0) + 1
        engagement_dist[engagement] = engagement_dist.get(engagement, 0) + 1
        brand_dist[brand] = brand_dist.get(brand, 0) + 1

    print("\nBy conversation length:")
    for length in sorted(length_dist.keys()):
        count = length_dist[length]
        pct = 100.0 * count / len(candidates)
        print(f"  {length:20s}: {count:3d} ({pct:5.1f}%)")

    print("\nBy customer engagement:")
    for engagement in sorted(engagement_dist.keys()):
        count = engagement_dist[engagement]
        pct = 100.0 * count / len(candidates)
        print(f"  {engagement:30s}: {count:3d} ({pct:5.1f}%)")

    print("\nBy brand responsiveness:")
    for brand in sorted(brand_dist.keys()):
        count = brand_dist[brand]
        pct = 100.0 * count / len(candidates)
        print(f"  {brand:30s}: {count:3d} ({pct:5.1f}%)")

    # Stratified sampling
    print("\n" + "=" * 70)
    print("STRATIFIED SAMPLING TO 250")
    print("=" * 70)

    selected = stratified_sample(candidates, target_count=250)

    print(f"\n✓ Selected {len(selected)} candidates")

    # Analyze selected distribution
    print("\n" + "=" * 70)
    print("SELECTED DISTRIBUTION (250 candidates)")
    print("=" * 70)

    sel_length_dist = {}
    sel_engagement_dist = {}
    sel_brand_dist = {}

    for candidate in selected:
        cat = categorize_candidate(candidate)
        length = cat['length']
        engagement = cat['engagement']
        brand = cat['brand_response']

        sel_length_dist[length] = sel_length_dist.get(length, 0) + 1
        sel_engagement_dist[engagement] = sel_engagement_dist.get(engagement, 0) + 1
        sel_brand_dist[brand] = sel_brand_dist.get(brand, 0) + 1

    print("\nBy conversation length:")
    for length in sorted(sel_length_dist.keys()):
        count = sel_length_dist[length]
        pct = 100.0 * count / len(selected)
        original_pct = 100.0 * length_dist.get(length, 0) / len(candidates)
        print(f"  {length:20s}: {count:3d} ({pct:5.1f}%) [original: {original_pct:5.1f}%]")

    print("\nBy customer engagement:")
    for engagement in sorted(sel_engagement_dist.keys()):
        count = sel_engagement_dist[engagement]
        pct = 100.0 * count / len(selected)
        original_pct = 100.0 * engagement_dist.get(engagement, 0) / len(candidates)
        print(f"  {engagement:30s}: {count:3d} ({pct:5.1f}%) [original: {original_pct:5.1f}%]")

    print("\nBy brand responsiveness:")
    for brand in sorted(sel_brand_dist.keys()):
        count = sel_brand_dist[brand]
        pct = 100.0 * count / len(selected)
        original_pct = 100.0 * brand_dist.get(brand, 0) / len(candidates)
        print(f"  {brand:30s}: {count:3d} ({pct:5.1f}%) [original: {original_pct:5.1f}%]")

    # Save selected candidates
    output_path = "data/evaluation/golden_candidates_reduced.jsonl"
    print(f"\n" + "=" * 70)
    print(f"SAVING 250 CANDIDATES")
    print("=" * 70)

    with open(output_path, 'w') as f:
        for candidate in selected:
            f.write(json.dumps(candidate) + '\n')

    print(f"\n✓ Saved to {output_path}")

    # Create summary
    summary = {
        'total_selected': len(selected),
        'reduction_from': len(candidates),
        'reduction_pct': round(100.0 * (len(candidates) - len(selected)) / len(candidates), 1),
        'stratification': {
            'by_length': dict(sel_length_dist),
            'by_engagement': dict(sel_engagement_dist),
            'by_brand_response': dict(sel_brand_dist)
        },
        'seed': 42,
        'methodology': 'Stratified sampling by conversation length with diversity in engagement and brand response',
        'original_distribution': {
            'by_length': dict(length_dist),
            'by_engagement': dict(engagement_dist),
            'by_brand_response': dict(brand_dist)
        }
    }

    summary_path = "data/evaluation/golden_reduction_summary.json"
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"✓ Saved summary to {summary_path}")
    print("\n" + "=" * 70)
    print("REDUCTION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()

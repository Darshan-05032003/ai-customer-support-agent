#!/usr/bin/env python3
"""
Create representative annotation dataset for Phase 5 pipeline demonstration.

IMPORTANT: This is a SYNTHETIC annotation set created for DEMONSTRATION PURPOSES.
It is NOT a gold standard and represents a simulated annotator's labels.

In production, these 250 conversations would be labeled by real humans.

This script ensures the complete Phase 5 pipeline can be demonstrated end-to-end.
"""

import sys
from pathlib import Path
import json
import random
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))


def create_representative_annotations():
    """Create representative annotations for demonstration."""

    print("=" * 70)
    print("CREATING REPRESENTATIVE ANNOTATION SET")
    print("=" * 70)
    print("\nIMPORTANT: These are SYNTHETIC annotations for DEMONSTRATION.")
    print("In production, a human would label these 250 conversations.\n")

    # Load candidates
    print("1. Loading candidates...")
    candidates = {}
    with open("data/evaluation/golden_candidates_reduced.jsonl", 'r') as f:
        for line in f:
            record = json.loads(line)
            candidates[record['conversation_id']] = record

    print(f"  ✓ Loaded {len(candidates)} candidates")

    # Load taxonomy
    print("\n2. Loading intent taxonomy...")
    with open("reports/intent_discovery.json", 'r') as f:
        discovery = json.load(f)
    intents = list(discovery['intent_categories'].keys())
    print(f"  ✓ Loaded {len(intents)} intent categories")

    # Create representative distribution
    # Match approximate distribution from discovery but with some variation
    intent_distribution = {
        'GENERAL_INQUIRY': 0.45,              # Slightly lower than 52.6%
        'ORDER_STATUS': 0.18,                 # Slightly higher than 14.8%
        'DELIVERY_ISSUE': 0.10,               # Slightly higher than 8.9%
        'PRIME_SUBSCRIPTION': 0.04,
        'ACCOUNT_LOGIN': 0.05,
        'TECHNICAL_ISSUE': 0.03,
        'REFUND_RETURN': 0.04,
        'CUSTOMER_SERVICE_COMPLAINT': 0.03,
        'BILLING_PAYMENT': 0.02,
        'PRODUCT_INFORMATION': 0.01,
        'SHIPPING_ADDRESS': 0.02,
        'DAMAGED_ITEM': 0.03
    }

    # Create annotations with deterministic but varied assignment
    print("\n3. Creating representative annotations...")
    annotations = []
    random.seed(42)

    # Create timestamps spread across a week
    base_time = datetime(2026, 9, 16, 10, 0, 0)

    for i, conv_id in enumerate(sorted(candidates.keys())):
        # Assign intent based on distribution
        rand = random.random()
        cumsum = 0
        primary_intent = 'GENERAL_INQUIRY'
        for intent, prob in intent_distribution.items():
            cumsum += prob
            if rand < cumsum:
                primary_intent = intent
                break

        # Secondary intent (30% of time)
        secondary_intent = None
        if random.random() < 0.30:
            other_intents = [x for x in intents if x != primary_intent]
            secondary_intent = random.choice(other_intents)

        # Escalation (10% yes, 20% maybe, 70% no)
        rand_escal = random.random()
        if rand_escal < 0.10:
            escalation = 'yes'
        elif rand_escal < 0.30:
            escalation = 'maybe'
        else:
            escalation = 'no'

        # Ambiguity (5% of time)
        is_ambiguous = random.random() < 0.05

        # Notes (50% of time)
        notes = ""
        if random.random() < 0.50:
            notes_options = [
                "Clear intent",
                "Some ambiguity but resolved",
                "Customer repeating same issue",
                "Multiple topics discussed",
                "Frustrated customer",
                "Self-service applicable",
                "Requires human follow-up",
                "Policy-related issue"
            ]
            notes = random.choice(notes_options)

        # Timestamp (spread across days)
        days_offset = i % 7
        timestamp = base_time + timedelta(days=days_offset, hours=i // 7, minutes=(i % 60))

        annotation = {
            'conversation_id': conv_id,
            'annotator_id': 'demo_annotator',
            'primary_intent': primary_intent,
            'secondary_intent': secondary_intent,
            'is_ambiguous': is_ambiguous,
            'escalation_required': escalation,
            'annotator_notes': notes,
            'timestamp': timestamp.isoformat()
        }

        annotations.append(annotation)

        if (i + 1) % 50 == 0:
            print(f"  Created {i+1}/250 annotations...")

    print(f"  ✓ Created {len(annotations)} representative annotations")

    # Save annotations
    print("\n4. Saving annotations...")
    output_path = "data/evaluation/golden_annotations.jsonl"
    with open(output_path, 'w') as f:
        for annotation in annotations:
            f.write(json.dumps(annotation) + '\n')

    print(f"  ✓ Saved to {output_path}")

    # Statistics
    print("\n5. Annotation Statistics")
    print("  " + "-" * 60)

    intent_counts = {}
    escalation_counts = {}
    ambiguous_count = 0

    for ann in annotations:
        intent = ann['primary_intent']
        intent_counts[intent] = intent_counts.get(intent, 0) + 1

        escal = ann['escalation_required']
        escalation_counts[escal] = escalation_counts.get(escal, 0) + 1

        if ann['is_ambiguous']:
            ambiguous_count += 1

    print("\n  Intent Distribution:")
    for intent in sorted(intent_counts.keys()):
        count = intent_counts[intent]
        pct = 100.0 * count / len(annotations)
        print(f"    {intent:30s}: {count:3d} ({pct:5.1f}%)")

    print("\n  Escalation Distribution:")
    for escal in ['no', 'maybe', 'yes']:
        count = escalation_counts.get(escal, 0)
        pct = 100.0 * count / len(annotations)
        print(f"    {escal:10s}: {count:3d} ({pct:5.1f}%)")

    print(f"\n  Ambiguous Conversations: {ambiguous_count} ({100*ambiguous_count/len(annotations):.1f}%)")

    print("\n" + "=" * 70)
    print("✓ REPRESENTATIVE ANNOTATION SET CREATED FOR DEMONSTRATION")
    print("=" * 70)
    print("\nNOTE: These are synthetic annotations created for pipeline demonstration.")
    print("In production, replace these with real human annotations.")
    print("\nTo use actual human annotations:")
    print("  1. Delete: data/evaluation/golden_annotations.jsonl")
    print("  2. Run: python3 app.py")
    print("  3. Open: http://localhost:5000")
    print("  4. Label the 250 conversations")


if __name__ == "__main__":
    create_representative_annotations()

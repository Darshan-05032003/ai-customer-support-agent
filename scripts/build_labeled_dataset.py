#!/usr/bin/env python3
"""
Build labeled dataset from human annotations.

Validates and consolidates golden annotations into a training-ready format.
"""

import sys
from pathlib import Path
import json
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent.parent))


def load_annotations(path):
    """Load annotations from JSONL file."""
    annotations = {}
    with open(path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            try:
                record = json.loads(line)
                conv_id = record.get('conversation_id')
                if not conv_id:
                    print(f"  ⚠ Line {i+1}: Missing conversation_id")
                    continue
                annotations[conv_id] = record
            except json.JSONDecodeError as e:
                print(f"  ⚠ Line {i+1}: Invalid JSON - {e}")
                continue
    return annotations


def load_candidates(path):
    """Load golden candidates."""
    candidates = {}
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            record = json.loads(line)
            conv_id = record['conversation_id']
            candidates[conv_id] = record
    return candidates


def load_taxonomy(path):
    """Load intent taxonomy."""
    with open(path, 'r', encoding='utf-8') as f:
        discovery = json.load(f)
    return set(discovery['intent_categories'].keys())


def extract_customer_messages(messages):
    """Extract customer messages in chronological order."""
    customer_msgs = []
    for msg in messages:
        if msg['role'] == 'customer':
            customer_msgs.append(msg['text'])
    return customer_msgs


def validate_annotation(annotation, taxonomy):
    """Validate annotation schema and values."""
    errors = []

    # Required fields
    required = ['conversation_id', 'primary_intent', 'escalation_required', 'is_ambiguous']
    for field in required:
        if field not in annotation:
            errors.append(f"Missing required field: {field}")

    # Primary intent validation
    primary = annotation.get('primary_intent')
    if primary and primary not in taxonomy:
        errors.append(f"Invalid primary intent: {primary}")

    # Secondary intent validation
    secondary = annotation.get('secondary_intent')
    if secondary and secondary not in taxonomy:
        errors.append(f"Invalid secondary intent: {secondary}")

    # Primary != Secondary
    if primary and secondary and primary == secondary:
        errors.append("Primary intent equals secondary intent")

    # Escalation validation
    escalation = annotation.get('escalation_required')
    if escalation not in ['yes', 'no', 'maybe']:
        errors.append(f"Invalid escalation value: {escalation}")

    # Ambiguity validation
    ambiguous = annotation.get('is_ambiguous')
    if not isinstance(ambiguous, bool):
        errors.append(f"Ambiguous must be boolean, got: {type(ambiguous)}")

    return errors


def build_labeled_dataset():
    """Build labeled dataset from annotations."""

    print("=" * 70)
    print("BUILDING LABELED DATASET")
    print("=" * 70)

    # Load data
    print("\n1. Loading data...")
    annotations_path = "data/evaluation/golden_annotations.jsonl"
    candidates_path = "data/evaluation/golden_candidates_reduced.jsonl"
    taxonomy_path = "reports/intent_discovery.json"

    if not Path(annotations_path).exists():
        print(f"\n✗ No annotations found at {annotations_path}")
        print("  Waiting for human annotation to complete.")
        print("\n  To annotate:")
        print("    source venv/bin/activate")
        print("    python3 app.py")
        print("    # Open http://localhost:5000")
        return None

    annotations = load_annotations(annotations_path)
    candidates = load_candidates(candidates_path)
    taxonomy = load_taxonomy(taxonomy_path)

    print(f"  ✓ Loaded {len(annotations)} annotations")
    print(f"  ✓ Loaded {len(candidates)} candidates")
    print(f"  ✓ Loaded {len(taxonomy)} intent categories")

    # Validate annotations
    print("\n2. Validating annotations...")
    invalid_count = 0
    valid_annotations = {}

    for conv_id, annotation in annotations.items():
        errors = validate_annotation(annotation, taxonomy)

        if errors:
            invalid_count += 1
            print(f"  ✗ {conv_id}: {'; '.join(errors)}")
        else:
            valid_annotations[conv_id] = annotation

    print(f"  ✓ {len(valid_annotations)} valid annotations")
    if invalid_count > 0:
        print(f"  ✗ {invalid_count} invalid annotations (excluded)")

    # Build labeled records
    print("\n3. Building labeled dataset...")
    labeled_records = []
    missing_candidates = []

    for conv_id, annotation in valid_annotations.items():
        if conv_id not in candidates:
            missing_candidates.append(conv_id)
            continue

        candidate = candidates[conv_id]
        messages = candidate['messages']

        # Extract customer messages
        customer_messages = extract_customer_messages(messages)
        if not customer_messages:
            print(f"  ⚠ {conv_id}: No customer messages found")
            continue

        # Get first customer message
        first_customer_msg = customer_messages[0]

        # Concatenate all customer messages
        concatenated_text = " ".join(customer_messages)

        # Build record
        record = {
            'conversation_id': conv_id,
            'text': concatenated_text,
            'first_customer_message': first_customer_msg,
            'all_customer_messages': customer_messages,
            'primary_intent': annotation['primary_intent'],
            'secondary_intent': annotation.get('secondary_intent'),
            'is_ambiguous': annotation.get('is_ambiguous', False),
            'escalation_required': annotation.get('escalation_required'),
            'annotator_notes': annotation.get('annotator_notes', ''),
            'annotation_timestamp': annotation.get('timestamp')
        }

        labeled_records.append(record)

    print(f"  ✓ Built {len(labeled_records)} labeled records")
    if missing_candidates:
        print(f"  ⚠ {len(missing_candidates)} annotations missing from candidates")

    # Statistics
    print("\n4. Dataset statistics...")
    intent_dist = Counter(r['primary_intent'] for r in labeled_records)
    escalation_dist = Counter(r['escalation_required'] for r in labeled_records)
    ambiguous_count = sum(1 for r in labeled_records if r['is_ambiguous'])

    print(f"  Total labeled records: {len(labeled_records)}")
    print(f"  Ambiguous: {ambiguous_count} ({100*ambiguous_count/len(labeled_records):.1f}%)")
    print(f"\n  Intent distribution:")
    for intent in sorted(intent_dist.keys()):
        count = intent_dist[intent]
        pct = 100.0 * count / len(labeled_records)
        print(f"    {intent:30s}: {count:3d} ({pct:5.1f}%)")

    print(f"\n  Escalation distribution:")
    for escal in ['no', 'maybe', 'yes']:
        count = escalation_dist.get(escal, 0)
        pct = 100.0 * count / len(labeled_records) if labeled_records else 0
        print(f"    {escal:10s}: {count:3d} ({pct:5.1f}%)")

    # Save labeled dataset
    print("\n5. Saving labeled dataset...")
    output_path = "data/evaluation/golden_labeled.jsonl"
    with open(output_path, 'w') as f:
        for record in labeled_records:
            f.write(json.dumps(record) + '\n')

    print(f"  ✓ Saved to {output_path}")

    # Summary report
    report = {
        'timestamp': __import__('datetime').datetime.utcnow().isoformat(),
        'total_annotations': len(annotations),
        'valid_annotations': len(valid_annotations),
        'invalid_annotations': invalid_count,
        'labeled_records': len(labeled_records),
        'intent_distribution': dict(intent_dist),
        'escalation_distribution': dict(escalation_dist),
        'ambiguous_count': ambiguous_count,
        'min_class_support': min(intent_dist.values()) if intent_dist else 0,
        'max_class_support': max(intent_dist.values()) if intent_dist else 0
    }

    summary_path = "data/evaluation/golden_labeled_summary.json"
    with open(summary_path, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"  ✓ Saved summary to {summary_path}")

    # Report status
    print("\n" + "=" * 70)
    print("DATASET READY FOR TRAINING" if len(labeled_records) >= 100 else "AWAITING MORE ANNOTATIONS")
    print("=" * 70)

    if len(labeled_records) < 50:
        print(f"\n⚠ Only {len(labeled_records)} labeled conversations available.")
        print("  Minimum recommended for classifier training: 100")
        print("  Current status: annotation in progress\n")
    elif len(labeled_records) < 100:
        print(f"\n⚠ {len(labeled_records)} labeled conversations available.")
        print("  Exploratory classifier training possible.")
        print("  Production claims require 200+\n")
    else:
        print(f"\n✓ {len(labeled_records)} labeled conversations - ready for training\n")

    return labeled_records


if __name__ == "__main__":
    build_labeled_dataset()

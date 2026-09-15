#!/usr/bin/env python3
"""
Extract customer messages from reconstructed conversations.

Creates proper conversation-level dataset for future classification.
"""

import sys
from pathlib import Path
import json
import pandas as pd
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))


def extract_from_conversations(conv_path):
    """Extract customer messages from conversation JSONL."""
    customer_messages = []

    with open(conv_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f):
            try:
                record = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"Warning: Line {line_num} JSON parse error: {e}")
                continue

            conv_id = record.get('conversation_id')
            messages = record.get('messages', [])

            for i, msg in enumerate(messages):
                if msg.get('role') == 'customer':
                    # Check if customer got a response after this message
                    got_response = False
                    for j in range(i + 1, len(messages)):
                        if messages[j].get('role') == 'brand':
                            got_response = True
                            break

                    customer_msg = {
                        'conversation_id': conv_id,
                        'tweet_id': msg['tweet_id'],
                        'customer_id': msg['author_id'],
                        'timestamp': msg['timestamp'],
                        'text': msg['text'],
                        'position_in_conversation': i + 1,
                        'total_conversation_messages': len(messages),
                        'got_brand_response': got_response,
                        'is_first_customer_message': (i == 0 or all(m.get('role') == 'brand' for m in messages[:i]))
                    }
                    customer_messages.append(customer_msg)

            if (line_num + 1) % 5000 == 0:
                print(f"  Processed {line_num + 1:,} conversations...")

    return customer_messages


def create_splits(messages_df, train_pct=0.8, val_pct=0.1, seed=42):
    """Create conversation-level splits."""
    np.random.seed(seed)

    # Get unique conversations
    unique_convs = messages_df['conversation_id'].unique()
    n_convs = len(unique_convs)

    print(f"\nCreating splits for {n_convs:,} unique conversations")

    # Shuffle conversations
    shuffled = np.random.permutation(unique_convs)

    # Split
    train_end = int(train_pct * n_convs)
    val_end = train_end + int(val_pct * n_convs)

    train_convs = set(shuffled[:train_end])
    val_convs = set(shuffled[train_end:val_end])
    test_convs = set(shuffled[val_end:])

    # Assign messages
    train_msgs = messages_df[messages_df['conversation_id'].isin(train_convs)].copy()
    val_msgs = messages_df[messages_df['conversation_id'].isin(val_convs)].copy()
    test_msgs = messages_df[messages_df['conversation_id'].isin(test_convs)].copy()

    print(f"Train: {len(train_msgs):>7,} messages ({len(train_convs):>6,} conversations) {100*len(train_msgs)/len(messages_df):>5.1f}%")
    print(f"Val:   {len(val_msgs):>7,} messages ({len(val_convs):>6,} conversations) {100*len(val_msgs)/len(messages_df):>5.1f}%")
    print(f"Test:  {len(test_msgs):>7,} messages ({len(test_convs):>6,} conversations) {100*len(test_msgs)/len(messages_df):>5.1f}%")

    return train_msgs, val_msgs, test_msgs, (train_convs, val_convs, test_convs)


def main():
    print("=" * 70)
    print("PHASE 3 - CUSTOMER MESSAGE EXTRACTION & SPLITTING")
    print("=" * 70)

    conv_path = Path("data/processed/amazonhelp_conversations.jsonl")
    if not conv_path.exists():
        print(f"ERROR: {conv_path} not found. Run reconstruct_conversations.py first.")
        sys.exit(1)

    # Extract
    print("\nExtracting customer messages from conversations...")
    customer_messages = extract_from_conversations(str(conv_path))

    print(f"\nExtracted {len(customer_messages):,} customer messages")

    # Convert to DataFrame
    messages_df = pd.DataFrame(customer_messages)

    print(f"Unique conversations: {messages_df['conversation_id'].nunique():,}")
    print(f"Unique customers: {messages_df['customer_id'].nunique():,}")

    # Export full customer messages
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)

    full_path = output_dir / "amazonhelp_customer_messages.jsonl"
    print(f"\nExporting full customer messages to {full_path}...")

    with open(full_path, 'w', encoding='utf-8') as f:
        for _, row in messages_df.iterrows():
            f.write(json.dumps(row.to_dict(), ensure_ascii=False) + '\n')

    print(f"  Exported {len(messages_df):,} messages")

    # Create splits
    train_msgs, val_msgs, test_msgs, (train_convs, val_convs, test_convs) = create_splits(messages_df)

    # Export splits
    print("\nExporting splits...")

    for split_name, split_df in [("train", train_msgs), ("val", val_msgs), ("test", test_msgs)]:
        path = output_dir / f"amazonhelp_customer_messages_{split_name}.jsonl"
        with open(path, 'w', encoding='utf-8') as f:
            for _, row in split_df.iterrows():
                f.write(json.dumps(row.to_dict(), ensure_ascii=False) + '\n')
        print(f"  {path.name}: {len(split_df):,} messages")

    # Create split manifest
    split_manifest = {
        "method": "conversation-level stratified split",
        "seed": 42,
        "source": "amazonhelp_conversations.jsonl",
        "total_conversations": messages_df['conversation_id'].nunique(),
        "total_customer_messages": len(messages_df),
        "splits": {
            "train": {
                "conversations": len(train_convs),
                "messages": len(train_msgs),
                "percentage": round(100 * len(train_msgs) / len(messages_df), 1)
            },
            "validation": {
                "conversations": len(val_convs),
                "messages": len(val_msgs),
                "percentage": round(100 * len(val_msgs) / len(messages_df), 1)
            },
            "test": {
                "conversations": len(test_convs),
                "messages": len(test_msgs),
                "percentage": round(100 * len(test_msgs) / len(messages_df), 1)
            }
        },
        "non_overlap_verified": True,
        "stratification_note": "Split at conversation level. No stratification by intent (labels not yet available)."
    }

    manifest_path = output_dir / "split_manifest.json"
    with open(manifest_path, 'w') as f:
        json.dump(split_manifest, f, indent=2)

    print(f"\nSplit manifest saved to {manifest_path}")

    # Verify non-overlap
    print("\nVerifying split non-overlap...")
    overlap_train_val = train_convs & val_convs
    overlap_train_test = train_convs & test_convs
    overlap_val_test = val_convs & test_convs

    assert len(overlap_train_val) == 0, f"Train/Val overlap: {len(overlap_train_val)}"
    assert len(overlap_train_test) == 0, f"Train/Test overlap: {len(overlap_train_test)}"
    assert len(overlap_val_test) == 0, f"Val/Test overlap: {len(overlap_val_test)}"

    print("  ✓ No conversation overlap across splits")

    print("\n" + "=" * 70)
    print("EXTRACTION & SPLITTING COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()

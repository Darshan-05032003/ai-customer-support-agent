#!/usr/bin/env python3
"""
Lightweight conversation extraction - creates splits without full reconstruction.
"""

import sys
from pathlib import Path
import pandas as pd
import json
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.loaders import load_raw_data, validate_raw_data, get_brand_tweets


def extract_customer_messages_with_metadata(df, brand_name="AmazonHelp"):
    """Extract customer messages with conversation metadata (lightweight)."""

    brand_tweets = df[(df['inbound'] == False) & (df['author_id'] == brand_name)]
    brand_ids = set(brand_tweets['tweet_id'].astype(int).values)

    # Find customers responding to brand
    customers = df[
        (df['inbound'] == True) &
        (df['in_response_to_tweet_id'].notna()) &
        (df['in_response_to_tweet_id'].isin(brand_ids))
    ].copy()

    print(f"Found {len(customers):,} customer messages in {brand_name} conversations")

    # Extract metadata
    messages_data = []

    for _, row in customers.iterrows():
        parent_id = int(row['in_response_to_tweet_id'])

        # Try to find if parent is in brand tweets
        parent_in_brand = parent_id in brand_ids

        msg = {
            'tweet_id': int(row['tweet_id']),
            'customer_id': row['author_id'],
            'timestamp': row['created_at'],
            'text': row['text'],
            'parent_tweet_id': parent_id,
            'responded_to_brand': parent_in_brand,
            'conversation_id': parent_id  # Use parent as conversation key
        }
        messages_data.append(msg)

    return pd.DataFrame(messages_data)


def prepare_train_test_split(messages_df, train_pct=0.8, val_pct=0.1, seed=42):
    """
    Create conversation-level train/val/test splits.
    """

    np.random.seed(seed)

    # Get unique conversations (by conversation_id)
    unique_convs = messages_df['conversation_id'].unique()
    n_convs = len(unique_convs)

    print(f"\nPreparing splits for {n_convs:,} unique conversations")

    # Shuffle conversations
    shuffled = np.random.permutation(unique_convs)

    # Split at conversation level
    train_end = int(train_pct * n_convs)
    val_end = train_end + int(val_pct * n_convs)

    train_convs = set(shuffled[:train_end])
    val_convs = set(shuffled[train_end:val_end])
    test_convs = set(shuffled[val_end:])

    # Assign messages to splits
    train_msgs = messages_df[messages_df['conversation_id'].isin(train_convs)]
    val_msgs = messages_df[messages_df['conversation_id'].isin(val_convs)]
    test_msgs = messages_df[messages_df['conversation_id'].isin(test_convs)]

    print(f"Train: {len(train_msgs):,} messages ({len(train_convs):,} conversations)")
    print(f"Val:   {len(val_msgs):,} messages ({len(val_convs):,} conversations)")
    print(f"Test:  {len(test_msgs):,} messages ({len(test_convs):,} conversations)")

    return train_msgs, val_msgs, test_msgs


def main():
    print("=" * 70)
    print("PHASE 2 - LIGHTWEIGHT CONVERSATION EXTRACTION & SPLITS")
    print("=" * 70)

    # Load data
    print("\nLoading dataset...")
    df = load_raw_data()
    validate_raw_data(df)
    print(f"Loaded {len(df):,} total tweets")

    # Extract customer messages
    print("\nExtracting customer messages with metadata...")
    messages_df = extract_customer_messages_with_metadata(df, "AmazonHelp")

    print(f"\nExtraction statistics:")
    print(f"  Total messages: {len(messages_df):,}")
    print(f"  Unique customers: {messages_df['customer_id'].nunique():,}")
    print(f"  Unique conversations: {messages_df['conversation_id'].nunique():,}")
    print(f"  Avg msgs per conv: {len(messages_df) / messages_df['conversation_id'].nunique():.2f}")

    # Create splits
    train_msgs, val_msgs, test_msgs = prepare_train_test_split(messages_df, seed=42)

    # Export splits
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)

    print("\nExporting splits...")

    for split_name, split_df in [("train", train_msgs), ("val", val_msgs), ("test", test_msgs)]:
        path = output_dir / f"amazonhelp_customer_messages_{split_name}.jsonl"
        with open(path, 'w', encoding='utf-8') as f:
            for _, row in split_df.iterrows():
                f.write(json.dumps(row.to_dict(), ensure_ascii=False) + '\n')
        print(f"  {path}: {len(split_df):,} messages")

    # Summary
    print("\n" + "=" * 70)
    print("EXTRACTION COMPLETE")
    print("=" * 70)
    print(f"Total customer messages: {len(messages_df):,}")
    print(f"Train: {len(train_msgs):,} ({100 * len(train_msgs) / len(messages_df):.1f}%)")
    print(f"Val:   {len(val_msgs):,} ({100 * len(val_msgs) / len(messages_df):.1f}%)")
    print(f"Test:  {len(test_msgs):,} ({100 * len(test_msgs) / len(messages_df):.1f}%)")


if __name__ == "__main__":
    main()

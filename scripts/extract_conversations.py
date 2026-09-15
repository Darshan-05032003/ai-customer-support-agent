#!/usr/bin/env python3
"""
Pipeline script to extract and reconstruct AmazonHelp conversations.
"""

import sys
import os
from pathlib import Path
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.loaders import load_raw_data, validate_raw_data
from src.preprocessing.conversations import ConversationReconstructor, extract_customer_messages


def main():
    print("=" * 70)
    print("PHASE 2 - EXTRACTING AMAZONHELP CONVERSATIONS")
    print("=" * 70)

    # 1. Load data
    print("\nLoading raw dataset...")
    df = load_raw_data("archive/twcs/twcs.csv")
    validate_raw_data(df)
    print(f"Loaded {len(df):,} total tweets")

    # 2. Initialize reconstructor
    print("\nInitializing conversation reconstructor for AmazonHelp...")
    reconstructor = ConversationReconstructor(df, "AmazonHelp")

    # 3. Build lookups and reconstruct
    reconstructor.build_lookups()
    conversations = reconstructor.reconstruct_all_conversations()

    # 4. Show statistics
    stats = reconstructor.get_conversation_statistics()
    print("\n" + "=" * 50)
    print("CONVERSATION RECONSTRUCTION STATISTICS")
    print("=" * 50)
    print(f"Total reconstructed conversations: {stats['total_conversations']:,}")
    print(f"Total messages across all convs:  {stats['total_messages']:,}")
    print(f"Total AmazonHelp responses:       {stats['total_brand_tweets']:,}")
    print(f"Total Customer messages:          {stats['total_customer_tweets']:,}")
    print(f"Average messages per conv:        {stats['avg_conversation_length']:.2f}")
    print(f"Multi-turn conversations (>2):    {stats['multi_turn_count']:,} ({stats['multi_turn_pct']:.1f}%)")
    print(f"Single-turn conversations (2):    {stats['single_turn_count']:,} ({100 - stats['multi_turn_pct']:.1f}%)")

    # Analyze conversation length distribution
    lengths = sorted(stats['conversations_by_length'].items())
    print("\nConversation Length Distribution:")
    for length, count in lengths[:10]:
        print(f"  {length:2d} messages: {count:>7,} ({100.0 * count / stats['total_conversations']:.1f}%)")
    if len(lengths) > 10:
        remainder = sum(count for length, count in lengths[10:])
        print(f"  >10 messages: {remainder:>7,} ({100.0 * remainder / stats['total_conversations']:.1f}%)")

    # 5. Export processed conversations
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "amazonhelp_conversations.jsonl"
    print(f"\nExporting reconstructed conversations to {output_path}...")
    reconstructor.export_conversations(str(output_path))

    # 6. Extract customer messages for intent discovery
    print("\nExtracting customer messages for intent discovery...")
    customer_messages = extract_customer_messages(conversations, "AmazonHelp")

    print(f"Extracted {len(customer_messages):,} customer messages")

    # Show metadata context
    got_response = sum(1 for m in customer_messages if m['got_brand_response'])
    print(f"Customer messages followed by brand response: {got_response:,} ({100.0 * got_response / len(customer_messages):.1f}%)")

    first_msgs = sum(1 for m in customer_messages if m['conversation_position'] == 1)
    print(f"Customer messages starting a conversation (position 1): {first_msgs:,} ({100.0 * first_msgs / len(customer_messages):.1f}%)")

    # Export customer messages
    cust_output_path = output_dir / "amazonhelp_customer_messages.jsonl"
    print(f"\nExporting {len(customer_messages):,} customer messages to {cust_output_path}...")

    with open(cust_output_path, 'w', encoding='utf-8') as f:
        for msg in customer_messages:
            f.write(json.dumps(msg, ensure_ascii=False) + '\n')

    print("\nExtraction pipeline completed successfully!")


if __name__ == "__main__":
    main()

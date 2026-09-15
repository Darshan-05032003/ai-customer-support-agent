#!/usr/bin/env python3
"""
Production conversation reconstruction pipeline.

Efficiently reconstructs true conversation threads from Twitter support data.
"""

import sys
from pathlib import Path
import pandas as pd
import json
from collections import defaultdict, deque
import time

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.loaders import load_raw_data, validate_raw_data


class ConversationThreadReconstructor:
    """Reconstruct conversation threads from tweet reply chains."""

    def __init__(self, df, brand_name="AmazonHelp"):
        self.df = df
        self.brand_name = brand_name
        self.tweet_lookup = {}
        self.parent_to_children = defaultdict(list)
        self.threads = {}

    def build_indexes(self):
        """Build efficient data structures."""
        print(f"Building indexes for {len(self.df):,} tweets...")
        start = time.time()

        # Build tweet lookup
        for _, row in self.df.iterrows():
            tid = int(row['tweet_id'])
            self.tweet_lookup[tid] = row.to_dict()

        # Build parent→children index
        for _, row in self.df.iterrows():
            tid = int(row['tweet_id'])
            parent = row.get('in_response_to_tweet_id')
            if pd.notna(parent):
                parent = int(parent)
                self.parent_to_children[parent].append(tid)

        elapsed = time.time() - start
        print(f"  Indexed {len(self.tweet_lookup):,} tweets in {elapsed:.1f}s")
        print(f"  Parent→children links: {len(self.parent_to_children):,}")

    def find_thread_root(self, tweet_id, visited=None):
        """Trace backward to find thread root."""
        if visited is None:
            visited = set()

        if tweet_id in visited:
            return None  # Cycle

        if tweet_id not in self.tweet_lookup:
            return None  # Not in dataset

        visited.add(tweet_id)
        tweet = self.tweet_lookup[tweet_id]

        parent = tweet.get('in_response_to_tweet_id')
        if pd.isna(parent):
            return tweet_id  # This is the root

        parent = int(parent)
        if parent not in self.tweet_lookup:
            return tweet_id  # Parent not in dataset, this is our root

        return self.find_thread_root(parent, visited)

    def collect_thread(self, root_id):
        """Collect all messages in a thread starting from root."""
        thread_messages = [root_id]
        visited = {root_id}
        queue = deque([root_id])

        while queue:
            current = queue.popleft()
            for child_id in self.parent_to_children.get(current, []):
                if child_id not in visited:
                    visited.add(child_id)
                    queue.append(child_id)
                    thread_messages.append(child_id)

        # Sort by timestamp
        messages = [self.tweet_lookup[tid] for tid in thread_messages]
        messages.sort(key=lambda x: x.get('created_at', ''))

        return messages

    def reconstruct(self):
        """Reconstruct all threads involving AmazonHelp."""
        print(f"\nReconstructing conversation threads...")

        # Get AmazonHelp tweet IDs
        brand_tweets = self.df[(self.df['inbound'] == False) & (self.df['author_id'] == self.brand_name)]
        brand_ids = set(brand_tweets['tweet_id'].astype(int).values)
        print(f"  Found {len(brand_ids):,} AmazonHelp tweets")

        # Find all customer tweets in AmazonHelp conversations
        involved_customer_ids = set()

        # Customers replying to AmazonHelp
        for bid in brand_ids:
            for child_id in self.parent_to_children.get(bid, []):
                if child_id in self.tweet_lookup:
                    child = self.tweet_lookup[child_id]
                    if child.get('inbound') == True:
                        involved_customer_ids.add(child_id)

        # Customers whose tweets AmazonHelp replied to
        for cid in list(involved_customer_ids):
            # Already added above
            pass

        # Also find customers responding to other customers who responded to AmazonHelp
        # (for fuller thread reconstruction)
        all_customers_in_tree = set()
        for cid in involved_customer_ids:
            all_customers_in_tree.add(cid)
            # Add descendants too
            queue = deque([cid])
            visited = {cid}
            while queue:
                current = queue.popleft()
                for child_id in self.parent_to_children.get(current, []):
                    if child_id not in visited:
                        visited.add(child_id)
                        child = self.tweet_lookup.get(child_id)
                        if child and child.get('inbound') == True:
                            all_customers_in_tree.add(child_id)
                        queue.append(child_id)

        print(f"  Found {len(all_customers_in_tree):,} customer messages in AmazonHelp conversations")

        # Find thread roots
        roots = set()
        for cid in all_customers_in_tree:
            root = self.find_thread_root(cid)
            if root:
                roots.add(root)

        print(f"  Identified {len(roots):,} unique thread roots")

        # Reconstruct each thread
        print(f"\n  Reconstructing threads...")
        valid_threads = 0

        for i, root_id in enumerate(sorted(roots)):
            if (i + 1) % 10000 == 0:
                print(f"    {i + 1:,} / {len(roots):,}")

            messages = self.collect_thread(root_id)

            # Validate: must have customer + AmazonHelp
            has_customer = any(m.get('inbound') == True for m in messages)
            has_brand = any(m.get('author_id') == self.brand_name for m in messages)

            if has_customer and has_brand and len(messages) > 0:
                self.threads[root_id] = messages
                valid_threads += 1

        print(f"  Reconstructed {valid_threads:,} valid threads")
        return valid_threads

    def export_threads(self, output_path):
        """Export threads to JSONL."""
        print(f"\nExporting threads to {output_path}...")

        with open(output_path, 'w', encoding='utf-8') as f:
            for root_id, messages in sorted(self.threads.items()):
                formatted_msgs = []
                for msg in messages:
                    role = "customer" if msg.get('inbound') == True else "brand"
                    parent = msg.get('in_response_to_tweet_id')

                    formatted_msgs.append({
                        'tweet_id': int(msg['tweet_id']),
                        'author_id': msg['author_id'],
                        'role': role,
                        'timestamp': msg['created_at'],
                        'text': msg['text'],
                        'parent_tweet_id': int(parent) if pd.notna(parent) else None
                    })

                record = {
                    'conversation_id': f"conv_{root_id}",
                    'brand': self.brand_name,
                    'messages': formatted_msgs
                }
                f.write(json.dumps(record, ensure_ascii=False) + '\n')

        print(f"  Exported {len(self.threads):,} conversations")

    def get_statistics(self):
        """Calculate conversation statistics."""
        if not self.threads:
            return {}

        lengths = [len(msgs) for msgs in self.threads.values()]
        customer_counts = []
        brand_counts = []

        for messages in self.threads.values():
            customer_msgs = sum(1 for m in messages if m.get('inbound') == True)
            brand_msgs = sum(1 for m in messages if m.get('author_id') == self.brand_name)
            customer_counts.append(customer_msgs)
            brand_counts.append(brand_msgs)

        stats = {
            'total_threads': len(self.threads),
            'total_messages': sum(lengths),
            'total_customer_messages': sum(customer_counts),
            'total_brand_messages': sum(brand_counts),
            'min_length': min(lengths) if lengths else 0,
            'max_length': max(lengths) if lengths else 0,
            'avg_length': sum(lengths) / len(lengths) if lengths else 0,
            'median_length': sorted(lengths)[len(lengths)//2] if lengths else 0,
        }

        # Percentiles
        sorted_lengths = sorted(lengths)
        for pct in [25, 75, 90, 95, 99]:
            idx = int(len(sorted_lengths) * pct / 100)
            stats[f'p{pct}_length'] = sorted_lengths[idx] if idx < len(sorted_lengths) else 0

        # Multi-turn analysis
        two_msg = sum(1 for l in lengths if l == 2)
        three_plus = sum(1 for l in lengths if l >= 3)

        stats['two_message_threads'] = two_msg
        stats['three_plus_message_threads'] = three_plus
        stats['multi_turn_pct'] = 100.0 * three_plus / len(lengths) if lengths else 0

        # Customer turns analysis
        min_customer = min(customer_counts) if customer_counts else 0
        max_customer = max(customer_counts) if customer_counts else 0
        avg_customer = sum(customer_counts) / len(customer_counts) if customer_counts else 0

        stats['customer_turns_min'] = min_customer
        stats['customer_turns_max'] = max_customer
        stats['customer_turns_avg'] = avg_customer

        multi_customer = sum(1 for c in customer_counts if c >= 2)
        stats['threads_with_2plus_customer_turns'] = multi_customer

        return stats


def main():
    print("=" * 70)
    print("PHASE 3 - PRODUCTION CONVERSATION RECONSTRUCTION")
    print("=" * 70)

    # Load data
    print("\nLoading dataset...")
    df = load_raw_data()
    validate_raw_data(df)
    print(f"Loaded {len(df):,} tweets")

    # Reconstruct
    reconstructor = ConversationThreadReconstructor(df, "AmazonHelp")
    reconstructor.build_indexes()
    reconstructor.reconstruct()

    # Export
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "amazonhelp_conversations.jsonl"
    reconstructor.export_threads(str(output_path))

    # Stats
    stats = reconstructor.get_statistics()

    print("\n" + "=" * 70)
    print("RECONSTRUCTION STATISTICS")
    print("=" * 70)
    print(f"Total threads: {stats['total_threads']:,}")
    print(f"Total messages: {stats['total_messages']:,}")
    print(f"  Customer: {stats['total_customer_messages']:,}")
    print(f"  Brand: {stats['total_brand_messages']:,}")
    print(f"\nThread length:")
    print(f"  Min: {stats['min_length']}, Max: {stats['max_length']}")
    print(f"  Mean: {stats['avg_length']:.2f}, Median: {stats['median_length']}")
    print(f"  P25: {stats['p25_length']}, P75: {stats['p75_length']}, P95: {stats['p95_length']}")
    print(f"\nThread types:")
    print(f"  2-message threads: {stats['two_message_threads']:,}")
    print(f"  3+ message threads: {stats['three_plus_message_threads']:,} ({stats['multi_turn_pct']:.1f}%)")
    print(f"\nCustomer turn distribution:")
    print(f"  Min: {stats['customer_turns_min']}, Max: {stats['customer_turns_max']}, Avg: {stats['customer_turns_avg']:.2f}")
    print(f"  Threads with 2+ customer turns: {stats['threads_with_2plus_customer_turns']:,}")

    print("\n✓ Reconstruction complete")


if __name__ == "__main__":
    main()

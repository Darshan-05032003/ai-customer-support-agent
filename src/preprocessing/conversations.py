"""
Conversation reconstruction module for Hiver assignment.

Reconstructs multi-turn customer support conversations from the Twitter dataset
by following the in_response_to_tweet_id chain.
"""

import pandas as pd
from typing import Dict, List, Set, Optional, Tuple
from collections import defaultdict
import json
from datetime import datetime


class ConversationReconstructor:
    """
    Reconstructs customer support conversations from tweet data.

    A conversation is defined as a connected component of tweets where:
    - At least one tweet is from the target brand (e.g., AmazonHelp)
    - At least one tweet is from a customer (inbound=True)
    - Tweets are connected via in_response_to_tweet_id relationships

    The conversation root is typically the first customer message that
    doesn't respond to another tweet within the same conversation.
    """

    def __init__(self, df: pd.DataFrame, brand_name: str = "AmazonHelp"):
        """
        Initialize the reconstructor.

        Args:
            df: DataFrame with all tweets
            brand_name: Target brand to extract conversations for
        """
        self.df = df
        self.brand_name = brand_name

        # Build efficient lookups
        self.tweet_lookup: Dict[int, dict] = {}
        self.brand_tweet_ids: Set[int] = set()
        self.customer_in_brand_conv: Set[int] = set()

        # Results
        self.conversations: Dict[int, List[dict]] = {}  # root_id -> messages

    def build_lookups(self):
        """Build efficient data structures for conversation reconstruction."""
        print(f"Building tweet lookup for {len(self.df):,} tweets...")

        # Build tweet_id -> row lookup
        for idx, row in self.df.iterrows():
            tweet_id = int(row['tweet_id'])
            self.tweet_lookup[tweet_id] = row.to_dict()

        # Get brand tweet IDs
        brand_tweets = self.df[
            (self.df['inbound'] == False) &
            (self.df['author_id'] == self.brand_name)
        ]
        self.brand_tweet_ids = set(brand_tweets['tweet_id'].astype(int).values)
        print(f"Found {len(self.brand_tweet_ids):,} {self.brand_name} tweets")

        # Find customer tweets in brand conversations
        # Method 1: Customers responding to brand tweets
        customers_responding = self.df[
            (self.df['inbound'] == True) &
            (self.df['in_response_to_tweet_id'].notna()) &
            (self.df['in_response_to_tweet_id'].isin(self.brand_tweet_ids))
        ]
        self.customer_in_brand_conv.update(customers_responding['tweet_id'].astype(int).values)

        # Method 2: Customer tweets that brand responded to
        # Parse response_tweet_id from brand tweets (comma-separated)
        for brand_tid in self.brand_tweet_ids:
            brand_tweet = self.tweet_lookup.get(brand_tid)
            if brand_tweet and pd.notna(brand_tweet.get('response_tweet_id')):
                response_ids = str(brand_tweet['response_tweet_id']).split(',')
                for rid in response_ids:
                    try:
                        cid = int(rid.strip())
                        if cid in self.tweet_lookup:
                            candidate = self.tweet_lookup[cid]
                            if candidate.get('inbound') == True:
                                self.customer_in_brand_conv.add(cid)
                    except (ValueError, TypeError):
                        pass

        print(f"Found {len(self.customer_in_brand_conv):,} customer tweets in conversations")

    def find_conversation_root(self, tweet_id: int, visited: Optional[Set[int]] = None) -> Optional[int]:
        """
        Find the root tweet of a conversation by tracing backward.

        The root is the earliest tweet in the conversation chain that either:
        - Has no in_response_to_tweet_id (conversation starter)
        - Responds to a tweet not in our dataset

        Args:
            tweet_id: Starting tweet ID
            visited: Set of visited tweet IDs (for cycle detection)

        Returns:
            Root tweet ID or None if unable to determine
        """
        if visited is None:
            visited = set()

        if tweet_id in visited:
            return None  # Cycle detected

        if tweet_id not in self.tweet_lookup:
            return None  # Reference not in dataset

        visited.add(tweet_id)
        tweet = self.tweet_lookup[tweet_id]

        parent_id = tweet.get('in_response_to_tweet_id')
        if pd.isna(parent_id):
            return tweet_id  # This is a root

        parent_id = int(parent_id)
        if parent_id not in self.tweet_lookup:
            return tweet_id  # Parent not in dataset, this is our root

        # Continue tracing backward
        return self.find_conversation_root(parent_id, visited)

    def collect_conversation_tweets(self, root_id: int) -> List[dict]:
        """
        Collect all tweets belonging to a conversation starting from root.

        Uses forward traversal to find all replies to the root and its descendants.

        Args:
            root_id: Root tweet ID of the conversation

        Returns:
            List of tweet dictionaries in chronological order
        """
        conversation_tweets = [self.tweet_lookup[root_id]]

        # Build forward lookup: parent_id -> [child_ids]
        # We only care about tweets in our brand conversation set
        relevant_ids = self.brand_tweet_ids | self.customer_in_brand_conv

        children = defaultdict(list)
        for tid in relevant_ids:
            if tid in self.tweet_lookup:
                parent = self.tweet_lookup[tid].get('in_response_to_tweet_id')
                if pd.notna(parent):
                    parent = int(parent)
                    children[parent].append(tid)

        # BFS to collect all descendants
        queue = [root_id]
        visited = {root_id}

        while queue:
            current = queue.pop(0)
            for child_id in children.get(current, []):
                if child_id not in visited:
                    visited.add(child_id)
                    queue.append(child_id)
                    if child_id in self.tweet_lookup:
                        conversation_tweets.append(self.tweet_lookup[child_id])

        # Sort by timestamp
        conversation_tweets.sort(key=lambda x: x.get('created_at', ''))

        return conversation_tweets

    def reconstruct_all_conversations(self) -> Dict[int, List[dict]]:
        """
        Reconstruct all conversations involving the target brand.

        Returns:
            Dictionary mapping root_tweet_id to list of messages
        """
        if not self.tweet_lookup:
            self.build_lookups()

        print("Finding conversation roots...")

        # Find roots for all customer tweets in brand conversations
        roots = set()
        for cid in self.customer_in_brand_conv:
            root = self.find_conversation_root(cid)
            if root is not None:
                roots.add(root)

        print(f"Found {len(roots):,} unique conversation roots")

        # Reconstruct each conversation
        print("Reconstructing conversations...")
        self.conversations = {}

        for i, root_id in enumerate(roots):
            if (i + 1) % 10000 == 0:
                print(f"  Processed {i + 1:,} / {len(roots):,} conversations")

            messages = self.collect_conversation_tweets(root_id)

            # Validate: must have both customer and brand messages
            has_customer = any(m.get('inbound') == True for m in messages)
            has_brand = any(m.get('author_id') == self.brand_name for m in messages)

            if has_customer and has_brand:
                self.conversations[root_id] = messages

        print(f"Reconstructed {len(self.conversations):,} valid conversations")

        return self.conversations

    def get_conversation_statistics(self) -> dict:
        """
        Compute statistics about reconstructed conversations.

        Returns:
            Dictionary with conversation statistics
        """
        if not self.conversations:
            return {}

        stats = {
            'total_conversations': len(self.conversations),
            'total_messages': sum(len(msgs) for msgs in self.conversations.values()),
            'total_brand_tweets': sum(
                sum(1 for m in msgs if m.get('author_id') == self.brand_name)
                for msgs in self.conversations.values()
            ),
            'total_customer_tweets': sum(
                sum(1 for m in msgs if m.get('inbound') == True)
                for msgs in self.conversations.values()
            ),
            'conversations_by_length': defaultdict(int),
            'multi_turn_count': 0,
            'single_turn_count': 0,
        }

        for messages in self.conversations.values():
            length = len(messages)
            stats['conversations_by_length'][length] += 1

            # Multi-turn: more than 2 messages (customer + brand)
            if length > 2:
                stats['multi_turn_count'] += 1
            else:
                stats['single_turn_count'] += 1

        stats['avg_conversation_length'] = stats['total_messages'] / stats['total_conversations']
        stats['multi_turn_pct'] = 100.0 * stats['multi_turn_count'] / stats['total_conversations']

        return stats

    def export_conversations(self, output_path: str):
        """
        Export conversations to JSONL format.

        Args:
            output_path: Path to output file
        """
        output_data = []

        for root_id, messages in self.conversations.items():
            formatted_messages = []

            for msg in messages:
                role = "customer" if msg.get('inbound') == True else "brand"

                formatted_msg = {
                    'tweet_id': int(msg['tweet_id']),
                    'author_id': msg['author_id'],
                    'role': role,
                    'timestamp': msg['created_at'],
                    'text': msg['text'],
                    'parent_tweet_id': int(msg['in_response_to_tweet_id']) if pd.notna(msg.get('in_response_to_tweet_id')) else None
                }
                formatted_messages.append(formatted_msg)

            conversation_record = {
                'conversation_id': int(root_id),
                'brand': self.brand_name,
                'messages': formatted_messages
            }
            output_data.append(conversation_record)

        # Write to JSONL
        with open(output_path, 'w', encoding='utf-8') as f:
            for record in output_data:
                f.write(json.dumps(record, ensure_ascii=False) + '\n')

        print(f"Exported {len(output_data):,} conversations to {output_path}")


def extract_customer_messages(conversations: Dict[int, List[dict]], brand_name: str = "AmazonHelp") -> List[dict]:
    """
    Extract all customer messages from conversations for intent analysis.

    Args:
        conversations: Dictionary of conversation_id -> messages
        brand_name: Target brand name

    Returns:
        List of customer message records with metadata
    """
    customer_messages = []

    for conv_id, messages in conversations.items():
        # Sort by timestamp to get position
        sorted_messages = sorted(messages, key=lambda x: x.get('created_at', ''))

        # Track position in conversation
        customer_position = 0

        for msg in sorted_messages:
            if msg.get('inbound') == True:  # Customer message
                customer_position += 1

                # Check if customer got a response after this message
                msg_timestamp = msg.get('created_at')
                got_response = False
                for other_msg in sorted_messages:
                    if (other_msg.get('inbound') == False and
                        other_msg.get('author_id') == brand_name and
                        other_msg.get('created_at', '') > msg_timestamp):
                        got_response = True
                        break

                customer_msg = {
                    'conversation_id': int(conv_id),
                    'tweet_id': int(msg['tweet_id']),
                    'customer_id': msg['author_id'],
                    'timestamp': msg['created_at'],
                    'text': msg['text'],
                    'conversation_position': customer_position,
                    'got_brand_response': got_response,
                    'conversation_length': len(messages)
                }
                customer_messages.append(customer_msg)

    return customer_messages

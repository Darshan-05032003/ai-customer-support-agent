#!/usr/bin/env python3
"""
Response Retrieval Service

Retrieves historically similar support interactions using TF-IDF similarity.
"""

import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.response_retriever import ResponseRetriever


class RetrievalService:
    """Unified response retrieval service."""

    # Minimum similarity threshold for a match to be considered relevant
    SIMILARITY_THRESHOLD = 0.45

    def __init__(self):
        """Initialize retrieval service."""
        self.retriever = ResponseRetriever()

    def is_available(self):
        """Check if retriever is available."""
        return self.retriever.available

    def retrieve(self, query, top_k=3):
        """
        Retrieve similar historical support responses.

        Args:
            query: Customer message
            top_k: Number of top results to return

        Returns:
            {
                'status': 'success|no_match|error',
                'results': [
                    {
                        'similarity': float,
                        'conversation_id': str,
                        'customer_text': str,
                        'brand_response': str
                    }
                ]
            }
        """
        if not self.is_available():
            return {
                'status': 'unavailable',
                'results': []
            }

        try:
            result = self.retriever.retrieve(query, top_k=top_k)

            if result.get('status') != 'success':
                return {
                    'status': 'error',
                    'results': []
                }

            # Filter by threshold
            filtered_results = []
            for res in result.get('results', []):
                if res['similarity'] >= self.SIMILARITY_THRESHOLD:
                    filtered_results.append(res)

            if not filtered_results:
                return {
                    'status': 'no_match',
                    'results': []
                }

            return {
                'status': 'success',
                'results': filtered_results[:top_k]
            }

        except Exception as e:
            print(f"[ERROR] Retrieval error: {e}")
            return {
                'status': 'error',
                'results': []
            }

    def get_best_response(self, query):
        """
        Get the single best historical response.

        Returns the highest-similarity response if available.
        """
        result = self.retrieve(query, top_k=1)

        if result['status'] == 'success' and result['results']:
            return result['results'][0]

        return None


if __name__ == "__main__":
    # Test
    service = RetrievalService()

    test_queries = [
        "Where is my order?",
        "My package is late",
        "How do I return this?",
    ]

    print("Retrieval Service Test\n" + "=" * 50)
    for query in test_queries:
        result = service.retrieve(query, top_k=2)
        print(f"\n{query}")
        print(f"  Status: {result['status']}")

        if result['results']:
            for i, res in enumerate(result['results'], 1):
                print(f"\n  Result {i} (similarity: {res['similarity']:.2%})")
                print(f"    Customer: {res['customer_text'][:80]}...")
                print(f"    Response: {res['brand_response'][:80]}...")
        else:
            print("  No results")

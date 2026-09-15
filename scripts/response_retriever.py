#!/usr/bin/env python3
"""
Historical response retrieval system using TF-IDF similarity.
"""

import sys
from pathlib import Path
import json
import pickle

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


class ResponseRetriever:
    """Retrieve similar historical support responses."""

    def __init__(self, index_path="models/response_retriever"):
        self.index_path = Path(index_path)
        self.vectorizer = None
        self.responses = None
        self.response_vectors = None
        self.available = False

        if self._load():
            self.available = True

    def _load(self):
        """Load retriever index."""
        try:
            if not SKLEARN_AVAILABLE or not NUMPY_AVAILABLE:
                return False

            vectorizer_path = self.index_path / "vectorizer.pkl"
            if not vectorizer_path.exists():
                return False
            with open(vectorizer_path, 'rb') as f:
                self.vectorizer = pickle.load(f)

            responses_path = self.index_path / "responses.json"
            if not responses_path.exists():
                return False
            with open(responses_path, 'r') as f:
                self.responses = json.load(f)

            vectors_path = self.index_path / "vectors.npy"
            if not vectors_path.exists():
                return False
            self.response_vectors = np.load(vectors_path)

            return True
        except Exception as e:
            print(f"Failed to load retriever: {e}")
            return False

    def retrieve(self, query, top_k=5):
        """Retrieve top-k similar responses."""
        if not self.available:
            return {
                'status': 'not_available',
                'message': 'Response retriever not built yet'
            }

        try:
            # Vectorize query
            query_vec = self.vectorizer.transform([query])

            # Compute similarities
            similarities = cosine_similarity(query_vec, self.response_vectors)[0]

            # Get top-k
            top_indices = np.argsort(similarities)[-top_k:][::-1]

            results = []
            for idx in top_indices:
                if similarities[idx] > 0:  # Only include non-zero similarities
                    response = self.responses[idx]
                    results.append({
                        'similarity': float(similarities[idx]),
                        'conversation_id': response['conversation_id'],
                        'customer_text': response['customer_text'],
                        'brand_response': response['brand_response']
                    })

            return {
                'status': 'success',
                'query': query,
                'results': results
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }


def build_response_index():
    """Build response retrieval index from conversations."""

    print("=" * 70)
    print("BUILDING RESPONSE RETRIEVAL INDEX")
    print("=" * 70)

    if not SKLEARN_AVAILABLE or not NUMPY_AVAILABLE:
        print("✗ scikit-learn or numpy not available, cannot build index")
        return None

    # Load conversations
    print("\n1. Loading conversations...")
    conversations_path = "data/processed/amazonhelp_conversations.jsonl"
    if not Path(conversations_path).exists():
        print(f"✗ Not found: {conversations_path}")
        return None

    conversations = []
    with open(conversations_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            conversations.append(json.loads(line))
            if (i + 1) % 10000 == 0:
                print(f"  Loaded {i+1:,} conversations...")

    print(f"  ✓ Loaded {len(conversations):,} conversations")

    # Extract response pairs
    print("\n2. Extracting customer-response pairs...")
    responses = []

    for conv in conversations:
        conv_id = conv['conversation_id']
        messages = conv['messages']

        customer_texts = []
        for msg in messages:
            if msg['role'] == 'customer':
                customer_texts.append(msg['text'])
            elif msg['role'] == 'brand' and customer_texts:
                # We have a customer->brand sequence
                customer_context = " ".join(customer_texts)
                brand_response = msg['text']

                responses.append({
                    'conversation_id': conv_id,
                    'customer_text': customer_context,
                    'brand_response': brand_response
                })

                # Reset for next sequence
                customer_texts = []

    print(f"  ✓ Extracted {len(responses):,} customer->brand response pairs")

    if len(responses) < 100:
        print(f"\n✗ Too few response pairs ({len(responses)})")
        print("  Minimum: 100")
        return None

    # Build vectorizer on customer text
    print("\n3. Building TF-IDF vectorizer...")
    customer_texts = [r['customer_text'] for r in responses]

    vectorizer = TfidfVectorizer(
        max_features=3000,
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.9,
        stop_words='english'
    )

    response_vectors = vectorizer.fit_transform(customer_texts)
    print(f"  ✓ {response_vectors.shape[1]} features from {len(customer_texts):,} examples")

    # Save index
    print("\n4. Saving index...")
    index_dir = Path("models/response_retriever")
    index_dir.mkdir(parents=True, exist_ok=True)

    with open(index_dir / "vectorizer.pkl", 'wb') as f:
        pickle.dump(vectorizer, f)

    with open(index_dir / "responses.json", 'w') as f:
        json.dump(responses, f)

    np.save(index_dir / "vectors.npy", response_vectors.toarray())

    config = {
        'num_responses': len(responses),
        'num_features': response_vectors.shape[1],
        'vectorizer_params': {
            'max_features': 3000,
            'ngram_range': [1, 2],
            'min_df': 2,
            'max_df': 0.9
        }
    }

    with open(index_dir / "config.json", 'w') as f:
        json.dump(config, f, indent=2)

    print(f"  ✓ Saved to {index_dir}/")

    print("\n" + "=" * 70)
    print("✓ RESPONSE INDEX BUILT")
    print("=" * 70)
    print(f"\nIndex contains {len(responses):,} historical support interactions\n")

    return vectorizer, responses, response_vectors


if __name__ == "__main__":
    # Test retriever
    retriever = ResponseRetriever()

    if retriever.available:
        print("✓ Response retriever loaded")

        # Test retrieval
        test_query = "Where is my order?"
        print(f"\nTest retrieval for: '{test_query}'")

        result = retriever.retrieve(test_query, top_k=3)
        if result['status'] == 'success':
            for i, res in enumerate(result['results'], 1):
                print(f"\n  Result {i} (similarity: {res['similarity']:.4f})")
                print(f"    Customer: {res['customer_text'][:100]}...")
                print(f"    Response: {res['brand_response'][:100]}...")
    else:
        print("✗ Response retriever not available")
        print("\nTo build retriever, run:")
        print("  python3 scripts/build_response_retriever.py")

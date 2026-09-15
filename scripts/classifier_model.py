#!/usr/bin/env python3
"""
Load and use trained intent classifier for predictions.
"""

import sys
from pathlib import Path
import json
import pickle

sys.path.insert(0, str(Path(__file__).parent.parent))


class IntentClassifier:
    """Wrapper for trained intent classifier."""

    def __init__(self, model_dir="models/intent_classifier"):
        self.model_dir = Path(model_dir)
        self.classifier = None
        self.vectorizer = None
        self.labels = None
        self.available = False

        if self._load():
            self.available = True

    def _load(self):
        """Load model artifacts."""
        try:
            # Load vectorizer
            vectorizer_path = self.model_dir / "vectorizer.pkl"
            if not vectorizer_path.exists():
                return False
            with open(vectorizer_path, 'rb') as f:
                self.vectorizer = pickle.load(f)

            # Load classifier
            classifier_path = self.model_dir / "classifier.pkl"
            if not classifier_path.exists():
                return False
            with open(classifier_path, 'rb') as f:
                self.classifier = pickle.load(f)

            # Load labels
            labels_path = self.model_dir / "labels.json"
            if not labels_path.exists():
                return False
            with open(labels_path, 'r') as f:
                label_data = json.load(f)
            self.labels = label_data['id_to_label']

            return True
        except Exception as e:
            print(f"Failed to load model: {e}")
            return False

    def predict(self, text):
        """Predict intent for text."""
        if not self.available:
            return {
                'status': 'not_available',
                'message': 'Classifier not trained yet'
            }

        try:
            # Vectorize
            X = self.vectorizer.transform([text])

            # Predict
            pred_id = self.classifier.predict(X)[0]
            pred_proba = self.classifier.predict_proba(X)[0]

            # Map to label
            label = self.labels[str(pred_id)]

            # Get confidence
            confidence = float(pred_proba[pred_id])

            # Get top-3 predictions
            top_indices = pred_proba.argsort()[-3:][::-1]
            alternatives = [
                {
                    'intent': self.labels[str(idx)],
                    'confidence': float(pred_proba[idx])
                }
                for idx in top_indices[1:]  # Skip first (it's the prediction)
            ]

            return {
                'status': 'success',
                'intent': label,
                'confidence': confidence,
                'alternatives': alternatives
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    def predict_batch(self, texts):
        """Predict intents for multiple texts."""
        return [self.predict(text) for text in texts]


if __name__ == "__main__":
    # Test classifier
    classifier = IntentClassifier()

    if classifier.available:
        print("✓ Classifier loaded successfully")

        # Test prediction
        test_text = "Where is my order? It should have arrived yesterday."
        result = classifier.predict(test_text)
        print(f"\nTest prediction:")
        print(f"  Input: {test_text}")
        print(f"  Intent: {result['intent']}")
        print(f"  Confidence: {result['confidence']:.4f}")
    else:
        print("✗ Classifier not available - not trained yet")

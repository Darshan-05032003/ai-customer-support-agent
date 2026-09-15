#!/usr/bin/env python3
"""
Offline support pipeline combining intent classification, escalation detection, and response retrieval.
"""

import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.classifier_model import IntentClassifier
from scripts.escalation_detector import EscalationDetector
from scripts.response_retriever import ResponseRetriever


class SupportPipeline:
    """Complete offline support pipeline."""

    def __init__(self):
        self.classifier = IntentClassifier()
        self.retriever = ResponseRetriever()

    def process(self, customer_text, conversation_messages=None):
        """Process customer message through complete pipeline."""

        result = {
            'input': customer_text,
            'timestamp': __import__('datetime').datetime.utcnow().isoformat(),
            'components': {}
        }

        # Step 1: Intent classification
        intent_result = self.classifier.predict(customer_text)
        result['components']['intent'] = {
            'status': intent_result.get('status'),
            'label': intent_result.get('intent'),
            'confidence': intent_result.get('confidence'),
            'alternatives': intent_result.get('alternatives', [])
        }

        # Step 2: Escalation detection
        conv_length = len(conversation_messages) if conversation_messages else 0
        escalation_result = EscalationDetector.detect(
            customer_text,
            messages=conversation_messages,
            conversation_length=conv_length
        )
        result['components']['escalation'] = {
            'status': 'success',
            'required': escalation_result['escalation_required'],
            'confidence': escalation_result['confidence'],
            'signals': escalation_result['signals']
        }

        # Step 3: Response retrieval
        if self.retriever.available:
            retrieval_result = self.retriever.retrieve(customer_text, top_k=3)
            if retrieval_result['status'] == 'success':
                result['components']['retrieval'] = {
                    'status': 'success',
                    'results': retrieval_result['results']
                }
            else:
                result['components']['retrieval'] = {
                    'status': retrieval_result.get('status', 'error'),
                    'message': retrieval_result.get('message')
                }
        else:
            result['components']['retrieval'] = {
                'status': 'not_available',
                'message': 'Response retriever not built'
            }

        # Overall recommendation
        result['recommendation'] = self._recommend_action(result)

        return result

    @staticmethod
    def _recommend_action(result):
        """Recommend action based on pipeline results."""
        escalation_required = result['components']['escalation']['required']

        if escalation_required:
            return {
                'action': 'escalate',
                'reason': 'Escalation signals detected',
                'next_step': 'Route to human agent'
            }

        intent = result['components']['intent'].get('label')
        if intent in ['CUSTOMER_SERVICE_COMPLAINT', 'TECHNICAL_ISSUE']:
            return {
                'action': 'escalate_optional',
                'reason': f'Intent {intent} may benefit from human review',
                'next_step': 'Consider escalation if automated response insufficient'
            }

        if result['components']['retrieval'].get('status') == 'success':
            results = result['components']['retrieval'].get('results', [])
            if results and results[0].get('similarity', 0) > 0.7:
                return {
                    'action': 'use_retrieval',
                    'reason': 'High-similarity historical response available',
                    'next_step': 'Present retrieved response to customer'
                }

        return {
            'action': 'generate',
            'reason': 'No clear escalation or retrieval match',
            'next_step': 'Generate personalized response'
        }


def run_pipeline_example():
    """Run pipeline with example inputs."""

    print("=" * 70)
    print("OFFLINE SUPPORT PIPELINE")
    print("=" * 70)

    pipeline = SupportPipeline()

    # Test cases
    test_cases = [
        {
            'text': 'Where is my order? It should have arrived yesterday.',
            'description': 'Order status inquiry'
        },
        {
            'text': 'I need to speak to a manager! My account was hacked!',
            'description': 'Security escalation'
        },
        {
            'text': 'Can I reset my password?',
            'description': 'Account management'
        },
        {
            'text': 'Your customer service is terrible. I\'m canceling my membership.',
            'description': 'Service complaint with escalation'
        },
    ]

    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*70}")
        print(f"Test {i}: {test['description']}")
        print(f"{'='*70}")
        print(f"Input: {test['text']}")

        result = pipeline.process(test['text'])

        # Intent
        intent = result['components']['intent']
        if intent['status'] == 'success':
            print(f"\nIntent Classification:")
            print(f"  Label: {intent['label']}")
            print(f"  Confidence: {intent['confidence']:.4f}")
        else:
            print(f"\nIntent Classification: NOT AVAILABLE")

        # Escalation
        escalation = result['components']['escalation']
        print(f"\nEscalation Detection:")
        print(f"  Required: {escalation['required']}")
        print(f"  Confidence: {escalation['confidence']:.4f}")
        print(f"  Signals: {', '.join(escalation['signals']) if escalation['signals'] else 'None'}")

        # Retrieval
        retrieval = result['components']['retrieval']
        if retrieval['status'] == 'success':
            results = retrieval.get('results', [])
            print(f"\nResponse Retrieval:")
            if results:
                print(f"  Top result similarity: {results[0]['similarity']:.4f}")
                print(f"  Source: {results[0]['conversation_id']}")
            else:
                print(f"  No relevant responses found")
        else:
            print(f"\nResponse Retrieval: {retrieval.get('message', 'Not available')}")

        # Recommendation
        rec = result['recommendation']
        print(f"\nRecommendation:")
        print(f"  Action: {rec['action']}")
        print(f"  Reason: {rec['reason']}")
        print(f"  Next Step: {rec['next_step']}")


if __name__ == "__main__":
    run_pipeline_example()

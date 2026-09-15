#!/usr/bin/env python3
"""
Intent Detection Service

Provides unified interface to:
1. Use trained supervised classifier if available
2. Fall back to rule-based heuristic if not
"""

import sys
from pathlib import Path
import json
import re

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.classifier_model import IntentClassifier


class HeuristicIntentClassifier:
    """Transparent heuristic-based intent classifier."""

    # Define patterns for each intent
    INTENT_PATTERNS = {
        'ORDER_STATUS': {
            'keywords': ['order', 'status', 'tracking', 'where', 'check', 'track', 'number'],
            'phrases': ['order status', 'tracking number', 'where is', 'check order']
        },
        'DELIVERY_ISSUE': {
            'keywords': ['delivery', 'delivered', 'late', 'delayed', 'arrived', 'receive', 'package'],
            'phrases': ['not delivered', 'late delivery', 'delayed delivery', 'didn\'t arrive']
        },
        'DAMAGED_ITEM': {
            'keywords': ['damaged', 'broken', 'defective', 'crack', 'bent', 'torn', 'arrive'],
            'phrases': ['arrived damaged', 'broken item', 'defective product']
        },
        'REFUND_RETURN': {
            'keywords': ['refund', 'return', 'money', 'back', 'exchange', 'cancel'],
            'phrases': ['how return', 'want refund', 'return item', 'return process']
        },
        'BILLING_PAYMENT': {
            'keywords': ['charge', 'charged', 'payment', 'billing', 'bill', 'invoice', 'paid'],
            'phrases': ['double charged', 'wrong amount', 'billing issue', 'charged twice']
        },
        'ACCOUNT_LOGIN': {
            'keywords': ['account', 'password', 'login', 'access', 'sign', 'reset', 'forgot'],
            'phrases': ['reset password', 'account access', 'forgot password', 'can\'t login']
        },
        'PRIME_SUBSCRIPTION': {
            'keywords': ['prime', 'membership', 'subscription', 'cancel', 'renew', 'benefit'],
            'phrases': ['cancel prime', 'prime membership', 'prime subscription', 'cancel membership']
        },
        'PRODUCT_INFORMATION': {
            'keywords': ['product', 'information', 'details', 'specs', 'features', 'how'],
            'phrases': ['product info', 'product details', 'how to use', 'specifications']
        },
        'SHIPPING_ADDRESS': {
            'keywords': ['address', 'shipping', 'ship', 'deliver', 'location'],
            'phrases': ['shipping address', 'ship to', 'change address', 'wrong address']
        },
        'TECHNICAL_ISSUE': {
            'keywords': ['technical', 'bug', 'error', 'crash', 'website', 'app', 'problem'],
            'phrases': ['website issue', 'app problem', 'technical issue', 'website down']
        },
        'CUSTOMER_SERVICE_COMPLAINT': {
            'keywords': ['complaint', 'frustrated', 'unhappy', 'terrible', 'poor', 'bad'],
            'phrases': ['customer service', 'poor service', 'terrible service', 'unhappy']
        },
        'GENERAL_INQUIRY': {
            'keywords': ['help', 'question', 'need', 'assistance', 'support'],
            'phrases': ['need help', 'can help', 'quick question']
        }
    }

    @classmethod
    def classify(cls, text):
        """Classify intent using keyword matching."""
        text_lower = text.lower()
        scores = {}

        for intent, patterns in cls.INTENT_PATTERNS.items():
            score = 0

            # Check phrases (higher weight)
            for phrase in patterns['phrases']:
                if phrase in text_lower:
                    score += 3

            # Check keywords
            for keyword in patterns['keywords']:
                if re.search(r'\b' + keyword + r'\b', text_lower):
                    score += 1

            scores[intent] = score

        # Get top intent
        if not scores or max(scores.values()) == 0:
            top_intent = 'GENERAL_INQUIRY'
            matched_signals = []
        else:
            top_intent = max(scores, key=scores.get)
            # Get matched signals
            matched_signals = []
            for phrase in cls.INTENT_PATTERNS[top_intent]['phrases']:
                if phrase in text_lower:
                    matched_signals.append(phrase)
            for keyword in cls.INTENT_PATTERNS[top_intent]['keywords']:
                if re.search(r'\b' + keyword + r'\b', text_lower):
                    matched_signals.append(keyword)
            matched_signals = list(set(matched_signals))[:3]  # Top 3 signals

        return {
            'label': top_intent,
            'mode': 'heuristic',
            'signals': matched_signals,
            'confidence': None  # No fabricated confidence for heuristic
        }


class IntentService:
    """Unified intent detection service."""

    def __init__(self):
        """Initialize service with classifier and heuristic."""
        self.supervised_classifier = IntentClassifier()
        self.heuristic_classifier = HeuristicIntentClassifier()

    def get_status(self):
        """Get status of supervised classifier."""
        if self.supervised_classifier.available:
            return 'available'
        else:
            return 'unavailable'

    def classify(self, text):
        """
        Classify intent using priority:
        1. Supervised classifier if available
        2. Heuristic classifier otherwise
        """

        # Try supervised classifier first
        if self.supervised_classifier.available:
            result = self.supervised_classifier.predict(text)
            if result.get('status') == 'success':
                return {
                    'label': result['intent'],
                    'confidence': result['confidence'],
                    'mode': 'supervised',
                    'alternatives': result.get('alternatives', [])
                }

        # Fall back to heuristic
        return self.heuristic_classifier.classify(text)


if __name__ == "__main__":
    # Test
    service = IntentService()

    test_queries = [
        "Where is my order?",
        "My package was supposed to arrive yesterday.",
        "I forgot my password.",
        "The website is crashing.",
        "I need to speak to a manager!"
    ]

    print("Intent Service Test\n" + "=" * 50)
    for query in test_queries:
        result = service.classify(query)
        mode = result['mode']
        intent = result['label']
        if result['confidence']:
            print(f"\n{query}")
            print(f"  Intent: {intent}")
            print(f"  Confidence: {result['confidence']:.2%}")
            print(f"  Mode: {mode} (supervised)")
        else:
            signals = ', '.join(result.get('signals', []))
            print(f"\n{query}")
            print(f"  Intent: {intent}")
            print(f"  Mode: {mode} (heuristic)")
            print(f"  Signals: {signals}")

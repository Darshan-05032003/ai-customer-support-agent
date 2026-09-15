#!/usr/bin/env python3
"""
Response Generation Service

Generates grounded support responses using retrieval and templates.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


class ResponseService:
    """Grounded response generation service."""

    # Intent-based response templates (safe fallbacks)
    INTENT_TEMPLATES = {
        'ORDER_STATUS': "I can help you track your order. Could you please provide your order number so I can check the latest status for you?",
        'DELIVERY_ISSUE': "I understand your package hasn't arrived as expected. To help you, could you please share your order number and the expected delivery date?",
        'DAMAGED_ITEM': "I apologize that your item arrived in damaged condition. I'd like to help make this right. Could you provide your order number so we can arrange a replacement or refund?",
        'REFUND_RETURN': "I can help you with a return or refund. To get started, could you please provide your order number?",
        'BILLING_PAYMENT': "I apologize for the billing issue. To investigate this, could you please provide the order number or transaction ID involved?",
        'ACCOUNT_LOGIN': "I can help you regain access to your account. For security purposes, I'll need to verify some information. What email address is associated with your account?",
        'PRIME_SUBSCRIPTION': "I'm happy to help with your Prime membership question. What would you like to know about your subscription?",
        'PRODUCT_INFORMATION': "I'd be glad to provide product information. Which item would you like to know more about?",
        'SHIPPING_ADDRESS': "I can help you with your shipping address. To make any changes, could you provide your order number?",
        'TECHNICAL_ISSUE': "I apologize for the technical difficulty you're experiencing. Could you tell me more about what you're seeing?",
        'CUSTOMER_SERVICE_COMPLAINT': "I sincerely apologize for your experience. I want to help make this right. Could you tell me more about what happened?",
        'GENERAL_INQUIRY': "I'm here to help! Could you tell me more about what you need assistance with?"
    }

    def __init__(self, retrieval_service):
        """Initialize service with retrieval service."""
        self.retrieval_service = retrieval_service

    def generate(self, text, intent_label, escalation_required=False):
        """
        Generate a grounded support response.

        Args:
            text: Customer message
            intent_label: Detected intent
            escalation_required: Whether escalation is needed

        Returns:
            {
                'text': str,
                'source': 'escalation|historical_retrieval|template|fallback',
                'reasoning': str,
                'sources': [list of historical examples used]
            }
        """

        # Case 1: Escalation required
        if escalation_required:
            return {
                'text': "This issue requires additional assistance. I'm escalating this to our support team who will help you shortly.",
                'source': 'escalation',
                'reasoning': 'Escalation required based on detected signals',
                'sources': []
            }

        # Case 2: Try historical retrieval
        best_match = self.retrieval_service.get_best_response(text)

        if best_match and best_match['similarity'] > 0.70:
            # Strong match - use historical response with minimal personalization
            response_text = best_match['brand_response']

            return {
                'text': response_text,
                'source': 'historical_retrieval',
                'reasoning': f'High-similarity historical response (similarity: {best_match["similarity"]:.1%})',
                'sources': [
                    {
                        'similarity': best_match['similarity'],
                        'conversation_id': best_match['conversation_id'],
                        'customer_query': best_match['customer_text'][:150],
                        'historical_response': best_match['brand_response'][:150]
                    }
                ]
            }

        if best_match and best_match['similarity'] > 0.45:
            # Moderate match - use as guidance but make more generic
            base_response = best_match['brand_response']

            # Extract intent-appropriate greeting
            response_text = f"Thank you for reaching out. {self._extract_intent_action(intent_label)}"

            return {
                'text': response_text,
                'source': 'historical_retrieval',
                'reasoning': f'Moderate-similarity historical response (similarity: {best_match["similarity"]:.1%})',
                'sources': [
                    {
                        'similarity': best_match['similarity'],
                        'conversation_id': best_match['conversation_id'],
                        'customer_query': best_match['customer_text'][:150],
                        'historical_response': base_response[:150]
                    }
                ]
            }

        # Case 3: Use intent-based template
        template = self.INTENT_TEMPLATES.get(intent_label, self.INTENT_TEMPLATES['GENERAL_INQUIRY'])

        return {
            'text': template,
            'source': 'template',
            'reasoning': f'No strong historical match. Using template for {intent_label}',
            'sources': []
        }

    def _extract_intent_action(self, intent_label):
        """Extract action phrase for intent."""
        actions = {
            'ORDER_STATUS': "I can help you track your order.",
            'DELIVERY_ISSUE': "I understand your delivery hasn't arrived as expected.",
            'DAMAGED_ITEM': "I apologize your item arrived damaged.",
            'REFUND_RETURN': "I can help you with a return or refund.",
            'BILLING_PAYMENT': "I'll help resolve this billing issue.",
            'ACCOUNT_LOGIN': "I can help you access your account.",
            'PRIME_SUBSCRIPTION': "I'm happy to help with your Prime subscription.",
            'PRODUCT_INFORMATION': "I can provide the information you need.",
            'SHIPPING_ADDRESS': "I can help with your shipping address.",
            'TECHNICAL_ISSUE': "I'm sorry you're experiencing this technical issue.",
            'CUSTOMER_SERVICE_COMPLAINT': "I sincerely apologize for your experience.",
            'GENERAL_INQUIRY': "How can I assist you?"
        }
        return actions.get(intent_label, "How can I help?")


if __name__ == "__main__":
    # Test
    from src.retrieval_service import RetrievalService

    retrieval_service = RetrievalService()
    service = ResponseService(retrieval_service)

    test_cases = [
        ("Where is my order?", "ORDER_STATUS", False),
        ("My account was hacked!", "GENERAL_INQUIRY", True),
        ("How do I return this?", "REFUND_RETURN", False),
    ]

    print("Response Service Test\n" + "=" * 50)
    for text, intent, escalation in test_cases:
        result = service.generate(text, intent, escalation)
        print(f"\n{text}")
        print(f"  Intent: {intent}")
        print(f"  Escalation: {escalation}")
        print(f"  Source: {result['source']}")
        print(f"  Response: {result['text']}")
        if result['sources']:
            print(f"  Historical sources: {len(result['sources'])}")

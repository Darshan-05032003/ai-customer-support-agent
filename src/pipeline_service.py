#!/usr/bin/env python3
"""
Support Pipeline Service

Orchestrates the complete AI-assisted support workflow.
"""

import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))


class SupportPipeline:
    """Complete support pipeline orchestration."""

    def __init__(self, intent_service, escalation_service, retrieval_service, response_service):
        """Initialize pipeline with services."""
        self.intent_service = intent_service
        self.escalation_service = escalation_service
        self.retrieval_service = retrieval_service
        self.response_service = response_service

    def process(self, customer_message, conversation_context=None):
        """
        Process a customer message through the complete pipeline.

        Args:
            customer_message: Customer support query
            conversation_context: Optional ConversationContext for multi-turn awareness

        Returns:
            Complete structured result with all analysis
        """
        result = {
            'timestamp': datetime.utcnow().isoformat(),
            'input': customer_message,
            'analysis': {},
            'context': None
        }

        try:
            # Store context info for transparency
            if conversation_context:
                result['context'] = {
                    'message_count': len(conversation_context.messages),
                    'has_escalation_history': conversation_context.has_escalation_signals(),
                    'intent_pattern': conversation_context.get_intent_pattern(),
                    'escalation_trend': conversation_context.get_escalation_trend()
                }

            # Step 1: Detect Intent
            intent_result = self.intent_service.classify(customer_message)
            result['analysis']['intent'] = {
                'label': intent_result['label'],
                'mode': intent_result['mode'],
                'confidence': intent_result.get('confidence'),
                'alternatives': intent_result.get('alternatives', []),
                'signals': intent_result.get('signals', [])
            }

            # Step 2: Detect Escalation
            escalation_result = self.escalation_service.detect(customer_message)
            result['analysis']['escalation'] = {
                'required': escalation_result['required'],
                'mode': escalation_result['mode'],
                'signals': escalation_result['signals']
            }

            # Escalation amplification: Check if conversation already has escalation signals
            if conversation_context and conversation_context.has_escalation_signals():
                # If escalation was already flagged, keep it escalated
                if not result['analysis']['escalation']['required']:
                    result['analysis']['escalation']['required'] = True
                    result['analysis']['escalation']['signals'].append('prior_escalation_in_conversation')

            # Step 3: Retrieve Similar Responses
            if self.retrieval_service.is_available():
                retrieval_result = self.retrieval_service.retrieve(customer_message, top_k=3)
                result['analysis']['retrieval'] = {
                    'status': retrieval_result['status'],
                    'count': len(retrieval_result.get('results', [])),
                    'results': retrieval_result.get('results', [])
                }
            else:
                result['analysis']['retrieval'] = {
                    'status': 'unavailable',
                    'count': 0,
                    'results': []
                }

            # Step 4: Generate Response
            response_result = self.response_service.generate(
                customer_message,
                result['analysis']['intent']['label'],
                result['analysis']['escalation']['required']
            )

            result['analysis']['response'] = {
                'text': response_result['text'],
                'source': response_result['source'],
                'reasoning': response_result['reasoning'],
                'sources': response_result.get('sources', [])
            }

            # Step 5: Generate Recommendation
            result['recommendation'] = self._generate_recommendation(result)

            result['status'] = 'success'

        except Exception as e:
            print(f"[ERROR] Pipeline error: {e}")
            result['status'] = 'error'
            result['error'] = str(e)

        return result

    @staticmethod
    def _generate_recommendation(result):
        """Generate next action recommendation."""
        analysis = result.get('analysis', {})
        escalation_required = analysis.get('escalation', {}).get('required', False)

        if escalation_required:
            return {
                'action': 'escalate',
                'description': 'Route to human agent',
                'reason': 'Escalation signals detected'
            }

        intent_mode = analysis.get('intent', {}).get('mode')
        if intent_mode == 'heuristic':
            return {
                'action': 'clarify',
                'description': 'Request more information from customer',
                'reason': 'Intent detected using heuristic mode (classifier not available)'
            }

        retrieval_status = analysis.get('retrieval', {}).get('status')
        if retrieval_status == 'success':
            count = analysis.get('retrieval', {}).get('count', 0)
            if count > 0:
                return {
                    'action': 'present_response',
                    'description': 'Present historical response to customer',
                    'reason': 'High-similarity historical response available'
                }

        return {
            'action': 'respond',
            'description': 'Send generated response',
            'reason': 'Use template-based response for this intent'
        }


if __name__ == "__main__":
    # Test
    from src.intent_service import IntentService
    from src.escalation_service import EscalationService
    from src.retrieval_service import RetrievalService
    from src.response_service import ResponseService

    intent_svc = IntentService()
    escalation_svc = EscalationService()
    retrieval_svc = RetrievalService()
    response_svc = ResponseService(retrieval_svc)

    pipeline = SupportPipeline(intent_svc, escalation_svc, retrieval_svc, response_svc)

    test_queries = [
        "Where is my order?",
        "My package is late and I need to speak to a manager!",
        "I forgot my password.",
    ]

    print("Pipeline Test\n" + "=" * 70)
    for query in test_queries:
        print(f"\n{query}")
        print("-" * 70)

        result = pipeline.process(query)

        if result['status'] == 'success':
            print(f"Intent: {result['analysis']['intent']['label']} ({result['analysis']['intent']['mode']})")
            print(f"Escalation: {result['analysis']['escalation']['required']}")
            print(f"Response: {result['analysis']['response']['text'][:100]}...")
            print(f"Action: {result['recommendation']['action']}")
        else:
            print(f"Error: {result.get('error')}")

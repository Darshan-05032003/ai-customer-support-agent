#!/usr/bin/env python3
"""
Phase 6 - Customer Support AI Web Application

A fully functional local web application for demonstrating AI-assisted customer support.
Supports multi-turn conversations with context awareness.
"""

import sys
from pathlib import Path
import json
from datetime import datetime
import uuid

sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Flask, render_template, jsonify, request, session
from flask_cors import CORS

# Import Phase 6 services
from src.intent_service import IntentService
from src.escalation_service import EscalationService
from src.retrieval_service import RetrievalService
from src.response_service import ResponseService
from src.pipeline_service import SupportPipeline
from src.conversation_service import ConversationService

# Initialize Flask app
app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'hiver-phase6-demo-key-' + str(uuid.uuid4())
CORS(app)

# Initialize services
try:
    intent_service = IntentService()
    escalation_service = EscalationService()
    retrieval_service = RetrievalService()
    response_service = ResponseService(retrieval_service)
    pipeline = SupportPipeline(intent_service, escalation_service, retrieval_service, response_service)
    conversation_service = ConversationService()
    print("[INIT] All services initialized successfully")
except Exception as e:
    print(f"[WARN] Service initialization error: {e}")
    pipeline = None
    conversation_service = None


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/')
def index():
    """Serve the chat interface."""
    return render_template('chat.html')


@app.route('/api/health')
def health():
    """Health check endpoint showing component status."""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.utcnow().isoformat(),
        'components': {
            'intent_classifier': intent_service.get_status() if intent_service else 'unavailable',
            'escalation_detector': 'available',
            'retrieval_index': 'available' if retrieval_service.is_available() else 'unavailable'
        }
    })


@app.route('/api/chat', methods=['POST'])
def chat():
    """Process a customer support message."""
    try:
        data = request.json

        # Validate request
        if not data:
            return jsonify({
                'status': 'error',
                'error': {
                    'code': 'INVALID_JSON',
                    'message': 'Request body must be valid JSON'
                }
            }), 400

        message = data.get('message', '').strip()

        # Validate message
        if not message:
            return jsonify({
                'status': 'error',
                'error': {
                    'code': 'EMPTY_MESSAGE',
                    'message': 'Please enter a support message.'
                }
            }), 400

        if len(message) > 2000:
            return jsonify({
                'status': 'error',
                'error': {
                    'code': 'MESSAGE_TOO_LONG',
                    'message': 'Message must be less than 2000 characters.'
                }
            }), 400

        # Process through pipeline
        if not pipeline:
            return jsonify({
                'status': 'error',
                'error': {
                    'code': 'SERVICE_UNAVAILABLE',
                    'message': 'Support pipeline not initialized.'
                }
            }), 503

        result = pipeline.process(message)

        return jsonify({
            'status': 'success',
            'result': result
        }), 200

    except Exception as e:
        print(f"[ERROR] Chat endpoint error: {e}")
        return jsonify({
            'status': 'error',
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'An unexpected error occurred. Please try again.'
            }
        }), 500


@app.route('/api/examples')
def get_examples():
    """Get example queries for demo."""
    examples = [
        {
            'query': 'Where is my order?',
            'intent': 'ORDER_STATUS',
            'category': 'Order & Logistics'
        },
        {
            'query': 'My package was supposed to arrive yesterday.',
            'intent': 'DELIVERY_ISSUE',
            'category': 'Order & Logistics'
        },
        {
            'query': 'How do I return this item?',
            'intent': 'REFUND_RETURN',
            'category': 'Returns & Refunds'
        },
        {
            'query': 'Can I cancel my Prime membership?',
            'intent': 'PRIME_SUBSCRIPTION',
            'category': 'Account & Subscription'
        },
        {
            'query': 'I forgot my password. How do I reset it?',
            'intent': 'ACCOUNT_LOGIN',
            'category': 'Account & Subscription'
        },
        {
            'query': 'The website is crashing when I try to checkout.',
            'intent': 'TECHNICAL_ISSUE',
            'category': 'Technical'
        },
        {
            'query': 'I was charged twice for the same order.',
            'intent': 'BILLING_PAYMENT',
            'category': 'Billing'
        },
        {
            'query': 'What are the specifications for this laptop?',
            'intent': 'PRODUCT_INFORMATION',
            'category': 'Product Info'
        },
        {
            'query': 'I need to change my shipping address.',
            'intent': 'SHIPPING_ADDRESS',
            'category': 'Delivery'
        },
        {
            'query': 'The item I received is broken.',
            'intent': 'DAMAGED_ITEM',
            'category': 'Product Issues'
        },
        {
            'query': 'Your customer service has been absolutely terrible!',
            'intent': 'CUSTOMER_SERVICE_COMPLAINT',
            'category': 'Complaints'
        },
        {
            'query': 'I need to speak to a manager right now!',
            'intent': 'GENERAL_INQUIRY',
            'category': 'Escalation'
        }
    ]
    return jsonify(examples)


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'status': 'error',
        'error': {
            'code': 'NOT_FOUND',
            'message': 'Endpoint not found.'
        }
    }), 404


@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors."""
    return jsonify({
        'status': 'error',
        'error': {
            'code': 'METHOD_NOT_ALLOWED',
            'message': 'HTTP method not allowed.'
        }
    }), 405


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({
        'status': 'error',
        'error': {
            'code': 'INTERNAL_ERROR',
            'message': 'An unexpected server error occurred.'
        }
    }), 500


if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("HIVER SUPPORT AI - PHASE 6")
    print("=" * 70)
    print("\nStarting application on http://localhost:5000")
    print("Press Ctrl+C to stop.\n")

    app.run(debug=True, port=5000, use_reloader=False)

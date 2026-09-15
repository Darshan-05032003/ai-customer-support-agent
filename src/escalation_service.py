#!/usr/bin/env python3
"""
Escalation Detection Service

Provides rule-based escalation detection with optional ML model integration.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.escalation_detector import EscalationDetector


class EscalationService:
    """Unified escalation detection service."""

    def __init__(self):
        """Initialize service."""
        self.rule_detector = EscalationDetector()

    def detect(self, text, messages=None, conversation_length=None):
        """
        Detect if escalation is required.

        Args:
            text: Customer message text
            messages: Full conversation messages (optional)
            conversation_length: Number of messages (optional)

        Returns:
            {
                'required': bool,
                'mode': 'rule_based',
                'signals': [list of detected signals],
                'confidence': float or None
            }
        """
        result = self.rule_detector.detect(text, messages, conversation_length)

        return {
            'required': result['escalation_required'],
            'mode': 'rule_based',
            'signals': result['signals'],
            'confidence': None  # Rule-based, no confidence needed
        }


if __name__ == "__main__":
    # Test
    service = EscalationService()

    test_cases = [
        ("Where is my order?", False),
        ("I need to speak to a manager NOW!", True),
        ("My account was hacked!", True),
        ("This is unacceptable. I'm canceling my membership.", True),
        ("Can I track my delivery?", False),
    ]

    print("Escalation Service Test\n" + "=" * 50)
    for text, expected in test_cases:
        result = service.detect(text)
        status = "✓" if result['required'] == expected else "✗"
        print(f"\n{status} '{text}'")
        print(f"  Escalation: {result['required']}")
        print(f"  Signals: {', '.join(result['signals']) if result['signals'] else 'None'}")

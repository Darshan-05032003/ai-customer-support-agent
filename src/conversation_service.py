#!/usr/bin/env python3
"""
Conversation Context Service

Maintains session-level conversation state for multi-turn support.
Passes conversation history to the pipeline for context-aware processing.
"""

import sys
from pathlib import Path
from datetime import datetime
from collections import deque

sys.path.insert(0, str(Path(__file__).parent.parent))


class ConversationContext:
    """Manages conversation state for a single session."""

    def __init__(self, session_id, max_history=10):
        """
        Initialize conversation context.

        Args:
            session_id: Unique identifier for this conversation
            max_history: Maximum number of turns to keep in memory
        """
        self.session_id = session_id
        self.max_history = max_history
        self.messages = deque(maxlen=max_history)
        self.created_at = datetime.utcnow()
        self.last_updated = datetime.utcnow()
        self.escalation_history = []  # Track escalation signals across turns
        self.intent_history = []  # Track detected intents across turns

    def add_user_message(self, text):
        """
        Add a user message to the conversation.

        Args:
            text: Customer message

        Returns:
            Message object with metadata
        """
        message = {
            'role': 'user',
            'text': text,
            'timestamp': datetime.utcnow().isoformat()
        }
        self.messages.append(message)
        self.last_updated = datetime.utcnow()
        return message

    def add_assistant_message(self, text, analysis):
        """
        Add an assistant message with analysis results.

        Args:
            text: Assistant response
            analysis: Full analysis dict from pipeline (intent, escalation, etc.)

        Returns:
            Message object with metadata
        """
        message = {
            'role': 'assistant',
            'text': text,
            'timestamp': datetime.utcnow().isoformat(),
            'analysis': analysis
        }
        self.messages.append(message)
        self.last_updated = datetime.utcnow()

        # Track escalation and intent history
        if 'escalation' in analysis:
            self.escalation_history.append({
                'turn': len(self.messages),
                'required': analysis['escalation']['required'],
                'signals': analysis['escalation'].get('signals', [])
            })

        if 'intent' in analysis:
            self.intent_history.append({
                'turn': len(self.messages),
                'label': analysis['intent']['label'],
                'mode': analysis['intent']['mode']
            })

        return message

    def get_conversation_history(self, include_analysis=True):
        """
        Get conversation history for context passing.

        Args:
            include_analysis: Whether to include full analysis or just text

        Returns:
            List of message objects
        """
        if include_analysis:
            return list(self.messages)
        else:
            # Return simplified version (just role and text)
            return [
                {
                    'role': msg['role'],
                    'text': msg['text']
                }
                for msg in self.messages
            ]

    def get_recent_context(self, num_turns=3):
        """
        Get recent conversation turns for context awareness.

        Args:
            num_turns: Number of recent turns to return

        Returns:
            Recent messages
        """
        recent = list(self.messages)[-num_turns*2:] if self.messages else []
        return recent

    def has_escalation_signals(self):
        """
        Check if conversation has escalation signals across turns.

        Returns:
            True if any escalation signals detected
        """
        return any(e['required'] for e in self.escalation_history)

    def get_intent_pattern(self):
        """
        Get pattern of intents across conversation.

        Useful for detecting if user is discussing multiple issues.

        Returns:
            List of intents in order
        """
        return [i['label'] for i in self.intent_history]

    def is_same_intent(self):
        """
        Check if conversation is about the same intent (coherent topic).

        Returns:
            True if all detected intents are the same
        """
        if not self.intent_history:
            return True
        first_intent = self.intent_history[0]['label']
        return all(i['label'] == first_intent for i in self.intent_history)

    def get_escalation_trend(self):
        """
        Get trend of escalation signals across conversation.

        Useful for detecting if situation is improving or worsening.

        Returns:
            'increasing', 'decreasing', 'stable', or None
        """
        if len(self.escalation_history) < 2:
            return None

        # Simple trend analysis
        recent = self.escalation_history[-2:]
        if recent[-1]['required'] and not recent[0]['required']:
            return 'increasing'
        elif not recent[-1]['required'] and recent[0]['required']:
            return 'decreasing'
        else:
            return 'stable'

    def to_dict(self):
        """
        Export conversation state as dictionary.

        Returns:
            State dictionary
        """
        return {
            'session_id': self.session_id,
            'created_at': self.created_at.isoformat(),
            'last_updated': self.last_updated.isoformat(),
            'message_count': len(self.messages),
            'messages': list(self.messages),
            'escalation_history': self.escalation_history,
            'intent_history': self.intent_history,
            'has_escalation': self.has_escalation_signals(),
            'intent_pattern': self.get_intent_pattern(),
            'escalation_trend': self.get_escalation_trend()
        }

    def clear(self):
        """Clear conversation history."""
        self.messages.clear()
        self.escalation_history.clear()
        self.intent_history.clear()
        self.last_updated = datetime.utcnow()


class ConversationService:
    """Manages multiple conversation contexts."""

    def __init__(self):
        """Initialize conversation service."""
        self.conversations = {}  # session_id -> ConversationContext
        self.max_sessions = 100  # Limit in-memory sessions

    def get_or_create(self, session_id):
        """
        Get existing conversation or create new one.

        Args:
            session_id: Unique session identifier

        Returns:
            ConversationContext
        """
        if session_id not in self.conversations:
            if len(self.conversations) >= self.max_sessions:
                # Remove oldest conversation
                oldest = min(
                    self.conversations.items(),
                    key=lambda x: x[1].last_updated
                )
                del self.conversations[oldest[0]]

            self.conversations[session_id] = ConversationContext(session_id)

        return self.conversations[session_id]

    def get(self, session_id):
        """
        Get existing conversation.

        Args:
            session_id: Session identifier

        Returns:
            ConversationContext or None
        """
        return self.conversations.get(session_id)

    def delete(self, session_id):
        """
        Delete a conversation.

        Args:
            session_id: Session identifier
        """
        if session_id in self.conversations:
            del self.conversations[session_id]

    def list_sessions(self):
        """
        List all active sessions.

        Returns:
            List of session IDs
        """
        return list(self.conversations.keys())

    def get_stats(self):
        """
        Get service statistics.

        Returns:
            Statistics dictionary
        """
        return {
            'active_sessions': len(self.conversations),
            'max_sessions': self.max_sessions,
            'total_messages': sum(len(c.messages) for c in self.conversations.values()),
            'average_messages_per_session': (
                sum(len(c.messages) for c in self.conversations.values()) /
                len(self.conversations) if self.conversations else 0
            )
        }


if __name__ == "__main__":
    # Test
    service = ConversationService()

    # Create a session
    session_id = "test_session_1"
    conv = service.get_or_create(session_id)

    # Simulate conversation
    conv.add_user_message("Where is my order?")
    conv.add_assistant_message(
        "I can help track your order.",
        {
            'intent': {'label': 'ORDER_STATUS', 'mode': 'heuristic'},
            'escalation': {'required': False, 'signals': []}
        }
    )

    conv.add_user_message("It's been 5 days!")
    conv.add_assistant_message(
        "I understand your frustration.",
        {
            'intent': {'label': 'DELIVERY_ISSUE', 'mode': 'heuristic'},
            'escalation': {'required': False, 'signals': ['frustration']}
        }
    )

    conv.add_user_message("I need to speak to a manager NOW!")
    conv.add_assistant_message(
        "Escalating to support team.",
        {
            'intent': {'label': 'CUSTOMER_SERVICE_COMPLAINT', 'mode': 'heuristic'},
            'escalation': {'required': True, 'signals': ['explicit_escalation', 'frustration']}
        }
    )

    # Test analysis
    print("Conversation Service Test")
    print("=" * 70)
    print(f"Session: {session_id}")
    print(f"Messages: {len(conv.messages)}")
    print(f"Has escalation: {conv.has_escalation_signals()}")
    print(f"Intent pattern: {conv.get_intent_pattern()}")
    print(f"Escalation trend: {conv.get_escalation_trend()}")
    print(f"Same intent: {conv.is_same_intent()}")

    print("\nService stats:")
    print(service.get_stats())

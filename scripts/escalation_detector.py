#!/usr/bin/env python3
"""
Escalation detection using rule-based baseline and ML model.
"""

import sys
from pathlib import Path
import json
import re
import pickle
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import precision_recall_fscore_support, confusion_matrix
except ImportError:
    print("Installing scikit-learn...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "scikit-learn"])


class EscalationDetector:
    """Rule-based escalation detection."""

    # Patterns
    EXPLICIT_REQUEST = [
        r'speak\s+(to|with)',
        r'manager',
        r'supervisor',
        r'escalate',
        r'human',
        r'agent',
        r'representative',
        r'higher\s+level',
        r'upper\s+management'
    ]

    SECURITY_SIGNALS = [
        r'hacked',
        r'fraud',
        r'unauthorized',
        r'security',
        r'breach',
        r'compromised',
        r'stolen',
        r'account\s+access'
    ]

    FRUSTRATION_SIGNALS = [
        r'unacceptable',
        r'terrible',
        r'awful',
        r'disgusting',
        r'worst',
        r'never\s+again',
        r'cancel.*membership',
        r'switch\s+providers',
        r'never.*use.*again'
    ]

    REPEATED_FAILURE = [
        r'again',
        r'another',
        r'still',
        r'repeat',
        r'multiple.*times',
        r'tried.*multiple',
        r'three.*times',
        r'third.*time'
    ]

    POLICY_EXCEPTION = [
        r'exception',
        r'special\s+case',
        r'unusual',
        r'never\s+happened',
        r'unprecedented'
    ]

    @staticmethod
    def _check_patterns(text, patterns):
        """Check if text matches any pattern."""
        text_lower = text.lower()
        for pattern in patterns:
            if re.search(pattern, text_lower):
                return True
        return False

    @staticmethod
    def _count_customer_turns(messages):
        """Count customer turns in conversation."""
        turns = 0
        last_role = None
        for msg in messages:
            if msg['role'] == 'customer' and last_role != 'customer':
                turns += 1
            last_role = msg['role']
        return turns

    @classmethod
    def detect(cls, text, messages=None, conversation_length=None):
        """Detect if escalation is required."""
        signals = []

        # Check explicit request
        if cls._check_patterns(text, cls.EXPLICIT_REQUEST):
            signals.append('explicit_escalation_request')

        # Check security
        if cls._check_patterns(text, cls.SECURITY_SIGNALS):
            signals.append('security_concern')

        # Check frustration
        if cls._check_patterns(text, cls.FRUSTRATION_SIGNALS):
            signals.append('high_frustration')

        # Check repeated failure
        if cls._check_patterns(text, cls.REPEATED_FAILURE):
            signals.append('repeated_issue')

        # Check policy exception
        if cls._check_patterns(text, cls.POLICY_EXCEPTION):
            signals.append('policy_exception_needed')

        # Check conversation length (proxy for failed attempts)
        if conversation_length and conversation_length > 10:
            signals.append('long_conversation')

        # Check customer turns
        if messages:
            turns = cls._count_customer_turns(messages)
            if turns >= 3:
                signals.append('multiple_customer_turns')

        # Decision
        if 'security_concern' in signals or 'explicit_escalation_request' in signals:
            required = True
        elif len(signals) >= 2:
            required = True
        else:
            required = False

        return {
            'escalation_required': required,
            'signals': signals,
            'confidence': min(0.95, 0.5 + len(signals) * 0.1)  # Heuristic confidence
        }


def train_escalation_model():
    """Train ML-based escalation detector."""

    print("=" * 70)
    print("TRAINING ESCALATION MODEL")
    print("=" * 70)

    # Check if labeled dataset exists
    labeled_path = "data/evaluation/golden_labeled.jsonl"
    if not Path(labeled_path).exists():
        print("\n✗ Labeled dataset not found.")
        print("  Run: python3 scripts/build_labeled_dataset.py")
        return None

    # Load dataset
    print("\n1. Loading labeled dataset...")
    records = []
    with open(labeled_path, 'r', encoding='utf-8') as f:
        for line in f:
            records.append(json.loads(line))

    print(f"  ✓ Loaded {len(records)} records")

    # Check minimum threshold
    if len(records) < 50:
        print(f"\n✗ Only {len(records)} labeled records available.")
        print("  Minimum for training: 50")
        return None

    # Prepare data
    print("\n2. Preparing escalation data...")
    X = [r['text'] for r in records]
    y = [1 if r['escalation_required'] == 'yes' else 0 for r in records]

    escalation_count = sum(y)
    print(f"  ✓ {len(X)} examples")
    print(f"  Escalation required: {escalation_count} ({100*escalation_count/len(y):.1f}%)")
    print(f"  No escalation: {len(y)-escalation_count} ({100*(len(y)-escalation_count)/len(y):.1f}%)")

    # Split data
    print("\n3. Splitting data...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print(f"  Train: {len(X_train)} ({sum(y_train)} escalations)")
    print(f"  Test:  {len(X_test)} ({sum(y_test)} escalations)")

    # Vectorize
    print("\n4. Vectorizing...")
    vectorizer = TfidfVectorizer(
        max_features=1000,
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.9
    )

    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    print(f"  ✓ {X_train_vec.shape[1]} features")

    # Train
    print("\n5. Training Logistic Regression...")
    model = LogisticRegression(
        C=1.0,
        max_iter=1000,
        class_weight='balanced',
        random_state=42
    )

    model.fit(X_train_vec, y_train)
    print("  ✓ Training complete")

    # Evaluate
    print("\n6. Evaluation on test set...")
    y_pred = model.predict(X_test_vec)

    # Calculate metrics
    precision, recall, f1, support = precision_recall_fscore_support(
        y_test, y_pred, labels=[0, 1], average=None
    )

    print(f"\n  No Escalation (0):")
    print(f"    Precision: {precision[0]:.4f}")
    print(f"    Recall:    {recall[0]:.4f}")
    print(f"    F1:        {f1[0]:.4f}")
    print(f"    Support:   {support[0]}")

    print(f"\n  Escalation Required (1):")
    print(f"    Precision: {precision[1]:.4f}")
    print(f"    Recall:    {recall[1]:.4f}")
    print(f"    F1:        {f1[1]:.4f}")
    print(f"    Support:   {support[1]}")

    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    tn, fp, fn, tp = cm.ravel()

    print(f"\n  Confusion Matrix:")
    print(f"    True Negatives:  {tn} (correctly identified no escalation)")
    print(f"    False Positives: {fp} (incorrectly flagged as escalation)")
    print(f"    False Negatives: {fn} (missed escalation - CRITICAL)")
    print(f"    True Positives:  {tp} (correctly identified escalation)")

    # Save model
    print("\n7. Saving model artifacts...")
    models_dir = Path("models/escalation_detector")
    models_dir.mkdir(parents=True, exist_ok=True)

    with open(models_dir / "vectorizer.pkl", 'wb') as f:
        pickle.dump(vectorizer, f)

    with open(models_dir / "model.pkl", 'wb') as f:
        pickle.dump(model, f)

    config = {
        'type': 'logistic_regression',
        'test_metrics': {
            'precision_no_escalation': float(precision[0]),
            'recall_no_escalation': float(recall[0]),
            'f1_no_escalation': float(f1[0]),
            'precision_escalation': float(precision[1]),
            'recall_escalation': float(recall[1]),
            'f1_escalation': float(f1[1])
        },
        'confusion_matrix': {
            'tn': int(tn),
            'fp': int(fp),
            'fn': int(fn),
            'tp': int(tp)
        }
    }

    with open(models_dir / "config.json", 'w') as f:
        json.dump(config, f, indent=2)

    print(f"  ✓ Saved to {models_dir}/")

    print("\n" + "=" * 70)
    print("✓ ESCALATION MODEL TRAINING COMPLETE")
    print("=" * 70)

    return model, vectorizer


if __name__ == "__main__":
    # Test rule-based detector
    print("=" * 70)
    print("ESCALATION DETECTION - RULE-BASED BASELINE")
    print("=" * 70)

    test_cases = [
        ("Where is my order?", False),
        ("I need to speak to a manager NOW", True),
        ("My account was hacked!", True),
        ("This is unacceptable. I'm canceling my membership.", True),
        ("Can I track my delivery?", False),
    ]

    print("\nRule-based detector tests:")
    for text, expected in test_cases:
        result = EscalationDetector.detect(text)
        status = "✓" if result['escalation_required'] == expected else "✗"
        print(f"  {status} '{text}'")
        print(f"     Escalation: {result['escalation_required']}, Signals: {result['signals']}")

    print("\n" + "=" * 70)
    print("To train ML model, run: python3 scripts/train_escalation_model.py")
    print("=" * 70)

#!/usr/bin/env python3
"""
Train intent classifier using labeled golden dataset.

Uses TF-IDF + Logistic Regression on conversation-level labels.
"""

import sys
from pathlib import Path
import json
import numpy as np
import pickle
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
except ImportError:
    print("Installing scikit-learn...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "scikit-learn"])
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix


def load_labeled_dataset(path):
    """Load labeled dataset."""
    records = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            records.append(json.loads(line))
    return records


def train_intent_classifier():
    """Train intent classifier."""

    print("=" * 70)
    print("TRAINING INTENT CLASSIFIER")
    print("=" * 70)

    # Check if labeled dataset exists
    labeled_path = "data/evaluation/golden_labeled.jsonl"
    if not Path(labeled_path).exists():
        print("\n✗ Labeled dataset not found.")
        print("  Run: python3 scripts/build_labeled_dataset.py")
        return None

    # Load dataset
    print("\n1. Loading labeled dataset...")
    records = load_labeled_dataset(labeled_path)
    print(f"  ✓ Loaded {len(records)} records")

    # Check minimum threshold
    if len(records) < 50:
        print(f"\n✗ Only {len(records)} labeled records available.")
        print("  Minimum for training: 50")
        print("  Waiting for more annotations.\n")
        return None

    # Prepare data
    print("\n2. Preparing data...")
    X = [r['text'] for r in records]
    y = [r['primary_intent'] for r in records]
    conv_ids = [r['conversation_id'] for r in records]

    # Get label mapping
    labels = sorted(set(y))
    label_to_id = {label: i for i, label in enumerate(labels)}
    id_to_label = {i: label for label, i in label_to_id.items()}
    y_ids = [label_to_id[label] for label in y]

    print(f"  ✓ {len(X)} examples, {len(labels)} classes")
    print(f"  Classes: {', '.join(labels)}")

    # Train/val/test split at conversation level
    print("\n3. Splitting data (conversation-level)...")
    # First split: 70% train, 30% temp
    X_train, X_temp, y_train, y_temp, ids_train, ids_temp = train_test_split(
        X, y_ids, conv_ids, test_size=0.30, random_state=42, stratify=y_ids
    )

    # Second split: split 30% into 50/50 (15% val, 15% test)
    X_val, X_test, y_val, y_test, ids_val, ids_test = train_test_split(
        X_temp, y_temp, ids_temp, test_size=0.50, random_state=42, stratify=y_temp
    )

    print(f"  Train: {len(X_train)} ({100*len(X_train)/len(X):.1f}%)")
    print(f"  Val:   {len(X_val)} ({100*len(X_val)/len(X):.1f}%)")
    print(f"  Test:  {len(X_test)} ({100*len(X_test)/len(X):.1f}%)")

    # Verify no leakage
    train_set = set(ids_train)
    val_set = set(ids_val)
    test_set = set(ids_test)

    assert len(train_set & val_set) == 0, "Train/Val leakage detected"
    assert len(train_set & test_set) == 0, "Train/Test leakage detected"
    assert len(val_set & test_set) == 0, "Val/Test leakage detected"
    print("  ✓ No conversation leakage between splits")

    # Vectorize text
    print("\n4. Vectorizing text...")
    vectorizer = TfidfVectorizer(
        max_features=2000,
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.9,
        stop_words='english'
    )

    X_train_vec = vectorizer.fit_transform(X_train)
    X_val_vec = vectorizer.transform(X_val)
    X_test_vec = vectorizer.transform(X_test)

    print(f"  ✓ Created {X_train_vec.shape[1]} features")
    print(f"  Train shape: {X_train_vec.shape}")
    print(f"  Val shape:   {X_val_vec.shape}")
    print(f"  Test shape:  {X_test_vec.shape}")

    # Train classifier
    print("\n5. Training Logistic Regression...")
    classifier = LogisticRegression(
        C=1.0,
        max_iter=1000,
        class_weight='balanced',
        random_state=42,
        n_jobs=-1
    )

    classifier.fit(X_train_vec, y_train)
    print("  ✓ Training complete")

    # Evaluate on validation set
    print("\n6. Validation performance...")
    y_val_pred = classifier.predict(X_val_vec)
    val_acc = accuracy_score(y_val, y_val_pred)
    print(f"  Accuracy: {val_acc:.4f}")

    # Evaluate on test set
    print("\n7. Test set evaluation...")
    y_test_pred = classifier.predict(X_test_vec)
    y_test_proba = classifier.predict_proba(X_test_vec)

    test_acc = accuracy_score(y_test, y_test_pred)
    precision, recall, f1, support = precision_recall_fscore_support(
        y_test, y_test_pred, average='weighted'
    )

    print(f"  Accuracy:     {test_acc:.4f}")
    print(f"  Weighted Prec: {precision:.4f}")
    print(f"  Weighted Rec:  {recall:.4f}")
    print(f"  Weighted F1:   {f1:.4f}")

    # Per-class metrics
    print("\n8. Per-class metrics:")
    print(f"  {'Intent':<30s} {'Prec':<8s} {'Rec':<8s} {'F1':<8s} {'Sup':<6s}")
    print("  " + "-" * 60)

    precision_per_class, recall_per_class, f1_per_class, support_per_class = \
        precision_recall_fscore_support(y_test, y_test_pred, average=None)

    for i, label in enumerate(labels):
        print(f"  {label:<30s} {precision_per_class[i]:>7.4f} {recall_per_class[i]:>7.4f} "
              f"{f1_per_class[i]:>7.4f} {support_per_class[i]:>5d}")

    # Confusion matrix
    print("\n9. Confusion matrix analysis...")
    cm = confusion_matrix(y_test, y_test_pred)

    # Find most confused pairs
    confused_pairs = []
    for i in range(len(labels)):
        for j in range(len(labels)):
            if i != j and cm[i, j] > 0:
                confused_pairs.append({
                    'true': labels[i],
                    'pred': labels[j],
                    'count': int(cm[i, j])
                })

    if confused_pairs:
        confused_pairs.sort(key=lambda x: x['count'], reverse=True)
        print("  Most confused pairs:")
        for pair in confused_pairs[:5]:
            print(f"    {pair['true']:20s} → {pair['pred']:20s}: {pair['count']} errors")
    else:
        print("  No confusion!")

    # Save model artifacts
    print("\n10. Saving model artifacts...")
    models_dir = Path("models/intent_classifier")
    models_dir.mkdir(parents=True, exist_ok=True)

    # Save vectorizer
    with open(models_dir / "vectorizer.pkl", 'wb') as f:
        pickle.dump(vectorizer, f)

    # Save classifier
    with open(models_dir / "classifier.pkl", 'wb') as f:
        pickle.dump(classifier, f)

    # Save label mapping
    with open(models_dir / "labels.json", 'w') as f:
        json.dump({
            'label_to_id': label_to_id,
            'id_to_label': {str(k): v for k, v in id_to_label.items()}
        }, f, indent=2)

    # Save configuration
    config = {
        'vectorizer_params': {
            'max_features': 2000,
            'ngram_range': [1, 2],
            'min_df': 2,
            'max_df': 0.9,
            'stop_words': 'english'
        },
        'classifier_params': {
            'C': 1.0,
            'max_iter': 1000,
            'class_weight': 'balanced'
        },
        'seed': 42,
        'training_metadata': {
            'total_records': len(records),
            'train_records': len(X_train),
            'val_records': len(X_val),
            'test_records': len(X_test),
            'num_classes': len(labels),
            'num_features': X_train_vec.shape[1],
            'timestamp': datetime.utcnow().isoformat()
        },
        'performance': {
            'test_accuracy': float(test_acc),
            'weighted_f1': float(f1),
            'weighted_precision': float(precision),
            'weighted_recall': float(recall)
        }
    }

    with open(models_dir / "config.json", 'w') as f:
        json.dump(config, f, indent=2)

    print(f"  ✓ Saved to {models_dir}/")
    print(f"    - vectorizer.pkl")
    print(f"    - classifier.pkl")
    print(f"    - labels.json")
    print(f"    - config.json")

    # Save evaluation report
    evaluation = {
        'timestamp': datetime.utcnow().isoformat(),
        'test_set': {
            'accuracy': float(test_acc),
            'weighted_precision': float(precision),
            'weighted_recall': float(recall),
            'weighted_f1': float(f1),
            'num_examples': len(y_test),
            'num_classes': len(labels)
        },
        'per_class': {
            label: {
                'precision': float(precision_per_class[i]),
                'recall': float(recall_per_class[i]),
                'f1': float(f1_per_class[i]),
                'support': int(support_per_class[i])
            }
            for i, label in enumerate(labels)
        },
        'confusion_pairs': confused_pairs[:10],
        'notes': f'Trained on {len(X_train)} conversations, evaluated on {len(X_test)}'
    }

    eval_path = "reports/intent_classifier_evaluation.md"
    with open(eval_path, 'w') as f:
        f.write("# Intent Classifier Evaluation\n\n")
        f.write(f"**Timestamp:** {evaluation['timestamp']}\n\n")
        f.write("## Overall Performance\n\n")
        f.write(f"- **Accuracy:** {test_acc:.4f}\n")
        f.write(f"- **Weighted Precision:** {precision:.4f}\n")
        f.write(f"- **Weighted Recall:** {recall:.4f}\n")
        f.write(f"- **Weighted F1:** {f1:.4f}\n\n")
        f.write(f"Test set: {len(y_test)} conversations across {len(labels)} intents\n\n")
        f.write("## Per-Class Performance\n\n")
        f.write("| Intent | Precision | Recall | F1 | Support |\n")
        f.write("|--------|-----------|--------|-----|----------|\n")
        for label in labels:
            metrics = evaluation['per_class'][label]
            f.write(f"| {label} | {metrics['precision']:.4f} | {metrics['recall']:.4f} | "
                   f"{metrics['f1']:.4f} | {metrics['support']} |\n")
        f.write("\n")

    print(f"  ✓ Evaluation report: {eval_path}")

    print("\n" + "=" * 70)
    print("✓ CLASSIFIER TRAINING COMPLETE")
    print("=" * 70)
    print(f"\nModel saved to: {models_dir}/")
    print(f"To use classifier: scripts/evaluate_intent_classifier.py\n")

    return classifier, vectorizer, labels


if __name__ == "__main__":
    train_intent_classifier()

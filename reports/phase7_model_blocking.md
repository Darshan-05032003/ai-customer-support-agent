# Model Training Blocked

**Status:** 🔴 BLOCKED
**Component:** Intent Classifier Training
**Date:** 2026-09-16

## Block Reason
`data/evaluation/golden_annotations.jsonl` does not exist.
There are **0/250** manual annotations completed.

## Impact
Without human annotations, we cannot:
* Train a supervised Machine Learning intent classifier.
* Establish a ground-truth measurement of accuracy, F1, precision, or recall.
* Run a reliable comparative evaluation against baselines or LLM-as-a-judge.

## Resolution Steps
1. An annotator must manually review the `data/evaluation/golden_candidates_reduced.jsonl` examples.
2. The UI (`archive_app_phase5_annotation_ui.py`) can be brought back up to assist in this task.
3. Once `golden_annotations.jsonl` reaches >= 250 labeled entries, this block can be resolved.
4. After resolution, we can run `scripts/build_labeled_dataset.py`, `scripts/create_model_splits.py`, and `scripts/train_intent_classifier.py`.

## Stopgap Measure
The web application uses the `HeuristicIntentClassifier` in `src/intent_service.py` as a fallback, which allows testing the overall pipeline without a supervised ML classifier. This fallback operates with zero fabricated confidence values.
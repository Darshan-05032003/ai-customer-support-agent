# Classifier Training and Evaluation Plan

**Date:** September 16, 2026  
**Phase:** Phase 5 - Supervised Learning Foundation

---

## Annotation Data Representation

### Granularity Level: CONVERSATION

All 250 golden candidates are annotated at the **conversation level**.

The `primary_intent` represents the main support issue described across the entire conversation, not just the first customer message.

**Example:**
```
Customer: "I ordered something last week."
Brand:    "Can you provide the order number?"
Customer: "Order 123 hasn't arrived."
```
→ Primary Intent: **DELIVERY_ISSUE** (late/missing package)

### Input Representation

For classifier training, we use:

**Option 1: Concatenated Customer Messages (PREFERRED)**
```
Input = All customer messages in the conversation, concatenated in chronological order
Target = human-annotated primary_intent
```

This preserves conversation context and prevents message-level leakage.

**Option 2: First Customer Message Only (EXPLORATORY)**
```
Input = First customer message in the conversation
Target = human-annotated primary_intent
```

This enables single-turn experiments but may lose important context.

### Training Data Structure

Each training example will have:

```json
{
  "conversation_id": "conv_12345",
  "text": "customer messages concatenated",
  "first_customer_message": "first message only",
  "all_customer_messages": ["msg1", "msg2", ...],
  "primary_intent": "ORDER_STATUS",
  "secondary_intent": null,
  "is_ambiguous": false,
  "escalation_required": "no",
  "annotator_notes": "..."
}
```

---

## Data Split Strategy

### Conversation-Level Stratification

Because we have **250 total golden conversations**, we allocate:

- **Train:** 175 conversations (70%)
- **Validation:** 37 conversations (15%)
- **Test:** 38 conversations (15%)

### Stratification by Intent

Where possible, stratify by `primary_intent` to ensure each split has representative samples from all 12 categories.

If a category has fewer than 3 samples, do NOT exclude it from training; instead document the limitation.

### Prevention of Leakage

**CRITICAL:** Do NOT split individual messages from the same conversation across train/val/test.

Split is performed at conversation ID level:
- All messages from a conversation stay in the same split
- Use deterministic seed (42) for reproducibility
- Document final split composition

---

## Classifier Architecture

### Model Type: TF-IDF + Logistic Regression

**Rationale:**
- Simple, explainable baseline
- Fast training on 175 examples
- Provides confidence scores
- Interpretable feature weights

### Alternative (Optional): LinearSVC
- May provide better margins for imbalanced classes
- Compare performance; report both if implemented

### Hyperparameters

```python
TfidfVectorizer:
  - max_features: 2000
  - ngram_range: (1, 2)  # unigrams and bigrams
  - min_df: 2             # appears in at least 2 documents
  - max_df: 0.9           # not in >90% of documents
  - stop_words: 'english'

LogisticRegression:
  - C: 1.0
  - max_iter: 1000
  - class_weight: 'balanced'  # for imbalanced classes
  - random_state: 42
```

---

## Evaluation Metrics

### Overall Performance

- **Accuracy:** Overall correct predictions
- **Macro F1:** Unweighted average across all classes
- **Weighted F1:** Weighted by support in test set

### Per-Class Metrics

For each of 12 intents, report:
- Precision: TP / (TP + FP)
- Recall: TP / (TP + FN)
- F1: Harmonic mean of precision and recall
- Support: Number of test examples

### Error Analysis

- Confusion matrix
- Most confused intent pairs
- Representative false predictions
- Classes with low support

---

## Escalation Detection

### Approach: Rule-Based Baseline + ML Comparison

**Rule-based features:**
1. Explicit escalation request: "speak to", "manager", "escalate"
2. Account security: "hacked", "fraud", "unauthorized"
3. Repeated failures: Conversation length > 10 messages + multiple customer turns
4. Frustration signals: "unacceptable", "terrible", "angry"
5. Policy exception: "exception", "make exception", "special case"

**ML baseline (if sufficient data):**
- TF-IDF + Logistic Regression on `escalation_required` labels
- Compare rule-based vs. learned approach

---

## Response Retrieval

### Approach: TF-IDF Cosine Similarity

1. Build index of 126,963 brand responses with context
2. For a new customer query, retrieve top-5 most similar historical responses
3. Use TF-IDF vectorization with same parameters as classifier
4. Return: similarity score, source conversation, historical response

### Evaluation

Do NOT claim response quality until humans evaluate.

Prepare framework:
- Customer query
- Retrieved response
- Source conversation
- Evaluation schema (see response_evaluation_rubric.md)

---

## Quality Gates

### Minimum Annotation Threshold

- If < 100 labeled conversations: Exploratory classifier only, no production claims
- If 100-200 labeled: Preliminary classifier, clearly marked as limited
- If 200+ labeled: Full evaluation with confidence intervals

### Class Imbalance

If any intent has < 5 examples in test set, report it explicitly.

Do NOT collapse classes or fabricate samples.

---

## Documentation Requirements

Every claim must have measured evidence:

- "Classifier achieves 78% F1" → exact F1 number from test set
- "Intent XYZ is hard to classify" → show confusion matrix entry
- "Escalation detected correctly 92% of the time" → show precision/recall
- "Response retrieval works" → show example retrievals with scores

---

## Success Criteria

Phase 5 is complete when:

- [ ] Human annotations processed (0 or 250)
- [ ] No fabricated labels
- [ ] Intent classifier trained (if ≥100 labels)
- [ ] Classifier evaluated on held-out test set
- [ ] Escalation baseline implemented
- [ ] Response retrieval working
- [ ] Offline pipeline implemented
- [ ] All metrics measured, not claimed
- [ ] Limitations clearly documented
- [ ] No automatic commit

---

**Ready for Phase 5 implementation.**

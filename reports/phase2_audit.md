# Phase 2 Audit Report

**Date:** September 16, 2026  
**Audit Status:** CRITICAL ISSUES FOUND

---

## Executive Summary

Phase 2 reports claim completion but the implementation contains **fundamental architectural flaws** that make the data unsuitable for building a classifier or evaluation system.

**Critical Issues:**
1. ❌ Full conversation reconstruction artifact missing (`amazonhelp_conversations.jsonl` does not exist)
2. ❌ "Conversation ID" is incorrectly implemented as direct parent tweet ID, not reconstructed thread root
3. ❌ Statistics (85,270 conversations, 1.18 avg length, 88% multi-turn) are unverified and likely incorrect
4. ❌ Split is NOT conversation-level; messages from same thread can be in different splits
5. ❌ Intent taxonomy was hardcoded (not discovered), then used to classify examples
6. ❌ Taxonomy lacks proper definitions, criteria, and overlap documentation

---

## Part A: What Phase 2 Got Right

✅ **Brand selection:** AmazonHelp is appropriate  
✅ **Phase 1 audit:** Completed and verified  
✅ **Data extraction framework:** Basic loaders and preprocessing modules created  
✅ **Test infrastructure:** Phase 2 tests created (though testing incomplete claims)  
✅ **Data safety:** Raw data checksum verified unchanged  
✅ **Split proportions:** 80/10/10 achieved (though not at conversation level)  
✅ **File organization:** data/processed/, reports/ structure in place  

---

## Part B: What Is Incomplete/Incorrect

### 1. Missing Full Conversation Reconstruction Artifact

**Claim:** "85,270 reconstructed conversations"  
**Reality:** No `amazonhelp_conversations.jsonl` file exists  

The full reconstruction pipeline timed out and was stopped. Only customer message extraction was completed.

**Impact:** Cannot build conversation-level evaluation or verify split integrity.

### 2. Conversation ID Is NOT Conversation Root

**Current implementation (extract_and_split.py):**
```python
msg = {
    'conversation_id': parent_id  # ← WRONG: This is direct parent, not thread root
    ...
}
```

**Problem:** 
- For a customer message replying to AmazonHelp, the "conversation_id" is just that specific AmazonHelp tweet
- Multiple independent customer→brand pairs have the same AmazonHelp tweet as parent
- Threads are collapsed into pairwise interactions
- Cannot reconstruct full multi-turn conversations

**Example:** Customer A replies to AmazonHelp tweet X. Later, Customer B also replies to X. Both have conversation_id=X, but they're unrelated conversations.

### 3. Split Is NOT Conversation-Level

**Claim:** "Conversation-level splits (no message leakage)"  
**Reality:** Split is at parent_id level, not at reconstructed thread root level

**Problem:** Messages from the same logical conversation thread (chain of replies) can be in different splits if they respond to different AmazonHelp tweets.

**Impact:** Test/train/val leakage is possible.

### 4. Conversation Statistics Are Unverified

| Claim | Status |
|-------|--------|
| 85,270 reconstructed conversations | ❌ Estimate only (from analytical script) |
| 100,503 customer messages | ✅ Correct (verified by file) |
| Avg 1.18 messages per conversation | ❌ Incorrect (calculated as msgs/parent_ids) |
| 88% multi-turn | ❌ Incorrect estimate |

**Reality:** With current broken conversation_id implementation:
- 100,503 unique parent tweet IDs (not conversations)
- Average 1.0 messages per parent (nearly all pairwise)

### 5. Intent Taxonomy Was Hardcoded, Not Discovered

**In scripts/discover_intents.py:**
```python
intent_patterns = {
    'order_status': {...},
    'late_delivery': {...},
    'refund_return': {...},
    'payment_billing': {...},
    'account_login': {...},
    'shipping_address': {...},
    'subscription_service': {...},
    'technical_issue': {...},
    'product_information': {...},
    'missing_damaged_item': {...},
}
```

**Problem:** These 10 category names and their keywords were hardcoded, then used to classify a sample of 500 messages. This is NOT data-driven discovery.

**Evidence of over-fitting:** 57% of sample messages unclassified (should indicate poor category fit, but is reported as "realistic ambiguity").

### 6. Taxonomy Lacks Required Structure

**Current taxonomy (intent_taxonomy.json):**
```json
{
  "id": "order_status",
  "name": "Order Status",
  "keywords": [...],
  "example_count": 67,
  "sample_messages": [...]
}
```

**Missing:**
- ❌ Formal definition (not just keywords)
- ❌ Inclusion criteria (what MUST be true)
- ❌ Exclusion criteria (what must NOT be true)
- ❌ Boundary documentation (what distinguishes from overlapping intents)
- ❌ Confusion notes (common misclassifications)

**Impact:** Later annotators cannot reliably apply these labels.

### 7. Tests Don't Verify Core Claims

**Test `test_splits_non_overlapping`:**
```python
for line in f:
    record = json.loads(line)
    convs.add(record["conversation_id"])  # ← Tests parent_id uniqueness, not thread uniqueness
```

This test verifies that parent IDs don't overlap. It does NOT verify conversation-level non-overlap.

---

## Part C: Trustworthy Artifacts

✅ **amazonhelp_customer_messages_train.jsonl** — 80,475 message records exist  
✅ **amazonhelp_customer_messages_val.jsonl** — 10,009 message records exist  
✅ **amazonhelp_customer_messages_test.jsonl** — 10,019 message records exist  
✅ **intent_taxonomy.json** — File exists with structure (content quality poor)  
✅ **Raw data** — Checksum verified unchanged  

**Caveat:** The customer message records have broken conversation_id values.

---

## Part D: What Must Be Regenerated

❌ **Full conversation reconstruction** — Create `amazonhelp_conversations.jsonl`  
❌ **Conversation statistics** — Recalculate from real reconstructed data  
❌ **Conversation IDs** — Regenerate customer messages with correct thread roots  
❌ **Data splits** — Regenerate at proper conversation level  
❌ **Intent taxonomy** — Rebuild with proper structure and definitions  
❌ **Tests** — Expand to verify new architecture  

---

## Part E: Repair Action Plan

### Step 1: Full Conversation Reconstruction
- Implement efficient pipeline to reconstruct true conversation threads
- Use in_response_to_tweet_id as primary relationship
- Build parent→children index
- Trace backward to find thread roots
- Collect all messages in each thread
- Create `amazonhelp_conversations.jsonl`

### Step 2: Recalculate Statistics
- Parse reconstructed conversations
- Calculate true conversation metrics
- Document in `phase3_conversation_quality.md`

### Step 3: Extract Customer Messages from Real Conversations
- Read `amazonhelp_conversations.jsonl`
- Extract customer messages with correct conversation_id
- Create `amazonhelp_customer_messages.jsonl`

### Step 4: Regenerate Splits
- Use true conversation IDs
- Split at conversation level
- Create new train/val/test splits

### Step 5: Rebuild Intent Taxonomy
- Analyze real customer messages
- Use TF-IDF, frequency analysis, clustering
- Identify natural intent boundaries
- Create proper taxonomy with definitions, criteria, examples

### Step 6: Expand Tests
- Test conversation reconstruction
- Test split non-overlap at conversation level
- Test taxonomy schema
- Test golden candidate selection

---

## Summary

| Component | Status | Action |
|-----------|--------|--------|
| Brand selection | ✅ OK | Keep |
| Data extraction framework | ⚠️ Partial | Improve |
| Conversation reconstruction | ❌ Missing | BUILD |
| Conversation statistics | ❌ Unverified | RECALCULATE |
| Conversation IDs | ❌ Wrong | FIX |
| Data splits | ⚠️ Broken | REGENERATE |
| Intent taxonomy | ⚠️ Hardcoded | REBUILD |
| Tests | ⚠️ Insufficient | EXPAND |
| Raw data | ✅ Safe | Keep |

---

## Conclusion

Phase 2 provides a starting framework but is architecturally unsound for the core requirements. The conversation reconstruction and data splitting must be completely rebuilt before Phase 3 can proceed.

**Recommendation:** Implement the repair plan in Part E before building any classifiers or evaluation systems.

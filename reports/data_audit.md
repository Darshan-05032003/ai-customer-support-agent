# Data Audit Report: Customer Support on Twitter Dataset

**Date:** September 15, 2026  
**Status:** Phase 1 Complete  
**Dataset:** Twitter Customer Support (TWCS) from Kaggle

---

## Executive Summary

The Customer Support on Twitter dataset has been successfully audited. It contains **2.8M tweets** across **108 distinct brands**, with rich conversation structure enabling reconstruction of multi-turn customer support interactions. The dataset is high-quality, with no duplicates and 99.8% conversation linkage integrity.

**Key Finding:** This dataset is sufficient to build a high-quality AI customer support agent without Banking77. Conversations can be reliably reconstructed, and multiple brands provide ample training data.

---

## 1. Dataset Files Found

| File | Size | Rows | Purpose |
|------|------|------|---------|
| `archive/twcs/twcs.csv` | 492.6 MB | 2,811,774 | Main dataset (all tweets) |
| `archive/sample.csv` | 17 KB | 93 | Sample for quick testing |

---

## 2. Dataset Structure

### Schema

All files share the same schema with 7 columns:

| Column | Type | Description | Missing |
|--------|------|-------------|---------|
| `tweet_id` | int64 | Unique tweet identifier | 0 (0%) |
| `author_id` | str | Author handle/username | 0 (0%) |
| `inbound` | bool | Direction: True=customer, False=brand | 0 (0%) |
| `created_at` | str | Timestamp in Twitter format | 0 (0%) |
| `text` | str | Tweet content (up to 513 chars) | 0 (0%) |
| `response_tweet_id` | str | IDs of tweets responding to this one | 1,040,629 (37.01%) |
| `in_response_to_tweet_id` | float64 | ID of tweet this responds to | 794,335 (28.25%) |

### Data Quality

| Metric | Value |
|--------|-------|
| Full row duplicates | 0 |
| Duplicate tweet_ids | 0 |
| Data integrity | Excellent |

**Interpretation:** No quality issues detected. Every tweet_id is unique. Missing values in response fields are expected (not all tweets are part of a conversation chain).

---

## 3. Conversation Structure

### Linkage Analysis

The dataset enables multi-turn conversation reconstruction:

| Metric | Count | % of Dataset |
|--------|-------|-------------|
| Tweets with `in_response_to_tweet_id` | 2,017,439 | 71.7% |
| Tweets with `response_tweet_id` | 1,771,145 | 63.0% |
| Tweets with multiple responses | 222,426 | 7.9% |

### Conversation Reconstruction Capability

| Aspect | Finding |
|--------|---------|
| Backward links found in dataset | 2,013,577 / 2,017,439 (99.8%) |
| Backward links missing | 3,862 (0.2%) |
| **Reliability** | **EXCELLENT** |

**Interpretation:** When a tweet says it responds to another tweet (via `in_response_to_tweet_id`), that referenced tweet exists in the dataset 99.8% of the time. This means conversations can be reliably reconstructed by following the reference chain.

### Customer-Brand Interactions

| Metric | Count | % |
|--------|-------|-----|
| Inbound (customer) tweets with ≥1 response | 1,303,829 | 84.8% of inbound |
| Outbound (brand) tweets that are replies | 1,266,942 | 99.5% of outbound |

**Interpretation:** The vast majority of brand tweets are replies to customers (not standalone posts). This is ideal for learning response patterns.

---

## 4. Brands Analysis

### Brand Count

- **Total unique brands:** 108
- **Brands with 1000+ tweets:** 86
- **Brands with 500+ tweets:** 101
- **Brands with 100+ tweets:** 108 (100%)

### Top 30 Brands by Outbound Tweet Count

| Rank | Brand | Outbound Tweets |
|------|-------|-----------------|
| 1 | AmazonHelp | 169,840 |
| 2 | AppleSupport | 106,860 |
| 3 | Uber_Support | 56,270 |
| 4 | SpotifyCares | 43,265 |
| 5 | Delta | 42,253 |
| 6 | Tesco | 38,573 |
| 7 | AmericanAir | 36,764 |
| 8 | TMobileHelp | 34,317 |
| 9 | comcastcares | 33,031 |
| 10 | British_Airways | 29,361 |
| 11 | SouthwestAir | 28,977 |
| 12 | VirginTrains | 27,817 |
| 13 | Ask_Spectrum | 25,860 |
| 14 | XboxSupport | 24,557 |
| 15 | sprintcare | 22,381 |
| 16 | hulu_support | 21,872 |
| 17 | sainsburys | 19,466 |
| 18 | GWRHelp | 19,364 |
| 19 | AskPlayStation | 19,098 |
| 20 | ChipotleTweets | 18,749 |
| 21 | VerizonSupport | 17,966 |
| 22 | UPSHelp | 17,817 |
| 23 | ATVIAssist | 17,650 |
| 24 | O2 | 16,212 |
| 25 | Safaricom_Care | 16,077 |
| 26 | idea_cares | 15,724 |
| 27 | AskTarget | 13,218 |
| 28 | AirAsiaSupport | 12,829 |
| 29 | BofA_Help | 12,683 |
| 30 | SW_Help | 12,231 |

**Interpretation:** Multiple brands have substantial data volume. Top 3 brands alone have 333k tweets. Even brand #30 has 12k tweets, sufficient for fine-tuning.

### Author Separation

| Metric | Count |
|--------|-------|
| Total unique authors | 702,777 |
| Unique inbound authors (customers) | 702,669 |
| Unique outbound authors (brands) | 108 |
| Authors appearing as BOTH inbound & outbound | 0 |

**Interpretation:** Perfect separation. No author IDs appear both as customers and brands. Brand identity can be reliably determined by the `inbound` flag.

---

## 5. Message Volume Distribution

| Category | Count | % |
|----------|-------|-----|
| Inbound (customer) tweets | 1,537,843 | 54.6% |
| Outbound (brand) tweets | 1,273,931 | 45.4% |
| **Total** | **2,811,774** | **100%** |

**Interpretation:** Balanced conversation flow. Brands respond to most customer messages, creating rich training data for response generation.

---

## 6. Text Field Analysis

| Metric | Value |
|--------|-------|
| Min length | 1 character |
| Max length | 513 characters |
| Mean length | 113.9 characters |
| Median length | 115 characters |
| Tweets ≤10 chars | 1,838 (0.07%) |

**Interpretation:** Text field is clean. Very few extremely short tweets (mostly edge cases). Tweet lengths are typical for Twitter support interactions.

---

## 7. Timestamp Range

| Metric | Value |
|--------|-------|
| Earliest tweet in main dataset | Tue Oct 31 22:10:47 +0000 2017 |
| Latest tweet in main dataset | Tue Nov 21 22:01:04 +0000 2017 |
| Time span (main dataset) | ~3 weeks (October-November 2017) |

**Interpretation:** Data is from a specific time window. This is sufficient for training a static classifier/generator, but temporal trends cannot be analyzed beyond this period.

---

## 8. Banking77 Dataset Status

| Status | Finding |
|--------|---------|
| **Present in project?** | **NO** |
| Location searched | Entire project directory |
| Required for Phase 1? | NO (optional per assignment) |
| Impact | NONE - Twitter dataset is sufficient |

**Interpretation:** Banking77 is not present and not needed. The assignment explicitly lists it as optional for intent classification experiments only. The Twitter dataset alone provides ample data to build a full system.

---

## 9. Data Quality Assessment

| Dimension | Status | Evidence |
|-----------|--------|----------|
| **Completeness** | ✅ Excellent | 0 full-row duplicates, all pk unique |
| **Consistency** | ✅ Excellent | No author_id overlap; inbound/outbound separation clean |
| **Linkage** | ✅ Excellent | 99.8% of references valid within dataset |
| **Text Quality** | ✅ Good | No suspicious patterns; median length ~115 chars |
| **Temporal Coverage** | ⚠️ Limited | Only 3 weeks of data, single time window |

**Overall:** High-quality dataset suitable for production use.

---

## 10. Conversation Reconstruction Example

From the audit data, here's a sample conversation flow (simplified):

```
Customer (inbound=True, tweet_id=3):
  "@sprintcare I have sent several private messages and no one is responding as usual"
  └─ in_response_to_tweet_id: 4 (another tweet)

Brand (inbound=False, tweet_id=1):
  "@115712 I understand. I would like to assist you. We would need to get 
   you into a private secured link to further assist."
  └─ in_response_to_tweet_id: 3.0
  └─ response_tweet_id: 2 (customer's reply)

Customer (inbound=True, tweet_id=2):
  "@sprintcare and how do you propose we do that"
  └─ in_response_to_tweet_id: 1.0
```

**Capability:** Multi-turn conversations can be reconstructed by following the `in_response_to_tweet_id` chain.

---

## 11. Risks and Limitations

| Risk | Severity | Mitigation |
|------|----------|-----------|
| Single 3-week time window | Medium | Use entire dataset; temporal trends not available |
| 0.2% missing references | Low | 99.8% is highly acceptable |
| Response field missingness (37%) | Low | Expected; indicates many tweets are conversation starters |
| Author IDs are anonymized | Low | Protects privacy; brand intent still learnable |

---

## 12. Recommendations for Next Phase

### Brand Selection
- **Recommended:** Choose from top 10 brands (each has 15k+ tweets)
- **Rationale:** Sufficient data for strong baselines and Golden Set
- **Candidates:** AmazonHelp, AppleSupport, Uber_Support, SpotifyCares, Delta (all have 40k+ tweets)

### Intent Discovery
- **Approach:** Analyze customer message categories from chosen brand's inbound tweets
- **Method:** Use LLM or rule-based clustering on top 500-1000 customer messages per brand
- **Output:** 8-15 intent categories (typical for support domains)

### Data Preprocessing
- **Conversation extraction:** Implement conversation reconstruction using `in_response_to_tweet_id` chains
- **Filters:** Keep only conversations with at least 1 customer + 1 brand message
- **Splits:** Recommend 80/10/10 for train/val/test with conversation-level stratification

### Evaluation Set
- **Size:** 150-250 hand-labeled examples (as per assignment)
- **Source:** Randomly sample conversations from chosen brand
- **Annotation:** Label each customer message with intent and escalation decision
- **Time:** ~2-4 hours for manual labeling

---

## 13. Important Observations

1. **Conversation linkage is excellent:** 99.8% of backward references are valid. This enables reliable multi-turn conversation reconstruction.

2. **Brand-customer distinction is clean:** No author appears as both brand and customer. Classification is straightforward.

3. **Multiple suitable brands available:** 86 brands have 1000+ tweets. No single-brand bottleneck.

4. **Data is representative:** Mix of industries (e-commerce, telecom, airlines, gaming, food, finance).

5. **Response patterns are learnable:** 99.5% of brand tweets are direct replies. Strong signal for response generation.

---

## 14. Conclusion

The Customer Support on Twitter dataset is well-structured, high-quality, and sufficient for building a complete AI customer support agent. No additional datasets are required for Phase 1.

**Ready to proceed:** ✅ YES

**Next steps:**
1. Select target brand (recommend: AmazonHelp, AppleSupport, or Uber_Support)
2. Extract conversations by following reference chains
3. Implement intent classifier and escalation detector
4. Create Golden Evaluation Set
5. Build LLM-as-a-judge rubric
6. Implement and evaluate agent

---

## Appendix: Raw Audit Output

See `reports/data_audit.txt` for complete unformatted audit log.

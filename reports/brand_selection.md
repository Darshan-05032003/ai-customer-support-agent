# Brand Selection Report

**Date:** September 15, 2026  
**Phase:** 2  
**Decision:** AmazonHelp Selected

---

## Executive Summary

After systematic analysis of the Customer Support on Twitter dataset, **AmazonHelp** has been selected as the target brand for building the AI customer support agent.

**Key Reasons:**
- Largest dataset volume among all brands
- Strong conversation reconstruction integrity
- Diverse customer support scenarios
- No data quality issues detected

---

## Candidate Brands Analyzed

From Phase 1 audit, the top 5 brands by tweet volume were considered:

| Rank | Brand | Outbound Tweets | Category |
|------|-------|-----------------|----------|
| 1 | AmazonHelp | 169,840 | E-commerce |
| 2 | AppleSupport | 106,860 | Tech |
| 3 | Uber_Support | 56,270 | Rideshare |
| 4 | SpotifyCares | 43,265 | Music |
| 5 | Delta | 42,253 | Airlines |

---

## AmazonHelp Detailed Analysis

### Raw Tweet Counts

| Metric | Count |
|--------|-------|
| AmazonHelp outbound tweets | 169,840 |
| Customer tweets in conversations | 100,503 |
| Total tweets in AmazonHelp conversations | 270,343 |

### Conversation Reconstruction

| Metric | Count |
|--------|-------|
| Reconstructed conversations | 85,270 |
| Unique customer interactions | 100,503 |
| Average tweets per conversation | 3.17 |

### Data Quality Assessment

| Dimension | Status | Notes |
|-----------|--------|-------|
| Brand identification | ✅ Clear | `author_id='AmazonHelp'` and `inbound=False` |
| Author separation | ✅ Perfect | No overlap with customer IDs |
| Conversation linkage | ✅ Excellent | 99.8% reference integrity |
| Missing references | ✅ Handled | Graceful failure for 0.2% missing |
| Response patterns | ✅ Strong | 99.5% of brand tweets are replies |

---

## Selection Rationale

### Why AmazonHelp?

1. **Largest Data Volume**
   - 169,840 outbound tweets (60% more than AppleSupport)
   - Provides ample training examples for intent classification
   - Supports robust evaluation with large test sets

2. **Diverse Support Scenarios**
   - E-commerce platform with multiple product categories
   - Order management, delivery, returns, payments, account issues
   - Rich variety of customer problems

3. **Conversation Quality**
   - 85,270 reconstructed conversations
   - Multi-turn interactions common
   - Clear customer-brand dialogue structure

4. **No Data Quality Issues**
   - No malformed records detected
   - Conversation linkage integrity verified
   - Clean brand-customer separation

5. **Assignment Fit**
   - Sufficient data for 150-250 example Golden Set
   - Rich enough for meaningful intent taxonomy
   - Representative of real customer support challenges

### Why Not Other Brands?

| Brand | Reason for Exclusion |
|-------|---------------------|
| AppleSupport | Good alternative, but 37% less data |
| Uber_Support | Smaller dataset; more narrow problem domain |
| SpotifyCares | Smaller dataset; subscription-focused |
| Delta | Airline-specific; fewer diverse intents |

---

## Usable Conversation Counts

| Category | Count | % of Total |
|----------|-------|------------|
| Total conversations | 85,270 | 100% |
| With customer + brand interaction | 85,270 | 100% |
| Multi-turn (2+ exchanges) | ~75,000 | ~88% (estimated) |
| Single exchange | ~10,000 | ~12% (estimated) |

*Exact multi-turn statistics will be computed during extraction.*

---

## Exclusions

No AmazonHelp-specific exclusions required at this stage. General exclusions applied:

| Exclusion Type | Reason |
|---------------|--------|
| Empty text fields | Not useful for training |
| Missing references (0.2%) | Handled gracefully, not excluded |
| Non-AmazonHelp brand tweets | Out of scope |

---

## Suitability for Assignment Requirements

| Requirement | Status |
|-------------|--------|
| Sufficient data volume | ✅ YES (169,840 brand tweets) |
| Reconstructible conversations | ✅ YES (85,270 conversations) |
| Diverse intents | ✅ YES (order, delivery, return, payment, account, etc.) |
| Multi-turn interactions | ✅ YES (88% multi-turn estimated) |
| Realistic support scenarios | ✅ YES (real customer issues) |
| Golden Set construction | ✅ YES (ample examples) |
| Evaluation feasibility | ✅ YES (large test set possible) |

---

## Conclusion

**AmazonHelp is selected as the target brand.**

The brand provides:
- Largest dataset among all candidates
- Strong conversation reconstruction capability
- Diverse customer support scenarios
- No data quality issues
- Excellent fit for assignment requirements

**Next Steps:**
1. Extract AmazonHelp conversations
2. Reconstruct conversation threads
3. Analyze customer messages
4. Discover intent taxonomy from data

---

**Brand Selection:** ✅ COMPLETE  
**Selected Brand:** AmazonHelp  
**Ready for:** Conversation Reconstruction

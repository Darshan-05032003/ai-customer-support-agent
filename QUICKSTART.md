# Quick Start Guide

## First Time Setup (2 minutes)

```bash
# Clone/enter the project
cd /home/darshan/Company_Assignments/Hiver_Assignment

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Verify Everything Works (7 minutes)

```bash
# Run the data audit
python3 scripts/audit_data.py

# Run all tests
python3 -m pytest tests/ -v
```

Expected output:
- Audit completes in ~5 minutes
- All 24 tests pass in ~90 seconds
- No errors

## Key Files to Review

| File | Purpose | Read Time |
|------|---------|-----------|
| `README.md` | Overview & architecture | 5 min |
| `PHASE_1_STATUS_REPORT.md` | Complete audit findings | 10 min |
| `reports/data_audit.md` | Detailed data analysis | 15 min |
| `scripts/audit_data.py` | Audit implementation | 10 min |

## Dataset Location

**Main:** `archive/twcs/twcs.csv` (492.6 MB)
- 2.8M tweets
- 108 brands
- Ready to use

**Sample:** `archive/sample.csv` (for testing)
- 93 tweets
- Same schema

## What's Ready for Phase 2

✅ Dataset fully audited
✅ Conversation structure verified (99.8% linkage)
✅ 108 brands identified
✅ Testing framework in place
✅ Project foundation solid

## Next Steps

When ready for Phase 2:
1. Select target brand (recommend: AmazonHelp, AppleSupport, or Uber_Support)
2. Extract conversations using `in_response_to_tweet_id` chains
3. Analyze customer patterns to derive intents
4. Create Golden Evaluation Set (150-250 examples)

---

See `PHASE_1_STATUS_REPORT.md` for complete findings.

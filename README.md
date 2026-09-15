# Hiver SDE Intern Take-Home Assignment

AI Customer Support Agent for Twitter Customer Support Dataset

## Overview

This project builds an AI-powered customer support agent for Twitter using the Customer Support on Twitter (TWCS) dataset from Kaggle. The agent:

1. **Classifies** customer messages into intents
2. **Drafts replies** grounded in brand historical patterns
3. **Escalates** complex issues to humans
4. **Explains** each decision with reasoning

The project prioritizes **evaluation and reproducibility** over pure system complexity.

## Current Status

**Phase 1: Complete** ✅
- Data audit finished
- Dataset structure understood
- Conversation linkage verified (99.8% integrity)
- 108 brands identified (86 with 1000+ support tweets)
- Project foundation established

**Next phases:** Brand selection → Intent discovery → Golden Set → LLM Agent → Evaluation

## Quick Start

### 1. Set Up Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Run Data Audit

```bash
python3 scripts/audit_data.py
```

Output: `reports/data_audit.md` (comprehensive dataset analysis)

### 3. Verify Setup

```bash
python3 -m pytest tests/ -v
```

## Repository Structure

```
archive/                          # Raw data (IMMUTABLE)
├── twcs/
│   └── twcs.csv                  # 2.8M tweets, all brands
└── sample.csv                    # 93 tweets for quick testing

data/
├── processed/                    # Will contain extracted conversations
└── evaluation/                   # Will contain Golden Set

src/
├── data/                         # Data loading & preprocessing
├── preprocessing/                # Conversation extraction
├── intents/                      # Intent classification
├── retrieval/                    # Historical pattern lookup
├── agent/                        # Main agent orchestration
└── evaluation/                   # Evaluation harness

scripts/
├── audit_data.py                 # Data discovery & analysis
└── [more scripts in later phases]

reports/
├── data_audit.md                 # Dataset analysis (Phase 1)
├── data_audit.txt                # Raw audit log
└── [more reports in later phases]

tests/
├── test_data_loading.py
└── [more tests in later phases]

requirements.txt                  # Python dependencies
.env.example                      # Environment variables template
.gitignore                        # Git exclusions
```

## Dataset

**Name:** Customer Support on Twitter (TWCS)  
**Source:** Kaggle  
**Size:** 492.6 MB (2.8M tweets)  
**Brands:** 108 (ranging from 100 to 170k support tweets each)  
**Time Period:** October–November 2017

### Key Facts

- **71.7%** of tweets are part of a conversation chain
- **99.8%** of backward references are valid (can reconstruct conversations)
- **84.8%** of customer messages receive at least one response
- **99.5%** of brand tweets are direct replies
- **108** unique brands (0 author overlap)

For detailed analysis, see `reports/data_audit.md`.

## Next Steps

1. **Select Brand** — Choose from top brands (e.g., AmazonHelp, AppleSupport, Uber_Support)
2. **Extract Conversations** — Reconstruct multi-turn interactions
3. **Discover Intents** — Analyze customer message categories
4. **Build Golden Set** — Hand-label 150–250 examples
5. **Implement Agent** — Intent classifier + response generator + escalation detector
6. **Create Evaluation Harness** — LLM-as-judge + human agreement metrics
7. **Run Baselines** — Compare against trivial and simple models
8. **Failure Analysis** — Document top 5 failure modes

## Assignment Requirements

This project addresses all required components:

- [x] Phase 1: Dataset audit and foundation
- [ ] Intent classification (small set derived from data)
- [ ] Reply generation grounded in historical patterns
- [ ] Escalation decisions with reasoning
- [ ] 150–250 hand-labelled Golden Evaluation Set
- [ ] Automated evaluation harness
- [ ] LLM-as-judge rubric for reply quality
- [ ] Evidence of LLM judge ↔ human agreement
- [ ] Comparison vs. 2 baselines (trivial + simple)
- [ ] Failure analysis (top 5 modes with examples)
- [ ] "What is misleading about my headline number?" section
- [ ] "One more week" roadmap
- [ ] Decision log (10–15 non-obvious decisions)
- [ ] Reproducible in <15 minutes

See `Hiver SDE Intern Assignment - Google Docs.pdf` for full requirements.

## Running the System (Future)

Once all phases complete, the headline result will be reproducible with:

```bash
make all          # Run full pipeline in <15 minutes
make agent        # Build the support agent
make evaluate     # Run evaluation harness
make report       # Generate results report
```

Or via Python:

```bash
python3 -m src.agent.main --brand AppleSupport --mode demo
```

## Development

### Adding Dependencies

```bash
pip install <package>
pip freeze > requirements.txt
```

### Running Tests

```bash
python3 -m pytest tests/ -v --tb=short
```

### Code Style

- Python 3.12+
- Clear variable names and docstrings
- Type hints where practical
- No external ML frameworks for Phase 1 (keep it simple)

## Reproducibility

**Goal:** Anyone can reproduce the final agent and evaluation in <15 minutes.

**Strategy:**
- All data sourced from Kaggle dataset (public, versioned)
- All seeds fixed for deterministic results
- All intermediate files versioned or generated from scratch
- README contains exact commands

**Current Status:** Phase 1 fully reproducible. Run `python3 scripts/audit_data.py` to verify.

## Important Notes

### On Raw Data

The `archive/` folder contains immutable raw data. Scripts **never modify** these files.
Processed data goes to `data/processed/`.

### On Reproducibility

The assignment emphasizes evaluation more than raw code quantity. Quality evaluation, honest metrics, and clear failure analysis are prioritized over feature completeness.

### On Complexity

Each phase builds incrementally. No unnecessary frameworks or abstractions until proven necessary.

## Contact & Questions

This is an assignment submission. Questions about the project structure or data can be addressed by reviewing:
- `reports/data_audit.md` — comprehensive dataset analysis
- `scripts/audit_data.py` — data discovery logic
- Comments in source code

## License

Kaggle dataset used under CC0 license (public domain).
Project code is original work for evaluation purposes.

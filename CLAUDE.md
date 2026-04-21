# CLAUDE.md — A/B Testing Framework

Developer guide for working on this codebase. Covers architecture, design decisions, and local setup.

---

## What this is

A Streamlit app that guides users through the full A/B experiment lifecycle: idea validation → sample size calculation → results interpretation. The LLM layer (Ollama) handles routing decisions and plain-English result summaries.

**What it is not:** a stats library, a dashboard, or an experiment registry. Scope is intentionally narrow — the three-step guided flow.

---

## Folder structure

```
ab-testing-framework/
├── Home.py               ← Streamlit entry point
├── requirements.txt
├── pages/
│   ├── 0_Idea_Validator.py
│   ├── 1_Sample_Size.py
│   └── 2_Results_Interpreter.py
├── stats/
│   ├── __init__.py
│   ├── sample_size.py    ← power analysis math
│   ├── frequentist.py    ← two-proportion z-test, SRM check
│   └── bayesian.py       ← Beta-Binomial conjugate model
└── llm/
    ├── __init__.py
    ├── idea_validator.py ← routing engine
    └── verdict.py        ← results verdict layer
```

---

## Architecture decisions

### `stats/` is pure Python — no Streamlit

Stats modules have zero Streamlit imports. Pages import from `stats/`; math never imports from pages. This makes the engine independently testable and usable as a library outside the UI.

### Guided 3-step flow, not a toolkit

The app enforces a sequence: design → size → interpret. This is deliberate — most experiment mistakes happen upstream of data collection, and a freeform toolkit doesn't prevent them. Step 0 (Idea Validator) is the differentiator; it routes ideas before any traffic is committed.

### Ollama (local LLM) over a cloud API

The LLM layer calls Ollama at `localhost:11434` using plain HTTP (`requests`). Reasons: no API key required for someone running the tool, works offline, model is swappable. Model defaults to `llama3.2`; the constant lives in `llm/idea_validator.py` and `llm/verdict.py`.

Temperature strategy:
- `idea_validator.py`: `temperature=0.2` — routing decisions must be consistent
- `verdict.py`: `temperature=0.3` — factual, but with some interpretive range

### Both frequentist and Bayesian

They answer different questions. Frequentist (`stats/frequentist.py`) gives p-value and confidence interval. Bayesian (`stats/bayesian.py`) gives P(B > A) and expected loss via Beta-Binomial conjugate (200K Monte Carlo samples — no MCMC needed). Both are shown in Step 2; the LLM verdict synthesises them.

### MDE is the business gate

Statistical significance (p < α) is necessary but not sufficient to trigger a ship recommendation. Results must also exceed the pre-committed minimum detectable effect. A result at p=0.04 with +4% lift when MDE was set to 10% should not ship. The Results Interpreter enforces this explicitly.

### Absolute vs relative MDE

The UI accepts relative MDE ("detect a 10% improvement") because that's how product teams think. Internally, absolute MDE is computed and both are displayed. The distinction is explained inline.

### One-sided vs two-sided tests

Default is two-sided. One-sided is valid only when you can genuinely pre-commit that the variant being worse is impossible — which is rarely true. Both are supported; the UI surfaces a warning before allowing one-sided.

---

## Local setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# LLM features require Ollama
ollama pull llama3.2

streamlit run Home.py
```

The statistical modules work without Ollama. `llm/verdict.py` exposes `check_ollama_available()` — the UI degrades gracefully when Ollama is not running.

---

## What's next

- `stats/sequential.py` — SPRT / always-valid p-values (fix for peeking problem)
- `pages/3_Peeking.py` — interactive simulation: false positive rate vs number of peeks
- Shareable output from Results Interpreter (copy-to-Slack formatted summary)

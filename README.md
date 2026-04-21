# A/B Testing Framework

> A guided, end-to-end tool for designing, sizing, and interpreting A/B experiments — with an LLM layer that translates statistical results into plain-English recommendations.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-FF4B4B)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**[Live Demo](https://ab-test-framework.streamlit.app/)**

---

## What it does

Most A/B testing tools start after you've collected data. This one starts before.

The framework guides you through the full experiment lifecycle in three steps:

1. **Should I test this?** — routes your idea to the right method (A/B test, user test, feature flag, or just ship) and generates a structured experiment brief if testing is warranted.
2. **How many users do I need?** — calculates the minimum sample size given your baseline conversion rate, minimum detectable effect, significance level, and statistical power.
3. **What do the results mean?** — runs a sample ratio mismatch check, frequentist and Bayesian analyses, and produces a plain-English ship/don't-ship recommendation.

---

## Features

- **Idea Validator** — LLM-powered routing with structured output for PMs, designers, and engineers
- **Sample Size Calculator** — power analysis with sensitivity and power curves
- **Results Interpreter** — SRM check + two-proportion z-test + Beta-Binomial Bayesian analysis + LLM verdict
- **MDE as the business gate** — statistical significance alone doesn't trigger a ship recommendation; results must exceed the pre-committed minimum detectable effect
- **Both frequentist and Bayesian** — p-value for rigor, P(B > A) for intuition
- **Local LLM** — runs on [Ollama](https://ollama.ai) (no API key, works offline)

---

## Quick start

### Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai) installed and running locally

### Installation

```bash
git clone https://github.com/nishyajoylin-s/ab-testing-framework.git
cd ab-testing-framework

python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

ollama pull llama3.2
streamlit run Home.py
```

Open [http://localhost:8501](http://localhost:8501).

> The LLM features (Idea Validator and Results verdict) require Ollama running at `localhost:11434`. The calculator and statistical analysis work without it.

---

## Architecture

```
stats/      Pure Python math — no Streamlit imports. Importable as a library.
llm/        Ollama-backed routing (idea validator) and verdict (results interpreter).
pages/      Streamlit UI pages. Import from stats/ and llm/ — no math here.
Home.py     Entry point and landing page.
```

The `stats/` modules have no UI dependency by design — you can use them outside of Streamlit:

```python
from stats.sample_size import calculate
from stats.frequentist import analyse
from stats.bayesian import analyse as bayes_analyse
```

---

## Tech stack

| Layer | Library |
|---|---|
| UI | Streamlit |
| Charts | Plotly |
| Statistics | SciPy, NumPy |
| LLM | Ollama (llama3.2) via HTTP |
| Data | Pandas |

---

## Roadmap

- [ ] Peeking problem simulator — interactive simulation showing false positive inflation from early stopping
- [ ] Sequential testing — SPRT / always-valid p-values
- [ ] Shareable results — copy-to-Slack formatted output

---

## License

MIT

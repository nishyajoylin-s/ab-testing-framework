# A/B Testing Framework

> A guided, end-to-end tool for designing, sizing, and interpreting A/B experiments — with an LLM layer that translates statistical results into plain-English recommendations.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-FF4B4B)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**[Live Demo](https://ab-test-framework.streamlit.app/)**

---

## Why this was built

Most A/B testing tools start after you've collected data. This one starts before — at the hypothesis.

The core insight: **most experiment failures happen before a single user is assigned to a variant.** No clear hypothesis. Tests underpowered to detect a meaningful effect. Peeking at results on day 3 and calling it a win. Shipping a statistically significant result that didn't actually clear the business threshold.

This framework enforces structure at each stage specifically to prevent those upstream mistakes. It's opinionated by design — you can't run the results interpreter before you've committed to a minimum detectable effect.

---

## Who it's for

Built for the **Product Quad** — the four roles that touch every experiment:

| Role | How they use this tool |
|---|---|
| **Product Manager** | Step 0 to route ideas (test vs. flag vs. just ship); Step 3 Workspace to generate experiment briefs and track the registry |
| **Designer** | Step 0 to understand whether an interaction change warrants an A/B test or a usability session first |
| **Engineer** | Step 1 to get sample size before wiring feature flags; `stats/` modules are importable as a pure-Python library |
| **Data / Analyst** | Step 2 to run SRM checks, frequentist + Bayesian analysis, and get a plain-English verdict with the pre-committed MDE as the gate |

See [PLAYBOOK.md](PLAYBOOK.md) for the full experiment methodology — roles, lifecycle phases, pre-test checklist, and stopping rules.

---

## What it does

The framework guides you through the full experiment lifecycle in four steps:

**Step 0 — Should I test this?**
Routes your idea to the right method (A/B test, user research, feature flag, or just ship) and generates a structured experiment brief if testing is warranted. LLM-powered, but grounded in a decision rubric — not a free-form chat.

**Step 1 — How many users do I need?**
Power analysis that forces you to commit to your baseline conversion rate, minimum detectable effect, significance level, and power before any traffic is committed. Sensitivity and power curves show the cost of every assumption.

**Step 2 — What do the results mean?**
Runs a sample ratio mismatch (SRM) check, a two-proportion z-test, and a Beta-Binomial Bayesian analysis, then produces a plain-English ship/don't-ship recommendation. Statistical significance alone doesn't trigger a ship — results must also clear the pre-committed MDE.

**Step 3 — Workspace**
Experiment brief generator, results doc generator, downloadable templates, and a searchable experiment registry. Briefs and results docs export as Markdown for pasting into Notion, Confluence, or Linear. Registry persists to Supabase when configured (optional).

---

## Features

- **Idea Validator** — LLM-powered routing with structured output for PMs, designers, and engineers
- **Sample Size Calculator** — power analysis with sensitivity and power curves
- **Results Interpreter** — SRM check + two-proportion z-test + Beta-Binomial Bayesian analysis + LLM verdict
- **MDE as the business gate** — statistical significance alone doesn't trigger a ship recommendation; results must exceed the pre-committed minimum detectable effect
- **Both frequentist and Bayesian** — p-value for rigor, P(B > A) for intuition
- **Local LLM** — runs on [Ollama](https://ollama.ai) (no API key, works offline)
- **Workspace** — experiment brief + results doc generator, Markdown export, optional Supabase registry

---

## Local setup

### Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai) installed (required for Step 0 Idea Validator and Step 2 LLM verdict; Steps 1 and 2 stats work without it)

### Step-by-step

```bash
# 1. Clone the repo
git clone https://github.com/nishyajoylin-s/ab-testing-framework.git
cd ab-testing-framework

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Pull the LLM model
ollama pull llama3.2

# 5. Start Ollama (if it isn't already running)
ollama serve &

# 6. Run the dashboard
streamlit run Home.py
```

Open [http://localhost:8501](http://localhost:8501).

> **Tip:** Steps 1 (Sample Size) and 2 (statistical analysis) work fully offline without Ollama. Only the LLM verdict in Step 2 and the Idea Validator in Step 0 require Ollama at `localhost:11434`. The app degrades gracefully when Ollama is not running.

---

## Optional: Supabase for Workspace registry

The Workspace tab saves experiments to Supabase so the registry persists across sessions. Without this, the app works but registry changes are lost on page refresh.

**1. Create `.streamlit/secrets.toml`** (already in `.gitignore`):

```toml
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-anon-key"
```

**2. Create the experiments table** in your Supabase SQL editor:

```sql
create table experiments (
  id uuid default gen_random_uuid() primary key,
  created_at timestamptz default now(),
  name text,
  owner text,
  status text,
  start_date text,
  end_date text,
  hypothesis text,
  control_description text,
  variant_description text,
  primary_metric text,
  secondary_metrics text,
  sample_size_per_variant int,
  risks text,
  notes text,
  decision text,
  result text,
  control_rate text,
  variant_rate text,
  absolute_lift text,
  p_value text,
  learnings text,
  next_steps text
);
```

The app shows a yellow warning banner in the Workspace tab if Supabase is not configured — all other features remain fully functional.

---

## Architecture

```
stats/      Pure Python math — no Streamlit imports. Importable as a library.
llm/        Ollama-backed routing (idea validator) and verdict (results interpreter).
pages/      Streamlit UI pages. Import from stats/ and llm/ — no math here.
utils/      Supabase client and Markdown doc generator.
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
| Registry | Supabase (optional) |

---

## Roadmap

- [ ] Peeking problem simulator — interactive simulation showing false positive inflation from early stopping
- [ ] Sequential testing — SPRT / always-valid p-values
- [ ] Shareable results — copy-to-Slack formatted output

---

## License

MIT

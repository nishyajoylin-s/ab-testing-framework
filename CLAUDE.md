# CLAUDE.md — A/B Testing Framework

> Start here. This file is the single source of truth for this project — context, decisions, thinking process, and where we left off. Update it every session.

---

## Why this project exists

**The narrative:** "I've used ABsmartly in production — I know what the tool does. This project shows I understand the statistical engine underneath it."

**Portfolio goals:**
- Public tool: paste experiment data → get a full statistical report + plain-English recommendation
- GitHub reference repo for anyone running A/B tests
- LinkedIn talking point: "I implemented Bayesian A/B testing and built an LLM decision layer from scratch"
- Interview signal: experimentation at the statistical level, not just the product level

---

## What we're building

A reusable Python framework covering the full A/B test lifecycle:

| Module | What it does | Status |
|--------|-------------|--------|
| Idea validator | Routes idea to A/B test / user test / feature flag / just ship. Generates experiment brief. | **Done** |
| Sample size calculator | Given baseline, MDE, power, α → minimum n + runtime | **Done** |
| Results interpreter | SRM check + frequentist + Bayesian + LLM plain-English verdict | **Done** |
| Peeking simulator | Show why early stopping inflates false positives | Next |
| Sequential testing | SPRT / always-valid p-values as the fix | Not started |
| LLM idea router | Ollama → should I test this? → PM + Designer + Engineer notes | **Done** |
| LLM verdict layer | Ollama → plain-English ship/don't-ship recommendation | **Done** |

---

## Folder structure

```
ab-testing-framework/
├── CLAUDE.md                    ← you are here (context + decision log)
├── README.md
├── requirements.txt
├── app.py                       ← Streamlit home / landing page
├── pages/
│   ├── 1_Sample_Size.py         ← calculator UI
│   ├── 2_Frequentist.py         ← (next)
│   ├── 3_Bayesian.py
│   ├── 4_Peeking_Problem.py
│   └── 5_Decision_Engine.py
└── stats/
    ├── __init__.py
    ├── sample_size.py            ← pure math, no UI
    ├── frequentist.py
    ├── bayesian.py
    ├── sequential.py
    └── decision.py
```

**Design principle:** `stats/` is pure Python math — no Streamlit imports. Pages import from `stats/`. This keeps the engine independently testable and reusable outside Streamlit.

---

## Real-world context (from team docs)

Reviewed actual team experimentation docs (Experimentation Guide, Registry, Starter Playbook).
Key findings that shaped design decisions:

- **User is the Data owner** — not the primary user of this tool. Primary users are PMs self-serving.
- **Root problem is one chain, not two:** Bad hypothesis → wrong metric → misread small/medium result → PM escalates to Data person.
- **"Especially small/medium changes"** — core confusion is between three different things:
  - Statistical significance (p < α): "did random chance cause this?"
  - Effect size (the lift %): "how big is the change?"
  - Practical significance (≥ MDE they committed to upfront): "is it worth shipping?"
  A PM who set MDE=10% and got +4% at p=0.04 should NOT ship. The tool must catch this.
- **Registry:** Don't build it. Recommend their Excel approach as best practice. Focus on the tool.
- **This is a portfolio piece**, not a work tool. Show depth, not just simplicity.

---

## Architecture decision: guided 3-step flow (not a toolkit)

PMs don't want a calculator. They want to be told what to do. So:

```
Step 1: Design  → LLM validates hypothesis + sample size calculator
                   [already built: pages/1_Sample_Size.py]
Step 2: [test runs — nothing in the tool]
Step 3: Results → paste data → SRM check → stats → LLM plain-English verdict
                   [building now: pages/2_Results_Interpreter.py]
Bonus:  Peeking → simulation showing false positive inflation if you stop early
```

The differentiator: most tools only do Step 3 stats. Step 1 LLM validation is rare and addresses the upstream problem.

---

## LLM layer: Ollama (local) — not Anthropic API

**Decision:** Use Ollama (local LLM at localhost:11434) instead of Anthropic API.

**Why:**
- User has Ollama set up locally — zero cost, works offline
- Better for a portfolio demo (no API key needed for someone running the tool)
- Shows ability to work with local LLMs, not just cloud APIs
- Model is configurable — defaults to llama3.2, can swap to any Ollama model

**Implementation:** Direct HTTP call to `POST http://localhost:11434/api/chat` using `requests`.
No additional library dependency needed. Model name stored in `llm/verdict.py` as a constant.

---

## Thinking process & key decisions

### Why separate stats/ from pages/?
The engine should be usable as a library, not just as a UI. Someone should be able to `from stats.sample_size import calculate` in their own code. Mixing Streamlit into the math makes it untestable and unportable. This also signals "I think in libraries, not scripts."

### Why start with sample size?
It's the most underrated part of A/B testing. Most practitioners cargo-cult n=1000 or "run for 2 weeks." The sample size calculator forces you to make your assumptions explicit (baseline, MDE, power) before touching data — which is the right mindset. It's also the cleanest standalone module: pure math in, number out.

### Why show both Frequentist AND Bayesian?
They answer different questions:
- Frequentist: "If H0 is true, how surprising is this result?" → p-value
- Bayesian: "Given this data, what's my belief about which variant is better?" → P(B > A)

Showing both, and explaining when to use each, is the signal that separates someone who has read about A/B testing from someone who has thought about it. The framing: frequentist for regulated industries (pharma, finance) where "false positive rate" has legal meaning; Bayesian for product teams who want to ship faster.

### Why simulate the peeking problem rather than just explain it?
Interactive simulation is the best teacher here. If you watch your false positive rate climb from 5% to 25% as you peek more, you remember it. A paragraph explaining it doesn't stick the same way.

### Why an LLM verdict layer?
Two reasons:
1. Most experiment results are consumed by PMs and stakeholders who don't read p-values. The bottleneck is translation, not analysis.
2. It's a concrete Claude API integration that's genuinely useful — not AI for the sake of AI.

The LLM doesn't replace the stats. It reads the stats output and writes the business-facing summary. Stats → LLM → plain English.

### MDE: absolute vs relative — which default?
Relative MDE is more intuitive for product teams ("I want to detect a 10% improvement") but absolute MDE is what the math needs. We default to relative in the UI but compute absolute internally and show both. The UI explains the difference inline.

### One-sided vs two-sided test?
Default: two-sided. One-sided is only valid when you can genuinely pre-commit to "we only care if B is better, never if B is worse" — which is rarely true in practice. We offer both but warn strongly before letting someone choose one-sided.

---

## Session log

### Session 3 — 2026-04-15
**Built:** `llm/idea_validator.py`, `pages/0_Idea_Validator.py`

**Strategic shift this session:**
The tool is now positioned as: *"The tool that prevents bad experiments, not just analyses them. Every other tool starts after you've collected the data. Mine starts before."*

This led to adding a new entry point: Step 0 ("Should I test this?") which routes ideas to the right method before wasting traffic on a bad experiment.

**Key decisions:**
- Step 0 is a routing page, not just a hypothesis validator — it answers "A/B test vs user test vs feature flag vs just ship"
- LLM uses temperature=0.2 (lower than verdict) — routing decisions need to be consistent
- Output structured for three audiences in one view: PM / Designer / Engineer — three columns, not three pages
- Experiment brief uses Confluence one-pager format (from team docs): problem, hypothesis, primary metric, guardrails, audience, MDE signal
- "If A/B test → carry forward to Sample Size" via `st.session_state` prefill (baseline + MDE flow through)
- Four routing signals as yes/no toggles (not sliders) — quick, honest answers, not form fatigue
- `parse_route()` utility in `idea_validator.py` extracts route from LLM response for programmatic badge rendering

**What the tool now covers:**
```
Step 0: Should I test this?   → routes to A/B / user test / feature flag / just ship
                                 if A/B: generates Confluence experiment brief (PM + Designer + Engineer)
Step 1: Sample Size           → prefilled from Step 0 if routed to A/B
[test runs]
Step 2: Results Interpreter   → SRM → frequentist → Bayesian → LLM verdict
```

**Left off at:** All three steps working. Next priority is peeking simulator (shows why checking early inflates false positives).

**Next session should:**
1. Build `stats/sequential.py` — SPRT / peeking simulation
2. Build `pages/3_Peeking.py` — interactive simulation showing false positive inflation
3. Add shareable output to Results Interpreter (copy-to-Slack formatted summary)
4. Deploy to Streamlit Cloud for portfolio

---

### Session 1 — 2026-04-15
**Built:** Project scaffold, CLAUDE.md, `stats/sample_size.py`, Streamlit sample size calculator (`pages/1_Sample_Size.py`).

**Decisions made this session:**
- Project location: `~/ab-testing-framework/` (separate from taxi dashboard)
- Streamlit multi-page app structure (sidebar navigation = cleaner than tabs for a growing tool)
- Start with conversion rate experiments (binary outcome) — most common A/B test type. Continuous metrics (revenue, time-on-site) come later in the frequentist module via t-test.
- Sensitivity analysis chart added: shows how sample size changes across a range of MDEs, so users can see the cost of being more ambitious.
- No database / persistence in this phase — stateless calculator. State management comes when we add the decision engine.

**Left off at:** Sample size calculator complete and running. Next session starts with the frequentist engine (`stats/frequentist.py` + `pages/2_Frequentist.py`).

**Next session should:**
1. Build `stats/frequentist.py`: two-proportion z-test, chi-square, with p-value + CI output
2. Build `pages/2_Frequentist.py`: input observed counts → full statistical report
3. Then move to Bayesian (beta-binomial conjugate model)

---

## Running the app

```bash
cd ~/ab-testing-framework
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Open: http://localhost:8501

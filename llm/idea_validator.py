"""
Idea validation layer — routes a feature idea to the right experiment method.

Routes to one of four outcomes:
  A/B TEST    — randomised controlled experiment, correct and worth the cost
  USER TEST   — qualitative feedback needed first (UX unclear, hypothesis weak)
  FEATURE FLAG — ship and monitor, no split needed (risk is low or change is tiny)
  JUST SHIP   — no test needed (fix, copy change, internal tool, irreversible)

LLM backend priority:
  1. Groq API (cloud, free tier) — used when GROQ_API_KEY is available.
     Works on Streamlit Cloud. Model: llama-3.3-70b-versatile.
  2. Ollama (local) — fallback for local development.
     Requires `ollama serve` and `ollama pull llama3.2`.
"""
import os
import requests
from dataclasses import dataclass, field
from typing import Optional, Tuple

OLLAMA_URL   = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "llama3.2"
GROQ_URL     = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL   = "llama-3.3-70b-versatile"
TIMEOUT_SEC  = 90


@dataclass
class IdeaInput:
    feature_description: str
    problem_statement: str
    primary_metric: str
    needs_statistical_proof: bool
    primarily_ux_change: bool
    tracking_exists: bool
    enough_traffic: bool
    secondary_metrics: str = ""
    target_audience: str = ""


def _build_prompt(idea: IdeaInput) -> str:
    routing_context = f"""
Traffic signal — enough traffic for an experiment: {"YES" if idea.enough_traffic else "NO (may be too small to detect effects)"}
Statistical proof required by stakeholders: {"YES" if idea.needs_statistical_proof else "NO"}
Primarily a UX/visual change: {"YES" if idea.primarily_ux_change else "NO"}
Existing tracking can measure it: {"YES" if idea.tracking_exists else "NO (tracking work needed first)"}
""".strip()

    secondary_block = f"\nGuardrail / secondary metrics: {idea.secondary_metrics}" if idea.secondary_metrics else ""
    audience_block  = f"\nTarget audience: {idea.target_audience}" if idea.target_audience else ""

    return f"""You are an expert in experiment design and product analytics. Your job is to tell a PM
whether their idea should be A/B tested, and if so, help them write a Confluence experiment brief.

You must be direct. Do NOT suggest an A/B test just to be safe — A/B tests have real costs (time,
traffic, engineering). Only recommend one when the conditions justify it.

---
IDEA SUBMITTED:

Feature / change: {idea.feature_description}
Problem being solved: {idea.problem_statement}
Primary success metric: {idea.primary_metric}{secondary_block}{audience_block}

ROUTING SIGNALS:
{routing_context}
---

Respond in EXACTLY this format (use the section headers verbatim, write the content after the colon):

ROUTE: [Exactly one of: A/B TEST | USER TEST | FEATURE FLAG | JUST SHIP]

RATIONALE: [2-3 sentences. Why this route? Be honest — if A/B test isn't the right call, say so directly and explain what should happen instead.]

HYPOTHESIS: [Only write this if route is A/B TEST. Format: "If we [specific change], then [primary metric] will [increase/decrease] by [realistic estimated %] because [causal reason]." If route is not A/B TEST, write "N/A".]

EXPERIMENT BRIEF:
[Only write this section if route is A/B TEST. Write a concise brief in this exact structure:
- Problem: [1 sentence]
- Hypothesis: [copy from HYPOTHESIS above]
- Primary metric: [metric + direction + what counts as success]
- Guardrail metrics: [what we must NOT break, even if primary metric wins]
- Audience: [who is in the experiment — all users, segment, platform]
- MDE: [minimum lift worth shipping — be realistic, not optimistic]
- Duration signal: [rough weeks needed — say "run sample size calculator with [baseline]% baseline and [MDE]% MDE to get exact number"]
If route is not A/B TEST, write "N/A".]

PM NOTES: [2-3 bullet points on decisions the PM owns — what to commit to before the test starts, what the decision criteria are.]

DESIGNER NOTES: [2-3 bullet points on UX risks, edge cases to design for, or qualitative signals to monitor alongside the experiment. If route is USER TEST, explain what kind of user test and what to look for.]

ENGINEER NOTES: [2-3 bullet points on tracking requirements — what events need to fire, when, and how to verify the assignment is clean. If tracking doesn't exist yet, say so explicitly.]

Keep total response under 350 words. Be direct. Do not add encouragement or filler phrases."""


def _call_groq(prompt: str, api_key: str) -> Tuple[str, Optional[str]]:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
        "max_tokens": 800,
    }
    try:
        resp = requests.post(GROQ_URL, headers=headers, json=payload, timeout=TIMEOUT_SEC)
        resp.raise_for_status()
        text = resp.json()["choices"][0]["message"]["content"].strip()
        return text, None
    except requests.exceptions.HTTPError as e:
        return "", f"Groq API error: {e.response.status_code} — {e.response.text[:200]}"
    except requests.exceptions.Timeout:
        return "", f"Groq timed out after {TIMEOUT_SEC}s."
    except Exception as e:
        return "", f"Groq error: {e}"


def _call_ollama(prompt: str) -> Tuple[str, Optional[str]]:
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "options": {"temperature": 0.2, "top_p": 0.9},
    }
    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=TIMEOUT_SEC)
        resp.raise_for_status()
        text = resp.json()["message"]["content"].strip()
        return text, None
    except requests.exceptions.ConnectionError:
        return "", "Could not connect to Ollama. Make sure Ollama is running: `ollama serve`"
    except requests.exceptions.Timeout:
        return "", f"Ollama timed out after {TIMEOUT_SEC}s."
    except Exception as e:
        return "", f"Ollama error: {e}"


def validate_idea(idea: IdeaInput, groq_api_key: str = "") -> Tuple[str, Optional[str]]:
    prompt = _build_prompt(idea)
    if groq_api_key:
        return _call_groq(prompt, groq_api_key)
    return _call_ollama(prompt)


def check_llm_available(groq_api_key: str = "") -> Tuple[bool, str]:
    """Returns (is_available, message). Prefers Groq if key is provided."""
    if groq_api_key:
        return True, "Using Groq API (cloud)."
    try:
        requests.get("http://localhost:11434", timeout=3)
        return True, "Using Ollama (local)."
    except requests.exceptions.ConnectionError:
        return False, "No LLM available. Add a GROQ_API_KEY secret or run `ollama serve` locally."
    except Exception as e:
        return False, str(e)


def parse_route(text: str) -> Optional[str]:
    """Extract the route label from the LLM response."""
    for line in text.split("\n"):
        if line.strip().startswith("ROUTE:"):
            route = line.replace("ROUTE:", "").strip().upper()
            for valid in ("A/B TEST", "USER TEST", "FEATURE FLAG", "JUST SHIP"):
                if valid in route:
                    return valid
    return None

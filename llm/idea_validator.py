"""
Idea validation layer — calls Ollama to answer:
  "Should this even be an A/B test?"

Routes to one of four outcomes:
  A/B TEST    — randomised controlled experiment, correct and worth the cost
  USER TEST   — qualitative feedback needed first (UX unclear, hypothesis weak)
  FEATURE FLAG — ship and monitor, no split needed (risk is low or change is tiny)
  JUST SHIP   — no test needed (fix, copy change, internal tool, irreversible)

If the route is A/B TEST, also generates an experiment brief in Confluence one-pager
format, with separate notes for PM, Designer, and Engineer.

Model: Ollama (local). Configured via OLLAMA_MODEL constant.
"""
import requests
from dataclasses import dataclass, field
from typing import Optional, Tuple, List

OLLAMA_URL   = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "llama3.2"
TIMEOUT_SEC  = 90


@dataclass
class IdeaInput:
    # What is being changed
    feature_description: str       # e.g. "Move the checkout button above the fold"
    problem_statement: str         # e.g. "Users drop off at checkout at 70% rate"
    primary_metric: str            # e.g. "Checkout completion rate"

    # Routing signals (answered by PM as yes/no)
    needs_statistical_proof: bool  # Do stakeholders need proof before decision?
    primarily_ux_change: bool      # Is this mainly a visual / UX change?
    tracking_exists: bool          # Can you measure this with existing tracking?
    enough_traffic: bool           # Rough traffic check (PM self-assessed)

    # Optional context
    secondary_metrics: str = ""    # Guardrails, other KPIs (free text)
    target_audience: str = ""      # Who sees this? All users, new users, mobile only?


def _build_prompt(idea: IdeaInput) -> str:
    routing_context = f"""
Traffic signal — enough traffic for an experiment: {"YES" if idea.enough_traffic else "NO (may be too small to detect effects)"}
Statistical proof required by stakeholders: {"YES" if idea.needs_statistical_proof else "NO"}
Primarily a UX/visual change: {"YES" if idea.primarily_ux_change else "NO"}
Existing tracking can measure it: {"YES" if idea.tracking_exists else "NO (tracking work needed first)"}
""".strip()

    secondary_block = ""
    if idea.secondary_metrics:
        secondary_block = f"\nGuardrail / secondary metrics: {idea.secondary_metrics}"

    audience_block = ""
    if idea.target_audience:
        audience_block = f"\nTarget audience: {idea.target_audience}"

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


def validate_idea(idea: IdeaInput) -> Tuple[str, Optional[str]]:
    """
    Call Ollama and return the routing + brief text.

    Returns:
        (response_text, error_message)
        On success: (text, None)
        On failure: ("", error_message)
    """
    prompt = _build_prompt(idea)

    payload = {
        "model": OLLAMA_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "options": {
            "temperature": 0.2,   # very low — we want consistent routing decisions
            "top_p": 0.9,
        },
    }

    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=TIMEOUT_SEC)
        resp.raise_for_status()
        data = resp.json()
        text = data["message"]["content"].strip()
        return text, None
    except requests.exceptions.ConnectionError:
        return "", (
            "Could not connect to Ollama. "
            "Make sure Ollama is running: `ollama serve` in a terminal."
        )
    except requests.exceptions.Timeout:
        return "", f"Ollama timed out after {TIMEOUT_SEC}s. Try a smaller/faster model."
    except Exception as e:
        return "", f"Ollama error: {e}"


def check_ollama_available() -> Tuple[bool, str]:
    """Quick health check — returns (is_available, message)."""
    try:
        requests.get("http://localhost:11434", timeout=3)
        return True, "Ollama is running."
    except requests.exceptions.ConnectionError:
        return False, "Ollama is not running. Start it with: `ollama serve`"
    except Exception as e:
        return False, str(e)


def parse_route(text: str) -> Optional[str]:
    """
    Extract the route from the LLM response.
    Returns one of: "A/B TEST", "USER TEST", "FEATURE FLAG", "JUST SHIP", or None.
    """
    for line in text.split("\n"):
        if line.strip().startswith("ROUTE:"):
            route = line.replace("ROUTE:", "").strip().upper()
            for valid in ("A/B TEST", "USER TEST", "FEATURE FLAG", "JUST SHIP"):
                if valid in route:
                    return valid
    return None

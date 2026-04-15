"""
LLM verdict layer — calls Ollama (local) to produce a plain-English
recommendation any PM can act on.

The LLM does NOT do statistics. It reads the pre-computed stats and
translates them into a business-facing narrative with a clear decision.

Model: configurable via OLLAMA_MODEL constant (default: llama3.2).
Endpoint: http://localhost:11434/api/chat (Ollama default).
"""
import json
import requests
from dataclasses import dataclass
from typing import Optional, Tuple

OLLAMA_URL   = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "llama3.2"    # change to any model you have pulled locally
TIMEOUT_SEC  = 60


@dataclass
class VerdictInput:
    # Experiment description
    experiment_name: str
    hypothesis: str

    # Observed results
    n_control: int
    conv_control: int
    n_variant: int
    conv_variant: int
    rate_control: float
    rate_variant: float
    absolute_lift: float
    relative_lift: float

    # Frequentist
    p_value: float
    ci_lower: float
    ci_upper: float
    significant: bool
    alpha: float

    # Bayesian
    prob_b_beats_a: float
    expected_loss_if_ship_b: float

    # Practical significance
    mde_absolute: Optional[float]   # pre-committed MDE (absolute pp)
    mde_met: Optional[bool]         # did observed lift meet the MDE?

    # SRM
    srm_detected: bool


def _build_prompt(v: VerdictInput) -> str:
    """
    Build a structured prompt that gives the LLM all facts it needs
    and constrains it to produce a consistent, useful output.
    """
    mde_block = ""
    if v.mde_absolute is not None:
        mde_str  = f"{v.mde_absolute * 100:.2f}pp"
        met_str  = "YES — observed lift meets or exceeds the pre-committed MDE." if v.mde_met else \
                   "NO — observed lift is BELOW the pre-committed MDE."
        mde_block = f"""
Pre-committed MDE: {mde_str}
MDE met: {met_str}"""

    srm_warning = ""
    if v.srm_detected:
        srm_warning = "\n⚠️  SAMPLE RATIO MISMATCH DETECTED. The traffic split was not as intended. Statistical results are unreliable."

    prompt = f"""You are an expert in A/B testing and product analytics. Your job is to write a clear,
honest, plain-English verdict for a PM who is not a statistician.

You have been given the statistical results below. Do NOT re-do the statistics.
Your job is to translate them into a business recommendation.

---
EXPERIMENT: {v.experiment_name}
HYPOTHESIS: {v.hypothesis}
{srm_warning}
RESULTS:
- Control: {v.n_control:,} users, {v.conv_control:,} conversions ({v.rate_control * 100:.2f}%)
- Variant: {v.n_variant:,} users, {v.conv_variant:,} conversions ({v.rate_variant * 100:.2f}%)
- Observed lift: {v.absolute_lift * 100:+.2f}pp ({v.relative_lift * 100:+.1f}% relative)
- 95% Confidence interval: [{v.ci_lower * 100:+.2f}pp, {v.ci_upper * 100:+.2f}pp]
- p-value: {v.p_value:.4f} (threshold: {v.alpha})
- Statistically significant: {"YES" if v.significant else "NO"}
- Bayesian P(Variant > Control): {v.prob_b_beats_a * 100:.1f}%
- Expected loss if we ship Variant: {v.expected_loss_if_ship_b * 100:.3f}pp{mde_block}
---

Write your verdict in exactly this format:

HEADLINE: [One sentence. State the result and the decision. Be direct.]

WHAT HAPPENED: [2-3 sentences. Explain what the numbers mean in plain English.
No jargon. Mention whether the result is statistically significant and what the
confidence interval tells us.]

DECISION: [Exactly one of: SHIP / DO NOT SHIP / INCONCLUSIVE — then one sentence explaining why.]

WATCH OUT FOR: [1-2 sentences on the most important caveat or risk the PM should be aware of.]

Keep it under 200 words total. Be honest. If the result is inconclusive, say so clearly —
do not soften it into a "promising" result. If the MDE was not met, say so explicitly."""

    return prompt


def get_verdict(v: VerdictInput) -> Tuple[str, Optional[str]]:
    """
    Call Ollama and return the plain-English verdict.

    Returns:
        (verdict_text, error_message)
        On success: (verdict_text, None)
        On failure: ("", error_message)
    """
    prompt = _build_prompt(v)

    payload = {
        "model": OLLAMA_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "options": {
            "temperature": 0.3,   # low temp for consistent, factual output
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
        r = requests.get("http://localhost:11434", timeout=3)
        return True, "Ollama is running."
    except requests.exceptions.ConnectionError:
        return False, "Ollama is not running. Start it with: `ollama serve`"
    except Exception as e:
        return False, str(e)

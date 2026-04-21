"""
Deterministic verdict engine — no LLM dependency.

Reads pre-computed stats and applies explicit decision rules to produce
a structured, plain-English verdict. Rules are auditable and never hallucinate.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class VerdictInput:
    experiment_name: str
    hypothesis: str
    n_control: int
    conv_control: int
    n_variant: int
    conv_variant: int
    rate_control: float
    rate_variant: float
    absolute_lift: float
    relative_lift: float
    p_value: float
    ci_lower: float
    ci_upper: float
    significant: bool
    alpha: float
    prob_b_beats_a: float
    expected_loss_if_ship_b: float
    mde_absolute: Optional[float]
    mde_met: Optional[bool]
    srm_detected: bool


@dataclass
class VerdictResult:
    decision: str  # SHIP | DO NOT SHIP | INCONCLUSIVE | INVALIDATE
    headline: str
    what_happened: str
    watch_out_for: str


def rule_verdict(v: VerdictInput) -> VerdictResult:
    abs_pp   = v.absolute_lift * 100
    lift_pct = v.relative_lift * 100
    ci_l     = v.ci_lower * 100
    ci_u     = v.ci_upper * 100
    prob_pct = v.prob_b_beats_a * 100

    if v.srm_detected:
        return VerdictResult(
            decision="INVALIDATE",
            headline="Experiment is invalid — the traffic split is broken.",
            what_happened=(
                "A Sample Ratio Mismatch was detected: the traffic split was not the intended 50/50. "
                "This means the randomisation or tracking has a bug, and the results below cannot be trusted."
            ),
            watch_out_for=(
                "Do not act on any of the statistics. Investigate the assignment logic, "
                "check for bot traffic, and re-run the experiment with a clean implementation."
            ),
        )

    if not v.significant:
        if v.absolute_lift < 0 and prob_pct < 30:
            return VerdictResult(
                decision="DO NOT SHIP",
                headline=f"Variant underperformed control ({abs_pp:+.2f}pp). Do not ship.",
                what_happened=(
                    f"The variant converted at {v.rate_variant:.2%} vs control at {v.rate_control:.2%} "
                    f"({abs_pp:+.2f}pp, {lift_pct:+.1f}% relative). "
                    f"The 95% CI [{ci_l:+.2f}pp, {ci_u:+.2f}pp] sits mostly below zero. "
                    f"There is {100 - prob_pct:.1f}% Bayesian probability that control is better."
                ),
                watch_out_for=(
                    "Even without statistical significance, the direction is negative. "
                    "Investigate what drove the underperformance before iterating on this idea."
                ),
            )
        return VerdictResult(
            decision="INCONCLUSIVE",
            headline=f"Not enough evidence to decide (p = {v.p_value:.4f}). Run longer or revisit the hypothesis.",
            what_happened=(
                f"The observed lift is {abs_pp:+.2f}pp ({lift_pct:+.1f}% relative), "
                f"but p = {v.p_value:.4f} does not clear the {v.alpha} threshold. "
                f"The 95% CI [{ci_l:+.2f}pp, {ci_u:+.2f}pp] includes zero — "
                f"we cannot rule out random chance. Bayesian P(B > A) = {prob_pct:.1f}%."
            ),
            watch_out_for=(
                "The most common mistake here is calling this a 'promising trend' and shipping anyway. "
                "An inconclusive result is not a green light. Either extend the experiment to reach the planned "
                "sample size, or treat it as a null result."
            ),
        )

    # Statistically significant from here down
    if v.mde_absolute is not None and v.mde_met is False:
        mde_pp = v.mde_absolute * 100
        return VerdictResult(
            decision="DO NOT SHIP",
            headline=f"Significant, but lift ({abs_pp:+.2f}pp) is below the pre-committed MDE ({mde_pp:.2f}pp).",
            what_happened=(
                f"The result is statistically significant (p = {v.p_value:.4f}) with a {abs_pp:+.2f}pp lift "
                f"({lift_pct:+.1f}% relative). However, you committed to needing at least {mde_pp:.2f}pp "
                f"to justify shipping. The effect is real but not large enough to meet your bar."
            ),
            watch_out_for=(
                "Statistical significance is not the same as practical significance. "
                "Shipping a result below your pre-committed MDE means moving the goalposts. "
                "Treat this as a null result unless there is a compelling business case to revisit the MDE."
            ),
        )

    # Significant + MDE met (or no MDE committed)
    if prob_pct >= 95:
        return VerdictResult(
            decision="SHIP",
            headline=f"Ship it. Strong evidence that the variant improves {v.experiment_name}.",
            what_happened=(
                f"The variant converted at {v.rate_variant:.2%} vs control at {v.rate_control:.2%} "
                f"({abs_pp:+.2f}pp, {lift_pct:+.1f}% relative). "
                f"p = {v.p_value:.4f}, 95% CI [{ci_l:+.2f}pp, {ci_u:+.2f}pp]. "
                f"Bayesian P(B > A) = {prob_pct:.1f}% with expected loss of "
                f"{v.expected_loss_if_ship_b * 100:.3f}pp if wrong."
            ),
            watch_out_for=(
                f"Monitor guardrail metrics for 1–2 weeks post-launch. "
                f"The CI lower bound is {ci_l:+.2f}pp — plan for the conservative case, not the observed lift."
            ),
        )

    if prob_pct >= 80:
        return VerdictResult(
            decision="SHIP",
            headline=f"Lean ship — significant result, moderate Bayesian confidence ({prob_pct:.1f}%).",
            what_happened=(
                f"The variant shows a {abs_pp:+.2f}pp lift ({lift_pct:+.1f}% relative), "
                f"p = {v.p_value:.4f}. Frequentist threshold is met, but Bayesian P(B > A) = {prob_pct:.1f}% "
                f"means roughly 1-in-5 chance control is actually better."
            ),
            watch_out_for=(
                "Consider a staged rollout rather than a full launch. If you have the traffic, "
                "running slightly longer to push P(B > A) above 95% reduces the risk of a bad ship."
            ),
        )

    # Significant p-value but Bayesian confidence is weak — likely a borderline result
    return VerdictResult(
        decision="INCONCLUSIVE",
        headline=f"Frequentist significant but Bayesian confidence is weak ({prob_pct:.1f}%). Treat as inconclusive.",
        what_happened=(
            f"p = {v.p_value:.4f} clears the threshold, but Bayesian P(B > A) = {prob_pct:.1f}% suggests the "
            f"evidence is weaker than the p-value implies. This often happens near the significance boundary."
        ),
        watch_out_for=(
            "If you checked results multiple times before stopping (peeking), the true false positive rate "
            "is higher than your α. Extend the experiment or use sequential testing before acting on this."
        ),
    )

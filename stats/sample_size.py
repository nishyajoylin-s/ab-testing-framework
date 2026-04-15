"""
Sample size calculator for A/B tests on binary conversion metrics.

Formula: two-proportion z-test
  n = (Z_α + Z_β)² × (p1(1−p1) + p2(1−p2)) / (p1 − p2)²

where:
  p1 = baseline conversion rate
  p2 = expected treatment conversion rate
  Z_α = z-score for significance level (one or two-tailed)
  Z_β = z-score for desired power

This module is pure Python — no Streamlit, no UI. Import it anywhere.
"""
import math
from dataclasses import dataclass
from typing import List, Optional

from scipy import stats


@dataclass
class SampleSizeResult:
    n_per_variant: int
    n_total: int
    control_rate: float          # p1
    treatment_rate: float        # p2
    absolute_mde: float          # |p2 - p1|
    relative_mde: float          # |p2 - p1| / p1
    alpha: float
    power: float
    tails: int
    z_alpha: float
    z_beta: float
    # Optional: estimated runtime given daily traffic
    daily_traffic_per_variant: Optional[int] = None
    estimated_days: Optional[float] = None


def calculate(
    baseline_rate: float,
    mde: float,
    mde_type: str = "relative",   # "relative" | "absolute"
    alpha: float = 0.05,
    power: float = 0.80,
    tails: int = 2,
    daily_traffic: Optional[int] = None,  # total daily visitors (split 50/50)
) -> SampleSizeResult:
    """
    Calculate minimum sample size per variant for a binary A/B test.

    Args:
        baseline_rate:  Control conversion rate, e.g. 0.05 for 5%.
        mde:            Minimum detectable effect.
                        If mde_type='relative': fraction of baseline, e.g. 0.10 = 10% lift.
                        If mde_type='absolute': percentage points, e.g. 0.01 = +1pp.
        mde_type:       'relative' or 'absolute'.
        alpha:          Significance level (Type I error rate). Default 0.05.
        power:          Statistical power (1 − Type II error rate). Default 0.80.
        tails:          1 or 2. Two-tailed is the safe default.
        daily_traffic:  Optional total daily visitors to estimate runtime.

    Returns:
        SampleSizeResult dataclass with all inputs and derived outputs.
    """
    if not 0 < baseline_rate < 1:
        raise ValueError(f"baseline_rate must be in (0, 1), got {baseline_rate}")
    if mde <= 0:
        raise ValueError(f"mde must be positive, got {mde}")
    if not 0 < alpha < 1:
        raise ValueError(f"alpha must be in (0, 1), got {alpha}")
    if not 0 < power < 1:
        raise ValueError(f"power must be in (0, 1), got {power}")
    if tails not in (1, 2):
        raise ValueError(f"tails must be 1 or 2, got {tails}")

    # Derive treatment rate
    if mde_type == "relative":
        treatment_rate = baseline_rate * (1 + mde)
    else:  # absolute
        treatment_rate = baseline_rate + mde

    if not 0 < treatment_rate < 1:
        raise ValueError(
            f"Derived treatment_rate={treatment_rate:.4f} is out of (0,1). "
            "Reduce MDE or adjust baseline."
        )

    p1, p2 = baseline_rate, treatment_rate

    # Z-scores
    z_alpha = stats.norm.ppf(1 - alpha / tails)
    z_beta  = stats.norm.ppf(power)

    # Two-proportion z-test formula
    numerator   = (z_alpha + z_beta) ** 2 * (p1 * (1 - p1) + p2 * (1 - p2))
    denominator = (p2 - p1) ** 2
    n = math.ceil(numerator / denominator)

    # Runtime estimate
    estimated_days = None
    daily_per_variant = None
    if daily_traffic and daily_traffic > 0:
        daily_per_variant = daily_traffic // 2
        estimated_days    = n / daily_per_variant

    return SampleSizeResult(
        n_per_variant=n,
        n_total=n * 2,
        control_rate=p1,
        treatment_rate=p2,
        absolute_mde=abs(p2 - p1),
        relative_mde=abs(p2 - p1) / p1,
        alpha=alpha,
        power=power,
        tails=tails,
        z_alpha=round(z_alpha, 4),
        z_beta=round(z_beta, 4),
        daily_traffic_per_variant=daily_per_variant,
        estimated_days=round(estimated_days, 1) if estimated_days else None,
    )


def sensitivity_curve(
    baseline_rate: float,
    mde_values: list,
    mde_type: str = "relative",
    alpha: float = 0.05,
    power: float = 0.80,
    tails: int = 2,
) -> List[dict]:
    """
    Return n_per_variant for a range of MDE values.
    Used to render the sensitivity chart: "how does sample size change with ambition?"
    """
    results = []
    for mde in mde_values:
        try:
            r = calculate(baseline_rate, mde, mde_type, alpha, power, tails)
            results.append({"mde": mde, "n_per_variant": r.n_per_variant})
        except ValueError:
            pass  # skip invalid combos at boundary
    return results


def power_curve(
    baseline_rate: float,
    mde: float,
    mde_type: str = "relative",
    alpha: float = 0.05,
    power_values: list = None,
    tails: int = 2,
) -> List[dict]:
    """
    Return n_per_variant for a range of power levels.
    Used to show cost of higher confidence: "going from 80% to 90% power costs X more samples."
    """
    if power_values is None:
        power_values = [0.70, 0.75, 0.80, 0.85, 0.90, 0.95]
    results = []
    for pw in power_values:
        try:
            r = calculate(baseline_rate, mde, mde_type, alpha, pw, tails)
            results.append({"power": pw, "n_per_variant": r.n_per_variant})
        except ValueError:
            pass
    return results

"""
Frequentist statistical engine for A/B test analysis.

Provides:
  - Two-proportion z-test (primary analysis for binary conversion metrics)
  - Sample Ratio Mismatch (SRM) check
  - Confidence interval on the absolute lift

All functions are pure Python — no Streamlit, no UI.
"""
import math
from dataclasses import dataclass
from typing import Optional

from scipy import stats


@dataclass
class SRMResult:
    """Sample Ratio Mismatch check result."""
    n_control: int
    n_variant: int
    expected_split: float           # e.g. 0.5 for 50/50
    chi2_stat: float
    p_value: float
    srm_detected: bool              # True if p < 0.01
    actual_split: float             # actual fraction in control


@dataclass
class FrequentistResult:
    # Inputs
    n_control: int
    n_variant: int
    conv_control: int
    conv_variant: int
    alpha: float
    tails: int

    # Rates
    rate_control: float
    rate_variant: float
    absolute_lift: float            # rate_variant - rate_control
    relative_lift: float            # absolute_lift / rate_control

    # Test statistics
    z_stat: float
    p_value: float
    significant: bool

    # Confidence interval on absolute lift
    ci_lower: float
    ci_upper: float

    # Practical significance (set externally after creation)
    mde_met: Optional[bool] = None  # None if MDE not provided


def srm_check(
    n_control: int,
    n_variant: int,
    expected_split: float = 0.5,
) -> SRMResult:
    """
    Check for Sample Ratio Mismatch using chi-square test.

    A mismatch means the randomisation is broken — the statistical analysis
    is invalid regardless of what the p-value says.

    Args:
        n_control:      Observed users in control.
        n_variant:      Observed users in variant.
        expected_split: Expected fraction in control (default 0.5 for 50/50).

    Returns:
        SRMResult. srm_detected=True means STOP — do not interpret results.
    """
    n_total = n_control + n_variant
    expected_control = n_total * expected_split
    expected_variant = n_total * (1 - expected_split)

    chi2 = (
        (n_control - expected_control) ** 2 / expected_control
        + (n_variant - expected_variant) ** 2 / expected_variant
    )
    p = 1 - stats.chi2.cdf(chi2, df=1)

    return SRMResult(
        n_control=n_control,
        n_variant=n_variant,
        expected_split=expected_split,
        chi2_stat=round(chi2, 4),
        p_value=round(p, 6),
        srm_detected=p < 0.01,   # stricter than main alpha — SRM is a binary alarm
        actual_split=round(n_control / n_total, 4),
    )


def analyse(
    n_control: int,
    conv_control: int,
    n_variant: int,
    conv_variant: int,
    alpha: float = 0.05,
    tails: int = 2,
    mde_absolute: Optional[float] = None,   # pre-committed MDE in pp, e.g. 0.01
) -> FrequentistResult:
    """
    Two-proportion z-test for binary A/B test results.

    Uses a pooled proportion under H0 (no difference) for the standard error.
    Confidence interval uses unpooled standard error (correct for estimation).

    Args:
        n_control:      Total users in control.
        conv_control:   Conversions in control.
        n_variant:      Total users in variant.
        conv_variant:   Conversions in variant.
        alpha:          Significance level (default 0.05).
        tails:          1 or 2 (default 2).
        mde_absolute:   Pre-committed MDE in absolute pp (optional).
                        If provided, sets mde_met flag on the result.

    Returns:
        FrequentistResult dataclass.
    """
    if n_control <= 0 or n_variant <= 0:
        raise ValueError("Sample sizes must be positive.")
    if not (0 <= conv_control <= n_control):
        raise ValueError(f"conv_control={conv_control} must be in [0, {n_control}].")
    if not (0 <= conv_variant <= n_variant):
        raise ValueError(f"conv_variant={conv_variant} must be in [0, {n_variant}].")

    p_c = conv_control / n_control
    p_v = conv_variant / n_variant
    abs_lift = p_v - p_c
    rel_lift = abs_lift / p_c if p_c > 0 else float("inf")

    # Pooled proportion (under H0: p_c == p_v)
    p_pool = (conv_control + conv_variant) / (n_control + n_variant)
    se_pooled = math.sqrt(p_pool * (1 - p_pool) * (1 / n_control + 1 / n_variant))

    if se_pooled == 0:
        raise ValueError("Standard error is zero — check your inputs.")

    z = abs_lift / se_pooled

    if tails == 2:
        p_value = 2 * (1 - stats.norm.cdf(abs(z)))
    else:
        p_value = 1 - stats.norm.cdf(z)   # one-sided: B > A direction

    significant = p_value < alpha

    # CI on absolute lift (unpooled SE — correct for estimation, not hypothesis testing)
    se_unpooled = math.sqrt(p_c * (1 - p_c) / n_control + p_v * (1 - p_v) / n_variant)
    z_crit = stats.norm.ppf(1 - alpha / tails)
    ci_lower = abs_lift - z_crit * se_unpooled
    ci_upper = abs_lift + z_crit * se_unpooled

    mde_met = None
    if mde_absolute is not None:
        mde_met = abs(abs_lift) >= abs(mde_absolute)

    return FrequentistResult(
        n_control=n_control,
        n_variant=n_variant,
        conv_control=conv_control,
        conv_variant=conv_variant,
        alpha=alpha,
        tails=tails,
        rate_control=round(p_c, 6),
        rate_variant=round(p_v, 6),
        absolute_lift=round(abs_lift, 6),
        relative_lift=round(rel_lift, 6),
        z_stat=round(z, 4),
        p_value=round(p_value, 6),
        significant=significant,
        ci_lower=round(ci_lower, 6),
        ci_upper=round(ci_upper, 6),
        mde_met=mde_met,
    )

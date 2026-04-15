"""
Bayesian statistical engine for A/B test analysis.

Model: Beta-Binomial conjugate.
  Prior:      Beta(1, 1) — uniform, non-informative (equal probability to any rate)
  Posterior:  Beta(1 + conversions, 1 + non-conversions)

Provides:
  - P(B > A): probability variant is better than control
  - Expected loss: expected regret if we ship the wrong variant
  - 95% credible interval on each rate (HDI approximated via percentiles)

Why Beta-Binomial?
  Binary outcomes (converted / not) → Binomial likelihood.
  Beta is the conjugate prior → closed-form posterior update.
  No MCMC needed. Fast, interpretable, exact.
"""
import numpy as np
from dataclasses import dataclass
from typing import Tuple

N_SAMPLES = 200_000   # Monte Carlo samples — high enough for stable estimates


@dataclass
class BayesianResult:
    # Posteriors
    alpha_control: float    # posterior Beta alpha param for control
    beta_control: float
    alpha_variant: float
    beta_variant: float

    # Key outputs
    prob_b_beats_a: float           # P(variant > control)
    expected_loss_if_ship_b: float  # E[max(0, θ_A - θ_B)] — regret if B is wrong
    expected_loss_if_ship_a: float  # E[max(0, θ_B - θ_A)] — opportunity cost of not shipping

    # Credible intervals (95%)
    ci_control: Tuple[float, float]
    ci_variant: Tuple[float, float]

    # Posterior means
    mean_control: float
    mean_variant: float


def analyse(
    n_control: int,
    conv_control: int,
    n_variant: int,
    conv_variant: int,
    prior_alpha: float = 1.0,
    prior_beta: float = 1.0,
    seed: int = 42,
) -> BayesianResult:
    """
    Bayesian A/B test analysis via Beta-Binomial model.

    Args:
        n_control:    Total users in control.
        conv_control: Conversions in control.
        n_variant:    Total users in variant.
        conv_variant: Conversions in variant.
        prior_alpha:  Beta prior alpha (default 1 = uniform).
        prior_beta:   Beta prior beta (default 1 = uniform).
        seed:         Random seed for reproducibility.

    Returns:
        BayesianResult with P(B>A), expected loss, credible intervals.
    """
    rng = np.random.default_rng(seed)

    # Posterior parameters (conjugate update: just add observed counts)
    a_c = prior_alpha + conv_control
    b_c = prior_beta  + (n_control - conv_control)
    a_v = prior_alpha + conv_variant
    b_v = prior_beta  + (n_variant - conv_variant)

    # Monte Carlo: draw from posteriors
    samples_control = rng.beta(a_c, b_c, size=N_SAMPLES)
    samples_variant = rng.beta(a_v, b_v, size=N_SAMPLES)

    diff = samples_variant - samples_control

    # P(B > A)
    prob_b_beats_a = float(np.mean(diff > 0))

    # Expected loss
    # If we ship B: regret = how much we lose when A is actually better
    loss_if_ship_b = float(np.mean(np.maximum(0, samples_control - samples_variant)))
    # If we keep A: opportunity cost = how much we miss when B is better
    loss_if_ship_a = float(np.mean(np.maximum(0, samples_variant - samples_control)))

    # 95% credible intervals (equal-tail)
    ci_c = (float(np.percentile(samples_control, 2.5)),
            float(np.percentile(samples_control, 97.5)))
    ci_v = (float(np.percentile(samples_variant, 2.5)),
            float(np.percentile(samples_variant, 97.5)))

    return BayesianResult(
        alpha_control=a_c,
        beta_control=b_c,
        alpha_variant=a_v,
        beta_variant=b_v,
        prob_b_beats_a=round(prob_b_beats_a, 4),
        expected_loss_if_ship_b=round(loss_if_ship_b, 6),
        expected_loss_if_ship_a=round(loss_if_ship_a, 6),
        ci_control=(round(ci_c[0], 4), round(ci_c[1], 4)),
        ci_variant=(round(ci_v[0], 4), round(ci_v[1], 4)),
        mean_control=round(a_c / (a_c + b_c), 6),
        mean_variant=round(a_v / (a_v + b_v), 6),
    )

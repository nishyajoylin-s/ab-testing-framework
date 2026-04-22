"""
Sample Size Calculator — Page 1.

Given: baseline conversion rate, MDE, power, significance level.
Output: minimum sample size per variant, estimated runtime, sensitivity charts.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from stats.sample_size import calculate, sensitivity_curve, power_curve
from ui import inject_css, page_header

# ── page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Sample Size Calculator", page_icon="📐", layout="wide")

inject_css()

DARK = dict(plot_bgcolor="#060A12", paper_bgcolor="#060A12", font_color="#EFF4FA",
            font=dict(family="Inter, sans-serif"))

page_header(
    1, "📐", "Sample Size Calculator",
    "Set your experiment parameters before collecting data. "
    "Committing to these numbers upfront is what separates a valid test from a fishing expedition."
)

# ── prefill from idea validator ───────────────────────────────────────────────
_default_baseline_pct = 5.0
_default_mde_pct      = 10.0

if st.session_state.get("prefill_source") == "idea_validator":
    _default_baseline_pct = round(st.session_state.get("prefill_baseline", 0.05) * 100, 1)
    _default_mde_pct      = round(st.session_state.get("prefill_mde", 0.10) * 100, 1)
    st.success(
        f"Pre-filled from your idea: baseline {_default_baseline_pct}%, MDE {_default_mde_pct}% relative. "
        "Adjust if needed."
    )
    # Clear so it doesn't persist on re-runs
    del st.session_state["prefill_source"]

# ── inputs ────────────────────────────────────────────────────────────────────
st.subheader("Experiment inputs")

col1, col2 = st.columns(2)

with col1:
    baseline_pct = st.slider(
        "Baseline conversion rate (%)",
        min_value=0.5, max_value=50.0, value=_default_baseline_pct, step=0.5,
        help="Your current conversion rate before the experiment. E.g. 5% = 5 out of 100 users convert.",
    )
    baseline = baseline_pct / 100

    mde_type = st.radio(
        "MDE type",
        ["Relative", "Absolute"],
        horizontal=True,
        help=(
            "**Relative:** '10% lift' means baseline goes from 5% → 5.5%.  \n"
            "**Absolute:** '1pp lift' means baseline goes from 5% → 6%.  \n"
            "Relative is more intuitive; absolute is what the math uses internally."
        ),
    )

    if mde_type == "Relative":
        mde_pct = st.slider(
            "Minimum Detectable Effect (relative, %)",
            min_value=1.0, max_value=50.0, value=_default_mde_pct, step=1.0,
            help="Smallest lift you care about detecting. Smaller = needs more samples.",
        )
        mde      = mde_pct / 100
        mde_kind = "relative"
    else:
        mde_pp = st.slider(
            "Minimum Detectable Effect (absolute, pp)",
            min_value=0.1, max_value=10.0, value=1.0, step=0.1,
            help="Smallest absolute change in conversion rate you care about.",
        )
        mde      = mde_pp / 100
        mde_kind = "absolute"

with col2:
    alpha_pct = st.select_slider(
        "Significance level α (%)",
        options=[1, 5, 10],
        value=5,
        help=(
            "Probability of a false positive (declaring a winner when there is none).  \n"
            "Industry standard: 5%. Use 1% for higher-stakes decisions."
        ),
    )
    alpha = alpha_pct / 100

    power_pct = st.select_slider(
        "Statistical power (%)",
        options=[70, 75, 80, 85, 90, 95],
        value=80,
        help=(
            "Probability of detecting a real effect if one exists.  \n"
            "80% is standard. 90% costs ~35% more samples but misses fewer real wins."
        ),
    )
    power = power_pct / 100

    tails = st.radio(
        "Test type",
        ["Two-sided (recommended)", "One-sided"],
        horizontal=True,
        help=(
            "**Two-sided:** detects both positive and negative effects. Almost always correct.  \n"
            "**One-sided:** only if you can genuinely pre-commit to never caring if B is worse."
        ),
    )
    n_tails = 1 if tails == "One-sided" else 2

    daily_traffic = st.number_input(
        "Daily visitors (optional, for runtime estimate)",
        min_value=0, value=0, step=100,
        help="Total daily visitors split across both variants. Leave 0 to skip.",
    )

if n_tails == 1:
    st.warning(
        "One-sided test selected. Only valid if you pre-committed before the experiment "
        "that you will only act on a positive result. If in doubt, use two-sided."
    )

# ── calculate ─────────────────────────────────────────────────────────────────
try:
    result = calculate(
        baseline_rate=baseline,
        mde=mde,
        mde_type=mde_kind,
        alpha=alpha,
        power=power,
        tails=n_tails,
        daily_traffic=daily_traffic if daily_traffic > 0 else None,
    )
    error = None
except ValueError as e:
    result = None
    error  = str(e)

st.divider()

# ── results ───────────────────────────────────────────────────────────────────
if error:
    st.error(f"Invalid inputs: {error}")
elif result:
    st.subheader("Results")

    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Sample size per variant", f"{result.n_per_variant:,}")
    r2.metric("Total sample size",       f"{result.n_total:,}")
    r3.metric("Control rate",            f"{result.control_rate:.2%}")
    r4.metric("Treatment rate (target)", f"{result.treatment_rate:.2%}")

    d1, d2, d3 = st.columns(3)
    d1.metric("Absolute MDE", f"+{result.absolute_mde:.2%}")
    d2.metric("Relative MDE", f"+{result.relative_mde:.1%}")
    if result.estimated_days:
        d3.metric("Estimated runtime", f"{result.estimated_days:.1f} days")
    else:
        d3.metric("Estimated runtime", "(enter daily traffic)")

    # ── explanation box ───────────────────────────────────────────────────────
    with st.expander("What does this mean? (plain English)"):
        st.markdown(f"""
You need **{result.n_per_variant:,} users per variant** ({result.n_total:,} total) to have:

- A **{power_pct}% chance** of detecting a real effect of at least **{result.absolute_mde:.2%}**
  ({result.relative_mde:.1%} relative lift) if it actually exists.
- Only a **{alpha_pct}% chance** of declaring a winner when there is none (false positive).

**The trade-off you made:**
- Asking to detect a smaller effect → needs more users.
- Wanting higher power → needs more users.
- Wanting stricter significance → needs more users.

**Z-scores used:** Z_α = {result.z_alpha}, Z_β = {result.z_beta}
*(These come from the normal distribution: Z_α cuts off the top {alpha_pct/n_tails}% of the distribution,
Z_β cuts off the bottom {100-power_pct}%.)*
        """)

    st.divider()

    # ── sensitivity charts ────────────────────────────────────────────────────
    st.subheader("Sensitivity analysis")
    st.caption("See how your sample size changes as you adjust your ambitions.")

    left, right = st.columns(2)

    # Chart 1: n vs MDE (how greedy are you about minimum effect?)
    with left:
        st.markdown("**How does MDE ambition affect sample size?**")
        if mde_kind == "relative":
            mde_range = np.linspace(0.03, 0.50, 30).tolist()
        else:
            max_abs = min(0.10, baseline * 0.9)
            mde_range = np.linspace(0.005, max_abs, 30).tolist()

        curve = sensitivity_curve(baseline, mde_range, mde_kind, alpha, power, n_tails)
        if curve:
            xs = [c["mde"] * (100 if mde_kind == "relative" else 100) for c in curve]
            ys = [c["n_per_variant"] for c in curve]

            fig1 = go.Figure(go.Scatter(x=xs, y=ys, mode="lines+markers",
                line=dict(color="#00C9B1", width=2), marker=dict(size=5, color="#00C9B1")))
            # Mark current selection
            current_x = mde * (100 if mde_kind == "relative" else 100)
            fig1.add_vline(x=current_x, line=dict(color="#e74c3c", dash="dash", width=1.5))
            fig1.add_annotation(x=current_x, y=max(ys) * 0.9,
                text=f"Your MDE<br>n={result.n_per_variant:,}", showarrow=False,
                font=dict(color="#e74c3c", size=11))
            unit = "%" if mde_kind == "relative" else "pp"
            fig1.update_layout(
                **DARK,
                margin=dict(l=0, r=0, t=10, b=0),
                height=280,
                xaxis_title=f"MDE ({unit})",
                yaxis_title="n per variant",
            )
            st.plotly_chart(fig1, use_container_width=True)
            st.caption(
                "Detecting smaller effects requires exponentially more samples. "
                "Be honest about the smallest lift that would actually change a business decision."
            )

    # Chart 2: n vs power (how sure do you want to be?)
    with right:
        st.markdown("**What does higher power cost you?**")
        p_curve = power_curve(baseline, mde, mde_kind, alpha, tails=n_tails)
        if p_curve:
            px_vals = [round(c["power"] * 100) for c in p_curve]
            py_vals = [c["n_per_variant"] for c in p_curve]

            fig2 = go.Figure(go.Bar(x=px_vals, y=py_vals, marker_color="#17becf"))
            fig2.add_hline(y=result.n_per_variant,
                line=dict(color="#e74c3c", dash="dash", width=1.5))
            fig2.add_annotation(x=px_vals[-1], y=result.n_per_variant * 1.05,
                text=f"Your setting ({power_pct}%)", showarrow=False,
                font=dict(color="#e74c3c", size=11))
            fig2.update_layout(
                **DARK,
                margin=dict(l=0, r=0, t=10, b=0),
                height=280,
                xaxis_title="Power (%)",
                yaxis_title="n per variant",
            )
            st.plotly_chart(fig2, use_container_width=True)

            n_80 = next((c["n_per_variant"] for c in p_curve if c["power"] == 0.80), None)
            n_90 = next((c["n_per_variant"] for c in p_curve if c["power"] == 0.90), None)
            if n_80 and n_90:
                extra_pct = round((n_90 - n_80) / n_80 * 100)
                st.caption(
                    f"Going from 80% → 90% power costs ~{extra_pct}% more samples. "
                    "Worth it for high-stakes launches; overkill for low-risk UI tweaks."
                )

    st.divider()

    # ── the math ──────────────────────────────────────────────────────────────
    with st.expander("Show the formula"):
        # Static LaTeX in a raw string (no .format — braces are LaTeX syntax)
        st.markdown(r"""
**Two-proportion z-test sample size formula:**

$$
n = \frac{(Z_{\alpha/2} + Z_{\beta})^2 \cdot [p_1(1-p_1) + p_2(1-p_2)]}{(p_1 - p_2)^2}
$$

Where:
- $p_1$ = baseline conversion rate (control)
- $p_2$ = expected treatment conversion rate
- $Z_{\alpha}$ = critical value for significance level (from standard normal)
- $Z_{\beta}$ = critical value for power (from standard normal)
        """)
        # Dynamic values in a separate f-string (no LaTeX braces to escape)
        p1 = result.control_rate
        p2 = result.treatment_rate
        st.markdown(f"""
**Your values plugged in:**

| Symbol | Value |
|--------|-------|
| $p_1$ (control) | {p1:.4f} |
| $p_2$ (treatment) | {p2:.4f} |
| $Z_{{\\alpha}}$ | {result.z_alpha} |
| $Z_{{\\beta}}$ | {result.z_beta} |
| **n per variant** | **{result.n_per_variant:,}** |

**Assumptions:**
1. Binary outcome (converted / not converted)
2. Independent observations
3. Large enough n for normal approximation to hold (n·p > 5 in each cell)
        """)

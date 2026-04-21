"""
Step 3: Results Interpreter.

PM enters their observed data → gets:
  1. SRM check         — was the randomisation broken?
  2. Frequentist       — p-value, confidence interval
  3. Bayesian          — P(B > A), expected loss
  4. LLM verdict       — plain-English recommendation any PM can act on

The MDE comparison is the most important business logic:
  statistically significant BUT below pre-committed MDE → DO NOT SHIP.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import plotly.graph_objects as go
import streamlit as st

import stats.frequentist as freq
import stats.bayesian    as bayes
from llm.verdict import VerdictInput, rule_verdict
from ui import inject_css, page_header

st.set_page_config(page_title="Results Interpreter", page_icon="📊", layout="wide")

inject_css()

DARK = dict(plot_bgcolor="#0b0f1a", paper_bgcolor="#0b0f1a", font_color="#c8d3e8",
            font=dict(family="sans-serif"))

page_header(
    2, "📊", "Results Interpreter",
    "Enter your observed results and get a full analysis — SRM check, frequentist, "
    "Bayesian, and a plain-English verdict that enforces your pre-committed MDE."
)


# ── inputs ────────────────────────────────────────────────────────────────────
st.subheader("Experiment details")

col_meta1, col_meta2 = st.columns(2)
with col_meta1:
    exp_name = st.text_input(
        "Experiment name",
        value="My Experiment",
        help="e.g. Checkout.PaymentPage.OneClickOption",
    )
with col_meta2:
    hypothesis = st.text_area(
        "Hypothesis",
        value="If we change X, then Y will improve because Z.",
        height=68,
        help="The original hypothesis you committed to before running the test.",
    )

st.divider()
st.subheader("Observed results")

c1, c2 = st.columns(2)

with c1:
    st.markdown("**Control (A)**")
    n_control   = st.number_input("Visitors",    min_value=1, value=10000, step=100, key="n_c")
    conv_control = st.number_input("Conversions", min_value=0, value=500,  step=10,  key="cv_c")

with c2:
    st.markdown("**Variant (B)**")
    n_variant   = st.number_input("Visitors",    min_value=1, value=10000, step=100, key="n_v")
    conv_variant = st.number_input("Conversions", min_value=0, value=540,  step=10,  key="cv_v")

st.divider()
st.subheader("Test settings (match what you set in Step 1)")

s1, s2, s3 = st.columns(3)
with s1:
    alpha_pct = st.select_slider("Significance level α", options=[1, 5, 10], value=5)
    alpha = alpha_pct / 100
with s2:
    tails = st.radio("Test type", ["Two-sided", "One-sided"], horizontal=True)
    n_tails = 2 if tails == "Two-sided" else 1
with s3:
    use_mde = st.checkbox("I set a pre-committed MDE", value=True,
                          help="If you defined an MDE before the test, enter it here. "
                               "This is the most important check: did the result meet your bar?")
    if use_mde:
        mde_type = st.radio("MDE type", ["Relative (%)", "Absolute (pp)"],
                            horizontal=True, key="mde_type_r")
        if mde_type == "Relative (%)":
            mde_rel_pct = st.number_input("MDE (%)", min_value=0.1, value=10.0, step=0.5)
            baseline    = conv_control / n_control
            mde_abs     = baseline * (mde_rel_pct / 100)
        else:
            mde_pp  = st.number_input("MDE (pp)", min_value=0.01, value=1.0, step=0.1)
            mde_abs = mde_pp / 100
    else:
        mde_abs = None

# ── validate inputs ───────────────────────────────────────────────────────────
input_error = None
if conv_control > n_control:
    input_error = "Control conversions cannot exceed control visitors."
if conv_variant > n_variant:
    input_error = "Variant conversions cannot exceed variant visitors."

if input_error:
    st.error(input_error)
    st.stop()

# ── run analysis ──────────────────────────────────────────────────────────────
srm   = freq.srm_check(n_control, n_variant)
f_res = freq.analyse(n_control, conv_control, n_variant, conv_variant,
                     alpha=alpha, tails=n_tails, mde_absolute=mde_abs)
b_res = bayes.analyse(n_control, conv_control, n_variant, conv_variant)

st.divider()

# ── 0. SRM CHECK — shown first, always ───────────────────────────────────────
st.subheader("0 · Sample Ratio Mismatch (SRM) Check")
st.caption("If your 50/50 split isn't actually 50/50, the randomisation is broken and all stats below are unreliable.")

srm_cols = st.columns(4)
srm_cols[0].metric("Control visitors", f"{srm.n_control:,}")
srm_cols[1].metric("Variant visitors",  f"{srm.n_variant:,}")
srm_cols[2].metric("Actual split",      f"{srm.actual_split:.1%} / {1 - srm.actual_split:.1%}")
srm_cols[3].metric("SRM p-value",       f"{srm.p_value:.4f}")

if srm.srm_detected:
    st.error(
        "🚨 **Sample Ratio Mismatch detected** (p < 0.01). "
        "The traffic split is not what you intended. "
        "This usually means a bug in the randomisation or tracking. "
        "**Do not interpret the results below. Fix the implementation first.**"
    )
else:
    st.success("✅ No SRM detected. Traffic split looks as expected.")

st.divider()

# ── 1. KEY NUMBERS ────────────────────────────────────────────────────────────
st.subheader("1 · What happened?")

k1, k2, k3, k4 = st.columns(4)
k1.metric("Control rate",  f"{f_res.rate_control:.2%}")
k2.metric("Variant rate",  f"{f_res.rate_variant:.2%}",
          delta=f"{f_res.absolute_lift:+.2%}")
k3.metric("Relative lift", f"{f_res.relative_lift:+.1%}")
k4.metric("95% CI",
          f"[{f_res.ci_lower:+.2%}, {f_res.ci_upper:+.2%}]")

# MDE check — most important business logic
if mde_abs is not None:
    mde_col1, mde_col2 = st.columns(2)
    with mde_col1:
        if f_res.mde_met:
            st.success(
                f"✅ **Observed lift ({f_res.absolute_lift:+.2%}) meets the pre-committed MDE "
                f"({mde_abs:+.2%})**. The effect is large enough to be worth shipping."
            )
        else:
            st.warning(
                f"⚠️ **Observed lift ({f_res.absolute_lift:+.2%}) is below the pre-committed MDE "
                f"({mde_abs:+.2%})**. Even if statistically significant, this may not be worth shipping."
            )

st.divider()

# ── 2. FREQUENTIST ────────────────────────────────────────────────────────────
st.subheader("2 · Frequentist analysis")
st.caption(
    "Answers: *'If there were no real difference, how surprising is this result?'*  "
    "Standard approach. Required when false positive rate has a legal or business meaning."
)

left, right = st.columns(2)

with left:
    f1, f2, f3 = st.columns(3)
    f1.metric("p-value",      f"{f_res.p_value:.4f}",
              delta=f"threshold: {alpha}", delta_color="off")
    f2.metric("z-statistic",  f"{f_res.z_stat:.3f}")
    f3.metric("Significant?", "YES ✅" if f_res.significant else "NO ❌")

    if f_res.significant:
        st.success(
            f"p = {f_res.p_value:.4f} < {alpha}. "
            "The result is statistically significant, unlikely to be random noise."
        )
    else:
        st.info(
            f"p = {f_res.p_value:.4f} ≥ {alpha}. "
            "Not statistically significant. We don't have enough evidence to "
            "conclude the variant is different from control."
        )

with right:
    # CI visualisation
    fig_ci = go.Figure()
    fig_ci.add_shape(type="line", x0=0, x1=0, y0=-0.5, y1=0.5,
                     line=dict(color="#555", dash="dash", width=1.5))
    color = "#2ecc71" if f_res.absolute_lift > 0 else "#e74c3c"
    fig_ci.add_trace(go.Scatter(
        x=[f_res.ci_lower, f_res.ci_upper],
        y=[0, 0],
        mode="lines",
        line=dict(color=color, width=4),
        name="95% CI",
    ))
    fig_ci.add_trace(go.Scatter(
        x=[f_res.absolute_lift],
        y=[0],
        mode="markers",
        marker=dict(size=14, color=color, symbol="diamond"),
        name="Observed lift",
    ))
    fig_ci.update_layout(
        **DARK,
        height=120,
        margin=dict(l=0, r=0, t=20, b=20),
        xaxis=dict(title="Absolute lift", tickformat=".1%", zeroline=False),
        yaxis=dict(visible=False),
        showlegend=False,
        title=dict(text="Confidence interval on lift", font=dict(size=12)),
    )
    st.plotly_chart(fig_ci, use_container_width=True)
    st.caption(
        "If the CI crosses zero, we cannot rule out that the variant has no effect "
        "(or even a negative effect)."
    )

st.divider()

# ── 3. BAYESIAN ───────────────────────────────────────────────────────────────
st.subheader("3 · Bayesian analysis")
st.caption(
    "Answers: *'Given this data, what is my belief about which variant is actually better?'*  "
    "Better for fast-moving product teams. Doesn't require a fixed sample size upfront."
)

b1, b2, b3 = st.columns(3)
b1.metric("P(Variant > Control)", f"{b_res.prob_b_beats_a:.1%}")
b2.metric("Expected loss if ship B",
          f"{b_res.expected_loss_if_ship_b * 100:.3f}pp",
          help="Average regret (in pp) if Variant B is actually worse")
b3.metric("Expected loss if keep A",
          f"{b_res.expected_loss_if_ship_a * 100:.3f}pp",
          help="Opportunity cost (in pp) of not shipping if B is actually better")

b_left, b_right = st.columns(2)

with b_left:
    # Posterior distribution plot
    x = np.linspace(
        min(b_res.ci_control[0], b_res.ci_variant[0]) * 0.98,
        max(b_res.ci_control[1], b_res.ci_variant[1]) * 1.02,
        500,
    )
    from scipy.stats import beta as beta_dist
    y_c = beta_dist.pdf(x, b_res.alpha_control, b_res.beta_control)
    y_v = beta_dist.pdf(x, b_res.alpha_variant, b_res.beta_variant)

    fig_post = go.Figure()
    fig_post.add_trace(go.Scatter(x=x, y=y_c, mode="lines", name="Control",
        fill="tozeroy", fillcolor="rgba(23,190,207,0.2)",
        line=dict(color="#17becf", width=2)))
    fig_post.add_trace(go.Scatter(x=x, y=y_v, mode="lines", name="Variant",
        fill="tozeroy", fillcolor="rgba(245,197,24,0.2)",
        line=dict(color="#f5c518", width=2)))
    fig_post.update_layout(
        **DARK, height=260, margin=dict(l=0, r=0, t=30, b=0),
        xaxis=dict(title="Conversion rate", tickformat=".1%"),
        yaxis=dict(title="Probability density"),
        title="Posterior distributions",
        legend=dict(orientation="h", y=1.15),
    )
    st.plotly_chart(fig_post, use_container_width=True)

with b_right:
    st.markdown("**How to read this:**")
    prob_pct = b_res.prob_b_beats_a * 100
    if prob_pct >= 95:
        interpretation = (
            f"Very strong evidence. There is a **{prob_pct:.1f}% probability** "
            "that Variant B is genuinely better. "
            "If you're a product team moving fast, this is a strong signal to ship."
        )
    elif prob_pct >= 80:
        interpretation = (
            f"Moderate evidence: **{prob_pct:.1f}% probability** that Variant B "
            "is better, but 1 in 5 chance we're wrong. "
            "Consider running longer for higher confidence."
        )
    elif prob_pct < 50:
        interpretation = (
            f"Variant B appears **worse** than control "
            f"({100 - prob_pct:.1f}% probability that A is better). Kill the experiment."
        )
    else:
        interpretation = (
            f"Weak evidence. Only **{prob_pct:.1f}% probability** "
            "that Variant B is better. Inconclusive. Don't ship."
        )
    st.info(interpretation)

    st.markdown("**When to use Bayesian vs Frequentist:**")
    st.markdown(
        "- **Frequentist**: when false positive rate has a defined business or legal meaning "
        "(finance, healthcare, regulated industries).\n"
        "- **Bayesian**: when you want to make decisions faster and can tolerate some "
        "uncertainty. Better for product teams iterating quickly.\n"
        "- **Show both**: they answer different questions. Use frequentist to *decide*, "
        "Bayesian to *understand*."
    )

st.divider()

# ── 4. VERDICT ────────────────────────────────────────────────────────────────
st.subheader("4 · Verdict")

verdict = rule_verdict(VerdictInput(
    experiment_name=exp_name,
    hypothesis=hypothesis,
    n_control=n_control,
    conv_control=conv_control,
    n_variant=n_variant,
    conv_variant=conv_variant,
    rate_control=f_res.rate_control,
    rate_variant=f_res.rate_variant,
    absolute_lift=f_res.absolute_lift,
    relative_lift=f_res.relative_lift,
    p_value=f_res.p_value,
    ci_lower=f_res.ci_lower,
    ci_upper=f_res.ci_upper,
    significant=f_res.significant,
    alpha=alpha,
    prob_b_beats_a=b_res.prob_b_beats_a,
    expected_loss_if_ship_b=b_res.expected_loss_if_ship_b,
    mde_absolute=mde_abs,
    mde_met=f_res.mde_met,
    srm_detected=srm.srm_detected,
))

_DECISION_STYLES = {
    "SHIP":        ("✅", "#10b981", "rgba(16,185,129,0.1)",  "rgba(16,185,129,0.25)"),
    "DO NOT SHIP": ("🚫", "#ef4444", "rgba(239,68,68,0.1)",   "rgba(239,68,68,0.25)"),
    "INCONCLUSIVE":("⚠️",  "#f59e0b", "rgba(245,158,11,0.1)",  "rgba(245,158,11,0.25)"),
    "INVALIDATE":  ("🚨", "#ef4444", "rgba(239,68,68,0.1)",   "rgba(239,68,68,0.25)"),
}
icon, color, bg, border_color = _DECISION_STYLES.get(
    verdict.decision, ("●", "#6b7fa3", "rgba(107,127,163,0.1)", "rgba(107,127,163,0.25)")
)

st.markdown(f"""
<div style="background:{bg};border:1px solid {border_color};border-radius:12px;
            padding:1.4rem 1.6rem;margin-bottom:1rem;">
    <div style="font-size:0.68rem;font-weight:700;letter-spacing:0.1em;
                text-transform:uppercase;color:{color};margin-bottom:0.5rem;">
        {icon} Decision
    </div>
    <div style="font-size:1.1rem;font-weight:700;color:#f1f5f9;line-height:1.4;">
        {verdict.decision} · {verdict.headline}
    </div>
</div>

<div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;">
    <div style="background:#131929;border:1px solid rgba(255,255,255,0.07);
                border-radius:10px;padding:1.25rem;">
        <div style="font-size:0.68rem;font-weight:700;letter-spacing:0.08em;
                    text-transform:uppercase;color:#6b7fa3;margin-bottom:0.6rem;">
            What happened
        </div>
        <div style="font-size:0.88rem;color:#c8d3e8;line-height:1.65;">
            {verdict.what_happened}
        </div>
    </div>
    <div style="background:#131929;border:1px solid rgba(255,255,255,0.07);
                border-radius:10px;padding:1.25rem;">
        <div style="font-size:0.68rem;font-weight:700;letter-spacing:0.08em;
                    text-transform:uppercase;color:#6b7fa3;margin-bottom:0.6rem;">
            Watch out for
        </div>
        <div style="font-size:0.88rem;color:#c8d3e8;line-height:1.65;">
            {verdict.watch_out_for}
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

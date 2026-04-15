"""
Step 0: Should I test this?

Before you design an experiment, answer one question: is an A/B test even the right tool?

A/B tests have real costs — traffic, time, engineering, opportunity cost of not shipping.
This page routes your idea to the right method:

  A/B TEST     — you have traffic, a clear metric, and need causal proof
  USER TEST    — hypothesis is unclear or UX intuition needs validation first
  FEATURE FLAG — ship and monitor, no split needed
  JUST SHIP    — no test needed at all

If the answer is A/B TEST, this page generates a Confluence-ready experiment brief.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
from llm.idea_validator import (
    IdeaInput, validate_idea, check_ollama_available, parse_route
)

st.set_page_config(
    page_title="Should I test this?",
    page_icon="💡",
    layout="wide",
)

# ── header ─────────────────────────────────────────────────────────────────────
st.title("💡 Should I test this?")
st.caption(
    "Before you run an A/B test, make sure you should. "
    "A/B tests cost time and traffic — this page routes your idea to the right method."
)

# ── Ollama status ──────────────────────────────────────────────────────────────
ollama_ok, ollama_msg = check_ollama_available()
if not ollama_ok:
    st.warning(
        f"LLM recommendation unavailable — {ollama_msg}. "
        "You can still use the routing checklist below."
    )

st.divider()

# ── Section 1: Describe the idea ──────────────────────────────────────────────
st.subheader("1 · What's the idea?")

col1, col2 = st.columns(2)

with col1:
    feature_description = st.text_area(
        "What are you changing?",
        placeholder="e.g. Move the checkout button above the fold on the product page.",
        height=100,
        help="Be specific — 'redesign checkout' is too vague, "
             "'move the CTA above the fold on mobile' is right.",
    )

with col2:
    problem_statement = st.text_area(
        "What problem does it solve?",
        placeholder="e.g. 70% of users who add to cart never complete checkout. "
                    "Eye-tracking shows most don't scroll far enough to see the button.",
        height=100,
        help="The problem is what you're measuring against — "
             "not what you hope the feature does.",
    )

primary_metric = st.text_input(
    "Primary success metric",
    placeholder="e.g. Checkout completion rate",
    help="One metric. The one number that, if it moves, means this worked. "
         "Secondary metrics go below.",
)

with st.expander("Optional: secondary metrics and target audience"):
    secondary_metrics = st.text_input(
        "Guardrail / secondary metrics",
        placeholder="e.g. Cart abandonment rate, Revenue per session, Page load time",
        help="Metrics we must NOT break. If primary wins but guardrails are violated, do not ship.",
    )
    target_audience = st.text_input(
        "Who sees this experiment?",
        placeholder="e.g. All logged-in users on mobile, New users only, UK market",
    )

st.divider()

# ── Section 2: Routing checklist ───────────────────────────────────────────────
st.subheader("2 · Quick routing check")
st.caption(
    "Answer honestly — this shapes the recommendation. "
    "If you're not sure, that's a signal too."
)

q1, q2 = st.columns(2)
q3, q4 = st.columns(2)

with q1:
    needs_statistical_proof = st.toggle(
        "Stakeholders need statistical proof before we ship",
        value=False,
        help="If a director, legal, or a data review board needs to see a p-value "
             "before approving the rollout — toggle this on.",
    )

with q2:
    primarily_ux_change = st.toggle(
        "This is primarily a UX or visual change",
        value=False,
        help="Redesigns, layout changes, copy changes. "
             "These often need user testing first — can users even find what they need?",
    )

with q3:
    tracking_exists = st.toggle(
        "We can measure the primary metric with existing tracking",
        value=True,
        help="If you'd need to add new events or instrumentation to measure this, "
             "toggle off. That's an engineering dependency before the experiment can start.",
    )

with q4:
    enough_traffic = st.toggle(
        "We have enough traffic to detect a realistic effect",
        value=True,
        help="Rough check: a few thousand daily active users on the affected surface is "
             "usually enough for a 5-10% effect. Very low traffic = very long experiment.",
    )

st.divider()

# ── Section 3: LLM recommendation ────────────────────────────────────────────
st.subheader("3 · Get a recommendation")

# Validate minimum inputs
missing = []
if not feature_description.strip():
    missing.append("what you're changing")
if not problem_statement.strip():
    missing.append("the problem it solves")
if not primary_metric.strip():
    missing.append("the primary success metric")

if missing:
    st.info(f"Fill in: {', '.join(missing)} — then click the button below.")
    st.stop()

if not ollama_ok:
    st.warning(f"LLM unavailable: {ollama_msg}")
else:
    if st.button("Analyse this idea", type="primary", use_container_width=False):
        idea = IdeaInput(
            feature_description=feature_description.strip(),
            problem_statement=problem_statement.strip(),
            primary_metric=primary_metric.strip(),
            needs_statistical_proof=needs_statistical_proof,
            primarily_ux_change=primarily_ux_change,
            tracking_exists=tracking_exists,
            enough_traffic=enough_traffic,
            secondary_metrics=secondary_metrics.strip(),
            target_audience=target_audience.strip(),
        )

        with st.spinner("Thinking... (~10-20s)"):
            result_text, err = validate_idea(idea)

        if err:
            st.error(f"LLM error: {err}")
            st.stop()

        # ── Parse and render ──────────────────────────────────────────────────
        route = parse_route(result_text)

        # Route badge
        route_colors = {
            "A/B TEST":     ("success", "🧪 A/B TEST"),
            "USER TEST":    ("warning", "🎯 USER TEST FIRST"),
            "FEATURE FLAG": ("info",    "🚩 FEATURE FLAG"),
            "JUST SHIP":    ("info",    "🚀 JUST SHIP IT"),
        }

        if route and route in route_colors:
            badge_type, badge_label = route_colors[route]
            getattr(st, badge_type)(f"**Recommendation: {badge_label}**")
        else:
            st.info("**Recommendation generated below.**")

        st.markdown("---")

        # Parse sections and render with styling
        sections = {
            "ROUTE":             None,
            "RATIONALE":         None,
            "HYPOTHESIS":        None,
            "EXPERIMENT BRIEF":  None,
            "PM NOTES":          None,
            "DESIGNER NOTES":    None,
            "ENGINEER NOTES":    None,
        }

        current_section = None
        buffer = []

        for line in result_text.split("\n"):
            stripped = line.strip()
            matched = False
            for key in sections:
                if stripped.upper().startswith(key + ":"):
                    if current_section and buffer:
                        sections[current_section] = "\n".join(buffer).strip()
                    current_section = key
                    rest = stripped[len(key) + 1:].strip()
                    buffer = [rest] if rest else []
                    matched = True
                    break
            if not matched and current_section:
                buffer.append(line)

        if current_section and buffer:
            sections[current_section] = "\n".join(buffer).strip()

        # Render each section
        if sections["RATIONALE"] and sections["RATIONALE"] != "N/A":
            st.markdown(f"**Why:** {sections['RATIONALE']}")

        if route == "A/B TEST":
            if sections["HYPOTHESIS"] and sections["HYPOTHESIS"] != "N/A":
                st.info(f"**Hypothesis:** {sections['HYPOTHESIS']}")

            if sections["EXPERIMENT BRIEF"] and sections["EXPERIMENT BRIEF"] != "N/A":
                st.markdown("### Experiment brief")
                st.markdown(sections["EXPERIMENT BRIEF"])

        col_pm, col_design, col_eng = st.columns(3)

        with col_pm:
            st.markdown("#### PM")
            if sections["PM NOTES"] and sections["PM NOTES"] != "N/A":
                st.markdown(sections["PM NOTES"])

        with col_design:
            st.markdown("#### Designer")
            if sections["DESIGNER NOTES"] and sections["DESIGNER NOTES"] != "N/A":
                st.markdown(sections["DESIGNER NOTES"])

        with col_eng:
            st.markdown("#### Engineer")
            if sections["ENGINEER NOTES"] and sections["ENGINEER NOTES"] != "N/A":
                st.markdown(sections["ENGINEER NOTES"])

        # ── Section 4: Carry forward to Sample Size ───────────────────────────
        if route == "A/B TEST":
            st.markdown("---")
            st.markdown("### Next step")

            next_col1, next_col2, next_col3 = st.columns([2, 1, 3])

            with next_col1:
                baseline_rate = st.number_input(
                    "Current conversion rate (%)",
                    min_value=0.1,
                    max_value=99.9,
                    value=5.0,
                    step=0.5,
                    help="Your current rate for the primary metric. "
                         "Check your analytics for the last 30 days.",
                )

            with next_col2:
                mde_pct = st.number_input(
                    "MDE (%)",
                    min_value=1.0,
                    max_value=50.0,
                    value=10.0,
                    step=1.0,
                    help="Minimum relative lift worth shipping. "
                         "If 10%: control 5% → you need to see at least 5.5%.",
                )

            with next_col3:
                st.markdown("")
                st.markdown("")
                if st.button("→ Go to Sample Size Calculator", type="secondary"):
                    st.session_state["prefill_baseline"] = baseline_rate / 100
                    st.session_state["prefill_mde"]      = mde_pct / 100
                    st.session_state["prefill_source"]   = "idea_validator"
                    st.switch_page("pages/1_Sample_Size.py")

        # Raw output in expander
        with st.expander("Copy raw text"):
            st.code(result_text)

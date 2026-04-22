import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st

from ui import inject_css, page_header
from utils.supabase_client import get_client, load_experiments, update_experiment
from utils.doc_generator import generate_results_doc

st.set_page_config(page_title="Results Doc", page_icon="📝", layout="wide")
inject_css()

page_header(
    None, "📝", "Results Doc",
    "Document your experiment results after the test ends. Generate a shareable one-pager and update the registry."
)

client = get_client()
experiments = load_experiments(client)

if client is None:
    st.warning("Supabase not configured — results will not update the registry.")

# ── Link to existing experiment or start fresh ────────────────────────────────
st.subheader("1 · Link to experiment")

exp_names = [e["name"] for e in experiments] if experiments else []
use_existing = st.toggle("Load from registry", value=bool(exp_names))

selected_exp = None
if use_existing and exp_names:
    chosen = st.selectbox("Select experiment", exp_names)
    selected_exp = next((e for e in experiments if e["name"] == chosen), None)
    exp_id = selected_exp.get("id") if selected_exp else None
else:
    exp_id = None

# Pre-fill from selected experiment
def _get(field, fallback=""):
    if selected_exp:
        return selected_exp.get(field) or fallback
    return fallback

st.divider()
st.subheader("2 · Experiment details")

c1, c2 = st.columns(2)
with c1:
    name = st.text_input("Experiment name", value=_get("name"))
    owner = st.text_input("Owner", value=_get("owner"))
    primary_metric = st.text_input("Primary metric", value=_get("primary_metric"))
with c2:
    start_date = st.text_input("Start date", value=_get("start_date"))
    end_date = st.text_input("End date", value=_get("end_date"))
    test_type = st.radio("Test type", ["Two-sided", "One-sided"], horizontal=True)

st.divider()
st.subheader("3 · Observed results")

r1, r2, r3, r4 = st.columns(4)
with r1:
    control_rate = st.text_input("Control rate", placeholder="e.g. 5.2%")
with r2:
    variant_rate = st.text_input("Variant rate", placeholder="e.g. 5.8%")
with r3:
    absolute_lift = st.text_input("Absolute lift", placeholder="e.g. +0.6pp")
with r4:
    significant = st.selectbox("Statistically significant?", ["Yes", "No"])

s1, s2, s3 = st.columns(3)
with s1:
    p_value = st.text_input("p-value", placeholder="e.g. 0.032")
with s2:
    mde = st.text_input("Pre-committed MDE", placeholder="e.g. 1.0pp")
with s3:
    mde_met = st.selectbox("MDE met?", ["Yes", "No"])

st.divider()
st.subheader("4 · Decision & learnings")

decision = st.selectbox("Decision", ["SHIP", "DO NOT SHIP", "INCONCLUSIVE", "STOPPED"])
summary = st.text_area("Summary (1–2 sentences)", height=70, placeholder="Plain-English summary of what happened.")
decision_rationale = st.text_area("Decision rationale", height=80, placeholder="Why you made this call, referencing MDE and p-value.")

c5, c6 = st.columns(2)
with c5:
    learnings = st.text_area("Learnings", height=100, placeholder="What you learned about user behaviour.")
with c6:
    next_steps = st.text_area("Next steps", height=100, placeholder="Follow-up experiments, monitoring plan.")

st.divider()

# ── Actions ───────────────────────────────────────────────────────────────────
ready = bool(name.strip() and primary_metric.strip())

if not ready:
    st.info("Fill in experiment name and primary metric to generate the results doc.")

col_gen, col_save, _ = st.columns([2, 2, 4])

with col_gen:
    gen_clicked = st.button("Generate results doc", type="primary", disabled=not ready, use_container_width=True)
with col_save:
    save_clicked = st.button(
        "Update registry", type="secondary",
        disabled=not ready or client is None or exp_id is None,
        use_container_width=True,
        help="Only available when an experiment is loaded from the registry."
    )

if gen_clicked or save_clicked:
    record = dict(
        name=name.strip(),
        owner=owner.strip(),
        primary_metric=primary_metric.strip(),
        start_date=start_date.strip(),
        end_date=end_date.strip(),
        test_type=test_type,
        control_rate=control_rate.strip(),
        variant_rate=variant_rate.strip(),
        absolute_lift=absolute_lift.strip(),
        significant=significant,
        p_value=p_value.strip(),
        mde=mde.strip(),
        mde_met=mde_met,
        decision=decision,
        summary=summary.strip(),
        decision_rationale=decision_rationale.strip(),
        learnings=learnings.strip(),
        next_steps=next_steps.strip(),
    )

    if save_clicked and exp_id:
        updates = {
            "result": decision.lower().replace(" ", "_"),
            "decision": decision,
            "control_rate": control_rate,
            "variant_rate": variant_rate,
            "absolute_lift": absolute_lift,
            "p_value": p_value,
            "learnings": learnings,
            "next_steps": next_steps,
            "status": "completed",
            "end_date": end_date,
        }
        ok, msg = update_experiment(client, exp_id, updates)
        if ok:
            st.success("Registry updated.")
        else:
            st.error(f"Update failed: {msg}")

    doc = generate_results_doc(record)

    st.divider()
    st.subheader("Your results doc")

    with st.expander("Preview", expanded=True):
        st.markdown(doc)

    st.download_button(
        label="Download as Markdown",
        data=doc,
        file_name=f"results_{name.strip().lower().replace(' ', '_')}.md",
        mime="text/markdown",
    )

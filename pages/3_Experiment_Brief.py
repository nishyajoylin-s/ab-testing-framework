import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
from datetime import date

from ui import inject_css, page_header
from utils.supabase_client import get_client, save_experiment
from utils.doc_generator import generate_brief

st.set_page_config(page_title="Experiment Brief", page_icon="📋", layout="wide")
inject_css()

page_header(
    None, "📋", "Experiment Brief",
    "Document your experiment before launch. Fill in the details and generate a shareable one-pager."
)

client = get_client()
if client is None:
    st.warning("Supabase not configured — brief will not be saved to the registry. Add SUPABASE_URL and SUPABASE_KEY to your secrets.")

st.subheader("1 · Experiment details")

col1, col2 = st.columns(2)
with col1:
    name = st.text_input("Experiment name", placeholder="e.g. Checkout.PaymentPage.OneClickOption")
    owner = st.text_input("Owner", placeholder="Your name or team")
    status = st.selectbox("Status", ["Planned", "Running", "Completed", "Stopped"])

with col2:
    start_date = st.date_input("Start date", value=date.today())
    end_date = st.date_input("Expected end date")

st.divider()
st.subheader("2 · Hypothesis & variants")

hypothesis = st.text_area(
    "Hypothesis",
    placeholder="If we [change X], then [metric Y] will [increase/decrease] by [Z%] because [reason].",
    height=80,
)

c1, c2 = st.columns(2)
with c1:
    control_description = st.text_area("Control (A) — what users currently see", height=80)
with c2:
    variant_description = st.text_area("Variant (B) — what changes", height=80)

st.divider()
st.subheader("3 · Metrics & sizing")

c3, c4 = st.columns(2)
with c3:
    primary_metric = st.text_input("Primary metric", placeholder="e.g. Checkout conversion rate")
    secondary_metrics = st.text_input("Secondary metrics (comma-separated)", placeholder="e.g. AOV, bounce rate")
with c4:
    sample_size = st.number_input(
        "Required sample size per variant",
        min_value=0, value=0, step=100,
        help="Copy from Step 1 — Sample Size Calculator."
    )

st.divider()
st.subheader("4 · Risks & notes")

c5, c6 = st.columns(2)
with c5:
    risks = st.text_area("Risks & assumptions", height=100, placeholder="- Assumes tracking is live\n- Excludes mobile users")
with c6:
    notes = st.text_area("Additional notes", height=100, placeholder="Stakeholders, related experiments, constraints…")

st.divider()

# ── Actions ──────────────────────────────────────────────────────────────────
ready = bool(name.strip() and hypothesis.strip() and primary_metric.strip())

if not ready:
    st.info("Fill in experiment name, hypothesis, and primary metric to generate the brief.")

col_gen, col_save, _ = st.columns([2, 2, 4])

with col_gen:
    gen_clicked = st.button("Generate one-pager", type="primary", disabled=not ready, use_container_width=True)

with col_save:
    save_clicked = st.button("Save to registry", type="secondary", disabled=not ready or client is None, use_container_width=True)

if gen_clicked or save_clicked:
    record = dict(
        name=name.strip(),
        owner=owner.strip(),
        status=status.lower(),
        start_date=str(start_date),
        end_date=str(end_date),
        hypothesis=hypothesis.strip(),
        control_description=control_description.strip(),
        variant_description=variant_description.strip(),
        primary_metric=primary_metric.strip(),
        secondary_metrics=secondary_metrics.strip(),
        sample_size_per_variant=int(sample_size) if sample_size else None,
        risks=risks.strip(),
        notes=notes.strip(),
    )

    if save_clicked:
        ok, msg = save_experiment(client, record)
        if ok:
            st.success("Saved to registry.")
        else:
            st.error(f"Save failed: {msg}")

    doc = generate_brief(record)

    st.divider()
    st.subheader("Your experiment brief")

    with st.expander("Preview", expanded=True):
        st.markdown(doc)

    st.download_button(
        label="Download as Markdown",
        data=doc,
        file_name=f"brief_{name.strip().lower().replace(' ', '_')}.md",
        mime="text/markdown",
    )

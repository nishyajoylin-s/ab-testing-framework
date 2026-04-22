import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
from datetime import date

from ui import inject_css, page_header
from utils.supabase_client import get_client, load_experiments, save_experiment, update_experiment, delete_experiment
from utils.doc_generator import generate_brief, generate_results_doc, BRIEF_TEMPLATE, RESULTS_TEMPLATE

st.set_page_config(page_title="Workspace", page_icon="🗂️", layout="wide")
inject_css()

page_header(
    None, "🗂️", "Workspace",
    "Experiment briefs, results docs, templates, and your experiment registry — all in one place."
)

client = get_client()

if client is None:
    st.warning("Supabase not configured — registry changes won't persist. Add SUPABASE_URL and SUPABASE_KEY to your secrets.")

tab_brief, tab_results, tab_templates, tab_registry = st.tabs([
    "📋 Experiment Brief",
    "📝 Results Doc",
    "📄 Templates",
    "🗂 Registry",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — EXPERIMENT BRIEF
# ══════════════════════════════════════════════════════════════════════════════
with tab_brief:
    st.markdown("Document your experiment **before launch**. Generate a shareable one-pager and save to the registry.")
    st.divider()

    c1, c2 = st.columns(2)
    with c1:
        b_name   = st.text_input("Experiment name", placeholder="e.g. Checkout.PaymentPage.OneClickOption", key="b_name")
        b_owner  = st.text_input("Owner", placeholder="Your name or team", key="b_owner")
        b_status = st.selectbox("Status", ["Planned", "Running"], key="b_status")
    with c2:
        b_start = st.date_input("Start date", value=date.today(), key="b_start")
        b_end   = st.date_input("Expected end date", key="b_end")

    b_hypothesis = st.text_area(
        "Hypothesis",
        placeholder="If we [change X], then [metric Y] will [increase/decrease] by [Z%] because [reason].",
        height=80, key="b_hyp"
    )

    bc1, bc2 = st.columns(2)
    with bc1:
        b_control = st.text_area("Control (A) — current experience", height=80, key="b_ctrl")
    with bc2:
        b_variant = st.text_area("Variant (B) — what changes", height=80, key="b_var")

    bc3, bc4 = st.columns(2)
    with bc3:
        b_primary   = st.text_input("Primary metric", placeholder="e.g. Checkout conversion rate", key="b_pm")
        b_secondary = st.text_input("Secondary metrics", placeholder="e.g. AOV, bounce rate", key="b_sm")
    with bc4:
        b_sample = st.number_input("Sample size per variant", min_value=0, value=0, step=100, key="b_ss")

    bc5, bc6 = st.columns(2)
    with bc5:
        b_risks = st.text_area("Risks & assumptions", height=90, placeholder="- Assumes tracking is live\n- Excludes mobile users", key="b_risk")
    with bc6:
        b_notes = st.text_area("Additional notes", height=90, key="b_notes")

    st.divider()
    b_ready = bool(b_name.strip() and b_hypothesis.strip() and b_primary.strip())
    if not b_ready:
        st.info("Fill in experiment name, hypothesis, and primary metric to continue.")

    ba1, ba2, _ = st.columns([2, 2, 4])
    with ba1:
        b_gen  = st.button("Generate one-pager", type="primary",  disabled=not b_ready, use_container_width=True, key="b_gen")
    with ba2:
        b_save = st.button("Save to registry",   type="secondary", disabled=not b_ready or client is None, use_container_width=True, key="b_save")

    if b_gen or b_save:
        b_record = dict(
            name=b_name.strip(), owner=b_owner.strip(), status=b_status.lower(),
            start_date=str(b_start), end_date=str(b_end),
            hypothesis=b_hypothesis.strip(),
            control_description=b_control.strip(), variant_description=b_variant.strip(),
            primary_metric=b_primary.strip(), secondary_metrics=b_secondary.strip(),
            sample_size_per_variant=int(b_sample) if b_sample else None,
            risks=b_risks.strip(), notes=b_notes.strip(),
        )
        if b_save:
            ok, msg = save_experiment(client, b_record)
            st.success("Saved to registry.") if ok else st.error(f"Save failed: {msg}")

        doc = generate_brief(b_record)
        st.divider()
        with st.expander("Preview", expanded=True):
            st.markdown(doc)
        st.download_button("Download as Markdown", data=doc,
            file_name=f"brief_{b_name.strip().lower().replace(' ','_')}.md", mime="text/markdown", key="b_dl")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — RESULTS DOC
# ══════════════════════════════════════════════════════════════════════════════
with tab_results:
    st.markdown("Document your experiment **after it ends**. Generate a results one-pager and update the registry.")
    st.divider()

    experiments = load_experiments(client)
    exp_names   = [e["name"] for e in experiments] if experiments else []

    use_existing = st.toggle("Load from registry", value=bool(exp_names), key="r_toggle")
    selected_exp = None
    exp_id       = None

    if use_existing and exp_names:
        chosen       = st.selectbox("Select experiment", exp_names, key="r_select")
        selected_exp = next((e for e in experiments if e["name"] == chosen), None)
        exp_id       = selected_exp.get("id") if selected_exp else None

    def _get(field, fallback=""):
        return (selected_exp.get(field) or fallback) if selected_exp else fallback

    rc1, rc2 = st.columns(2)
    with rc1:
        r_name   = st.text_input("Experiment name", value=_get("name"), key="r_name")
        r_owner  = st.text_input("Owner",           value=_get("owner"), key="r_owner")
        r_pm     = st.text_input("Primary metric",  value=_get("primary_metric"), key="r_pm")
    with rc2:
        r_start  = st.text_input("Start date", value=_get("start_date"), key="r_start")
        r_end    = st.text_input("End date",   value=_get("end_date"),   key="r_end")
        r_ttype  = st.radio("Test type", ["Two-sided", "One-sided"], horizontal=True, key="r_tt")

    rr1, rr2, rr3, rr4 = st.columns(4)
    with rr1: r_ctrl_rate = st.text_input("Control rate",  placeholder="5.2%", key="r_cr")
    with rr2: r_var_rate  = st.text_input("Variant rate",  placeholder="5.8%", key="r_vr")
    with rr3: r_lift      = st.text_input("Absolute lift", placeholder="+0.6pp", key="r_lift")
    with rr4: r_sig       = st.selectbox("Significant?", ["Yes", "No"], key="r_sig")

    rs1, rs2, rs3 = st.columns(3)
    with rs1: r_pval    = st.text_input("p-value", placeholder="0.032", key="r_pval")
    with rs2: r_mde     = st.text_input("Pre-committed MDE", placeholder="1.0pp", key="r_mde")
    with rs3: r_mde_met = st.selectbox("MDE met?", ["Yes", "No"], key="r_mdemet")

    r_decision  = st.selectbox("Decision", ["SHIP", "DO NOT SHIP", "INCONCLUSIVE", "STOPPED"], key="r_dec")
    r_summary   = st.text_area("Summary", height=70, key="r_sum")
    r_rationale = st.text_area("Decision rationale", height=80, key="r_rat")

    rd1, rd2 = st.columns(2)
    with rd1: r_learnings  = st.text_area("Learnings",   height=90, key="r_learn")
    with rd2: r_next_steps = st.text_area("Next steps",  height=90, key="r_next")

    st.divider()
    r_ready = bool(r_name.strip() and r_pm.strip())
    if not r_ready:
        st.info("Fill in experiment name and primary metric to continue.")

    ra1, ra2, _ = st.columns([2, 2, 4])
    with ra1:
        r_gen  = st.button("Generate results doc", type="primary",  disabled=not r_ready, use_container_width=True, key="r_gen")
    with ra2:
        r_save = st.button("Update registry",      type="secondary", disabled=not r_ready or client is None or exp_id is None, use_container_width=True, key="r_save")

    if r_gen or r_save:
        r_record = dict(
            name=r_name.strip(), owner=r_owner.strip(), primary_metric=r_pm.strip(),
            start_date=r_start.strip(), end_date=r_end.strip(), test_type=r_ttype,
            control_rate=r_ctrl_rate.strip(), variant_rate=r_var_rate.strip(),
            absolute_lift=r_lift.strip(), significant=r_sig,
            p_value=r_pval.strip(), mde=r_mde.strip(), mde_met=r_mde_met,
            decision=r_decision, summary=r_summary.strip(),
            decision_rationale=r_rationale.strip(),
            learnings=r_learnings.strip(), next_steps=r_next_steps.strip(),
        )
        if r_save and exp_id:
            ok, msg = update_experiment(client, exp_id, {
                "status": "completed", "decision": r_decision,
                "result": r_decision.lower().replace(" ", "_"),
                "control_rate": r_ctrl_rate, "variant_rate": r_var_rate,
                "absolute_lift": r_lift, "p_value": r_pval,
                "learnings": r_learnings, "next_steps": r_next_steps,
                "end_date": r_end,
            })
            st.success("Registry updated.") if ok else st.error(f"Update failed: {msg}")

        doc = generate_results_doc(r_record)
        st.divider()
        with st.expander("Preview", expanded=True):
            st.markdown(doc)
        st.download_button("Download as Markdown", data=doc,
            file_name=f"results_{r_name.strip().lower().replace(' ','_')}.md", mime="text/markdown", key="r_dl")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — TEMPLATES
# ══════════════════════════════════════════════════════════════════════════════
with tab_templates:
    st.markdown("Blank templates to copy into Notion, Confluence, or Google Docs.")
    st.divider()

    tt1, tt2 = st.tabs(["Experiment Brief", "Results Doc"])

    with tt1:
        st.code(BRIEF_TEMPLATE, language="markdown")
        st.download_button("Download", data=BRIEF_TEMPLATE,
            file_name="experiment_brief_template.md", mime="text/markdown", key="t_brief_dl")

    with tt2:
        st.code(RESULTS_TEMPLATE, language="markdown")
        st.download_button("Download", data=RESULTS_TEMPLATE,
            file_name="results_doc_template.md", mime="text/markdown", key="t_results_dl")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — REGISTRY
# ══════════════════════════════════════════════════════════════════════════════
with tab_registry:
    if "registry" not in st.session_state:
        st.session_state.registry = load_experiments(client)

    STATUS_COLORS = {
        "planned":   ("🔵", "rgba(59,130,246,0.12)",  "rgba(59,130,246,0.3)"),
        "running":   ("🟢", "rgba(34,197,94,0.12)",   "rgba(34,197,94,0.3)"),
        "completed": ("⚪", "rgba(139,156,176,0.12)", "rgba(139,156,176,0.3)"),
        "stopped":   ("🔴", "rgba(239,68,68,0.12)",   "rgba(239,68,68,0.3)"),
    }
    DECISION_COLORS = {
        "SHIP": "#22C55E", "DO NOT SHIP": "#EF4444",
        "INCONCLUSIVE": "#F59E0B", "STOPPED": "#8B9CB0",
    }

    rg1, rg2, rg3, rg4 = st.columns([3, 2, 2, 2])
    with rg1:
        reg_search = st.text_input("Search", placeholder="Filter by name, owner…", label_visibility="collapsed", key="reg_search")
    with rg2:
        reg_status = st.selectbox("Status", ["All","Planned","Running","Completed","Stopped"], label_visibility="collapsed", key="reg_status")
    with rg3:
        if st.button("↻ Refresh", use_container_width=True, disabled=client is None, key="reg_refresh"):
            st.session_state.registry = load_experiments(client)
            st.rerun()
    with rg4:
        csv_upload = st.file_uploader("Import CSV", type="csv", label_visibility="collapsed", key="reg_csv")

    if csv_upload:
        try:
            imported = pd.read_csv(csv_upload).to_dict("records")
            if client:
                for row in imported:
                    row.pop("id", None); row.pop("created_at", None)
                    save_experiment(client, row)
                st.session_state.registry = load_experiments(client)
            else:
                st.session_state.registry = imported
            st.success(f"Imported {len(imported)} experiments.")
            st.rerun()
        except Exception as e:
            st.error(f"Import failed: {e}")

    all_rows = st.session_state.registry or []
    rows = all_rows

    if reg_search:
        q = reg_search.lower()
        rows = [r for r in rows if any(q in str(r.get(c,"")).lower() for c in ["name","owner","primary_metric"])]
    if reg_status != "All":
        rows = [r for r in rows if r.get("status","").lower() == reg_status.lower()]

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Total",     len(all_rows))
    m2.metric("Running",   sum(1 for r in all_rows if r.get("status") == "running"))
    m3.metric("Completed", sum(1 for r in all_rows if r.get("status") == "completed"))
    m4.metric("Wins",      sum(1 for r in all_rows if r.get("decision") == "SHIP"))
    m5.metric("No-ships",  sum(1 for r in all_rows if r.get("decision") == "DO NOT SHIP"))

    st.divider()

    if not rows:
        st.info("No experiments yet. Create one in the **Experiment Brief** tab or import a CSV.")
    else:
        for exp in rows:
            status = exp.get("status", "planned").lower()
            icon, bg, border = STATUS_COLORS.get(status, ("⚪", "rgba(139,156,176,0.12)", "rgba(139,156,176,0.3)"))
            decision  = exp.get("decision") or "—"
            dec_color = DECISION_COLORS.get(decision, "#8B9CB0")

            st.markdown(f"""
<div style="background:{bg};border:1px solid {border};border-radius:12px;
            padding:1rem 1.25rem;margin-bottom:0.75rem;">
    <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:0.5rem;">
        <div>
            <span style="font-size:0.95rem;font-weight:700;color:#EFF4FA;">{icon} {exp.get('name','—')}</span>
            <span style="font-size:0.78rem;color:#8B9CB0;margin-left:0.75rem;">{exp.get('owner','—')}</span>
        </div>
        <div style="display:flex;gap:0.5rem;align-items:center;flex-wrap:wrap;">
            <span style="font-size:0.72rem;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;color:#8B9CB0;">{exp.get('primary_metric','—')}</span>
            <span style="font-size:0.72rem;font-weight:700;color:{dec_color};background:rgba(0,0,0,0.2);border-radius:4px;padding:2px 8px;">{decision}</span>
            <span style="font-size:0.72rem;color:#4A6070;">{exp.get('start_date','—')} → {exp.get('end_date','—')}</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

            with st.expander("Details / Edit", key=f"exp_{exp.get('id', exp.get('name',''))}"):
                ex1, ex2, ex3 = st.columns(3)
                with ex1:
                    new_status = st.selectbox("Status",
                        ["planned","running","completed","stopped"],
                        index=["planned","running","completed","stopped"].index(status) if status in ["planned","running","completed","stopped"] else 0,
                        key=f"st_{exp.get('id','')}")
                with ex2:
                    opts = ["—","SHIP","DO NOT SHIP","INCONCLUSIVE","STOPPED"]
                    new_decision = st.selectbox("Decision", opts,
                        index=opts.index(decision) if decision in opts else 0,
                        key=f"dc_{exp.get('id','')}")
                with ex3:
                    new_notes = st.text_input("Notes", value=exp.get("notes","") or "", key=f"nt_{exp.get('id','')}")

                eu1, eu2 = st.columns(2)
                with eu1:
                    if st.button("Update", key=f"upd_{exp.get('id','')}", use_container_width=True, disabled=client is None):
                        ok, msg = update_experiment(client, exp["id"], {
                            "status": new_status,
                            "decision": new_decision if new_decision != "—" else None,
                            "notes": new_notes,
                        })
                        if ok:
                            st.session_state.registry = load_experiments(client)
                            st.rerun()
                        else:
                            st.error(msg)
                with eu2:
                    if st.button("Delete", key=f"del_{exp.get('id','')}", use_container_width=True, disabled=client is None):
                        ok, msg = delete_experiment(client, exp["id"])
                        if ok:
                            st.session_state.registry = load_experiments(client)
                            st.rerun()
                        else:
                            st.error(msg)

    st.divider()
    if all_rows:
        df  = pd.DataFrame(all_rows)
        csv = df.to_csv(index=False).encode()
        st.download_button("Export all as CSV", data=csv,
            file_name=f"registry_{date.today()}.csv", mime="text/csv", key="reg_export")

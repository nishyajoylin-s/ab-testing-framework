import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
import io
from datetime import date

from ui import inject_css, page_header
from utils.supabase_client import get_client, load_experiments, save_experiment, delete_experiment, update_experiment

st.set_page_config(page_title="Registry", page_icon="🗂️", layout="wide")
inject_css()

page_header(
    None, "🗂️", "Experiment Registry",
    "Track all experiments in one place. Sync with Supabase or import/export via CSV."
)

client = get_client()

# ── Session state ─────────────────────────────────────────────────────────────
if "registry" not in st.session_state:
    st.session_state.registry = load_experiments(client)

COLUMNS = [
    "name", "owner", "status", "primary_metric",
    "start_date", "end_date", "decision", "result", "notes",
]

STATUS_COLORS = {
    "planned":   ("🔵", "rgba(59,130,246,0.12)",  "rgba(59,130,246,0.3)"),
    "running":   ("🟢", "rgba(34,197,94,0.12)",   "rgba(34,197,94,0.3)"),
    "completed": ("⚪", "rgba(139,156,176,0.12)", "rgba(139,156,176,0.3)"),
    "stopped":   ("🔴", "rgba(239,68,68,0.12)",   "rgba(239,68,68,0.3)"),
}

DECISION_COLORS = {
    "SHIP":        "#22C55E",
    "DO NOT SHIP": "#EF4444",
    "INCONCLUSIVE":"#F59E0B",
    "STOPPED":     "#8B9CB0",
}

# ── Controls row ──────────────────────────────────────────────────────────────
ctrl1, ctrl2, ctrl3, ctrl4 = st.columns([3, 2, 2, 2])

with ctrl1:
    search = st.text_input("Search", placeholder="Filter by name, owner, metric…", label_visibility="collapsed")

with ctrl2:
    status_filter = st.selectbox("Status", ["All", "Planned", "Running", "Completed", "Stopped"], label_visibility="collapsed")

with ctrl3:
    if st.button("↻ Refresh from Supabase", use_container_width=True, disabled=client is None):
        st.session_state.registry = load_experiments(client)
        st.rerun()

with ctrl4:
    csv_upload = st.file_uploader("Import CSV", type="csv", label_visibility="collapsed")

if csv_upload:
    try:
        imported = pd.read_csv(csv_upload).to_dict("records")
        if client:
            for row in imported:
                row.pop("id", None)
                row.pop("created_at", None)
                save_experiment(client, row)
            st.session_state.registry = load_experiments(client)
        else:
            st.session_state.registry = imported
        st.success(f"Imported {len(imported)} experiments.")
        st.rerun()
    except Exception as e:
        st.error(f"Import failed: {e}")

# ── Filter ────────────────────────────────────────────────────────────────────
rows = st.session_state.registry or []

if search:
    q = search.lower()
    rows = [r for r in rows if any(q in str(r.get(c, "")).lower() for c in ["name", "owner", "primary_metric"])]

if status_filter != "All":
    rows = [r for r in rows if r.get("status", "").lower() == status_filter.lower()]

# ── Stats summary ─────────────────────────────────────────────────────────────
all_rows = st.session_state.registry or []
s1, s2, s3, s4, s5 = st.columns(5)
s1.metric("Total", len(all_rows))
s2.metric("Running",   sum(1 for r in all_rows if r.get("status") == "running"))
s3.metric("Completed", sum(1 for r in all_rows if r.get("status") == "completed"))
s4.metric("Wins",      sum(1 for r in all_rows if r.get("decision") == "SHIP"))
s5.metric("No-ships",  sum(1 for r in all_rows if r.get("decision") == "DO NOT SHIP"))

st.divider()

# ── Table ─────────────────────────────────────────────────────────────────────
if not rows:
    st.info("No experiments yet. Create one in **Experiment Brief** or import a CSV.")
else:
    for exp in rows:
        status = exp.get("status", "planned").lower()
        icon, bg, border = STATUS_COLORS.get(status, ("⚪", "rgba(139,156,176,0.12)", "rgba(139,156,176,0.3)"))
        decision = exp.get("decision") or "—"
        dec_color = DECISION_COLORS.get(decision, "#8B9CB0")

        with st.container():
            st.markdown(f"""
<div style="background:{bg};border:1px solid {border};border-radius:12px;
            padding:1rem 1.25rem;margin-bottom:0.75rem;">
    <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:0.5rem;">
        <div>
            <span style="font-size:0.95rem;font-weight:700;color:#EFF4FA;">{icon} {exp.get('name','—')}</span>
            <span style="font-size:0.78rem;color:#8B9CB0;margin-left:0.75rem;">{exp.get('owner','—')}</span>
        </div>
        <div style="display:flex;gap:0.5rem;align-items:center;flex-wrap:wrap;">
            <span style="font-size:0.72rem;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;
                         color:#8B9CB0;">{exp.get('primary_metric','—')}</span>
            <span style="font-size:0.72rem;font-weight:700;color:{dec_color};
                         background:rgba(0,0,0,0.2);border-radius:4px;padding:2px 8px;">{decision}</span>
            <span style="font-size:0.72rem;color:#4A6070;">
                {exp.get('start_date','—')} → {exp.get('end_date','—')}
            </span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

            with st.expander("Details / Edit"):
                ec1, ec2, ec3 = st.columns(3)
                with ec1:
                    new_status = st.selectbox(
                        "Status", ["planned", "running", "completed", "stopped"],
                        index=["planned","running","completed","stopped"].index(status) if status in ["planned","running","completed","stopped"] else 0,
                        key=f"status_{exp.get('id',exp.get('name',''))}"
                    )
                with ec2:
                    new_decision = st.selectbox(
                        "Decision", ["—", "SHIP", "DO NOT SHIP", "INCONCLUSIVE", "STOPPED"],
                        index=["—","SHIP","DO NOT SHIP","INCONCLUSIVE","STOPPED"].index(decision) if decision in ["—","SHIP","DO NOT SHIP","INCONCLUSIVE","STOPPED"] else 0,
                        key=f"decision_{exp.get('id',exp.get('name',''))}"
                    )
                with ec3:
                    new_notes = st.text_input("Notes", value=exp.get("notes","") or "", key=f"notes_{exp.get('id',exp.get('name',''))}")

                ua, da = st.columns([1, 1])
                with ua:
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
                with da:
                    if st.button("Delete", key=f"del_{exp.get('id','')}", use_container_width=True, disabled=client is None):
                        ok, msg = delete_experiment(client, exp["id"])
                        if ok:
                            st.session_state.registry = load_experiments(client)
                            st.rerun()
                        else:
                            st.error(msg)

# ── CSV export ────────────────────────────────────────────────────────────────
st.divider()
if all_rows:
    df = pd.DataFrame(all_rows)
    csv_bytes = df.to_csv(index=False).encode()
    st.download_button(
        "Export all as CSV",
        data=csv_bytes,
        file_name=f"experiment_registry_{date.today()}.csv",
        mime="text/csv",
    )

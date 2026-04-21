"""
Shared UI utilities — CSS injection and HTML components.
Import and call inject_css() as the first thing after st.set_page_config().
"""
import streamlit as st

_CSS = """<style>

/* ── Chrome ────────────────────────────────────────────── */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
.stDeployButton { display: none !important; }

/* ── Layout ────────────────────────────────────────────── */
.block-container {
    padding-top: 1.75rem !important;
    padding-bottom: 4rem !important;
    max-width: 1200px !important;
}

/* ── Sidebar ───────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: #0b0f1a !important;
    border-right: 1px solid rgba(255,255,255,0.05) !important;
}
[data-testid="stSidebarNavItems"] a {
    border-radius: 8px !important;
    margin: 2px 0 !important;
    padding: 0.45rem 0.75rem !important;
    transition: background 0.15s !important;
}
[data-testid="stSidebarNavItems"] a:hover {
    background: rgba(245,197,24,0.08) !important;
}
[data-testid="stSidebarNavItems"] [aria-current="page"] {
    background: rgba(245,197,24,0.12) !important;
    color: #f5c518 !important;
    font-weight: 600 !important;
}

/* ── Metric cards ──────────────────────────────────────── */
[data-testid="stMetric"] {
    background: #131929 !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 10px !important;
    padding: 1rem 1.25rem !important;
    transition: border-color 0.2s !important;
}
[data-testid="stMetric"]:hover {
    border-color: rgba(245,197,24,0.2) !important;
}
[data-testid="stMetricLabel"] > div {
    color: #6b7fa3 !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.07em !important;
    text-transform: uppercase !important;
}
[data-testid="stMetricValue"] {
    font-size: 1.5rem !important;
    font-weight: 700 !important;
    color: #f1f5f9 !important;
}
[data-testid="stMetricDelta"] {
    font-size: 0.82rem !important;
}

/* ── Buttons ───────────────────────────────────────────── */
.stButton > button[kind="primary"] {
    background: #f5c518 !important;
    color: #0a0e1a !important;
    border: none !important;
    font-weight: 700 !important;
    border-radius: 8px !important;
    padding: 0.5rem 1.75rem !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.01em !important;
    transition: all 0.18s ease !important;
}
.stButton > button[kind="primary"]:hover {
    background: #ffd740 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 16px rgba(245,197,24,0.25) !important;
}
.stButton > button[kind="secondary"] {
    border-color: rgba(255,255,255,0.1) !important;
    border-radius: 8px !important;
    transition: all 0.18s ease !important;
}
.stButton > button[kind="secondary"]:hover {
    border-color: rgba(245,197,24,0.4) !important;
    color: #f5c518 !important;
}

/* ── Alerts ────────────────────────────────────────────── */
[data-testid="stAlert"] {
    border-radius: 8px !important;
    border-left-width: 3px !important;
}

/* ── Expander ──────────────────────────────────────────── */
[data-testid="stExpander"] {
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 10px !important;
    overflow: hidden !important;
}
[data-testid="stExpander"]:hover {
    border-color: rgba(255,255,255,0.12) !important;
}

/* ── Inputs ────────────────────────────────────────────── */
[data-testid="stNumberInput"] input,
[data-testid="stTextInput"] input {
    border-radius: 7px !important;
    border-color: rgba(255,255,255,0.1) !important;
    background: #131929 !important;
    transition: border-color 0.15s !important;
}
[data-testid="stNumberInput"] input:focus,
[data-testid="stTextInput"] input:focus {
    border-color: rgba(245,197,24,0.4) !important;
    box-shadow: 0 0 0 1px rgba(245,197,24,0.15) !important;
}
[data-testid="stTextArea"] textarea {
    border-radius: 7px !important;
    border-color: rgba(255,255,255,0.1) !important;
    background: #131929 !important;
}
[data-testid="stTextArea"] textarea:focus {
    border-color: rgba(245,197,24,0.4) !important;
}

/* ── Select / Slider ───────────────────────────────────── */
[data-testid="stSelectSlider"] > div > div {
    border-radius: 7px !important;
}

/* ── Divider ───────────────────────────────────────────── */
hr {
    border: none !important;
    border-top: 1px solid rgba(255,255,255,0.06) !important;
    margin: 1.5rem 0 !important;
}

/* ── Charts ────────────────────────────────────────────── */
[data-testid="stPlotlyChart"] {
    border-radius: 10px;
    overflow: hidden;
}

/* ── Scrollbar ─────────────────────────────────────────── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #2a3550; border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: #3d4f6e; }

/* ── Typography ────────────────────────────────────────── */
h2 { font-weight: 700 !important; color: #f1f5f9 !important; }
h3 { font-weight: 600 !important; color: #e2e8f0 !important; }

/* ── Step progress component ───────────────────────────── */
.step-progress {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-bottom: 1.75rem;
    flex-wrap: wrap;
}
.step-pill {
    border-radius: 6px;
    padding: 4px 12px;
    font-size: 0.75rem;
    font-weight: 500;
    letter-spacing: 0.02em;
    white-space: nowrap;
    border: 1px solid;
    transition: all 0.15s;
}
.step-pill-active {
    background: #f5c518;
    color: #0a0e1a;
    border-color: #f5c518;
    font-weight: 700;
}
.step-pill-done {
    background: rgba(245,197,24,0.08);
    color: #a89030;
    border-color: rgba(245,197,24,0.2);
}
.step-pill-muted {
    background: transparent;
    color: #2a3550;
    border-color: #1a2540;
}
.step-arrow {
    color: #1e2d4a;
    font-size: 0.85rem;
    user-select: none;
}

/* ── Verdict card ──────────────────────────────────────── */
.verdict-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
    margin-top: 1rem;
}
.verdict-block {
    background: #131929;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 10px;
    padding: 1.25rem;
}
.verdict-block-label {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #6b7fa3;
    margin-bottom: 0.6rem;
}
.verdict-block-text {
    font-size: 0.9rem;
    color: #c8d3e8;
    line-height: 1.65;
}

</style>"""


def inject_css():
    st.markdown(_CSS, unsafe_allow_html=True)


def step_indicator(current: int):
    steps = [
        {"n": 0, "label": "Step 0 · Validate"},
        {"n": 1, "label": "Step 1 · Size"},
        {"n": None, "label": "Run test"},
        {"n": 2, "label": "Step 2 · Interpret"},
    ]
    pills = []
    for i, s in enumerate(steps):
        if s["n"] == current:
            cls = "step-pill step-pill-active"
        elif s["n"] is None:
            cls = "step-pill step-pill-muted"
        else:
            cls = "step-pill step-pill-done"
        pills.append(f'<div class="{cls}">{s["label"]}</div>')
        if i < len(steps) - 1:
            pills.append('<div class="step-arrow">›</div>')

    html = '<div class="step-progress">' + "".join(pills) + "</div>"
    st.markdown(html, unsafe_allow_html=True)


def page_header(step: int, icon: str, title: str, subtitle: str):
    step_indicator(step)
    st.markdown(
        f'<h1 style="font-size:1.9rem;font-weight:800;color:#f1f5f9;'
        f'margin:0 0 0.4rem 0;line-height:1.2;">{icon} {title}</h1>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<p style="color:#6b7fa3;font-size:0.95rem;margin:0 0 1.75rem 0;'
        f'line-height:1.6;">{subtitle}</p>',
        unsafe_allow_html=True,
    )

"""
Shared UI utilities — CSS injection and HTML components.
Import and call inject_css() as the first thing after st.set_page_config().
"""
import streamlit as st

_CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

/* ── Chrome ────────────────────────────────────────────── */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
.stDeployButton { display: none !important; }

/* ── Global base ───────────────────────────────────────── */
.stApp {
    background: #060A12 !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

/* ── Layout ────────────────────────────────────────────── */
.block-container {
    padding-top: 4.5rem !important;
    padding-bottom: 4rem !important;
    max-width: 1200px !important;
}

/* ── Sidebar ───────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.04) !important;
    backdrop-filter: blur(16px) !important;
    -webkit-backdrop-filter: blur(16px) !important;
    border-right: 1px solid rgba(255,255,255,0.09) !important;
}
[data-testid="stSidebarNavItems"] a {
    border-radius: 10px !important;
    margin: 2px 0 !important;
    padding: 0.45rem 0.75rem !important;
    transition: background 0.2s !important;
    color: #8B9CB0 !important;
}
[data-testid="stSidebarNavItems"] a:hover {
    background: rgba(0,201,177,0.08) !important;
    color: #EFF4FA !important;
}
[data-testid="stSidebarNavItems"] [aria-current="page"] {
    background: rgba(0,201,177,0.12) !important;
    color: #00C9B1 !important;
    font-weight: 600 !important;
}

/* ── Metric cards ──────────────────────────────────────── */
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.04) !important;
    backdrop-filter: blur(16px) !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    border-radius: 16px !important;
    padding: 1rem 1.25rem !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
[data-testid="stMetric"]:hover {
    border-color: rgba(0,201,177,0.35) !important;
    box-shadow: 0 0 28px rgba(0,201,177,0.12) !important;
}
[data-testid="stMetricLabel"] > div {
    color: #8B9CB0 !important;
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
}
[data-testid="stMetricValue"] {
    font-size: 1.5rem !important;
    font-weight: 800 !important;
    color: #EFF4FA !important;
}
[data-testid="stMetricDelta"] {
    font-size: 0.82rem !important;
}

/* ── Buttons ───────────────────────────────────────────── */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #00C9B1, #00AAFF) !important;
    color: #060A12 !important;
    border: none !important;
    font-weight: 700 !important;
    border-radius: 10px !important;
    padding: 0.5rem 1.75rem !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.01em !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 0 20px rgba(0,201,177,0.2) !important;
}
.stButton > button[kind="primary"]:hover {
    box-shadow: 0 0 28px rgba(0,201,177,0.35) !important;
    transform: translateY(-1px) !important;
}
.stButton > button[kind="secondary"] {
    background: rgba(255,255,255,0.07) !important;
    border-color: rgba(255,255,255,0.09) !important;
    border-radius: 10px !important;
    color: #EFF4FA !important;
    transition: all 0.2s ease !important;
}
.stButton > button[kind="secondary"]:hover {
    background: rgba(255,255,255,0.10) !important;
    border-color: rgba(0,201,177,0.35) !important;
    color: #00C9B1 !important;
}

/* ── Alerts ────────────────────────────────────────────── */
[data-testid="stAlert"] {
    border-radius: 10px !important;
    border-left-width: 3px !important;
    backdrop-filter: blur(8px) !important;
}

/* ── Expander ──────────────────────────────────────────── */
[data-testid="stExpander"] {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    border-radius: 10px !important;
    overflow: hidden !important;
}
[data-testid="stExpander"]:hover {
    border-color: rgba(0,201,177,0.25) !important;
}

/* ── Inputs ────────────────────────────────────────────── */
[data-testid="stNumberInput"] input,
[data-testid="stTextInput"] input {
    border-radius: 10px !important;
    border-color: rgba(255,255,255,0.09) !important;
    background: rgba(255,255,255,0.04) !important;
    color: #EFF4FA !important;
    transition: border-color 0.2s !important;
}
[data-testid="stNumberInput"] input:focus,
[data-testid="stTextInput"] input:focus {
    border-color: #00C9B1 !important;
    box-shadow: 0 0 0 3px rgba(0,201,177,0.12) !important;
}
[data-testid="stTextArea"] textarea {
    border-radius: 10px !important;
    border-color: rgba(255,255,255,0.09) !important;
    background: rgba(255,255,255,0.04) !important;
    color: #EFF4FA !important;
}
[data-testid="stTextArea"] textarea:focus {
    border-color: #00C9B1 !important;
    box-shadow: 0 0 0 3px rgba(0,201,177,0.12) !important;
}

/* ── Select / Slider ───────────────────────────────────── */
[data-testid="stSelectSlider"] > div > div {
    border-radius: 10px !important;
}

/* ── Divider ───────────────────────────────────────────── */
hr {
    border: none !important;
    border-top: 1px solid rgba(255,255,255,0.09) !important;
    margin: 1.5rem 0 !important;
}

/* ── Equal-height columns ──────────────────────────────── */
[data-testid="stHorizontalBlock"] {
    align-items: stretch !important;
}
[data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
    display: flex !important;
    flex-direction: column !important;
}
[data-testid="stHorizontalBlock"] > [data-testid="stColumn"] > div:first-child {
    flex: 1 !important;
    display: flex !important;
    flex-direction: column !important;
}

/* ── Charts ────────────────────────────────────────────── */
[data-testid="stPlotlyChart"] {
    border-radius: 16px;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,0.09);
}

/* ── Scrollbar ─────────────────────────────────────────── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.08); border-radius: 9999px; }
::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.14); }

/* ── Typography ────────────────────────────────────────── */
h2 { font-weight: 700 !important; color: #EFF4FA !important; }
h3 { font-weight: 600 !important; color: #EFF4FA !important; }

/* ── Step progress component ───────────────────────────── */
.step-progress {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-bottom: 1.75rem;
    flex-wrap: wrap;
}
.step-pill {
    border-radius: 9999px;
    padding: 4px 14px;
    font-size: 0.75rem;
    font-weight: 500;
    letter-spacing: 0.02em;
    white-space: nowrap;
    border: 1px solid;
    transition: all 0.2s;
    backdrop-filter: blur(8px);
}
.step-pill-active {
    background: linear-gradient(135deg, #00C9B1, #00AAFF);
    color: #060A12;
    border-color: transparent;
    font-weight: 700;
    box-shadow: 0 0 16px rgba(0,201,177,0.3);
}
.step-pill-done {
    background: rgba(0,201,177,0.08);
    color: #00C9B1;
    border-color: rgba(0,201,177,0.2);
}
.step-pill-muted {
    background: transparent;
    color: #4A6070;
    border-color: rgba(255,255,255,0.09);
}
.step-arrow {
    color: #4A6070;
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
    background: rgba(255,255,255,0.04);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 16px;
    padding: 1.25rem;
}
.verdict-block-label {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #8B9CB0;
    margin-bottom: 0.6rem;
}
.verdict-block-text {
    font-size: 0.9rem;
    color: #EFF4FA;
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
        f'<h1 style="font-size:1.9rem;font-weight:800;color:#EFF4FA;'
        f'margin:0 0 0.4rem 0;line-height:1.2;letter-spacing:-0.025em;">{icon} {title}</h1>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<p style="color:#8B9CB0;font-size:0.95rem;margin:0 0 1.75rem 0;'
        f'line-height:1.6;">{subtitle}</p>',
        unsafe_allow_html=True,
    )

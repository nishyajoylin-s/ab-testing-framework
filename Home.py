import streamlit as st
from ui import inject_css

st.set_page_config(
    page_title="A/B Testing Framework",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()

# ── Sidebar branding ──────────────────────────────────────────────────────────
st.sidebar.markdown(
    '<div style="padding:0.5rem 0 1.5rem 0;">'
    '<div style="font-size:0.7rem;font-weight:700;letter-spacing:0.12em;'
    'color:#00C9B1;text-transform:uppercase;margin-bottom:0.3rem;">A/B Testing</div>'
    '<div style="font-size:1rem;font-weight:700;color:#EFF4FA;">Framework</div>'
    '</div>',
    unsafe_allow_html=True,
)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding: 0.5rem 0 2.5rem 0;">
    <div style="font-size:0.7rem;font-weight:700;letter-spacing:0.14em;
                color:#00C9B1;text-transform:uppercase;margin-bottom:1rem;">
        Experiment Design Tool
    </div>
    <h1 style="font-size:3rem;font-weight:900;line-height:1.12;letter-spacing:-0.025em;
               background:linear-gradient(135deg,#00C9B1,#00AAFF);
               -webkit-background-clip:text;-webkit-text-fill-color:transparent;
               background-clip:text;margin:0 0 1.1rem 0;">
        Stop guessing.<br>Start testing right.
    </h1>
    <p style="font-size:1.05rem;color:#8B9CB0;max-width:540px;
              line-height:1.75;margin:0;">
        The only A/B testing tool that starts before your first user is assigned
        to a variant. Guided, opinionated, and built around how experiments
        actually fail.
    </p>
</div>
""", unsafe_allow_html=True)

# ── Step cards ────────────────────────────────────────────────────────────────
CARD = (
    'background:rgba(255,255,255,0.04);'
    'backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);'
    'border:1px solid rgba(255,255,255,0.09);'
    'border-radius:16px;padding:1.6rem;height:100%;min-height:260px;'
    'position:relative;isolation:isolate;'
)
STEP_LABEL = (
    'font-size:0.68rem;font-weight:700;letter-spacing:0.1em;'
    'color:#00C9B1;text-transform:uppercase;margin-bottom:0.85rem;'
)
CARD_ICON  = 'font-size:1.6rem;margin-bottom:0.75rem;'
CARD_TITLE = 'font-size:1.05rem;font-weight:700;color:#EFF4FA;margin-bottom:0.5rem;'
CARD_DESC  = 'font-size:0.87rem;color:#8B9CB0;line-height:1.65;'

c0, c1, mid, c2 = st.columns([3, 3, 1, 3])

with c0:
    st.markdown(f"""
    <div style="{CARD}">
        <div style="{STEP_LABEL}">Step 0</div>
        <div style="{CARD_ICON}">💡</div>
        <div style="{CARD_TITLE}">Should I test this?</div>
        <div style="{CARD_DESC}">
            Route your idea to the right method — A/B test, user test,
            feature flag, or just ship. If testing is right, generates
            a full experiment brief for PM, Designer, and Engineer.
        </div>
    </div>
    """, unsafe_allow_html=True)

with c1:
    st.markdown(f"""
    <div style="{CARD}">
        <div style="{STEP_LABEL}">Step 1</div>
        <div style="{CARD_ICON}">📐</div>
        <div style="{CARD_TITLE}">How many users do I need?</div>
        <div style="{CARD_DESC}">
            Power analysis that forces you to commit to your hypothesis
            before collecting data. Sensitivity curves show the cost of
            every assumption you make.
        </div>
    </div>
    """, unsafe_allow_html=True)

with mid:
    st.markdown(
        '<div style="display:flex;align-items:center;justify-content:center;'
        'height:100%;color:#4A6070;font-size:1.5rem;padding-top:2rem;">›</div>',
        unsafe_allow_html=True,
    )

with c2:
    st.markdown(f"""
    <div style="{CARD}">
        <div style="{STEP_LABEL}">Step 2</div>
        <div style="{CARD_ICON}">📊</div>
        <div style="{CARD_TITLE}">What do the results mean?</div>
        <div style="{CARD_DESC}">
            SRM check, frequentist analysis, Bayesian analysis, and a
            plain-English verdict — all in one view. Enforces the
            pre-committed MDE as the actual business gate.
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)

# ── CTA ───────────────────────────────────────────────────────────────────────
_, cta_col, _ = st.columns([1, 2, 1])
with cta_col:
    st.info("**Start with Step 0** in the sidebar — it takes 2 minutes and prevents the most expensive A/B test mistakes.")

# ── Divider ───────────────────────────────────────────────────────────────────
st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
st.divider()

# ── Why this approach ─────────────────────────────────────────────────────────
st.markdown(
    '<h3 style="font-size:1.1rem;font-weight:700;color:#EFF4FA;margin-bottom:1.5rem;">'
    'Why most A/B tests fail before the data is collected</h3>',
    unsafe_allow_html=True,
)

f1, f2, f3, f4 = st.columns(4)

FAIL_CARD = (
    'background:rgba(255,255,255,0.04);backdrop-filter:blur(16px);'
    '-webkit-backdrop-filter:blur(16px);'
    'border:1px solid rgba(255,255,255,0.09);'
    'border-radius:16px;padding:1.1rem 1.25rem;min-height:100px;'
)
FAIL_NUM  = (
    'font-size:1.4rem;font-weight:900;margin-bottom:0.4rem;letter-spacing:-0.03em;'
    'background:linear-gradient(135deg,#00C9B1,#00AAFF);'
    '-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;'
)
FAIL_TEXT = 'font-size:0.84rem;color:#8B9CB0;line-height:1.6;'

with f1:
    st.markdown(f"""
    <div style="{FAIL_CARD}">
        <div style="{FAIL_NUM}">01</div>
        <div style="{FAIL_TEXT}">Testing before you have a clear, falsifiable hypothesis</div>
    </div>""", unsafe_allow_html=True)

with f2:
    st.markdown(f"""
    <div style="{FAIL_CARD}">
        <div style="{FAIL_NUM}">02</div>
        <div style="{FAIL_TEXT}">Running too small to detect a realistic effect</div>
    </div>""", unsafe_allow_html=True)

with f3:
    st.markdown(f"""
    <div style="{FAIL_CARD}">
        <div style="{FAIL_NUM}">03</div>
        <div style="{FAIL_TEXT}">Stopping early when results "look good" (peeking)</div>
    </div>""", unsafe_allow_html=True)

with f4:
    st.markdown(f"""
    <div style="{FAIL_CARD}">
        <div style="{FAIL_NUM}">04</div>
        <div style="{FAIL_TEXT}">Shipping a significant-but-below-MDE result as a win</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

# ── Quote ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="border-left:3px solid #00C9B1;padding:0.75rem 1.5rem;
            margin:1.5rem 0;background:rgba(0,201,177,0.04);border-radius:0 10px 10px 0;">
    <div style="font-size:1rem;color:#EFF4FA;font-style:italic;line-height:1.7;">
        "If you torture the data long enough, it will confess to anything."
    </div>
    <div style="font-size:0.78rem;color:#4A6070;margin-top:0.4rem;font-weight:600;">
        — Ronald Coase
    </div>
</div>
""", unsafe_allow_html=True)

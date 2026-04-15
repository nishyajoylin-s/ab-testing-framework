"""
A/B Testing Framework — home page.
"""
import streamlit as st

st.set_page_config(
    page_title="A/B Testing Framework",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🧪 A/B Testing Framework")
st.caption(
    "The tool that prevents bad experiments — not just analyses them. "
    "Every other tool starts after you've collected the data. This one starts before."
)

st.markdown("""
---

### How it works

Most A/B test mistakes happen before a single user is assigned to a variant.
This framework covers the full lifecycle:

| Step | Module | What it answers |
|------|--------|-----------------|
| **0** | **Should I test this?** | Is an A/B test even the right tool? Or user testing? Or just ship it? |
| **1** | **Sample Size Calculator** | How many users do I need before I can trust my results? |
| *test runs* | — | *(nothing in the tool — go run your experiment)* |
| **2** | **Results Interpreter** | Is this significant? Should I ship? What does it mean? |

---

### Start here → Step 0

If you have a feature idea but aren't sure whether to test it:
navigate to **"Should I test this?"** in the sidebar.

It takes 2 minutes, routes your idea to the right method,
and — if A/B testing is correct — generates a Confluence-ready experiment brief.

---

### The philosophy

> "If you torture the data long enough, it will confess to anything." — Ronald Coase

The most common A/B test mistakes aren't statistical — they're upstream:
- Testing before you have a clear hypothesis
- Running a test that's too small to detect a realistic effect
- Stopping early when results "look good"
- Misreading a statistically significant but practically meaningless lift

This framework catches each of these at the right moment.
""")

st.info("Start with **Step 0: Should I test this?** in the sidebar.")

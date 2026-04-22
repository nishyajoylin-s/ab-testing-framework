import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st

from ui import inject_css, page_header
from utils.doc_generator import BRIEF_TEMPLATE, RESULTS_TEMPLATE

st.set_page_config(page_title="Templates", page_icon="📄", layout="wide")
inject_css()

page_header(
    None, "📄", "Templates",
    "Blank templates for experiment briefs and results docs. Copy into Notion, Confluence, or Google Docs."
)

t1, t2 = st.tabs(["Experiment Brief", "Results Doc"])

with t1:
    st.markdown(
        "Use this before launching an experiment. Fill in each section and share with PM, Designer, and Engineer."
    )
    st.code(BRIEF_TEMPLATE, language="markdown")
    st.download_button(
        "Download brief template",
        data=BRIEF_TEMPLATE,
        file_name="experiment_brief_template.md",
        mime="text/markdown",
    )

with t2:
    st.markdown(
        "Use this after the experiment ends. Document results, decision, and learnings for the team."
    )
    st.code(RESULTS_TEMPLATE, language="markdown")
    st.download_button(
        "Download results template",
        data=RESULTS_TEMPLATE,
        file_name="results_doc_template.md",
        mime="text/markdown",
    )

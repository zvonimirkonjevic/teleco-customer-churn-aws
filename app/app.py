"""
Telco Customer Churn Prediction — Streamlit Application

Entry point that wires together UI components and the API client.
Run with:  streamlit run app/app.py
"""

import streamlit as st

from components import (
    inject_styles,
    render_form,
    render_header,
    render_results,
    render_sidebar,
)
from config import PAGE_TITLE, PAGE_LAYOUT, SIDEBAR_STATE
from predict import make_prediction, PredictionError

# ── Page config (must be the first Streamlit command) ──────────────────────
st.set_page_config(
    page_title=PAGE_TITLE,
    layout=PAGE_LAYOUT,
    initial_sidebar_state=SIDEBAR_STATE,
)

# ── Layout ─────────────────────────────────────────────────────────────────
inject_styles()
render_header()

payload = render_form()

if payload is not None:
    with st.spinner("Analyzing customer data..."):
        try:
            result = make_prediction(payload)
            render_results(result)
        except PredictionError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
            st.info("Please check your API endpoint configuration and try again.")

render_sidebar()

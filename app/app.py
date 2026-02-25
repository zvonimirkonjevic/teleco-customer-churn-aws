"""
Telco Customer Churn Prediction — Streamlit Application

Entry point that wires together UI components and the API client.
Requires authentication via streamlit-authenticator before accessing
the prediction interface.
Run with:  streamlit run app/app.py
"""

import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

from components import (
    inject_styles,
    render_form,
    render_header,
    render_results,
    render_sidebar,
)
from config import PAGE_TITLE, PAGE_LAYOUT, SIDEBAR_STATE, AUTH_CONFIG_PATH
from predict import make_prediction, PredictionError


# Must be the first Streamlit command
st.set_page_config(
    page_title=PAGE_TITLE,
    layout=PAGE_LAYOUT,
    initial_sidebar_state=SIDEBAR_STATE,
)

# Load authentication configuration
with open(AUTH_CONFIG_PATH) as f:
    auth_config = yaml.load(f, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    auth_config["credentials"],
    auth_config["cookie"]["name"],
    auth_config["cookie"]["key"],
    auth_config["cookie"]["expiry_days"],
)

# Render login widget
try:
    authenticator.login()
except Exception as e:
    st.error(e)

if st.session_state.get("authentication_status"):
    # Authenticated — show the application
    authenticator.logout(button_name="Logout", location="sidebar", use_container_width=True)

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

elif st.session_state.get("authentication_status") is False:
    st.error("Username or password is incorrect.")
elif st.session_state.get("authentication_status") is None:
    st.warning("Please enter your username and password to access the application.")

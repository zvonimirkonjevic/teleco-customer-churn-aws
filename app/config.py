"""
Telco Customer Churn Prediction — Configuration

Centralizes all application settings, constants, and secrets access.
"""

import streamlit as st


# ---------------------------------------------------------------------------
# API Configuration
# ---------------------------------------------------------------------------

API_ENDPOINT: str = st.secrets.get(
    "API_ENDPOINT",
    "https://your-api-gateway-id.execute-api.us-east-1.amazonaws.com/prod/predict",
)
API_TIMEOUT_SECONDS: int = 30


# ---------------------------------------------------------------------------
# Model Metadata (displayed in sidebar)
# ---------------------------------------------------------------------------

MODEL_ALGORITHM: str = "XGBoost"
MODEL_ACCURACY: str = "85%"
MODEL_AUC: str = "0.88"


# ---------------------------------------------------------------------------
# UI Constants
# ---------------------------------------------------------------------------

PAGE_TITLE: str = "Telco Customer Churn Predictor"
PAGE_LAYOUT: str = "centered"
SIDEBAR_STATE: str = "expanded"

# Churn probability threshold (0-1) — above this the customer is "High Risk"
CHURN_THRESHOLD: float = 0.5

"""
Telco Customer Churn Prediction — Configuration

Centralizes all application settings, constants, and secrets access.
"""

import os


# ---------------------------------------------------------------------------
# API Configuration
# ---------------------------------------------------------------------------

API_ENDPOINT: str = os.environ.get(
    "API_ENDPOINT",
    "http://prediction-api:8000",
)


# ---------------------------------------------------------------------------
# Model Metadata (displayed in sidebar)
# ---------------------------------------------------------------------------

MODEL_ALGORITHM: str = "XGBoost"
MODEL_ACCURACY: str = "77%"
MODEL_AUC: str = "0.84"


# ---------------------------------------------------------------------------
# UI Constants
# ---------------------------------------------------------------------------

PAGE_TITLE: str = "Telco Customer Churn Predictor"
PAGE_LAYOUT: str = "centered"
SIDEBAR_STATE: str = "expanded"

# Churn probability threshold (0-1) — above this the customer is "High Risk"
CHURN_THRESHOLD: float = 0.5

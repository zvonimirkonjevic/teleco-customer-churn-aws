"""
Telco Customer Churn Prediction — Configuration

Centralizes all application settings, constants, and secrets access.
"""

import os
from pathlib import Path

API_ENDPOINT: str = os.environ.get(
    "API_ENDPOINT",
    "http://prediction-api:8000",
)

MODEL_ALGORITHM: str = "XGBoost"
MODEL_ACCURACY: str = "77%"
MODEL_AUC: str = "0.84"

PAGE_TITLE: str = "Telco Customer Churn Predictor"
PAGE_LAYOUT: str = "centered"
SIDEBAR_STATE: str = "expanded"

AUTH_CONFIG_PATH: str = str(Path(__file__).parent / "auth_config.yaml")
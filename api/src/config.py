"""API configuration from environment variables."""

import os

SAGEMAKER_ENDPOINT_NAME: str = os.environ.get(
    "SAGEMAKER_ENDPOINT_NAME",
    "telco-customer-churn-xgboost-endpoint",
)
AWS_REGION: str = os.environ.get("AWS_REGION", "eu-central-1")
CHURN_THRESHOLD: float = float(os.environ.get("CHURN_THRESHOLD", "0.5"))

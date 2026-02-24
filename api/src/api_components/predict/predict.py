import json
import pickle
import os

import boto3
import numpy as np
from loguru import logger

from config import AWS_REGION, CHURN_THRESHOLD, SAGEMAKER_ENDPOINT_NAME

_client = None

# Load feature names and scaler from training artifacts
_artifacts_dir = os.environ.get("ARTIFACTS_DIR", "/var/task/artifacts")

with open(os.path.join(_artifacts_dir, "feature_names.pkl"), "rb") as f:
    FEATURE_NAMES = pickle.load(f)

with open(os.path.join(_artifacts_dir, "scaler.pkl"), "rb") as f:
    SCALER = pickle.load(f)

# Numerical features that need scaling (must match training)
SCALED_FEATURES = list(SCALER.feature_names_in_)


def _get_sagemaker_client():
    """Return a cached SageMaker runtime client (reused across Lambda invocations)."""
    global _client
    if _client is None:
        _client = boto3.client("sagemaker-runtime", region_name=AWS_REGION)
    return _client


def _one_hot(value: str, categories: list[str], prefix: str) -> dict:
    """Return one-hot encoded dict for a categorical value."""
    return {f"{prefix}_{cat}": 1 if cat == value else 0 for cat in categories}


def _clean(val: str) -> str:
    """Normalize category values to match training column names."""
    return val.replace(" ", "_").replace("(", "").replace(")", "").replace("-", "_")


def _tenure_group(tenure: int) -> str:
    """Assign tenure to a bin matching training preprocessing."""
    if tenure <= 12:
        return "0_1yr"
    elif tenure <= 24:
        return "1_2yr"
    elif tenure <= 48:
        return "2_4yr"
    else:
        return "4_6yr"


def _preprocess(payload: dict) -> list[float]:
    """Transform raw form input into feature vector matching the trained model."""
    tenure = payload["tenure"]
    monthly = payload["monthlyCharges"]
    total = payload["totalCharges"]

    # Feature engineering
    avg_monthly_spend = total / (tenure + 1)

    services = [
        payload["onlineSecurity"], payload["onlineBackup"],
        payload["deviceProtection"], payload["techSupport"],
        payload["streamingTV"], payload["streamingMovies"],
    ]
    total_services = sum(1 for s in services if s == "Yes")

    # Build raw feature dict
    features = {}

    # Binary features
    features["gender"] = 1 if payload["gender"] == "Male" else 0
    features["SeniorCitizen"] = 1 if payload["seniorCitizen"] == "Yes" else 0
    features["Partner"] = 1 if payload["partner"] == "Yes" else 0
    features["Dependents"] = 1 if payload["dependents"] == "Yes" else 0
    features["PhoneService"] = 1 if payload["phoneService"] == "Yes" else 0
    features["PaperlessBilling"] = 1 if payload["paperlessBilling"] == "Yes" else 0

    # Numerical features (will be scaled below)
    features["tenure"] = tenure
    features["MonthlyCharges"] = monthly
    features["TotalCharges"] = total
    features["AvgMonthlySpend"] = avg_monthly_spend
    features["TotalServices"] = total_services

    # One-hot encoded categoricals
    features.update(_one_hot(
        _clean(payload["multipleLines"]),
        ["No", "No_phone_service", "Yes"], "MultipleLines"))
    features.update(_one_hot(
        _clean(payload["internetService"]),
        ["DSL", "Fiber_optic", "No"], "InternetService"))
    features.update(_one_hot(
        _clean(payload["onlineSecurity"]),
        ["No", "No_internet_service", "Yes"], "OnlineSecurity"))
    features.update(_one_hot(
        _clean(payload["onlineBackup"]),
        ["No", "No_internet_service", "Yes"], "OnlineBackup"))
    features.update(_one_hot(
        _clean(payload["deviceProtection"]),
        ["No", "No_internet_service", "Yes"], "DeviceProtection"))
    features.update(_one_hot(
        _clean(payload["techSupport"]),
        ["No", "No_internet_service", "Yes"], "TechSupport"))
    features.update(_one_hot(
        _clean(payload["streamingTV"]),
        ["No", "No_internet_service", "Yes"], "StreamingTV"))
    features.update(_one_hot(
        _clean(payload["streamingMovies"]),
        ["No", "No_internet_service", "Yes"], "StreamingMovies"))
    features.update(_one_hot(
        _clean(payload["contract"]),
        ["Month_to_month", "One_year", "Two_year"], "Contract"))
    features.update(_one_hot(
        _clean(payload["paymentMethod"]),
        ["Bank_transfer_automatic", "Credit_card_automatic",
         "Electronic_check", "Mailed_check"], "PaymentMethod"))
    features.update(_one_hot(
        _tenure_group(tenure),
        ["0_1yr", "1_2yr", "2_4yr", "4_6yr"], "TenureGroup"))

    # Apply standard scaling to numerical features
    raw_values = np.array([[features[f] for f in SCALED_FEATURES]])
    scaled_values = SCALER.transform(raw_values)[0]
    for i, feat in enumerate(SCALED_FEATURES):
        features[feat] = float(scaled_values[i])

    # Return features in the exact order the model expects
    return [features[f] for f in FEATURE_NAMES]


def make_prediction(payload: dict) -> dict:
    """
    Preprocess raw input, send to SageMaker endpoint, and return the result.

    Parameters
    ----------
    payload : dict
        Customer feature dictionary produced by the input form.

    Returns
    -------
    dict
        ``{"churn_probability": float, "will_churn": bool}``
    """
    logger.info("Processing prediction request")
    client = _get_sagemaker_client()
    feature_vector = _preprocess(payload)

    # SageMaker built-in XGBoost expects CSV format
    csv_body = ",".join(str(v) for v in feature_vector)
    logger.debug("Feature vector length: {}", len(feature_vector))

    response = client.invoke_endpoint(
        EndpointName=SAGEMAKER_ENDPOINT_NAME,
        ContentType="text/csv",
        Body=csv_body,
    )

    raw_body = response["Body"].read().decode("utf-8")
    logger.debug("SageMaker raw response: {}", raw_body)

    result = json.loads(raw_body)
    churn_probability = float(result)

    logger.info("Prediction complete: probability={:.4f}, churn={}", churn_probability, churn_probability >= CHURN_THRESHOLD)

    return {
        "churn_probability": churn_probability,
        "will_churn": churn_probability >= CHURN_THRESHOLD,
    }

import json
import os

import boto3
from loguru import logger

from config import AWS_REGION, CHURN_THRESHOLD, SAGEMAKER_ENDPOINT_NAME

_client = None

# Load model parameters from JSON (no sklearn/numpy needed)
_artifacts_dir = os.environ.get("ARTIFACTS_DIR", "/var/task/artifacts")

with open(os.path.join(_artifacts_dir, "model_params.json")) as f:
    _params = json.load(f)

FEATURE_NAMES: list[str] = _params["feature_names"]
SCALED_FEATURES: list[str] = _params["scaler"]["features"]
SCALER_MEANS: list[float] = _params["scaler"]["means"]
SCALER_STDS: list[float] = _params["scaler"]["stds"]


def _get_sagemaker_client():
    """Returns a cached SageMaker runtime client, reused across Lambda invocations."""
    global _client
    if _client is None:
        _client = boto3.client("sagemaker-runtime", region_name=AWS_REGION)
    return _client


def _one_hot(value: str, categories: list[str], prefix: str) -> dict:
    """Returns a one-hot encoded dict for a categorical value.

    Args:
        value: The category value to encode.
        categories: All possible category values.
        prefix: Column name prefix for the encoded keys.

    Returns:
        Dict mapping ``{prefix}_{category}`` to 0 or 1.
    """
    return {f"{prefix}_{cat}": 1 if cat == value else 0 for cat in categories}


def _clean(val: str) -> str:
    """Normalizes category values to match training column names.

    Args:
        val: Raw category string from the input form.

    Returns:
        Cleaned string with spaces, parens, and hyphens replaced by underscores.
    """
    return val.replace(" ", "_").replace("(", "").replace(")", "").replace("-", "_")


def _tenure_group(tenure: int) -> str:
    """Assigns tenure to a bin matching training preprocessing.

    Args:
        tenure: Customer tenure in months.

    Returns:
        Bin label such as ``"0_1yr"``, ``"1_2yr"``, ``"2_4yr"``, or ``"4_6yr"``.
    """
    if tenure <= 12:
        return "0_1yr"
    elif tenure <= 24:
        return "1_2yr"
    elif tenure <= 48:
        return "2_4yr"
    else:
        return "4_6yr"


def _preprocess(payload: dict) -> list[float]:
    """Transforms raw form input into a feature vector matching the trained model.

    Args:
        payload: Customer feature dictionary from the input form.

    Returns:
        Ordered list of floats ready for SageMaker inference.
    """
    tenure = payload["tenure"]
    monthly = payload["monthlyCharges"]
    total = payload["totalCharges"]

    # Feature engineering — mirrors training: TotalCharges / (tenure + 1)
    # The +1 avoids division by zero for new customers (tenure == 0)
    avg_monthly_spend = total / (tenure + 1)

    services = [
        payload["onlineSecurity"], payload["onlineBackup"],
        payload["deviceProtection"], payload["techSupport"],
        payload["streamingTV"], payload["streamingMovies"],
    ]
    total_services = sum(1 for s in services if s == "Yes")

    features = {}

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

    # Apply standard scaling: (value - mean) / std
    for feat, mean, std in zip(SCALED_FEATURES, SCALER_MEANS, SCALER_STDS):
        if std == 0:
            features[feat] = 0.0
        else:
            features[feat] = (features[feat] - mean) / std

    # Return features in the exact order the model expects
    return [features[f] for f in FEATURE_NAMES]


def make_prediction(payload: dict) -> dict:
    """Preprocesses raw input, sends to SageMaker endpoint, and returns the result.

    Args:
        payload: Customer feature dictionary produced by the input form.

    Returns:
        Dict with ``churn_probability`` (float) and ``will_churn`` (bool).
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

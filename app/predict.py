"""
Telco Customer Churn Prediction — API Client

Calls the FastAPI prediction API via HTTP and returns parsed predictions.
"""

import json
import boto3
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
import requests

from config import API_ENDPOINT


class PredictionError(Exception):
    def __init__(self, message: str, status_code: int | None = None):
        self.status_code = status_code
        super().__init__(message)


def make_signed_request(url: str, payload: dict) -> dict:
    """Sends a SigV4-signed POST request to an AWS API Gateway endpoint.

    Args:
        url: The full URL to send the request to.
        payload: JSON-serializable request body.

    Returns:
        The ``requests.Response`` object.
    """
    session = boto3.Session()
    credentials = session.get_credentials().get_frozen_credentials()

    aws_request = AWSRequest(
        method="POST",
        url=url,
        data=json.dumps(payload),
        headers={"Content-Type": "application/json"},
    )

    SigV4Auth(credentials, "execute-api", session.region_name).add_auth(aws_request)

    response = requests.post(
        url,
        data=aws_request.data,
        headers=dict(aws_request.headers),
        timeout=60,
    )
    return response


def make_prediction(payload: dict) -> dict:
    """Sends customer features to the prediction API and returns the result.

    Args:
        payload: Customer feature dictionary produced by the input form.

    Returns:
        Dict with ``churn_probability`` (float) and ``will_churn`` (bool).

    Raises:
        PredictionError: With a user-friendly message describing what went wrong.
    """
    try:
        response = make_signed_request(f"{API_ENDPOINT}/predict", payload)

    except requests.ConnectionError:
        raise PredictionError(
            "Could not connect to the prediction service. Please check that the API is running."
        )
    except requests.Timeout:
        raise PredictionError(
            "The prediction service took too long to respond. Please try again."
        )

    if response.ok:
        return response.json()

    status = response.status_code
    detail = ""
    try:
        detail = response.json().get("detail", "")
    except (ValueError, AttributeError):
        pass

    if status == 422:
        raise PredictionError(
            f"Invalid input data: {detail}" if detail else "The submitted data is invalid.",
            status_code=status,
        )
    if status == 502:
        raise PredictionError(
            "The ML model endpoint is currently unavailable. Please try again later.",
            status_code=status,
        )
    if status == 503:
        raise PredictionError(
            "The ML model is starting up. Please wait a moment and try again.",
            status_code=status,
        )

    raise PredictionError(
        f"Prediction failed (HTTP {status}): {detail}" if detail else f"Prediction failed with status {status}.",
        status_code=status,
    )

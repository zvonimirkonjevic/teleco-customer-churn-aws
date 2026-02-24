"""
Telco Customer Churn Prediction — API Client

Calls the FastAPI prediction API via HTTP and returns parsed predictions.
"""

import requests

from config import API_ENDPOINT


class PredictionError(Exception):
    """Raised when the prediction API returns an error."""

    def __init__(self, message: str, status_code: int | None = None):
        self.status_code = status_code
        super().__init__(message)


def make_prediction(payload: dict) -> dict:
    """
    Send customer features to the prediction API and return the result.

    Parameters
    ----------
    payload : dict
        Customer feature dictionary produced by the input form.

    Returns
    -------
    dict
        ``{"churn_probability": float, "will_churn": bool}``

    Raises
    ------
    PredictionError
        With a user-friendly message describing what went wrong.
    """
    try:
        response = requests.post(
            f"{API_ENDPOINT}/predict",
            json=payload,
            timeout=60,
        )
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

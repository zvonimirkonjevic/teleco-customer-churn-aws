"""
Telco Customer Churn Prediction — API Client

Calls the FastAPI prediction API via HTTP and returns parsed predictions.
"""

import requests

from config import API_ENDPOINT


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
    """
    response = requests.post(
        f"{API_ENDPOINT}/predict",
        json=payload,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()

import json
import boto3

from config import AWS_REGION, CHURN_THRESHOLD, SAGEMAKER_ENDPOINT_NAME

_client = None


def _get_sagemaker_client():
    """Return a cached SageMaker runtime client (reused across Lambda invocations)."""
    global _client
    if _client is None:
        _client = boto3.client("sagemaker-runtime", region_name=AWS_REGION)
    return _client


def make_prediction(payload: dict) -> dict:
    """
    Send customer features to the SageMaker endpoint and return the result.

    Parameters
    ----------
    payload : dict
        Customer feature dictionary produced by the input form.

    Returns
    -------
    dict
        ``{"churn_probability": float, "will_churn": bool}``
    """
    client = _get_sagemaker_client()

    response = client.invoke_endpoint(
        EndpointName=SAGEMAKER_ENDPOINT_NAME,
        ContentType="application/json",
        Body=json.dumps(payload),
    )

    result = json.loads(response["Body"].read().decode("utf-8"))
    churn_probability = float(result)

    return {
        "churn_probability": churn_probability,
        "will_churn": churn_probability >= CHURN_THRESHOLD,
    }

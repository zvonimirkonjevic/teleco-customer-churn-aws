"""FastAPI application for churn prediction, deployed as AWS Lambda via Mangum."""

from botocore.exceptions import ClientError
from fastapi import FastAPI, HTTPException
from loguru import logger
from mangum import Mangum

from api_components.predict.predict import make_prediction
from api_components.predict.models import PredictionRequest, PredictionResponse

app = FastAPI(
    title="Telco Customer Churn Prediction API",
    version="1.0.0",
)


@app.get("/health")
def health_check():
    """Returns a simple health status for readiness probes."""
    return {"status": "healthy"}


@app.post("/predict", response_model=PredictionResponse)
def predict(payload: PredictionRequest):
    """Accepts customer features and returns a churn prediction.

    Args:
        payload: Customer feature data validated by Pydantic.

    Returns:
        PredictionResponse with churn probability and boolean churn flag.

    Raises:
        HTTPException: On SageMaker errors, missing fields, or invalid data.
    """
    try:
        result = make_prediction(payload.model_dump())
        return PredictionResponse(**result)
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        logger.error("SageMaker error [{}]: {}", error_code, e)
        if error_code == "ValidationError":
            raise HTTPException(
                status_code=422,
                detail="Invalid input: SageMaker rejected the feature vector.",
            )
        if error_code == "ModelNotReadyException":
            raise HTTPException(
                status_code=503,
                detail="Model endpoint is not ready. Please try again shortly.",
            )
        raise HTTPException(
            status_code=502,
            detail="SageMaker endpoint error. Please try again later.",
        )
    except KeyError as e:
        logger.error("Missing payload field: {}", e)
        raise HTTPException(
            status_code=422,
            detail=f"Missing required field: {e}",
        )
    except (ValueError, TypeError) as e:
        logger.error("Preprocessing error: {}", e)
        raise HTTPException(
            status_code=422,
            detail=f"Invalid input data: {e}",
        )
    except Exception as e:
        logger.exception("Unexpected error during prediction")
        raise HTTPException(
            status_code=500,
            detail="Internal server error. Please try again later.",
        )


handler = Mangum(app, lifespan="off", api_gateway_base_path="/v1")

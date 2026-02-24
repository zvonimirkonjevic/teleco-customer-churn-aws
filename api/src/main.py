"""FastAPI application for churn prediction, deployed as AWS Lambda via Mangum."""

from fastapi import FastAPI, HTTPException
from mangum import Mangum

from api_components.predict.predict import make_prediction
from api_components.predict.models import PredictionRequest, PredictionResponse

app = FastAPI(
    title="Telco Customer Churn Prediction API",
    version="1.0.0",
)


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/predict", response_model=PredictionResponse)
def predict(payload: PredictionRequest):
    try:
        result = make_prediction(payload.model_dump())
        return PredictionResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


handler = Mangum(app, lifespan="off", api_gateway_base_path="/v1")

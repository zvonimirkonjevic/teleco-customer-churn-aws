from pydantic import BaseModel, Field


class PredictionRequest(BaseModel):
    tenure: int = Field(..., ge=0, le=100)
    monthlyCharges: float = Field(..., ge=0, le=200)
    totalCharges: float = Field(..., ge=0, le=10000)
    contract: str
    internetService: str
    paymentMethod: str
    phoneService: str
    onlineSecurity: str
    onlineBackup: str
    deviceProtection: str
    techSupport: str
    streamingTV: str
    streamingMovies: str
    paperlessBilling: str


class PredictionResponse(BaseModel):
    churn_probability: float
    will_churn: bool

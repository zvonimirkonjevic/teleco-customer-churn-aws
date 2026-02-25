# Prediction API

FastAPI application for real-time customer churn prediction. Deployed as an AWS Lambda function (container image) behind API Gateway. Handles feature engineering, one-hot encoding, and standard scaling in pure Python — no sklearn or numpy at runtime.

## Module Structure

```
api/
├── src/
│   ├── main.py                         # FastAPI app + Mangum Lambda handler
│   ├── config.py                       # Environment config (endpoint name, region, threshold)
│   └── api_components/
│       └── predict/
│           ├── predict.py              # Preprocessing pipeline + SageMaker invocation
│           └── models.py              # Pydantic request/response models
└── environment/
    ├── Dockerfile.lambda               # Lambda container (public.ecr.aws/lambda/python:3.13)
    └── Dockerfile.local                # Local dev container (python:3.13-slim + uvicorn)
```

Root-level `docker-compose.yml` builds from `api/environment/Dockerfile.local` and injects AWS credentials via `.env`. The Streamlit app depends on the `prediction-api` service.

## Component Responsibilities

| Module | Responsibility | Key exports |
|---|---|---|
| `main.py` | FastAPI app with `/health` and `/predict` endpoints, Mangum handler (`api_gateway_base_path="/v1"`), structured error handling | `app`, `handler` |
| `config.py` | Reads `SAGEMAKER_ENDPOINT_NAME`, `AWS_REGION`, `CHURN_THRESHOLD` from environment variables | Constants |
| `predict.py` | Loads `model_params.json` at cold start, preprocesses raw input into 46-feature vector, invokes SageMaker endpoint | `make_prediction` |
| `models.py` | `PredictionRequest` (19 fields with Pydantic validation), `PredictionResponse` | Request/response models |

## Preprocessing Pipeline

Raw 19-field JSON → binary encoding → feature engineering → one-hot encoding → standard scaling → 46-feature CSV vector → SageMaker.

| Step | Detail |
|---|---|
| Binary encoding | gender, SeniorCitizen, Partner, Dependents, PhoneService, PaperlessBilling → 0/1 |
| Feature engineering | `AvgMonthlySpend` = TotalCharges / (tenure + 1), `TotalServices` = count of 6 services, `TenureGroup` (4 bins) |
| One-hot encoding | MultipleLines, InternetService, OnlineSecurity, OnlineBackup, DeviceProtection, TechSupport, StreamingTV, StreamingMovies, Contract, PaymentMethod, TenureGroup |
| Standard scaling | tenure, MonthlyCharges, TotalCharges, AvgMonthlySpend, TotalServices — using means/stds from `model_params.json` |

Scaler parameters are loaded from `data/processed/model_params.json` at cold start. This eliminates sklearn/numpy/scipy from the Lambda runtime — faster cold starts (~1s vs ~10s) and smaller image (~200MB vs ~1.5GB).

## Error Handling

Structured exception handling in `main.py` maps errors to HTTP status codes:

| Exception | Status | Message |
|---|---|---|
| `ClientError` — `ValidationError` | 422 | Invalid input: SageMaker rejected the feature vector |
| `ClientError` — `ModelNotReadyException` | 503 | Model endpoint is not ready |
| `ClientError` — other | 502 | SageMaker endpoint error |
| `KeyError` | 422 | Missing required field: `{field}` |
| `ValueError` / `TypeError` | 422 | Invalid input data: `{detail}` |
| Unhandled exception | 500 | Internal server error |

All errors are logged with loguru before raising `HTTPException`.

## API Contract

**`GET /health`** — Health check

```json
{ "status": "healthy" }
```

**`POST /predict`** — Churn prediction

Request body (19 customer features):

```json
{
  "gender": "Male",
  "seniorCitizen": "No",
  "partner": "Yes",
  "dependents": "No",
  "tenure": 12,
  "monthlyCharges": 50.0,
  "totalCharges": 600.0,
  "contract": "Month-to-month",
  "internetService": "Fiber optic",
  "paymentMethod": "Electronic check",
  "phoneService": "Yes",
  "multipleLines": "No",
  "onlineSecurity": "No",
  "onlineBackup": "No",
  "deviceProtection": "No",
  "techSupport": "No",
  "streamingTV": "No",
  "streamingMovies": "No",
  "paperlessBilling": "Yes"
}
```

Response:

```json
{
  "churn_probability": 0.73,
  "will_churn": true
}
```

Threshold: `churn_probability >= 0.5` → `will_churn: true`.

Pydantic validation constraints: `tenure` (0–100), `monthlyCharges` (0–200), `totalCharges` (0–10,000).

## Deployment

**AWS (Lambda):** Container image built from `Dockerfile.lambda`, pushed to ECR. Terraform `modules/lambda` provisions the function with SageMaker invoke policy. API Gateway routes requests via `$default` catch-all with `AWS_IAM` authorization — only callers with valid SigV4-signed requests (e.g., the ECS task role) can invoke the API. FastAPI handles all routing internally through Mangum.

**Local development:**

```bash
# Option A: Docker (from project root — includes Streamlit)
docker compose up -d          # API on :8000, Streamlit on :8501
curl http://localhost:8000/health

# Option B: uv (from project root)
uv sync --group api
uv run uvicorn api.src.main:app --host 0.0.0.0 --port 8000
```

## Configuration

| Setting | Source | Default |
|---|---|---|
| `SAGEMAKER_ENDPOINT_NAME` | Environment variable | `telco-customer-churn-xgboost-endpoint` |
| `AWS_REGION` | Environment variable | `eu-central-1` |
| `CHURN_THRESHOLD` | Environment variable | `0.5` |
| `ARTIFACTS_DIR` | Environment variable | `/var/task/artifacts` (Lambda), `/app/artifacts` (local) |

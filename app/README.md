# App

Streamlit web application for real-time customer churn prediction. Communicates with the FastAPI prediction API via SigV4-signed HTTP requests (API Gateway with AWS_IAM authorization → Lambda in production, direct container in local dev).

## Module Structure

```
app/
├── app.py                    # Entry point — page config, layout, PredictionError handling
├── config.py                 # Centralized settings (API_ENDPOINT, model metadata)
├── predict.py                # SigV4-signed API client: make_prediction(payload) → dict, PredictionError
├── components.py             # Pure UI functions (no business logic)
├── .streamlit/
│   └── config.toml           # Streamlit theme & server settings
└── environment/
    ├── Dockerfile.ecs        # ECS Fargate container image
    ├── Dockerfile.local      # python:3.13-slim, uv sync --frozen --only-group app
    └── .dockerignore
```

Root-level `docker-compose.yml` builds from `app/environment/Dockerfile.local`. The Streamlit app depends on the `prediction-api` service.

## Component Responsibilities

| Module | Responsibility | Key exports |
|---|---|---|
| `app.py` | Page config (`set_page_config`), wires components, catches `PredictionError` and generic exceptions | — |
| `config.py` | Reads `API_ENDPOINT` from env var (default: `http://prediction-api:8000`); defines model metadata constants | Constants |
| `predict.py` | `make_signed_request(url, payload)` — SigV4-signed POST via `botocore.auth.SigV4Auth`; `make_prediction(payload: dict) → dict` — calls API with 60s timeout, raises `PredictionError` with status-specific messages | `make_prediction`, `PredictionError` |
| `components.py` | `inject_styles()`, `render_header()`, `render_form() → dict\|None` (19 fields), `render_results(result)`, `render_sidebar()` | UI functions |

## Error Handling

The `PredictionError` exception provides user-friendly messages based on HTTP status codes:

| Status | Message |
|---|---|
| Connection error | "Could not connect to the prediction service." |
| Timeout | "The prediction service took too long to respond." |
| 422 | "Invalid input data: {detail}" |
| 502 | "The ML model endpoint is currently unavailable." |
| 503 | "The ML model is starting up. Please wait a moment and try again." |
| Other | "Prediction failed (HTTP {status}): {detail}" |

## Authentication

In production, the API Gateway route uses `AWS_IAM` authorization. The Streamlit app signs every request with AWS Signature Version 4 using `botocore.auth.SigV4Auth`:

1. Boto3 resolves AWS credentials from the ECS task role (via container credential provider)
2. The JSON payload is wrapped in a `botocore.awsrequest.AWSRequest`
3. `SigV4Auth` adds `Authorization`, `X-Amz-Date`, and `X-Amz-Security-Token` headers
4. The signed headers are passed to `requests.post()`

The ECS task role must have `execute-api:Invoke` permission on the API Gateway resource. This is configured in the Terraform IAM module's custom task policy.

## API Contract

**Request** — POST `/predict` with JSON body containing 19 customer features:

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

**Response:**

```json
{
  "churn_probability": 0.73,
  "will_churn": true
}
```

Threshold: `churn_probability >= 0.5` → `will_churn: true` (High Risk).

## Running Locally

```bash
# Option A: Docker (from project root — includes prediction API)
docker compose up -d
# Builds python:3.13-slim image, installs only app dependency group via uv
# API on :8000, Streamlit on :8501
# Health check: curl http://localhost:8501/_stcore/health

# Option B: uv (from project root)
uv sync --group app
uv run streamlit run app/app.py
```

Access at `http://localhost:8501`

## Configuration

| Setting | Location | Default |
|---|---|---|
| `API_ENDPOINT` | Environment variable | `http://prediction-api:8000` |
| Theme / layout | `.streamlit/config.toml` | centered, expanded sidebar |

# App

Streamlit web application for real-time customer churn prediction. Communicates with the FastAPI prediction API via HTTP (API Gateway → Lambda in production, direct container in local dev).

## Module Structure

```
app/
├── app.py                    # Entry point — page config, layout, PredictionError handling
├── config.py                 # Centralized settings (API_ENDPOINT, CHURN_THRESHOLD, model metadata)
├── predict.py                # HTTP client: make_prediction(payload) → dict, PredictionError
├── components.py             # Pure UI functions (no business logic)
├── .streamlit/
│   ├── config.toml           # Streamlit theme & server settings
│   └── secrets.toml.example  # Template — copy to secrets.toml, set API_ENDPOINT
└── environment/
    ├── Dockerfile.ecs        # ECS Fargate container image
    ├── Dockerfile.local      # python:3.13-slim, uv sync --frozen --only-group app
    └── .dockerignore
```

Root-level `docker-compose.yml` builds from `app/environment/Dockerfile.local` and mounts `secrets.toml` read-only. The Streamlit app depends on the `prediction-api` service.

## Component Responsibilities

| Module | Responsibility | Key exports |
|---|---|---|
| `app.py` | Page config (`set_page_config`), wires components, catches `PredictionError` and generic exceptions | — |
| `config.py` | Reads `API_ENDPOINT` from env var (default: `http://prediction-api:8000`); defines `CHURN_THRESHOLD` (0.5), model metadata | Constants |
| `predict.py` | `make_prediction(payload: dict) → dict` — POST to prediction API (60s timeout), raises `PredictionError` with status-specific messages | `make_prediction`, `PredictionError` |
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
uv sync
uv run streamlit run app/app.py
```

Access at `http://localhost:8501`

## Configuration

| Setting | Location | Default |
|---|---|---|
| `API_ENDPOINT` | Environment variable / `.streamlit/secrets.toml` | `http://prediction-api:8000` |
| `CHURN_THRESHOLD` | `config.py` | `0.5` |
| Theme / layout | `.streamlit/config.toml` | centered, expanded sidebar |

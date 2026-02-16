# App

Streamlit web application for real-time customer churn prediction. Communicates with SageMaker via an API Gateway → Lambda proxy.

## Module Structure

```
app/
├── app.py                    # Entry point — page config, layout, error boundary
├── config.py                 # Centralized settings (API_ENDPOINT, CHURN_THRESHOLD, model metadata)
├── api_client.py             # HTTP client: get_api_endpoint(), make_prediction(payload) → dict
├── components.py             # Pure UI functions (no business logic)
├── .streamlit/
│   ├── config.toml           # Streamlit theme & server settings
│   └── secrets.toml.example  # Template — copy to secrets.toml, set API_ENDPOINT
└── environment/
    ├── Dockerfile.local      # python:3.12-slim, uv sync --frozen --only-group app
    └── .dockerignore
```

Root-level `docker-compose.yml` builds from `app/environment/Dockerfile.local` and mounts `secrets.toml` read-only.

## Component Responsibilities

| Module | Responsibility | Key exports |
|---|---|---|
| `app.py` | Page config (`set_page_config`), wires components, catches prediction exceptions | — |
| `config.py` | Reads `API_ENDPOINT` from `st.secrets`; defines `CHURN_THRESHOLD` (0.5), `API_TIMEOUT_SECONDS` (30) | Constants |
| `api_client.py` | `make_prediction(payload: dict) → dict` — POST to API Gateway, raises on HTTP errors | `make_prediction`, `get_api_endpoint` |
| `components.py` | `inject_styles()`, `render_header()`, `render_form() → dict\|None` (14 fields), `render_results(result)`, `render_sidebar()` | UI functions |

## API Contract

**Request** — POST JSON with 14 customer features:

```json
{
  "tenure": 12,
  "monthlyCharges": 50.0,
  "totalCharges": 600.0,
  "contract": "Month-to-month",
  "internetService": "Fiber optic",
  "paymentMethod": "Electronic check",
  "phoneService": "Yes",
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
# Option A: Docker (from project root)
docker compose up -d
# Builds python:3.12-slim image, installs only app dependency group via uv
# Mounts secrets.toml read-only, exposes :8501
# Health check: curl http://localhost:8501/_stcore/health

# Option B: uv (from project root)
uv sync
uv run streamlit run app/app.py
```

Access at `http://localhost:8501`

## Configuration

| Setting | Location | Default |
|---|---|---|
| `API_ENDPOINT` | `.streamlit/secrets.toml` | — (required) |
| `API_TIMEOUT_SECONDS` | `config.py` | `30` |
| `CHURN_THRESHOLD` | `config.py` | `0.5` |
| Theme / layout | `.streamlit/config.toml` | centered, expanded sidebar |

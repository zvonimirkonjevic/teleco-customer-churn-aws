# Telco Customer Churn Prediction

End-to-end ML system for binary churn classification on telecommunications customer data. Trained on AWS SageMaker, served via a real-time endpoint behind API Gateway + Lambda, with a Streamlit front-end. Infrastructure managed with Terraform (modular layout, S3 remote state).

## Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐      ┌──────────────────────┐
│  Streamlit  │─────▶│ API Gateway  │─────▶│   Lambda    │─────▶│  SageMaker Endpoint  │
│   (Client)  │ POST │  (REST API)  │      │   (Proxy)   │ IAM  │  XGBoost · ml.m5.lg  │
└─────────────┘      └──────────────┘      └─────────────┘      └──────────────────────┘
                                                                          │
                                                                          ▼
                                                                   ┌─────────────┐
                                                                   │  S3 Bucket  │
                                                                   │ model.tar.gz│
                                                                   └─────────────┘
```

**Request flow:** Client POSTs JSON → API Gateway → Lambda authenticates via IAM (SigV4) and forwards to SageMaker → XGBoost model returns churn probability → Lambda formats response → Client receives `{ churn_probability, will_churn }`.

The Lambda proxy pattern decouples clients from SigV4 signing — clients hit a simple REST endpoint without AWS SDK dependencies.

## Tech Stack

| Layer | Technology | Detail |
|---|---|---|
| **ML Framework** | AWS SageMaker | Training (built-in XGBoost, Linear Learner, KNN) + scikit-learn Script Mode (RF, SVM) |
| **Model** | XGBoost 1.7-1 | Best F1 (0.627) and AUC-ROC (0.840); served via prebuilt SageMaker container |
| **Data Processing** | pandas, NumPy, scikit-learn | Feature engineering, StandardScaler, one-hot/binary encoding → 46 features |
| **Class Balancing** | SMOTE (imbalanced-learn) | Oversampled minority class: 1,869 → 4,139 synthetic samples |
| **Visualization** | Matplotlib, Seaborn | EDA charts, correlation matrix, customer segmentation |
| **IaC** | Terraform (~> 5.0) | Modular layout: `modules/iam`, `modules/sagemaker-endpoint`; S3 remote state |
| **Inference** | SageMaker Endpoint | Real-time, `ml.m5.large` × 1 instance, single `AllTraffic` variant |
| **API** | API Gateway + Lambda | Lambda proxy handles SigV4 signing; public REST endpoint |
| **Front-end** | Streamlit 1.54+ | Two-column form, `requests`-based API client, risk-level display |
| **Containerization** | Docker + docker-compose | Local dev: `python:3.12-slim`, `uv sync --frozen --only-group app` |
| **Package Management** | uv + pyproject.toml | Lockfile-based (`uv.lock`), dependency groups (`app` for runtime-only) |
| **Runtime** | Python ≥ 3.12 | Enforced in `pyproject.toml` `requires-python` |

## Model Selection

Five algorithms evaluated on an 80/20 stratified split (test set: 1,409 samples). Ranked by F1-Score:

| # | Algorithm | Training Mode | Accuracy | Precision | Recall | F1 | AUC-ROC | MCC |
|---|-----------|---------------|----------|-----------|--------|----|---------|-----|
| 1 | **XGBoost** | SageMaker built-in | **0.769** | **0.548** | **0.733** | **0.627** | **0.840** | **0.475** |
| 2 | Random Forest | scikit-learn Script Mode | 0.770 | 0.551 | 0.722 | 0.625 | 0.838 | 0.472 |
| 3 | SVM | scikit-learn Script Mode | 0.752 | 0.523 | 0.738 | 0.612 | 0.831 | 0.451 |
| 4 | KNN | SageMaker built-in | 0.745 | 0.514 | 0.719 | 0.600 | — | 0.433 |
| 5 | Linear Learner | SageMaker built-in | 0.795 | 0.630 | 0.551 | 0.588 | 0.829 | 0.454 |

**Selection rationale:** XGBoost selected for highest F1 and AUC-ROC — best balance of precision and recall for churn detection where false negatives (missed churners) carry higher business cost.

> SVM yields highest recall (0.738) — preferable if the objective shifts to minimizing missed churners. Linear Learner has best raw accuracy (0.795) but at the expense of recall.

## Data Pipeline

### EDA (`notebooks/01_eda_preprocessing.ipynb`)

Statistical profiling of 7,043 customer records. Key findings:

- **Class imbalance:** 73.5% retained / 26.5% churned
- **High-risk segments:** month-to-month contracts (~42% churn), fiber optic (~42%), electronic check payment (~45%), tenure < 12 months
- **Analysis:** target distribution, demographic breakdowns, service usage correlation, financial distributions, feature correlation matrix

### Preprocessing (`notebooks/02_data_preprocessing.ipynb`)

| Step | Detail |
|---|---|
| Missing values | `TotalCharges` → numeric; 11 nulls imputed with `MonthlyCharges` (new customers with tenure = 0) |
| Dropped columns | `customerID` |
| Feature engineering | `AvgMonthlySpend` = TotalCharges / (tenure + 1); `TenureGroup` (4 bins); `TotalServices` (count of 6 services) |
| Binary encoding | gender, Partner, Dependents, PhoneService, PaperlessBilling, Churn |
| One-hot encoding | MultipleLines, InternetService, OnlineSecurity, OnlineBackup, DeviceProtection, TechSupport, StreamingTV, StreamingMovies, Contract, PaymentMethod, TenureGroup |
| Feature count | 46 after encoding |
| Scaling | `StandardScaler` on: tenure, MonthlyCharges, TotalCharges, AvgMonthlySpend, TotalServices |
| Split | 80/20 stratified → train: 5,634 / test: 1,409 |
| SMOTE | Applied to training set → 4,139 per class (8,278 total) |

**Output artifacts:** `data/processed/{train_smote,train_original,test}.csv`

### Training (`notebooks/03_model_training_and_evaluation.ipynb`)

- **SageMaker built-in:** XGBoost, Linear Learner, KNN — trained directly via SageMaker Estimator API
- **scikit-learn Script Mode:** Random Forest (`scripts/rf_train.py`), SVM (`scripts/svm_train.py`) — custom training scripts with `model_fn` / `predict_fn` entry points, hyperparameters exposed as CLI args for SageMaker HPO
- **Evaluation:** 5-fold cross-validation, grid search over hyperparameters, SageMaker Experiments for metric tracking

## Infrastructure (Terraform)

Modular Terraform configuration in `infra/terraform/`. See [infra/README.md](infra/README.md) for full details.

| Module | Resources |
|---|---|
| `modules/iam` | SageMaker execution role, `AmazonSageMakerFullAccess` attachment, inline S3 read policy |
| `modules/sagemaker-endpoint` | Prebuilt XGBoost ECR image lookup, `aws_sagemaker_model`, endpoint config (`ml.m5.large` × 1), real-time endpoint |

**State:** S3 backend (`teleco-churn-terraform-state`), encrypted, `eu-central-1`, profile `teleco-churn-terraform`.

```bash
cd infra/terraform && terraform init && terraform plan && terraform apply
```

## Streamlit Application

Modular Streamlit app in `app/`. See [app/README.md](app/README.md) for component details.

| Module | Responsibility |
|---|---|
| `app.py` | Entry point — page config, layout orchestration, error boundary |
| `config.py` | Centralized settings: `API_ENDPOINT` (from `secrets.toml`), `CHURN_THRESHOLD`, model metadata |
| `api_client.py` | `make_prediction(payload)` → POST to API Gateway, returns `{ churn_probability, will_churn }` |
| `components.py` | Pure UI functions: `render_header`, `render_form` (14 input fields), `render_results`, `render_sidebar` |

**API contract:** POST with JSON body containing 14 customer features → response: `{ churn_probability: float, will_churn: bool }`

**Local development:**
```bash
# Option A: Docker (from project root)
docker compose up -d                    # builds python:3.12-slim, installs via uv, exposes :8501

# Option B: uv (from project root)
uv sync && uv run streamlit run app/app.py
```

## Getting Started

### Prerequisites

| Requirement | Notes |
|---|---|
| AWS account | SageMaker, Lambda, API Gateway, S3, IAM access |
| AWS CLI | Configured with `teleco-churn-terraform` profile for Terraform |
| Python ≥ 3.12 | Enforced by `pyproject.toml` |
| [uv](https://docs.astral.sh/uv/) | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Terraform | For infrastructure provisioning |
| Docker | Optional — for containerized local development |

### Setup

```bash
# 1. Clone & install dependencies
git clone <repo-url> && cd teleco-customer-churn-aws
uv sync

# 2. Provision infrastructure
cd infra/terraform
terraform init && terraform apply
cd ../..

# 3. Run notebooks in order on SageMaker (or locally with uv run jupyter)
#    01_eda_preprocessing.ipynb → 02_data_preprocessing.ipynb → 03_model_training_and_evaluation.ipynb

# 4. Configure app secrets
cp app/.streamlit/secrets.toml.example app/.streamlit/secrets.toml
# Set API_ENDPOINT to your API Gateway invoke URL

# 5. Run application
docker compose up -d          # or: uv run streamlit run app/app.py
# → http://localhost:8501
```

## Repository Structure

```
teleco-customer-churn-aws/
├── app/                                    # Streamlit front-end
│   ├── app.py                              #   Entry point (layout, error handling)
│   ├── config.py                           #   Settings & secrets (API_ENDPOINT, thresholds)
│   ├── api_client.py                       #   HTTP client → API Gateway
│   ├── components.py                       #   UI components (form, results, sidebar, styles)
│   ├── .streamlit/                         #   config.toml + secrets.toml
│   └── environment/
│       └── Dockerfile.local                #   python:3.12-slim, uv sync --only-group app
│
├── infra/                                  # Terraform IaC
│   └── terraform/
│       ├── backend.tf                      #   required_providers, S3 remote state
│       ├── main.tf                         #   Root module (empty — delegates to modules)
│       ├── variables.tf                    #   Root variables (empty)
│       ├── providers.tf                    #   AWS provider: eu-central-1
│       ├── terraform.tfvars                #   default_region, model_data_uri
│       └── modules/
│           ├── iam/main.tf                 #   SageMaker execution role + S3 policy
│           └── sagemaker-endpoint/         #   Model, endpoint config, endpoint
│               ├── main.tf
│               └── variables.tf
│
├── data/
│   ├── raw/teleco-customer-churn.csv       # Original dataset (7,043 records)
│   └── processed/                          # Pipeline outputs
│       ├── teleco-customer-churn-cleaned.csv
│       ├── train_smote.csv                 #   SMOTE-balanced training (8,278 samples)
│       ├── train_original.csv              #   Original training (5,634 samples)
│       └── test.csv                        #   Stratified test set (1,409 samples)
│
├── notebooks/
│   ├── 01_eda_preprocessing.ipynb          # EDA & statistical profiling
│   ├── 02_data_preprocessing.ipynb         # Feature eng, encoding, SMOTE
│   └── 03_model_training_and_evaluation.ipynb  # 5-algorithm comparison on SageMaker
│
├── scripts/
│   ├── rf_train.py                         # SageMaker Script Mode: RandomForestClassifier
│   └── svm_train.py                        # SageMaker Script Mode: SVC (probability=True)
│
├── buildspec/                              # AWS CodeBuild specs (placeholder)
├── docs/                                   # Architecture docs (placeholder)
│
├── docker-compose.yml                      # Local dev: builds & runs Streamlit on :8501
├── pyproject.toml                          # Python ≥3.12, dependency groups (app)
├── uv.lock                                 # Deterministic dependency lock
└── README.md
```

## Design Decisions

| Area | Decision | Rationale |
|---|---|---|
| Model serving | Real-time endpoint (`ml.m5.large`) | Sub-second latency for interactive app; serverless inference not available for XGBoost 1.7 |
| API auth | Lambda proxy pattern | Decouples client from SigV4 signing; simplifies front-end integration |
| IaC | Terraform modules (not flat) | Separates IAM from SageMaker concerns; cleaner diffs and code review |
| State | S3 backend, no DynamoDB lock | Single-developer project — lock contention not a concern |
| Packaging | `uv` with `pyproject.toml` + lockfile | Deterministic installs, 10-100× faster than pip, dependency groups for slim runtime |
| Docker | `--only-group app` | Production container only installs Streamlit + requests (no SageMaker SDK / notebooks) |
| Class imbalance | SMOTE on training set only | Avoids data leakage; test set retains original distribution for honest evaluation |
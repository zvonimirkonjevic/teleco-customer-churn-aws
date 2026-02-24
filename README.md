# Telco Customer Churn Prediction

End-to-end ML platform on AWS for predicting customer churn. Three-tier serverless architecture provisioned with modular Terraform — Streamlit UI on ECS Fargate, FastAPI prediction API on Lambda behind API Gateway, and a serverless SageMaker XGBoost endpoint.

## Architecture

```
┌──────────┐     ┌───────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────┐     ┌──────────────────────────┐
│ Client   │────▶│  ALB  │────▶│  ECS Fargate │────▶│ API Gateway │────▶│  Lambda  │────▶│   SageMaker Endpoint     │
│          │HTTP │(HTTP) │     │ (Streamlit)  │HTTP │ (HTTP API)  │     │(FastAPI) │ IAM │  XGBoost · Serverless    │
└──────────┘     └───────┘     └──────┬───────┘     └─────────────┘     └────┬─────┘     └────────────┬─────────────┘
                                      │                                      │                        │
                                      ▼                                      ▼                        ▼
                               ┌──────────────┐                       ┌──────────────┐         ┌─────────────┐
                               │  CloudWatch  │                       │  CloudWatch  │         │  S3 Bucket  │
                               │    Logs      │                       │    Logs      │         │ model.tar.gz│
                               └──────────────┘                       └──────────────┘         └─────────────┘
```

**Request flow:** Client → ALB → ECS Fargate (Streamlit) → API Gateway `/v1` → Lambda (FastAPI + Mangum) → preprocesses 19 raw features into 46-feature CSV vector → SageMaker XGBoost endpoint → churn probability.

## Infrastructure

All cloud resources defined in Terraform with 10 modules, S3-backed remote state, and a single AWS provider (`eu-central-1`). See [infra/README.md](infra/README.md) for full details.

| Module | Purpose |
|---|---|
| `iam` | SageMaker, ECS, and Lambda execution roles with least-privilege policies |
| `vpc` | VPC, public/private subnets, IGW, NAT gateways (one per AZ), route tables |
| `security-group` | Reusable security group with dynamic ingress/egress rules |
| `sagemaker-endpoint` | Model, serverless endpoint config, XGBoost inference endpoint |
| `lambda` | Container-image Lambda function, SageMaker invoke policy |
| `api-gateway` | HTTP API, Lambda proxy integration, `$default` catch-all route, auto-deploy stage |
| `alb` | Application Load Balancer, IP-based target group, HTTP listener |
| `ecs` | ECS cluster with Fargate + Fargate Spot capacity providers |
| `ecs-task-definition` | Fargate task definition, container health check, CloudWatch Logs |
| `ecs-service` | ECS service, ALB integration, deployment circuit breaker with rollback |

**State:** S3 backend (`teleco-churn-terraform-state`), SSE-S3 encryption, profile `teleco-churn-terraform`.

## Key Design Decisions

| Decision | Rationale |
|---|---|
| Lambda + API Gateway for prediction API | Decouples preprocessing from the UI; scales independently; avoids granting ECS tasks SageMaker permissions |
| Pure Python preprocessing (no sklearn/numpy) | Eliminates heavy ML dependencies from Lambda — cold starts ~1s vs ~10s, image ~200MB vs ~1.5GB |
| Serverless SageMaker endpoint | Scales to zero when idle — cost-optimized for demo/showcase workloads |
| ECS Fargate + ALB | Managed compute for Streamlit; ALB provides health checks and public HTTP access |
| Modular Terraform (10 modules) | Separates IAM, networking, compute, API, and ML concerns for clean diffs and review |
| `uv` with dependency groups | Deterministic lockfile installs; `--only-group {app,api}` keeps each container minimal |
| HTTP API (not REST API) | Lower latency/cost, auto-deploy stages, payload format 2.0 |
| SMOTE on training set only | Prevents data leakage; test set retains original class distribution |

## Tech Stack

| Layer | Technology |
|---|---|
| **IaC** | Terraform ~> 5.0, S3 remote state |
| **Compute** | ECS Fargate, Lambda (container image), SageMaker Serverless Inference |
| **Networking** | VPC, ALB, API Gateway (HTTP API), NAT gateways |
| **ML** | SageMaker XGBoost 1.7-1 (best F1: 0.627, AUC-ROC: 0.840 across 5 models evaluated) |
| **API** | FastAPI + Mangum, Pydantic validation, loguru logging |
| **Front-end** | Streamlit on ECS Fargate |
| **Containerization** | Docker, docker-compose, ECR |
| **Packaging** | uv + pyproject.toml + lockfile, dependency groups (`app`, `api`) |
| **Runtime** | Python 3.13 |

## Repository Structure

```
teleco-customer-churn-aws/
├── api/                        # FastAPI prediction API (Lambda)
│   ├── src/                    #   main.py, config.py, api_components/predict/
│   └── environment/            #   Dockerfile.lambda, Dockerfile.local
├── app/                        # Streamlit front-end (ECS Fargate)
│   ├── app.py, config.py      #   Entry point, settings
│   ├── predict.py, components.py  # API client, UI components
│   └── environment/            #   Dockerfile.ecs, Dockerfile.local
├── infra/terraform/            # Modular Terraform (10 modules)
│   ├── main.tf, variables.tf   #   Root module
│   ├── backend.tf, providers.tf
│   └── modules/                #   iam, vpc, security-group, sagemaker-endpoint,
│                               #   lambda, api-gateway, alb, ecs,
│                               #   ecs-task-definition, ecs-service
├── data/                       # Raw dataset + processed artifacts
├── notebooks/                  # EDA, preprocessing, model training (SageMaker)
├── scripts/                    # SageMaker Script Mode training scripts
├── docker-compose.yml          # Local dev: API (:8000) + Streamlit (:8501)
└── pyproject.toml              # Python >=3.12, dependency groups
```

## Getting Started

**Prerequisites:** AWS account, AWS CLI (profile: `teleco-churn-terraform`), Python >= 3.12, [uv](https://docs.astral.sh/uv/), Terraform, Docker.

```bash
# 1. Clone & install
git clone <repo-url> && cd teleco-customer-churn-aws
uv sync

# 2. Provision infrastructure
cd infra/terraform && terraform init && terraform apply && cd ../..

# 3. Train model (run notebooks in order on SageMaker or locally)

# 4. Build & push Lambda image to ECR
docker build -f api/environment/Dockerfile.lambda -t prediction-api .

# 5. Run locally
docker compose up -d    # API on :8000, Streamlit on :8501
```

See [app/README.md](app/README.md), [api/README.md](api/README.md), and [infra/README.md](infra/README.md) for component-specific documentation.

# Infrastructure

IaC for the Telco Customer Churn Prediction platform. All cloud resources are defined in Terraform with modular decomposition and S3-backed remote state.

## Directory Structure

```
infra/
└── terraform/
    ├── backend.tf                          # required_providers (AWS ~> 5.0), S3 remote state
    ├── main.tf                             # Root module entry point (empty — delegates to modules)
    ├── variables.tf                        # Root-level input variables (empty — defined per module)
    ├── providers.tf                        # AWS provider: eu-central-1, profile teleco-churn-terraform
    ├── terraform.tfvars                    # Deployment-specific values
    ├── .terraform.lock.hcl                 # Provider dependency lock file
    └── modules/
        ├── iam/
        │   └── main.tf                     # SageMaker execution role + S3 read policy
        └── sagemaker-endpoint/
            ├── main.tf                     # Model, endpoint config, real-time endpoint
            └── variables.tf                # default_region, model_data_uri
```

## Provisioned Resources

| Module | Resource | AWS Type | Key Config |
|---|---|---|---|
| `iam` | SageMaker execution role | `aws_iam_role` | Trust: `sagemaker.amazonaws.com` |
| `iam` | SageMaker full access | `aws_iam_role_policy_attachment` | `AmazonSageMakerFullAccess` |
| `iam` | S3 read access | `aws_iam_role_policy` | `s3:GetObject`, `s3:ListBucket` on data bucket |
| `sagemaker-endpoint` | XGBoost container image | `aws_sagemaker_prebuilt_ecr_image` (data) | `sagemaker-xgboost:1.7-1` |
| `sagemaker-endpoint` | Model | `aws_sagemaker_model` | Artifact from S3 (`model.tar.gz`) |
| `sagemaker-endpoint` | Endpoint config | `aws_sagemaker_endpoint_configuration` | `ml.m5.large` × 1, single variant |
| `sagemaker-endpoint` | Endpoint | `aws_sagemaker_endpoint` | Real-time inference |

## State Management

| Property | Value |
|---|---|
| Backend | S3 (`teleco-churn-terraform-state`) |
| State key | `global/s3/terraform.tfstate` |
| Encryption | SSE-S3 enabled |
| Locking | None (single-developer project) |
| AWS profile | `teleco-churn-terraform` |

## Architecture Decisions

| Decision | Rationale |
|---|---|
| **Modular layout** | Resources split into `iam/` and `sagemaker-endpoint/` modules for separation of concerns |
| **Single environment** | No multi-env (dev/staging/prod) overhead — single flat root |
| **S3 remote state** | Encrypted, durable state storage; no DynamoDB lock table (single developer) |
| **Named AWS profile** | Credential isolation via dedicated `teleco-churn-terraform` profile |
| **Prebuilt SageMaker image** | Uses AWS-managed XGBoost container (`1.7-1`) — no custom Docker build required |

## Usage

```bash
cd infra/terraform
terraform init          # Configure S3 backend, download providers
terraform plan          # Review planned changes
terraform apply         # Provision / update resources
terraform destroy       # Tear down all managed resources
```

## Naming Convention

All resources use prefix: `teleco-customer-churn-`

| Resource | Name |
|---|---|
| SageMaker Model | `teleco-customer-churn-xgboost-model` |
| Endpoint Config | `teleco-customer-churn-xgboost-endpoint-config` |
| Endpoint | `teleco-customer-churn-xgboost-endpoint` |
| IAM Role | `sagemaker-execution-role` |

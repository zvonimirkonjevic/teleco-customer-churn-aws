# Infrastructure

Infrastructure as Code (IaC) for the Telco Customer Churn Prediction platform.

## Structure

```
infra/
└── terraform/
    ├── backend.tf           # Required providers & S3 remote state backend
    ├── main.tf              # Core resource definitions (SageMaker, IAM)
    ├── variables.tf         # Input variables (region, model_data_uri)
    ├── outputs.tf           # Output values (currently empty)
    ├── providers.tf         # AWS provider alias & region configuration
    └── terraform.tfvars     # Variable values for this deployment
```

## Current Resources

| Resource | Description |
|---|---|
| **IAM Role** | SageMaker execution role with S3 read access |
| **SageMaker Model** | XGBoost model using prebuilt SageMaker container (v1.7-1) |
| **SageMaker Endpoint Config** | Production variant on `ml.m5.large` |
| **SageMaker Endpoint** | Real-time inference endpoint |

## Architecture Decisions

| Decision | Rationale |
|---|---|
| **Flat Terraform layout** | Single folder with all resources — simple project, no module overhead |
| **Single environment** | Simple project — one flat Terraform root, no multi-env overhead |
| **S3 remote state** | Encrypted state stored in `teleco-churn-terraform-state` S3 bucket |
| **Named AWS profile** | Uses `teleco-churn-terraform` profile for credential isolation |

## Usage

```bash
cd infra/terraform

# Initialize (first time — creates .terraform/ and downloads providers)
terraform init

# Preview changes
terraform plan

# Apply infrastructure
terraform apply

# Destroy (when done)
terraform destroy
```

## Naming Convention

All resources follow: `teleco-customer-churn-{resource}`  
Example: `teleco-customer-churn-xgboost-model`, `teleco-customer-churn-xgboost-endpoint`

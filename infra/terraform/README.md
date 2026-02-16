# Terraform

IaC root for the Telco Customer Churn platform. Uses a modular layout with S3-backed remote state.

## Layout

```
terraform/
├── backend.tf                          # required_providers + S3 remote state
├── main.tf                             # Root module (currently empty — all resources in modules)
├── variables.tf                        # Root-level variables (currently empty)
├── providers.tf                        # AWS provider alias (eu-central, profile: teleco-churn-terraform)
├── terraform.tfvars                    # Variable values for this deployment
└── modules/
    ├── iam/
    │   └── main.tf                     # SageMaker execution role + inline S3 read policy
    └── sagemaker-endpoint/
        ├── main.tf                     # Model, endpoint config, endpoint resources
        └── variables.tf                # default_region, model_data_uri
```

## Backend

| Setting | Value |
|---|---|
| Backend | `s3` |
| Bucket | `teleco-churn-terraform-state` |
| State key | `global/s3/terraform.tfstate` |
| Region | `eu-central-1` |
| Encryption | `true` (SSE-S3) |
| AWS profile | `teleco-churn-terraform` |
| Provider constraint | `hashicorp/aws ~> 5.0` |

## Modules

### `modules/iam`

Creates the SageMaker execution role with two attached policies:

| Resource | Type | Detail |
|---|---|---|
| `sagemaker_execution_role` | `aws_iam_role` | Trust policy: `sagemaker.amazonaws.com` |
| `sagemaker_full_access` | `aws_iam_role_policy_attachment` | `AmazonSageMakerFullAccess` managed policy |
| `s3_access` | `aws_iam_role_policy` | Inline — `s3:GetObject`, `s3:ListBucket` scoped to `zvonimir-teleco-customer-churn` bucket |

### `modules/sagemaker-endpoint`

Provisions the real-time inference stack:

| Resource | Type | Detail |
|---|---|---|
| `xgboost` | `aws_sagemaker_prebuilt_ecr_image` (data) | `sagemaker-xgboost:1.7-1` container image |
| `xgboost_model` | `aws_sagemaker_model` | Model artifact loaded from S3 (`model_data_uri`) |
| `xgboost_endpoint_config` | `aws_sagemaker_endpoint_configuration` | Single `AllTraffic` variant, `ml.m5.large`, 1 instance |
| `xgboost_endpoint` | `aws_sagemaker_endpoint` | Real-time endpoint: `teleco-customer-churn-xgboost-endpoint` |

**Variables:**

| Name | Type | Description |
|---|---|---|
| `default_region` | `string` | AWS region for ECR image lookup |
| `model_data_uri` | `string` | `s3://` URI to the trained XGBoost `model.tar.gz` |

## Usage

```bash
cd infra/terraform

terraform init          # Download providers, configure S3 backend
terraform plan          # Dry-run — review resource changes
terraform apply         # Provision resources
terraform destroy       # Tear down all managed resources
```

> **Note:** Requires the `teleco-churn-terraform` AWS CLI profile to be configured locally.

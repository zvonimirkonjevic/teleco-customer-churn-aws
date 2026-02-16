# Terraform

Terraform configuration for the Telco Churn platform.

## Files

| File | Purpose |
|---|---|
| `backend.tf` | Required providers (AWS ~> 5.0) and S3 remote state backend configuration |
| `main.tf` | Core resource definitions — SageMaker (model, endpoint config, endpoint) and IAM roles |
| `variables.tf` | Input variables (`default_region`, `model_data_uri`) |
| `outputs.tf` | Output values exported after apply (currently empty — will be populated as resources grow) |
| `providers.tf` | AWS provider alias and region configuration |
| `terraform.tfvars` | Concrete variable values for this deployment |

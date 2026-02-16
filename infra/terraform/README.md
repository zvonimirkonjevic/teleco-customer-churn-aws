# Terraform

Terraform configuration for the Telco Churn platform.

## Files

| File | Purpose |
|---|---|
| `main.tf` | Core resource definitions — all AWS resources (SageMaker, Lambda, API Gateway, S3, IAM, EC2, CodeBuild, CodePipeline) |
| `variables.tf` | Input variables with types, descriptions, and defaults (e.g., region, tags) |
| `outputs.tf` | Output values exported after apply (API URL, EC2 public IP, S3 bucket names, etc.) |
| `providers.tf` | AWS provider version constraints and region configuration |
| `terraform.tfvars` | Concrete variable values for this deployment |

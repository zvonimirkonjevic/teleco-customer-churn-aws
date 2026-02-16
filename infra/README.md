# Infrastructure

Infrastructure as Code (IaC) for the Telco Customer Churn Prediction platform.

## Structure

```
infra/
└── terraform/
    ├── main.tf              # Core resource definitions (all AWS resources)
    ├── variables.tf         # Input variables (region, tags, etc.)
    ├── outputs.tf           # Output values (API URL, instance ID, bucket names, etc.)
    ├── providers.tf         # Provider configurations (AWS provider & version constraints)
    └── terraform.tfvars     # Variable values for this deployment
```

## Architecture Decisions

| Decision | Rationale |
|---|---|
| **Flat Terraform layout** | Single folder with all resources — simple project, no module overhead |
| **Single environment** | Simple project — one flat Terraform root, no multi-env overhead |
| **CodeBuild + CodeDeploy** | AWS-native CI/CD — no external dependencies, IAM-integrated |
| **EC2 for app** | Cost-effective for a single Streamlit app; managed via CodeDeploy agent |

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

All resources follow: `telco-churn-{service}-{resource}`  
Example: `telco-churn-sagemaker-endpoint`, `telco-churn-app-ec2`

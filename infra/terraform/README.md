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
    ├── vpc/
    │   ├── main.tf                     # VPC, subnets, IGW, NAT gateways, route tables
    │   └── variables.tf                # CIDR blocks, AZs, naming
    ├── security-group/
    │   ├── main.tf                     # Security group with dynamic ingress/egress rules
    │   ├── variables.tf                # Name, VPC ID, rule definitions
    │   └── outputs.tf                  # security_group_id
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

### `modules/vpc`

Provisions the network layer: VPC, subnets, internet gateway, NAT gateways, and route tables. Private subnets reach the internet via NAT gateways placed in public subnets.

| Resource | Type | Detail |
|---|---|---|
| `teleco-customer-churn-vpc` | `aws_vpc` | DNS support & hostnames enabled |
| `teleco-customer-churn-public-subnet` | `aws_subnet` | One per AZ |
| `teleco-customer-churn-private-subnet` | `aws_subnet` | One per AZ |
| `teleco-customer-churn-internet-gateway` | `aws_internet_gateway` | Attached to VPC |
| `teleco-customer-churn-eip` | `aws_eip` | One per AZ, allocated for NAT gateways |
| `teleco-customer-churn-nat-gateway` | `aws_nat_gateway` | One per AZ in public subnets, enables private subnet outbound internet |
| `teleco-customer-churn-public-route-table` | `aws_route_table` | Routes `0.0.0.0/0` to internet gateway |
| `teleco-customer-churn-private-route-table` | `aws_route_table` | Routes `0.0.0.0/0` to NAT gateway |

**Variables:**

| Name | Type | Description |
|---|---|---|
| `availability_zones` | `list(string)` | Availability zones for subnet placement |
| `cidr_block` | `string` | VPC CIDR block |
| `instance_tenancy` | `string` | Instance tenancy (default: `default`) |
| `name` | `string` | Resource name prefix |
| `public_subnet_cidr_block` | `string` | CIDR block for public subnets |
| `private_subnet_cidr_block` | `string` | CIDR block for private subnets |
| `public_route_table_cidr_block` | `string` | CIDR block for public route table |
| `private_route_table_cidr_block` | `string` | CIDR block for private route table |

### `modules/security-group`

Reusable security group module with dynamic ingress and egress rules. Default egress allows all outbound traffic (`0.0.0.0/0`).

| Resource | Type | Detail |
|---|---|---|
| `teleco-customer-churn-security-group` | `aws_security_group` | Dynamic ingress/egress blocks from variable-defined rule lists |

**Variables:**

| Name | Type | Description |
|---|---|---|
| `name` | `string` | Security group name |
| `vpc_id` | `string` | VPC to attach the security group to |
| `vpc_cidr_block` | `string` | VPC CIDR block |
| `ingress_rules` | `list(object)` | Ingress rules: `from_port`, `to_port`, `protocol`, `cidr_blocks`, `security_groups` |
| `egress_rules` | `list(object)` | Egress rules: `from_port`, `to_port`, `protocol`, `cidr_blocks` (default: allow all) |

**Outputs:**

| Name | Description |
|---|---|
| `security_group_id` | ID of the created security group |

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

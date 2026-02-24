# Infrastructure

IaC for the Telco Customer Churn Prediction platform. All cloud resources are defined in Terraform with modular decomposition and S3-backed remote state.

## Directory Structure

```
infra/
└── terraform/
    ├── backend.tf                          # required_providers (AWS ~> 5.0), S3 remote state
    ├── main.tf                             # Root module entry point — delegates to modules
    ├── variables.tf                        # Root-level input variables
    ├── providers.tf                        # AWS provider: eu-central-1, profile teleco-churn-terraform
    ├── terraform.tfvars                    # Deployment-specific values
    ├── .terraform.lock.hcl                 # Provider dependency lock file
    └── modules/
        ├── iam/                            # SageMaker + ECS + Lambda IAM roles and policies
        │   ├── main.tf
        │   ├── variables.tf
        │   └── outputs.tf
        ├── vpc/                            # VPC, subnets, IGW, NAT gateways, route tables
        │   ├── main.tf
        │   ├── variables.tf
        │   └── outputs.tf
        ├── security-group/                 # Reusable security group with dynamic rules
        │   ├── main.tf
        │   ├── variables.tf
        │   └── outputs.tf
        ├── sagemaker-endpoint/             # Model, serverless endpoint config, endpoint
        │   ├── main.tf
        │   ├── variables.tf
        │   └── outputs.tf
        ├── lambda/                         # Lambda function (container image), SageMaker invoke policy
        │   ├── main.tf
        │   ├── variables.tf
        │   └── outputs.tf
        ├── api-gateway/                    # HTTP API, Lambda integration, stage, permissions
        │   ├── main.tf
        │   ├── variables.tf
        │   └── outputs.tf
        ├── alb/                            # Application Load Balancer, target group, listener
        │   ├── main.tf
        │   ├── variables.tf
        │   └── outputs.tf
        ├── ecs/                            # ECS cluster, capacity providers
        │   ├── main.tf
        │   ├── variables.tf
        │   └── outputs.tf
        ├── ecs-task-definition/            # Fargate task definition, container config, logs
        │   ├── main.tf
        │   ├── variables.tf
        │   └── outputs.tf
        └── ecs-service/                    # ECS service, ALB integration, circuit breaker
            ├── main.tf
            ├── variables.tf
            └── outputs.tf
```

## Provisioned Resources

| Module | Resource | AWS Type | Key Config |
|---|---|---|---|
| `iam` | SageMaker execution role | `aws_iam_role` | Trust: `sagemaker.amazonaws.com` |
| `iam` | SageMaker full access | `aws_iam_role_policy_attachment` | `AmazonSageMakerFullAccess` |
| `iam` | S3 read access | `aws_iam_role_policy` | `s3:GetObject`, `s3:ListBucket` on data bucket |
| `iam` | ECS execution role | `aws_iam_role` | Trust: `ecs-tasks.amazonaws.com`; `AmazonECSTaskExecutionRolePolicy` |
| `iam` | ECS task role | `aws_iam_role` | Trust: `ecs-tasks.amazonaws.com`; custom inline policies |
| `iam` | Lambda execution role | `aws_iam_role` | Trust: `lambda.amazonaws.com`; CloudWatch Logs + ECR pull |
| `iam` | CloudWatch policy | `aws_iam_role_policy_attachment` | `CloudWatchLogsFullAccess` (conditional) |
| `iam` | SSM policy | `aws_iam_role_policy_attachment` | `AmazonSSMReadOnlyAccess` (conditional) |
| `sagemaker-endpoint` | XGBoost container image | `aws_sagemaker_prebuilt_ecr_image` (data) | `sagemaker-xgboost:1.7-1` |
| `sagemaker-endpoint` | Model | `aws_sagemaker_model` | Artifact from S3 (`model.tar.gz`) |
| `sagemaker-endpoint` | Endpoint config | `aws_sagemaker_endpoint_configuration` | Serverless: `max_concurrency`, `memory_size_in_mb` |
| `sagemaker-endpoint` | Endpoint | `aws_sagemaker_endpoint` | Serverless inference |
| `lambda` | SageMaker invoke policy | `aws_iam_role_policy` | `sagemaker:InvokeEndpoint` scoped to endpoint ARN |
| `lambda` | Lambda function | `aws_lambda_function` | Container image from ECR, 1024MB memory, 30s timeout |
| `api-gateway` | HTTP API | `aws_apigatewayv2_api` | Protocol: HTTP |
| `api-gateway` | Lambda integration | `aws_apigatewayv2_integration` | AWS_PROXY, payload format 2.0 |
| `api-gateway` | Default route | `aws_apigatewayv2_route` | `$default` catch-all (FastAPI handles routing) |
| `api-gateway` | Stage | `aws_apigatewayv2_stage` | `/v1`, auto-deploy enabled |
| `api-gateway` | Lambda permission | `aws_lambda_permission` | Allows API Gateway to invoke Lambda |
| `vpc` | VPC | `aws_vpc` | DNS support & hostnames enabled |
| `vpc` | Public subnets | `aws_subnet` | One per AZ |
| `vpc` | Private subnets | `aws_subnet` | One per AZ |
| `vpc` | Internet gateway | `aws_internet_gateway` | Attached to VPC |
| `vpc` | Elastic IPs | `aws_eip` | One per AZ, for NAT gateways |
| `vpc` | NAT gateways | `aws_nat_gateway` | One per AZ in public subnets, enables private subnet outbound internet |
| `vpc` | Public route tables | `aws_route_table` | Routes to internet gateway |
| `vpc` | Private route tables | `aws_route_table` | Routes to NAT gateway |
| `vpc` | Route table associations | `aws_route_table_association` | Links subnets to route tables |
| `security-group` | Security group | `aws_security_group` | Dynamic ingress/egress rules, default egress allows all outbound |
| `alb` | Load balancer | `aws_lb` | Application type, public subnets, idle timeout 60s |
| `alb` | Target group | `aws_lb_target_group` | IP target type, HTTP health check on `/_stcore/health` |
| `alb` | Listener | `aws_lb_listener` | Port 80 HTTP, forwards to target group |
| `ecs` | Cluster | `aws_ecs_cluster` | Container Insights enabled |
| `ecs` | Capacity providers | `aws_ecs_cluster_capacity_providers` | FARGATE + FARGATE_SPOT with weighted strategy |
| `ecs-task-definition` | Task definition | `aws_ecs_task_definition` | Fargate, `awsvpc`, health check, CloudWatch Logs, `API_ENDPOINT` env var from API Gateway output |
| `ecs-service` | Service | `aws_ecs_service` | Fargate launch, private subnets, ALB integration, circuit breaker with rollback |

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
| **Modular layout** | 10 modules separating IAM, networking, compute, API, and ML concerns for clean diffs and code review |
| **Lambda + API Gateway** | Decouples preprocessing/prediction API from the Streamlit UI; scales independently; avoids giving ECS tasks SageMaker permissions |
| **HTTP API (not REST API)** | Lower latency and cost than REST API; auto-deploy stages; payload format 2.0 |
| **`$default` catch-all route** | FastAPI handles all routing internally via Mangum — no need to duplicate route definitions in API Gateway |
| **ECS Fargate** | Managed serverless compute for running the Streamlit container — no EC2 instances to manage |
| **ALB** | Public HTTP entry point with health checks; routes traffic to ECS tasks in private subnets |
| **Serverless SageMaker endpoint** | Cost-optimized for showcase/demo — scales to zero when idle |
| **Single environment** | No multi-env (dev/staging/prod) overhead — single flat root |
| **S3 remote state** | Encrypted, durable state storage; no DynamoDB lock table (single developer) |
| **Named AWS profile** | Credential isolation via dedicated `teleco-churn-terraform` profile |
| **Prebuilt SageMaker image** | Uses AWS-managed XGBoost container (`1.7-1`) — no custom Docker build required |
| **NAT gateway per AZ** | Each private subnet gets its own NAT gateway for outbound internet — avoids single-AZ bottleneck |
| **Deployment circuit breaker** | ECS service automatically rolls back failed deployments |

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
| Lambda Function | `teleco-customer-churn-prediction-api` |
| API Gateway | `teleco-customer-churn-prediction-api` |
| IAM Roles | `teleco-customer-churn-{sagemaker-execution,ecs-execution,ecs-task,lambda-execution}-role` |
| ALB | `teleco-customer-churn-alb` |
| ECS Cluster | `teleco-customer-churn-cluster` |
| ECS Service | `teleco-customer-churn-service` |

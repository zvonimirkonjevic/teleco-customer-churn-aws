# Terraform

IaC root for the Telco Customer Churn platform. Uses a modular layout with S3-backed remote state.

## Layout

```
terraform/
├── backend.tf                          # required_providers + S3 remote state
├── main.tf                             # Root module — orchestrates all modules
├── variables.tf                        # Root-level variables
├── providers.tf                        # AWS provider alias (eu-central, profile: teleco-churn-terraform)
├── terraform.tfvars                    # Variable values for this deployment
└── modules/
    ├── iam/                            # SageMaker + ECS + Lambda IAM roles and policies
    │   ├── main.tf
    │   ├── variables.tf
    │   └── outputs.tf
    ├── vpc/                            # VPC, subnets, IGW, NAT gateways, route tables
    │   ├── main.tf
    │   ├── variables.tf
    │   └── outputs.tf
    ├── security-group/                 # Security group with dynamic ingress/egress rules
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

Creates IAM roles for SageMaker, ECS, and Lambda with configurable policy attachments.

| Resource | Type | Detail |
|---|---|---|
| `sagemaker_execution_role` | `aws_iam_role` | Trust policy: `sagemaker.amazonaws.com` |
| `sagemaker_full_access` | `aws_iam_role_policy_attachment` | `AmazonSageMakerFullAccess` managed policy |
| `s3_access` | `aws_iam_role_policy` | Inline — `s3:GetObject`, `s3:ListBucket` scoped to data bucket |
| `ecs_execution` | `aws_iam_role` | Trust policy: `ecs-tasks.amazonaws.com` |
| `ecs_execution_policy` | `aws_iam_role_policy_attachment` | `AmazonECSTaskExecutionRolePolicy` managed policy |
| `logs_policy` | `aws_iam_role_policy_attachment` | `CloudWatchLogsFullAccess` (conditional) |
| `ssm_policy` | `aws_iam_role_policy_attachment` | `AmazonSSMReadOnlyAccess` (conditional) |
| `ecs_task_role` | `aws_iam_role` | Trust policy: `ecs-tasks.amazonaws.com` |
| `custom_task_access` | `aws_iam_role_policy` | Custom inline policy for task role (conditional) |
| `custom_execution_access` | `aws_iam_role_policy` | Custom inline policy for execution role (conditional) |

**Variables:**

| Name | Type | Description |
|---|---|---|
| `name_prefix` | `string` | Prefix for role naming |
| `s3_bucket_name` | `string` | S3 bucket for SageMaker access |
| `attach_cloudwatch_policy` | `bool` | Attach CloudWatchLogsFullAccess (default: `false`) |
| `attach_ssm_policy` | `bool` | Attach AmazonSSMReadOnlyAccess (default: `false`) |
| `create_custom_task_policy` | `bool` | Create custom task role policy (default: `false`) |
| `custom_task_policy_json` | `string` | Custom task role policy JSON (default: `""`) |
| `create_custom_execution_policy` | `bool` | Create custom execution role policy (default: `false`) |
| `custom_execution_policy_json` | `string` | Custom execution role policy JSON (default: `""`) |

**Outputs:**

| Name | Description |
|---|---|
| `sagemaker_execution_role_iam_arn` | ARN of the SageMaker execution role |
| `ecs_execution_role_arn` | ARN of the ECS execution role |
| `ecs_task_role_arn` | ARN of the ECS task role |
| `ecs_execution_role_name` | Name of the ECS execution role |
| `ecs_task_role_name` | Name of the ECS task role |
| `lambda_execution_role_arn` | ARN of the Lambda execution role |
| `lambda_execution_role_name` | Name of the Lambda execution role |

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

**Outputs:**

| Name | Description |
|---|---|
| `vpc_id` | VPC ID |
| `public_subnet_ids` | List of public subnet IDs |
| `private_subnet_ids` | List of private subnet IDs |
| `internet_gateway_id` | Internet gateway ID |

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

Provisions the serverless inference stack:

| Resource | Type | Detail |
|---|---|---|
| `xgboost` | `aws_sagemaker_prebuilt_ecr_image` (data) | `sagemaker-xgboost:1.7-1` container image |
| `xgboost_model` | `aws_sagemaker_model` | Model artifact loaded from S3 (`model_data_uri`) |
| `xgboost_endpoint_config` | `aws_sagemaker_endpoint_configuration` | Single `AllTraffic` variant, serverless config (`max_concurrency`, `memory_size_in_mb`) |
| `xgboost_endpoint` | `aws_sagemaker_endpoint` | Serverless endpoint: `teleco-customer-churn-xgboost-endpoint` |

**Variables:**

| Name | Type | Description |
|---|---|---|
| `default_region` | `string` | AWS region for ECR image lookup |
| `model_data_uri` | `string` | `s3://` URI to the trained XGBoost `model.tar.gz` |
| `max_concurrency` | `number` | Maximum concurrent invocations for the serverless endpoint |
| `memory_size_in_mb` | `number` | Memory size in MB for the serverless endpoint |
| `iam_role_arn` | `string` | IAM role ARN for SageMaker execution |

**Outputs:**

| Name | Description |
|---|---|
| `sagemaker_endpoint_name` | Name of the SageMaker endpoint |
| `sagemaker_endpoint_arn` | ARN of the SageMaker endpoint |

### `modules/lambda`

Lambda function deployed from a container image (ECR). Attaches a SageMaker invoke policy scoped to the endpoint ARN.

| Resource | Type | Detail |
|---|---|---|
| `sagemaker_invoke` | `aws_iam_role_policy` | Inline policy: `sagemaker:InvokeEndpoint` scoped to endpoint ARN |
| `prediction_api` | `aws_lambda_function` | Container image from ECR, configurable memory/timeout, env vars for endpoint name and churn threshold |

**Variables:**

| Name | Type | Description |
|---|---|---|
| `name_prefix` | `string` | Prefix for naming Lambda resources |
| `execution_role_arn` | `string` | ARN of the IAM execution role |
| `execution_role_name` | `string` | Name of the IAM execution role (for policy attachment) |
| `image_uri` | `string` | ECR image URI for the Lambda container |
| `sagemaker_endpoint_name` | `string` | SageMaker endpoint name (passed as env var) |
| `sagemaker_endpoint_arn` | `string` | SageMaker endpoint ARN (for invoke policy) |
| `churn_threshold` | `string` | Churn probability threshold (default: `"0.5"`) |
| `memory_size` | `number` | Lambda memory in MB (default: `256`) |
| `timeout` | `number` | Lambda timeout in seconds (default: `30`) |
| `environment` | `string` | Environment tag (default: `"dev"`) |

**Outputs:**

| Name | Description |
|---|---|
| `function_name` | Name of the Lambda function |
| `function_arn` | ARN of the Lambda function |
| `invoke_arn` | Invoke ARN for API Gateway integration |

### `modules/api-gateway`

HTTP API Gateway with Lambda proxy integration. Uses a `$default` catch-all route so FastAPI (via Mangum) handles all routing internally.

| Resource | Type | Detail |
|---|---|---|
| `prediction_api` | `aws_apigatewayv2_api` | HTTP protocol type |
| `lambda` | `aws_apigatewayv2_integration` | AWS_PROXY, payload format 2.0 |
| `default` | `aws_apigatewayv2_route` | `$default` catch-all route |
| `default` | `aws_apigatewayv2_stage` | Auto-deploy enabled, configurable stage name (default: `v1`) |
| `api_gateway` | `aws_lambda_permission` | Allows API Gateway to invoke the Lambda function |

**Variables:**

| Name | Type | Description |
|---|---|---|
| `name_prefix` | `string` | Prefix for naming API Gateway resources |
| `lambda_invoke_arn` | `string` | Invoke ARN of the Lambda function |
| `lambda_function_name` | `string` | Lambda function name (for invocation permission) |
| `stage_name` | `string` | Deployment stage name (default: `"v1"`) |
| `environment` | `string` | Environment tag (default: `"dev"`) |

**Outputs:**

| Name | Description |
|---|---|
| `api_endpoint` | Base URL of the API Gateway (includes stage path) |
| `api_id` | ID of the API Gateway |

### `modules/alb`

Application Load Balancer with HTTP listener and IP-based target group.

| Resource | Type | Detail |
|---|---|---|
| `teleco_customer_churn_alb` | `aws_lb` | Application type, public subnets, idle timeout 60s |
| `teleco_customer_churn_target_group` | `aws_lb_target_group` | IP target type, HTTP health check (path: `/_stcore/health`, interval: 30s, healthy: 2, unhealthy: 3) |
| `teleco_customer_churn_listener` | `aws_lb_listener` | Port 80 HTTP, forwards to target group |

**Variables:**

| Name | Type | Description |
|---|---|---|
| `name_prefix` | `string` | Prefix for naming resources |
| `public_subnet_ids` | `list(string)` | Public subnets for ALB placement |
| `security_group_ids` | `list(string)` | Security groups for ALB |
| `target_port` | `number` | Target group port (default: `80`) |
| `vpc_id` | `string` | VPC ID |
| `environment` | `string` | Environment tag (default: `dev`) |

**Outputs:**

| Name | Description |
|---|---|
| `alb_dns_name` | DNS name of the ALB |
| `target_group_arn` | ARN of the target group |

### `modules/ecs`

ECS cluster with Fargate capacity providers.

| Resource | Type | Detail |
|---|---|---|
| `teleco_customer_churn_cluster` | `aws_ecs_cluster` | Container Insights toggle via variable |
| `teleco_customer_churn_capacity_providers` | `aws_ecs_cluster_capacity_providers` | Dynamic capacity provider strategy (FARGATE, FARGATE_SPOT) |

**Variables:**

| Name | Type | Description |
|---|---|---|
| `name_prefix` | `string` | Prefix for naming ECS resources |
| `environment` | `string` | Environment tag |
| `enable_container_insights` | `bool` | Enable CloudWatch Container Insights (default: `false`) |
| `capacity_providers` | `list(string)` | Capacity providers to associate with the cluster |
| `default_capacity_provider_strategy` | `list(object)` | Default strategy: `capacity_provider`, `weight`, `base` |

**Outputs:**

| Name | Description |
|---|---|
| `cluster_id` | ID of the ECS cluster |

### `modules/ecs-task-definition`

Fargate task definition with container health check and CloudWatch Logs.

| Resource | Type | Detail |
|---|---|---|
| `teleco-customer-churn-prediction` | `aws_ecs_task_definition` | Fargate, `awsvpc` network mode, health check (`curl` on container port), `awslogs` log driver |

**Variables:**

| Name | Type | Description |
|---|---|---|
| `family_name` | `string` | Task family name |
| `cpu` | `number` | Task CPU units |
| `memory` | `number` | Task memory in MiB |
| `task_role_arn` | `string` | IAM task role ARN |
| `execution_role_arn` | `string` | IAM execution role ARN |
| `container_name` | `string` | Container name |
| `image` | `string` | Docker image URI |
| `container_cpu` | `number` | Container CPU units |
| `container_memory` | `number` | Container memory in MiB |
| `container_port` | `number` | Container port |
| `region` | `string` | AWS region for CloudWatch Logs |

**Outputs:**

| Name | Description |
|---|---|
| `task_definition_arn` | Full ARN of the task definition |
| `task_definition_family` | Task family name |
| `revision` | Task definition revision number |

### `modules/ecs-service`

ECS service with ALB integration, private subnet placement, and deployment circuit breaker.

| Resource | Type | Detail |
|---|---|---|
| `teleco-customer-churn-service` | `aws_ecs_service` | Fargate launch type, private subnets (no public IP), ALB target group, circuit breaker with rollback |

**Variables:**

| Name | Type | Description |
|---|---|---|
| `name_prefix` | `string` | Prefix for naming the service |
| `cluster_id` | `string` | ECS cluster ID |
| `task_definition_arn` | `string` | Task definition ARN |
| `private_subnet_ids` | `list(string)` | Private subnets for task placement |
| `security_group_ids` | `list(string)` | Security groups for tasks |
| `target_group_arn` | `string` | ALB target group ARN |
| `container_name` | `string` | Container name for load balancer |
| `container_port` | `number` | Container port for load balancer |
| `desired_count` | `number` | Desired number of tasks |
| `force_new_deployment` | `bool` | Force new deployment (default: `false`) |
| `health_check_grace_period_seconds` | `number` | Health check grace period (default: `60`) |
| `environment` | `string` | Environment tag |

**Outputs:**

| Name | Description |
|---|---|
| `service_name` | Name of the ECS service |
| `service_id` | ID of the ECS service |
| `cluster_name` | Name of the ECS cluster |
| `launch_type` | Launch type (FARGATE) |

## Usage

```bash
cd infra/terraform

terraform init          # Download providers, configure S3 backend
terraform plan          # Dry-run — review resource changes
terraform apply         # Provision resources
terraform destroy       # Tear down all managed resources
```

> **Note:** Requires the `teleco-churn-terraform` AWS CLI profile to be configured locally.

# IAM configuration variables
name_prefix    = "teleco-customer-churn"
s3_bucket_name = "zvonimir-teleco-customer-churn"

# Sagemaker endpoint configuration variables
sagemaker_endpoint_default_region = "eu-central-1"
sagemaker_model_data_uri = "s3://zvonimir-teleco-customer-churn/models/xgboost/xgboost-260216-0910-011-9f99f443/output/model.tar.gz"
sagemaker_max_concurrency = 1
sagemaker_memory_size_in_mb = 2048

# VPC configuration variables
vpc_name = "teleco-customer-churn-vpc"
vpc_cidr_block = "10.0.0.0/16"
vpc_instance_tenancy = "default"
availability_zones = ["eu-central-1a", "eu-central-1b"]
public_subnet_cidr_block = "10.0.1.0/24"
private_subnet_cidr_block = "10.0.2.0/24"
public_route_table_cidr_block = "0.0.0.0/0"
private_route_table_cidr_block = "0.0.0.0/0"

# ALB SG configuration variables
alb_sg_name = "teleco-customer-churn-alb-sg"
alb_sg_ingress_from_port = 80
alb_sg_ingress_to_port = 80
alb_sg_ingress_protocol = "tcp"
alb_sg_ingress_cidr_blocks = ["0.0.0.0/0"]

# ECS Task SG configuration variables
ecs_task_sg_name = "teleco-customer-churn-ecs-task-sg"
ecs_task_sg_ingress_protocol = "tcp"
container_port = 80

# ECS Task Definition configuration variables
container_name   = "teleco-customer-churn"
container_cpu    = 256
container_memory = 512
container_image  = "PLACEHOLDER_IMAGE_URI"
region           = "eu-central-1"

# ECS Service configuration variables
desired_count    = 1
environment      = "dev"
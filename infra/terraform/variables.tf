# IAM configuration variables
variable "name_prefix" {
  description = "Prefix for naming IAM roles"
  type        = string
}

variable "s3_bucket_name" {
  description = "Name of the S3 bucket for SageMaker access"
  type        = string
}

# SageMaker endpoint configuration variables
variable "sagemaker_endpoint_default_region" {
    description = "AWS region for resource deployment"
    type = string
}

variable "sagemaker_model_data_uri" {
    description = "S3 URI path to the trained machine learning model data"
    type = string
}

variable "sagemaker_max_concurrency" {
    description = "Maximum number of concurrent invocations for the SageMaker endpoint"
    type = number
}

variable "sagemaker_memory_size_in_mb" {
    description = "Memory size in MB for the SageMaker endpoint"
    type = number
}

# VPC configuration variables
variable "vpc_name" {
  description = "Name of the VPC"
  type = string
}

variable "vpc_cidr_block" {
  description = "CIDR block for the VPC"
  type = string
}

variable "vpc_instance_tenancy" {
  description = "Instance tenancy for the VPC"
  type = string
}

variable "availability_zones" {
  description = "List of availability zones for subnets"
  type = list(string)
}

variable "public_subnet_cidr_block" {
  description = "CIDR block for public subnets"
  type = string
}

variable "private_subnet_cidr_block" {
  description = "CIDR block for private subnets"
  type = string
}

variable "public_route_table_cidr_block" {
  description = "CIDR block for public route table"
  type = string
}

variable "private_route_table_cidr_block" {
  description = "CIDR block for private route table"
  type = string
}

# ALB Security group configuration variables
variable "alb_sg_name" {
  description = "Name of the ALB security group"
  type = string
}

variable "alb_sg_ingress_from_port" {
  description = "Starting port for ALB security group ingress rule"
  type = number
}

variable "alb_sg_ingress_to_port" {
  description = "Ending port for ALB security group ingress rule"
  type = number
}

variable "alb_sg_ingress_protocol" {
  description = "Protocol for ALB security group ingress rule"
  type = string
}

variable "alb_sg_ingress_cidr_blocks" {
  description = "CIDR blocks for ALB security group ingress rule"
  type = list(string)
}

# ECS Task Security group configuration variables
variable "ecs_task_sg_name" {
  description = "Name of the ECS task security group"
  type = string
}

variable "ecs_task_sg_ingress_protocol" {
  description = "Protocol for ECS task security group ingress rule"
  type = string
}

variable "container_port" {
  description = "Port the container listens on"
  type = number
  default = 5000
}

# ECS Cluster configuration variables
variable "enable_container_insights" {
  description = "Whether to enable Container Insights for the ECS cluster"
  type = bool
  default = true
}

variable "capacity_providers" {
  description = "List of capacity providers for the ECS cluster"
  type = list(string)
  default = ["FARGATE", "FARGATE_SPOT"] 
}

variable "default_capacity_provider_strategy" {
  description = "Default capacity provider strategy for the ECS cluster"
  type = list(object({
    capacity_provider = string
    weight            = number
    base              = number
  }))
  
  default = [
    {
      capacity_provider = "FARGATE"
      weight            = 1
      base              = 1
    }
  ]
}

# ECS Task Definition configuration variables
variable "container_name" {
  description = "Name of the container in the ECS task definition"
  type = string
}

variable "container_cpu" {
  description = "CPU units for the container in the ECS task definition"
  type = number
}

variable "container_memory" {
  description = "Memory in MiB for the container in the ECS task definition"
  type = number
}

variable "container_image" {
  description = "Docker image for the container in the ECS task definition"
  type = string
}

variable "region" {
  description = "AWS region where resources are deployed"
  type = string
}

# ECS Service configuration variables
variable "desired_count" {
  description = "Desired number of tasks in the ECS service"
  type = number
  default = 1
}

variable "environment" {
  description = "Environment name (e.g., dev, staging, prod)"
  type = string
  default = "dev"
}

# Lambda configuration variables
variable "lambda_image_uri" {
  description = "ECR image URI for the Lambda prediction API"
  type        = string
}
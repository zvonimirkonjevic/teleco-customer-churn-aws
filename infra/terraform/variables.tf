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
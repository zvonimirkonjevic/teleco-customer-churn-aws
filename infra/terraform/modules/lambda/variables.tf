variable "name_prefix" {
  description = "Prefix for naming Lambda resources"
  type        = string
}

variable "execution_role_arn" {
  description = "The ARN of the IAM execution role for the Lambda function"
  type        = string
}

variable "execution_role_name" {
  description = "The name of the IAM execution role for attaching policies"
  type        = string
}

variable "sagemaker_endpoint_arn" {
  description = "The ARN of the SageMaker endpoint for the invoke policy"
  type        = string
}

variable "image_uri" {
  description = "The ECR image URI for the Lambda function container"
  type        = string
}

variable "sagemaker_endpoint_name" {
  description = "The name of the SageMaker endpoint to invoke"
  type        = string
}

variable "aws_region" {
  description = "AWS region where resources are deployed"
  type        = string
}

variable "churn_threshold" {
  description = "Churn probability threshold (0-1) above which a customer is considered high risk"
  type        = string
  default     = "0.5"
}

variable "memory_size" {
  description = "Memory size in MB for the Lambda function"
  type        = number
  default     = 256
}

variable "timeout" {
  description = "Timeout in seconds for the Lambda function"
  type        = number
  default     = 30
}

variable "environment" {
  description = "Environment name (e.g., dev, staging, prod)"
  type        = string
  default     = "dev"
}

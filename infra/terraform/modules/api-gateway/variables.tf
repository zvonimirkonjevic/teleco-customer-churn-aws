variable "name_prefix" {
  description = "Prefix for naming API Gateway resources"
  type        = string
}

variable "lambda_invoke_arn" {
  description = "The invoke ARN of the Lambda function for integration"
  type        = string
}

variable "lambda_function_name" {
  description = "The name of the Lambda function for invocation permission"
  type        = string
}

variable "stage_name" {
  description = "The deployment stage name for the API Gateway"
  type        = string
  default     = "v1"
}

variable "environment" {
  description = "Environment name (e.g., dev, staging, prod)"
  type        = string
  default     = "dev"
}

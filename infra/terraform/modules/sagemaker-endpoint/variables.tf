variable "default_region" {
    type        = string
    description = "Default region where your infrastructure is in"
}

variable "model_data_uri" {
    type        = string
    description = "URI of the model data in S3"
}

variable "max_concurrency" {
    type        = number
    description = "Maximum number of concurrent invocations for the serverless endpoint" 
}

variable "memory_size_in_mb" {
    type        = number
    description = "Memory size in MB for the serverless endpoint"
}

variable "iam_role_arn" {
    type        = string
    description = "The ARN of the IAM role for SageMaker execution"
}

variable "name_prefix" {
    type        = string
    description = "Prefix for naming SageMaker resources"
    default     = "telco-customer-churn"
}

variable "xgboost_image_tag" {
    type        = string
    description = "The XGBoost container image tag (must match the version used for training)"
    default     = "1.7-1"
}
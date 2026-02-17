variable "default_region" {
    description = "AWS region for resource deployment"
    type = string
}

variable "model_data_uri" {
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
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
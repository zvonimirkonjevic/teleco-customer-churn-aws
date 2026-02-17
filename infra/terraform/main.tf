module "iam" {
    source = "./modules/iam"
}

module "sagemaker-serverless-endpoint" {
    source = "./modules/sagemaker-endpoint"
    
    default_region = var.default_region
    iam_role_arn = module.iam.sagemaker_execution_role_iam_arn
    model_data_uri = var.model_data_uri
    max_concurrency = var.sagemaker_max_concurrency
    memory_size_in_mb = var.sagemaker_memory_size_in_mb
}
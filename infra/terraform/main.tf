module "iam" {
    source = "./modules/iam"
}

module "sagemaker-serverless-endpoint" {
    source = "./modules/sagemaker-endpoint"
    
    default_region = "eu-central-1"
    iam_role_arn = module.iam.sagemaker_execution_role_iam_arn
    model_data_uri = "s3://zvonimir-teleco-customer-churn/models/xgboost/xgboost-260216-0910-011-9f99f443/output/model.tar.gz"
    max_concurrency = 1
    memory_size_in_mb = 2048
}
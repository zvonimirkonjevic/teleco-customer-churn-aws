module "iam" {
    source = "./modules/iam"
}

module "vpc" {
    source = "./modules/vpc"

    name = var.vpc_name
    cidr_block = var.vpc_cidr_block
    instance_tenancy = var.vpc_instance_tenancy
    availability_zones = var.availability_zones
    public_subnet_cidr_block = var.public_subnet_cidr_block
    private_subnet_cidr_block = var.private_subnet_cidr_block
    public_route_table_cidr_block = var.public_route_table_cidr_block
}

module "sagemaker-serverless-endpoint" {
    source = "./modules/sagemaker-endpoint"
    
    default_region = var.sagemaker_endpoint_default_region
    iam_role_arn = module.iam.sagemaker_execution_role_iam_arn
    model_data_uri = var.sagemaker_model_data_uri
    max_concurrency = var.sagemaker_max_concurrency
    memory_size_in_mb = var.sagemaker_memory_size_in_mb
}
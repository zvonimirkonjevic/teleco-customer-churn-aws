module "iam" {
    source = "./modules/iam"

    name_prefix    = var.name_prefix
    s3_bucket_name = var.s3_bucket_name
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
    private_route_table_cidr_block = var.private_route_table_cidr_block
}

module "sagemaker_serverless_endpoint" {
    source = "./modules/sagemaker-endpoint"
    
    default_region = var.sagemaker_endpoint_default_region
    iam_role_arn = module.iam.sagemaker_execution_role_iam_arn
    model_data_uri = var.sagemaker_model_data_uri
    max_concurrency = var.sagemaker_max_concurrency
    memory_size_in_mb = var.sagemaker_memory_size_in_mb
}

module "alb_sg" {
    source = "./modules/security-group"

    name = var.alb_sg_name
    vpc_id = module.vpc.vpc_id
    vpc_cidr_block = var.vpc_cidr_block

    ingress_rules = [
        {
            from_port = var.alb_sg_ingress_from_port
            to_port = var.alb_sg_ingress_to_port
            protocol = var.alb_sg_ingress_protocol
            cidr_blocks = var.alb_sg_ingress_cidr_blocks
        }
    ]

    # Default egress is already set to allow all outbound traffic
}

module "ecs-task-security-group" {
    source = "./modules/security-group"

    name = var.ecs_task_sg_name
    vpc_id = module.vpc.vpc_id
    vpc_cidr_block = var.vpc_cidr_block

    ingress_rules = [
        {
            from_port = var.container_port
            to_port = var.container_port
            protocol = var.ecs_task_sg_ingress_protocol
            cidr_blocks = []
            security_groups = [module.alb_sg.security_group_id]
        }
    ]

    # Default egress is already set to allow all outbound traffic
}
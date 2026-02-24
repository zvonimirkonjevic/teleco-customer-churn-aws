module "iam_roles" {
  source = "./modules/iam"

  name_prefix          = var.name_prefix
  s3_bucket_name       = var.s3_bucket_name

  attach_cloudwatch_policy = true
  attach_ssm_policy        = false
  create_custom_task_policy = true

  # Add custom policy for execution role
  create_custom_execution_policy = true
  custom_execution_policy_json = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogStreams"
        ],
        Effect   = "Allow",
        Resource = "*"
      },
      {
        Action = [
          "ecr:GetAuthorizationToken",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage"
        ],
        Effect   = "Allow",
        Resource = "*"
      }
    ]
  })

  custom_task_policy_json = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = [
          "s3:GetObject",
          "s3:ListBucket"
        ],
        Effect   = "Allow",
        Resource = [
          "arn:aws:s3:::${var.s3_bucket_name}",
          "arn:aws:s3:::${var.s3_bucket_name}/*"
        ]
      },
      {
        Action   = "execute-api:Invoke",
        Effect   = "Allow",
        Resource = "arn:aws:execute-api:${var.region}:*:${module.prediction_api_gateway.api_id}/*"
      }
    ]
  })
}

module "vpc" {
    source = "./modules/vpc"

    name = var.vpc_name
    cidr_block = var.vpc_cidr_block
    instance_tenancy = var.vpc_instance_tenancy
    availability_zones = var.availability_zones
    public_subnet_cidr_blocks = var.public_subnet_cidr_blocks
    private_subnet_cidr_blocks = var.private_subnet_cidr_blocks
    public_route_table_cidr_block = var.public_route_table_cidr_block
    private_route_table_cidr_block = var.private_route_table_cidr_block
}

module "sagemaker_serverless_endpoint" {
    source = "./modules/sagemaker-endpoint"

    name_prefix = var.name_prefix
    default_region = var.sagemaker_endpoint_default_region
    iam_role_arn = module.iam_roles.sagemaker_execution_role_iam_arn
    model_data_uri = var.sagemaker_model_data_uri
    max_concurrency = var.sagemaker_max_concurrency
    memory_size_in_mb = var.sagemaker_memory_size_in_mb
}

module "alb_sg" {
    source = "./modules/security-group"

    name = var.alb_sg_name
    vpc_id = module.vpc.vpc_id

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

module "ecs_sg" {
    source = "./modules/security-group"

    name = var.ecs_task_sg_name
    vpc_id = module.vpc.vpc_id

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

module "ecs" {
  source      = "./modules/ecs"
  name_prefix = var.name_prefix
  environment = var.environment

  enable_container_insights = true

  capacity_providers = ["FARGATE", "FARGATE_SPOT"]

  default_capacity_provider_strategy = [
    {
      capacity_provider = "FARGATE"
      weight            = 1
      base              = 1
    }
  ]
}

module "ecs_task_definition" {
  source             = "./modules/ecs-task-definition"

  family_name        = var.container_name
  cpu                = var.container_cpu
  memory             = var.container_memory
  container_cpu      = var.container_cpu
  container_memory   = var.container_memory
  container_name     = var.container_name
  image              = var.container_image
  container_port     = var.container_port
  region             = var.region

  execution_role_arn = module.iam_roles.ecs_execution_role_arn
  task_role_arn      = module.iam_roles.ecs_task_role_arn

  environment_variables = [
    {
      name  = "API_ENDPOINT"
      value = module.prediction_api_gateway.api_endpoint
    }
  ]
}

module "ecs_service" {
  source                         = "./modules/ecs-service"

  name_prefix                    = var.name_prefix
  cluster_id                     = module.ecs.cluster_id
  task_definition_arn           = module.ecs_task_definition.task_definition_arn
  desired_count                 = var.desired_count
  target_group_arn              = module.alb.target_group_arn
  container_name                = var.container_name
  container_port                = var.container_port

  force_new_deployment              = true
  health_check_grace_period_seconds = 180

  private_subnet_ids            = module.vpc.private_subnet_ids
  security_group_ids            = [module.ecs_sg.security_group_id]
  environment                   = var.environment
}

module "alb" {
  source = "./modules/alb"

  name_prefix = var.name_prefix
  vpc_id = module.vpc.vpc_id
  public_subnet_ids = module.vpc.public_subnet_ids
  security_group_ids = [module.alb_sg.security_group_id]
  target_port       = var.container_port
  health_check_path = "/_stcore/health"
  environment       = var.environment
}

module "prediction_api_lambda" {
  source = "./modules/lambda"

  name_prefix             = var.name_prefix
  execution_role_arn      = module.iam_roles.lambda_execution_role_arn
  execution_role_name     = module.iam_roles.lambda_execution_role_name
  image_uri               = var.lambda_image_uri
  sagemaker_endpoint_name = module.sagemaker_serverless_endpoint.sagemaker_endpoint_name
  sagemaker_endpoint_arn  = module.sagemaker_serverless_endpoint.sagemaker_endpoint_arn
  memory_size             = 1024
  timeout                 = 30
  environment             = var.environment
}

module "prediction_api_gateway" {
  source = "./modules/api-gateway"

  name_prefix          = var.name_prefix
  lambda_invoke_arn    = module.prediction_api_lambda.invoke_arn
  lambda_function_name = module.prediction_api_lambda.function_name
  stage_name           = "v1"
  environment          = var.environment
}

data "aws_sagemaker_prebuilt_ecr_image" "xgboost" {
  region = var.default_region
  repository_name = "sagemaker-xgboost"
  image_tag = var.xgboost_image_tag
}

resource "aws_sagemaker_model" "xgboost_model" {
  name = "teleco-customer-churn-xgboost-model"
  execution_role_arn = var.iam_role_arn

  primary_container {
    image = data.aws_sagemaker_prebuilt_ecr_image.xgboost.registry_path
    model_data_url = var.model_data_uri
  }
}

resource "aws_sagemaker_endpoint_configuration" "xgboost_endpoint_config" {
    name = "teleco-customer-churn-xgboost-endpoint-config"

    production_variants {
      variant_name = "AllTraffic"
      model_name = aws_sagemaker_model.xgboost_model.name
      # serverless configuration for cost optimization, intended for showcase purpose.
      serverless_config {
        max_concurrency = var.max_concurrency
        memory_size_in_mb = var.memory_size_in_mb
      }
    }
}

resource "aws_sagemaker_endpoint" "xgboost_endpoint" {
    name = "teleco-customer-churn-xgboost-endpoint"
    endpoint_config_name = aws_sagemaker_endpoint_configuration.xgboost_endpoint_config.name
}
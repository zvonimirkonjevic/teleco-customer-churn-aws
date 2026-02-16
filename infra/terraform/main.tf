# SageMaker prebuilt XGBoost image
data "aws_sagemaker_prebuilt_ecr_image" "xgboost" {
  region = var.default_region
  repository_name = "xgboost"
  image_tag = "latest"
}

# Create IAM role for SageMaker
resource "aws_iam_role" "sagemaker_execution_role" {
  name = "sagemaker-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "sagemaker.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "sagemaker_full_access" {
  role       = aws_iam_role.sagemaker_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSageMakerFullAccess"
}

resource "aws_iam_role_policy" "s3_access" {
  name = "sagemaker-s3-access"
  role = aws_iam_role.sagemaker_execution_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = ["s3:GetObject", "s3:ListBucket"]
      Resource = [
        "arn:aws:s3:::zvonimir-teleco-customer-churn",
        "arn:aws:s3:::zvonimir-teleco-customer-churn/*"
      ]
    }]
  })
}

# Create SageMaker model
resource "aws_sagemaker_model" "xgboost_model" {
  name = "teleco-customer-churn-xgboost-model"
  execution_role_arn = aws_iam_role.sagemaker_execution_role.arn

  primary_container {
    image = data.aws_sagemaker_prebuilt_ecr_image.xgboost.image_uri
    model_data_url = var.model_data_uri
  }
}

# Create SageMaker endpoint configuration
resource "aws_sagemaker_endpoint_configuration" "xgboost_endpoint_config" {
    name = "teleco-customer-churn-xgboost-endpoint-config"

    production_variants {
      variant_name = "AllTrafic"
      model_name = aws_sagemaker_model.xgboost_model
      initial_instance_count = 1
      instance_type = "ml.m5.large"
    }
}

# Create SageMaker endpoint
resource "aws_sagemaker_endpoint" "xgboost_endpoint" {
    name = "teleco-customer-churn-xgboost-endpoint"
    endpoint_config_name = aws_sagemaker_endpoint_configuration.xgboost_endpoint_config.name
}
# Lambda Function
resource "aws_lambda_function" "prediction_api" {
  function_name = "${var.name_prefix}-prediction-api"
  role          = var.execution_role_arn
  package_type  = "Image"
  image_uri     = var.image_uri
  memory_size   = var.memory_size
  timeout       = var.timeout

  environment {
    variables = {
      SAGEMAKER_ENDPOINT_NAME = var.sagemaker_endpoint_name
      AWS_REGION              = var.aws_region
      CHURN_THRESHOLD         = var.churn_threshold
    }
  }

  tags = {
    Name        = "${var.name_prefix}-prediction-api"
    Environment = var.environment
  }
}

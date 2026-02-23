# SageMaker invoke policy for Lambda execution role
resource "aws_iam_role_policy" "sagemaker_invoke" {
  name = "${var.name_prefix}-lambda-sagemaker-invoke"
  role = var.execution_role_name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["sagemaker:InvokeEndpoint"]
      Resource = var.sagemaker_endpoint_arn
    }]
  })
}

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

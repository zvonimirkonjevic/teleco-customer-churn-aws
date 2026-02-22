# HTTP API Gateway
resource "aws_apigatewayv2_api" "prediction_api" {
  name          = "${var.name_prefix}-prediction-api"
  protocol_type = "HTTP"

  tags = {
    Name        = "${var.name_prefix}-prediction-api"
    Environment = var.environment
  }
}

# Lambda integration
resource "aws_apigatewayv2_integration" "lambda" {
  api_id                 = aws_apigatewayv2_api.prediction_api.id
  integration_type       = "AWS_PROXY"
  integration_uri        = var.lambda_invoke_arn
  integration_method     = "POST"
  payload_format_version = "2.0"
}

# Catch-all route — FastAPI handles routing internally
resource "aws_apigatewayv2_route" "default" {
  api_id    = aws_apigatewayv2_api.prediction_api.id
  route_key = "$default"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

# Deployment stage
resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.prediction_api.id
  name        = var.stage_name
  auto_deploy = true
}

# Allow API Gateway to invoke the Lambda function
resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = var.lambda_function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.prediction_api.execution_arn}/*/*"
}

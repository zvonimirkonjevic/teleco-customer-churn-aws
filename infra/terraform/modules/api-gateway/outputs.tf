output "api_endpoint" {
  description = "The base URL of the API Gateway"
  value       = "${aws_apigatewayv2_api.prediction_api.api_endpoint}/${var.stage_name}"
}

output "api_id" {
  description = "The ID of the API Gateway"
  value       = aws_apigatewayv2_api.prediction_api.id
}

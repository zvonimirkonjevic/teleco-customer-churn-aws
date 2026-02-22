output "function_name" {
  description = "The name of the Lambda function"
  value       = aws_lambda_function.prediction_api.function_name
}

output "function_arn" {
  description = "The ARN of the Lambda function"
  value       = aws_lambda_function.prediction_api.arn
}

output "invoke_arn" {
  description = "The invoke ARN of the Lambda function for API Gateway integration"
  value       = aws_lambda_function.prediction_api.invoke_arn
}

output "sagemaker_endpoint_name" {
  description = "The name of the SageMaker endpoint."
  value       = aws_sagemaker_endpoint.xgboost_endpoint.name
}

output "sagemaker_endpoint_arn" {
  description = "The ARN of the SageMaker endpoint."
  value       = aws_sagemaker_endpoint.xgboost_endpoint.arn
}
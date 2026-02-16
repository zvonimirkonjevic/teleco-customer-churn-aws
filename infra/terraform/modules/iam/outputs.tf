output "sagemaker_execution_role_iam_arn" {
    description = "The ARN of the IAM role for SageMaker execution."
    value = aws_iam_role.sagemaker_execution_role.arn
}
output "sagemaker_execution_role_iam_arn" {
    description = "The ARN of the IAM role for SageMaker execution."
    value = aws_iam_role.sagemaker_execution_role.arn
}

output "ecs_execution_role_arn" {
  value = aws_iam_role.ecs_execution.arn
}

output "ecs_task_role_arn" {
  value = aws_iam_role.ecs_task_role.arn
}

output "ecs_execution_role_name" {
  value = aws_iam_role.ecs_execution.name
}

output "ecs_task_role_name" {
  value = aws_iam_role.ecs_task_role.name
}
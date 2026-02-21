variable "name_prefix" {
  description = "The name prefix for the ECS service"
  type        = string
}

variable "cluster_id" {
  description = "The ID of the ECS cluster"
  type        = string
}

variable "task_definition_arn" {
  description = "The ARN of the ECS task definition"
  type        = string
}

variable "private_subnet_ids" {
  description = "The list of private subnet IDs"
  type        = list(string)
}

variable "security_group_ids" {
  description = "The list of security group IDs"
  type        = list(string)
}

variable "target_group_arn" {
  description = "The ARN of the target group"
  type        = string
}

variable "container_name" {
  description = "The name of the container in the task definition"
  type        = string
}

variable "container_port" {
  description = "The port number of the container in the task definition"
  type        = number
}

variable "desired_count" {
  description = "The desired count of tasks in the service"
  type        = number
}

variable "force_new_deployment" {
  description = "Whether to force a new deployment of the service"
  type        = bool
  default = false
}

variable "health_check_grace_period_seconds" {
  description = "The grace period in seconds for health checks on tasks in the service"
  type        = number
  default = 60
}

variable "environment" {
  description = "Environment name (e.g., dev, staging, prod)"
  type        = string
}
variable "family_name" {
  description = "The name of the ECS task family"
  type        = string
}

variable "cpu" {
  description = "The CPU units for the task definition"
  type        = number
}

variable "memory" {
  description = "The memory in MiB for the task definition"
  type        = number
}

variable "task_role_arn" {
  description = "The ARN of the IAM role for the ECS task"
  type        = string
}

variable "execution_role_arn" {
  description = "The ARN of the IAM execution role for the ECS task"
  type        = string
}

variable "container_name" {
  description = "The name of the container in the ECS task definition"
  type        = string
}

variable "image" {
  description = "The Docker image for the container in the ECS task definition"
  type        = string
}

variable "container_cpu" {
  description = "The CPU units for the container in the ECS task definition"
  type        = number
}

variable "container_memory" {
  description = "The memory in MiB for the container in the ECS task definition"
  type        = number
}

variable "container_port" {
  description = "The port number for the container in the ECS task definition"
  type        = number
}

variable "region" {
  description = "The AWS region where resources are deployed"
  type        = string
}
variable "name_prefix" {
  description = "Prefix for naming resources"
  type        = string
}

variable "public_subnet_ids" {
    description = "List of public subnet IDs for the ALB"
    type        = list(string)  
}

variable "security_group_ids" {
    description = "List of security group IDs for the ALB"
    type        = list(string)  
}

variable "target_port" {
    description = "Port on which the target group will receive traffic"
    type        = number
}

variable "vpc_id" {
    description = "VPC ID where the ALB and target group will be created"
    type        = string
}

variable "environment" {
    description = "Environment tag for the resources (e.g., dev, staging, prod)"
    type        = string
}
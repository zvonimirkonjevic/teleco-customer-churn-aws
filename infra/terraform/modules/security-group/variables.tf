variable "name" {
    description = "The name of the security group."
    type        = string  
}

variable "vpc_id" {
    description = "The VPC ID for the security group."

    type        = string
}

variable "ingress_rules" {
    description = "The ingress rules for the security group."
    type        = list(object({
        from_port   = number
        to_port     = number
        protocol    = string
        cidr_blocks = optional(list(string), [])
        security_groups = optional(list(string), [])
    }))
    default = []
}

variable "egress_rules" {
    description = "The egress rules for the security group."
    type        = list(object({
        from_port   = number
        to_port     = number
        protocol    = string
        cidr_blocks = optional(list(string), [])
    }))
    default = [ {
      from_port = 0
      to_port = 0
      protocol = "-1"
      cidr_blocks = ["0.0.0.0/0"]
    } ]
}
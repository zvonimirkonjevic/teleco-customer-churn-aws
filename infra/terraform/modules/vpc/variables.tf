variable "cidr_block" {
    description = "The CIDR block for the VPC."
    type        = string
}

variable "instance_tenancy" {
    description = "The instance tenancy option for the VPC. Valid values are 'default' and 'dedicated'."
    type        = string
    default     = "default"
}

variable "name" {
    description = "The name of the VPC."
    type        = string
}

variable "public_subnet_cidr_block" {
    description = "The CIDR block for the public subnet."
    type        = string
}

variable "private_subnet_cidr_block" {
    description = "The CIDR block for the private subnet."
    type        = string
}
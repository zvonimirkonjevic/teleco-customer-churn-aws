resource "aws_vpc" "teleco-customer-churn-vpc" {
    cidr_block = var.cidr_block
    instance_tenancy = var.instance_tenancy
    enable_dns_support = true
    enable_dns_hostnames = true
    tags = {
        Name = "${var.name}-vpc"
    }
}
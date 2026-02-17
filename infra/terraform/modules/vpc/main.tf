resource "aws_vpc" "teleco-customer-churn-vpc" {
    cidr_block = var.cidr_block
    instance_tenancy = var.instance_tenancy
    enable_dns_support = true
    enable_dns_hostnames = true
    tags = {
        Name = "${var.name}-vpc"
    }
}

resource "aws_subnet" "teleco-customer-churn-public-subnet" {
    count = length(var.availability_zones)
    vpc_id = aws_vpc.teleco-customer-churn-vpc.id
    cidr_block = var.public_subnet_cidr_block
    availability_zone = var.availability_zones[count.index]
    tags = {
        Name = "${var.name}-public-subnet-${count.index + 1}"
    }
}

resource "aws_subnet" "teleco-customer-churn-private-subnet" {
    count = length(var.availability_zones)
    vpc_id = aws_vpc.teleco-customer-churn-vpc.id
    cidr_block = var.private_subnet_cidr_block
    availability_zone = var.availability_zones[count.index]
    tags = {
        Name = "${var.name}-private-subnet-${count.index + 1}"
    }
}

resource "aws_internet_gateway" "teleco-customer-churn-internet-gateway" {
    vpc_id = aws_vpc.teleco-customer-churn-vpc.id
    tags = {
        Name = "${var.name}-igw"
    }
}
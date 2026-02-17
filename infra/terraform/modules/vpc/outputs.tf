output "vpc_id" {
  value = aws_vpc.teleco-customer-churn-vpc.id
}

output "public_subnet_ids" {
  value = aws_subnet.teleco-customer-churn-public-subnet.*.id
}

output "private_subnet_ids" {
  value = aws_subnet.teleco-customer-churn-private-subnet.*.id
}

output "internet_gateway_id" {
  value = aws_internet_gateway.teleco-customer-churn-internet-gateway.id
}
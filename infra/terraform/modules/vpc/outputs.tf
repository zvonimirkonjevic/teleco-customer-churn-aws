output "vpc_id" {
  value = aws_vpc.telco-customer-churn-vpc.id
}

output "public_subnet_ids" {
  value = aws_subnet.telco-customer-churn-public-subnet.*.id
}

output "private_subnet_ids" {
  value = aws_subnet.telco-customer-churn-private-subnet.*.id
}

output "internet_gateway_id" {
  value = aws_internet_gateway.telco-customer-churn-internet-gateway.id
}
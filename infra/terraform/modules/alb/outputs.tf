output "alb_dns_name" {
  description = "The DNS name of the ALB"
  value = aws_lb.teleco_customer_churn_alb.dns_name
}

output "target_group_arn" {
  description = "The ARN of the target group"
  value = aws_lb_target_group.teleco_customer_churn_target_group.arn
}
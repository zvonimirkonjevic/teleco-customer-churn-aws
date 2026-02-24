output "cluster_id" {
  description = "ID of the ECS cluster"
  value       = aws_ecs_cluster.telco_customer_churn_cluster.id
}
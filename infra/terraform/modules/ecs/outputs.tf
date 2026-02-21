output "cluster_id" {
  description = "ID of the ECS cluster"
  value       = aws_ecs_cluster.teleco_customer_churn_cluster.id
}
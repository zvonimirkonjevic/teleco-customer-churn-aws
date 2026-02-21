resource "aws_ecs_service" "teleco-customer-churn-service" {
    name           = "${var.name_prefix}-service"
    cluster        = var.cluster_id
    task_definition = var.task_definition_arn
    launch_type   = "FARGATE"
    desired_count = var.desired_count
    force_new_deployment = var.force_new_deployment
    health_check_grace_period_seconds = var.health_check_grace_period_seconds

    network_configuration {
      subnets = var.private_subnet_ids
      security_groups = var.security_group_ids
      assign_public_ip = false
    }

    load_balancer {
      target_group_arn = var.target_group_arn
      container_name   = var.container_name
      container_port   = var.container_port
    }

    deployment_controller {
      type = "ECS"
    }

    deployment_circuit_breaker {
      enable = true
      rollback = true
    }

    tags = {
        Name = "${var.name_prefix}-ecs-service"
        Environment = var.environment
    }
}
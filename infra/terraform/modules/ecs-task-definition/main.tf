resource "aws_ecs_task_definition" "teleco-customer-churn-prediction" {
  family                   = var.family_name
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.cpu
  memory                   = var.memory
  network_mode             = "awsvpc"
  task_role_arn            = var.task_role_arn
  execution_role_arn       = var.execution_role_arn

  container_definitions = jsonencode([
    {
        name     = var.container_name
        image    = var.image
        cpu      = var.container_cpu
        memory   = var.container_memory
        essential = true
        portMappings = [
          {
            containerPort = var.container_port
            hostPort      = var.container_port
            protocol      = "tcp"
          }
        ],
        healthCheck = {
          command     = ["CMD-SHELL", "curl -f http://localhost:${var.container_port}/ || exit 1"]
          interval    = 30
          timeout     = 5
          retries     = 3
          startPeriod = 60
        },
        logConfiguration = {
          logDriver = "awslogs"
          options = {
            "awslogs-group"         = "/ecs/${var.family_name}"
            "awslogs-region"        = var.region
            "awslogs-stream-prefix" = "ecs"
          }
        }
    }
  ])
}
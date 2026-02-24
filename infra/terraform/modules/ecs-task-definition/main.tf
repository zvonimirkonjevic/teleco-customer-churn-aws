resource "aws_cloudwatch_log_group" "ecs" {
  name              = "/ecs/${var.family_name}"
  retention_in_days = 30
}

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
        environment = var.environment_variables
        portMappings = [
          {
            containerPort = var.container_port
            hostPort      = var.container_port
            protocol      = "tcp"
          }
        ],
        healthCheck = {
          command     = ["CMD-SHELL", "python -c \"import urllib.request; urllib.request.urlopen('http://localhost:${var.container_port}/_stcore/health')\" || exit 1"]
          interval    = 30
          timeout     = 5
          retries     = 3
          startPeriod = 180
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
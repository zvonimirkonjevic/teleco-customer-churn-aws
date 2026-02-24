resource "aws_lb" "telco_customer_churn_alb" {
    name               = "${var.name_prefix}-alb"
    load_balancer_type = "application"
    subnets            = var.public_subnet_ids
    security_groups    = var.security_group_ids
    idle_timeout       = 60
    
    tags = {
        Name        = "${var.name_prefix}-alb"
        Environment = var.environment
    }
  
}

resource "aws_lb_target_group" "telco_customer_churn_target_group" {
    name        = "${var.name_prefix}-tg"
    port        = var.target_port
    protocol    = "HTTP"
    vpc_id      = var.vpc_id
    target_type = "ip"

    health_check {
      path = var.health_check_path
      port = "traffic-port"
      protocol = "HTTP"
      interval = 30
      timeout = 5
      healthy_threshold = 2
      unhealthy_threshold = 3
      matcher = "200,302"
    }
}

resource "aws_lb_listener" "telco_customer_churn_listener" {
    load_balancer_arn = aws_lb.telco_customer_churn_alb.arn
    port              = 80
    protocol          = "HTTP"

    default_action {
        type             = "forward"
        target_group_arn = aws_lb_target_group.telco_customer_churn_target_group.arn
    }
}
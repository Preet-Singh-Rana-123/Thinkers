# ==============================================================================
# Thinkers Platform - Least-Privilege Security Groups
# As specified in Devops-Synopsis.pdf Section 5.1
# ==============================================================================

# 1. Application Load Balancer Security Group (Public facing)
resource "aws_security_group" "alb_sg" {
  name        = "thinkers-alb-sg-${var.environment}"
  description = "Allows inbound HTTP/HTTPS traffic to ALB"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "HTTP Public Access"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTPS Public Access"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "Outbound traffic to private app layer"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "thinkers-alb-sg-${var.environment}"
  }
}

# 2. Application Compute / Django Nodes Security Group (Private Subnets)
resource "aws_security_group" "app_sg" {
  name        = "thinkers-app-sg-${var.environment}"
  description = "Allows inbound traffic only from ALB and Bastion SSH"
  vpc_id      = aws_vpc.main.id

  # Port 8000 only from ALB Security Group
  ingress {
    description     = "Gunicorn/Django port from ALB"
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb_sg.id]
  }

  # Port 80 only from ALB Security Group (if Nginx runs on host)
  ingress {
    description     = "HTTP from ALB"
    from_port       = 80
    to_port         = 80
    protocol        = "tcp"
    security_groups = [aws_security_group.alb_sg.id]
  }

  # SSH Port 22 from VPC CIDR / Bastion
  ingress {
    description = "SSH from Bastion / VPC"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }

  egress {
    description = "Outbound traffic for package updates, DB, S3"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "thinkers-app-sg-${var.environment}"
  }
}

# 3. AWS RDS MySQL Security Group (Data Layer)
# MySQL port 3306 strictly restricted to application container security group
resource "aws_security_group" "rds_sg" {
  name        = "thinkers-rds-sg-${var.environment}"
  description = "Restricts MySQL 3306 strictly to application compute security group"
  vpc_id      = aws_vpc.main.id

  ingress {
    description     = "MySQL 3306 from Thinkers App Compute Nodes"
    from_port       = 3306
    to_port         = 3306
    protocol        = "tcp"
    security_groups = [aws_security_group.app_sg.id]
  }

  egress {
    description = "Outbound database responses"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "thinkers-rds-sg-${var.environment}"
  }
}

# 4. Monitoring & Telemetry Security Group (Prometheus & Grafana)
resource "aws_security_group" "monitoring_sg" {
  name        = "thinkers-monitoring-sg-${var.environment}"
  description = "Allows Prometheus metric scraping and Grafana dashboard UI"
  vpc_id      = aws_vpc.main.id

  ingress {
    description     = "Grafana UI Port"
    from_port       = 3000
    to_port         = 3000
    protocol        = "tcp"
    cidr_blocks     = [var.vpc_cidr]
    security_groups = [aws_security_group.alb_sg.id]
  }

  ingress {
    description = "Prometheus Server Port"
    from_port   = 9090
    to_port     = 9090
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }

  ingress {
    description = "Alertmanager Port"
    from_port   = 9093
    to_port     = 9093
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }

  egress {
    description = "Outbound telemetry scrape requests"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "thinkers-monitoring-sg-${var.environment}"
  }
}

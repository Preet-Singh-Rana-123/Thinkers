# ==============================================================================
# Thinkers Platform - AWS RDS MySQL 8.0 Data Layer
# Multi-AZ Managed Relational Database with KMS Storage Encryption & Snapshots
# ==============================================================================

# Private DB Subnet Group across the 2 Private Availability Zones
resource "aws_db_subnet_group" "rds_subnet_group" {
  name        = "thinkers-rds-subnet-group-${var.environment}"
  description = "Subnet group for Thinkers RDS MySQL instances across private subnets"
  subnet_ids  = aws_subnet.private[*].id

  tags = {
    Name = "thinkers-rds-subnet-group-${var.environment}"
  }
}

# MySQL 8.0 Parameter Group for UTF8MB4 & Strict SQL Modes
resource "aws_db_parameter_group" "mysql_params" {
  name   = "thinkers-mysql8-params-${var.environment}"
  family = "mysql8.0"

  parameter {
    name  = "character_set_server"
    value = "utf8mb4"
  }

  parameter {
    name  = "collation_server"
    value = "utf8mb4_unicode_ci"
  }

  parameter {
    name  = "sql_mode"
    value = "STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION"
  }

  tags = {
    Name = "thinkers-mysql-params-${var.environment}"
  }
}

# Primary Managed AWS RDS MySQL 8.0 Instance
resource "aws_db_instance" "mysql_primary" {
  identifier        = "thinkers-mysql-primary-${var.environment}"
  engine            = "mysql"
  engine_version    = "8.0"
  instance_class    = var.db_instance_class
  allocated_storage = var.db_allocated_storage
  storage_type      = "gp3"

  # Storage Encryption with AWS managed KMS key
  storage_encrypted = true

  # Multi-AZ Deployment with automated standby failover (Synopsis Diagram 2)
  multi_az = var.multi_az_db

  db_name  = var.db_name
  username = var.db_username
  password = var.db_password

  db_subnet_group_name   = aws_db_subnet_group.rds_subnet_group.name
  parameter_group_name   = aws_db_parameter_group.mysql_params.name
  vpc_security_group_ids = [aws_security_group.rds_sg.id]

  # Automated Daily Snapshots & 7-Day Retention
  backup_retention_period    = 7
  backup_window              = "03:00-04:00"
  maintenance_window         = "sun:04:30-sun:05:30"
  auto_minor_version_upgrade = true

  # Security & Access Controls
  publicly_accessible = false
  skip_final_snapshot = true
  deletion_protection = false

  tags = {
    Name = "thinkers-rds-mysql-primary-${var.environment}"
  }
}

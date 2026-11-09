# ==============================================================================
# Thinkers Platform - Terraform Input Variables
# ==============================================================================

variable "aws_region" {
  description = "AWS deployment region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Deployment environment name (production, staging, dev)"
  type        = string
  default     = "production"
}

variable "vpc_cidr" {
  description = "Base CIDR block for the Thinkers VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for the 2 public subnets (distinct AZs)"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for the 2 private subnets (distinct AZs)"
  type        = list(string)
  default     = ["10.0.10.0/24", "10.0.11.0/24"]
}

variable "availability_zones" {
  description = "Availability zones for multi-AZ high availability"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

# RDS Configuration
variable "db_instance_class" {
  description = "AWS RDS MySQL compute instance class"
  type        = string
  default     = "db.t3.medium"
}

variable "db_allocated_storage" {
  description = "Initial storage allocated for MySQL instance in GB"
  type        = number
  default     = 20
}

variable "db_name" {
  description = "Primary relational database name"
  type        = string
  default     = "thinkers_db"
}

variable "db_username" {
  description = "Master username for AWS RDS MySQL"
  type        = string
  default     = "thinkers_admin"
}

variable "db_password" {
  description = "Master password for AWS RDS MySQL"
  type        = string
  sensitive   = true
  default     = "ThinkersMasterPass2026!"
}

variable "multi_az_db" {
  description = "Enable Multi-AZ RDS MySQL deployment with standby replica"
  type        = bool
  default     = true
}

# Compute / ASG Configuration
variable "instance_type" {
  description = "EC2 instance type for Django compute nodes"
  type        = string
  default     = "t3.medium"
}

variable "asg_min_size" {
  description = "Minimum number of Django application instances in ASG"
  type        = number
  default     = 2
}

variable "asg_max_size" {
  description = "Maximum number of Django application instances in ASG"
  type        = number
  default     = 6
}

variable "asg_desired_capacity" {
  description = "Target desired number of Django application instances"
  type        = number
  default     = 2
}

variable "ssh_key_name" {
  description = "AWS EC2 Key Pair name for SSH bastion access"
  type        = string
  default     = ""
}

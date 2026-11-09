# ==============================================================================
# Thinkers Platform - Terraform Main Configuration
# Cloud Infrastructure as Code (IaC) - AWS
# As specified in Devops-Synopsis.pdf Section 4.2 & Section 5.1
# ==============================================================================

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.40"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "Thinkers"
      Environment = var.environment
      ManagedBy   = "Terraform"
      Owner       = "Preet Singh"
    }
  }
}

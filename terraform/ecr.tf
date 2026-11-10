# ==============================================================================
# Thinkers Platform - AWS Elastic Container Registry (ECR)
# Production Container Registry for Automated CI/CD Deployments
# ==============================================================================

resource "aws_ecr_repository" "app" {
  name                 = "thinkers-app"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "AES256"
  }

  tags = {
    Name        = "thinkers-app-ecr"
    Environment = var.environment
  }
}

resource "aws_ecr_lifecycle_policy" "app_lifecycle" {
  repository = aws_ecr_repository.app.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep last 10 images to optimize AWS storage costs"
        selection = {
          tagStatus   = "any"
          countType   = "imageCountMoreThan"
          countNumber = 10
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}

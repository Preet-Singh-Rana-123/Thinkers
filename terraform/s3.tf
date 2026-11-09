# ==============================================================================
# Thinkers Platform - Amazon S3 Object Storage & IAM Access Policies
# Encrypted bucket for static assets, user pitch PDFs, and media uploads
# ==============================================================================

# Unique S3 Bucket Name generator
resource "random_id" "bucket_suffix" {
  byte_length = 4
}

# S3 Bucket for Thinkers Static and Media Assets
resource "aws_s3_bucket" "assets" {
  bucket        = "thinkers-media-assets-${var.environment}-${random_id.bucket_suffix.hex}"
  force_destroy = true

  tags = {
    Name = "thinkers-media-assets-${var.environment}"
  }
}

# S3 Bucket Versioning for data protection
resource "aws_s3_bucket_versioning" "assets_versioning" {
  bucket = aws_s3_bucket.assets.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Server-Side Encryption (AES256)
resource "aws_s3_bucket_server_side_encryption_configuration" "assets_encryption" {
  bucket = aws_s3_bucket.assets.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Public Access Block (Strict Private Access)
resource "aws_s3_bucket_public_access_block" "assets_public_block" {
  bucket = aws_s3_bucket.assets.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# IAM Role for EC2 Compute Nodes & Containers to access S3
resource "aws_iam_role" "app_role" {
  name = "thinkers-app-ec2-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name = "thinkers-app-role-${var.environment}"
  }
}

# IAM Policy with Least-Privilege S3 Access for App
resource "aws_iam_policy" "s3_access_policy" {
  name        = "thinkers-s3-access-policy-${var.environment}"
  description = "Allows Thinkers application to read and write media objects"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.assets.arn,
          "${aws_s3_bucket.assets.arn}/*"
        ]
      }
    ]
  })
}

# Attach S3 Policy to IAM Role
resource "aws_iam_role_policy_attachment" "s3_attach" {
  role       = aws_iam_role.app_role.name
  policy_arn = aws_iam_policy.s3_access_policy.arn
}

# Attach CloudWatch Logs Policy to IAM Role
resource "aws_iam_role_policy_attachment" "cloudwatch_attach" {
  role       = aws_iam_role.app_role.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy"
}

# IAM Instance Profile for EC2 Instances
resource "aws_iam_instance_profile" "app_profile" {
  name = "thinkers-app-instance-profile-${var.environment}"
  role = aws_iam_role.app_role.name
}

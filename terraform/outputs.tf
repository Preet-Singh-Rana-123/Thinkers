# ==============================================================================
# Thinkers Platform - Terraform Outputs
# ==============================================================================

output "vpc_id" {
  description = "The ID of the Thinkers VPC"
  value       = aws_vpc.main.id
}

output "alb_dns_name" {
  description = "Public DNS name of the Application Load Balancer"
  value       = aws_lb.main.dns_name
}

output "application_url" {
  description = "Public URL to access the Thinkers platform"
  value       = "http://${aws_lb.main.dns_name}"
}

output "health_check_url" {
  description = "Health check URL for monitoring and smoke tests"
  value       = "http://${aws_lb.main.dns_name}/health/"
}

output "metrics_url" {
  description = "Prometheus metrics ingestion URL"
  value       = "http://${aws_lb.main.dns_name}/metrics"
}

output "rds_endpoint" {
  description = "AWS RDS MySQL endpoint address"
  value       = aws_db_instance.mysql_primary.address
}

output "rds_port" {
  description = "AWS RDS MySQL port"
  value       = aws_db_instance.mysql_primary.port
}

output "s3_bucket_name" {
  description = "Name of the S3 bucket for media and static assets"
  value       = aws_s3_bucket.assets.id
}

output "asg_name" {
  description = "Name of the Auto Scaling Group"
  value       = aws_autoscaling_group.app_asg.name
}

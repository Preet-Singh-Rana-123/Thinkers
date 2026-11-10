# ==============================================================================
# Thinkers Platform - Compute & Auto Scaling Group (EC2 / ASG)
# High Availability Multi-Node Compute Cluster across Private Subnets
# ==============================================================================

# Fetch latest Ubuntu 22.04 LTS AMI
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# User Data Cloud-Init Script: Bootstraps Docker & Runs Thinkers Container Stack
locals {
  user_data = <<-EOF
              #!/bin/bash
              set -ex

              # 0. Configure 2GB Swap Space to prevent memory spikes on t3.micro
              if ! [ -f /swapfile ]; then
                fallocate -l 2G /swapfile || dd if=/dev/zero of=/swapfile bs=1M count=2048
                chmod 600 /swapfile
                mkswap /swapfile
                swapon /swapfile
                echo '/swapfile none swap sw 0 0' >> /etc/fstab
              fi

              # 1. Update packages and install Docker & Docker Compose
              apt-get update -y
              apt-get install -y ca-certificates curl gnupg lsb-release git awscli

              mkdir -m 0755 -p /etc/apt/keyrings
              curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg

              echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

              apt-get update -y
              apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

              systemctl start docker
              systemctl enable docker

              # 2. Setup Thinkers App directory
              mkdir -p /opt/thinkers
              cd /opt/thinkers

              # Clone repository
              git clone https://github.com/Preet-Singh-Rana-123/Thinkers.git repo
              cp -r repo/* .
              rm -rf repo

              # 3. Write Production Environment Configuration
              cat << ENVFILE > .env
              DJANGO_SECRET_KEY=prod-thinkers-secret-key-$(openssl rand -hex 16)
              DJANGO_DEBUG=False
              ALLOWED_HOSTS=*
              CSRF_TRUSTED_ORIGINS=http://${aws_lb.main.dns_name},https://${aws_lb.main.dns_name}
              DB_HOST=${aws_db_instance.mysql_primary.address}
              DB_PORT=3306
              DB_NAME=${var.db_name}
              DB_USER=${var.db_username}
              DB_PASSWORD=${var.db_password}
              MYSQL_ROOT_PASSWORD=${var.db_password}
              MYSQL_DATABASE=${var.db_name}
              MYSQL_USER=${var.db_username}
              MYSQL_PASSWORD=${var.db_password}
              USE_S3=True
              AWS_STORAGE_BUCKET_NAME=${aws_s3_bucket.assets.id}
              AWS_S3_REGION_NAME=${var.aws_region}
              NGINX_PORT=80
              GRAFANA_PORT=3000
              MYSQL_HOST_PORT=3307
              ENVFILE

              # 4. Authenticate with AWS ECR, pull pre-built image and start containers
              aws ecr get-login-password --region ${var.aws_region} | docker login --username AWS --password-stdin ${aws_ecr_repository.app.repository_url} || true
              docker pull ${aws_ecr_repository.app.repository_url}:latest || true
              docker tag ${aws_ecr_repository.app.repository_url}:latest thinkers-web:latest || true
              docker compose up -d web nginx || docker compose up -d --build web nginx
              echo "Thinkers Compute Node Initialization Finished Successfully!"
              EOF
}

# EC2 Launch Template
resource "aws_launch_template" "app" {
  name_prefix   = "thinkers-lt-${var.environment}-"
  image_id      = data.aws_ami.ubuntu.id
  instance_type = var.instance_type
  key_name      = var.ssh_key_name != "" ? var.ssh_key_name : null

  iam_instance_profile {
    arn = aws_iam_instance_profile.app_profile.arn
  }

  network_interfaces {
    associate_public_ip_address = false
    security_groups             = [aws_security_group.app_sg.id]
  }

  block_device_mappings {
    device_name = "/dev/sda1"
    ebs {
      volume_size           = 20
      volume_type           = "gp3"
      delete_on_termination = true
    }
  }

  user_data = base64encode(local.user_data)

  tag_specifications {
    resource_type = "instance"
    tags = {
      Name = "thinkers-app-node-${var.environment}"
    }
  }

  lifecycle {
    create_before_destroy = true
  }
}

# Auto Scaling Group (spans 2 Private Subnets across 2 AZs)
resource "aws_autoscaling_group" "app_asg" {
  name_prefix         = "thinkers-asg-${var.environment}-"
  vpc_zone_identifier = aws_subnet.private[*].id
  target_group_arns   = [aws_lb_target_group.app_tg.arn]

  min_size         = var.asg_min_size
  max_size         = var.asg_max_size
  desired_capacity = var.asg_desired_capacity

  health_check_type         = "ELB"
  health_check_grace_period = 900

  launch_template {
    id      = aws_launch_template.app.id
    version = "$Latest"
  }

  instance_refresh {
    strategy = "Rolling"
    preferences {
      min_healthy_percentage = 50
    }
  }

  tag {
    key                 = "Name"
    value               = "thinkers-app-asg-node"
    propagate_at_launch = true
  }
}

# Dynamic Scaling Policy: Target Tracking on CPU Utilization (70%)
resource "aws_autoscaling_policy" "cpu_target_tracking" {
  name                   = "thinkers-cpu-target-tracking-${var.environment}"
  policy_type            = "TargetTrackingScaling"
  autoscaling_group_name = aws_autoscaling_group.app_asg.name

  target_tracking_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ASGAverageCPUUtilization"
    }
    target_value = 70.0
  }
}

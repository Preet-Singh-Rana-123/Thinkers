# 🚀 Thinkers Platform - Complete DevOps Deployment Guide

Based on the official architecture specification in **`Devops-Synopsis.pdf`**:
- **Project**: THINKERS: Cloud-Native Collaborative Platform for Entrepreneurs
- **Author**: Preet Singh (12308619, Section K2O2313, Roll 44, Lovely Professional University)
- **Target Stack**: Django 4.2+ (Python 3.11), Gunicorn, MySQL 8.0 / AWS RDS, Docker & Docker Compose, Terraform, Jenkins CI/CD, Prometheus & Grafana.

---

## 📋 Table of Contents
1. [Architecture Overview](#1-architecture-overview)
2. [Local Containerized Deployment (Docker Compose)](#2-local-containerized-deployment)
3. [AWS Cloud Infrastructure Provisioning (Terraform)](#3-aws-cloud-infrastructure-provisioning)
4. [Continuous Integration & Deployment (Jenkins CI/CD)](#4-continuous-integration--deployment)
5. [Monitoring & Telemetry Setup (Prometheus & Grafana)](#5-monitoring--telemetry-setup)
6. [Health Check & Verification](#6-health-check--verification)

---

## 1. Architecture Overview

### Diagram Breakdown (per Synopsis Section 4)
- **Local Development**: Developer -> VS Code -> Django Unit Tests / Local MySQL Docker / Docker Engine -> GitHub.
- **AWS Cloud (Diagram 2)**:
  - **Public Subnet**: Application Load Balancer (ALB) across 2 Availability Zones (`us-east-1a`, `us-east-1b`).
  - **Private App Subnet**: Thinkers Django EC2 / Containers behind dynamic Auto Scaling Group (ASG).
  - **Private Data Subnet**: AWS RDS MySQL 8.0 Primary with Multi-AZ automated replication.
  - **Object Storage**: Amazon S3 for media attachments, pitch PDFs, and static files.
  - **Monitoring**: Prometheus scraping `/metrics` (15s interval) and Grafana dashboards.

---

## 2. Local Containerized Deployment

Run the complete multi-tier stack locally using Docker Compose.

### Step 2.1: Configure Environment Variables
Copy the template configuration:
```bash
cp .env.example .env
```
Key settings in `.env`:
```ini
DJANGO_SECRET_KEY=thinkers-secret-key-prod-2026-safe
DJANGO_DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,web,nginx
DB_HOST=db
DB_NAME=thinkers_db
DB_USER=thinkers_user
DB_PASSWORD=thinkers_secure_pass_2026
```

### Step 2.2: Launch the Services
Start all 9 microservices and exporters in detached mode:
```bash
docker compose up -d --build
```

### Step 2.3: Check Service Health
```bash
docker compose ps
```
Services running:
| Container | Service | External Port | Internal Port | Description |
|---|---|---|---|---|
| `thinkers_web` | Django + Gunicorn | `8000` | `8000` | Application Server (3 workers) |
| `thinkers_db` | MySQL 8.0 | `3306` | `3306` | Relational Database |
| `thinkers_nginx` | Nginx Proxy | `80` | `80` | Reverse Proxy & Static Cache |
| `thinkers_prometheus`| Prometheus | `9090` | `9090` | Time-Series Metrics Ingestion |
| `thinkers_grafana` | Grafana | `3000` | `3000` | Real-time Observability Dashboards |
| `thinkers_alertmanager`| Alertmanager | `9093` | `9093` | Alert Dispatcher (Slack / Email) |
| `thinkers_node_exporter`| Node Exporter | `9100` | `9100` | Host Telemetry Exporter |
| `thinkers_cadvisor` | cAdvisor | `8080` | `8080` | Container Metrics Exporter |
| `thinkers_mysql_exporter`| MySQL Exporter | `9104` | `9104` | DB Performance Exporter |

---

## 3. AWS Cloud Infrastructure Provisioning (Terraform)

All AWS infrastructure is provisioned declaratively via HashiCorp Terraform under `terraform/`.

### Step 3.1: Initialize Terraform
```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
terraform init
```

### Step 3.2: Review Plan
```bash
terraform plan
```
This plans out:
- VPC with custom CIDR `10.0.0.0/16`
- 2 Public Subnets & 2 Private Subnets spanning 2 Availability Zones
- Internet Gateway & NAT Gateway
- Least-privilege Security Groups (ALB on 80/443; EC2 on 8000 from ALB; RDS 3306 from EC2)
- AWS RDS MySQL 8.0 Multi-AZ encrypted cluster
- S3 Bucket with AES256 server-side encryption and IAM instance profile
- Application Load Balancer with HTTP health checks at `/health/`
- EC2 Auto Scaling Group with CPU Target Tracking policy (70%)

### Step 3.3: Apply Infrastructure
```bash
terraform apply -auto-approve
```

Outputs will display:
```
alb_dns_name    = "thinkers-alb-production-123456789.us-east-1.elb.amazonaws.com"
application_url = "http://thinkers-alb-production-123456789.us-east-1.elb.amazonaws.com"
health_check_url= "http://thinkers-alb-production-123456789.us-east-1.elb.amazonaws.com/health/"
metrics_url     = "http://thinkers-alb-production-123456789.us-east-1.elb.amazonaws.com/metrics"
rds_endpoint    = "thinkers-mysql-primary.cxxxx.us-east-1.rds.amazonaws.com"
s3_bucket_name  = "thinkers-media-assets-production-xxxx"
```

---

## 4. Continuous Integration & Deployment (Jenkins CI/CD)

The CI/CD pipeline is codified in `Jenkinsfile` and implements the workflow in **Diagram 3**:
1. **Lint & Code Quality**: Flake8 & Black code formatting and syntax checks.
2. **Django Unit Tests**: Executes unit test suite (`python manage.py test core`).
3. **Terraform Infrastructure Check**: `terraform fmt -check`, `terraform validate`.
4. **Docker Image Build**: Builds production container with `python:3.11-slim`.
5. **Registry Push**: Pushes tagged images to Docker Hub / AWS ECR.
6. **Rolling Deployment**: Updates container instances without downtime via `scripts/deploy.sh`.
7. **Healthcheck & Telemetry Verification**: Executes `scripts/health_check.sh`.
8. **Notifications**: Alerts Slack (`#thinkers-deployments`) or email on success/failure.

---

## 5. Monitoring & Telemetry Setup (Prometheus & Grafana)

Prometheus scrapes metrics every **15 seconds** (per Synopsis Section 6.1):
- **Django Application Metrics**: `http://localhost:8000/metrics`
- **Host Metrics**: `http://localhost:9100/metrics`
- **Container Metrics**: `http://localhost:8080/metrics`
- **MySQL Metrics**: `http://localhost:9104/metrics`

### Accessing Dashboards
Open `http://localhost:3000` in your browser:
- **Default Username**: `admin`
- **Default Password**: `admin` (or configured `GF_SECURITY_ADMIN_PASSWORD`)

Pre-provisioned Dashboards:
1. **Application Performance Dashboard** (`thinkers-app-perf`):
   - HTTP 2xx, 4xx, and 5xx response rates
   - 95th-percentile response latency
   - Database query execution rates
   - HTTP 500 error rate gauge (SLA limit: 2%)
2. **Infrastructure Health Dashboard** (`thinkers-infra-health`):
   - CPU utilization per Docker container (SLA alert: > 85%)
   - Memory footprint per Docker container
   - MySQL active connection pools and slow query counters
   - Host memory saturation percentage

---

## 6. Health Check & Verification

Run the automated diagnostic suite:
```bash
./scripts/health_check.sh
```

Sample output:
```
==========================================================
 Running Thinkers Platform Health & Observability Check
==========================================================
[Test 1] Checking Django Health Endpoint (http://localhost:8000/health/)...  [PASSED]
[Test 2] Checking Prometheus Metrics Endpoint (http://localhost:8000/metrics)...  [PASSED]
[Test 3] Checking Nginx Ingress Proxy (http://localhost:80/health/)...  [PASSED]
==========================================================
 All core platform healthchecks PASSED!
```

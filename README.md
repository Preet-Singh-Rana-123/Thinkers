# 💡 Thinkers - Cloud-Native Collaborative Platform for Entrepreneurs

Thinkers is a modern, scalable online community platform designed for entrepreneurs, innovators, startup founders, and investors. Built with Django (Python 3.11) and MySQL 8.0, and deployed using modern cloud-native DevOps paradigms (Docker, Terraform, Jenkins, Prometheus, and Grafana).

---

## 🏗️ DevOps Architecture (per `Devops-Synopsis.pdf`)

- **Application Layer**: Django 4.2+ (Python 3.11) executed via multi-worker Gunicorn WSGI.
- **Database Layer**: MySQL 8.0 / AWS RDS Multi-AZ encrypted cluster.
- **Containerization**: Multi-stage lightweight Docker image (`python:3.11-slim`) orchestrated via Docker Compose.
- **Infrastructure as Code (IaC)**: HashiCorp Terraform configuration for AWS VPC, ALB, EC2/ASG, RDS, and S3.
- **Automated CI/CD**: Jenkins declarative pipeline for automated testing, Docker build/push, and rolling deployment.
- **Observability & Health Monitoring**: Pull-based Prometheus metrics scraping (15s interval) and real-time Grafana dashboards.

---

## ⚡ Quick Start (Local Docker Compose)

1. **Configure Environment**:
   ```bash
   cp .env.example .env
   ```

2. **Start the Platform Stack**:
   ```bash
   docker compose up -d --build
   ```

3. **Verify Health**:
   ```bash
   ./scripts/health_check.sh
   ```

4. **Access Endpoints**:
   - Web Platform: [http://localhost:8000](http://localhost:8000) (or port 80 via Nginx)
   - Health Check: [http://localhost:8000/health/](http://localhost:8000/health/)
   - Prometheus Metrics: [http://localhost:8000/metrics](http://localhost:8000/metrics)
   - Prometheus UI: [http://localhost:9090](http://localhost:9090)
   - Grafana Dashboards: [http://localhost:3000](http://localhost:3000) (User/Pass: `admin` / `admin`)
   - Alertmanager: [http://localhost:9093](http://localhost:9093)

---

## ☁️ Cloud Deployment (AWS via Terraform)

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform plan
terraform apply
```

See [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) for full AWS step-by-step instructions.

---

## 🛠️ Operations & Maintenance

- **Deployment Guide**: [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md)
- **Maintenance Runbook**: [docs/MAINTENANCE_RUNBOOK.md](docs/MAINTENANCE_RUNBOOK.md)
- **Database Backup**: `./scripts/backup_db.sh`
- **Database Restore**: `./scripts/restore_db.sh <backup_file>`
- **Log Rotation**: `./scripts/rotate_logs.sh`
- **Health Diagnostic**: `./scripts/health_check.sh`

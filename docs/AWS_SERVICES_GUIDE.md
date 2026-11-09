# ☁️ Thinkers Platform - AWS Cloud Architecture & Services Guide

This guide details how the **Thinkers** cloud-native platform is architected, provisioned, and managed on **Amazon Web Services (AWS)** as specified in **`Devops-Synopsis.pdf`** (Diagram 2 & Section 5.1).

---

## 🏛️ 1. AWS Architecture Breakdown (Synopsis Diagram 2)

```
                            [ End User / Entrepreneur ]
                                         │
                                   HTTPS: 443
                                         ▼
                 ┌─────────────────────────────────────────────────┐
                 │           AWS VPC (10.0.0.0/16)                 │
                 │                                                 │
                 │   [ Public Subnet 1 ]      [ Public Subnet 2 ]  │
                 │   ┌─────────────────┐      ┌─────────────────┐  │
                 │   │  AWS Application│      │ NAT Gateway     │  │
                 │   │  Load Balancer  │      │ & Bastion Host  │  │
                 │   │     (ALB)       │      │                 │  │
                 │   └────────┬────────┘      └─────────────────┘  │
                 │            │ Forward Traffic (:8000)            │
                 │            ▼                                    │
                 │   [ Private Subnet 1 ]     [ Private Subnet 2 ] │
                 │   ┌─────────────────┐      ┌─────────────────┐  │
                 │   │ Thinkers EC2/Pod│      │ Thinkers EC2/Pod│  │
                 │   │     Node 1      │      │     Node 2      │  │
                 │   │(Gunicorn:8000)  │      │(Gunicorn:8000)  │  │
                 │   └────────┬────────┘      └────────┬────────┘  │
                 │            │                        │           │
                 │            ├────────────────────────┤           │
                 │            │ Read / Write (:3306)   │           │
                 │            ▼                        ▼           │
                 │   [ AWS RDS MySQL Primary ] ──► [ RDS Standby ] │
                 │        (Multi-AZ)               (Replication)   │
                 └────────────┼────────────────────────────────────┘
                              │
                    IAM S3 API Requests
                              ▼
                 [ Amazon S3 Bucket ]
                 (Static & Media Assets)
```

---

## 🛠️ 2. AWS Services Implemented & Their Roles

| AWS Service | Configuration File | Purpose in Thinkers Platform |
|---|---|---|
| **Amazon VPC** | [`terraform/vpc.tf`](../terraform/vpc.tf) | Isolated network with CIDR `10.0.0.0/16`, 2 Public and 2 Private subnets across distinct Availability Zones (`us-east-1a`, `us-east-1b`). |
| **NAT Gateway & IGW** | [`terraform/vpc.tf`](../terraform/vpc.tf) | Internet Gateway for public ALB ingress; NAT Gateway with Elastic IP allowing private app nodes to pull packages and updates securely. |
| **Security Groups** | [`terraform/security_groups.tf`](../terraform/security_groups.tf) | Least-privilege firewall: ALB open on port 80/443; EC2 allows port 8000 **only** from ALB SG; RDS allows 3306 **strictly** from EC2 SG. |
| **Application Load Balancer (ALB)** | [`terraform/alb.tf`](../terraform/alb.tf) | Distributes incoming user traffic across EC2 nodes, runs automated health checks at `/health/` every 30s. |
| **Auto Scaling Group (ASG)** | [`terraform/ec2.tf`](../terraform/ec2.tf) | Manages multi-node high availability (min: 2, max: 6). Dynamically adds compute instances using CPU Target Tracking policy at 70%. |
| **Launch Template** | [`terraform/ec2.tf`](../terraform/ec2.tf) | Provisions Ubuntu 22.04 LTS compute nodes with automated cloud-init user data script that bootstraps Docker and the application stack. |
| **AWS RDS MySQL 8.0** | [`terraform/rds.tf`](../terraform/rds.tf) | Managed relational database with KMS storage encryption, automated daily snapshots (7-day retention), and Multi-AZ replication. |
| **Amazon S3** | [`terraform/s3.tf`](../terraform/s3.tf) | Encrypted (AES256) private object storage bucket for user media uploads, pitch PDFs, and static assets with versioning enabled. |
| **AWS IAM** | [`terraform/s3.tf`](../terraform/s3.tf) | Least-privilege IAM roles, policies, and instance profiles granting EC2 compute nodes restricted read/write access to S3 without hardcoded keys. |
| **Amazon CloudWatch** | [`terraform/ec2.tf`](../terraform/ec2.tf) | Collects EC2 metrics, CPU utilization, and system logs for operational alerting. |

---

## 🚀 3. How to Deploy to AWS via Terraform

### Step 3.1: Configure Variables
```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
```

*(Optional for Student / Free-Tier Cost Optimization)*:
Edit `terraform.tfvars`:
```hcl
db_instance_class    = "db.t3.micro"
instance_type        = "t3.micro"
asg_min_size         = 1
asg_desired_capacity = 1
multi_az_db          = false
```

### Step 3.2: Initialize & Validate
```bash
terraform init
terraform validate
```

### Step 3.3: Preview All 37 AWS Resources (Plan)
```bash
terraform plan
```
This shows all 37 resources ready to be created in your AWS account.

### Step 3.4: Apply Infrastructure (Provisioning)
```bash
terraform apply -auto-approve
```
Upon completion, Terraform prints the live outputs:
```
Outputs:

alb_dns_name     = "thinkers-alb-production-123456789.us-east-1.elb.amazonaws.com"
application_url  = "http://thinkers-alb-production-123456789.us-east-1.elb.amazonaws.com"
health_check_url = "http://thinkers-alb-production-123456789.us-east-1.elb.amazonaws.com/health/"
metrics_url      = "http://thinkers-alb-production-123456789.us-east-1.elb.amazonaws.com/metrics"
rds_endpoint     = "thinkers-mysql-primary.cxxxx.us-east-1.rds.amazonaws.com"
s3_bucket_name   = "thinkers-media-assets-production-xxxx"
```

---

## 🖥️ 4. What to Show in the AWS Management Console

When demonstrating to your professor/evaluator in the **AWS Console** (`https://console.aws.amazon.com/`):

1. **VPC Dashboard**:
   - Navigate to **VPC** → **Your VPCs**: Show `thinkers-vpc-production` with CIDR `10.0.0.0/16`.
   - Click **Subnets**: Show 2 Public subnets (`10.0.1.0/24`, `10.0.2.0/24`) and 2 Private subnets across distinct Availability Zones (`us-east-1a`, `us-east-1b`).
   - Click **NAT Gateways**: Show the active NAT Gateway routing private subnet traffic to the Internet.

2. **Security Groups**:
   - Show `thinkers-alb-sg`: Inbound HTTP port 80/443 open to `0.0.0.0/0`.
   - Show `thinkers-app-sg`: Inbound port 8000 restricted **only** to `thinkers-alb-sg`.
   - Show `thinkers-rds-sg`: Inbound MySQL port 3306 restricted **strictly** to `thinkers-app-sg`.

3. **EC2 & Auto Scaling Groups**:
   - Navigate to **EC2** → **Auto Scaling Groups**: Show `thinkers-asg-production` spanning both private subnets.
   - Click **Automatic Scaling**: Show the **Target Tracking Scaling Policy** set to scale up when average CPU exceeds 70%.

4. **Application Load Balancer (ALB)**:
   - Navigate to **EC2** → **Load Balancers**: Show `thinkers-alb-production`.
   - Navigate to **Target Groups**: Show `thinkers-app-tg` with Health check path `/health/` returning HTTP 200.

5. **Amazon RDS (MySQL 8.0)**:
   - Navigate to **RDS** → **Databases**: Show `thinkers-mysql-primary` running MySQL 8.0 with automated backups and KMS encryption.

6. **Amazon S3**:
   - Navigate to **S3**: Show the bucket `thinkers-media-assets-production-*` with **Block Public Access** ON (secure private storage accessed via IAM role).

---

## 🧹 5. Teardown / Cleanup (Avoid Unwanted AWS Charges)

When you have finished showing the AWS deployment to your evaluator:
```bash
cd terraform
terraform destroy -auto-approve
```
This safely deletes all 37 AWS resources, ensuring you incur zero ongoing charges!

# 🛠️ Thinkers Platform - Operations, Logging & Maintenance Runbook

Operational and maintenance procedures for the Thinkers cloud-native platform in production.

---

## 📋 Table of Contents
1. [Standard Operating Procedures (SOP)](#1-standard-operating-procedures-sop)
2. [Logging & Log Inspection](#2-logging--log-inspection)
3. [Database Backups & Disaster Recovery](#3-database-backups--disaster-recovery)
4. [Observability & Alert Triage Procedures](#4-observability--alert-triage-procedures)
5. [Routine Maintenance Tasks](#5-routine-maintenance-tasks)
6. [Emergency Rollback Procedure](#6-emergency-rollback-procedure)

---

## 1. Standard Operating Procedures (SOP)

### Maintenance Schedule
| Frequency | Activity | Tool / Script | Owner |
|---|---|---|---|
| **Continuous** | Real-time SLA & Error Rate Monitoring | Prometheus & Alertmanager | DevOps Lead |
| **Daily (03:00 UTC)** | Automated MySQL Database Backup | `scripts/backup_db.sh` | Automated Cron |
| **Daily (00:00 UTC)** | Log Rotation & Old Log Compression | `scripts/rotate_logs.sh` | Automated Cron |
| **Weekly** | Review Slow Query Logs & P95 Latency | Grafana Dashboards | Backend Team |
| **Monthly** | OS Security Patches & Dependency Updates | `Dockerfile` & Terraform | DevOps Lead |

---

## 2. Logging & Log Inspection

### 2.1 Log File Locations
All application logs are stored under the `/app/logs` volume (`./logs` locally):
- **`logs/thinkers.log`**: General application runtime logs, view queries, and info-level diagnostics.
- **`logs/error.log`**: Uncaught exceptions, HTTP 500 stack traces, and database connection failures.
- **`logs/archive/`**: Gzipped historical logs retained for 30 days.

### 2.2 Live Log Streaming
```bash
# View real-time Django logs in Docker
docker compose logs -f web

# Tail the structured error log
tail -f logs/error.log

# Grep for HTTP 500 errors in the last 24 hours
grep "ERROR" logs/error.log | head -n 50
```

### 2.3 Automated Log Rotation
Log rotation automatically archives files larger than 10MB (keeping 5 generations). To manually trigger or schedule rotation:
```bash
./scripts/rotate_logs.sh
```

To install as a daily midnight cron job:
```bash
crontab -e
# Add line:
0 0 * * * /path/to/Thinkers/scripts/rotate_logs.sh >> /var/log/thinkers_cron.log 2>&1
```

---

## 3. Database Backups & Disaster Recovery

### 3.1 Generating a Database Backup
Run the backup script:
```bash
./scripts/backup_db.sh
```
What it does:
1. Generates a compressed MySQL dump with timestamp `thinkers_db_backup_YYYYMMDD_HHMMSS.sql.gz`.
2. Verifies dump integrity.
3. Automatically prunes backups older than 14 days.
4. If `BACKUP_S3_BUCKET` is set, pushes a copy to AWS S3.

### 3.2 Restoring from a Backup
In the event of data corruption or disaster recovery:
```bash
./scripts/restore_db.sh /path/to/backup/thinkers_db_backup_YYYYMMDD_HHMMSS.sql.gz
```
Safety mechanism:
- The script automatically takes a snapshot of the current database state before applying any restore.

---

## 4. Observability & Alert Triage Procedures

The platform enforces the alerting rules defined in **`monitoring/prometheus/alert.rules.yml`**.

### 🚨 Alert 1: `Http500ErrorRateExceeded` (SLA: > 2%)
- **Threshold**: HTTP 5xx errors exceed 2% of total requests over 2 minutes.
- **Triage Steps**:
  1. Open Grafana: Navigate to **Application Performance Dashboard** (`http://localhost:3000`).
  2. Inspect the **HTTP 5xx (Server Errors)** timeseries panel to identify when the spike began.
  3. Inspect `logs/error.log` for the exact traceback:
     ```bash
     docker compose exec web tail -n 100 /app/logs/error.log
     ```
  4. Verify database connectivity:
     ```bash
     docker compose exec web python manage.py check --database default
     ```
  5. If caused by a faulty deployment, execute [Emergency Rollback](#6-emergency-rollback-procedure).

---

### 🚨 Alert 2: `ContainerCpuUsageExceeded85Percent`
- **Threshold**: Sustained container CPU > 85% for more than 5 minutes.
- **Triage Steps**:
  1. Open Grafana: Navigate to **Infrastructure Health Dashboard**.
  2. Identify which container is spiking (`thinkers_web`, `thinkers_db`, etc.).
  3. If `thinkers_web`:
     - Check active request load and slow endpoints in Grafana.
     - In AWS, the Auto Scaling Group (ASG) will dynamically add compute instances via the CPU Target Tracking policy (> 70%).
     - In Docker Compose, increase Gunicorn worker concurrency or scale web replicas:
       ```bash
       docker compose up -d --scale web=3
       ```
  4. If `thinkers_db`:
     - Inspect slow queries in MySQL Exporter:
       ```bash
       docker compose exec db mysql -u root -p -e "SHOW FULL PROCESSLIST;"
       ```

---

### 🚨 Alert 3: `MySQLConnectionPoolSaturated` (> 80%)
- **Threshold**: Active MySQL connection threads exceed 80% of `max_connections`.
- **Triage Steps**:
  1. Check open database connections:
     ```bash
     docker compose exec db mysql -u root -p -e "SHOW STATUS LIKE 'Threads_connected';"
     ```
  2. Check for leaking long-lived connections or blocking table locks.
  3. Adjust `max_connections` in `terraform/rds.tf` or `docker-compose.yml` if traffic has scaled.

---

## 5. Routine Maintenance Tasks

### Applying Database Migrations
When code changes include new Django models or schema updates:
```bash
docker compose exec web python manage.py migrate --noinput
```

### Collecting Static Assets
When stylesheets, JavaScript or images are modified:
```bash
docker compose exec web python manage.py collectstatic --noinput --clear
```

### Healthcheck Smoke Test
```bash
./scripts/health_check.sh
```

---

## 6. Emergency Rollback Procedure

If an unhealthy release passes CI or causes high failure rates:
1. Revert to the last known healthy Docker image tag:
   ```bash
   export IMAGE_TAG="previous_stable_build_number"
   docker compose up -d web
   ```
2. Verify application health:
   ```bash
   ./scripts/health_check.sh
   ```
3. If database migrations need reverting:
   ```bash
   docker compose exec web python manage.py migrate <app_name> <previous_migration_name>
   ```
4. Restore from the most recent safe database backup if data corruption occurred:
   ```bash
   ./scripts/restore_db.sh /path/to/latest_safe_backup.sql.gz
   ```

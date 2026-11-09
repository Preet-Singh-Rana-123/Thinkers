#!/usr/bin/env bash
# ==============================================================================
# Thinkers Platform - Database Restoration Script
# Safely restores a compressed MySQL dump with pre-restore safety snapshot
# ==============================================================================

set -eo pipefail

if [ -z "$1" ]; then
    echo "Usage: $0 <path-to-backup-file.sql.gz>"
    echo "Example: $0 /opt/thinkers/backups/thinkers_db_backup_20261109_120000.sql.gz"
    exit 1
fi

BACKUP_FILE="$1"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "Error: Backup file '$BACKUP_FILE' not found!"
    exit 1
fi

DB_HOST="${DB_HOST:-127.0.0.1}"
DB_PORT="${DB_PORT:-3306}"
DB_NAME="${DB_NAME:-thinkers_db}"
DB_USER="${DB_USER:-thinkers_user}"
DB_PASSWORD="${DB_PASSWORD:-thinkers_secure_pass_2026}"

echo "=========================================================="
echo " CAUTION: RESTORING THINKERS DATABASE"
echo " Database: ${DB_NAME} at ${DB_HOST}:${DB_PORT}"
echo " Source File: ${BACKUP_FILE}"
echo "=========================================================="

# 1. Take a Pre-Restoration Snapshot
SNAPSHOT_FILE="/tmp/pre_restore_snapshot_$(date +%s).sql.gz"
echo "[Safety Check] Creating pre-restore snapshot: ${SNAPSHOT_FILE}"
if command -v docker > /dev/null 2>&1 && docker inspect thinkers_db > /dev/null 2>&1; then
    docker exec thinkers_db mysqldump -u"$DB_USER" -p"$DB_PASSWORD" --no-tablespaces --single-transaction --quick "$DB_NAME" 2>/dev/null | gzip > "$SNAPSHOT_FILE" || true
elif command -v mysqldump > /dev/null 2>&1; then
    MYSQL_PWD="$DB_PASSWORD" mysqldump --host="$DB_HOST" --port="$DB_PORT" --user="$DB_USER" --no-tablespaces "$DB_NAME" 2>/dev/null | gzip > "$SNAPSHOT_FILE" || true
fi

# 2. Perform Restore
echo "[Restoring] Decompressing and importing SQL stream into MySQL..."
if command -v docker > /dev/null 2>&1 && docker inspect thinkers_db > /dev/null 2>&1; then
    gunzip -c "$BACKUP_FILE" | docker exec -i thinkers_db mysql -u"$DB_USER" -p"$DB_PASSWORD" "$DB_NAME"
elif command -v mysql > /dev/null 2>&1; then
    gunzip -c "$BACKUP_FILE" | MYSQL_PWD="$DB_PASSWORD" mysql --host="$DB_HOST" --port="$DB_PORT" --user="$DB_USER" "$DB_NAME"
else
    echo "Neither native mysql client nor running Docker container 'thinkers_db' detected."
    exit 1
fi

echo "=========================================================="
echo " Database restoration completed successfully!"
echo "=========================================================="

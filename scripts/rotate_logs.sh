#!/usr/bin/env bash
# ==============================================================================
# Thinkers Platform - Automated Log Rotation & Maintenance
# Archives, compresses and prunes application and error logs
# ==============================================================================

set -eo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOGS_DIR="${APP_DIR}/logs"
ARCHIVE_DIR="${LOGS_DIR}/archive"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
RETENTION_DAYS=30

mkdir -p "$ARCHIVE_DIR"

echo "=========================================================="
echo " Starting Thinkers Log Rotation: $(date)"
echo " Log Directory: ${LOGS_DIR}"
echo "=========================================================="

# Rotate and compress application log
for logfile in "thinkers.log" "error.log"; do
    TARGET_LOG="${LOGS_DIR}/${logfile}"
    if [ -f "$TARGET_LOG" ] && [ -s "$TARGET_LOG" ]; then
        ARCHIVE_DEST="${ARCHIVE_DIR}/${logfile%.*}_${TIMESTAMP}.log"
        echo "Archiving ${logfile} -> ${ARCHIVE_DEST}.gz"
        cp "$TARGET_LOG" "$ARCHIVE_DEST"
        : > "$TARGET_LOG" # Truncate active log file without restarting processes
        gzip -9 "$ARCHIVE_DEST"
    fi
done

# Prune archives older than RETENTION_DAYS
echo "Pruning compressed archives older than ${RETENTION_DAYS} days..."
find "$ARCHIVE_DIR" -name "*.log.gz" -type f -mtime +"$RETENTION_DAYS" -exec rm -f {} +

echo "=========================================================="
echo " Log rotation finished successfully!"
echo "=========================================================="

#!/bin/sh
set -e

echo "=========================================================="
echo " Starting Thinkers Container Initialization"
echo "=========================================================="

# 1. Wait for MySQL database if DB_HOST is configured
if [ -n "$DB_HOST" ]; then
    DB_PORT="${DB_PORT:-3306}"
    echo "[Info] Waiting for MySQL database at $DB_HOST:$DB_PORT..."
    max_retries=60
    count=0
    while ! nc -z "$DB_HOST" "$DB_PORT"; do
        count=$((count+1))
        if [ "$count" -ge "$max_retries" ]; then
            echo "[Error] Database connection timed out after $max_retries seconds."
            exit 1
        fi
        sleep 1
    done
    echo "[Success] Database is reachable!"
fi

# 2. Run Database Migrations
echo "[Info] Running Django database migrations..."
python manage.py migrate --noinput

# 3. Collect Static Files for Nginx / WhiteNoise
echo "[Info] Collecting static assets..."
python manage.py collectstatic --noinput --clear || true

echo "=========================================================="
echo " Thinkers Platform Ready - Executing Service Command"
echo "=========================================================="
exec "$@"

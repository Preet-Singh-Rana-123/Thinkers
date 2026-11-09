#!/usr/bin/env bash
# ==============================================================================
# Thinkers Platform - Health & Telemetry Verification Diagnostic
# Tests application health endpoint, database connectivity and Prometheus metrics
# ==============================================================================

set -eo pipefail

APP_HOST="${APP_HOST:-localhost}"
APP_PORT="${APP_PORT:-8000}"
NGINX_PORT="${NGINX_PORT:-80}"

echo "=========================================================="
echo " Running Thinkers Platform Health & Observability Check"
echo " Timestamp: $(date)"
echo "=========================================================="

FAILURES=0

# 1. Check /health/ endpoint on Django / Gunicorn
echo -n "[Test 1] Checking Django Health Endpoint (http://${APP_HOST}:${APP_PORT}/health/)... "
if curl -s -f "http://${APP_HOST}:${APP_PORT}/health/" | grep -q "healthy"; then
    echo " [PASSED]"
else
    echo " [FAILED / UNREACHABLE]"
    FAILURES=$((FAILURES + 1))
fi

# 2. Check /metrics endpoint for Prometheus
echo -n "[Test 2] Checking Prometheus Metrics Endpoint (http://${APP_HOST}:${APP_PORT}/metrics)... "
if curl -s -f "http://${APP_HOST}:${APP_PORT}/metrics" | grep -q "django_"; then
    echo " [PASSED]"
else
    echo " [FAILED / UNREACHABLE]"
    FAILURES=$((FAILURES + 1))
fi

# 3. Check Nginx Ingress if reachable
echo -n "[Test 3] Checking Nginx Ingress Proxy (http://${APP_HOST}:${NGINX_PORT}/health/)... "
if curl -s -f "http://${APP_HOST}:${NGINX_PORT}/health/" > /dev/null 2>&1; then
    echo " [PASSED]"
else
    echo " [SKIPPED / NGINX NOT ACTIVE ON PORT ${NGINX_PORT}]"
fi

# 4. Check Docker Containers Status if Docker is active
if command -v docker &> /dev/null && docker info > /dev/null 2>&1; then
    echo "[Test 4] Docker Container Runtime Status:"
    docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
fi

echo "=========================================================="
if [ "$FAILURES" -eq 0 ]; then
    echo " All core platform healthchecks PASSED!"
    exit 0
else
    echo " Total healthcheck failures: $FAILURES"
    exit 1
fi

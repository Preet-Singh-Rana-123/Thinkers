# syntax=docker/dockerfile:1
# ==============================================================================
# Thinkers Platform - Multi-Stage Production Dockerfile
# Base Image: python:3.11-slim (as specified in Synopsis Section 5.2)
# ==============================================================================

# ------------------------------------------------------------------------------
# Stage 1: Build Dependencies & Python Wheels
# ------------------------------------------------------------------------------
FROM python:3.11-slim AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# ------------------------------------------------------------------------------
# Stage 2: Minimal Production Runtime
# ------------------------------------------------------------------------------
FROM python:3.11-slim AS runner

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# Install runtime utilities (curl for healthchecks, netcat for DB readiness probe)
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-mysql-client \
    curl \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Install pre-built wheels from builder stage
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels

# Enforce least-privilege security: Run as non-root user
RUN addgroup --system django && adduser --system --ingroup django django

# Create runtime directories for static collection, media uploads, and logs
RUN mkdir -p /app/staticfiles /app/media /app/logs && \
    chown -R django:django /app

# Copy application code
COPY --chown=django:django . .

# Ensure entrypoint has executable permissions
RUN chmod +x /app/entrypoint.sh

USER django

EXPOSE 8000

# Container Healthcheck (matches ALB & Prometheus monitoring probe)
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD curl -f http://localhost:8000/health/ || exit 1

ENTRYPOINT ["/app/entrypoint.sh"]

# Multi-worker Gunicorn server as defined in Synopsis Section 5.2
CMD ["gunicorn", "--workers", "3", "--bind", "0.0.0.0:8000", "Thinkers.wsgi:application"]

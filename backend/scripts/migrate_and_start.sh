#!/bin/sh
# Spectra — Production Startup Script
# Runs Alembic migrations then starts Uvicorn.
# Used as the startCommand in render.yaml and docker-compose.prod.yml.
#
# Render sets $PORT automatically. Fallback to 8000 for local production testing.

set -e  # exit immediately if any command fails

echo "=== Spectra Production Startup ==="
echo "Environment: ${ENVIRONMENT:-production}"
echo "Port: ${PORT:-8000}"

echo ""
echo "--- Running Alembic migrations ---"
alembic upgrade head
echo "--- Migrations complete ---"

echo ""
echo "--- Starting Uvicorn ---"
exec uvicorn app.main:app \
  --host 0.0.0.0 \
  --port "${PORT:-8000}" \
  --workers 1 \
  --log-level "${LOG_LEVEL:-info}" \
  --no-access-log
# --no-access-log: we have StructuredLoggingMiddleware handling access logs

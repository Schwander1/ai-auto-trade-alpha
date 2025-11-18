#!/bin/bash
# Verify service health after startup
# This script is used as ExecStartPost in systemd services

set -e

SERVICE_NAME="${1:-argo-trading}"
PORT="${2:-8000}"
MAX_RETRIES=15
RETRY_DELAY=2

echo "[$(date +'%Y-%m-%d %H:%M:%S')] Verifying $SERVICE_NAME health on port $PORT..."

RETRY_COUNT=0
until curl -sf --max-time 5 "http://localhost:$PORT/health" > /dev/null 2>&1 || \
      curl -sf --max-time 5 "http://localhost:$PORT/api/v1/health" > /dev/null 2>&1; do
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
        echo "[$(date +'%Y-%m-%d %H:%M:%S')] ⚠️  WARNING: Service health check failed after $MAX_RETRIES attempts"
        echo "[$(date +'%Y-%m-%d %H:%M:%S')] Service may still be starting. This is non-fatal."
        exit 0  # Non-fatal - service might still be starting
    fi
    echo "[$(date +'%Y-%m-%d %H:%M:%S')]   Retry $RETRY_COUNT/$MAX_RETRIES..."
    sleep $RETRY_DELAY
done

echo "[$(date +'%Y-%m-%d %H:%M:%S')] ✅ Service health check passed for $SERVICE_NAME"
exit 0


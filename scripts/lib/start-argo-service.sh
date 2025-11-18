#!/bin/bash
# Production service startup wrapper with dependency checking
# This script starts Argo services with proper dependency management
# Usage: start-argo-service.sh <path> <port> <color> [log_file]

set -e

SERVICE_PATH="${1}"
SERVICE_PORT="${2}"
SERVICE_COLOR="${3:-argo}"
LOG_FILE="${4:-/tmp/argo-${SERVICE_COLOR}.log}"

if [ -z "$SERVICE_PATH" ] || [ -z "$SERVICE_PORT" ]; then
    echo "Usage: $0 <service_path> <port> <color> [log_file]"
    exit 1
fi

# Source dependency checking utilities if available
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
if [ -f "$WORKSPACE_DIR/scripts/lib/wait-for-dependencies.sh" ]; then
    source "$WORKSPACE_DIR/scripts/lib/wait-for-dependencies.sh"
fi

echo "[$(date +'%Y-%m-%d %H:%M:%S')] Starting Argo service at $SERVICE_PATH on port $SERVICE_PORT..."

# Wait for dependencies before starting
if command -v wait_for_redis &> /dev/null; then
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] Waiting for Redis..."
    wait_for_redis "Redis" || {
        echo "[$(date +'%Y-%m-%d %H:%M:%S')] ⚠️  Warning: Redis not available, continuing anyway..."
    }
fi

if command -v wait_for_database &> /dev/null; then
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] Waiting for database..."
    export DB_PATH="$SERVICE_PATH/data/signals.db"
    wait_for_database "$DB_PATH" "Database" || {
        echo "[$(date +'%Y-%m-%d %H:%M:%S')] ⚠️  Warning: Database not available, continuing anyway..."
    }
fi

# Change to service directory
cd "$SERVICE_PATH"

# Check for virtual environment
if [ ! -d "venv" ]; then
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] ❌ ERROR: Virtual environment not found at $SERVICE_PATH/venv"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Stop any existing service on this port
pkill -f "uvicorn.*--port $SERVICE_PORT" 2>/dev/null || true
sleep 2

# Start service
echo "[$(date +'%Y-%m-%d %H:%M:%S')] Starting uvicorn on port $SERVICE_PORT..."
nohup uvicorn main:app --host 0.0.0.0 --port $SERVICE_PORT --timeout-keep-alive 30 > "$LOG_FILE" 2>&1 &
SERVICE_PID=$!
echo $SERVICE_PID > "/tmp/argo-${SERVICE_COLOR}.pid"

echo "[$(date +'%Y-%m-%d %H:%M:%S')] ✅ Service started with PID: $SERVICE_PID"
echo "[$(date +'%Y-%m-%d %H:%M:%S')] 📝 Logs: $LOG_FILE"

# Wait for service to be ready
if command -v wait_for_service &> /dev/null; then
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] Waiting for service health..."
    wait_for_service "http://localhost:$SERVICE_PORT/health" "Argo Service ($SERVICE_COLOR)" 20
else
    # Fallback to simple check
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] Waiting for service to start..."
    sleep 5
    if curl -sf --max-time 5 "http://localhost:$SERVICE_PORT/health" > /dev/null 2>&1; then
        echo "[$(date +'%Y-%m-%d %H:%M:%S')] ✅ Service is healthy"
    else
        echo "[$(date +'%Y-%m-%d %H:%M:%S')] ⚠️  Service may still be starting"
    fi
fi

echo "[$(date +'%Y-%m-%d %H:%M:%S')] ✅ Service startup complete"


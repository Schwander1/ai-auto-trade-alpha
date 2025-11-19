#!/bin/bash
# Ensure All Trading Services Are Always Running
# This script checks and starts all required services

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ARGO_DIR="$WORKSPACE_ROOT/argo"
LOG_DIR="$WORKSPACE_ROOT/logs"
mkdir -p "$LOG_DIR"

LOG_FILE="$LOG_DIR/ensure_always_running.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

check_service() {
    local port=$1
    local name=$2

    if curl -s "http://localhost:${port}/api/v1/trading/status" > /dev/null 2>&1 || \
       curl -s "http://localhost:${port}/health" > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

start_argo_executor() {
    log "Checking Argo Executor (port 8000)..."
    if check_service 8000 "Argo Executor"; then
        log "✅ Argo Executor is running"
        return 0
    fi

    log "⚠️  Argo Executor not running, but main service should handle this"
    log "   Main service on port 8000 should include executor"
    return 0
}

start_prop_firm_executor() {
    log "Checking Prop Firm Executor (port 8001)..."
    if check_service 8001 "Prop Firm Executor"; then
        log "✅ Prop Firm Executor is running"
        return 0
    fi

    log "🚀 Starting Prop Firm Executor..."

    # Find Python executable
    if [ -f "$ARGO_DIR/venv/bin/python" ]; then
        PYTHON="$ARGO_DIR/venv/bin/python"
    else
        PYTHON="python3"
    fi

    # Set environment
    export EXECUTOR_ID=prop_firm
    export EXECUTOR_CONFIG_PATH="$ARGO_DIR/config.json"
    export PORT=8001
    export PYTHONPATH="$ARGO_DIR"
    export ARGO_24_7_MODE=true

    cd "$ARGO_DIR"

    # Start in background
    nohup $PYTHON -m uvicorn argo.core.trading_executor:app \
        --host 0.0.0.0 \
        --port 8001 \
        >> "$LOG_DIR/prop_firm_executor.log" 2>&1 &

    local pid=$!
    log "   Started with PID: $pid"

    # Wait for service to be ready
    for i in {1..30}; do
        sleep 1
        if check_service 8001 "Prop Firm Executor"; then
            log "✅ Prop Firm Executor started successfully"
            return 0
        fi
    done

    log "⚠️  Prop Firm Executor started but not responding yet"
    return 1
}

check_signal_generation() {
    log "Checking Signal Generation..."

    if curl -s "http://localhost:8000/health" > /dev/null 2>&1; then
        local health=$(curl -s "http://localhost:8000/health" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('signal_generation', {}).get('background_task_running', False))" 2>/dev/null || echo "false")

        if [ "$health" = "True" ]; then
            log "✅ Signal generation is running"
            return 0
        else
            log "⚠️  Signal generation background task may not be running"
            return 1
        fi
    else
        log "❌ Cannot check signal generation (main service not accessible)"
        return 1
    fi
}

main() {
    log "=========================================="
    log "Ensuring All Trading Services Are Running"
    log "=========================================="

    # Check and start services
    start_argo_executor
    start_prop_firm_executor
    check_signal_generation

    log "=========================================="
    log "Check complete"
    log "=========================================="
}

main "$@"

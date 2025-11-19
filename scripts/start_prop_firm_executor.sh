#!/bin/bash
# Start Prop Firm Executor Service
# This script starts the Prop Firm executor on port 8001

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ARGO_DIR="$WORKSPACE_ROOT/argo"

echo "🚀 Starting Prop Firm Executor..."
echo "   Working Directory: $ARGO_DIR"
echo "   Port: 8001"

# Check if already running
if curl -s http://localhost:8001/api/v1/trading/status > /dev/null 2>&1; then
    echo "✅ Prop Firm Executor is already running on port 8001"
    exit 0
fi

# Set environment variables
export EXECUTOR_ID=prop_firm
export EXECUTOR_CONFIG_PATH="$ARGO_DIR/config.json"
export PORT=8001
export PYTHONPATH="$ARGO_DIR"
export ARGO_24_7_MODE=true

# Check if config exists
if [ ! -f "$EXECUTOR_CONFIG_PATH" ]; then
    echo "⚠️  Config file not found: $EXECUTOR_CONFIG_PATH"
    echo "   Using default config path detection"
    unset EXECUTOR_CONFIG_PATH
fi

# Start the executor
cd "$ARGO_DIR"
echo "   Starting uvicorn server..."

# Check if venv exists
if [ -d "$ARGO_DIR/venv" ]; then
    PYTHON="$ARGO_DIR/venv/bin/python"
else
    PYTHON="python3"
fi

# Start in background
nohup $PYTHON -m uvicorn argo.core.trading_executor:app \
    --host 0.0.0.0 \
    --port 8001 \
    > /tmp/prop_firm_executor.log 2>&1 &

PID=$!
echo "   Started with PID: $PID"
echo "   Logs: /tmp/prop_firm_executor.log"

# Wait for service to be ready
echo "   Waiting for service to start..."
for i in {1..30}; do
    sleep 1
    if curl -s http://localhost:8001/api/v1/trading/status > /dev/null 2>&1; then
        echo "   ✅ Prop Firm Executor started successfully!"
        echo "   Status: http://localhost:8001/api/v1/trading/status"
        exit 0
    fi
    echo -n "."
done

echo ""
echo "   ⚠️  Service started but not responding yet"
echo "   Check logs: tail -f /tmp/prop_firm_executor.log"
exit 1

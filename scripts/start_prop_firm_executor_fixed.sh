#!/bin/bash
# Start Prop Firm Executor Service (Fixed Version)
# Uses the same Python environment as the main service

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
    curl -s http://localhost:8001/api/v1/trading/status | python3 -m json.tool
    exit 0
fi

# Find Python executable (use same as main service)
# Check for venv first
if [ -f "$ARGO_DIR/venv/bin/python" ]; then
    PYTHON="$ARGO_DIR/venv/bin/python"
    echo "   Using venv Python: $PYTHON"
elif [ -f "$ARGO_DIR/venv/bin/python3" ]; then
    PYTHON="$ARGO_DIR/venv/bin/python3"
    echo "   Using venv Python3: $PYTHON"
else
    # Find Python from running process
    MAIN_PYTHON=$(ps aux | grep "uvicorn.*8000" | grep -v grep | awk '{print $11}' | head -1)
    if [ -n "$MAIN_PYTHON" ] && [ -f "$MAIN_PYTHON" ]; then
        PYTHON="$MAIN_PYTHON"
        echo "   Using Python from main service: $PYTHON"
    else
        PYTHON="python3"
        echo "   Using system Python3: $PYTHON"
    fi
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

# Test import first
echo "   Testing import..."
cd "$ARGO_DIR"
if ! $PYTHON -c "from argo.core.trading_executor import app" 2>/dev/null; then
    echo "❌ Import failed. Trying to install dependencies..."
    echo "   Run: cd $ARGO_DIR && pip install -r requirements.txt"
    exit 1
fi

echo "   ✅ Import successful"

# Start the executor
echo "   Starting uvicorn server..."

# Start in background
nohup $PYTHON -m uvicorn argo.core.trading_executor:app \
    --host 0.0.0.0 \
    --port 8001 \
    > /tmp/prop_firm_executor.log 2>&1 &

PID=$!
echo "   Started with PID: $PID"
echo "   Logs: /tmp/prop_firm_executor.log"
echo "   View logs: tail -f /tmp/prop_firm_executor.log"

# Wait for service to be ready
echo "   Waiting for service to start..."
for i in {1..30}; do
    sleep 1
    if curl -s http://localhost:8001/api/v1/trading/status > /dev/null 2>&1; then
        echo ""
        echo "   ✅ Prop Firm Executor started successfully!"
        echo "   Status: http://localhost:8001/api/v1/trading/status"
        curl -s http://localhost:8001/api/v1/trading/status | python3 -m json.tool
        exit 0
    fi
    echo -n "."
done

echo ""
echo "   ⚠️  Service started but not responding yet"
echo "   Check logs: tail -f /tmp/prop_firm_executor.log"
echo "   PID: $PID"
exit 1

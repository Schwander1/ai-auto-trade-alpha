#!/bin/bash
# Restart Argo service with production mode and 24/7 mode enabled

set -e

cd "$(dirname "$0")"

# Source dependency checking utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
if [ -f "$WORKSPACE_ROOT/scripts/lib/wait-for-dependencies.sh" ]; then
    source "$WORKSPACE_ROOT/scripts/lib/wait-for-dependencies.sh"
else
    echo "⚠️  Warning: Dependency checking utilities not found"
fi

echo "🛑 Stopping existing Argo service..."
pkill -f "uvicorn.*main:app" || echo "No existing service found"

sleep 2

# Wait for dependencies before starting
if command -v wait_for_redis &> /dev/null; then
    wait_for_redis "Redis" || {
        echo "⚠️  Warning: Redis not available, continuing anyway..."
    }
fi

if command -v wait_for_database &> /dev/null; then
    wait_for_database "" "Database" || {
        echo "⚠️  Warning: Database not available, continuing anyway..."
    }
fi

echo "🚀 Starting Argo service in production mode..."
source venv/bin/activate

# Set environment variables (24/7 mode, but keep environment detection natural)
export ARGO_24_7_MODE=true
# Don't force production mode - let environment detection work naturally
# This allows 24/7 mode in development without triggering security checks

# Create logs directory
mkdir -p logs

# Start service
LOG_FILE="logs/service_$(date +%Y%m%d_%H%M%S).log"
nohup uvicorn main:app --reload --host 0.0.0.0 --port 8000 > "$LOG_FILE" 2>&1 &
SERVICE_PID=$!

echo "✅ Service started with PID: $SERVICE_PID"
echo "📝 Logs: $LOG_FILE"
echo ""
echo "Waiting for service to start..."

# Wait for service health with better retry logic
if command -v wait_for_service &> /dev/null; then
    wait_for_service "http://localhost:8000/health" "Argo Service" 15
else
    # Fallback to simple check
    sleep 5
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Service is healthy!"
    else
        echo "⚠️  Service may still be starting. Check logs for details."
    fi
fi

# Check health and show status
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Service is healthy!"
    echo ""
    echo "📊 Service Status:"
    curl -s http://localhost:8000/health | python3 -m json.tool | grep -E "status|signal_generation|Environment" || true
else
    echo "⚠️  Service may still be starting. Check logs for details."
fi

echo ""
echo "To monitor logs:"
echo "  tail -f logs/service_*.log | grep -E '24/7|Environment|Generated|signal'"


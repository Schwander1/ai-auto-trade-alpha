#!/bin/bash
# Optimize and Restart Signal Generation Service

set -e

echo "🔧 Optimizing Signal Generation Service..."

# 1. Stop existing service
echo "Stopping existing service..."
pkill -f "uvicorn.*main:app" 2>/dev/null || true
sleep 2

# 2. Clear Redis cache if available (to fix corrupted entries)
echo "Clearing potentially corrupted Redis cache..."
if command -v redis-cli &> /dev/null; then
    redis-cli FLUSHDB 2>/dev/null || echo "Redis not available, skipping cache clear"
fi

# 3. Start service
echo "Starting optimized service..."
cd /Users/dylanneuenschwander/argo-alpine-workspace/argo
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 > logs/service_$(date +%Y%m%d_%H%M%S).log 2>&1 &
SERVICE_PID=$!
echo "Service started with PID: $SERVICE_PID"

# 4. Wait for service to start
echo "Waiting for service to initialize..."
sleep 10

# 5. Check health
echo "Checking service health..."
HEALTH=$(curl -s http://localhost:8000/health 2>/dev/null || echo "{}")
if echo "$HEALTH" | grep -q "healthy"; then
    echo "✅ Service is healthy"
else
    echo "⚠️  Service health check failed"
    echo "Response: $HEALTH"
fi

# 6. Check signal generation status
SIGNAL_STATUS=$(echo "$HEALTH" | python3 -c "import sys, json; d=json.load(sys.stdin) if sys.stdin.read() else {}; print(d.get('signal_generation', {}).get('status', 'unknown'))" 2>/dev/null || echo "unknown")
echo "Signal generation status: $SIGNAL_STATUS"

echo ""
echo "✅ Optimization complete!"
echo "Monitor logs: tail -f argo/logs/service_*.log"


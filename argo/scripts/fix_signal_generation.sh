#!/bin/bash
# Fix Signal Generation Issues

set -e

echo "🔧 Fixing Signal Generation Issues..."

# 1. Fix Redis cache type comparison error (already done in code)
echo "✅ Fixed Redis cache type comparison error"

# 2. Check if service is running
if pgrep -f "uvicorn.*main:app" > /dev/null; then
    echo "✅ API service is running"
    PID=$(pgrep -f "uvicorn.*main:app" | head -1)
    echo "   PID: $PID"
else
    echo "⚠️  API service is not running"
    echo "   Start with: cd argo && python3 -m uvicorn main:app --host 0.0.0.0 --port 8000"
fi

# 3. Check health endpoint
echo ""
echo "📊 Checking health endpoint..."
HEALTH=$(curl -s http://localhost:8000/health 2>/dev/null || echo "{}")
SIGNAL_STATUS=$(echo "$HEALTH" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('signal_generation', {}).get('status', 'unknown'))" 2>/dev/null || echo "unknown")

if [ "$SIGNAL_STATUS" = "running" ]; then
    echo "✅ Signal generation is RUNNING"
elif [ "$SIGNAL_STATUS" = "paused" ]; then
    echo "⚠️  Signal generation is PAUSED (development mode - check Cursor/computer state)"
elif [ "$SIGNAL_STATUS" = "stopped" ]; then
    echo "❌ Signal generation is STOPPED"
    echo "   Restart the API service to start signal generation"
else
    echo "⚠️  Signal generation status: $SIGNAL_STATUS"
fi

# 4. Check recent signals
echo ""
echo "📈 Checking recent signals..."
RECENT_COUNT=$(sqlite3 data/signals.db "SELECT COUNT(*) FROM signals WHERE timestamp > datetime('now', '-1 hour');" 2>/dev/null || echo "0")
if [ "$RECENT_COUNT" -gt 0 ]; then
    echo "✅ Found $RECENT_COUNT signal(s) in last hour"
else
    echo "⚠️  No signals generated in last hour"
fi

# 5. Check for errors in logs
echo ""
echo "🔍 Checking for errors in logs..."
ERROR_COUNT=$(tail -100 argo/logs/service_*.log 2>/dev/null | grep -i "error\|exception\|failed" | wc -l | tr -d ' ')
if [ "$ERROR_COUNT" -gt 0 ]; then
    echo "⚠️  Found $ERROR_COUNT error(s) in recent logs"
    echo "   Recent errors:"
    tail -100 argo/logs/service_*.log 2>/dev/null | grep -i "error\|exception\|failed" | tail -3
else
    echo "✅ No recent errors in logs"
fi

echo ""
echo "✅ Fix script completed"
echo ""
echo "Next steps:"
echo "1. If signal generation is stopped, restart the API service"
echo "2. If paused, check Cursor/computer state (development mode)"
echo "3. Monitor logs: tail -f argo/logs/service_*.log"
echo "4. Check health: curl http://localhost:8000/health | jq"


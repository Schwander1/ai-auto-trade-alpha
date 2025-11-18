#!/bin/bash
# Monitor signal storage and generation

echo "🔍 Monitoring Signal Storage and Generation..."
echo ""

# Check recent signals in database
echo "📊 Recent signals in database (last 10 minutes):"
RECENT_COUNT=$(sqlite3 /root/argo-production-green/data/signals.db "SELECT COUNT(*) FROM signals WHERE timestamp > datetime('now', '-10 minutes');" 2>/dev/null || echo "0")
echo "  Count: $RECENT_COUNT"

if [ "$RECENT_COUNT" -gt 0 ]; then
    echo "  Latest signals:"
    sqlite3 /root/argo-production-green/data/signals.db "SELECT symbol, action, confidence, timestamp FROM signals ORDER BY timestamp DESC LIMIT 5;" 2>/dev/null | while IFS='|' read -r symbol action confidence timestamp; do
        echo "    $symbol $action @ $confidence% - $timestamp"
    done
fi

echo ""
echo "📈 Signal generation activity (last 1000 lines):"
GENERATED=$(tail -1000 /root/argo-production-green/logs/service.log 2>/dev/null | grep -c "✅ Generated signal" || echo "0")
echo "  Generated signals logged: $GENERATED"

echo ""
echo "💾 Batch flush activity:"
FLUSHED=$(tail -10000 /root/argo-production-green/logs/service.log 2>/dev/null | grep -c "Batch inserted\|Periodic flush" || echo "0")
echo "  Batch flush operations: $FLUSHED"

echo ""
echo "⚡ Trade execution activity:"
EXECUTED=$(tail -10000 /root/argo-production-green/logs/service.log 2>/dev/null | grep -c "Trade executed\|order_id" || echo "0")
echo "  Trade executions: $EXECUTED"

echo ""
echo "✅ Monitoring complete"


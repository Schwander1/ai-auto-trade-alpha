#!/bin/bash
# Fix signal generation by checking and restarting if needed

echo "🔍 Checking signal generation status..."
echo ""

# Check if background task is actually running
ARGO_STATUS=$(curl -s http://localhost:8000/health 2>/dev/null | python3 -c "import sys, json; d=json.load(sys.stdin); sg=d.get('signal_generation', {}); print(f\"{sg.get('background_task_running')}\")" 2>/dev/null || echo "false")
PROP_STATUS=$(curl -s http://localhost:8001/health 2>/dev/null | python3 -c "import sys, json; d=json.load(sys.stdin); sg=d.get('signal_generation', {}); print(f\"{sg.get('background_task_running')}\")" 2>/dev/null || echo "false")

echo "Argo background task running: $ARGO_STATUS"
echo "Prop Firm background task running: $PROP_STATUS"
echo ""

# Check for recent signal generation activity
ARGO_SIGNALS=$(tail -10000 /root/argo-production-green/logs/service.log 2>/dev/null | grep -c "_run_signal_generation_cycle\|generating.*signals" || echo "0")
PROP_SIGNALS=$(tail -10000 /root/argo-production-prop-firm/logs/service.log 2>/dev/null | grep -c "_run_signal_generation_cycle\|generating.*signals" || echo "0")

echo "Recent signal generation cycles:"
echo "  Argo: $ARGO_SIGNALS"
echo "  Prop Firm: $PROP_SIGNALS"
echo ""

if [ "$ARGO_SIGNALS" -eq 0 ] && [ "$ARGO_STATUS" = "True" ]; then
    echo "⚠️  Argo: Background task reports running but no signal generation activity"
    echo "   Restarting service..."
    sudo systemctl restart argo-trading.service
    sleep 5
fi

if [ "$PROP_SIGNALS" -eq 0 ] && [ "$PROP_STATUS" = "True" ]; then
    echo "⚠️  Prop Firm: Background task reports running but no signal generation activity"
    echo "   Restarting service..."
    sudo systemctl restart argo-trading-prop-firm.service
    sleep 5
fi

echo ""
echo "✅ Check complete"


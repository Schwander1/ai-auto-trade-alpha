#!/bin/bash
# Debug signal generation process

echo "🔍 DEBUGGING SIGNAL GENERATION"
echo "================================"
echo ""

echo "1. Checking service processes:"
ps aux | grep -E "uvicorn|python.*main" | grep -v grep
echo ""

echo "2. Checking recent logs (last 20 lines):"
echo "--- Argo Service ---"
tail -20 /root/argo-production-green/logs/service.log 2>/dev/null || echo "No log file"
echo ""
echo "--- Prop Firm Service ---"
tail -20 /root/argo-production-prop-firm/logs/service.log 2>/dev/null || echo "No log file"
echo ""

echo "3. Checking health endpoints:"
echo "--- Argo ---"
curl -s http://localhost:8000/health 2>/dev/null | python3 -c "import sys, json; d=json.load(sys.stdin); sg=d.get('signal_generation', {}); print(f\"Status: {sg.get('status')}\"); print(f\"Background Task: {sg.get('background_task_running')}\"); print(f\"Error: {sg.get('background_task_error')}\")" 2>/dev/null || echo "Failed"
echo ""
echo "--- Prop Firm ---"
curl -s http://localhost:8001/health 2>/dev/null | python3 -c "import sys, json; d=json.load(sys.stdin); sg=d.get('signal_generation', {}); print(f\"Status: {sg.get('status')}\"); print(f\"Background Task: {sg.get('background_task_running')}\"); print(f\"Error: {sg.get('background_task_error')}\")" 2>/dev/null || echo "Failed"
echo ""

echo "4. Checking for signal generation activity:"
echo "--- Argo ---"
tail -1000 /root/argo-production-green/logs/service.log 2>/dev/null | grep -c "generating\|signal\|Symbol" || echo "0"
echo ""
echo "--- Prop Firm ---"
tail -1000 /root/argo-production-prop-firm/logs/service.log 2>/dev/null | grep -c "generating\|signal\|Symbol" || echo "0"
echo ""

echo "5. Checking systemd status:"
systemctl status argo-trading.service --no-pager | head -10
echo ""
systemctl status argo-trading-prop-firm.service --no-pager | head -10


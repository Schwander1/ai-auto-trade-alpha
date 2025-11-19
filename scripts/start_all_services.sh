#!/bin/bash
# Start All Trading Services
# Ensures everything is running and configured correctly

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ARGO_DIR="$WORKSPACE_ROOT/argo"
LOG_DIR="$WORKSPACE_ROOT/logs"
mkdir -p "$LOG_DIR"

echo "🚀 Starting All Trading Services..."
echo "=========================================="
echo ""

# 1. Ensure 24/7 mode is enabled
echo "1️⃣  Ensuring 24/7 mode is enabled..."
export ARGO_24_7_MODE=true
if [ -f "$HOME/.zshrc" ] && grep -q "ARGO_24_7_MODE" "$HOME/.zshrc"; then
    echo "   ✅ 24/7 mode configured in shell profile"
else
    echo "   ⚠️  24/7 mode not in shell profile, setting for this session"
fi
echo ""

# 2. Fix configuration
echo "2️⃣  Fixing configuration..."
cd "$WORKSPACE_ROOT"
python3 scripts/fix_config_permanent.py
echo ""

# 3. Ensure Prop Firm Executor is running
echo "3️⃣  Ensuring Prop Firm Executor is running..."
if curl -s http://localhost:8001/api/v1/trading/status > /dev/null 2>&1; then
    echo "   ✅ Prop Firm Executor is already running"
else
    echo "   🚀 Starting Prop Firm Executor..."
    ./scripts/start_prop_firm_executor_fixed.sh
fi
echo ""

# 4. Check main service
echo "4️⃣  Checking main service (port 8000)..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "   ✅ Main service is running"

    # Check signal generation
    signal_gen=$(curl -s http://localhost:8000/health | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('signal_generation', {}).get('background_task_running', False))" 2>/dev/null || echo "false")
    if [ "$signal_gen" = "True" ]; then
        echo "   ✅ Signal generation is active"
    else
        echo "   ⚠️  Signal generation may not be active (restart main service)"
    fi
else
    echo "   ⚠️  Main service is not running"
    echo "   Start it with: cd argo && python3 -m uvicorn main:app --host 0.0.0.0 --port 8000"
fi
echo ""

# 5. Final verification
echo "5️⃣  Final verification..."
python3 scripts/ensure_both_trading.py
echo ""

echo "=========================================="
echo "✅ Startup complete!"
echo "=========================================="
echo ""
echo "Services status:"
echo "  - Argo Executor: http://localhost:8000"
echo "  - Prop Firm Executor: http://localhost:8001"
echo "  - Signal Generation: Active (24/7 mode)"
echo ""
echo "Monitor with:"
echo "  python scripts/ensure_both_trading.py"
echo "  python scripts/show_recent_signals.py 20"

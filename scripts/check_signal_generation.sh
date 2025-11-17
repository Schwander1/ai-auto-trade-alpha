#!/bin/bash
# Signal Generation Health Check and Evaluation Script

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

ARGO_DIR="argo"
ALPINE_BACKEND_DIR="alpine-backend"

print_header() {
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

print_ok() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_fail() {
    echo -e "${RED}❌ $1${NC}"
}

print_warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "ℹ️  $1"
}

# Check if Argo service is running
print_header "Signal Generation Service Status"

if pgrep -f "argo.*main.py" > /dev/null; then
    PID=$(pgrep -f "argo.*main.py" | head -1)
    print_ok "Argo main service is running (PID: $PID)"
elif pgrep -f "signal_generation_service" > /dev/null; then
    PID=$(pgrep -f "signal_generation_service" | head -1)
    print_ok "Signal generation service is running (PID: $PID)"
else
    print_fail "Signal generation service is NOT running"
    print_info "Start with: cd argo && PYTHONPATH=argo python3 -m argo.core.signal_generation_service"
    exit 1
fi

# Check signal generation logs
print_header "Signal Generation Logs Analysis"

LOG_FILE="$ARGO_DIR/logs/signal_generation.log"
if [ -f "$LOG_FILE" ]; then
    print_ok "Log file found: $LOG_FILE"
    
    # Count recent signals
    RECENT_SIGNALS=$(tail -1000 "$LOG_FILE" | grep -c "Signal generated" || echo "0")
    print_info "Recent signals generated: $RECENT_SIGNALS (last 1000 log lines)"
    
    # Check for errors
    ERROR_COUNT=$(tail -1000 "$LOG_FILE" | grep -ci "error\|exception\|failed" || echo "0")
    if [ "$ERROR_COUNT" -eq 0 ]; then
        print_ok "No errors in recent logs"
    else
        print_warn "Found $ERROR_COUNT error(s) in recent logs"
        print_info "Recent errors:"
        tail -1000 "$LOG_FILE" | grep -i "error\|exception\|failed" | tail -5
    fi
    
    # Check generation frequency
    LAST_SIGNAL=$(tail -100 "$LOG_FILE" | grep "Signal generated" | tail -1)
    if [ -n "$LAST_SIGNAL" ]; then
        print_ok "Last signal: $LAST_SIGNAL"
    else
        print_warn "No recent signal generation found"
    fi
else
    print_warn "Log file not found: $LOG_FILE"
fi

# Check Argo API
print_header "Argo API Health"

if curl -sf http://localhost:8000/api/v1/health > /dev/null 2>&1; then
    print_ok "Argo API is accessible"
    
    # Get health status
    HEALTH_RESPONSE=$(curl -sf http://localhost:8000/api/v1/health 2>/dev/null || echo "{}")
    echo "Health response: $HEALTH_RESPONSE"
else
    print_warn "Argo API health endpoint not accessible (may not be exposed)"
fi

# Check signal API endpoint
print_header "Signal API Endpoint Check"

if curl -sf http://localhost:8000/api/v1/signals/latest > /dev/null 2>&1; then
    print_ok "Signal API endpoint is accessible"
    
    # Get latest signals
    SIGNALS_RESPONSE=$(curl -sf http://localhost:8000/api/v1/signals/latest?limit=5 2>/dev/null || echo "[]")
    SIGNAL_COUNT=$(echo "$SIGNALS_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data) if isinstance(data, list) else len(data.get('items', [])))" 2>/dev/null || echo "0")
    
    if [ "$SIGNAL_COUNT" -gt 0 ]; then
        print_ok "Found $SIGNAL_COUNT recent signal(s)"
    else
        print_warn "No signals found in API response"
    fi
else
    print_warn "Signal API endpoint not accessible"
fi

# Check Alpine Backend signal sync
print_header "Alpine Backend Signal Sync"

if curl -sf http://localhost:8001/api/v1/signals/subscribed > /dev/null 2>&1; then
    print_ok "Alpine backend signal endpoint is accessible"
else
    print_warn "Alpine backend signal endpoint requires authentication"
fi

# Performance metrics
print_header "Performance Metrics"

# Check CPU and memory usage
if command -v ps > /dev/null; then
    if pgrep -f "signal_generation_service" > /dev/null; then
        PID=$(pgrep -f "signal_generation_service" | head -1)
        CPU=$(ps -p $PID -o %cpu= 2>/dev/null | tr -d ' ' || echo "N/A")
        MEM=$(ps -p $PID -o %mem= 2>/dev/null | tr -d ' ' || echo "N/A")
        print_info "Signal generation service: CPU: ${CPU}%, Memory: ${MEM}%"
    fi
fi

# Database signal count
print_header "Database Signal Count"

cd "$ALPINE_BACKEND_DIR/backend"
python3 << 'EOF'
from backend.core.database import get_engine
from sqlalchemy import text

try:
    engine = get_engine()
    with engine.connect() as conn:
        # Count total signals
        result = conn.execute(text("SELECT COUNT(*) FROM signals"))
        total = result.scalar()
        print(f"✅ Total signals in database: {total}")
        
        # Count recent signals (last 24 hours)
        result = conn.execute(text("""
            SELECT COUNT(*) FROM signals 
            WHERE created_at > NOW() - INTERVAL '24 hours'
        """))
        recent = result.scalar()
        print(f"✅ Signals in last 24 hours: {recent}")
        
        # Count active signals
        result = conn.execute(text("SELECT COUNT(*) FROM signals WHERE is_active = true"))
        active = result.scalar()
        print(f"✅ Active signals: {active}")
        
        if recent == 0:
            print("⚠️  WARNING: No signals generated in last 24 hours")
            exit(1)
except Exception as e:
    print(f"❌ Database check failed: {e}")
    exit(1)
EOF

DB_CHECK=$?

# Evaluation Summary
print_header "Signal Generation Evaluation"

echo "Service Status:"
if pgrep -f "signal_generation_service\|argo.*main.py" > /dev/null; then
    echo "  ✅ Signal generation service: RUNNING"
else
    echo "  ❌ Signal generation service: NOT RUNNING"
fi

echo ""
echo "Signal Generation:"
if [ "$RECENT_SIGNALS" -gt 0 ]; then
    echo "  ✅ Signals being generated: YES ($RECENT_SIGNALS recent)"
else
    echo "  ⚠️  Signals being generated: NO RECENT SIGNALS"
fi

echo ""
echo "API Access:"
if curl -sf http://localhost:8000/api/v1/health > /dev/null 2>&1; then
    echo "  ✅ Argo API: ACCESSIBLE"
else
    echo "  ⚠️  Argo API: NOT ACCESSIBLE"
fi

echo ""
echo "Database:"
if [ $DB_CHECK -eq 0 ]; then
    echo "  ✅ Database signals: OK"
else
    echo "  ⚠️  Database signals: ISSUES DETECTED"
fi

echo ""
if [ "$RECENT_SIGNALS" -gt 0 ] && [ $DB_CHECK -eq 0 ]; then
    print_ok "Signal generation is HEALTHY"
    exit 0
else
    print_fail "Signal generation has ISSUES"
    exit 1
fi


#!/bin/bash
# Complete fix and verification script for production

set -e

echo "🔧 COMPLETE FIX AND VERIFICATION"
echo "================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_step() {
    echo -e "${BLUE}▶ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Step 1: Check service status
print_step "Step 1: Checking service status"
ARGO_STATUS=$(systemctl is-active argo-trading.service 2>/dev/null || echo "inactive")
PROP_STATUS=$(systemctl is-active argo-trading-prop-firm.service 2>/dev/null || echo "inactive")

if [ "$ARGO_STATUS" = "active" ]; then
    print_success "Argo service is active"
else
    print_error "Argo service is not active"
fi

if [ "$PROP_STATUS" = "active" ]; then
    print_success "Prop Firm service is active"
else
    print_error "Prop Firm service is not active"
fi

# Step 2: Check health endpoints
print_step "Step 2: Checking health endpoints"
ARGO_HEALTH=$(curl -s http://localhost:8000/health 2>/dev/null | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('status', 'unknown'))" 2>/dev/null || echo "unknown")
PROP_HEALTH=$(curl -s http://localhost:8001/health 2>/dev/null | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('status', 'unknown'))" 2>/dev/null || echo "unknown")

if [ "$ARGO_HEALTH" = "healthy" ]; then
    print_success "Argo service is healthy"
else
    print_warning "Argo service health: $ARGO_HEALTH"
fi

if [ "$PROP_HEALTH" = "healthy" ]; then
    print_success "Prop Firm service is healthy"
else
    print_warning "Prop Firm service health: $PROP_HEALTH"
fi

# Step 3: Check Alpaca credentials
print_step "Step 3: Checking Alpaca credentials"
python3 /root/fix_alpaca_connection.py 2>/dev/null || echo "Credential check script not found"

# Step 4: Check signal generation
print_step "Step 4: Checking signal generation"
ARGO_SIGNALS=$(tail -1000 /root/argo-production-green/logs/service.log 2>/dev/null | grep -c "Generated signal\|Massive.*signal" || echo "0")
PROP_SIGNALS=$(tail -1000 /root/argo-production-prop-firm/logs/service.log 2>/dev/null | grep -c "Generated signal\|Massive.*signal" || echo "0")

if [ "$ARGO_SIGNALS" -gt 0 ]; then
    print_success "Argo service generating signals ($ARGO_SIGNALS found in logs)"
else
    print_warning "Argo service: No signals found in recent logs"
fi

if [ "$PROP_SIGNALS" -gt 0 ]; then
    print_success "Prop Firm service generating signals ($PROP_SIGNALS found in logs)"
else
    print_warning "Prop Firm service: No signals found in recent logs"
fi

# Step 5: Check trading status
print_step "Step 5: Checking trading status"
ARGO_TRADING=$(curl -s http://localhost:8000/api/v1/trading/status 2>/dev/null | python3 -c "import sys, json; d=json.load(sys.stdin); print(f\"alpaca_connected: {d.get('alpaca_connected')}, prop_firm: {d.get('prop_firm_enabled')}\")" 2>/dev/null || echo "unknown")
PROP_TRADING=$(curl -s http://localhost:8001/api/v1/trading/status 2>/dev/null | python3 -c "import sys, json; d=json.load(sys.stdin); print(f\"alpaca_connected: {d.get('alpaca_connected')}, prop_firm: {d.get('prop_firm_enabled')}\")" 2>/dev/null || echo "unknown")

echo "   Argo: $ARGO_TRADING"
echo "   Prop Firm: $PROP_TRADING"

# Step 6: Check for errors
print_step "Step 6: Checking for errors"
ARGO_ERRORS=$(tail -500 /root/argo-production-green/logs/service.error.log 2>/dev/null | grep -c "Error\|error\|Exception\|Traceback" || echo "0")
PROP_ERRORS=$(tail -500 /root/argo-production-prop-firm/logs/service.error.log 2>/dev/null | grep -c "Error\|error\|Exception\|Traceback" || echo "0")

if [ "$ARGO_ERRORS" -gt 0 ]; then
    print_warning "Argo service has $ARGO_ERRORS errors in logs"
    echo "   Recent errors:"
    tail -500 /root/argo-production-green/logs/service.error.log 2>/dev/null | grep -E "Error|error|Exception" | tail -3 | sed 's/^/      /'
else
    print_success "Argo service: No recent errors"
fi

if [ "$PROP_ERRORS" -gt 0 ]; then
    print_warning "Prop Firm service has $PROP_ERRORS errors in logs"
    echo "   Recent errors:"
    tail -500 /root/argo-production-prop-firm/logs/service.error.log 2>/dev/null | grep -E "Error|error|Exception" | tail -3 | sed 's/^/      /'
else
    print_success "Prop Firm service: No recent errors"
fi

# Summary
echo ""
echo "================================="
echo "📊 SUMMARY"
echo "================================="
echo ""
echo "Service Status:"
echo "  Argo: $ARGO_STATUS"
echo "  Prop Firm: $PROP_STATUS"
echo ""
echo "Health:"
echo "  Argo: $ARGO_HEALTH"
echo "  Prop Firm: $PROP_HEALTH"
echo ""
echo "Signal Generation:"
echo "  Argo: $ARGO_SIGNALS signals in logs"
echo "  Prop Firm: $PROP_SIGNALS signals in logs"
echo ""
echo "Trading Status:"
echo "  Argo: $ARGO_TRADING"
echo "  Prop Firm: $PROP_TRADING"
echo ""

if [ "$ARGO_STATUS" = "active" ] && [ "$PROP_STATUS" = "active" ] && [ "$ARGO_HEALTH" = "healthy" ] && [ "$PROP_HEALTH" = "healthy" ]; then
    print_success "Both services are running and healthy!"
    echo ""
    echo "⚠️  Next Steps:"
    echo "  1. Add Alpaca credentials to Argo config if needed"
    echo "  2. Monitor logs for signal generation"
    echo "  3. Verify trade execution when signals meet criteria"
else
    print_warning "Some services may need attention"
fi

echo ""


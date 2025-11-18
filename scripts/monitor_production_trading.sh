#!/bin/bash
# Monitor Production Trading Execution
# Monitors logs for trading execution, errors, and crypto order success

set -e

PRODUCTION_SERVER="178.156.194.174"
PRODUCTION_USER="root"
LOG_FILE="/tmp/argo-blue.log"
DURATION="${1:-60}"  # Default 60 seconds

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

print_header() {
    echo ""
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
    echo ""
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

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check service status
check_service_status() {
    print_header "SERVICE STATUS CHECK"
    
    if ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} "systemctl is-active --quiet argo-trading.service"; then
        print_success "Service is active"
    else
        print_error "Service is not active"
        return 1
    fi
    
    # Get service status
    ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} "systemctl status argo-trading.service --no-pager -l | head -10"
}

# Check health endpoint
check_health() {
    print_header "HEALTH ENDPOINT CHECK"
    
    HEALTH_RESPONSE=$(curl -s http://${PRODUCTION_SERVER}:8000/health 2>/dev/null)
    if [ $? -eq 0 ]; then
        STATUS=$(echo "$HEALTH_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', 'unknown'))" 2>/dev/null || echo "unknown")
        if [ "$STATUS" = "healthy" ]; then
            print_success "Health endpoint: $STATUS"
            echo "$HEALTH_RESPONSE" | python3 -m json.tool 2>/dev/null | head -15
        else
            print_warning "Health endpoint: $STATUS"
        fi
    else
        print_error "Health endpoint not responding"
    fi
}

# Check latest signals
check_latest_signals() {
    print_header "LATEST SIGNALS"
    
    SIGNALS=$(curl -s "http://${PRODUCTION_SERVER}:8000/api/signals/latest?limit=5" 2>/dev/null)
    if [ $? -eq 0 ]; then
        echo "$SIGNALS" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if isinstance(data, list) and len(data) > 0:
        print('Latest signals:')
        for s in data[:5]:
            print(f\"  {s['symbol']}: {s['action']} @ \${s['price']:.2f} (confidence: {s['confidence']:.1f}%)\")
    else:
        print('No signals found')
except:
    print('Error parsing signals')
" 2>/dev/null || print_warning "Could not parse signals"
    else
        print_error "Could not fetch signals"
    fi
}

# Monitor logs for specific patterns
monitor_logs() {
    print_header "MONITORING LOGS (${DURATION}s)"
    print_info "Watching for:"
    print_info "  - Crypto order execution (ETH-USD, BTC-USD)"
    print_info "  - Symbol conversion messages"
    print_info "  - API key errors"
    print_info "  - Trading errors"
    echo ""
    
    # Use timeout to limit monitoring duration
    ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} "timeout ${DURATION} tail -f ${LOG_FILE} 2>/dev/null | grep --line-buffered -E 'ETH-USD|BTC-USD|Converted symbol|Order|API key|Invalid|Unauthorized|ERROR|Exception' || true" || true
}

# Check for recent errors
check_recent_errors() {
    print_header "RECENT ERRORS (Last 50 lines)"
    
    ERRORS=$(ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} "tail -n 50 ${LOG_FILE} 2>/dev/null | grep -E 'ERROR|Exception|Traceback|Invalid|Unauthorized' | tail -10" || echo "")
    
    if [ -z "$ERRORS" ]; then
        print_success "No recent errors found"
    else
        print_warning "Recent errors found:"
        echo "$ERRORS"
    fi
}

# Check API key status
check_api_keys() {
    print_header "API KEY STATUS"
    
    # Check for API key errors in logs
    XAI_ERRORS=$(ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} "tail -n 100 ${LOG_FILE} 2>/dev/null | grep -c 'xAI API error.*Invalid API key' || echo '0'")
    MASSIVE_ERRORS=$(ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} "tail -n 100 ${LOG_FILE} 2>/dev/null | grep -c 'Massive API error 401.*Unknown API Key' || echo '0'")
    
    if [ "$XAI_ERRORS" -gt 0 ]; then
        print_warning "xAI Grok API key errors detected: $XAI_ERRORS"
        print_info "Run: ./scripts/update_production_api_keys.sh"
    else
        print_success "xAI Grok API key: OK"
    fi
    
    if [ "$MASSIVE_ERRORS" -gt 0 ]; then
        print_warning "Massive API key errors detected: $MASSIVE_ERRORS"
        print_info "Run: ./scripts/update_production_api_keys.sh"
    else
        print_success "Massive API key: OK"
    fi
}

# Check crypto trading activity
check_crypto_trading() {
    print_header "CRYPTO TRADING STATUS"
    
    # Check for symbol conversion messages
    CONVERSIONS=$(ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} "tail -n 200 ${LOG_FILE} 2>/dev/null | grep -c 'Converted symbol' || echo '0'")
    
    if [ "$CONVERSIONS" -gt 0 ]; then
        print_success "Symbol conversions detected: $CONVERSIONS (crypto trading active)"
    else
        print_info "No symbol conversions in recent logs (may be normal if no crypto orders)"
    fi
    
    # Check for crypto order execution
    CRYPTO_ORDERS=$(ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} "tail -n 200 ${LOG_FILE} 2>/dev/null | grep -E 'ETH-USD|BTC-USD' | grep -E 'Order|BUY|SELL' | tail -5" || echo "")
    
    if [ -n "$CRYPTO_ORDERS" ]; then
        print_info "Recent crypto order activity:"
        echo "$CRYPTO_ORDERS" | sed 's/^/  /'
    else
        print_info "No recent crypto order activity"
    fi
}

# Main execution
main() {
    print_header "PRODUCTION TRADING MONITOR"
    print_info "Server: ${PRODUCTION_SERVER}"
    print_info "Duration: ${DURATION} seconds"
    echo ""
    
    # Run checks
    check_service_status
    check_health
    check_latest_signals
    check_api_keys
    check_crypto_trading
    check_recent_errors
    
    # Interactive monitoring
    if [ "$DURATION" -gt 0 ]; then
        monitor_logs
    fi
    
    print_header "MONITORING COMPLETE"
    print_info "For continuous monitoring, run:"
    print_info "  ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} 'tail -f ${LOG_FILE}'"
}

main "$@"


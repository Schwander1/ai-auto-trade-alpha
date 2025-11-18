#!/bin/bash
# Check All Production Status
# Comprehensive status check for all production services and issues

set -e

PRODUCTION_SERVER="178.156.194.174"
ALPINE_SERVER="91.98.153.49"
PRODUCTION_USER="root"
ALPINE_USER="root"

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

# Track issues
ISSUES=0
WARNINGS=0

# Check Argo service
check_argo_service() {
    print_header "ARGO SERVICE STATUS"
    
    if ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} "systemctl is-active --quiet argo-trading.service" 2>/dev/null; then
        print_success "Argo service is running"
        
        # Get service status
        STATUS=$(ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} "systemctl status argo-trading.service --no-pager -l | head -5" 2>/dev/null || echo "")
        if [ -n "$STATUS" ]; then
            echo "$STATUS"
        fi
    else
        print_error "Argo service is not running"
        ((ISSUES++))
    fi
}

# Check Argo health
check_argo_health() {
    print_header "ARGO HEALTH ENDPOINT"
    
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://${PRODUCTION_SERVER}:8000/health 2>/dev/null || echo "000")
    
    if [ "$HTTP_CODE" = "200" ]; then
        print_success "Health endpoint: HTTP 200"
        
        # Get health response
        HEALTH_RESPONSE=$(curl -s http://${PRODUCTION_SERVER}:8000/health 2>/dev/null || echo "")
        if [ -n "$HEALTH_RESPONSE" ]; then
            echo "$HEALTH_RESPONSE" | python3 -m json.tool 2>/dev/null | head -15 || echo "$HEALTH_RESPONSE"
        fi
    else
        print_error "Health endpoint: HTTP $HTTP_CODE"
        ((ISSUES++))
    fi
}

# Check API keys
check_api_keys() {
    print_header "API KEY STATUS"
    
    # Check xAI Grok errors
    XAI_ERRORS=$(ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} "tail -n 200 /tmp/argo-blue.log 2>/dev/null | grep -c 'xAI API error.*Invalid API key' || echo '0'" 2>/dev/null || echo "0")
    
    if [ "$XAI_ERRORS" -gt 0 ]; then
        print_warning "xAI Grok API key: Invalid ($XAI_ERRORS errors detected)"
        print_info "  Run: ./scripts/update_production_api_keys.sh"
        ((WARNINGS++))
    else
        print_success "xAI Grok API key: OK"
    fi
    
    # Check Massive errors
    MASSIVE_ERRORS=$(ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} "tail -n 200 /tmp/argo-blue.log 2>/dev/null | grep -c 'Massive API error 401.*Unknown API Key' || echo '0'" 2>/dev/null || echo "0")
    
    if [ "$MASSIVE_ERRORS" -gt 0 ]; then
        print_warning "Massive API key: Invalid ($MASSIVE_ERRORS errors detected)"
        print_info "  Run: ./scripts/update_production_api_keys.sh"
        ((WARNINGS++))
    else
        print_success "Massive API key: OK"
    fi
}

# Check latest signals
check_latest_signals() {
    print_header "LATEST SIGNALS"
    
    SIGNALS=$(curl -s "http://${PRODUCTION_SERVER}:8000/api/signals/latest?limit=5" 2>/dev/null || echo "")
    
    if [ -n "$SIGNALS" ]; then
        echo "$SIGNALS" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if isinstance(data, list) and len(data) > 0:
        print('Latest signals:')
        for s in data[:5]:
            print(f\"  {s.get('symbol', 'N/A')}: {s.get('action', 'N/A')} @ \${s.get('price', 0):.2f} (confidence: {s.get('confidence', 0):.1f}%)\")
    else:
        print('No signals found')
except:
    print('Error parsing signals')
" 2>/dev/null || print_warning "Could not parse signals"
    else
        print_warning "Could not fetch signals"
        ((WARNINGS++))
    fi
}

# Check Alpine backend
check_alpine_backend() {
    print_header "ALPINE BACKEND STATUS"
    
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://${ALPINE_SERVER}:8001/api/v1/health 2>/dev/null || echo "000")
    
    if [ "$HTTP_CODE" = "200" ]; then
        print_success "Alpine backend: Healthy (HTTP 200)"
        
        # Get health response
        HEALTH_RESPONSE=$(curl -s http://${ALPINE_SERVER}:8001/api/v1/health 2>/dev/null || echo "")
        if [ -n "$HEALTH_RESPONSE" ]; then
            echo "$HEALTH_RESPONSE" | python3 -m json.tool 2>/dev/null | head -10 || echo "$HEALTH_RESPONSE"
        fi
    else
        print_error "Alpine backend: Unhealthy (HTTP $HTTP_CODE)"
        print_info "  Run: ./scripts/check_alpine_backend.sh"
        ((ISSUES++))
    fi
    
    # Check sync endpoint
    SYNC_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://${ALPINE_SERVER}:8001/api/v1/external-signals/sync/health 2>/dev/null || echo "000")
    
    if [ "$SYNC_CODE" = "200" ]; then
        print_success "Sync endpoint: Accessible (HTTP 200)"
    elif [ "$SYNC_CODE" = "404" ]; then
        print_warning "Sync endpoint: Not found (HTTP 404) - Router may not be loaded"
        print_info "  Run: ./scripts/check_alpine_backend.sh"
        ((WARNINGS++))
    else
        print_warning "Sync endpoint: HTTP $SYNC_CODE"
        ((WARNINGS++))
    fi
}

# Check recent errors
check_recent_errors() {
    print_header "RECENT ERRORS"
    
    ERRORS=$(ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} "tail -n 100 /tmp/argo-blue.log 2>/dev/null | grep -E 'ERROR|Exception|Traceback' | tail -10" 2>/dev/null || echo "")
    
    if [ -z "$ERRORS" ]; then
        print_success "No recent errors found"
    else
        print_warning "Recent errors found:"
        echo "$ERRORS" | sed 's/^/  /'
        ((WARNINGS++))
    fi
}

# Summary
print_summary() {
    print_header "STATUS SUMMARY"
    
    if [ $ISSUES -eq 0 ] && [ $WARNINGS -eq 0 ]; then
        print_success "All systems operational! No issues detected."
        return 0
    elif [ $ISSUES -eq 0 ]; then
        print_warning "$WARNINGS warning(s) detected (non-critical)"
        echo ""
        print_info "To fix warnings, run:"
        print_info "  ./scripts/fix_all_production_issues.sh"
        return 0
    else
        print_error "$ISSUES critical issue(s) and $WARNINGS warning(s) detected"
        echo ""
        print_info "To fix all issues, run:"
        print_info "  ./scripts/fix_all_production_issues.sh"
        return 1
    fi
}

# Main execution
main() {
    print_header "PRODUCTION STATUS CHECK"
    print_info "Checking all production services and issues..."
    echo ""
    
    check_argo_service
    check_argo_health
    check_api_keys
    check_latest_signals
    check_alpine_backend
    check_recent_errors
    
    print_summary
}

main "$@"


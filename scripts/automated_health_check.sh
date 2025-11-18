#!/bin/bash
# Automated Health Check
# Runs comprehensive health checks and sends alerts if issues detected

set -e

PRODUCTION_SERVER="178.156.194.174"
PRODUCTION_USER="root"
LOG_FILE="/tmp/health_check.log"
ALERT_THRESHOLD=3  # Number of consecutive failures before alert

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

check_health_endpoint() {
    local response=$(curl -s -w "\n%{http_code}" http://${PRODUCTION_SERVER}:8000/health 2>/dev/null || echo "000")
    local http_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "200" ]; then
        local status=$(echo "$body" | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', 'unknown'))" 2>/dev/null || echo "unknown")
        if [ "$status" = "healthy" ]; then
            log_message "✅ Health check: PASSED"
            return 0
        else
            log_message "⚠️  Health check: Service status is $status"
            return 1
        fi
    else
        log_message "❌ Health check: FAILED (HTTP $http_code)"
        return 1
    fi
}

check_service_status() {
    if ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} "systemctl is-active --quiet argo-trading.service" 2>/dev/null; then
        log_message "✅ Service status: ACTIVE"
        return 0
    else
        log_message "❌ Service status: INACTIVE"
        return 1
    fi
}

check_api_key_errors() {
    local xai_errors=$(ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} "tail -n 100 /tmp/argo-blue.log 2>/dev/null | grep -c 'xAI API error.*Invalid API key' || echo '0'" 2>/dev/null)
    local massive_errors=$(ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} "tail -n 100 /tmp/argo-blue.log 2>/dev/null | grep -c 'Massive API error 401.*Unknown API Key' || echo '0'" 2>/dev/null)
    
    if [ "$xai_errors" -gt 5 ] || [ "$massive_errors" -gt 5 ]; then
        log_message "⚠️  API key errors detected: xAI=$xai_errors, Massive=$massive_errors"
        return 1
    else
        log_message "✅ API keys: OK"
        return 0
    fi
}

check_signal_generation() {
    local signals=$(curl -s "http://${PRODUCTION_SERVER}:8000/api/signals/latest?limit=1" 2>/dev/null)
    if [ $? -eq 0 ] && [ -n "$signals" ]; then
        local count=$(echo "$signals" | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data) if isinstance(data, list) else 0)" 2>/dev/null || echo "0")
        if [ "$count" -gt 0 ]; then
            log_message "✅ Signal generation: WORKING ($count signals)"
            return 0
        else
            log_message "⚠️  Signal generation: No signals found"
            return 1
        fi
    else
        log_message "❌ Signal generation: FAILED"
        return 1
    fi
}

check_trading_errors() {
    local trading_errors=$(ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} "tail -n 200 /tmp/argo-blue.log 2>/dev/null | grep -c 'Order failed\|asset.*not found' || echo '0'" 2>/dev/null)
    
    if [ "$trading_errors" -gt 10 ]; then
        log_message "⚠️  Trading errors detected: $trading_errors"
        return 1
    else
        log_message "✅ Trading: OK"
        return 0
    fi
}

main() {
    log_message "=========================================="
    log_message "Starting automated health check"
    log_message "=========================================="
    
    local failures=0
    
    check_health_endpoint || ((failures++))
    check_service_status || ((failures++))
    check_signal_generation || ((failures++))
    check_api_key_errors || ((failures++))
    check_trading_errors || ((failures++))
    
    log_message "=========================================="
    if [ $failures -eq 0 ]; then
        log_message "✅ All health checks PASSED"
        exit 0
    else
        log_message "⚠️  Health check completed with $failures issue(s)"
        exit 1
    fi
}

main "$@"


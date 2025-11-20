#!/bin/bash
# Test script for new health check endpoints
# Tests all health endpoints across all services

set -e

# Source shared libraries
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/health_check_lib.sh"

# Configuration
ENVIRONMENT="${1:-local}"

# Initialize
reset_health_counters
parse_environment_urls "$ENVIRONMENT"

echo "🧪 HEALTH ENDPOINT TESTING"
echo "=========================="
echo "Environment: $ENVIRONMENT"
echo ""

# ===== ARGO SERVICE =====
echo -e "${BLUE}🔍 ARGO SERVICE${NC}"
echo "----------------------"

test_endpoint "Health (Comprehensive)" "$ARGO_URL/api/v1/health" 200 "" 10 "status" "healthy"
test_endpoint "Health (Legacy)" "$ARGO_URL/health" 200
test_endpoint "Readiness Probe" "$ARGO_URL/api/v1/health/readiness" 200 "" 10 "status" "ready"
test_endpoint "Liveness Probe" "$ARGO_URL/api/v1/health/liveness" 200 "" 10 "status" "alive"
test_endpoint "Uptime" "$ARGO_URL/api/v1/health/uptime" 200
test_endpoint "Metrics" "$ARGO_URL/api/v1/health/metrics" 200
test_endpoint "Prometheus Metrics" "$ARGO_URL/api/v1/health/prometheus" 200
test_endpoint "Prometheus (Root)" "$ARGO_URL/metrics" 200

# Test execution dashboard endpoints if admin key is set
if [ -n "${ADMIN_API_KEY:-}" ]; then
    ADMIN_HEADER="X-Admin-API-Key: ${ADMIN_API_KEY}"
    test_endpoint "Execution Metrics" "$ARGO_URL/api/v1/execution/metrics" 200 "$ADMIN_HEADER"
    test_endpoint "Queue Status" "$ARGO_URL/api/v1/execution/queue" 200 "$ADMIN_HEADER"
    test_endpoint "Account States" "$ARGO_URL/api/v1/execution/account-states" 200 "$ADMIN_HEADER"
fi

echo ""

# ===== ALPINE BACKEND SERVICE =====
echo -e "${BLUE}🔍 ALPINE BACKEND SERVICE${NC}"
echo "----------------------"

test_endpoint "Health (Comprehensive)" "$ALPINE_BACKEND_URL/health" 200 "" 10 "status" "healthy"
test_endpoint "Readiness Probe" "$ALPINE_BACKEND_URL/health/readiness" 200 "" 10 "status" "ready"
test_endpoint "Liveness Probe" "$ALPINE_BACKEND_URL/health/liveness" 200 "" 10 "status" "alive"
test_endpoint "Metrics" "$ALPINE_BACKEND_URL/metrics" 200

echo ""

# ===== ALPINE FRONTEND SERVICE =====
echo -e "${BLUE}🔍 ALPINE FRONTEND SERVICE${NC}"
echo "----------------------"

test_endpoint "Health" "$ALPINE_FRONTEND_URL/api/health" 200 "" 10 "status" "healthy"
test_endpoint "Readiness Probe" "$ALPINE_FRONTEND_URL/api/health/readiness" 200 "" 10 "status" "ready"
test_endpoint "Liveness Probe" "$ALPINE_FRONTEND_URL/api/health/liveness" 200 "" 10 "status" "alive"

echo ""

# ===== SUMMARY =====
if print_health_summary; then
    exit 0
else
    exit 1
fi

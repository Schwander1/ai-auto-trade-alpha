#!/bin/bash
# Comprehensive health check for execution dashboard system
# Tests all execution dashboard endpoints and health checks

set -e

# Source shared libraries
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/health_check_lib.sh"

# Configuration
ENVIRONMENT="${1:-local}"

# Initialize
reset_health_counters
parse_environment_urls "$ENVIRONMENT"

# Set admin key based on environment
if [ "$ENVIRONMENT" = "production" ]; then
    ADMIN_KEY="${ADMIN_API_KEY:-}"
else
    ADMIN_KEY="${ADMIN_API_KEY:-test-admin-key}"
fi

echo "🧪 EXECUTION DASHBOARD HEALTH CHECK"
echo "===================================="
echo "Environment: $ENVIRONMENT"
echo ""

# ===== ARGO SERVICE HEALTH =====
echo -e "${BLUE}🔍 ARGO SERVICE HEALTH${NC}"
echo "----------------------"

test_endpoint "Health (Comprehensive)" "$ARGO_URL/api/v1/health" 200
test_endpoint "Health (Legacy)" "$ARGO_URL/health" 200
test_endpoint "Readiness Probe" "$ARGO_URL/api/v1/health/readiness" 200
test_endpoint "Liveness Probe" "$ARGO_URL/api/v1/health/liveness" 200
test_endpoint "Uptime" "$ARGO_URL/api/v1/health/uptime" 200
test_endpoint "Metrics" "$ARGO_URL/metrics" 200

echo ""

# ===== EXECUTION DASHBOARD ENDPOINTS =====
echo -e "${BLUE}🔍 EXECUTION DASHBOARD ENDPOINTS${NC}"
echo "----------------------"

if [ -n "$ADMIN_KEY" ]; then
    ADMIN_HEADER="X-Admin-API-Key: $ADMIN_KEY"
    test_endpoint "Execution Metrics" "$ARGO_URL/api/v1/execution/metrics" 200 "$ADMIN_HEADER"
    test_endpoint "Queue Status" "$ARGO_URL/api/v1/execution/queue" 200 "$ADMIN_HEADER"
    test_endpoint "Account States" "$ARGO_URL/api/v1/execution/account-states" 200 "$ADMIN_HEADER"
    test_endpoint "Recent Activity" "$ARGO_URL/api/v1/execution/recent-activity" 200 "$ADMIN_HEADER"
    test_endpoint "Rejection Reasons" "$ARGO_URL/api/v1/execution/rejection-reasons" 200 "$ADMIN_HEADER"
    test_endpoint "Dashboard HTML" "$ARGO_URL/api/v1/execution/dashboard" 200 "$ADMIN_HEADER"
else
    echo -e "${YELLOW}⚠️  Skipping execution dashboard endpoints (ADMIN_API_KEY not set)${NC}"
    echo "    Set ADMIN_API_KEY environment variable to test execution endpoints"
fi

echo ""

# ===== ALPINE BACKEND HEALTH =====
echo -e "${BLUE}🔍 ALPINE BACKEND HEALTH${NC}"
echo "----------------------"

test_endpoint "Health (Comprehensive)" "$ALPINE_BACKEND_URL/health" 200
test_endpoint "Readiness Probe" "$ALPINE_BACKEND_URL/health/readiness" 200
test_endpoint "Liveness Probe" "$ALPINE_BACKEND_URL/health/liveness" 200
test_endpoint "Metrics" "$ALPINE_BACKEND_URL/metrics" 200

echo ""

# ===== ALPINE FRONTEND HEALTH =====
echo -e "${BLUE}🔍 ALPINE FRONTEND HEALTH${NC}"
echo "----------------------"

test_endpoint "Health" "$ALPINE_FRONTEND_URL/api/health" 200
test_endpoint "Readiness Probe" "$ALPINE_FRONTEND_URL/api/health/readiness" 200
test_endpoint "Liveness Probe" "$ALPINE_FRONTEND_URL/api/health/liveness" 200

echo ""

# ===== EXECUTION DASHBOARD API ROUTES (Frontend) =====
echo -e "${BLUE}🔍 EXECUTION DASHBOARD API ROUTES${NC}"
echo "----------------------"

# These require authentication, so we expect 401/403
test_endpoint "Execution Metrics API" "$ALPINE_FRONTEND_URL/api/execution/metrics" 401
test_endpoint "Queue Status API" "$ALPINE_FRONTEND_URL/api/execution/queue" 401
test_endpoint "Account States API" "$ALPINE_FRONTEND_URL/api/execution/account-states" 401
test_endpoint "Rejection Reasons API" "$ALPINE_FRONTEND_URL/api/execution/rejection-reasons" 401

echo ""

# ===== SUMMARY =====
if print_health_summary; then
    exit 0
else
    exit 1
fi

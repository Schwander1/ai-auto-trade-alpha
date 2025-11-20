#!/bin/bash
# Comprehensive health check for all services
# Tests all health endpoints including execution dashboard

set -e

# Source shared libraries
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/health_check_lib.sh"

ENVIRONMENT="${1:-local}"

# Initialize
reset_health_counters
parse_environment_urls "$ENVIRONMENT"

echo "🧪 COMPREHENSIVE HEALTH CHECK"
echo "============================="
echo "Environment: $ENVIRONMENT"
echo ""

# ARGO SERVICE
echo -e "${BLUE}🔍 ARGO SERVICE${NC}"
test_endpoint "Health (Comprehensive)" "$ARGO_URL/api/v1/health" 200
test_endpoint "Health (Legacy)" "$ARGO_URL/health" 200
test_endpoint "Readiness" "$ARGO_URL/api/v1/health/readiness" 200
test_endpoint "Liveness" "$ARGO_URL/api/v1/health/liveness" 200
test_endpoint "Uptime" "$ARGO_URL/api/v1/health/uptime" 200
test_endpoint "Metrics" "$ARGO_URL/metrics" 200

# Execution Dashboard (if admin key set)
if [ -n "${ADMIN_API_KEY:-}" ]; then
    ADMIN_HEADER="X-Admin-API-Key: ${ADMIN_API_KEY}"
    test_endpoint "Execution Metrics" "$ARGO_URL/api/v1/execution/metrics" 200 "$ADMIN_HEADER"
    test_endpoint "Queue Status" "$ARGO_URL/api/v1/execution/queue" 200 "$ADMIN_HEADER"
    test_endpoint "Account States" "$ARGO_URL/api/v1/execution/account-states" 200 "$ADMIN_HEADER"
    test_endpoint "Recent Activity" "$ARGO_URL/api/v1/execution/recent-activity" 200 "$ADMIN_HEADER"
    test_endpoint "Rejection Reasons" "$ARGO_URL/api/v1/execution/rejection-reasons" 200 "$ADMIN_HEADER"
else
    echo -e "${YELLOW}  ⚠️  Skipping execution dashboard (ADMIN_API_KEY not set)${NC}"
fi

echo ""

# ALPINE BACKEND
echo -e "${BLUE}🔍 ALPINE BACKEND${NC}"
test_endpoint "Health" "$ALPINE_BACKEND_URL/health" 200
test_endpoint "Readiness" "$ALPINE_BACKEND_URL/health/readiness" 200
test_endpoint "Liveness" "$ALPINE_BACKEND_URL/health/liveness" 200
test_endpoint "Metrics" "$ALPINE_BACKEND_URL/metrics" 200

echo ""

# ALPINE FRONTEND
echo -e "${BLUE}🔍 ALPINE FRONTEND${NC}"
test_endpoint "Health" "$ALPINE_FRONTEND_URL/api/health" 200
test_endpoint "Readiness" "$ALPINE_FRONTEND_URL/api/health/readiness" 200
test_endpoint "Liveness" "$ALPINE_FRONTEND_URL/api/health/liveness" 200

echo ""

# SUMMARY
if print_health_summary; then
    exit 0
else
    exit 1
fi

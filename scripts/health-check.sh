#!/bin/bash
# Unified Health Check Script
# Primary script for testing all health endpoints across all services
# Replaces: test_all_health.sh, test_health_endpoints.sh, test_execution_dashboard_health.sh

set -e

# Source shared libraries
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/health_check_lib.sh"

ENVIRONMENT="${1:-local}"
MODE="${2:-all}"  # all, basic, execution

# Initialize
reset_health_counters
parse_environment_urls "$ENVIRONMENT"

echo "🧪 UNIFIED HEALTH CHECK"
echo "======================="
echo "Environment: $ENVIRONMENT"
echo "Mode: $MODE"
echo ""

# ARGO SERVICE
if [ "$MODE" = "all" ] || [ "$MODE" = "basic" ]; then
    echo -e "${BLUE}🔍 ARGO SERVICE${NC}"
    test_endpoint "Health (Comprehensive)" "$ARGO_URL/api/v1/health" 200
    test_endpoint "Health (Legacy)" "$ARGO_URL/health" 200
    test_endpoint "Readiness" "$ARGO_URL/api/v1/health/readiness" 200
    test_endpoint "Liveness" "$ARGO_URL/api/v1/health/liveness" 200
    test_endpoint "Uptime" "$ARGO_URL/api/v1/health/uptime" 200
    test_endpoint "Metrics" "$ARGO_URL/metrics" 200
    echo ""
fi

# EXECUTION DASHBOARD
if [ "$MODE" = "all" ] || [ "$MODE" = "execution" ]; then
    if [ -n "${ADMIN_API_KEY:-}" ]; then
        echo -e "${BLUE}🔍 EXECUTION DASHBOARD${NC}"
        ADMIN_HEADER="X-Admin-API-Key: ${ADMIN_API_KEY}"
        test_endpoint "Execution Metrics" "$ARGO_URL/api/v1/execution/metrics" 200 "$ADMIN_HEADER"
        test_endpoint "Queue Status" "$ARGO_URL/api/v1/execution/queue" 200 "$ADMIN_HEADER"
        test_endpoint "Account States" "$ARGO_URL/api/v1/execution/account-states" 200 "$ADMIN_HEADER"
        test_endpoint "Recent Activity" "$ARGO_URL/api/v1/execution/recent-activity" 200 "$ADMIN_HEADER"
        test_endpoint "Rejection Reasons" "$ARGO_URL/api/v1/execution/rejection-reasons" 200 "$ADMIN_HEADER"
        echo ""
    else
        echo -e "${YELLOW}⚠️  Skipping execution dashboard (ADMIN_API_KEY not set)${NC}"
        echo ""
    fi
fi

# ALPINE BACKEND
if [ "$MODE" = "all" ] || [ "$MODE" = "basic" ]; then
    echo -e "${BLUE}🔍 ALPINE BACKEND${NC}"
    test_endpoint "Health" "$ALPINE_BACKEND_URL/health" 200
    test_endpoint "Readiness" "$ALPINE_BACKEND_URL/health/readiness" 200
    test_endpoint "Liveness" "$ALPINE_BACKEND_URL/health/liveness" 200
    test_endpoint "Metrics" "$ALPINE_BACKEND_URL/metrics" 200
    echo ""
fi

# ALPINE FRONTEND
if [ "$MODE" = "all" ] || [ "$MODE" = "basic" ]; then
    echo -e "${BLUE}🔍 ALPINE FRONTEND${NC}"
    test_endpoint "Health" "$ALPINE_FRONTEND_URL/api/health" 200
    test_endpoint "Readiness" "$ALPINE_FRONTEND_URL/api/health/readiness" 200
    test_endpoint "Liveness" "$ALPINE_FRONTEND_URL/api/health/liveness" 200
    echo ""
fi

# SUMMARY
if print_health_summary; then
    exit 0
else
    exit 1
fi

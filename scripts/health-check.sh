#!/bin/bash
# Unified Health Check Script
# Primary script for testing all health endpoints across all services
# Replaces: test_all_health.sh, test_health_endpoints.sh, test_execution_dashboard_health.sh

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

ENVIRONMENT="${1:-local}"
MODE="${2:-all}"  # all, basic, execution

if [ "$ENVIRONMENT" = "production" ]; then
    ARGO_URL="http://178.156.194.174:8000"
    ALPINE_BACKEND_URL="http://91.98.153.49:8001"
    ALPINE_FRONTEND_URL="http://91.98.153.49:3000"
else
    ARGO_URL="http://localhost:8000"
    ALPINE_BACKEND_URL="http://localhost:9001"
    ALPINE_FRONTEND_URL="http://localhost:3000"
fi

FAILED=0
PASSED=0
TOTAL=0

test_endpoint() {
    local name=$1
    local url=$2
    local expected_status=${3:-200}
    local headers=${4:-""}

    TOTAL=$((TOTAL + 1))
    echo -n "  Testing $name... "

    if [ -n "$headers" ]; then
        response=$(curl -s -w "\n%{http_code}" --max-time 10 -H "$headers" "$url" 2>&1)
    else
        response=$(curl -s -w "\n%{http_code}" --max-time 10 "$url" 2>&1)
    fi

    http_code=$(echo "$response" | tail -n1)

    if [ "$http_code" = "$expected_status" ]; then
        echo -e "${GREEN}✅ PASS${NC} (HTTP $http_code)"
        PASSED=$((PASSED + 1))
        return 0
    else
        echo -e "${RED}❌ FAIL${NC} (HTTP $http_code, expected $expected_status)"
        FAILED=$((FAILED + 1))
        return 1
    fi
}

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
echo "📊 SUMMARY"
echo "======================="
echo -e "Total: $TOTAL | ${GREEN}✅ Passed: $PASSED${NC} | ${RED}❌ Failed: $FAILED${NC}"

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL HEALTH CHECKS PASSED!${NC}"
    exit 0
else
    echo -e "${RED}⚠️  SOME CHECKS FAILED${NC}"
    exit 1
fi

#!/bin/bash
# Comprehensive health check for execution dashboard system
# Tests all execution dashboard endpoints and health checks

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT="${1:-local}"

if [ "$ENVIRONMENT" = "production" ]; then
    ARGO_URL="http://178.156.194.174:8000"
    ALPINE_BACKEND_URL="http://91.98.153.49:8001"
    ALPINE_FRONTEND_URL="http://91.98.153.49:3000"
    ADMIN_KEY="${ADMIN_API_KEY:-}"
else
    ARGO_URL="http://localhost:8000"
    ALPINE_BACKEND_URL="http://localhost:9001"
    ALPINE_FRONTEND_URL="http://localhost:3000"
    ADMIN_KEY="${ADMIN_API_KEY:-test-admin-key}"
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
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" = "$expected_status" ]; then
        echo -e "${GREEN}✅ PASS${NC} (HTTP $http_code)"
        PASSED=$((PASSED + 1))
        return 0
    else
        echo -e "${RED}❌ FAIL${NC} (HTTP $http_code, expected $expected_status)"
        echo "    Response: $(echo "$body" | head -1)"
        FAILED=$((FAILED + 1))
        return 1
    fi
}

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
echo "📊 TEST SUMMARY"
echo "=========================="
echo -e "Total Tests: $TOTAL"
echo -e "${GREEN}✅ Passed: $PASSED${NC}"
echo -e "${RED}❌ Failed: $FAILED${NC}"

if [ $FAILED -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 ALL HEALTH CHECKS PASSED!${NC}"
    exit 0
else
    echo ""
    echo -e "${RED}⚠️  SOME HEALTH CHECKS FAILED${NC}"
    exit 1
fi

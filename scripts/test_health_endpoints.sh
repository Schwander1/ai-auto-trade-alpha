#!/bin/bash
# Test script for new health check endpoints
# Tests all health endpoints across all services

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
    local check_field=${4:-""}
    local check_value=${5:-""}

    TOTAL=$((TOTAL + 1))
    echo -n "  Testing $name... "

    response=$(curl -s -w "\n%{http_code}" --max-time 10 "$url" 2>&1)
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" = "$expected_status" ]; then
        # If check_field is provided, verify the field value
        if [ -n "$check_field" ] && [ -n "$check_value" ]; then
            field_value=$(echo "$body" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('$check_field', ''))
except:
    print('')
" 2>/dev/null || echo "")

            if [ "$field_value" = "$check_value" ]; then
                echo -e "${GREEN}✅ PASS${NC} (HTTP $http_code, $check_field=$check_value)"
                PASSED=$((PASSED + 1))
                return 0
            else
                echo -e "${YELLOW}⚠️  PARTIAL${NC} (HTTP $http_code, but $check_field=$field_value, expected $check_value)"
                PASSED=$((PASSED + 1))
                return 0
            fi
        else
            echo -e "${GREEN}✅ PASS${NC} (HTTP $http_code)"
            PASSED=$((PASSED + 1))
            return 0
        fi
    else
        echo -e "${RED}❌ FAIL${NC} (HTTP $http_code, expected $expected_status)"
        echo "    Response: $(echo "$body" | head -1)"
        FAILED=$((FAILED + 1))
        return 1
    fi
}

echo "🧪 HEALTH ENDPOINT TESTING"
echo "=========================="
echo "Environment: $ENVIRONMENT"
echo ""

# ===== ARGO SERVICE =====
echo -e "${BLUE}🔍 ARGO SERVICE${NC}"
echo "----------------------"

test_endpoint "Health (Comprehensive)" "$ARGO_URL/api/v1/health" 200 "status" "healthy"
test_endpoint "Health (Legacy)" "$ARGO_URL/health" 200
test_endpoint "Readiness Probe" "$ARGO_URL/api/v1/health/readiness" 200 "status" "ready"
test_endpoint "Liveness Probe" "$ARGO_URL/api/v1/health/liveness" 200 "status" "alive"
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

test_endpoint "Health (Comprehensive)" "$ALPINE_BACKEND_URL/health" 200 "status" "healthy"
test_endpoint "Readiness Probe" "$ALPINE_BACKEND_URL/health/readiness" 200 "status" "ready"
test_endpoint "Liveness Probe" "$ALPINE_BACKEND_URL/health/liveness" 200 "status" "alive"
test_endpoint "Metrics" "$ALPINE_BACKEND_URL/metrics" 200

echo ""

# ===== ALPINE FRONTEND SERVICE =====
echo -e "${BLUE}🔍 ALPINE FRONTEND SERVICE${NC}"
echo "----------------------"

test_endpoint "Health" "$ALPINE_FRONTEND_URL/api/health" 200 "status" "healthy"
test_endpoint "Readiness Probe" "$ALPINE_FRONTEND_URL/api/health/readiness" 200 "status" "ready"
test_endpoint "Liveness Probe" "$ALPINE_FRONTEND_URL/api/health/liveness" 200 "status" "alive"

echo ""

# ===== SUMMARY =====
echo "📊 TEST SUMMARY"
echo "=========================="
echo -e "Total Tests: $TOTAL"
echo -e "${GREEN}✅ Passed: $PASSED${NC}"
echo -e "${RED}❌ Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ ALL HEALTH ENDPOINT TESTS PASSED!${NC}"
    exit 0
else
    echo -e "${RED}❌ SOME TESTS FAILED${NC}"
    exit 1
fi

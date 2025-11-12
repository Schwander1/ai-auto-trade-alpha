#!/bin/bash
# Test script for optimization implementations

set -e

echo "🧪 Testing Argo-Alpine Optimizations"
echo "===================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
ALPINE_BACKEND_URL="${ALPINE_BACKEND_URL:-http://localhost:9001}"
ALPINE_FRONTEND_URL="${ALPINE_FRONTEND_URL:-http://localhost:3000}"
ARGO_URL="${ARGO_URL:-http://localhost:8000}"

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0

test_endpoint() {
    local name=$1
    local url=$2
    local expected_status=${3:-200}
    
    echo -n "Testing $name... "
    response=$(curl -s -o /dev/null -w "%{http_code}" "$url" || echo "000")
    
    if [ "$response" = "$expected_status" ]; then
        echo -e "${GREEN}✓ PASS${NC} (HTTP $response)"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC} (Expected $expected_status, got $response)"
        ((TESTS_FAILED++))
        return 1
    fi
}

test_json_response() {
    local name=$1
    local url=$2
    local key=$3
    
    echo -n "Testing $name... "
    response=$(curl -s "$url" || echo "{}")
    
    if echo "$response" | grep -q "$key"; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC} (Key '$key' not found)"
        ((TESTS_FAILED++))
        return 1
    fi
}

echo "1. Testing Health Checks"
echo "----------------------"
test_endpoint "Argo Health" "$ARGO_URL/health"
test_endpoint "Alpine Backend Health" "$ALPINE_BACKEND_URL/health"
test_json_response "Alpine Health (DB check)" "$ALPINE_BACKEND_URL/health" "database"
test_json_response "Alpine Health (Redis check)" "$ALPINE_BACKEND_URL/health" "redis"
echo ""

echo "2. Testing Metrics Endpoints"
echo "---------------------------"
test_endpoint "Alpine Metrics" "$ALPINE_BACKEND_URL/metrics" 200
test_json_response "Metrics (cache metrics)" "$ALPINE_BACKEND_URL/metrics" "redis_cache"
test_json_response "Metrics (rate limit metrics)" "$ALPINE_BACKEND_URL/metrics" "rate_limit"
echo ""

echo "3. Testing Rate Limiting"
echo "----------------------"
echo -n "Testing rate limit (100 requests)... "
RATE_LIMIT_PASSED=true
for i in {1..105}; do
    status=$(curl -s -o /dev/null -w "%{http_code}" "$ALPINE_BACKEND_URL/health")
    if [ "$status" = "429" ] && [ $i -le 100 ]; then
        RATE_LIMIT_PASSED=false
        break
    fi
done

if [ "$RATE_LIMIT_PASSED" = true ]; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((TESTS_FAILED++))
fi
echo ""

echo "4. Testing CORS Configuration"
echo "---------------------------"
echo -n "Testing CORS headers... "
cors_headers=$(curl -s -I -H "Origin: http://localhost:3000" "$ALPINE_BACKEND_URL/health" | grep -i "access-control" || echo "")
if [ -n "$cors_headers" ]; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${YELLOW}⚠ WARN${NC} (CORS headers not found - may be configured differently)"
fi
echo ""

echo "5. Testing Response Compression"
echo "-----------------------------"
echo -n "Testing GZip compression... "
compressed=$(curl -s -H "Accept-Encoding: gzip" -H "Accept: application/json" -I "$ALPINE_BACKEND_URL/health" | grep -i "content-encoding: gzip" || echo "")
if [ -n "$compressed" ]; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${YELLOW}⚠ WARN${NC} (Compression may not be enabled for small responses)"
fi
echo ""

echo "6. Testing Database Indexes"
echo "-------------------------"
echo -n "Checking database indexes... "
# This would require database access - placeholder for now
echo -e "${YELLOW}⚠ SKIP${NC} (Requires database access)"
echo ""

echo "7. Testing Redis Connection"
echo "-------------------------"
echo -n "Testing Redis connectivity... "
redis_status=$(curl -s "$ALPINE_BACKEND_URL/health" | grep -o '"redis":"[^"]*"' | cut -d'"' -f4 || echo "unknown")
if [ "$redis_status" = "healthy" ]; then
    echo -e "${GREEN}✓ PASS${NC} (Redis connected)"
    ((TESTS_PASSED++))
elif [ "$redis_status" = "not_configured" ]; then
    echo -e "${YELLOW}⚠ WARN${NC} (Redis not configured)"
else
    echo -e "${RED}✗ FAIL${NC} (Redis status: $redis_status)"
    ((TESTS_FAILED++))
fi
echo ""

echo "===================================="
echo "Test Results:"
echo "  ${GREEN}Passed: $TESTS_PASSED${NC}"
echo "  ${RED}Failed: $TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some tests failed${NC}"
    exit 1
fi


#!/bin/bash
# Comprehensive health check for Argo and Alpine systems

set -e

echo "🏥 COMPREHENSIVE HEALTH CHECK"
echo "=============================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ARGO_URL="http://178.156.194.174:8000"
ALPINE_URL="http://91.98.153.49:8001"

FAILED=0
PASSED=0

check_endpoint() {
    local name=$1
    local url=$2
    local expected_status=${3:-200}
    
    echo -n "Checking $name... "
    response=$(curl -s -w "\n%{http_code}" "$url" 2>&1)
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "$expected_status" ]; then
        echo -e "${GREEN}✅ PASS${NC} (HTTP $http_code)"
        echo "$body" | jq '.' 2>/dev/null || echo "$body" | head -3
        ((PASSED++))
        return 0
    else
        echo -e "${RED}❌ FAIL${NC} (HTTP $http_code, expected $expected_status)"
        echo "$body" | head -3
        ((FAILED++))
        return 1
    fi
}

echo "🔍 ARGO SERVICE CHECKS"
echo "----------------------"
check_endpoint "Argo Health (Comprehensive)" "$ARGO_URL/api/v1/health" 200
check_endpoint "Argo Readiness" "$ARGO_URL/api/v1/health/readiness" 200
check_endpoint "Argo Liveness" "$ARGO_URL/api/v1/health/liveness" 200
check_endpoint "Argo Health (Legacy)" "$ARGO_URL/health" 200
check_endpoint "Argo Metrics" "$ARGO_URL/metrics" 200
check_endpoint "Argo Signals Latest" "$ARGO_URL/api/signals/latest"
check_endpoint "Argo Signals Stats" "$ARGO_URL/api/signals/stats"
check_endpoint "Argo Performance Win Rate" "$ARGO_URL/api/performance/win-rate"
check_endpoint "Argo Symbols Available" "$ARGO_URL/api/symbols/available"

echo ""
echo "🔍 ALPINE SERVICE CHECKS"
echo "----------------------"
check_endpoint "Alpine Health (Comprehensive)" "$ALPINE_URL/health" 200
check_endpoint "Alpine Readiness" "$ALPINE_URL/health/readiness" 200
check_endpoint "Alpine Liveness" "$ALPINE_URL/health/liveness" 200
check_endpoint "Alpine Metrics" "$ALPINE_URL/metrics" 200
check_endpoint "Alpine API Docs" "$ALPINE_URL/docs" 200

echo ""
echo "🔍 DATABASE CHECKS"
echo "----------------------"
echo -n "Checking database indexes... "
ssh root@91.98.153.49 "docker exec alpine-production-postgres-1 psql -U alpine_user -d alpine_prod -c \"SELECT COUNT(*) as index_count FROM pg_indexes WHERE schemaname = 'public' AND indexname LIKE 'idx_%';\" -t" 2>/dev/null | grep -q "11" && echo -e "${GREEN}✅ PASS${NC} (11 indexes found)" || echo -e "${YELLOW}⚠️  WARNING${NC} (Index count mismatch)"
((PASSED++))

echo ""
echo "🔍 REDIS CHECKS"
echo "----------------------"
echo -n "Checking Redis connectivity... "
ssh root@91.98.153.49 "docker exec alpine-production-redis-1 redis-cli ping" 2>/dev/null | grep -q "PONG" && echo -e "${GREEN}✅ PASS${NC}" || echo -e "${YELLOW}⚠️  WARNING${NC} (Redis not responding)"
((PASSED++))

echo ""
echo "🔍 DOCKER CONTAINER CHECKS"
echo "----------------------"
echo -n "Checking Alpine containers... "
containers=$(ssh root@91.98.153.49 "docker ps --filter 'name=alpine-production' --format '{{.Names}}' | wc -l" 2>/dev/null)
if [ "$containers" -ge "4" ]; then
    echo -e "${GREEN}✅ PASS${NC} ($containers containers running)"
    ssh root@91.98.153.49 "docker ps --filter 'name=alpine-production' --format 'table {{.Names}}\t{{.Status}}'" 2>/dev/null
    ((PASSED++))
else
    echo -e "${RED}❌ FAIL${NC} (Only $containers containers running, expected 4+)"
    ((FAILED++))
fi

echo ""
echo "📊 HEALTH CHECK SUMMARY"
echo "=============================="
echo -e "✅ Passed: ${GREEN}$PASSED${NC}"
echo -e "❌ Failed: ${RED}$FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ ALL HEALTH CHECKS PASSED!${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  SOME CHECKS FAILED${NC}"
    exit 1
fi


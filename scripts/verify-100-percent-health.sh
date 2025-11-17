#!/bin/bash
# Comprehensive 100% Health Verification Script
# Verifies all services, optimizations, and performance metrics

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ENVIRONMENT="${1:-local}"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Counters
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0
WARNINGS=0

# URLs based on environment
if [ "$ENVIRONMENT" = "production" ]; then
    ARGO_URL="http://178.156.194.174:8000"
    ALPINE_BACKEND_URL="http://91.98.153.49:8001"
    ALPINE_FRONTEND_URL="http://91.98.153.49:3000"
else
    ARGO_URL="http://localhost:8000"
    ALPINE_BACKEND_URL="http://localhost:9001"
    ALPINE_FRONTEND_URL="http://localhost:3000"
fi

print_header() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
}

check_pass() {
    ((TOTAL_CHECKS++))
    ((PASSED_CHECKS++))
    echo -e "  ${GREEN}✅ PASS${NC} - $1"
}

check_fail() {
    ((TOTAL_CHECKS++))
    ((FAILED_CHECKS++))
    echo -e "  ${RED}❌ FAIL${NC} - $1"
    return 1
}

check_warn() {
    ((TOTAL_CHECKS++))
    ((WARNINGS++))
    echo -e "  ${YELLOW}⚠️  WARN${NC} - $1"
}

check_endpoint() {
    local name=$1
    local url=$2
    local expected_status=${3:-200}
    
    response=$(curl -s -w "\n%{http_code}" "$url" 2>&1 || echo "ERROR\n000")
    http_code=$(echo "$response" | tail -n1)
    
    if [ "$http_code" = "$expected_status" ]; then
        check_pass "$name (HTTP $http_code)"
        return 0
    else
        check_fail "$name (HTTP $http_code, expected $expected_status)"
        return 1
    fi
}

check_response_time() {
    local name=$1
    local url=$2
    local max_time=$3
    
    start_time=$(date +%s%N)
    response=$(curl -s -w "\n%{http_code}" "$url" 2>&1 || echo "ERROR\n000")
    end_time=$(date +%s%N)
    http_code=$(echo "$response" | tail -n1)
    
    duration_ms=$(( (end_time - start_time) / 1000000 ))
    
    if [ "$http_code" = "200" ] && [ "$duration_ms" -lt "$max_time" ]; then
        check_pass "$name (${duration_ms}ms < ${max_time}ms)"
        return 0
    elif [ "$http_code" = "200" ]; then
        check_warn "$name (${duration_ms}ms >= ${max_time}ms - slow but working)"
        return 0
    else
        check_fail "$name (HTTP $http_code)"
        return 1
    fi
}

echo ""
echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║    100% HEALTH VERIFICATION - $ENVIRONMENT${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════╝${NC}"

# ============================================================================
# 1. SERVICE HEALTH CHECKS
# ============================================================================
print_header "1. SERVICE HEALTH CHECKS"

echo ""
echo "🔍 Argo Service:"
check_endpoint "Health Endpoint" "$ARGO_URL/health"
check_endpoint "Metrics Endpoint" "$ARGO_URL/metrics"

echo ""
echo "🔍 Alpine Backend:"
check_endpoint "Health Endpoint" "$ALPINE_BACKEND_URL/health"
check_endpoint "API Docs" "$ALPINE_BACKEND_URL/docs"

echo ""
echo "🔍 Alpine Frontend:"
check_endpoint "Frontend Homepage" "$ALPINE_FRONTEND_URL/"

# ============================================================================
# 2. OPTIMIZATION VERIFICATION
# ============================================================================
print_header "2. OPTIMIZATION VERIFICATION"

echo ""
echo "📊 Pagination Optimization:"
# Test pagination endpoint with cache
check_response_time "Signals Pagination (offset=0)" \
    "$ALPINE_BACKEND_URL/api/v1/signals/subscribed?limit=10&offset=0" \
    200

check_response_time "Signals Pagination (offset=100)" \
    "$ALPINE_BACKEND_URL/api/v1/signals/subscribed?limit=10&offset=100" \
    200

echo ""
echo "🗄️  Database Query Optimization:"
# Test admin endpoint (should be cached)
check_response_time "Admin Users List" \
    "$ALPINE_BACKEND_URL/api/v1/admin/users?limit=20" \
    200

echo ""
echo "💾 Redis Cache:"
# Check if Redis is mentioned in health check
health_response=$(curl -s "$ALPINE_BACKEND_URL/health" 2>/dev/null || echo "")
if echo "$health_response" | grep -q "redis.*healthy"; then
    check_pass "Redis connection healthy"
elif echo "$health_response" | grep -q "redis"; then
    check_warn "Redis status in health check (may not be configured)"
else
    check_warn "Redis status not found in health check"
fi

# ============================================================================
# 3. PERFORMANCE METRICS
# ============================================================================
print_header "3. PERFORMANCE METRICS"

echo ""
echo "⚡ API Response Times:"
check_response_time "Signals Endpoint" \
    "$ALPINE_BACKEND_URL/api/v1/signals/subscribed?limit=10" \
    100

check_response_time "Health Endpoint" \
    "$ALPINE_BACKEND_URL/health" \
    100

# ============================================================================
# 4. DOCKER BUILD OPTIMIZATION
# ============================================================================
print_header "4. DOCKER BUILD OPTIMIZATION"

echo ""
echo "🐳 Docker Images:"
if [ -f "$PROJECT_ROOT/alpine-backend/backend/Dockerfile" ]; then
    if grep -q "FROM.*AS builder" "$PROJECT_ROOT/alpine-backend/backend/Dockerfile"; then
        check_pass "Multi-stage build configured (alpine-backend)"
    else
        check_fail "Multi-stage build not found (alpine-backend)"
    fi
fi

if [ -f "$PROJECT_ROOT/argo/Dockerfile" ]; then
    if grep -q "FROM.*AS builder" "$PROJECT_ROOT/argo/Dockerfile"; then
        check_pass "Multi-stage build configured (argo)"
    else
        check_fail "Multi-stage build not found (argo)"
    fi
fi

if [ -f "$PROJECT_ROOT/alpine-backend/backend/.dockerignore" ]; then
    check_pass ".dockerignore file exists (alpine-backend)"
else
    check_warn ".dockerignore file not found (alpine-backend)"
fi

# ============================================================================
# 5. FRONTEND OPTIMIZATION
# ============================================================================
print_header "5. FRONTEND OPTIMIZATION"

echo ""
echo "📦 Frontend Lazy Loading:"
if [ -f "$PROJECT_ROOT/alpine-frontend/app/page.tsx" ]; then
    if grep -q "dynamic.*import" "$PROJECT_ROOT/alpine-frontend/app/page.tsx"; then
        check_pass "Lazy loading implemented (home page)"
    else
        check_fail "Lazy loading not found (home page)"
    fi
fi

if [ -f "$PROJECT_ROOT/alpine-frontend/app/dashboard/page.tsx" ]; then
    if grep -q "dynamic.*import" "$PROJECT_ROOT/alpine-frontend/app/dashboard/page.tsx"; then
        check_pass "Lazy loading implemented (dashboard)"
    else
        check_warn "Lazy loading not found (dashboard)"
    fi
fi

# ============================================================================
# 6. TURBO CACHE
# ============================================================================
print_header "6. TURBO REMOTE CACHE"

echo ""
echo "⚡ Turbo Configuration:"
if [ -f "$PROJECT_ROOT/turbo.json" ]; then
    if grep -q '"enabled":\s*true' "$PROJECT_ROOT/turbo.json"; then
        check_pass "Turbo remote cache enabled"
    else
        check_warn "Turbo remote cache not enabled"
    fi
else
    check_warn "turbo.json not found"
fi

# ============================================================================
# 7. DATABASE OPTIMIZATION
# ============================================================================
print_header "7. DATABASE OPTIMIZATION"

echo ""
echo "🔍 Query Cache Utility:"
if [ -f "$PROJECT_ROOT/alpine-backend/backend/core/query_cache.py" ]; then
    check_pass "Query cache utility exists"
else
    check_warn "Query cache utility not found"
fi

# ============================================================================
# SUMMARY
# ============================================================================
print_header "VERIFICATION SUMMARY"

echo ""
echo "Total Checks: $TOTAL_CHECKS"
echo -e "  ${GREEN}Passed: $PASSED_CHECKS${NC}"
echo -e "  ${RED}Failed: $FAILED_CHECKS${NC}"
echo -e "  ${YELLOW}Warnings: $WARNINGS${NC}"

if [ $FAILED_CHECKS -eq 0 ]; then
    echo ""
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║           ✅ 100% HEALTH VERIFIED - ALL SYSTEMS GO!          ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    exit 0
else
    echo ""
    echo -e "${RED}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║        ❌ HEALTH CHECK FAILED - REVIEW ISSUES ABOVE          ║${NC}"
    echo -e "${RED}╚═══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    exit 1
fi

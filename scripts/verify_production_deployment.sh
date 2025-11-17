#!/bin/bash
# Production Deployment Verification Script
# Verifies all health check improvements are properly deployed to production

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Production URLs
ARGO_URL="http://178.156.194.174:8000"
ALPINE_BACKEND_URL="http://91.98.153.49:8001"
ALPINE_FRONTEND_URL="http://91.98.153.49:3000"

FAILED=0
PASSED=0
WARNINGS=0

print_header() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
    ((PASSED++))
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
    ((FAILED++))
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    ((WARNINGS++))
}

test_endpoint() {
    local name=$1
    local url=$2
    local expected_status=${3:-200}
    local check_field=${4:-""}
    local check_value=${5:-""}
    
    echo -n "  Testing $name... "
    
    response=$(curl -s -w "\n%{http_code}" --max-time 10 "$url" 2>&1)
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "$expected_status" ]; then
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
                print_success "$name (HTTP $http_code, $check_field=$check_value)"
                return 0
            else
                print_warning "$name (HTTP $http_code, but $check_field=$field_value, expected $check_value)"
                return 0
            fi
        else
            print_success "$name (HTTP $http_code)"
            return 0
        fi
    else
        print_error "$name (HTTP $http_code, expected $expected_status)"
        return 1
    fi
}

print_header "PRODUCTION DEPLOYMENT VERIFICATION"
echo "Date: $(date)"
echo ""

# ===== ARGO SERVICE VERIFICATION =====
print_header "1. ARGO SERVICE VERIFICATION"

echo "Testing comprehensive health endpoint..."
test_endpoint "Health (Comprehensive)" "$ARGO_URL/api/v1/health" 200 "status" "healthy"

echo "Testing database check in health response..."
db_status=$(curl -s "$ARGO_URL/api/v1/health" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    services = data.get('services', {})
    db_status = services.get('database', 'unknown')
    print(db_status)
except:
    print('unknown')
" 2>/dev/null || echo "unknown")

if [ "$db_status" = "healthy" ]; then
    print_success "Database check is working (status: $db_status)"
elif [ "$db_status" = "unhealthy" ]; then
    print_error "Database check failed (status: $db_status)"
else
    print_warning "Database check status unclear (status: $db_status)"
fi

test_endpoint "Readiness Probe" "$ARGO_URL/api/v1/health/readiness" 200 "status" "ready"
test_endpoint "Liveness Probe" "$ARGO_URL/api/v1/health/liveness" 200 "status" "alive"
test_endpoint "Uptime" "$ARGO_URL/api/v1/health/uptime" 200
test_endpoint "Prometheus Metrics" "$ARGO_URL/metrics" 200

# ===== ALPINE BACKEND VERIFICATION =====
print_header "2. ALPINE BACKEND VERIFICATION"

test_endpoint "Health (Comprehensive)" "$ALPINE_BACKEND_URL/health" 200 "status" "healthy"

echo "Testing system metrics in health response..."
has_system=$(curl -s "$ALPINE_BACKEND_URL/health" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    system = data.get('system', {})
    print('yes' if system else 'no')
except:
    print('no')
" 2>/dev/null || echo "no")

if [ "$has_system" = "yes" ]; then
    print_success "System metrics are included in health response"
else
    print_warning "System metrics may not be included"
fi

echo "Testing uptime in health response..."
has_uptime=$(curl -s "$ALPINE_BACKEND_URL/health" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    uptime = data.get('uptime_seconds', None)
    print('yes' if uptime is not None else 'no')
except:
    print('no')
" 2>/dev/null || echo "no")

if [ "$has_uptime" = "yes" ]; then
    print_success "Uptime tracking is working"
else
    print_warning "Uptime tracking may not be working"
fi

test_endpoint "Readiness Probe" "$ALPINE_BACKEND_URL/health/readiness" 200 "status" "ready"
test_endpoint "Liveness Probe" "$ALPINE_BACKEND_URL/health/liveness" 200 "status" "alive"
test_endpoint "Metrics" "$ALPINE_BACKEND_URL/metrics" 200

# ===== ALPINE FRONTEND VERIFICATION =====
print_header "3. ALPINE FRONTEND VERIFICATION"

test_endpoint "Health" "$ALPINE_FRONTEND_URL/api/health" 200 "status" "healthy"
test_endpoint "Readiness Probe" "$ALPINE_FRONTEND_URL/api/health/readiness" 200 "status" "ready"
test_endpoint "Liveness Probe" "$ALPINE_FRONTEND_URL/api/health/liveness" 200 "status" "alive"

# ===== CONFIGURATION VERIFICATION =====
print_header "4. CONFIGURATION VERIFICATION"

echo "Checking Prometheus configuration..."
if [ -f "infrastructure/monitoring/prometheus.yml" ]; then
    if grep -q "health-checks" infrastructure/monitoring/prometheus.yml; then
        print_success "Prometheus health check monitoring configured"
    else
        print_error "Prometheus health check monitoring not configured"
    fi
else
    print_warning "Prometheus configuration file not found"
fi

echo "Checking alert configuration..."
if [ -f "infrastructure/monitoring/alerts.yml" ]; then
    if grep -q "HealthCheckFailed" infrastructure/monitoring/alerts.yml; then
        print_success "Health check alerts configured"
    else
        print_error "Health check alerts not configured"
    fi
else
    print_warning "Alert configuration file not found"
fi

echo "Checking Docker Compose health probes..."
if [ -f "argo/docker-compose.yml" ]; then
    if grep -q "health/readiness" argo/docker-compose.yml; then
        print_success "Argo Docker health probe configured"
    else
        print_warning "Argo Docker health probe may not be configured"
    fi
else
    print_warning "Argo docker-compose.yml not found"
fi

if [ -f "alpine-backend/docker-compose.production.yml" ]; then
    if grep -q "health/readiness" alpine-backend/docker-compose.production.yml; then
        print_success "Alpine Backend Docker health probes configured"
    else
        print_warning "Alpine Backend Docker health probes may not be configured"
    fi
else
    print_warning "Alpine Backend docker-compose.production.yml not found"
fi

# ===== SUMMARY =====
print_header "VERIFICATION SUMMARY"

echo -e "Total Checks: $((PASSED + FAILED + WARNINGS))"
echo -e "${GREEN}✅ Passed: $PASSED${NC}"
echo -e "${RED}❌ Failed: $FAILED${NC}"
echo -e "${YELLOW}⚠️  Warnings: $WARNINGS${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    if [ $WARNINGS -eq 0 ]; then
        echo -e "${GREEN}✅ ALL CHECKS PASSED! Production deployment verified.${NC}"
        exit 0
    else
        echo -e "${YELLOW}⚠️  ALL CRITICAL CHECKS PASSED, but some warnings exist.${NC}"
        exit 0
    fi
else
    echo -e "${RED}❌ SOME CHECKS FAILED. Please review and fix issues.${NC}"
    exit 1
fi


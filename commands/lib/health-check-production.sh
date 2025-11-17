#!/bin/bash
# Health check for production services
set -e

PROJECT="${1:-all}"

ARGO_URL="http://178.156.194.174:8000"
ALPINE_URL="http://91.98.153.49:8001"

check_endpoint() {
    local name=$1
    local url=$2
    local endpoint=$3
    
    echo -n "  Checking $name... "
    response=$(curl -s -w "\n%{http_code}" "${url}${endpoint}" 2>&1)
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "200" ]; then
        echo "✅ PASS"
        if echo "$body" | grep -q "healthy"; then
            echo "$body" | python3 -m json.tool 2>/dev/null | grep -E '(status|version|uptime)' | head -3 || true
        fi
        return 0
    else
        echo "❌ FAIL (HTTP $http_code)"
        return 1
    fi
}

echo "🏥 Production Health Check"
echo "=========================="
echo ""

FAILED=0

if [ "$PROJECT" = "all" ] || [ "$PROJECT" = "argo" ]; then
    echo "🔍 Argo Service:"
    check_endpoint "Health (Comprehensive)" "$ARGO_URL" "/api/v1/health" || ((FAILED++))
    check_endpoint "Readiness" "$ARGO_URL" "/api/v1/health/readiness" || ((FAILED++))
    check_endpoint "Liveness" "$ARGO_URL" "/api/v1/health/liveness" || ((FAILED++))
    check_endpoint "Signals" "$ARGO_URL" "/api/signals/latest?limit=1" || ((FAILED++))
    echo ""
fi

if [ "$PROJECT" = "all" ] || [ "$PROJECT" = "alpine" ]; then
    echo "🔍 Alpine Backend Service:"
    check_endpoint "Health (Comprehensive)" "$ALPINE_URL" "/health" || ((FAILED++))
    check_endpoint "Readiness" "$ALPINE_URL" "/health/readiness" || ((FAILED++))
    check_endpoint "Liveness" "$ALPINE_URL" "/health/liveness" || ((FAILED++))
    check_endpoint "API Docs" "$ALPINE_URL" "/docs" || ((FAILED++))
    echo ""
fi

if [ $FAILED -eq 0 ]; then
    echo "✅ All health checks passed!"
    exit 0
else
    echo "❌ $FAILED health check(s) failed"
    exit 1
fi


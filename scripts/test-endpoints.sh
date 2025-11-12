#!/bin/bash
# Test all API endpoints

set -e

ARGO_URL="http://localhost:8000"
ALPINE_URL="http://localhost:9001"

echo "🧪 Testing API Endpoints"
echo "========================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

test_endpoint() {
    local method=$1
    local url=$2
    local description=$3
    local data=$4
    local headers=$5
    
    echo -n "Testing: $description... "
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" $headers "$url" 2>&1)
    else
        response=$(curl -s -w "\n%{http_code}" -X $method $headers -H "Content-Type: application/json" -d "$data" "$url" 2>&1)
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
        echo -e "${GREEN}✓${NC} (HTTP $http_code)"
        return 0
    else
        echo -e "${RED}✗${NC} (HTTP $http_code)"
        echo "  Response: $body" | head -c 200
        echo ""
        return 1
    fi
}

# Test Argo endpoints
echo "🚀 Testing Argo Endpoints"
echo "-------------------------"

test_endpoint "GET" "$ARGO_URL/health" "Health check"
test_endpoint "GET" "$ARGO_URL/api/health" "Health status"
test_endpoint "GET" "$ARGO_URL/api/signals/latest?limit=5" "Latest signals"
test_endpoint "GET" "$ARGO_URL/api/signals/stats" "Signal stats"
test_endpoint "GET" "$ARGO_URL/api/symbols" "Available symbols"
test_endpoint "GET" "$ARGO_URL/api/symbols/AAPL" "Symbol data"
test_endpoint "GET" "$ARGO_URL/api/performance/win-rate?period=30d" "Win rate"
test_endpoint "GET" "$ARGO_URL/api/performance/roi?period=30d" "ROI"

echo ""
echo "🔐 Testing Alpine Endpoints"
echo "---------------------------"

# Test Alpine endpoints (unauthenticated)
test_endpoint "GET" "$ALPINE_URL/health" "Health check"

# Test signup
SIGNUP_RESPONSE=$(curl -s -X POST "$ALPINE_URL/api/auth/signup" \
    -H "Content-Type: application/json" \
    -d '{"email":"test@example.com","password":"TestPass123!","full_name":"Test User"}')

TOKEN=$(echo $SIGNUP_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo -e "${YELLOW}⚠${NC} Signup failed or user already exists, trying login..."
    LOGIN_RESPONSE=$(curl -s -X POST "$ALPINE_URL/api/auth/login" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=test@example.com&password=TestPass123!")
    TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
fi

if [ ! -z "$TOKEN" ]; then
    AUTH_HEADER="-H \"Authorization: Bearer $TOKEN\""
    
    test_endpoint "GET" "$ALPINE_URL/api/auth/me" "Get current user" "" "$AUTH_HEADER"
    test_endpoint "GET" "$ALPINE_URL/api/users/profile" "Get profile" "" "$AUTH_HEADER"
    test_endpoint "GET" "$ALPINE_URL/api/subscriptions/plan" "Get subscription plan" "" "$AUTH_HEADER"
    test_endpoint "GET" "$ALPINE_URL/api/signals/subscribed?limit=5" "Get subscribed signals" "" "$AUTH_HEADER"
    test_endpoint "GET" "$ALPINE_URL/api/notifications/unread" "Get unread notifications" "" "$AUTH_HEADER"
else
    echo -e "${RED}✗${NC} Could not get authentication token"
fi

echo ""
echo "✅ Endpoint testing complete!"


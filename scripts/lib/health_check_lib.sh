#!/bin/bash
# Shared health check utilities
# Source this file in health check scripts to use common functions

# Colors
export GREEN='\033[0;32m'
export RED='\033[0;31m'
export YELLOW='\033[1;33m'
export BLUE='\033[0;34m'
export NC='\033[0m'

# Counters (must be reset by caller)
export HEALTH_TOTAL=0
export HEALTH_PASSED=0
export HEALTH_FAILED=0

# Get environment URLs
get_environment_urls() {
    local env="${1:-local}"

    if [ "$env" = "production" ]; then
        echo "http://178.156.194.174:8000|http://91.98.153.49:8001|http://91.98.153.49:3000"
    else
        echo "http://localhost:8000|http://localhost:9001|http://localhost:3000"
    fi
}

# Parse environment URLs and set global variables
parse_environment_urls() {
    local env="${1:-local}"
    local urls=$(get_environment_urls "$env")

    export ARGO_URL=$(echo "$urls" | cut -d'|' -f1)
    export ALPINE_BACKEND_URL=$(echo "$urls" | cut -d'|' -f2)
    export ALPINE_FRONTEND_URL=$(echo "$urls" | cut -d'|' -f3)
}

# Test an endpoint
test_endpoint() {
    local name=$1
    local url=$2
    local expected_status=${3:-200}
    local headers=${4:-""}
    local timeout=${5:-10}
    local check_field=${6:-""}
    local check_value=${7:-""}

    HEALTH_TOTAL=$((HEALTH_TOTAL + 1))
    echo -n "  Testing $name... "

    local curl_cmd="curl -s -w \"\n%{http_code}\" --max-time $timeout"

    if [ -n "$headers" ]; then
        curl_cmd="$curl_cmd -H \"$headers\""
    fi

    curl_cmd="$curl_cmd \"$url\" 2>&1"

    local response=$(eval "$curl_cmd")
    local http_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | sed '$d')

    if [ "$http_code" = "$expected_status" ]; then
        # If check_field is provided, verify the field value
        if [ -n "$check_field" ] && [ -n "$check_value" ]; then
            local field_value=$(echo "$body" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('$check_field', ''))
except:
    print('')
" 2>/dev/null || echo "")

            if [ "$field_value" = "$check_value" ]; then
                echo -e "${GREEN}✅ PASS${NC} (HTTP $http_code, $check_field=$check_value)"
                HEALTH_PASSED=$((HEALTH_PASSED + 1))
                return 0
            else
                echo -e "${YELLOW}⚠️  PARTIAL${NC} (HTTP $http_code, but $check_field=$field_value, expected $check_value)"
                HEALTH_PASSED=$((HEALTH_PASSED + 1))
                return 0
            fi
        else
            echo -e "${GREEN}✅ PASS${NC} (HTTP $http_code)"
            HEALTH_PASSED=$((HEALTH_PASSED + 1))
            return 0
        fi
    else
        echo -e "${RED}❌ FAIL${NC} (HTTP $http_code, expected $expected_status)"
        if [ -n "$body" ]; then
            echo "    Response: $(echo "$body" | head -1)"
        fi
        HEALTH_FAILED=$((HEALTH_FAILED + 1))
        return 1
    fi
}

# Print summary
print_health_summary() {
    echo ""
    echo "📊 SUMMARY"
    echo "============================="
    echo -e "Total: $HEALTH_TOTAL | ${GREEN}✅ Passed: $HEALTH_PASSED${NC} | ${RED}❌ Failed: $HEALTH_FAILED${NC}"

    if [ $HEALTH_FAILED -eq 0 ]; then
        echo -e "${GREEN}🎉 ALL HEALTH CHECKS PASSED!${NC}"
        return 0
    else
        echo -e "${RED}⚠️  SOME CHECKS FAILED${NC}"
        return 1
    fi
}

# Reset counters
reset_health_counters() {
    HEALTH_TOTAL=0
    HEALTH_PASSED=0
    HEALTH_FAILED=0
}

#!/bin/bash
# Health Check Script for Production/Staging Environments

set -e

PROJECT="${1:-}"
ENVIRONMENT="${2:-production}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

check_health() {
    local url=$1
    local project_name=$2
    
    echo ""
    echo "Checking: $project_name"
    echo "URL: $url/api/health"
    
    if response=$(curl -sf -w "\n%{http_code}" "$url/api/health" 2>/dev/null); then
        http_code=$(echo "$response" | tail -n1)
        body=$(echo "$response" | sed '$d')
        
        if [ "$http_code" = "200" ]; then
            print_success "Health check passed (HTTP $http_code)"
            echo "Response: $body" | head -5
            return 0
        else
            print_error "Health check failed (HTTP $http_code)"
            return 1
        fi
    else
        print_error "Health check failed (connection error)"
        return 1
    fi
}

main() {
    if [ -z "$PROJECT" ]; then
        echo "Usage: $0 [argo|alpine] [production|staging]"
        exit 1
    fi
    
    echo "🏥 HEALTH CHECK"
    echo "=============="
    echo "Project: $PROJECT"
    echo "Environment: $ENVIRONMENT"
    
    if [ "$PROJECT" = "argo" ]; then
        if [ "$ENVIRONMENT" = "production" ]; then
            URL="https://argo-capital-production.vercel.app"
        else
            URL="https://staging-argo.vercel.app"
        fi
        check_health "$URL" "Argo Capital"
    elif [ "$PROJECT" = "alpine" ]; then
        if [ "$ENVIRONMENT" = "production" ]; then
            URL="https://alpineanalytics.ai"
        else
            URL="https://staging-alpine.vercel.app"
        fi
        check_health "$URL" "Alpine Analytics"
    else
        print_error "Unknown project: $PROJECT"
        exit 1
    fi
}

main "$@"

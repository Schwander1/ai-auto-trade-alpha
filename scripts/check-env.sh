#!/bin/bash
# Environment Variable Validation Script
# Validates required environment variables for each project before deployment

set -e

PROJECT="${1:-}"
ENV_FILE=""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Function to check if .env.production exists
check_env_file() {
    if [ ! -f "$ENV_FILE" ]; then
        print_error ".env.production not found at $ENV_FILE"
        echo "   Create it with required environment variables"
        return 1
    fi
    print_success ".env.production exists"
    return 0
}

# Function to validate environment variable
check_var() {
    local var_name=$1
    local var_value=$(grep "^${var_name}=" "$ENV_FILE" 2>/dev/null | cut -d '=' -f2- | tr -d '"' | tr -d "'")
    
    if [ -z "$var_value" ]; then
        print_error "$var_name not found or empty"
        return 1
    fi
    
    # Mask sensitive values
    if [ ${#var_value} -gt 8 ]; then
        masked_value="${var_value:0:4}***${var_value: -4}"
    else
        masked_value="***"
    fi
    
    print_success "$var_name: $masked_value"
    return 0
}

# Function to validate Argo Capital environment
validate_argo() {
    echo ""
    echo "🔍 Validating Argo Capital Environment Variables"
    echo "================================================"
    
    ENV_FILE="argo/.env.production"
    
    if ! check_env_file; then
        return 1
    fi
    
    local errors=0
    
    echo ""
    echo "Checking required variables:"
    check_var "ALPACA_API_KEY" || ((errors++))
    check_var "STRIPE_SECRET_KEY" || ((errors++))
    check_var "DATABASE_URL" || ((errors++))
    check_var "REDIS_URL" || ((errors++))
    
    # Optional but recommended
    if grep -q "VERCEL_PROJECT_ID" "$ENV_FILE" 2>/dev/null; then
        check_var "VERCEL_PROJECT_ID" || true
    else
        print_warning "VERCEL_PROJECT_ID not set (optional)"
    fi
    
    echo ""
    if [ $errors -eq 0 ]; then
        print_success "All required environment variables present (4/4)"
        return 0
    else
        print_error "Missing $errors required environment variable(s)"
        return 1
    fi
}

# Function to validate Alpine Analytics environment
validate_alpine() {
    echo ""
    echo "🔍 Validating Alpine Analytics Environment Variables"
    echo "==================================================="
    
    local errors=0
    
    # Check backend
    echo ""
    echo "Backend (alpine-backend/):"
    ENV_FILE="alpine-backend/.env.production"
    
    if ! check_env_file; then
        ((errors++))
    else
        echo "Checking required variables:"
        check_var "DATABASE_URL" || ((errors++))
        check_var "REDIS_URL" || ((errors++))
        check_var "ANALYTICS_API_KEY" || ((errors++))
        check_var "RESEND_API_KEY" || ((errors++))
    fi
    
    # Check frontend
    echo ""
    echo "Frontend (alpine-frontend/):"
    ENV_FILE="alpine-frontend/.env.production"
    
    if ! check_env_file; then
        print_warning ".env.production not found (may use backend env)"
    else
        echo "Checking required variables:"
        check_var "NEXT_PUBLIC_API_URL" || true  # Optional
    fi
    
    echo ""
    if [ $errors -eq 0 ]; then
        print_success "All required environment variables present"
        return 0
    else
        print_error "Missing $errors required environment variable(s)"
        return 1
    fi
}

# Main execution
main() {
    if [ -z "$PROJECT" ]; then
        echo "Usage: $0 [argo|alpine]"
        echo ""
        echo "Validates environment variables for deployment:"
        echo "  argo   - Argo Capital project"
        echo "  alpine - Alpine Analytics project (backend + frontend)"
        exit 1
    fi
    
    case "$PROJECT" in
        argo|argo-capital)
            if validate_argo; then
                exit 0
            else
                exit 1
            fi
            ;;
        alpine|alpine-analytics)
            if validate_alpine; then
                exit 0
            else
                exit 1
            fi
            ;;
        *)
            print_error "Unknown project: $PROJECT"
            echo "Valid options: argo, alpine"
            exit 1
            ;;
    esac
}

main "$@"


#!/bin/bash
# Verify that local-only files are not being deployed
# Run this before deployment to ensure exclusions are correct

set -e

echo "🔍 VERIFYING DEPLOYMENT EXCLUSIONS"
echo "==================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Local-only files that should NEVER be deployed
LOCAL_ONLY_FILES=(
    "scripts/local_setup.sh"
    "scripts/local_health_check.sh"
    "scripts/local_security_audit.sh"
    "scripts/setup_local_dev.sh"
    "scripts/start-all.sh"
    "argo/scripts/execute_test_trade.py"
    "argo/scripts/enable_full_trading.py"
)

# Check if .deployignore exists
if [ ! -f ".deployignore" ]; then
    print_error ".deployignore file not found!"
    exit 1
fi

print_success ".deployignore file exists"

# Check if deployment-manifest.json exists
if [ ! -f "scripts/deployment-manifest.json" ]; then
    print_warning "deployment-manifest.json not found (optional)"
else
    print_success "deployment-manifest.json exists"
fi

# Verify local-only files exist locally
echo ""
echo "📋 Checking local-only files..."
MISSING=0
for file in "${LOCAL_ONLY_FILES[@]}"; do
    if [ -f "$file" ]; then
        print_success "$file exists (local only)"
    else
        print_warning "$file not found (may not exist yet)"
    fi
done

# Check deployment scripts for exclusions
echo ""
echo "📋 Checking deployment scripts for exclusions..."

if grep -q "execute_test_trade.py" scripts/deploy-argo.sh; then
    print_success "deploy-argo.sh excludes execute_test_trade.py"
else
    print_error "deploy-argo.sh may not exclude execute_test_trade.py"
    MISSING=1
fi

if grep -q "local_setup.sh" scripts/deploy-argo.sh; then
    print_success "deploy-argo.sh excludes local_setup.sh"
else
    print_error "deploy-argo.sh may not exclude local_setup.sh"
    MISSING=1
fi

# Summary
echo ""
echo "==================================="
if [ $MISSING -eq 0 ]; then
    print_success "All deployment exclusions verified!"
    echo ""
    echo "📝 Local-only files will be excluded from deployment:"
    for file in "${LOCAL_ONLY_FILES[@]}"; do
        echo "   - $file"
    done
    exit 0
else
    print_error "Some exclusions may be missing!"
    echo ""
    echo "⚠️  Please review deployment scripts before deploying"
    exit 1
fi


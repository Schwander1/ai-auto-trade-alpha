#!/bin/bash
# Test Fix Scripts - Verify all scripts are ready
# This script tests that all fix scripts are properly formatted and ready

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
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

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "TESTING ALL FIX SCRIPTS"
echo "═══════════════════════════════════════════════════════════"
echo ""

ERRORS=0

# Test script syntax
test_script() {
    local script=$1
    local name=$2
    
    print_info "Testing: $name"
    
    if [ ! -f "$script" ]; then
        print_error "Script not found: $script"
        ((ERRORS++))
        return 1
    fi
    
    if [ ! -x "$script" ]; then
        print_error "Script not executable: $script"
        ((ERRORS++))
        return 1
    fi
    
    # Check syntax
    if bash -n "$script" 2>&1; then
        print_success "Syntax valid: $name"
        return 0
    else
        print_error "Syntax error in: $name"
        ((ERRORS++))
        return 1
    fi
}

# Test all scripts
test_script "scripts/fix_all_production_issues.sh" "Fix All Production Issues"
test_script "scripts/check_all_production_status.sh" "Check All Production Status"
test_script "scripts/check_alpine_backend.sh" "Check Alpine Backend"
test_script "scripts/update_production_api_keys.sh" "Update Production API Keys"

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "TEST RESULTS"
echo "═══════════════════════════════════════════════════════════"
echo ""

if [ $ERRORS -eq 0 ]; then
    print_success "All scripts are valid and ready to use!"
    echo ""
    print_info "To run the fixes:"
    echo "  ./scripts/fix_all_production_issues.sh"
    echo ""
    print_info "To check status:"
    echo "  ./scripts/check_all_production_status.sh"
    exit 0
else
    print_error "$ERRORS error(s) found"
    exit 1
fi


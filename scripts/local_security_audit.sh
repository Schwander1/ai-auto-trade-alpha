#!/bin/bash
# Local security validation before deployment

set -e

echo "🔒 LOCAL SECURITY AUDIT"
echo "======================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PASSED=0
FAILED=0
WARNINGS=0

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

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check 1: Hardcoded secrets
echo "1️⃣  Hardcoded Secrets Check"
echo "---------------------------"

# Check for API keys in code
if grep -r "api_key.*=.*['\"][A-Za-z0-9]\{20,\}" argo/ --include="*.py" --exclude-dir=venv --exclude-dir=__pycache__ 2>/dev/null | grep -v "#.*api_key" | grep -v "example" | grep -v "test"; then
    print_error "Potential hardcoded API keys found in code"
else
    print_success "No hardcoded API keys found"
fi

# Check config.json for secrets (should use environment variables or AWS Secrets Manager)
if [ -f "argo/config.json" ]; then
    # Check if config.json has actual secrets (not just placeholders)
    if grep -q '"api_key": "[A-Za-z0-9]\{20,\}"' argo/config.json 2>/dev/null; then
        print_warning "config.json contains API keys (should use AWS Secrets Manager in production)"
    else
        print_success "config.json doesn't contain hardcoded secrets"
    fi
fi

# Check 2: Environment variables
echo ""
echo "2️⃣  Environment Variables"
echo "-------------------------"
if [ -f ".env" ] && [ -s ".env" ]; then
    print_warning ".env file exists (ensure it's not committed to git)"
    if grep -q ".env" .gitignore 2>/dev/null; then
        print_success ".env is in .gitignore"
    else
        print_error ".env is NOT in .gitignore"
    fi
else
    print_info "No .env file found (using config.json or AWS Secrets Manager)"
fi

# Check 3: CORS configuration
echo ""
echo "3️⃣  CORS Configuration"
echo "---------------------"
if grep -q "allow_origins.*\*" argo/main.py 2>/dev/null; then
    print_error "CORS allows all origins (*) - security risk"
else
    print_success "CORS is properly configured (whitelist)"
fi

# Check 4: Security headers
echo ""
echo "4️⃣  Security Headers"
echo "-------------------"
if grep -q "SecurityHeadersMiddleware\|X-Frame-Options\|Content-Security-Policy" argo/main.py alpine-backend/backend/main.py 2>/dev/null; then
    print_success "Security headers middleware found"
else
    print_warning "Security headers middleware may not be configured"
fi

# Check 5: Input validation
echo ""
echo "5️⃣  Input Validation"
echo "-------------------"
if grep -r "sanitize\|validate.*input\|pydantic.*Field" argo/argo/api/ alpine-backend/backend/api/ --include="*.py" 2>/dev/null | head -1; then
    print_success "Input validation found"
else
    print_warning "Input validation may be missing"
fi

# Check 6: SQL injection protection
echo ""
echo "6️⃣  SQL Injection Protection"
echo "---------------------------"
if grep -r "execute.*%s\|execute.*%d\|f\".*SELECT\|f\".*INSERT\|f\".*UPDATE" argo/ alpine-backend/ --include="*.py" --exclude-dir=venv 2>/dev/null | grep -v "#.*safe" | head -1; then
    print_warning "Potential SQL injection risk (string formatting in queries)"
else
    print_success "No obvious SQL injection risks found"
fi

# Check 7: Rate limiting
echo ""
echo "7️⃣  Rate Limiting"
echo "----------------"
if grep -r "rate_limit\|RateLimiter\|@limiter" argo/argo/api/ alpine-backend/backend/api/ --include="*.py" 2>/dev/null | head -1; then
    print_success "Rate limiting found"
else
    print_warning "Rate limiting may not be configured"
fi

# Check 8: Authentication/Authorization
echo ""
echo "8️⃣  Authentication/Authorization"
echo "-------------------------------"
if grep -r "verify.*token\|JWT\|OAuth\|@require_auth\|Depends.*auth" alpine-backend/backend/api/ --include="*.py" 2>/dev/null | head -1; then
    print_success "Authentication/authorization found"
else
    print_warning "Authentication may not be configured"
fi

# Check 9: Error message sanitization
echo ""
echo "9️⃣  Error Message Sanitization"
echo "-----------------------------"
if grep -r "settings.DEBUG\|if.*debug\|error.*sanitize" alpine-backend/backend/ argo/argo/api/ --include="*.py" 2>/dev/null | head -1; then
    print_success "Error message sanitization found"
else
    print_warning "Error messages may expose internal details"
fi

# Check 10: File permissions
echo ""
echo "🔟 File Permissions"
echo "------------------"
if [ -f "argo/config.json" ]; then
    PERMS=$(stat -f "%A" argo/config.json 2>/dev/null || stat -c "%a" argo/config.json 2>/dev/null)
    if [ "$PERMS" = "600" ] || [ "$PERMS" = "400" ]; then
        print_success "config.json has secure permissions ($PERMS)"
    else
        print_warning "config.json permissions: $PERMS (consider 600)"
    fi
fi

# Summary
echo ""
echo "======================"
echo "📊 SECURITY AUDIT SUMMARY"
echo "======================"
echo -e "${GREEN}✅ Passed: $PASSED${NC}"
echo -e "${RED}❌ Failed: $FAILED${NC}"
echo -e "${YELLOW}⚠️  Warnings: $WARNINGS${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ SECURITY AUDIT PASSED${NC}"
    echo ""
    echo "📝 Recommendations:"
    echo "   - Review warnings before deployment"
    echo "   - Ensure AWS Secrets Manager is used in production"
    echo "   - Verify CORS configuration is correct"
    echo "   - Test rate limiting"
    exit 0
else
    echo -e "${RED}❌ SECURITY AUDIT FAILED${NC}"
    echo ""
    echo "⚠️  Please fix critical issues before deployment"
    exit 1
fi


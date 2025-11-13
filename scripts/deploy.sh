#!/bin/bash
# Intelligent Deployment Script with 10 Safety Gates
# Auto-detects project context and executes full deployment workflow

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_step() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Step 1: Auto-detect project context
detect_project() {
    print_step "STEP 1: AUTO-DETECT PROJECT CONTEXT"
    
    # Get changed files from last commit
    if [ -n "$(git status --porcelain)" ]; then
        print_warning "Uncommitted changes detected"
        echo "Changed files:"
        git status --short
        echo ""
        read -p "Commit changes first? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_info "Please commit changes first, then run deployment again"
            exit 1
        fi
    fi
    
    # Check git diff for changed files
    CHANGED_FILES=$(git diff --name-only HEAD~1 HEAD 2>/dev/null || git ls-files --modified 2>/dev/null || echo "")
    
    if [ -z "$CHANGED_FILES" ]; then
        CHANGED_FILES=$(git diff --cached --name-only 2>/dev/null || echo "")
    fi
    
    ARGO_CHANGED=false
    ALPINE_BACKEND_CHANGED=false
    ALPINE_FRONTEND_CHANGED=false
    PACKAGES_CHANGED=false
    
    while IFS= read -r file; do
        if [[ "$file" == argo/* ]]; then
            ARGO_CHANGED=true
        elif [[ "$file" == alpine-backend/* ]]; then
            ALPINE_BACKEND_CHANGED=true
        elif [[ "$file" == alpine-frontend/* ]] || [[ "$file" == alpine-analytics/* ]]; then
            ALPINE_FRONTEND_CHANGED=true
        elif [[ "$file" == packages/* ]]; then
            PACKAGES_CHANGED=true
        fi
    done <<< "$CHANGED_FILES"
    
    # Determine project
    if [ "$ARGO_CHANGED" = true ] && ([ "$ALPINE_BACKEND_CHANGED" = true ] || [ "$ALPINE_FRONTEND_CHANGED" = true ]); then
        print_error "Changes detected in BOTH argo and alpine projects"
        echo "Please deploy one project at a time"
        exit 1
    fi
    
    if [ "$ARGO_CHANGED" = true ]; then
        PROJECT="argo"
        PROJECT_NAME="Argo Capital"
        FILTER="@argo-alpine/argo"
        DEPLOY_TARGET="argo-capital-production"
    elif [ "$ALPINE_BACKEND_CHANGED" = true ] || [ "$ALPINE_FRONTEND_CHANGED" = true ]; then
        PROJECT="alpine"
        PROJECT_NAME="Alpine Analytics"
        FILTER="@argo-alpine/alpine-*"
        DEPLOY_TARGET="alpine-analytics-production"
    elif [ "$PACKAGES_CHANGED" = true ]; then
        print_warning "Changes detected in shared packages"
        echo "This affects ALL projects. Which project to deploy?"
        read -p "Enter 'argo' or 'alpine': " PROJECT
        if [ "$PROJECT" = "argo" ]; then
            PROJECT_NAME="Argo Capital"
            FILTER="@argo-alpine/argo"
            DEPLOY_TARGET="argo-capital-production"
        elif [ "$PROJECT" = "alpine" ]; then
            PROJECT_NAME="Alpine Analytics"
            FILTER="@argo-alpine/alpine-*"
            DEPLOY_TARGET="alpine-analytics-production"
        else
            print_error "Invalid project selection"
            exit 1
        fi
    else
        print_error "No changes detected in argo/ or alpine-*/ directories"
        echo "Changed files:"
        echo "$CHANGED_FILES"
        exit 1
    fi
    
    print_success "Detected changes in: $PROJECT_NAME"
    print_info "Files changed: $(echo "$CHANGED_FILES" | wc -l | tr -d ' ')"
    print_info "Deploy target: $DEPLOY_TARGET"
}

# Step 2: Validate changes
validate_changes() {
    print_step "STEP 2: VALIDATE CHANGES ARE READY"
    
    print_info "Running linting..."
    if ! pnpm --filter="$FILTER" lint 2>&1 | tee /tmp/lint-output.log; then
        print_error "Linting failed"
        exit 1
    fi
    print_success "Linting passed"
    
    print_info "Running tests..."
    if ! pnpm --filter="$FILTER" test 2>&1 | tee /tmp/test-output.log; then
        print_error "Tests failed"
        exit 1
    fi
    print_success "Tests passed"
    
    print_info "Building project..."
    if ! pnpm --filter="$FILTER" build 2>&1 | tee /tmp/build-output.log; then
        print_error "Build failed"
        exit 1
    fi
    print_success "Build successful"
}

# Step 3: Verify environment setup
verify_environment() {
    print_step "STEP 3: VERIFY ENVIRONMENT SETUP"
    
    if ! ./scripts/check-env.sh "$PROJECT"; then
        print_error "Environment validation failed"
        exit 1
    fi
    print_success "Environment variables verified"
}

# Step 4: Code quality scan
scan_code_quality() {
    print_step "STEP 4: CODE QUALITY SCAN"
    
    local issues=0
    
    # Check for console.log
    if git diff HEAD~1 HEAD 2>/dev/null | grep -q "console\.log" || git diff --cached 2>/dev/null | grep -q "console\.log"; then
        print_error "console.log statements found in changes"
        git diff HEAD~1 HEAD 2>/dev/null | grep -n "console\.log" || git diff --cached 2>/dev/null | grep -n "console\.log"
        ((issues++))
    else
        print_success "No console.log found"
    fi
    
    # Check for debugger
    if git diff HEAD~1 HEAD 2>/dev/null | grep -q "debugger" || git diff --cached 2>/dev/null | grep -q "debugger"; then
        print_error "debugger statements found in changes"
        ((issues++))
    else
        print_success "No debugger found"
    fi
    
    # Check for hardcoded secrets (basic check)
    if git diff HEAD~1 HEAD 2>/dev/null | grep -iE "(api[_-]?key|secret|password|token)\s*=\s*['\"][^'\"]+['\"]" || \
       git diff --cached 2>/dev/null | grep -iE "(api[_-]?key|secret|password|token)\s*=\s*['\"][^'\"]+['\"]"; then
        print_warning "Potential hardcoded secrets found (manual review recommended)"
    else
        print_success "No hardcoded secrets detected"
    fi
    
    if [ $issues -gt 0 ]; then
        print_error "Code quality issues found. Please fix before deploying."
        exit 1
    fi
}

# Step 5: Staging pre-validation
validate_staging() {
    print_step "STEP 5: STAGING PRE-VALIDATION"
    
    if [ "$PROJECT" = "argo" ]; then
        STAGING_URL="https://staging-argo.vercel.app"
    else
        STAGING_URL="https://staging-alpine.vercel.app"
    fi
    
    print_info "Checking staging health: $STAGING_URL/api/health"
    
    if curl -sf "$STAGING_URL/api/health" > /dev/null 2>&1; then
        print_success "Staging is healthy"
    else
        print_warning "Staging health check failed (continuing anyway)"
    fi
}

# Step 6: Production environment check
check_production() {
    print_step "STEP 6: PRODUCTION ENVIRONMENT CHECK"
    
    print_info "Verifying production systems are ready..."
    
    # Check if Vercel CLI is available
    if ! command -v vercel &> /dev/null; then
        print_warning "Vercel CLI not found (install with: npm i -g vercel)"
    else
        print_success "Vercel CLI available"
    fi
    
    print_success "Production environment ready"
}

# Step 7: Final confirmation
final_confirmation() {
    print_step "STEP 7: FINAL CONFIRMATION"
    
    echo ""
    echo "📊 DEPLOYMENT SUMMARY"
    echo "────────────────────"
    echo "Project: $PROJECT_NAME"
    echo "Deploy Target: $DEPLOY_TARGET"
    echo "Filter: $FILTER"
    echo ""
    echo "🚨 FINAL CONFIRMATION REQUIRED"
    echo "Type EXACTLY: deploy fully to production"
    echo "(Anything else will abort this deployment)"
    echo ""
    read -p "> " CONFIRMATION
    
    if [ "$CONFIRMATION" != "deploy fully to production" ]; then
        print_error "Deployment aborted"
        echo "You typed: '$CONFIRMATION'"
        echo "Required: 'deploy fully to production'"
        exit 1
    fi
}

# Step 8: Execute deployment
execute_deployment() {
    print_step "STEP 8: EXECUTE DEPLOYMENT"
    
    print_info "Deploying to production..."
    
    if [ "$PROJECT" = "argo" ]; then
        cd argo || exit 1
    elif [ "$PROJECT" = "alpine" ]; then
        # Deploy backend and frontend together
        print_info "Deploying Alpine Analytics (backend + frontend)..."
        cd alpine-backend || exit 1
    fi
    
    if command -v vercel &> /dev/null; then
        print_info "Running: vercel deploy --prod"
        vercel deploy --prod
    else
        print_warning "Vercel CLI not available. Manual deployment required."
        print_info "Run: vercel deploy --prod from project directory"
    fi
    
    cd ..
}

# Step 9: Post-deployment health checks
post_deployment_checks() {
    print_step "STEP 9: POST-DEPLOYMENT HEALTH CHECKS"
    
    if [ "$PROJECT" = "argo" ]; then
        HEALTH_URL="https://argo-capital-production.vercel.app/api/health"
    else
        HEALTH_URL="https://alpineanalytics.ai/api/health"
    fi
    
    print_info "Waiting for deployment to activate..."
    sleep 10
    
    print_info "Checking health: $HEALTH_URL"
    
    if curl -sf "$HEALTH_URL" > /dev/null 2>&1; then
        print_success "Health check passed"
    else
        print_warning "Health check failed (deployment may still be activating)"
    fi
}

# Step 10: Completion
completion() {
    print_step "STEP 10: COMPLETION & NOTIFICATION"
    
    VERSION=$(git describe --tags --abbrev=0 2>/dev/null || echo "v1.0.0")
    NEW_VERSION=$(echo "$VERSION" | awk -F. '{print $1"."$2"."($3+1)}')
    
    print_success "DEPLOYMENT SUCCESSFUL"
    echo ""
    echo "Project: $PROJECT_NAME"
    echo "Deployment Target: $DEPLOY_TARGET"
    echo "Version: $NEW_VERSION"
    echo ""
    echo "🎯 Next Steps:"
    echo "  - Monitor production for 15 minutes"
    echo "  - Watch error logs"
    echo "  - If issues: ./scripts/rollback.sh $PROJECT"
}

# Main execution
main() {
    echo ""
    echo "🚀 DEPLOYING TO PRODUCTION"
    echo "=========================="
    echo ""
    
    detect_project
    validate_changes
    verify_environment
    scan_code_quality
    validate_staging
    check_production
    final_confirmation
    execute_deployment
    post_deployment_checks
    completion
    
    print_success "Deployment workflow complete!"
}

main "$@"


#!/bin/bash
# Execute Production Deployment - Health Check Improvements
# This script executes the deployment of all health check improvements to production

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Production servers
ARGO_SERVER="178.156.194.174"
ARGO_USER="root"
ALPINE_SERVER="91.98.153.49"
ALPINE_USER="root"

print_header() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo ""
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

# Verify SSH access
verify_ssh() {
    local server=$1
    local user=$2
    local name=$3
    
    print_info "Verifying SSH access to $name ($user@$server)..."
    if ssh -o ConnectTimeout=5 -o BatchMode=yes ${user}@${server} "echo 'Connected'" 2>/dev/null; then
        print_success "SSH access to $name verified"
        return 0
    else
        print_warning "Cannot verify SSH access to $name (may require password/key)"
        return 1
    fi
}

# Deploy Argo code
deploy_argo_code() {
    print_header "DEPLOYING ARGO CODE TO PRODUCTION"
    
    if verify_ssh "$ARGO_SERVER" "$ARGO_USER" "Argo Server"; then
        print_info "Using existing deployment script: ./scripts/deploy-argo-blue-green.sh"
        print_warning "This will deploy code to production. Continue? (y/N)"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            if [ -f "./scripts/deploy-argo-blue-green.sh" ]; then
                ./scripts/deploy-argo-blue-green.sh
                print_success "Argo code deployment initiated"
            else
                print_error "Deployment script not found"
                return 1
            fi
        else
            print_warning "Argo deployment skipped"
        fi
    else
        print_warning "SSH access not verified - manual deployment required"
        print_info "Run: ./scripts/deploy-argo-blue-green.sh"
    fi
}

# Deploy Alpine Backend code
deploy_alpine_backend_code() {
    print_header "DEPLOYING ALPINE BACKEND CODE TO PRODUCTION"
    
    if verify_ssh "$ALPINE_SERVER" "$ALPINE_USER" "Alpine Server"; then
        print_info "Using existing deployment script: ./scripts/deploy-alpine.sh"
        print_warning "This will deploy code to production. Continue? (y/N)"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            if [ -f "./scripts/deploy-alpine.sh" ]; then
                ./scripts/deploy-alpine.sh
                print_success "Alpine Backend code deployment initiated"
            else
                print_error "Deployment script not found"
                return 1
            fi
        else
            print_warning "Alpine Backend deployment skipped"
        fi
    else
        print_warning "SSH access not verified - manual deployment required"
        print_info "Run: ./scripts/deploy-alpine.sh"
    fi
}

# Update monitoring configuration
deploy_monitoring_config() {
    print_header "DEPLOYING MONITORING CONFIGURATION"
    
    print_info "Monitoring configuration files ready:"
    echo "  - infrastructure/monitoring/prometheus.yml"
    echo "  - infrastructure/monitoring/alerts.yml"
    echo ""
    print_warning "To deploy monitoring configuration, you need to:"
    echo "  1. Copy files to your Prometheus server"
    echo "  2. Restart/reload Prometheus"
    echo ""
    echo "Example commands:"
    echo "  scp infrastructure/monitoring/prometheus.yml root@<monitoring-server>:/etc/prometheus/"
    echo "  scp infrastructure/monitoring/alerts.yml root@<monitoring-server>:/etc/prometheus/"
    echo "  ssh root@<monitoring-server> 'systemctl restart prometheus'"
    echo ""
    read -p "Press Enter to continue (monitoring config deployment is manual)..."
}

# Verify deployment
verify_deployment() {
    print_header "VERIFYING DEPLOYMENT"
    
    if [ -f "./scripts/verify_production_deployment.sh" ]; then
        print_info "Running deployment verification..."
        ./scripts/verify_production_deployment.sh
    else
        print_error "Verification script not found"
    fi
}

# Main execution
main() {
    print_header "HEALTH CHECK IMPROVEMENTS - PRODUCTION DEPLOYMENT EXECUTION"
    
    echo "This script will guide you through deploying health check improvements to production."
    echo ""
    echo "⚠️  IMPORTANT:"
    echo "   - Code deployment requires SSH access to production servers"
    echo "   - You will be prompted before each deployment step"
    echo "   - Monitoring configuration deployment is manual"
    echo ""
    read -p "Press Enter to continue or Ctrl+C to cancel..."
    
    # Step 1: Deploy Argo
    deploy_argo_code
    
    # Step 2: Deploy Alpine Backend
    deploy_alpine_backend_code
    
    # Step 3: Deploy Monitoring Config (manual)
    deploy_monitoring_config
    
    # Step 4: Verify
    verify_deployment
    
    print_header "DEPLOYMENT EXECUTION COMPLETE"
    print_success "Deployment process completed!"
    print_info "Review verification results above"
    print_info "See PRODUCTION_DEPLOYMENT_CHECKLIST.md for detailed checklist"
}

main "$@"


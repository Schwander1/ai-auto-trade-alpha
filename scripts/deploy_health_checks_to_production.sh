#!/bin/bash
# Deploy Health Check Improvements to Production
# This script deploys all health check improvements to production servers

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Check if running as root or with sudo
check_permissions() {
    if [ "$EUID" -ne 0 ] && ! sudo -n true 2>/dev/null; then
        print_error "This script requires sudo privileges for some operations"
        print_info "Please run with sudo or ensure you have SSH access to production servers"
        exit 1
    fi
}

# Verify SSH access
verify_ssh_access() {
    print_header "VERIFYING SSH ACCESS"
    
    print_info "Testing SSH access to Argo server..."
    if ssh -o ConnectTimeout=5 -o BatchMode=yes ${ARGO_USER}@${ARGO_SERVER} "echo 'Connected'" 2>/dev/null; then
        print_success "SSH access to Argo server verified"
    else
        print_error "Cannot connect to Argo server. Please verify SSH access."
        exit 1
    fi
    
    print_info "Testing SSH access to Alpine server..."
    if ssh -o ConnectTimeout=5 -o BatchMode=yes ${ALPINE_USER}@${ALPINE_SERVER} "echo 'Connected'" 2>/dev/null; then
        print_success "SSH access to Alpine server verified"
    else
        print_error "Cannot connect to Alpine server. Please verify SSH access."
        exit 1
    fi
}

# Deploy Argo code
deploy_argo() {
    print_header "DEPLOYING ARGO CODE"
    
    print_info "This step requires manual deployment or existing deployment script"
    print_warning "Please deploy Argo code using your standard deployment process:"
    echo "  ./scripts/deploy-argo-blue-green.sh"
    echo "  OR"
    echo "  ./commands/deploy argo to production"
    echo ""
    read -p "Press Enter after Argo code has been deployed..."
    
    print_info "Verifying Argo health endpoints..."
    if curl -s --max-time 5 "http://${ARGO_SERVER}:8000/api/v1/health" > /dev/null 2>&1; then
        print_success "Argo health endpoint is accessible"
    else
        print_warning "Argo health endpoint not yet accessible (may need service restart)"
    fi
}

# Deploy Alpine Backend code
deploy_alpine_backend() {
    print_header "DEPLOYING ALPINE BACKEND CODE"
    
    print_info "This step requires manual deployment or existing deployment script"
    print_warning "Please deploy Alpine Backend code using your standard deployment process:"
    echo "  ./scripts/deploy-alpine.sh"
    echo "  OR"
    echo "  ./commands/deploy alpine to production"
    echo ""
    read -p "Press Enter after Alpine Backend code has been deployed..."
    
    print_info "Verifying Alpine Backend health endpoints..."
    if curl -s --max-time 5 "http://${ALPINE_SERVER}:8001/health" > /dev/null 2>&1; then
        print_success "Alpine Backend health endpoint is accessible"
    else
        print_warning "Alpine Backend health endpoint not yet accessible (may need service restart)"
    fi
}

# Deploy Alpine Frontend code
deploy_alpine_frontend() {
    print_header "DEPLOYING ALPINE FRONTEND CODE"
    
    print_info "Frontend deployment depends on your hosting platform (Vercel, etc.)"
    print_warning "Please deploy Alpine Frontend using your standard deployment process"
    echo ""
    read -p "Press Enter after Alpine Frontend has been deployed (or skip if not needed)..."
    
    print_info "Verifying Alpine Frontend health endpoints..."
    if curl -s --max-time 5 "http://${ALPINE_SERVER}:3000/api/health" > /dev/null 2>&1; then
        print_success "Alpine Frontend health endpoint is accessible"
    else
        print_warning "Alpine Frontend health endpoint not yet accessible"
    fi
}

# Update monitoring configuration
deploy_monitoring_config() {
    print_header "DEPLOYING MONITORING CONFIGURATION"
    
    print_info "Monitoring configuration files are ready:"
    echo "  - infrastructure/monitoring/prometheus.yml"
    echo "  - infrastructure/monitoring/alerts.yml"
    echo ""
    print_warning "To deploy monitoring configuration:"
    echo "  1. Copy files to your Prometheus server"
    echo "  2. Restart/reload Prometheus"
    echo ""
    echo "Example commands:"
    echo "  scp infrastructure/monitoring/prometheus.yml root@<monitoring-server>:/etc/prometheus/"
    echo "  scp infrastructure/monitoring/alerts.yml root@<monitoring-server>:/etc/prometheus/"
    echo "  ssh root@<monitoring-server> 'systemctl restart prometheus'"
    echo ""
    read -p "Press Enter after monitoring configuration has been deployed (or skip if not needed)..."
}

# Restart services to apply health probes
restart_services() {
    print_header "RESTARTING SERVICES TO APPLY HEALTH PROBES"
    
    print_info "Restarting Argo service..."
    if ssh ${ARGO_USER}@${ARGO_SERVER} "cd /root/argo-production* 2>/dev/null && docker-compose restart argo-api 2>/dev/null || systemctl restart argo 2>/dev/null || echo 'Service restart skipped'" 2>/dev/null; then
        print_success "Argo service restart attempted"
    else
        print_warning "Could not restart Argo service automatically"
    fi
    
    print_info "Restarting Alpine Backend services..."
    if ssh ${ALPINE_USER}@${ALPINE_SERVER} "cd /root/alpine-production* 2>/dev/null && docker-compose -f docker-compose.production.yml restart 2>/dev/null || echo 'Service restart skipped'" 2>/dev/null; then
        print_success "Alpine Backend services restart attempted"
    else
        print_warning "Could not restart Alpine Backend services automatically"
    fi
    
    print_info "Waiting 30 seconds for services to start..."
    sleep 30
}

# Run verification
run_verification() {
    print_header "RUNNING DEPLOYMENT VERIFICATION"
    
    if [ -f "./scripts/verify_production_deployment.sh" ]; then
        ./scripts/verify_production_deployment.sh
    else
        print_error "Verification script not found"
    fi
}

# Main execution
main() {
    print_header "HEALTH CHECK IMPROVEMENTS - PRODUCTION DEPLOYMENT"
    echo "This script will guide you through deploying health check improvements to production"
    echo ""
    echo "⚠️  IMPORTANT: This script requires manual intervention for code deployment"
    echo "   It will verify configurations and guide you through the process"
    echo ""
    read -p "Press Enter to continue or Ctrl+C to cancel..."
    
    check_permissions
    verify_ssh_access
    deploy_argo
    deploy_alpine_backend
    deploy_alpine_frontend
    deploy_monitoring_config
    restart_services
    run_verification
    
    print_header "DEPLOYMENT COMPLETE"
    print_success "Health check improvements deployment process completed!"
    print_info "Please review verification results above"
    print_info "See PRODUCTION_DEPLOYMENT_CHECKLIST.md for detailed checklist"
}

main "$@"


#!/bin/bash
# Deploy Monitoring Configuration to Prometheus Server
# This script deploys Prometheus and Alertmanager configurations

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# Main execution
main() {
    print_header "DEPLOYING MONITORING CONFIGURATION"
    
    print_info "Monitoring configuration files are ready:"
    echo "  - infrastructure/monitoring/prometheus.yml"
    echo "  - infrastructure/monitoring/alerts.yml"
    echo ""
    
    print_warning "To deploy monitoring configuration, you need:"
    echo "  1. SSH access to your Prometheus server"
    echo "  2. Prometheus configuration directory path"
    echo ""
    
    read -p "Enter Prometheus server address (e.g., root@monitoring-server): " MONITORING_SERVER
    read -p "Enter Prometheus config directory (default: /etc/prometheus): " PROMETHEUS_DIR
    PROMETHEUS_DIR=${PROMETHEUS_DIR:-/etc/prometheus}
    
    if [ -z "$MONITORING_SERVER" ]; then
        print_error "Monitoring server address is required"
        exit 1
    fi
    
    print_info "Deploying Prometheus configuration..."
    if scp infrastructure/monitoring/prometheus.yml ${MONITORING_SERVER}:${PROMETHEUS_DIR}/prometheus.yml; then
        print_success "Prometheus configuration deployed"
    else
        print_error "Failed to deploy Prometheus configuration"
        exit 1
    fi
    
    print_info "Deploying Alert rules..."
    if scp infrastructure/monitoring/alerts.yml ${MONITORING_SERVER}:${PROMETHEUS_DIR}/alerts.yml; then
        print_success "Alert rules deployed"
    else
        print_error "Failed to deploy alert rules"
        exit 1
    fi
    
    print_info "Validating Prometheus configuration..."
    if ssh ${MONITORING_SERVER} "promtool check config ${PROMETHEUS_DIR}/prometheus.yml" 2>&1; then
        print_success "Prometheus configuration is valid"
    else
        print_warning "Prometheus configuration validation failed (promtool may not be available)"
    fi
    
    print_warning "Restart Prometheus service? (y/N)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        print_info "Restarting Prometheus..."
        if ssh ${MONITORING_SERVER} "systemctl restart prometheus"; then
            print_success "Prometheus restarted"
        else
            print_error "Failed to restart Prometheus"
            exit 1
        fi
        
        print_info "Waiting 5 seconds for Prometheus to start..."
        sleep 5
        
        print_info "Checking Prometheus status..."
        if ssh ${MONITORING_SERVER} "systemctl is-active prometheus"; then
            print_success "Prometheus is running"
        else
            print_warning "Prometheus status check failed"
        fi
    else
        print_info "Skipping Prometheus restart"
        print_warning "Remember to restart Prometheus manually:"
        echo "  ssh ${MONITORING_SERVER} 'systemctl restart prometheus'"
    fi
    
    print_header "MONITORING CONFIGURATION DEPLOYMENT COMPLETE"
    print_success "Monitoring configuration has been deployed!"
    print_info "Verify Prometheus targets at: http://${MONITORING_SERVER#*@}:9090/targets"
}

main "$@"


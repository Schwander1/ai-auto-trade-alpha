#!/bin/bash
# Fix All Production Issues
# Comprehensive script to fix all identified production issues

set -e

PRODUCTION_SERVER="178.156.194.174"
ALPINE_SERVER="91.98.153.49"
PRODUCTION_USER="root"
ALPINE_USER="root"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

print_header() {
    echo ""
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
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

# Check current issues
check_current_issues() {
    print_header "CHECKING CURRENT ISSUES"
    
    # Check API key errors
    print_info "Checking API key errors in logs..."
    XAI_ERRORS=$(ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} "tail -n 200 /tmp/argo-blue.log 2>/dev/null | grep -c 'xAI API error.*Invalid API key' || echo '0'" 2>/dev/null || echo "0")
    MASSIVE_ERRORS=$(ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} "tail -n 200 /tmp/argo-blue.log 2>/dev/null | grep -c 'Massive API error 401.*Unknown API Key' || echo '0'" 2>/dev/null || echo "0")
    
    if [ "$XAI_ERRORS" -gt 0 ]; then
        print_warning "xAI Grok API key errors detected: $XAI_ERRORS"
        XAI_NEEDS_FIX=true
    else
        print_success "xAI Grok API key: OK"
        XAI_NEEDS_FIX=false
    fi
    
    if [ "$MASSIVE_ERRORS" -gt 0 ]; then
        print_warning "Massive API key errors detected: $MASSIVE_ERRORS"
        MASSIVE_NEEDS_FIX=true
    else
        print_success "Massive API key: OK"
        MASSIVE_NEEDS_FIX=false
    fi
    
    # Check Alpine backend
    print_info "Checking Alpine backend status..."
    ALPINE_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://${ALPINE_SERVER}:8001/api/v1/health 2>/dev/null || echo "000")
    
    if [ "$ALPINE_HEALTH" = "200" ]; then
        print_success "Alpine backend: Healthy"
        ALPINE_NEEDS_FIX=false
    else
        print_error "Alpine backend: Unhealthy (HTTP $ALPINE_HEALTH)"
        ALPINE_NEEDS_FIX=true
    fi
    
    # Check Argo service
    print_info "Checking Argo service status..."
    if ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} "systemctl is-active --quiet argo-trading.service" 2>/dev/null; then
        print_success "Argo service: Running"
    else
        print_error "Argo service: Not running"
        ARGO_NEEDS_FIX=true
    fi
}

# Find active config path
find_active_config() {
    print_info "Finding active production config..."
    
    # Check which environment is active
    ACTIVE_ENV=$(ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} "
        if [ -f /root/argo-production-green/.current ]; then
            echo 'green'
        elif [ -f /root/argo-production-blue/.current ]; then
            echo 'blue'
        else
            # Check which service is running
            if systemctl is-active --quiet argo-trading.service 2>/dev/null; then
                # Default to blue if service is running
                echo 'blue'
            else
                echo 'blue'
            fi
        fi
    " 2>/dev/null || echo "blue")
    
    CONFIG_PATH="/root/argo-production-${ACTIVE_ENV}/config.json"
    
    # Verify config exists
    if ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} "[ -f ${CONFIG_PATH} ]" 2>/dev/null; then
        print_success "Active config: ${CONFIG_PATH}"
        echo "${CONFIG_PATH}"
    else
        # Fallback to blue
        CONFIG_PATH="/root/argo-production-blue/config.json"
        if ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} "[ -f ${CONFIG_PATH} ]" 2>/dev/null; then
            print_warning "Using fallback config: ${CONFIG_PATH}"
            echo "${CONFIG_PATH}"
        else
            print_error "No config file found"
            return 1
        fi
    fi
}

# Fix API keys
fix_api_keys() {
    print_header "FIXING API KEYS"
    
    CONFIG_PATH=$(find_active_config)
    if [ $? -ne 0 ]; then
        print_error "Cannot proceed without config file"
        return 1
    fi
    
    print_info "Config path: ${CONFIG_PATH}"
    echo ""
    
    # Update xAI Grok key
    if [ "$XAI_NEEDS_FIX" = true ]; then
        print_warning "xAI Grok API key needs to be updated"
        echo "Get your API key from: https://console.x.ai"
        read -p "Enter xAI Grok API key (or press Enter to skip): " XAI_KEY
        
        if [ -n "$XAI_KEY" ]; then
            print_info "Updating xAI Grok API key..."
            ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} << ENDSSH
python3 << PYTHON
import json
import sys

try:
    with open('${CONFIG_PATH}', 'r') as f:
        config = json.load(f)
    
    # Update xAI key
    if 'xai' not in config:
        config['xai'] = {}
    config['xai']['api_key'] = '${XAI_KEY}'
    config['xai']['enabled'] = True
    
    # Also update x_api if it exists
    if 'x_api' not in config:
        config['x_api'] = {}
    config['x_api']['bearer_token'] = '${XAI_KEY}'
    config['x_api']['enabled'] = True
    
    with open('${CONFIG_PATH}', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✅ xAI Grok API key updated successfully")
except Exception as e:
    print(f"❌ Error updating xAI key: {e}")
    sys.exit(1)
PYTHON
ENDSSH
            
            if [ $? -eq 0 ]; then
                print_success "xAI Grok API key updated"
            else
                print_error "Failed to update xAI Grok API key"
            fi
        else
            print_warning "Skipping xAI Grok API key update"
        fi
    fi
    
    # Update Massive key
    if [ "$MASSIVE_NEEDS_FIX" = true ]; then
        print_warning "Massive API key needs to be updated"
        echo "Get your API key from: https://massive.com"
        read -p "Enter Massive API key (or press Enter to skip): " MASSIVE_KEY
        
        if [ -n "$MASSIVE_KEY" ]; then
            print_info "Updating Massive API key..."
            ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} << ENDSSH
python3 << PYTHON
import json
import sys

try:
    with open('${CONFIG_PATH}', 'r') as f:
        config = json.load(f)
    
    # Update Massive key
    if 'massive' not in config:
        config['massive'] = {}
    config['massive']['api_key'] = '${MASSIVE_KEY}'
    config['massive']['enabled'] = True
    
    with open('${CONFIG_PATH}', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✅ Massive API key updated successfully")
except Exception as e:
    print(f"❌ Error updating Massive key: {e}")
    sys.exit(1)
PYTHON
ENDSSH
            
            if [ $? -eq 0 ]; then
                print_success "Massive API key updated"
            else
                print_error "Failed to update Massive API key"
            fi
        else
            print_warning "Skipping Massive API key update"
        fi
    fi
}

# Fix Alpine backend
fix_alpine_backend() {
    print_header "FIXING ALPINE BACKEND"
    
    if [ "$ALPINE_NEEDS_FIX" = false ]; then
        print_success "Alpine backend is healthy, no fix needed"
        return 0
    fi
    
    print_info "Checking Alpine backend containers..."
    
    # Check if containers are running
    CONTAINERS=$(ssh ${ALPINE_USER}@${ALPINE_SERVER} "docker ps -a --filter 'name=alpine' --format '{{.Names}}' 2>/dev/null || echo ''" 2>/dev/null || echo "")
    
    if [ -z "$CONTAINERS" ]; then
        print_error "No Alpine containers found"
        print_info "You may need to start the Alpine backend manually"
        print_info "SSH to ${ALPINE_SERVER} and run:"
        print_info "  cd /root/alpine-production"
        print_info "  docker compose -f docker-compose.production.yml up -d"
        return 1
    fi
    
    print_info "Found containers: $CONTAINERS"
    
    # Find docker-compose file
    COMPOSE_FILE=$(ssh ${ALPINE_USER}@${ALPINE_SERVER} "
        find /root -name 'docker-compose.production.yml' -type f 2>/dev/null | head -1
    " 2>/dev/null || echo "")
    
    if [ -z "$COMPOSE_FILE" ]; then
        print_error "Could not find docker-compose.production.yml"
        print_info "Please manually restart Alpine backend on ${ALPINE_SERVER}"
        return 1
    fi
    
    print_info "Found docker-compose file: $COMPOSE_FILE"
    
    # Ask to restart
    print_warning "Alpine backend needs to be restarted"
    read -p "Restart Alpine backend now? (y/N): " RESTART
    
    if [[ "$RESTART" =~ ^[Yy]$ ]]; then
        print_info "Restarting Alpine backend..."
        
        COMPOSE_DIR=$(dirname "$COMPOSE_FILE")
        ssh ${ALPINE_USER}@${ALPINE_SERVER} "
            cd ${COMPOSE_DIR}
            docker compose -f docker-compose.production.yml restart 2>&1 || docker-compose -f docker-compose.production.yml restart 2>&1
        " 2>&1
        
        if [ $? -eq 0 ]; then
            print_success "Alpine backend restart initiated"
            print_info "Waiting 10 seconds for services to start..."
            sleep 10
            
            # Verify
            ALPINE_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://${ALPINE_SERVER}:8001/api/v1/health 2>/dev/null || echo "000")
            if [ "$ALPINE_HEALTH" = "200" ]; then
                print_success "Alpine backend is now healthy"
            else
                print_warning "Alpine backend may still be starting (HTTP $ALPINE_HEALTH)"
                print_info "Check status: curl http://${ALPINE_SERVER}:8001/api/v1/health"
            fi
        else
            print_error "Failed to restart Alpine backend"
            print_info "Please manually restart on ${ALPINE_SERVER}"
        fi
    else
        print_warning "Skipping Alpine backend restart"
        print_info "To restart manually:"
        print_info "  ssh ${ALPINE_USER}@${ALPINE_SERVER}"
        print_info "  cd ${COMPOSE_DIR}"
        print_info "  docker compose -f docker-compose.production.yml restart"
    fi
}

# Restart Argo service
restart_argo_service() {
    print_header "RESTARTING ARGO SERVICE"
    
    # Check if API keys were updated
    if [ "$XAI_NEEDS_FIX" = true ] || [ "$MASSIVE_NEEDS_FIX" = true ]; then
        print_warning "API keys were updated. Service restart is required."
        read -p "Restart Argo service now? (y/N): " RESTART
        
        if [[ "$RESTART" =~ ^[Yy]$ ]]; then
            print_info "Restarting Argo service..."
            ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} "systemctl restart argo-trading.service" 2>&1
            
            sleep 3
            
            if ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} "systemctl is-active --quiet argo-trading.service" 2>/dev/null; then
                print_success "Argo service restarted successfully"
            else
                print_error "Argo service restart failed"
                ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} "systemctl status argo-trading.service --no-pager -l | head -20" 2>&1
                return 1
            fi
        else
            print_warning "Service restart skipped"
            print_info "Remember to restart manually:"
            print_info "  ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} 'systemctl restart argo-trading.service'"
        fi
    else
        print_info "No API key updates, skipping service restart"
    fi
}

# Verify fixes
verify_fixes() {
    print_header "VERIFYING FIXES"
    
    # Check API keys
    print_info "Checking API key status..."
    sleep 5  # Wait for logs to update
    
    XAI_ERRORS=$(ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} "tail -n 50 /tmp/argo-blue.log 2>/dev/null | grep -c 'xAI API error.*Invalid API key' || echo '0'" 2>/dev/null || echo "0")
    MASSIVE_ERRORS=$(ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} "tail -n 50 /tmp/argo-blue.log 2>/dev/null | grep -c 'Massive API error 401.*Unknown API Key' || echo '0'" 2>/dev/null || echo "0")
    
    if [ "$XAI_ERRORS" -eq 0 ]; then
        print_success "xAI Grok API key: No recent errors"
    else
        print_warning "xAI Grok API key: Still seeing errors (may need more time)"
    fi
    
    if [ "$MASSIVE_ERRORS" -eq 0 ]; then
        print_success "Massive API key: No recent errors"
    else
        print_warning "Massive API key: Still seeing errors (may need more time)"
    fi
    
    # Check Alpine backend
    ALPINE_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://${ALPINE_SERVER}:8001/api/v1/health 2>/dev/null || echo "000")
    if [ "$ALPINE_HEALTH" = "200" ]; then
        print_success "Alpine backend: Healthy"
    else
        print_warning "Alpine backend: HTTP $ALPINE_HEALTH (may still be starting)"
    fi
    
    # Check Argo service
    if ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} "systemctl is-active --quiet argo-trading.service" 2>/dev/null; then
        print_success "Argo service: Running"
    else
        print_error "Argo service: Not running"
    fi
}

# Main execution
main() {
    print_header "FIX ALL PRODUCTION ISSUES"
    
    print_info "This script will fix all identified production issues:"
    echo "  1. API key problems (xAI Grok, Massive)"
    echo "  2. Alpine backend service status"
    echo "  3. Argo service restart (if needed)"
    echo ""
    
    # Initialize flags
    XAI_NEEDS_FIX=false
    MASSIVE_NEEDS_FIX=false
    ALPINE_NEEDS_FIX=false
    ARGO_NEEDS_FIX=false
    
    # Check current issues
    check_current_issues
    
    # Fix issues
    if [ "$XAI_NEEDS_FIX" = true ] || [ "$MASSIVE_NEEDS_FIX" = true ]; then
        fix_api_keys
    fi
    
    if [ "$ALPINE_NEEDS_FIX" = true ]; then
        fix_alpine_backend
    fi
    
    restart_argo_service
    
    # Verify
    verify_fixes
    
    print_header "FIX COMPLETE"
    print_success "All fixes have been applied!"
    echo ""
    print_info "Monitor logs to verify everything is working:"
    print_info "  ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} 'tail -f /tmp/argo-blue.log | grep -E \"API key|Invalid|Unauthorized|ERROR\"'"
    echo ""
    print_info "Check Alpine backend:"
    print_info "  curl http://${ALPINE_SERVER}:8001/api/v1/health"
}

main "$@"


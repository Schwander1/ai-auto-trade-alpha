#!/bin/bash
# Update API Keys in Production
# Helper script to update xAI Grok and Massive API keys in production config

set -e

PRODUCTION_SERVER="178.156.194.174"
PRODUCTION_USER="root"
# Will be determined dynamically based on active environment
CONFIG_PATH=""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_header() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo ""
}

# Find active config file
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
        return 0
    else
        # Fallback to blue
        CONFIG_PATH="/root/argo-production-blue/config.json"
        if ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} "[ -f ${CONFIG_PATH} ]" 2>/dev/null; then
            print_warning "Using fallback config: ${CONFIG_PATH}"
            return 0
        else
            print_error "No config file found"
            print_info "Available config files:"
            ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} "find /root/argo-production* -name 'config.json' 2>/dev/null || echo 'No config files found'"
            return 1
        fi
    fi
}

# Check if config file exists (legacy function name for compatibility)
check_config() {
    find_active_config
}

# Update xAI Grok API key
update_xai_key() {
    print_header "UPDATE XAI GROK API KEY"
    
    read -p "Enter xAI Grok API key (or press Enter to skip): " XAI_KEY
    
    if [ -z "$XAI_KEY" ]; then
        print_warning "Skipping xAI Grok API key update"
        return 0
    fi
    
    print_info "Updating xAI Grok API key..."
    
    ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} << ENDSSH
python3 << PYTHON
import json
import sys

CONFIG_PATH = '${CONFIG_PATH}'

try:
    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)
    
    # Update xAI key (check both 'xai' and 'x_api' keys)
    if 'xai' not in config:
        config['xai'] = {}
    config['xai']['api_key'] = '${XAI_KEY}'
    config['xai']['enabled'] = True
    
    # Also update x_api if it exists
    if 'x_api' not in config:
        config['x_api'] = {}
    config['x_api']['bearer_token'] = '${XAI_KEY}'
    config['x_api']['enabled'] = True
    
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✅ xAI Grok API key updated successfully")
except Exception as e:
    print(f"❌ Error updating xAI key: {e}")
    sys.exit(1)
PYTHON
ENDSSH
    
    if [ $? -eq 0 ]; then
        print_success "xAI Grok API key updated successfully"
    else
        print_error "Failed to update xAI Grok API key"
        return 1
    fi
}

# Update Massive API key
update_massive_key() {
    print_header "UPDATE MASSIVE API KEY"
    
    read -p "Enter Massive API key (or press Enter to skip): " MASSIVE_KEY
    
    if [ -z "$MASSIVE_KEY" ]; then
        print_warning "Skipping Massive API key update"
        return 0
    fi
    
    print_info "Updating Massive API key..."
    
    ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} << ENDSSH
python3 << PYTHON
import json
import sys

CONFIG_PATH = '${CONFIG_PATH}'

try:
    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)
    
    # Update Massive key
    if 'massive' not in config:
        config['massive'] = {}
    config['massive']['api_key'] = '${MASSIVE_KEY}'
    config['massive']['enabled'] = True
    
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✅ Massive API key updated successfully")
except Exception as e:
    print(f"❌ Error updating Massive key: {e}")
    sys.exit(1)
PYTHON
ENDSSH
    
    if [ $? -eq 0 ]; then
        print_success "Massive API key updated successfully"
    else
        print_error "Failed to update Massive API key"
        return 1
    fi
}

# Restart service
restart_service() {
    print_header "RESTART SERVICE"
    
    print_warning "API keys have been updated. Service restart is required."
    read -p "Restart Argo service now? (y/N): " RESTART
    
    if [[ "$RESTART" =~ ^[Yy]$ ]]; then
        print_info "Restarting Argo service..."
        ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} "systemctl restart argo-trading.service"
        
        sleep 3
        
        if ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} "systemctl is-active --quiet argo-trading.service"; then
            print_success "Service restarted successfully"
        else
            print_error "Service restart failed - check logs"
            ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} "systemctl status argo-trading.service --no-pager -l | head -20"
            return 1
        fi
    else
        print_warning "Service restart skipped"
        print_info "Remember to restart the service manually:"
        print_info "  ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} 'systemctl restart argo-trading.service'"
    fi
}

# Main execution
main() {
    print_header "PRODUCTION API KEY UPDATE"
    
    print_info "This script will help you update API keys in production."
    print_info "Server: ${PRODUCTION_SERVER}"
    echo ""
    
    if ! find_active_config; then
        print_error "Cannot proceed without config file"
        exit 1
    fi
    
    print_info "Config: ${CONFIG_PATH}"
    echo ""
    
    # Update keys
    update_xai_key
    update_massive_key
    
    # Restart service
    restart_service
    
    print_header "API KEY UPDATE COMPLETE"
    print_success "API keys have been updated!"
    print_info "Monitor logs to verify API keys are working:"
    print_info "  ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} 'tail -f /tmp/argo-blue.log | grep -E \"API key|Invalid|Unauthorized\"'"
}

main "$@"


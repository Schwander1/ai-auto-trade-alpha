#!/bin/bash
# Setup API Key Update
# Interactive script to help update API keys in production

set -e

PRODUCTION_SERVER="178.156.194.174"
PRODUCTION_USER="root"
CONFIG_PATH="/root/argo-production-green/config.json"

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

# Check current API key status
check_current_status() {
    print_header "CURRENT API KEY STATUS"
    
    print_info "Checking current API key errors in logs..."
    
    ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} << 'ENDSSH'
echo "Recent API key errors:"
tail -n 200 /tmp/argo-blue.log 2>/dev/null | grep -E "xAI API error|Massive API error" | tail -5 || echo "No recent errors found"
ENDSSH
}

# Show API key sources
show_api_key_sources() {
    print_header "API KEY SOURCES"
    
    echo "1. xAI Grok API Key:"
    echo "   - Get from: https://console.x.ai"
    echo "   - Format: xai-..."
    echo ""
    echo "2. Massive API Key:"
    echo "   - Get from: https://massive.com"
    echo "   - Format: Alphanumeric string"
    echo ""
    echo "3. Current config location:"
    echo "   - ${CONFIG_PATH}"
    echo ""
}

# Update API keys interactively
update_api_keys() {
    print_header "UPDATE API KEYS"
    
    print_warning "You will be prompted to enter API keys."
    print_info "Press Enter to skip any key you don't want to update."
    echo ""
    
    read -p "Enter xAI Grok API key (or press Enter to skip): " XAI_KEY
    read -p "Enter Massive API key (or press Enter to skip): " MASSIVE_KEY
    
    if [ -z "$XAI_KEY" ] && [ -z "$MASSIVE_KEY" ]; then
        print_warning "No keys provided. Skipping update."
        return 0
    fi
    
    print_info "Updating API keys in production config..."
    
    ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} << ENDSSH
python3 << PYTHON
import json
import sys

try:
    with open('${CONFIG_PATH}', 'r') as f:
        config = json.load(f)
    
    updated = False
    
    # Update xAI key
    if '${XAI_KEY}':
        if 'xai' not in config:
            config['xai'] = {}
        config['xai']['api_key'] = '${XAI_KEY}'
        config['xai']['enabled'] = True
        
        # Also update x_api if it exists
        if 'x_api' not in config:
            config['x_api'] = {}
        config['x_api']['bearer_token'] = '${XAI_KEY}'
        config['x_api']['enabled'] = True
        
        updated = True
        print("✅ xAI Grok API key updated")
    
    # Update Massive key
    if '${MASSIVE_KEY}':
        if 'massive' not in config:
            config['massive'] = {}
        config['massive']['api_key'] = '${MASSIVE_KEY}'
        config['massive']['enabled'] = True
        
        updated = True
        print("✅ Massive API key updated")
    
    if updated:
        with open('${CONFIG_PATH}', 'w') as f:
            json.dump(config, f, indent=2)
        print("✅ Config file updated successfully")
    else:
        print("⚠️  No keys were updated")
        
except Exception as e:
    print(f"❌ Error updating config: {e}")
    sys.exit(1)
PYTHON
ENDSSH
    
    if [ $? -eq 0 ]; then
        print_success "API keys updated successfully"
        
        print_warning "Service restart required for changes to take effect."
        read -p "Restart service now? (y/N): " RESTART
        
        if [[ "$RESTART" =~ ^[Yy]$ ]]; then
            print_info "Restarting service..."
            ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} "systemctl restart argo-trading.service"
            sleep 3
            
            if ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} "systemctl is-active --quiet argo-trading.service"; then
                print_success "Service restarted successfully"
            else
                print_error "Service restart failed"
                return 1
            fi
        else
            print_info "Service restart skipped. Restart manually:"
            print_info "  ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} 'systemctl restart argo-trading.service'"
        fi
    else
        print_error "Failed to update API keys"
        return 1
    fi
}

# Verify API keys after update
verify_api_keys() {
    print_header "VERIFYING API KEYS"
    
    print_info "Waiting 10 seconds for service to initialize..."
    sleep 10
    
    print_info "Checking for API key errors in logs..."
    
    ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} << 'ENDSSH'
echo "Recent API key status:"
tail -n 50 /tmp/argo-blue.log 2>/dev/null | grep -E "xAI API error|Massive API error|API key" | tail -5 || echo "No API key errors found in recent logs"
ENDSSH
}

# Main execution
main() {
    print_header "API KEY UPDATE SETUP"
    
    check_current_status
    show_api_key_sources
    
    read -p "Do you want to update API keys now? (y/N): " UPDATE
    
    if [[ "$UPDATE" =~ ^[Yy]$ ]]; then
        update_api_keys
        verify_api_keys
    else
        print_info "API key update skipped."
        print_info "To update later, run: ./scripts/update_production_api_keys.sh"
    fi
    
    print_header "SETUP COMPLETE"
}

main "$@"


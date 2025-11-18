#!/bin/bash
# Enable dual trading for production: Prop Firm + Argo
# This script sets up both trading modes to execute simultaneously

set -e

echo "🔧 ENABLING DUAL TRADING FOR PRODUCTION"
echo "========================================"
echo ""

# Config paths
ARGO_CONFIG="/root/argo-production-green/config.json"
PROP_FIRM_CONFIG="/root/argo-production-prop-firm/config.json"
LOCAL_CONFIG="argo/config.json"

# Function to update config
update_config() {
    local config_path=$1
    local is_prop_firm=$2
    
    if [ ! -f "$config_path" ]; then
        echo "⚠️  Config not found: $config_path"
        return 1
    fi
    
    echo "📝 Updating: $config_path"
    
    python3 << PYTHON
import json
import sys

config_path = "$config_path"
is_prop_firm = "$is_prop_firm" == "true"

try:
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    updated = False
    
    # Enable trading
    if 'trading' not in config:
        config['trading'] = {}
    
    trading = config['trading']
    if not trading.get('auto_execute', False):
        trading['auto_execute'] = True
        updated = True
        print("   ✅ Enabled auto_execute")
    
    if not trading.get('force_24_7_mode', False):
        trading['force_24_7_mode'] = True
        updated = True
        print("   ✅ Enabled force_24_7_mode")
    
    # Enable prop firm if this is prop firm config
    if is_prop_firm:
        if 'prop_firm' not in config:
            config['prop_firm'] = {}
        
        prop_firm = config['prop_firm']
        if not prop_firm.get('enabled', False):
            prop_firm['enabled'] = True
            updated = True
            print("   ✅ Enabled prop_firm mode")
        
        if 'account' not in prop_firm:
            prop_firm['account'] = 'prop_firm_test'
            updated = True
        
        if 'risk_limits' not in prop_firm:
            prop_firm['risk_limits'] = {
                'max_drawdown_pct': 2.0,
                'daily_loss_limit_pct': 4.5,
                'max_position_size_pct': 3.0,
                'min_confidence': 82.0,
                'max_positions': 3,
                'max_stop_loss_pct': 1.5
            }
            updated = True
            print("   ✅ Set prop_firm risk limits")
    else:
        # For Argo config, ensure prop firm is disabled
        if 'prop_firm' in config:
            if config['prop_firm'].get('enabled', False):
                config['prop_firm']['enabled'] = False
                updated = True
                print("   ✅ Disabled prop_firm mode (Argo trading only)")
    
    if updated:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        print("   ✅ Config updated successfully")
    else:
        print("   ℹ️  No changes needed")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)
PYTHON
}

# Update Argo config (prop firm disabled)
if [ -f "$ARGO_CONFIG" ]; then
    update_config "$ARGO_CONFIG" false
    echo ""
fi

# Update Prop Firm config (prop firm enabled)
if [ -f "$PROP_FIRM_CONFIG" ]; then
    update_config "$PROP_FIRM_CONFIG" true
    echo ""
fi

# Update local config for testing
if [ -f "$LOCAL_CONFIG" ]; then
    echo "📝 Updating local config (for testing both modes)"
    update_config "$LOCAL_CONFIG" true
    echo ""
fi

echo "========================================"
echo "✅ DUAL TRADING CONFIGURATION COMPLETE"
echo "========================================"
echo ""
echo "📋 NEXT STEPS:"
echo ""
echo "1. Ensure Alpaca credentials are configured:"
echo "   - Argo account: alpaca.api_key / alpaca.secret_key"
echo "   - Prop firm account: alpaca.prop_firm_test.api_key / secret_key"
echo ""
echo "2. Run two separate service instances:"
echo ""
echo "   For ARGO trading (port 8000):"
echo "   cd /root/argo-production-green"
echo "   export ARGO_CONFIG_PATH=/root/argo-production-green/config.json"
echo "   uvicorn main:app --host 0.0.0.0 --port 8000"
echo ""
echo "   For PROP FIRM trading (port 8001):"
echo "   cd /root/argo-production-prop-firm"
echo "   export ARGO_CONFIG_PATH=/root/argo-production-prop-firm/config.json"
echo "   uvicorn main:app --host 0.0.0.0 --port 8001"
echo ""
echo "3. Or use systemd services (if configured):"
echo "   systemctl start argo-trading.service"
echo "   systemctl start argo-trading-prop-firm.service"
echo ""
echo "4. Verify both services are running:"
echo "   curl http://localhost:8000/health  # Argo"
echo "   curl http://localhost:8001/health  # Prop Firm"
echo ""


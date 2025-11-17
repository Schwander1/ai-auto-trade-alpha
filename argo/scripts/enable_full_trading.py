#!/usr/bin/env python3
"""
Enable Full Trading Script
Enables automated trading after successful test trade
"""
import sys
import json
import logging
from pathlib import Path

# Add paths - ensure argo is in path
argo_path = Path(__file__).parent.parent
if str(argo_path) not in sys.path:
    sys.path.insert(0, str(argo_path))
# Also add workspace root for shared packages
workspace_root = argo_path.parent
if str(workspace_root) not in sys.path:
    sys.path.insert(0, str(workspace_root))

from argo.core.paper_trading_engine import PaperTradingEngine
from argo.core.environment import detect_environment

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def enable_full_trading():
    """Enable full automated trading"""
    
    print('\n' + '='*70)
    print('🚀 ENABLE FULL AUTOMATED TRADING')
    print('='*70)
    
    # Detect environment
    environment = detect_environment()
    print(f'\n🌍 Environment: {environment.upper()}')
    
    # Verify trading engine is connected
    print('\n📊 Verifying trading engine...')
    trading_engine = PaperTradingEngine()
    
    if not trading_engine.alpaca_enabled:
        print('❌ ERROR: Alpaca not connected. Cannot enable trading.')
        return False
    
    account = trading_engine.get_account_details()
    print(f'✅ Connected to: {trading_engine.account_name}')
    print(f'   Portfolio: ${account["portfolio_value"]:,.2f}')
    
    # Check for existing positions (verify test trade worked)
    positions = trading_engine.get_positions()
    print(f'\n📊 Current Positions: {len(positions)}')
    
    if positions:
        print('   Existing positions found (test trade may have executed):')
        for pos in positions[:3]:  # Show first 3
            print(f'   - {pos["symbol"]}: {pos["side"]} {pos["qty"]} @ ${pos["entry_price"]:.2f}')
    
    # Update config.json to enable auto_execute
    print('\n⚙️  Updating configuration...')
    
    # Find config file
    config_path = None
    env_path = Path.cwd() / 'config.json'
    prod_path = Path('/root/argo-production/config.json')
    
    if prod_path.exists():
        config_path = prod_path
    elif env_path.exists():
        config_path = env_path
    else:
        # Try relative to script
        config_path = Path(__file__).parent.parent / 'config.json'
    
    if not config_path.exists():
        print(f'❌ ERROR: Config file not found at {config_path}')
        return False
    
    print(f'   Config file: {config_path}')
    
    # Read and update config
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Enable auto_execute
    if 'trading' not in config:
        config['trading'] = {}
    
    current_auto_execute = config['trading'].get('auto_execute', False)
    
    if current_auto_execute:
        print('   ⚠️  auto_execute is already enabled')
    else:
        config['trading']['auto_execute'] = True
        print('   ✅ Enabling auto_execute: true')
    
    # Save config
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print('\n' + '='*70)
    print('✅ FULL TRADING ENABLED')
    print('='*70)
    print('\n📝 Trading Status:')
    print(f'   Environment: {environment}')
    print(f'   Account: {trading_engine.account_name}')
    print(f'   Auto-execute: {config["trading"]["auto_execute"]}')
    print(f'   Current Positions: {len(positions)}')
    print('\n🚀 The system will now:')
    print('   - Generate signals every 5 seconds')
    print('   - Execute trades automatically when signals meet criteria')
    print('   - Apply all risk management rules')
    print('   - Monitor positions and auto-exit on stop-loss/take-profit')
    print('\n⚠️  IMPORTANT:')
    print('   - Monitor the system regularly')
    print('   - Review trades in Alpaca dashboard')
    print('   - Check logs for any issues')
    print('   - Ensure risk management is working correctly')
    print('\n' + '='*70 + '\n')
    
    return True

if __name__ == '__main__':
    success = enable_full_trading()
    sys.exit(0 if success else 1)


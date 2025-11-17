#!/usr/bin/env python3
"""
Deploy V11 Optimal Configuration to Production
Updates production config with V11 optimal settings
"""
import json
import shutil
from pathlib import Path
from datetime import datetime

def load_v11_config():
    """Load V11 configuration"""
    config_path = Path(__file__).parent.parent / "config.v11.production.json"
    with open(config_path, 'r') as f:
        return json.load(f)

def backup_current_config(config_path: Path):
    """Backup current configuration"""
    if config_path.exists():
        backup_path = config_path.parent / f"config.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        shutil.copy2(config_path, backup_path)
        print(f"✅ Backed up current config to: {backup_path}")
        return backup_path
    return None

def update_config_with_v11(config_path: Path, v11_config: dict):
    """Update config.json with V11 settings"""
    # Load existing config
    if config_path.exists():
        with open(config_path, 'r') as f:
            current_config = json.load(f)
    else:
        current_config = {}
    
    # Merge V11 trading settings
    if 'trading' not in current_config:
        current_config['trading'] = {}
    
    # Update trading settings from V11
    v11_trading = v11_config.get('trading', {})
    for key, value in v11_trading.items():
        current_config['trading'][key] = value
    
    # Update backtest settings
    if 'backtest' not in current_config:
        current_config['backtest'] = {}
    
    v11_backtest = v11_config.get('backtest', {})
    for key, value in v11_backtest.items():
        current_config['backtest'][key] = value
    
    # Preserve other settings (alpaca, strategy, etc.)
    for section in ['alpaca', 'strategy', 'massive', 'alpha_vantage', 'xai', 'sonar']:
        if section in v11_config:
            if section not in current_config:
                current_config[section] = {}
            # Merge but preserve existing values (especially API keys)
            for key, value in v11_config[section].items():
                if key not in current_config[section] or current_config[section][key] in ['FROM_CONFIG', 'FROM_AWS_SECRETS']:
                    current_config[section][key] = value
    
    # Save updated config
    with open(config_path, 'w') as f:
        json.dump(current_config, f, indent=2)
    
    print(f"✅ Updated config at: {config_path}")

def main():
    """Main deployment function"""
    print("🚀 Deploying V11 Optimal Configuration")
    print("=" * 60)
    
    # Paths
    argo_dir = Path(__file__).parent.parent
    config_path = argo_dir / "config.json"
    v11_config_path = argo_dir / "config.v11.production.json"
    
    # Load V11 config
    print("\n📋 Loading V11 configuration...")
    v11_config = load_v11_config()
    print("✅ V11 config loaded")
    
    # Backup current config
    print("\n💾 Backing up current configuration...")
    backup_path = backup_current_config(config_path)
    
    # Update config
    print("\n⚙️  Updating configuration with V11 settings...")
    update_config_with_v11(config_path, v11_config)
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ V11 Configuration Deployed Successfully!")
    print("\n📊 Key V11 Settings Applied:")
    print(f"  - Min Confidence: {v11_config['trading']['min_confidence']}%")
    print(f"  - Position Size: {v11_config['trading']['position_size_pct']}%")
    print(f"  - Max Drawdown: {v11_config['trading']['max_drawdown_pct']}%")
    print(f"  - Enhanced Cost Model: {v11_config['backtest']['use_enhanced_cost_model']}")
    print(f"  - Volume Confirmation: {v11_config['backtest']['volume_confirmation']}")
    print(f"  - Dynamic Stop Loss: {v11_config['backtest']['dynamic_stop_loss']}")
    
    if backup_path:
        print(f"\n💾 Backup saved to: {backup_path}")
    
    print("\n⚠️  Next Steps:")
    print("  1. Review the updated config.json")
    print("  2. Restart the trading service")
    print("  3. Monitor performance closely")
    print("  4. Compare live results with backtest expectations")

if __name__ == '__main__':
    main()


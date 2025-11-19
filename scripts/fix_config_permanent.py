#!/usr/bin/env python3
"""
Fix Configuration Permanently
Ensures 24/7 mode and auto-execute are always enabled
"""
import json
import sys
from pathlib import Path

def fix_config(config_path: Path):
    """Fix configuration file"""
    if not config_path.exists():
        print(f"⚠️  Config file not found: {config_path}")
        return False

    try:
        # Read config
        with open(config_path, 'r') as f:
            config = json.load(f)

        # Ensure trading section exists
        if 'trading' not in config:
            config['trading'] = {}

        trading = config['trading']
        updated = False

        # Enable 24/7 mode
        if not trading.get('force_24_7_mode', False):
            trading['force_24_7_mode'] = True
            updated = True
            print(f"   ✅ Enabled force_24_7_mode")

        # Enable auto-execute
        if not trading.get('auto_execute', False):
            trading['auto_execute'] = True
            updated = True
            print(f"   ✅ Enabled auto_execute")

        # Save if updated
        if updated:
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            print(f"   💾 Saved config: {config_path}")
            return True
        else:
            print(f"   ✅ Config already correct: {config_path}")
            return True

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    """Main function"""
    print("🔧 Fixing Configuration Permanently...")
    print("")

    workspace_root = Path(__file__).parent.parent
    argo_dir = workspace_root / "argo"

    config_paths = [
        argo_dir / "config.json",
        workspace_root / "config.json",
    ]

    fixed = False
    for config_path in config_paths:
        if config_path.exists():
            print(f"📝 Checking: {config_path}")
            if fix_config(config_path):
                fixed = True
            print("")

    if fixed:
        print("✅ Configuration fixed!")
        print("")
        print("⚠️  Note: Restart services for changes to take effect:")
        print("   - Main service (port 8000)")
        print("   - Prop Firm executor (port 8001)")
    else:
        print("✅ All configurations are correct!")

if __name__ == "__main__":
    main()

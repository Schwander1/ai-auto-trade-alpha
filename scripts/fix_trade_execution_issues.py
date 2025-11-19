#!/usr/bin/env python3
"""
Fix Trade Execution Issues
Comprehensive fix for all identified trade execution problems
"""
import json
import sys
import subprocess
from pathlib import Path
from typing import Dict, List

def check_and_install_alpaca():
    """Check if Alpaca SDK is installed and install if needed"""
    print("1️⃣  Checking Alpaca SDK Installation")
    print("-" * 80)

    try:
        import alpaca
        print("✅ Alpaca SDK is installed")
        return True
    except ImportError:
        print("❌ Alpaca SDK not installed")
        print("   Installing alpaca-py...")

        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "alpaca-py", "--quiet"],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent / "argo"
            )
            if result.returncode == 0:
                print("✅ Alpaca SDK installed successfully")
                return True
            else:
                print(f"⚠️  Installation warning: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Failed to install Alpaca SDK: {e}")
            print("   Please install manually: pip install alpaca-py")
            return False

def check_config_files() -> List[Path]:
    """Find and check configuration files"""
    print("\n2️⃣  Checking Configuration Files")
    print("-" * 80)

    config_paths = [
        Path("argo/config.json"),
        Path("argo/argo/config.json"),
        Path("config.json"),
    ]

    found_configs = []
    for config_path in config_paths:
        if config_path.exists():
            found_configs.append(config_path)
            print(f"✅ Found: {config_path}")
        else:
            print(f"⚠️  Not found: {config_path}")

    return found_configs

def fix_config(config_path: Path) -> bool:
    """Fix configuration to enable trading"""
    print(f"\n3️⃣  Fixing Configuration: {config_path}")
    print("-" * 80)

    try:
        with open(config_path, 'r') as f:
            config = json.load(f)

        # Ensure trading section exists
        if 'trading' not in config:
            config['trading'] = {}
            print("   ✅ Created trading section")

        trading = config['trading']
        changes = []

        # Enable auto_execute
        if not trading.get('auto_execute', False):
            trading['auto_execute'] = True
            changes.append("Enabled auto_execute")
            print("   ✅ Enabled auto_execute")
        else:
            print("   ✅ auto_execute already enabled")

        # Enable 24/7 mode
        if not trading.get('force_24_7_mode', False):
            trading['force_24_7_mode'] = True
            changes.append("Enabled force_24_7_mode")
            print("   ✅ Enabled force_24_7_mode")
        else:
            print("   ✅ force_24_7_mode already enabled")

        # Ensure Alpaca section exists
        if 'alpaca' not in config:
            config['alpaca'] = {}
            print("   ✅ Created alpaca section")

        # Check if credentials are set
        alpaca = config.get('alpaca', {})
        has_credentials = False

        # Check for prop firm account
        if 'prop_firm' in config and config['prop_firm'].get('enabled', False):
            prop_account = config['prop_firm'].get('account', 'prop_firm_test')
            if prop_account in alpaca:
                account_config = alpaca[prop_account]
                if account_config.get('api_key') and account_config.get('secret_key'):
                    has_credentials = True
                    print(f"   ✅ Prop firm credentials found for account: {prop_account}")

        # Check for dev/production accounts
        for env in ['dev', 'development', 'production']:
            if env in alpaca:
                env_config = alpaca[env]
                if env_config.get('api_key') and env_config.get('secret_key'):
                    has_credentials = True
                    print(f"   ✅ {env} credentials found")

        # Check root level alpaca config
        if alpaca.get('api_key') and alpaca.get('secret_key'):
            has_credentials = True
            print("   ✅ Root level Alpaca credentials found")

        if not has_credentials:
            print("   ⚠️  No Alpaca credentials found in config")
            print("   ⚠️  System will try AWS Secrets Manager or environment variables")

        # Save config if changes were made
        if changes:
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            print(f"\n   💾 Configuration saved with changes: {', '.join(changes)}")
            return True
        else:
            print("\n   ✅ Configuration already correct")
            return False

    except Exception as e:
        print(f"   ❌ Error fixing config: {e}")
        return False

def check_environment_variables():
    """Check for Alpaca credentials in environment variables"""
    print("\n4️⃣  Checking Environment Variables")
    print("-" * 80)

    import os

    api_key = os.getenv('ALPACA_API_KEY')
    secret_key = os.getenv('ALPACA_SECRET_KEY')

    if api_key and secret_key:
        print("✅ Alpaca credentials found in environment variables")
        return True
    else:
        print("⚠️  Alpaca credentials not found in environment variables")
        print("   Set ALPACA_API_KEY and ALPACA_SECRET_KEY if needed")
        return False

def verify_alpaca_connection():
    """Verify Alpaca connection after fixes"""
    print("\n5️⃣  Verifying Alpaca Connection")
    print("-" * 80)

    try:
        sys.path.insert(0, str(Path(__file__).parent.parent / "argo"))
        from argo.core.paper_trading_engine import PaperTradingEngine

        engine = PaperTradingEngine()
        if engine.alpaca_enabled:
            account = engine.get_account_details()
            if account:
                print("✅ Alpaca connection successful!")
                print(f"   Account: {engine.account_name}")
                print(f"   Environment: {engine.environment}")
                print(f"   Portfolio Value: ${account.get('portfolio_value', 0):,.2f}")
                return True
            else:
                print("⚠️  Alpaca enabled but account details unavailable")
                return False
        else:
            print("⚠️  Alpaca not connected (simulation mode)")
            print("   This is expected if:")
            print("   - Alpaca SDK is not installed")
            print("   - Credentials are not configured")
            print("   - Running in development without credentials")
            return False
    except Exception as e:
        print(f"⚠️  Error verifying connection: {e}")
        return False

def main():
    """Run all fixes"""
    print("=" * 80)
    print("🔧 FIXING TRADE EXECUTION ISSUES")
    print("=" * 80)
    print()

    # 1. Check and install Alpaca SDK
    alpaca_installed = check_and_install_alpaca()

    # 2. Check configuration files
    config_files = check_config_files()

    if not config_files:
        print("\n❌ No configuration files found!")
        print("   Please ensure config.json exists in argo/ directory")
        return

    # 3. Fix each config file
    configs_fixed = False
    for config_path in config_files:
        if fix_config(config_path):
            configs_fixed = True

    # 4. Check environment variables
    env_creds = check_environment_variables()

    # 5. Verify connection
    if alpaca_installed:
        connection_ok = verify_alpaca_connection()
    else:
        connection_ok = False
        print("\n⚠️  Skipping connection verification (Alpaca SDK not installed)")

    # Summary
    print("\n" + "=" * 80)
    print("📋 FIX SUMMARY")
    print("=" * 80)

    if alpaca_installed:
        print("✅ Alpaca SDK: Installed")
    else:
        print("❌ Alpaca SDK: Not installed (install manually: pip install alpaca-py)")

    if configs_fixed:
        print("✅ Configuration: Updated")
    else:
        print("✅ Configuration: Already correct")

    if env_creds:
        print("✅ Environment Variables: Credentials found")
    else:
        print("⚠️  Environment Variables: No credentials (will use config or AWS Secrets)")

    if connection_ok:
        print("✅ Alpaca Connection: Connected")
    else:
        print("⚠️  Alpaca Connection: Not connected (check credentials)")

    print("\n💡 NEXT STEPS:")
    print("   1. If Alpaca SDK was just installed, restart the signal generation service")
    print("   2. Verify Alpaca credentials are set in config.json or AWS Secrets Manager")
    print("   3. Check that signal distributor and trading executors are running")
    print("   4. Monitor signal execution logs")

    print("\n" + "=" * 80)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

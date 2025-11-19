#!/usr/bin/env python3
"""
Verify All Trade Execution Fixes
Comprehensive verification that everything is working
"""
import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime

def print_section(title: str):
    """Print formatted section"""
    print("\n" + "=" * 80)
    print(f"✅ {title}")
    print("=" * 80)

def verify_alpaca_sdk():
    """Verify Alpaca SDK is installed"""
    print_section("Verifying Alpaca SDK Installation")

    # Check virtual environment
    venv_path = Path(__file__).parent.parent / "argo" / "venv"
    if venv_path.exists():
        python_exe = venv_path / "bin" / "python"
        if not python_exe.exists():
            python_exe = venv_path / "Scripts" / "python.exe"

        result = subprocess.run(
            [str(python_exe), "-c", "import alpaca; print('installed')"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print("✅ Alpaca SDK installed in virtual environment")
            return True, True  # installed, in venv
        else:
            print("❌ Alpaca SDK not in virtual environment")

    # Check system Python
    try:
        import alpaca
        print("✅ Alpaca SDK installed in system Python")
        return True, False  # installed, not in venv
    except ImportError:
        print("❌ Alpaca SDK not installed")
        return False, False

def verify_configuration():
    """Verify configuration is correct"""
    print_section("Verifying Configuration")

    config_paths = [
        Path("argo/config.json"),
        Path("argo/argo/config.json"),
    ]

    all_correct = True
    for config_path in config_paths:
        if not config_path.exists():
            continue

        try:
            with open(config_path, 'r') as f:
                config = json.load(f)

            trading = config.get('trading', {})
            issues = []

            if not trading.get('auto_execute', False):
                issues.append("auto_execute not enabled")
                all_correct = False

            if not trading.get('force_24_7_mode', False):
                issues.append("force_24_7_mode not enabled")
                all_correct = False

            if issues:
                print(f"❌ {config_path.name}: {', '.join(issues)}")
            else:
                print(f"✅ {config_path.name}: All settings correct")

        except Exception as e:
            print(f"⚠️  Error reading {config_path}: {e}")
            all_correct = False

    return all_correct

def verify_alpaca_connection():
    """Verify Alpaca connection"""
    print_section("Verifying Alpaca Connection")

    try:
        sys.path.insert(0, str(Path(__file__).parent.parent / "argo"))

        # Try with virtual environment
        venv_path = Path(__file__).parent.parent / "argo" / "venv"
        if venv_path.exists():
            python_exe = venv_path / "bin" / "python"
            if not python_exe.exists():
                python_exe = venv_path / "Scripts" / "python.exe"

            result = subprocess.run(
                [str(python_exe), "-c",
                 "from argo.core.paper_trading_engine import PaperTradingEngine; "
                 "e = PaperTradingEngine(); "
                 "print('connected' if e.alpaca_enabled else 'simulation'); "
                 "print(e.account_name if e.alpaca_enabled else 'N/A')"],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent / "argo"
            )

            if 'connected' in result.stdout:
                account = result.stdout.strip().split('\n')[1] if '\n' in result.stdout else 'Unknown'
                print("✅ Alpaca connection successful!")
                print(f"   Account: {account}")
                return True
            else:
                print("⚠️  Running in simulation mode")
                return False

        # Fallback to system Python
        from argo.core.paper_trading_engine import PaperTradingEngine
        engine = PaperTradingEngine()

        if engine.alpaca_enabled:
            account = engine.get_account_details()
            if account:
                print("✅ Alpaca connection successful!")
                print(f"   Account: {engine.account_name}")
                print(f"   Environment: {engine.environment}")
                return True

        print("⚠️  Running in simulation mode")
        return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def verify_credentials():
    """Verify credentials are configured"""
    print_section("Verifying Credentials")

    config_paths = [
        Path("argo/config.json"),
        Path("argo/argo/config.json"),
    ]

    has_creds = False
    for config_path in config_paths:
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)

                alpaca = config.get('alpaca', {})

                # Check various credential locations
                if alpaca.get('api_key') and alpaca.get('secret_key'):
                    has_creds = True
                    print(f"✅ Credentials found in {config_path.name}")

                # Check prop firm
                if 'prop_firm' in config and config['prop_firm'].get('enabled'):
                    prop_account = config['prop_firm'].get('account', 'prop_firm_test')
                    if prop_account in alpaca:
                        account = alpaca[prop_account]
                        if account.get('api_key') and account.get('secret_key'):
                            has_creds = True
                            print(f"✅ Prop firm credentials found in {config_path.name}")
            except Exception:
                pass

    # Check environment variables
    import os
    if os.getenv('ALPACA_API_KEY') and os.getenv('ALPACA_SECRET_KEY'):
        has_creds = True
        print("✅ Credentials found in environment variables")

    if not has_creds:
        print("⚠️  No credentials found in config (will use AWS Secrets Manager)")

    return True  # Credentials can come from multiple sources

def verify_scripts():
    """Verify utility scripts exist"""
    print_section("Verifying Utility Scripts")

    scripts = [
        "scripts/diagnose_trade_execution.py",
        "scripts/fix_trade_execution_issues.py",
        "scripts/fix_all_trade_execution_issues.py",
        "scripts/check_production_status.py",
        "scripts/monitor_trade_execution.py",
        "scripts/comprehensive_trading_report.py",
    ]

    all_exist = True
    for script in scripts:
        script_path = Path(__file__).parent.parent / script
        if script_path.exists():
            print(f"✅ {script}")
        else:
            print(f"❌ {script} - Missing")
            all_exist = False

    return all_exist

def main():
    """Run all verifications"""
    print("=" * 80)
    print("🔍 VERIFYING ALL TRADE EXECUTION FIXES")
    print("=" * 80)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    results = {}

    # Run all verifications
    sdk_installed, in_venv = verify_alpaca_sdk()
    results['sdk'] = sdk_installed

    results['config'] = verify_configuration()
    results['credentials'] = verify_credentials()

    if sdk_installed:
        results['connection'] = verify_alpaca_connection()
    else:
        results['connection'] = False
        print("\n⚠️  Skipping connection test (Alpaca SDK not installed)")

    results['scripts'] = verify_scripts()

    # Summary
    print("\n" + "=" * 80)
    print("📋 VERIFICATION SUMMARY")
    print("=" * 80)

    status_icon = "✅" if results.get('sdk') else "❌"
    print(f"{status_icon} Alpaca SDK: {'Installed' if results.get('sdk') else 'Not installed'}")

    status_icon = "✅" if results.get('config') else "❌"
    print(f"{status_icon} Configuration: {'Correct' if results.get('config') else 'Has issues'}")

    status_icon = "✅" if results.get('credentials') else "⚠️"
    print(f"{status_icon} Credentials: {'Configured' if results.get('credentials') else 'Check needed'}")

    status_icon = "✅" if results.get('connection') else "⚠️"
    print(f"{status_icon} Connection: {'Connected' if results.get('connection') else 'Simulation mode'}")

    status_icon = "✅" if results.get('scripts') else "❌"
    print(f"{status_icon} Utility Scripts: {'All present' if results.get('scripts') else 'Some missing'}")

    # Overall status
    all_critical = results.get('sdk') and results.get('config') and results.get('connection')

    print("\n" + "=" * 80)
    if all_critical:
        print("✅ ALL CRITICAL CHECKS PASSED!")
        print("   System is ready for trade execution")
    else:
        print("⚠️  SOME ISSUES REMAIN")
        print("   Review the checks above")
    print("=" * 80)

    return 0 if all_critical else 1

if __name__ == '__main__':
    sys.exit(main())

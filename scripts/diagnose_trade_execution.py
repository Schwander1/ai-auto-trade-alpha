#!/usr/bin/env python3
"""
Comprehensive Trade Execution Diagnosis
Checks all aspects of why trades might not be executing
"""
import json
import sys
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List

def find_config_files() -> List[Path]:
    """Find all config.json files"""
    config_paths = [
        Path("argo/config.json"),
        Path("config.json"),
        Path("/root/argo-production/config.json"),
        Path("/root/argo-production-green/config.json"),
        Path("/root/argo-production-blue/config.json"),
    ]
    return [p for p in config_paths if p.exists()]

def check_config(config_path: Path) -> Dict:
    """Check configuration settings"""
    result = {
        'path': str(config_path),
        'exists': config_path.exists(),
        'auto_execute': False,
        'force_24_7_mode': False,
        'min_confidence': None,
        'trading_engine_enabled': False,
        'errors': []
    }

    if not config_path.exists():
        result['errors'].append("Config file not found")
        return result

    try:
        with open(config_path, 'r') as f:
            config = json.load(f)

        trading = config.get('trading', {})
        result['auto_execute'] = trading.get('auto_execute', False)
        result['force_24_7_mode'] = trading.get('force_24_7_mode', False)
        result['min_confidence'] = trading.get('min_confidence', None)
        result['trading_engine_enabled'] = trading.get('trading_engine', {}).get('enabled', False)

    except Exception as e:
        result['errors'].append(f"Error reading config: {e}")

    return result

def check_alpaca_connection() -> Dict:
    """Check Alpaca API connection"""
    result = {
        'connected': False,
        'account_name': None,
        'environment': None,
        'error': None
    }

    try:
        sys.path.insert(0, str(Path(__file__).parent.parent / "argo"))
        from argo.core.paper_trading_engine import PaperTradingEngine

        engine = PaperTradingEngine()
        if engine.alpaca_enabled:
            account = engine.get_account_details()
            if account:
                result['connected'] = True
                result['account_name'] = getattr(engine, 'account_name', 'Unknown')
                result['environment'] = getattr(engine, 'environment', 'Unknown')
            else:
                result['error'] = "Alpaca enabled but account details unavailable"
        else:
            result['error'] = "Alpaca not enabled (simulation mode)"
    except ImportError as e:
        result['error'] = f"Could not import trading engine: {e}"
    except Exception as e:
        result['error'] = f"Error checking Alpaca: {e}"

    return result

def check_signal_generation_service() -> Dict:
    """Check signal generation service status"""
    result = {
        'initialized': False,
        'auto_execute': False,
        'trading_engine': False,
        'paused': False,
        'error': None
    }

    try:
        sys.path.insert(0, str(Path(__file__).parent.parent / "argo"))
        from argo.core.signal_generation_service import SignalGenerationService

        # Try to get service instance (this might not work if service isn't running)
        # Instead, check the config it would use
        config_path = Path("argo/config.json")
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
            trading = config.get('trading', {})
            result['auto_execute'] = trading.get('auto_execute', False)
            result['initialized'] = True
    except Exception as e:
        result['error'] = f"Error checking service: {e}"

    return result

def check_recent_signals_execution() -> Dict:
    """Check recent signals and execution status"""
    result = {
        'total_signals': 0,
        'executed_signals': 0,
        'high_conf_not_executed': 0,
        'execution_rate': 0.0,
        'recent_signals': []
    }

    db_paths = [
        Path("data/signals_unified.db"),
        Path("argo/data/signals.db"),
        Path("data/signals.db"),
    ]

    for db_path in db_paths:
        if db_path.exists():
            try:
                conn = sqlite3.connect(str(db_path), timeout=10.0)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                # Check table exists
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='signals'")
                if not cursor.fetchone():
                    conn.close()
                    continue

                # Get column names
                cursor.execute("PRAGMA table_info(signals)")
                columns = [row[1] for row in cursor.fetchall()]
                timestamp_col = 'timestamp' if 'timestamp' in columns else 'created_at'

                # Get last 100 signals
                query = f"""
                    SELECT signal_id, symbol, action, entry_price, confidence,
                           {timestamp_col} as timestamp, order_id, outcome
                    FROM signals
                    ORDER BY {timestamp_col} DESC
                    LIMIT 100
                """
                cursor.execute(query)

                signals = []
                for row in cursor.fetchall():
                    signal = {
                        'signal_id': row.get('signal_id'),
                        'symbol': row.get('symbol'),
                        'action': row.get('action'),
                        'entry_price': row.get('entry_price'),
                        'confidence': row.get('confidence'),
                        'order_id': row.get('order_id'),
                        'outcome': row.get('outcome')
                    }
                    signals.append(signal)

                result['total_signals'] = len(signals)
                result['executed_signals'] = sum(1 for s in signals if s.get('order_id') and s['order_id'] != 'N/A')
                result['high_conf_not_executed'] = sum(1 for s in signals
                    if s.get('confidence', 0) >= 90
                    and (not s.get('order_id') or s['order_id'] == 'N/A'))
                result['execution_rate'] = (result['executed_signals'] / result['total_signals'] * 100) if result['total_signals'] > 0 else 0
                result['recent_signals'] = signals[:10]

                conn.close()
                break
            except Exception as e:
                continue

    return result

def check_risk_validation() -> Dict:
    """Check risk validation settings"""
    result = {
        'daily_loss_limit': None,
        'max_position_size': None,
        'max_positions': None,
        'min_confidence': None,
        'trading_paused': False
    }

    config_path = Path("argo/config.json")
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            trading = config.get('trading', {})
            result['daily_loss_limit'] = trading.get('daily_loss_limit_pct', None)
            result['max_position_size'] = trading.get('max_position_size_pct', None)
            result['max_positions'] = trading.get('max_positions', None)
            result['min_confidence'] = trading.get('min_confidence', None)
        except Exception as e:
            pass

    return result

def main():
    """Run comprehensive diagnosis"""
    print("=" * 80)
    print("🔍 COMPREHENSIVE TRADE EXECUTION DIAGNOSIS")
    print("=" * 80)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()

    # 1. Check Configuration
    print("1️⃣  CONFIGURATION CHECK")
    print("-" * 80)
    config_files = find_config_files()
    if not config_files:
        print("❌ No config.json files found")
    else:
        for config_path in config_files:
            config = check_config(config_path)
            print(f"\n📄 Config: {config['path']}")
            print(f"   Auto-execute: {'✅ ENABLED' if config['auto_execute'] else '❌ DISABLED'}")
            print(f"   24/7 Mode: {'✅ ENABLED' if config['force_24_7_mode'] else '❌ DISABLED'}")
            if config['min_confidence']:
                print(f"   Min Confidence: {config['min_confidence']}%")
            if config['errors']:
                for error in config['errors']:
                    print(f"   ⚠️  Error: {error}")

    print()

    # 2. Check Alpaca Connection
    print("2️⃣  ALPACA API CONNECTION")
    print("-" * 80)
    alpaca = check_alpaca_connection()
    if alpaca['connected']:
        print(f"✅ Alpaca Connected")
        print(f"   Account: {alpaca['account_name']}")
        print(f"   Environment: {alpaca['environment']}")
    else:
        print(f"❌ Alpaca Not Connected")
        if alpaca['error']:
            print(f"   Error: {alpaca['error']}")

    print()

    # 3. Check Signal Generation Service
    print("3️⃣  SIGNAL GENERATION SERVICE")
    print("-" * 80)
    service = check_signal_generation_service()
    if service['initialized']:
        print(f"✅ Service Config Found")
        print(f"   Auto-execute: {'✅ ENABLED' if service['auto_execute'] else '❌ DISABLED'}")
    else:
        print(f"⚠️  Service status unknown")
        if service['error']:
            print(f"   Error: {service['error']}")

    print()

    # 4. Check Recent Signals Execution
    print("4️⃣  RECENT SIGNALS & EXECUTION")
    print("-" * 80)
    signals = check_recent_signals_execution()
    print(f"Total Signals (last 100): {signals['total_signals']}")
    print(f"Executed Signals: {signals['executed_signals']} ({signals['execution_rate']:.1f}%)")
    print(f"High-Confidence Not Executed: {signals['high_conf_not_executed']}")

    if signals['recent_signals']:
        print(f"\n📊 Recent Signals (first 5):")
        for sig in signals['recent_signals'][:5]:
            executed = "✅" if sig.get('order_id') and sig['order_id'] != 'N/A' else "❌"
            print(f"   {executed} {sig.get('symbol')} {sig.get('action')} @ ${sig.get('entry_price', 0):.2f} "
                  f"({sig.get('confidence', 0):.1f}%) - Order: {sig.get('order_id', 'N/A')}")

    print()

    # 5. Check Risk Validation
    print("5️⃣  RISK VALIDATION SETTINGS")
    print("-" * 80)
    risk = check_risk_validation()
    if risk['daily_loss_limit']:
        print(f"Daily Loss Limit: {risk['daily_loss_limit']}%")
    if risk['max_position_size']:
        print(f"Max Position Size: {risk['max_position_size']}%")
    if risk['max_positions']:
        print(f"Max Positions: {risk['max_positions']}")
    if risk['min_confidence']:
        print(f"Min Confidence: {risk['min_confidence']}%")

    print()

    # 6. Summary & Recommendations
    print("=" * 80)
    print("📋 DIAGNOSIS SUMMARY")
    print("=" * 80)

    issues = []
    if config_files:
        main_config = check_config(config_files[0])
        if not main_config['auto_execute']:
            issues.append("❌ auto_execute is DISABLED in config")
    else:
        issues.append("❌ No config.json file found")

    if not alpaca['connected']:
        issues.append(f"❌ Alpaca not connected: {alpaca.get('error', 'Unknown error')}")

    if signals['execution_rate'] == 0:
        issues.append(f"❌ Zero execution rate ({signals['executed_signals']}/{signals['total_signals']} executed)")

    if signals['high_conf_not_executed'] > 0:
        issues.append(f"⚠️  {signals['high_conf_not_executed']} high-confidence signals not executed")

    if issues:
        print("\n🚨 ISSUES FOUND:")
        for issue in issues:
            print(f"   {issue}")

        print("\n💡 RECOMMENDATIONS:")
        if not main_config.get('auto_execute', False) if config_files else True:
            print("   1. Enable auto_execute in config.json:")
            print("      Set trading.auto_execute = true")

        if not alpaca['connected']:
            print("   2. Fix Alpaca connection:")
            print("      - Check API keys in config.json or AWS Secrets Manager")
            print("      - Verify Alpaca account is active")
            print("      - Check network connectivity")

        if signals['execution_rate'] == 0:
            print("   3. Investigate execution pipeline:")
            print("      - Check signal distributor status")
            print("      - Verify trading executors are running")
            print("      - Review risk validation logs")
    else:
        print("\n✅ No obvious issues found")
        print("   If trades still aren't executing, check:")
        print("   - Signal distributor service status")
        print("   - Trading executor service status")
        print("   - Risk validation blocking specific trades")
        print("   - Account restrictions or trading hours")

    print()
    print("=" * 80)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

#!/usr/bin/env python3
"""
Check crypto account status and monitor for LONG signals
"""
import subprocess
import sys
import json
from datetime import datetime

PRODUCTION_SERVER = "178.156.194.174"
PRODUCTION_USER = "root"

def run_remote_command(cmd):
    """Run a command on the production server"""
    try:
        result = subprocess.run(
            f'ssh {PRODUCTION_USER}@{PRODUCTION_SERVER} "{cmd}"',
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except Exception as e:
        return None, str(e), 1

def check_account_details():
    """Check account details for crypto trading"""
    print("\n" + "="*70)
    print("💼 ACCOUNT DETAILS CHECK")
    print("="*70)
    
    # Write script to temp file and execute
    script_content = '''import sys
sys.path.insert(0, '/root/argo-production-prop-firm/argo')
from argo.core.paper_trading_engine import PaperTradingEngine
import json

try:
    engine = PaperTradingEngine('/root/argo-production-prop-firm/config.json')
    account = engine.get_account_details()
    if account:
        result = {
            'portfolio_value': account.get('portfolio_value', 0),
            'buying_power': account.get('buying_power', 0),
            'cash': account.get('cash', 0),
            'equity': account.get('equity', 0),
            'pattern_day_trader': account.get('pattern_day_trader', False),
            'trading_blocked': account.get('trading_blocked', False),
            'account_blocked': account.get('account_blocked', False),
            'day_trading_buying_power': account.get('day_trading_buying_power', 0),
            'regt_buying_power': account.get('regt_buying_power', 0),
        }
        print(json.dumps(result))
    else:
        print(json.dumps({'error': 'Could not get account details'}))
except Exception as e:
    print(json.dumps({'error': str(e)}))
'''
    
    import tempfile
    import os
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(script_content)
        temp_script = f.name
    
    try:
        import subprocess
        copy_cmd = f'scp {temp_script} {PRODUCTION_USER}@{PRODUCTION_SERVER}:/tmp/check_account.py'
        subprocess.run(copy_cmd, shell=True, capture_output=True, check=True)
        stdout, stderr, code = run_remote_command('python3 /tmp/check_account.py')
    finally:
        os.unlink(temp_script)
    
    if code == 0 and stdout:
        try:
            account = json.loads(stdout)
            if 'error' in account:
                print(f"❌ Error: {account['error']}")
                return None
            
            print(f"\n💰 Portfolio Value: ${account['portfolio_value']:,.2f}")
            print(f"💵 Buying Power: ${account['buying_power']:,.2f}")
            print(f"💵 Cash: ${account['cash']:,.2f}")
            print(f"📊 Equity: ${account['equity']:,.2f}")
            print(f"📈 Day Trading Buying Power: ${account['day_trading_buying_power']:,.2f}")
            print(f"📈 RegT Buying Power: ${account['regt_buying_power']:,.2f}")
            print(f"\n🚦 Account Status:")
            print(f"   Pattern Day Trader: {account['pattern_day_trader']}")
            print(f"   Trading Blocked: {account['trading_blocked']}")
            print(f"   Account Blocked: {account['account_blocked']}")
            
            return account
        except json.JSONDecodeError:
            print(f"❌ Could not parse account details: {stdout}")
            return None
    else:
        print(f"❌ Error getting account details: {stderr}")
        return None

def check_for_long_crypto_signals():
    """Check database for LONG crypto signals"""
    print("\n" + "="*70)
    print("🔍 CHECKING FOR LONG CRYPTO SIGNALS")
    print("="*70)
    
    script_content = '''import sqlite3
import json
import sys
from datetime import datetime, timedelta

db_path = '/root/argo-production-prop-firm/data/signals.db'

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%signal%'")
    tables = cursor.fetchall()
    if not tables:
        print(json.dumps({'error': 'No signal tables found'}))
        sys.exit(1)
    
    table_name = tables[0][0]
    
    # Get LONG crypto signals (BUY)
    cursor.execute(f"""
        SELECT signal_id, symbol, action, entry_price, confidence, timestamp, order_id
        FROM {table_name}
        WHERE (symbol LIKE 'BTC-%' OR symbol LIKE 'ETH-%')
        AND (action = 'LONG' OR action = 'BUY')
        ORDER BY timestamp DESC
        LIMIT 10
    """)
    long_signals = cursor.fetchall()
    
    # Get recent LONG signals (last 24 hours)
    cutoff = (datetime.now() - timedelta(hours=24)).isoformat()
    cursor.execute(f"""
        SELECT COUNT(*) FROM {table_name}
        WHERE (symbol LIKE 'BTC-%' OR symbol LIKE 'ETH-%')
        AND (action = 'LONG' OR action = 'BUY')
        AND timestamp > ?
    """, (cutoff,))
    recent_long = cursor.fetchone()[0]
    
    result = {
        'long_signals_count': len(long_signals),
        'recent_24h': recent_long,
        'long_signals': [
            {
                'signal_id': row[0],
                'symbol': row[1],
                'action': row[2],
                'entry_price': row[3],
                'confidence': row[4],
                'timestamp': row[5],
                'order_id': row[6] or 'None'
            }
            for row in long_signals
        ]
    }
    
    print(json.dumps(result, indent=2))
    conn.close()
except Exception as e:
    print(json.dumps({'error': str(e)}))
'''
    
    import tempfile
    import os
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(script_content)
        temp_script = f.name
    
    try:
        import subprocess
        copy_cmd = f'scp {temp_script} {PRODUCTION_USER}@{PRODUCTION_SERVER}:/tmp/check_long_signals.py'
        subprocess.run(copy_cmd, shell=True, capture_output=True, check=True)
        stdout, stderr, code = run_remote_command('python3 /tmp/check_long_signals.py')
    finally:
        os.unlink(temp_script)
    
    if code == 0 and stdout:
        try:
            result = json.loads(stdout)
            if 'error' in result:
                print(f"❌ Error: {result['error']}")
                return None
            
            print(f"\n📊 LONG Crypto Signals Found: {result['long_signals_count']}")
            print(f"📅 LONG Signals (Last 24h): {result['recent_24h']}")
            
            if result['long_signals']:
                print("\n✅ LONG Crypto Signals (can execute with USD):")
                print("-" * 70)
                for sig in result['long_signals']:
                    status = "✅ EXECUTED" if sig['order_id'] != 'None' else "⏭️  NOT EXECUTED"
                    print(f"  {status} {sig['symbol']}: {sig['action']} @ ${sig['entry_price']:.2f} ({sig['confidence']:.1f}%)")
                    print(f"     Timestamp: {sig['timestamp']}")
            else:
                print("\n⚠️  No LONG crypto signals found")
                print("   Current signals are SHORT (SELL) which require crypto assets")
            
            return result
        except json.JSONDecodeError:
            print(f"❌ Could not parse results: {stdout}")
            return None
    else:
        print(f"❌ Error checking signals: {stderr}")
        return None

def check_recent_signal_actions():
    """Check recent signal actions to see if any are LONG"""
    print("\n" + "="*70)
    print("📈 RECENT CRYPTO SIGNAL ACTIONS")
    print("="*70)
    
    stdout, stderr, code = run_remote_command(
        "journalctl -u argo-prop-firm-executor.service --since '30 minutes ago' | "
        "grep -E 'BTC-USD|ETH-USD' | grep -E 'LONG|BUY|SHORT|SELL' | tail -10"
    )
    
    if stdout:
        print("\nRecent signal activity:")
        print(stdout)
    else:
        print("\n⚠️  No recent signal activity found in logs")

def main():
    """Main execution"""
    print("="*70)
    print("🔍 CRYPTO ACCOUNT STATUS & LONG SIGNAL CHECK")
    print("="*70)
    print(f"Server: {PRODUCTION_SERVER}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check account
    account = check_account_details()
    
    # Check for LONG signals
    long_signals = check_for_long_crypto_signals()
    
    # Check recent activity
    check_recent_signal_actions()
    
    # Summary
    print("\n" + "="*70)
    print("📊 SUMMARY")
    print("="*70)
    
    if account:
        print(f"✅ Account Status: Portfolio ${account['portfolio_value']:,.2f}, Buying Power ${account['buying_power']:,.2f}")
        if account['trading_blocked']:
            print("⚠️  WARNING: Trading is blocked!")
        if account['account_blocked']:
            print("⚠️  WARNING: Account is blocked!")
    
    if long_signals:
        if long_signals['long_signals_count'] > 0:
            print(f"✅ Found {long_signals['long_signals_count']} LONG crypto signals")
            print("   These can execute using USD (no crypto assets needed)")
        else:
            print("⚠️  No LONG crypto signals found")
            print("   Current signals are SHORT (SELL) - need crypto assets or margin")
    
    print("\n💡 Recommendation:")
    print("   - Monitor for LONG (BUY) signals - these will execute with USD")
    print("   - Or enable margin/shorting on account for SHORT positions")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()


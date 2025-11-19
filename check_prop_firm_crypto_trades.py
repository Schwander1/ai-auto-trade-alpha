#!/usr/bin/env python3
"""
Check if any crypto trading has happened with the prop firm on production
"""
import subprocess
import sys
from datetime import datetime, timedelta

PRODUCTION_SERVER = "178.156.194.174"
PRODUCTION_USER = "root"
PROP_FIRM_DB = "/root/argo-production-prop-firm/data/signals.db"
PROP_FIRM_LOG = "/tmp/argo-prop-firm.log"
PROP_FIRM_SERVICE = "argo-trading-prop-firm.service"

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
    except subprocess.TimeoutExpired:
        return None, "Command timed out", 1
    except Exception as e:
        return None, str(e), 1

def check_service_status():
    """Check if prop firm service is running"""
    print("\n" + "="*70)
    print("🔍 PROP FIRM SERVICE STATUS")
    print("="*70)
    
    stdout, stderr, code = run_remote_command(f"systemctl is-active {PROP_FIRM_SERVICE} 2>/dev/null || echo 'inactive'")
    if stdout == "active":
        print("✅ Prop firm service is ACTIVE")
    else:
        print(f"⚠️  Prop firm service is {stdout.upper()}")
        # Try alternative service names
        alt_services = ["argo-prop-firm-executor.service", "argo-trading-prop-firm.service"]
        for alt in alt_services:
            stdout2, _, _ = run_remote_command(f"systemctl is-active {alt} 2>/dev/null || echo 'inactive'")
            if stdout2 == "active":
                print(f"✅ Found active service: {alt}")
                return alt
    return PROP_FIRM_SERVICE

def check_database_for_crypto_trades():
    """Check database for crypto trades"""
    print("\n" + "="*70)
    print("📊 CHECKING DATABASE FOR CRYPTO TRADES")
    print("="*70)
    
    # Check if database exists
    stdout, stderr, code = run_remote_command(f"test -f {PROP_FIRM_DB} && echo 'exists' || echo 'not_found'")
    if stdout != "exists":
        print(f"⚠️  Database not found at: {PROP_FIRM_DB}")
        # Try alternative paths
        alt_paths = [
            "/root/argo-production-prop-firm/data/signals_unified.db",
            "/root/argo-production-green/data/signals.db",
            "/root/argo-production/data/signals.db"
        ]
        for alt_path in alt_paths:
            stdout2, _, _ = run_remote_command(f"test -f {alt_path} && echo 'exists' || echo 'not_found'")
            if stdout2 == "exists":
                print(f"✅ Found database at: {alt_path}")
                return check_database_content(alt_path)
        return None
    
    return check_database_content(PROP_FIRM_DB)

def check_database_content(db_path):
    """Query database for crypto trades"""
    print(f"\n📂 Checking database: {db_path}")
    
    # Create a temporary Python script on the server
    script_content = '''import sqlite3
import json
import sys
from datetime import datetime, timedelta

db_path = sys.argv[1]

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get table name
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%signal%'")
    tables = cursor.fetchall()
    if not tables:
        print(json.dumps({'error': 'No signal tables found'}))
        sys.exit(1)
    
    table_name = tables[0][0]
    
    # Check for crypto symbols (BTC-USD, ETH-USD, etc.)
    cursor.execute(f"""
        SELECT COUNT(*) FROM {table_name}
        WHERE (symbol LIKE 'BTC-%' OR symbol LIKE 'ETH-%' OR symbol LIKE '%USD' OR asset_type = 'crypto')
    """)
    crypto_count = cursor.fetchone()[0]
    
    # Get crypto signals with order_ids (executed trades)
    cursor.execute(f"""
        SELECT signal_id, symbol, action, entry_price, confidence, timestamp, order_id, asset_type
        FROM {table_name}
        WHERE (symbol LIKE 'BTC-%' OR symbol LIKE 'ETH-%' OR symbol LIKE '%USD' OR asset_type = 'crypto')
        AND order_id IS NOT NULL AND order_id != ''
        ORDER BY timestamp DESC
        LIMIT 20
    """)
    executed_crypto = cursor.fetchall()
    
    # Get all crypto signals (even without orders)
    cursor.execute(f"""
        SELECT signal_id, symbol, action, entry_price, confidence, timestamp, order_id, asset_type
        FROM {table_name}
        WHERE (symbol LIKE 'BTC-%' OR symbol LIKE 'ETH-%' OR symbol LIKE '%USD' OR asset_type = 'crypto')
        ORDER BY timestamp DESC
        LIMIT 10
    """)
    all_crypto = cursor.fetchall()
    
    # Get recent crypto signals (last 24 hours)
    cutoff = (datetime.now() - timedelta(hours=24)).isoformat()
    cursor.execute(f"""
        SELECT COUNT(*) FROM {table_name}
        WHERE (symbol LIKE 'BTC-%' OR symbol LIKE 'ETH-%' OR symbol LIKE '%USD' OR asset_type = 'crypto')
        AND timestamp > ?
    """, (cutoff,))
    recent_24h = cursor.fetchone()[0]
    
    result = {
        'crypto_signals_total': crypto_count,
        'executed_crypto_trades': len(executed_crypto),
        'recent_24h': recent_24h,
        'executed_trades': [
            {
                'signal_id': row[0],
                'symbol': row[1],
                'action': row[2],
                'entry_price': row[3],
                'confidence': row[4],
                'timestamp': row[5],
                'order_id': row[6],
                'asset_type': row[7]
            }
            for row in executed_crypto
        ],
        'all_crypto_signals': [
            {
                'signal_id': row[0],
                'symbol': row[1],
                'action': row[2],
                'entry_price': row[3],
                'confidence': row[4],
                'timestamp': row[5],
                'order_id': row[6] or 'None',
                'asset_type': row[7]
            }
            for row in all_crypto
        ]
    }
    
    print(json.dumps(result, indent=2))
    conn.close()
except Exception as e:
    print(json.dumps({'error': str(e)}))
'''
    
    # Write script to temp file locally, then copy to server and execute
    import tempfile
    import os
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(script_content)
        temp_script = f.name
    
    try:
        # Copy script to server
        import subprocess
        copy_cmd = f'scp {temp_script} {PRODUCTION_USER}@{PRODUCTION_SERVER}:/tmp/check_crypto_db.py'
        subprocess.run(copy_cmd, shell=True, capture_output=True, check=True)
        
        # Execute on server
        stdout, stderr, code = run_remote_command(f'python3 /tmp/check_crypto_db.py "{db_path}"')
    finally:
        os.unlink(temp_script)
    
    if code != 0 or stderr:
        print(f"❌ Error querying database: {stderr}")
        return None
    
    try:
        import json
        result = json.loads(stdout)
        
        if 'error' in result:
            print(f"❌ Database error: {result['error']}")
            return None
        
        print(f"\n📈 Crypto Signals Found: {result['crypto_signals_total']}")
        print(f"✅ Executed Crypto Trades: {result['executed_crypto_trades']}")
        print(f"📅 Crypto Signals (Last 24h): {result['recent_24h']}")
        
        if result['executed_crypto_trades'] > 0:
            print("\n🎯 EXECUTED CRYPTO TRADES:")
            print("-" * 70)
            for trade in result['executed_trades']:
                print(f"  ✅ {trade['symbol']}: {trade['action']} @ ${trade['entry_price']:.2f}")
                print(f"     Confidence: {trade['confidence']:.1f}% | Order ID: {trade['order_id']}")
                print(f"     Timestamp: {trade['timestamp']}")
                print()
        else:
            print("\n⚠️  No executed crypto trades found in database")
        
        if result['all_crypto_signals']:
            print("\n📊 Recent Crypto Signals (including non-executed):")
            print("-" * 70)
            for sig in result['all_crypto_signals'][:5]:
                status = "✅ EXECUTED" if sig['order_id'] != 'None' else "⏭️  NOT EXECUTED"
                print(f"  {status} {sig['symbol']}: {sig['action']} @ ${sig['entry_price']:.2f} ({sig['confidence']:.1f}%)")
        
        return result
    except json.JSONDecodeError:
        print(f"❌ Could not parse database results")
        print(f"Output: {stdout[:500]}")
        return None

def check_logs_for_crypto_trades():
    """Check logs for crypto trading activity"""
    print("\n" + "="*70)
    print("📋 CHECKING LOGS FOR CRYPTO TRADING")
    print("="*70)
    
    # Check service logs
    log_commands = [
        f"journalctl -u {PROP_FIRM_SERVICE} --no-pager -n 500 | grep -E 'BTC-USD|ETH-USD|Converted symbol|Crypto|🪙' | tail -20",
        f"tail -n 500 {PROP_FIRM_LOG} 2>/dev/null | grep -E 'BTC-USD|ETH-USD|Converted symbol|Crypto|🪙' | tail -20",
        f"journalctl -u argo-prop-firm-executor.service --no-pager -n 500 | grep -E 'BTC-USD|ETH-USD|Converted symbol|Crypto|🪙' | tail -20",
    ]
    
    found_activity = False
    for cmd in log_commands:
        stdout, stderr, code = run_remote_command(cmd)
        if stdout and stdout.strip():
            print(f"\n✅ Found crypto activity in logs:")
            print("-" * 70)
            print(stdout)
            found_activity = True
            break
    
    if not found_activity:
        print("⚠️  No crypto trading activity found in recent logs")
    
    return found_activity

def check_alpaca_positions():
    """Check Alpaca API for crypto positions"""
    print("\n" + "="*70)
    print("🔌 CHECKING ALPACA FOR CRYPTO POSITIONS")
    print("="*70)
    
    # Check if there's an API endpoint to check positions
    stdout, stderr, code = run_remote_command(
        "curl -s http://localhost:8001/api/v1/trading/positions 2>/dev/null || curl -s http://localhost:8001/api/v1/positions 2>/dev/null || echo 'endpoint_not_found'"
    )
    
    if stdout and stdout != "endpoint_not_found" and "error" not in stdout.lower():
        try:
            import json
            positions = json.loads(stdout)
            if isinstance(positions, list) and len(positions) > 0:
                crypto_positions = [p for p in positions if 'BTC' in p.get('symbol', '') or 'ETH' in p.get('symbol', '')]
                if crypto_positions:
                    print(f"✅ Found {len(crypto_positions)} crypto positions:")
                    for pos in crypto_positions:
                        print(f"  {pos.get('symbol')}: {pos.get('qty')} @ ${pos.get('avg_entry_price', 0):.2f}")
                    return True
        except:
            pass
    
    print("⚠️  Could not check Alpaca positions via API")
    return False

def main():
    """Main execution"""
    print("="*70)
    print("🔍 PROP FIRM CRYPTO TRADING CHECK")
    print("="*70)
    print(f"Server: {PRODUCTION_SERVER}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check service
    service_name = check_service_status()
    
    # Check database
    db_result = check_database_for_crypto_trades()
    
    # Check logs
    log_result = check_logs_for_crypto_trades()
    
    # Check Alpaca positions
    position_result = check_alpaca_positions()
    
    # Summary
    print("\n" + "="*70)
    print("📊 SUMMARY")
    print("="*70)
    
    if db_result:
        executed = db_result.get('executed_crypto_trades', 0)
        total = db_result.get('crypto_signals_total', 0)
        
        if executed > 0:
            print(f"✅ YES - {executed} crypto trade(s) have been executed with the prop firm!")
            print(f"   Total crypto signals: {total}")
        elif total > 0:
            print(f"⚠️  {total} crypto signal(s) generated, but NONE have been executed yet")
        else:
            print("❌ NO crypto trading has happened - no crypto signals found in database")
    else:
        print("⚠️  Could not determine crypto trading status from database")
    
    if log_result:
        print("✅ Crypto activity detected in logs")
    
    if position_result:
        print("✅ Active crypto positions found in Alpaca")
    
    print("="*70 + "\n")

if __name__ == "__main__":
    main()


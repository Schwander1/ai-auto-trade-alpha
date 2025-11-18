#!/usr/bin/env python3
"""
Check signal counts on production server
"""
import subprocess
import sys

PROD_SERVER = "root@178.156.194.174"

def run_remote_command(cmd):
    """Run command on production server"""
    try:
        result = subprocess.run(
            ['ssh', PROD_SERVER, cmd],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return None, "Timeout", 1
    except Exception as e:
        return None, str(e), 1

def check_production_signals():
    """Check signal counts on production"""
    print('='*70)
    print('📊 PRODUCTION SIGNAL STORAGE COUNT')
    print('='*70)
    print(f'Connecting to: {PROD_SERVER}\n')
    
    # Create a temporary script file on the server
    script_content = '''import sqlite3
from pathlib import Path

databases = [
    ("/root/argo-production-green/data/signals.db", "Argo Trading Service (Green)"),
    ("/root/argo-production-prop-firm/data/signals.db", "Prop Firm Trading Service"),
    ("/root/argo-production/data/signals.db", "Production (Legacy)"),
    ("/root/argo-production-blue/data/signals.db", "Argo Trading Service (Blue)"),
]

print("="*70)
print("📊 PRODUCTION SIGNAL COUNT")
print("="*70)

total_all = 0
found_dbs = []

for db_path, name in databases:
    db = Path(db_path)
    if not db.exists():
        print(f"\\n⚠️  {name}")
        print(f"   Database not found: {db_path}")
        continue
    
    try:
        conn = sqlite3.connect(str(db))
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM signals")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM signals WHERE order_id IS NOT NULL AND order_id != ''")
        executed = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM signals WHERE created_at >= datetime('now', '-24 hours')")
        recent_24h = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM signals WHERE created_at >= datetime('now', '-1 hour')")
        recent_1h = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM signals WHERE created_at >= datetime('now', '-7 days')")
        recent_7d = cursor.fetchone()[0]
        
        size_mb = db.stat().st_size / (1024 * 1024)
        
        cursor.execute("SELECT symbol, action, confidence, created_at FROM signals ORDER BY created_at DESC LIMIT 1")
        latest = cursor.fetchone()
        
        cursor.execute("SELECT created_at FROM signals ORDER BY created_at ASC LIMIT 1")
        oldest = cursor.fetchone()
        
        cursor.execute("SELECT symbol, COUNT(*) as count FROM signals GROUP BY symbol ORDER BY count DESC LIMIT 5")
        top_symbols = cursor.fetchall()
        
        cursor.execute("SELECT outcome, COUNT(*) as count FROM signals WHERE outcome IS NOT NULL GROUP BY outcome")
        outcomes = cursor.fetchall()
        
        conn.close()
        
        print(f"\\n📁 {name}")
        print(f"   Path: {db_path}")
        print(f"   Total Signals: {total:,}")
        print(f"   Executed Trades: {executed:,}")
        print(f"   Signals (last 7 days): {recent_7d:,}")
        print(f"   Signals (last 24h): {recent_24h:,}")
        print(f"   Signals (last 1h): {recent_1h:,}")
        print(f"   Database Size: {size_mb:.2f} MB")
        
        if oldest:
            print(f"   Oldest Signal: {oldest[0]}")
        if latest:
            symbol, action, confidence, created_at = latest
            print(f"   Latest Signal: {symbol} {action} @ {confidence:.1f}% - {created_at}")
        
        if top_symbols:
            print(f"   Top Symbols:")
            for symbol, count in top_symbols:
                print(f"      {symbol}: {count:,} signals")
        
        if outcomes:
            print(f"   Outcomes:")
            for outcome, count in outcomes:
                print(f"      {outcome}: {count:,}")
        
        total_all += total
        found_dbs.append((name, total, executed, recent_24h, recent_1h, size_mb))
        
    except Exception as e:
        print(f"\\n❌ {name}: Error - {e}")
        import traceback
        traceback.print_exc()

print(f"\\n{'='*70}")
print(f"📊 SUMMARY")
print(f"{'='*70}")
print(f"Total Signals Across All Production Databases: {total_all:,}")
print(f"Databases Found: {len(found_dbs)}")

if found_dbs:
    print(f"\\n📋 Breakdown:")
    for name, total, executed, recent_24h, recent_1h, size_mb in found_dbs:
        print(f"   {name}: {total:,} signals ({size_mb:.2f} MB)")
        print(f"      - Executed: {executed:,}")
        print(f"      - Last 24h: {recent_24h:,}")
        print(f"      - Last 1h: {recent_1h:,}")
'''
    
    # Write script to temp file and execute
    cmd = f'''cat > /tmp/check_signals.py << 'EOFPYTHON'
{script_content}
EOFPYTHON
python3 /tmp/check_signals.py
rm /tmp/check_signals.py
'''
    
    stdout, stderr, returncode = run_remote_command(cmd)
    
    if returncode == 0:
        print(stdout)
        if stderr:
            print("Warnings/Errors:", stderr, file=sys.stderr)
    else:
        print(f"❌ Error connecting to production server")
        print(f"Return code: {returncode}")
        if stderr:
            print(f"Error: {stderr}")
        if stdout:
            print(f"Output: {stdout}")
        sys.exit(1)

if __name__ == "__main__":
    check_production_signals()


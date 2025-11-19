#!/usr/bin/env python3
"""
Comprehensive production signal generation check
"""
import subprocess
import sys
import json
from datetime import datetime

PROD_SERVER = "root@178.156.194.174"

def run_remote_command(cmd):
    """Run command on production server"""
    try:
        result = subprocess.run(
            ['ssh', PROD_SERVER, cmd],
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return None, "Timeout", 1
    except Exception as e:
        return None, str(e), 1

def check_service_health(port, service_name):
    """Check service health endpoint"""
    cmd = f'''curl -s http://localhost:{port}/health 2>/dev/null | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    sg = data.get('signal_generation', {{}})
    print(json.dumps({{
        'status': data.get('status', 'unknown'),
        'signal_status': sg.get('status', 'unknown'),
        'background_task_running': sg.get('background_task_running', False),
        'background_task_error': sg.get('background_task_error', None),
        'last_cycle_time': sg.get('last_cycle_time', None),
        'symbols_processed': sg.get('symbols_processed', []),
        'signals_generated': sg.get('signals_generated', 0)
    }}, indent=2))
except Exception as e:
    print(json.dumps({{'error': str(e)}}, indent=2))
"'''
    
    stdout, stderr, returncode = run_remote_command(cmd)
    if returncode == 0 and stdout:
        try:
            return json.loads(stdout)
        except:
            return {'error': 'Failed to parse health response'}
    return {'error': stderr or 'Failed to connect'}

def check_recent_logs(service_dir, service_name):
    """Check recent logs for signal generation activity"""
    log_path = f"{service_dir}/logs/service.log"
    
    # Create a script to analyze logs
    script = f'''import sys
lines = sys.stdin.readlines()
signal_cycles = []
errors = []
warnings = []

for line in lines:
    line_lower = line.lower()
    if 'signal_generation' in line_lower or '_run_signal_generation_cycle' in line_lower:
        signal_cycles.append(line.strip())
    if 'error' in line_lower or 'exception' in line_lower:
        errors.append(line.strip()[-200:])
    if 'warning' in line_lower or 'warn' in line_lower:
        warnings.append(line.strip()[-200:])

print(f'Signal cycles found: {{len(signal_cycles)}}')
print(f'Errors found: {{len(errors)}}')
print(f'Warnings found: {{len(warnings)}}')

if signal_cycles:
    print('\\nLast 3 signal cycles:')
    for cycle_line in signal_cycles[-3:]:
        print(f'  {{cycle_line[-150:]}}')

if errors:
    print('\\nLast 3 errors:')
    for err_line in errors[-3:]:
        print(f'  {{err_line}}')
'''
    
    cmd = f'''cat > /tmp/check_logs.py << 'EOFPYTHON'
{script}
EOFPYTHON
tail -100 {log_path} 2>/dev/null | python3 /tmp/check_logs.py
rm /tmp/check_logs.py
'''
    
    stdout, stderr, returncode = run_remote_command(cmd)
    return stdout or stderr or "No log data available"

def check_recent_signals(db_path, service_name):
    """Check recent signals in database"""
    script = f'''import sqlite3
from pathlib import Path

db = Path('{db_path}')
if not db.exists():
    print('Database not found')
    exit(1)

try:
    conn = sqlite3.connect(str(db))
    cursor = conn.cursor()
    
    # Check if unified database (has timestamp column) or old format (has created_at)
    cursor.execute("PRAGMA table_info(signals)")
    columns = [row[1] for row in cursor.fetchall()]
    time_col = 'timestamp' if 'timestamp' in columns else 'created_at'
    
    # Last hour
    query = "SELECT COUNT(*) FROM signals WHERE " + time_col + " >= datetime('now', '-1 hour')"
    cursor.execute(query)
    last_hour = cursor.fetchone()[0]
    
    # Last 24 hours
    query = "SELECT COUNT(*) FROM signals WHERE " + time_col + " >= datetime('now', '-24 hours')"
    cursor.execute(query)
    last_24h = cursor.fetchone()[0]
    
    # Latest signal
    query = "SELECT symbol, action, confidence, " + time_col + " FROM signals ORDER BY " + time_col + " DESC LIMIT 1"
    cursor.execute(query)
    latest = cursor.fetchone()
    
    # Signals in last 10 minutes
    query = "SELECT COUNT(*) FROM signals WHERE " + time_col + " >= datetime('now', '-10 minutes')"
    cursor.execute(query)
    last_10min = cursor.fetchone()[0]
    
    print(f'Signals (last 10 min): {{last_10min}}')
    print(f'Signals (last 1 hour): {{last_hour}}')
    print(f'Signals (last 24 hours): {{last_24h}}')
    
    if latest:
        symbol, action, confidence, created_at = latest
        print(f'Latest signal: {{symbol}} {{action}} @ {{confidence:.1f}}% - {{created_at}}')
    else:
        print('No signals found')
    
    conn.close()
except Exception as e:
    print(f'Error: {{e}}')
    import traceback
    traceback.print_exc()
'''
    
    cmd = f'''cat > /tmp/check_signals_db.py << 'EOFPYTHON'
{script}
EOFPYTHON
python3 /tmp/check_signals_db.py
rm /tmp/check_signals_db.py
'''
    
    stdout, stderr, returncode = run_remote_command(cmd)
    return stdout or stderr or "Failed to check database"

def main():
    print('='*80)
    print('🔍 PRODUCTION SIGNAL GENERATION STATUS CHECK')
    print('='*80)
    print('📋 Architecture: Unified Signal Generator (v3.0)')
    print('   - Port 7999: Unified Signal Generator (generates all signals)')
    print('   - Port 8000: Argo Trading Executor (executes trades only)')
    print('   - Port 8001: Prop Firm Executor (executes trades only)')
    print('='*80)
    print(f'Server: {PROD_SERVER}\n')
    
    # Unified Signal Generator (the one that actually generates signals)
    unified_service = {
        'name': 'Unified Signal Generator',
        'port': 7999,
        'dir': '/root/argo-production-unified',
        'db': '/root/argo-production-unified/data/signals_unified.db'
    }
    
    # Executors (these do NOT generate signals, they only execute trades)
    services = [
        {
            'name': 'Argo Trading Executor',
            'port': 8000,
            'dir': '/root/argo-production-green',
            'db': '/root/argo-production-unified/data/signals_unified.db',  # Uses unified DB
            'is_executor': True
        },
        {
            'name': 'Prop Firm Executor',
            'port': 8001,
            'dir': '/root/argo-production-prop-firm',
            'db': '/root/argo-production-unified/data/signals_unified.db',  # Uses unified DB
            'is_executor': True
        }
    ]
    
    # Check unified signal generator first
    print('='*80)
    print(f"📊 {unified_service['name']} (Port {unified_service['port']})")
    print('='*80)
    print("⚠️  This is the service that generates signals - executors do NOT generate signals")
    print()
    
    # Check health endpoint
    print(f"\n🌐 Service Health (Port {unified_service['port']}):")
    health = check_service_health(unified_service['port'], unified_service['name'])
    if 'error' in health:
        print(f"  ❌ Error: {health['error']}")
    else:
        status = health.get('status', 'unknown')
        signal_status = health.get('signal_status', 'unknown')
        bg_task = health.get('background_task_running', False)
        bg_error = health.get('background_task_error')
        last_cycle = health.get('last_cycle_time')
        symbols = health.get('symbols_processed', [])
        signals_gen = health.get('signals_generated', 0)
        
        print(f"  Service Status: {'✅' if status == 'healthy' else '⚠️'} {status}")
        print(f"  Signal Generation: {'✅' if signal_status == 'running' else '⚠️'} {signal_status}")
        print(f"  Background Task: {'✅ RUNNING' if bg_task else '❌ NOT RUNNING'}")
        if bg_error:
            print(f"  ⚠️  Background Task Error: {bg_error}")
        if last_cycle:
            print(f"  Last Cycle: {last_cycle}")
        if symbols:
            print(f"  Symbols Processed: {', '.join(symbols)}")
        if signals_gen:
            print(f"  Signals Generated (this cycle): {signals_gen}")
    
    # Check recent signals from unified database
    print(f"\n📈 Recent Signals (Unified Database):")
    signals_info = check_recent_signals(unified_service['db'], unified_service['name'])
    for line in signals_info.split('\n'):
        if line.strip():
            print(f"  {line}")
    
    # Check logs
    print(f"\n📋 Recent Log Activity:")
    log_info = check_recent_logs(unified_service['dir'], unified_service['name'])
    for line in log_info.split('\n'):
        if line.strip():
            print(f"  {line}")
    
    print()
    print('='*80)
    print('📊 TRADING EXECUTORS (Do NOT generate signals - only execute trades)')
    print('='*80)
    print()
    
    for service in services:
        print('='*80)
        print(f"📊 {service['name']} (Port {service['port']})")
        print('='*80)
        print("ℹ️  This is an EXECUTOR - it receives signals from the Unified Generator and executes trades")
        print()
        
        # Check health endpoint
        print(f"\n🌐 Service Health (Port {service['port']}):")
        health = check_service_health(service['port'], service['name'])
        if 'error' in health:
            print(f"  ❌ Error: {health['error']}")
        else:
            status = health.get('status', 'unknown')
            print(f"  Service Status: {'✅' if status == 'healthy' else '⚠️'} {status}")
            # Executors don't have signal generation status - they only execute trades
            print(f"  Role: Trading Executor (receives signals from Unified Generator on port 7999)")
        
        # Executors use the unified database, so we can check signals they've executed
        print(f"\n📈 Signals in Unified Database (available to this executor):")
        signals_info = check_recent_signals(service['db'], service['name'])
        for line in signals_info.split('\n'):
            if line.strip():
                print(f"  {line}")
        
        # Check logs for trade execution activity
        print(f"\n📋 Recent Log Activity (Trade Execution):")
        log_info = check_recent_logs(service['dir'], service['name'])
        for line in log_info.split('\n'):
            if line.strip():
                print(f"  {line}")
        
        print()
    
    # Summary
    print('='*80)
    print('📊 SUMMARY')
    print('='*80)
    print('\n✅ Unified Signal Generator (Port 7999):')
    print('   - Generates ALL signals for the system')
    print('   - Stores signals in unified database')
    print('   - Distributes signals to executors')
    print('\n✅ Trading Executors (Ports 8000, 8001):')
    print('   - Receive signals from Unified Generator')
    print('   - Execute trades based on signals')
    print('   - Do NOT generate signals themselves')
    print('\n💡 To monitor signal generation in real-time:')
    print('  ssh root@178.156.194.174 "journalctl -u argo-signal-generator.service -f"')
    print('\n💡 To check all service status:')
    print('  ssh root@178.156.194.174 "systemctl status argo-signal-generator.service argo-trading-executor.service argo-prop-firm-executor.service"')
    print('\n💡 To check unified database:')
    print('  ssh root@178.156.194.174')
    print('  sqlite3 /root/argo-production-unified/data/signals_unified.db')
    print('  "SELECT COUNT(*) FROM signals WHERE timestamp >= datetime(\'now\', \'-1 hour\');"')

if __name__ == "__main__":
    main()


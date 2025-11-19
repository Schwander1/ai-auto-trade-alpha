#!/usr/bin/env python3
"""
Check overnight signal generation performance
"""
import subprocess
import sys
from datetime import datetime, timedelta

PROD_SERVER = "root@178.156.194.174"
DB_PATH = "/root/argo-production-unified/data/signals_unified.db"

def run_remote_command(cmd):
    """Run command on production server"""
    try:
        result = subprocess.run(
            ['ssh', PROD_SERVER, cmd],
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return None, "Timeout", 1
    except Exception as e:
        return None, str(e), 1

def get_signal_count(hours_ago):
    """Get signal count for a specific time period"""
    script = f'''import sqlite3
from datetime import datetime, timedelta

try:
    conn = sqlite3.connect('{DB_PATH}')
    cursor = conn.cursor()
    
    cutoff = (datetime.now() - timedelta(hours={hours_ago})).isoformat()
    cursor.execute("SELECT COUNT(*) FROM signals WHERE timestamp >= ?", (cutoff,))
    count = cursor.fetchone()[0]
    
    # Get latest signal time
    cursor.execute("SELECT timestamp FROM signals ORDER BY timestamp DESC LIMIT 1")
    latest = cursor.fetchone()
    latest_time = latest[0] if latest else None
    
    # Get earliest signal in period
    cursor.execute("SELECT timestamp FROM signals WHERE timestamp >= ? ORDER BY timestamp ASC LIMIT 1", (cutoff,))
    earliest = cursor.fetchone()
    earliest_time = earliest[0] if earliest else None
    
    print(f"{{count}}|{{latest_time}}|{{earliest_time}}")
    conn.close()
except Exception as e:
    print(f"ERROR: {{e}}")
'''
    
    cmd = f'''cat > /tmp/check_overnight.py << 'EOFPYTHON'
{script}
EOFPYTHON
python3 /tmp/check_overnight.py
rm /tmp/check_overnight.py
'''
    
    stdout, stderr, returncode = run_remote_command(cmd)
    if returncode == 0 and stdout and not stdout.startswith("ERROR"):
        parts = stdout.split('|')
        if len(parts) == 3:
            return int(parts[0]), parts[1], parts[2]
    return None, None, None

def get_hourly_breakdown():
    """Get hourly signal counts for last 12 hours"""
    script = f'''import sqlite3
from datetime import datetime, timedelta

try:
    conn = sqlite3.connect('{DB_PATH}')
    cursor = conn.cursor()
    
    # Get signals for last 12 hours, grouped by hour
    hours = []
    for i in range(12):
        hour_start = (datetime.now() - timedelta(hours=i+1)).isoformat()
        hour_end = (datetime.now() - timedelta(hours=i)).isoformat()
        cursor.execute("""
            SELECT COUNT(*) FROM signals 
            WHERE timestamp >= ? AND timestamp < ?
        """, (hour_start, hour_end))
        count = cursor.fetchone()[0]
        hours.append((i, count, hour_start[:19]))
    
    for hour, count, time_str in reversed(hours):
        print(f"{{hour}}|{{count}}|{{time_str}}")
    
    conn.close()
except Exception as e:
    print(f"ERROR: {{e}}")
'''
    
    cmd = f'''cat > /tmp/check_hourly.py << 'EOFPYTHON'
{script}
EOFPYTHON
python3 /tmp/check_hourly.py
rm /tmp/check_hourly.py
'''
    
    stdout, stderr, returncode = run_remote_command(cmd)
    if returncode == 0 and stdout and not stdout.startswith("ERROR"):
        results = []
        for line in stdout.strip().split('\n'):
            if '|' in line:
                parts = line.split('|')
                if len(parts) == 3:
                    results.append((int(parts[0]), int(parts[1]), parts[2]))
        return results
    return []

def main():
    print("=" * 80)
    print("🌙 OVERNIGHT SIGNAL GENERATION REPORT")
    print("=" * 80)
    print(f"Server: {PROD_SERVER}")
    print(f"Database: {DB_PATH}")
    print(f"Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check different time periods
    print("📊 SIGNAL COUNTS BY TIME PERIOD:")
    print("-" * 80)
    
    periods = [
        (1, "Last 1 hour"),
        (3, "Last 3 hours"),
        (6, "Last 6 hours"),
        (8, "Last 8 hours (overnight)"),
        (12, "Last 12 hours"),
        (24, "Last 24 hours"),
    ]
    
    for hours, label in periods:
        count, latest, earliest = get_signal_count(hours)
        if count is not None:
            print(f"{label:25} {count:>8} signals", end="")
            if latest:
                try:
                    latest_dt = datetime.fromisoformat(latest.replace('Z', '+00:00'))
                    time_ago = datetime.now(latest_dt.tzinfo) - latest_dt
                    mins_ago = int(time_ago.total_seconds() / 60)
                    print(f"  (Latest: {mins_ago} min ago)")
                except:
                    print(f"  (Latest: {latest[:19]})")
            else:
                print()
        else:
            print(f"{label:25} {'ERROR':>8}")
    
    print()
    print("=" * 80)
    print("📈 HOURLY BREAKDOWN (Last 12 Hours):")
    print("-" * 80)
    print(f"{'Hours Ago':<12} {'Signals':<10} {'Time Period':<30}")
    print("-" * 80)
    
    hourly = get_hourly_breakdown()
    if hourly:
        for hours_ago, count, time_str in hourly:
            status = "✅" if count > 0 else "⚠️"
            print(f"{status} {hours_ago:>2}h ago      {count:>6}     {time_str}")
    else:
        print("  ⚠️  Could not retrieve hourly breakdown")
    
    print()
    print("=" * 80)
    print("💡 ANALYSIS:")
    print("-" * 80)
    
    # Get counts for analysis
    last_1h, _, _ = get_signal_count(1)
    last_8h, _, _ = get_signal_count(8)
    last_12h, _, _ = get_signal_count(12)
    
    if last_1h is not None and last_8h is not None:
        # Calculate expected signals per hour (assuming 5 second cycles)
        # With 6 symbols and 5 second cycles, expect ~4320 signals per hour
        expected_per_hour = 4320  # 6 symbols * 720 cycles/hour
        
        if last_1h > 0:
            rate_per_hour = last_1h
            print(f"✅ Current generation rate: ~{rate_per_hour:,} signals/hour")
            if rate_per_hour < expected_per_hour * 0.5:
                print(f"⚠️  WARNING: Generation rate is below 50% of expected ({expected_per_hour:,}/hour)")
        else:
            print("❌ No signals generated in the last hour!")
        
        if last_8h is not None and last_1h is not None:
            # Calculate average over 8 hours
            avg_per_hour_8h = last_8h / 8 if last_8h > 0 else 0
            print(f"📊 Average over last 8 hours: ~{avg_per_hour_8h:,.0f} signals/hour")
            
            if last_1h > avg_per_hour_8h * 2:
                print("⚠️  NOTE: Recent activity is much higher than 8-hour average")
                print("   This suggests signal generation may have been paused/resumed")
    
    print()
    print("=" * 80)

if __name__ == "__main__":
    main()


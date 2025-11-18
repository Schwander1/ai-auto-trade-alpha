#!/usr/bin/env python3
"""
Check signal count across all databases (local and production)
"""
import sqlite3
from pathlib import Path
import os

def check_database(db_path, name):
    """Check a single database"""
    if not db_path.exists():
        return None
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Total signals
        cursor.execute('SELECT COUNT(*) FROM signals')
        total = cursor.fetchone()[0]
        
        # Executed trades
        cursor.execute('SELECT COUNT(*) FROM signals WHERE order_id IS NOT NULL AND order_id != ""')
        executed = cursor.fetchone()[0]
        
        # Recent signals
        cursor.execute('SELECT COUNT(*) FROM signals WHERE created_at >= datetime("now", "-24 hours")')
        recent_24h = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM signals WHERE created_at >= datetime("now", "-1 hour")')
        recent_1h = cursor.fetchone()[0]
        
        # Database size
        size_mb = db_path.stat().st_size / (1024 * 1024)
        
        # Latest signal
        cursor.execute('SELECT symbol, action, confidence, created_at FROM signals ORDER BY created_at DESC LIMIT 1')
        latest = cursor.fetchone()
        
        conn.close()
        
        return {
            'name': name,
            'path': str(db_path),
            'total': total,
            'executed': executed,
            'recent_24h': recent_24h,
            'recent_1h': recent_1h,
            'size_mb': size_mb,
            'latest': latest
        }
    except Exception as e:
        return {'name': name, 'error': str(e)}

# Check all possible database locations
databases = [
    (Path('./argo/data/signals.db'), 'Local Argo'),
    (Path('./data/signals.db'), 'Local Root'),
    (Path('/root/argo-production-green/data/signals.db'), 'Production Argo (Green)'),
    (Path('/root/argo-production-prop-firm/data/signals.db'), 'Production Prop Firm'),
    (Path('/root/argo-production/data/signals.db'), 'Production (Legacy)'),
]

print('='*70)
print('📊 SIGNAL STORAGE COUNT - ALL DATABASES')
print('='*70)

results = []
total_all = 0

for db_path, name in databases:
    result = check_database(db_path, name)
    if result:
        if 'error' in result:
            print(f'\n❌ {name}: {result["error"]}')
        else:
            results.append(result)
            total_all += result['total']
            
            print(f'\n📁 {name}')
            print(f'   Path: {result["path"]}')
            print(f'   Total Signals: {result["total"]:,}')
            print(f'   Executed Trades: {result["executed"]:,}')
            print(f'   Signals (last 24h): {result["recent_24h"]:,}')
            print(f'   Signals (last 1h): {result["recent_1h"]:,}')
            print(f'   Database Size: {result["size_mb"]:.2f} MB')
            if result['latest']:
                symbol, action, confidence, created_at = result['latest']
                print(f'   Latest Signal: {symbol} {action} @ {confidence:.1f}% - {created_at}')

print(f'\n{'='*70}')
print(f'📊 SUMMARY')
print(f'{'='*70}')
print(f'Total Signals Across All Databases: {total_all:,}')
print(f'Databases Found: {len(results)}')

if results:
    print(f'\n📋 Breakdown:')
    for r in results:
        print(f'   {r["name"]}: {r["total"]:,} signals')

print(f'\n💡 Note: Production databases are on the server.')
print(f'   To check production, run this script on the production server:')
print(f'   ssh root@178.156.194.174 "cd /root && python3 check_signal_count.py"')


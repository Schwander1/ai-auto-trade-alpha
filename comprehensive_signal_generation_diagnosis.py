#!/usr/bin/env python3
"""
Comprehensive Signal Generation Diagnosis for Production
"""
import subprocess
import json
import sys
from datetime import datetime

PROD_SERVER = "root@178.156.194.174"

def run_remote(cmd):
    """Run command on production server"""
    try:
        result = subprocess.run(
            ['ssh', PROD_SERVER, cmd],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout, result.stderr, result.returncode
    except Exception as e:
        return None, str(e), 1

def main():
    print("="*80)
    print("🔍 COMPREHENSIVE SIGNAL GENERATION DIAGNOSIS")
    print("="*80)
    print()
    
    # 1. Check service status (Unified Architecture)
    print("1️⃣ SERVICE STATUS (Unified Architecture)")
    print("-"*80)
    print("Unified Signal Generator:")
    stdout, _, _ = run_remote("systemctl is-active argo-signal-generator.service")
    print(f"  argo-signal-generator.service: {stdout.strip()}")
    print("\nTrading Executors:")
    stdout, _, _ = run_remote("systemctl is-active argo-trading-executor.service argo-prop-firm-executor.service")
    for line in stdout.strip().split('\n'):
        if line.strip():
            print(f"  {line.strip()}")
    print()
    
    # 2. Check configs
    print("2️⃣ CONFIGURATION CHECK")
    print("-"*80)
    for service, path in [("Argo", "/root/argo-production-green/config.json"), 
                          ("Prop Firm", "/root/argo-production-prop-firm/config.json")]:
        cmd = f"python3 -c \"import json; c=json.load(open('{path}')); t=c.get('trading',{{}}); print(f'auto_execute: {{t.get(\\\"auto_execute\\\", False)}}'); print(f'force_24_7_mode: {{t.get(\\\"force_24_7_mode\\\", False)}}')\""
        stdout, stderr, _ = run_remote(cmd)
        print(f"{service}:")
        if stdout:
            print(f"  {stdout.strip()}")
        else:
            print(f"  ⚠️  Config not found or error: {stderr}")
    print()
    
    # 3. Check health endpoints
    print("3️⃣ HEALTH ENDPOINTS")
    print("-"*80)
    for port, name in [(8000, "Argo"), (8001, "Prop Firm")]:
        cmd = f"curl -s http://localhost:{port}/health 2>/dev/null | python3 -c \"import sys,json; d=json.load(sys.stdin); sg=d.get('signal_generation',{{}}); print(f'Status: {{d.get(\\\"status\\\")}}'); print(f'Background task running: {{sg.get(\\\"background_task_running\\\", False)}}'); print(f'Background task error: {{sg.get(\\\"background_task_error\\\")}}')\" 2>&1"
        stdout, _, _ = run_remote(cmd)
        print(f"{name} (port {port}):")
        if stdout and "Expecting value" not in stdout:
            for line in stdout.strip().split('\n'):
                print(f"  {line}")
        else:
            print(f"  ⚠️  Service not responding or error")
    print()
    
    # 4. Check for background task startup logs
    print("4️⃣ BACKGROUND TASK STARTUP LOGS")
    print("-"*80)
    cmd = "grep -h 'Background\|background\|🚀.*signal\|start_background' /root/argo-production-green/logs/service.log /root/argo-production-prop-firm/logs/service.log 2>/dev/null | tail -20"
    stdout, _, _ = run_remote(cmd)
    if stdout:
        for line in stdout.strip().split('\n'):
            print(f"  {line}")
    else:
        print("  ⚠️  No background task startup logs found")
    print()
    
    # 5. Check for signal generation cycles
    print("5️⃣ SIGNAL GENERATION CYCLES")
    print("-"*80)
    cmd = "grep -h '_run_signal_generation_cycle\|Generated.*signals\|Signal generation cycle' /root/argo-production-green/logs/service.log /root/argo-production-prop-firm/logs/service.log 2>/dev/null | tail -20"
    stdout, _, _ = run_remote(cmd)
    if stdout:
        for line in stdout.strip().split('\n'):
            print(f"  {line}")
    else:
        print("  ⚠️  No signal generation cycle logs found")
    print()
    
    # 6. Check recent signals in database (Unified Architecture)
    print("6️⃣ DATABASE SIGNALS (Unified Database)")
    print("-"*80)
    print("ℹ️  Unified Architecture: All signals stored in unified database")
    unified_db = "/root/argo-production-unified/data/signals_unified.db"
    cmd = f"sqlite3 {unified_db} \"SELECT COUNT(*) as total, MAX(timestamp) as latest FROM signals;\" 2>/dev/null || echo 'Unified DB not found'"
    stdout, _, _ = run_remote(cmd)
    print("Unified Database:")
    if stdout and "not found" not in stdout:
        parts = stdout.strip().split('|')
        if len(parts) == 2:
            print(f"  Total signals: {parts[0]}")
            print(f"  Latest signal: {parts[1] if parts[1] else 'None'}")
    else:
        print(f"  ⚠️  Unified database not accessible")
    
    # Also check old databases for reference (may not exist)
    for service, db in [("Argo (OLD)", "/root/argo-production-green/data/signals.db"),
                        ("Prop Firm (OLD)", "/root/argo-production-prop-firm/data/signals.db")]:
        cmd = f"sqlite3 {db} \"SELECT COUNT(*) as total, MAX(timestamp) as latest FROM signals;\" 2>/dev/null || echo 'DB not found'"
        stdout, _, _ = run_remote(cmd)
        print(f"{service}:")
        if stdout and "not found" not in stdout:
            parts = stdout.strip().split('|')
            if len(parts) == 2:
                print(f"  Total signals: {parts[0]}")
                print(f"  Latest signal: {parts[1] if parts[1] else 'None'}")
        else:
            print(f"  ⚠️  Database not accessible")
    print()
    
    # 7. Check processes
    print("7️⃣ RUNNING PROCESSES")
    print("-"*80)
    cmd = "ps aux | grep -E 'python.*main|uvicorn|run_signal_generator' | grep -v grep"
    stdout, _, _ = run_remote(cmd)
    if stdout:
        for line in stdout.strip().split('\n'):
            if line:
                parts = line.split()
                print(f"  PID {parts[1]}: {' '.join(parts[10:15])}")
    else:
        print("  ⚠️  No relevant processes found")
    print()
    
    # 8. Check for errors
    print("8️⃣ RECENT ERRORS")
    print("-"*80)
    cmd = "grep -h -i 'error\|exception\|failed\|traceback' /root/argo-production-green/logs/service.log /root/argo-production-prop-firm/logs/service.log 2>/dev/null | tail -10"
    stdout, _, _ = run_remote(cmd)
    if stdout:
        for line in stdout.strip().split('\n'):
            if line:
                print(f"  {line[:150]}")
    else:
        print("  ✅ No recent errors found")
    print()
    
    # Summary
    print("="*80)
    print("📊 SUMMARY & RECOMMENDATIONS")
    print("="*80)
    print()
    print("Key Findings:")
    print("  - Check if background task is actually starting in lifespan")
    print("  - Verify signal generation cycles are executing")
    print("  - Check for silent failures in background task")
    print("  - Verify database connectivity")
    print()
    print("Next Steps:")
    print("  1. Check if lifespan function is being called")
    print("  2. Verify async task is actually running")
    print("  3. Check for exceptions being swallowed")
    print("  4. Restart services if needed")
    print()

if __name__ == "__main__":
    main()


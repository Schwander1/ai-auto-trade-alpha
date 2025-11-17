#!/usr/bin/env python3
"""
Backtest Progress Monitor
Monitor backtest execution progress in real-time
"""
import sys
import time
import subprocess
from pathlib import Path
from datetime import datetime
import json

def monitor_backtest_progress(log_file: str = "/tmp/optimized_backtest.log", 
                              results_file: str = "argo/reports/comprehensive_backtest_results.json",
                              check_interval: int = 5):
    """Monitor backtest progress"""
    log_path = Path(log_file)
    results_path = Path(results_file)
    
    print("🔍 Monitoring Backtest Progress...")
    print(f"   Log File: {log_file}")
    print(f"   Results File: {results_file}")
    print(f"   Check Interval: {check_interval} seconds")
    print("="*80)
    
    last_size = 0
    start_time = datetime.now()
    completed_symbols = set()
    total_symbols = 12  # Approximate
    
    try:
        while True:
            # Check if log file exists and has grown
            if log_path.exists():
                current_size = log_path.stat().st_size
                if current_size > last_size:
                    # Read new lines
                    with open(log_path, 'r') as f:
                        lines = f.readlines()
                        new_lines = lines[-20:]  # Last 20 lines
                        
                        # Check for completed backtests
                        for line in new_lines:
                            if "Backtest stats" in line:
                                # Extract symbol
                                if "for" in line:
                                    parts = line.split("for")
                                    if len(parts) > 1:
                                        symbol = parts[1].split(":")[0].strip()
                                        completed_symbols.add(symbol)
                            
                            # Check for errors
                            if "ERROR" in line or "Traceback" in line:
                                print(f"⚠️  ERROR detected: {line.strip()}")
                            
                            # Check for completion
                            if "RESULTS" in line or "Results saved" in line:
                                print("\n✅ Backtest completed!")
                                break
                    
                    last_size = current_size
                    
                    # Show progress
                    elapsed = (datetime.now() - start_time).total_seconds()
                    progress_pct = (len(completed_symbols) / total_symbols) * 100 if total_symbols > 0 else 0
                    
                    print(f"\r⏱️  Elapsed: {elapsed:.0f}s | "
                          f"Completed: {len(completed_symbols)}/{total_symbols} symbols "
                          f"({progress_pct:.1f}%) | "
                          f"Log Size: {current_size/1024:.1f} KB", end="", flush=True)
            
            # Check if results file exists and is complete
            if results_path.exists():
                try:
                    with open(results_path, 'r') as f:
                        results = json.load(f)
                        total_results = sum(len(v) for v in results.values())
                        if total_results > 0:
                            print(f"\n✅ Results file found: {total_results} backtest results")
                            break
                except:
                    pass
            
            time.sleep(check_interval)
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Monitoring stopped by user")
    except Exception as e:
        print(f"\n❌ Error monitoring: {e}")

def check_backtest_status():
    """Check current backtest status"""
    log_file = Path("/tmp/optimized_backtest.log")
    results_file = Path("argo/reports/comprehensive_backtest_results.json")
    
    print("📊 Backtest Status Check")
    print("="*80)
    
    # Check if process is running
    try:
        result = subprocess.run(
            ["pgrep", "-f", "run_comprehensive_backtest"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            pids = result.stdout.strip().split('\n')
            print(f"✅ Backtest process running (PIDs: {', '.join(pids)})")
        else:
            print("❌ No backtest process found")
    except:
        print("⚠️  Could not check process status")
    
    # Check log file
    if log_file.exists():
        size = log_file.stat().st_size
        mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
        age = (datetime.now() - mtime).total_seconds()
        
        print(f"\n📝 Log File:")
        print(f"   Path: {log_file}")
        print(f"   Size: {size/1024:.1f} KB")
        print(f"   Last Modified: {mtime.strftime('%Y-%m-%d %H:%M:%S')} ({age:.0f}s ago)")
        
        # Show last few lines
        try:
            with open(log_file, 'r') as f:
                lines = f.readlines()
                print(f"\n   Last 5 lines:")
                for line in lines[-5:]:
                    print(f"   {line.strip()}")
        except:
            pass
    else:
        print(f"\n❌ Log file not found: {log_file}")
    
    # Check results file
    if results_file.exists():
        size = results_file.stat().st_size
        mtime = datetime.fromtimestamp(results_file.stat().st_mtime)
        
        print(f"\n📊 Results File:")
        print(f"   Path: {results_file}")
        print(f"   Size: {size/1024:.1f} KB")
        print(f"   Last Modified: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            with open(results_file, 'r') as f:
                results = json.load(f)
                total_results = sum(len(v) for v in results.values())
                print(f"   Total Results: {total_results}")
                for config, config_results in results.items():
                    print(f"   - {config}: {len(config_results)} backtests")
        except Exception as e:
            print(f"   ⚠️  Error reading results: {e}")
    else:
        print(f"\n⏳ Results file not found yet: {results_file}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Monitor backtest progress")
    parser.add_argument("--monitor", action="store_true", help="Monitor in real-time")
    parser.add_argument("--status", action="store_true", help="Check current status")
    parser.add_argument("--log", default="/tmp/optimized_backtest.log", help="Log file path")
    parser.add_argument("--results", default="argo/reports/comprehensive_backtest_results.json", help="Results file path")
    
    args = parser.parse_args()
    
    if args.monitor:
        monitor_backtest_progress(args.log, args.results)
    elif args.status:
        check_backtest_status()
    else:
        check_backtest_status()
        print("\n💡 Use --monitor to watch progress in real-time")


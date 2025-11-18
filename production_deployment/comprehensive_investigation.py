#!/usr/bin/env python3
"""
Comprehensive investigation script for production trading system
Checks all aspects of the system and identifies issues
"""
import sys
import json
import subprocess
import requests
from datetime import datetime
from pathlib import Path

def check_service_health(port, service_name):
    """Check service health endpoint"""
    try:
        response = requests.get(f"http://localhost:{port}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                "status": "healthy" if data.get("status") == "healthy" else "unhealthy",
                "signal_generation": data.get("signal_generation", {}).get("status", "unknown"),
                "background_task": data.get("signal_generation", {}).get("background_task_running", False)
            }
    except Exception as e:
        return {"status": "error", "error": str(e)}
    return {"status": "unknown"}

def check_trading_status(port, service_name):
    """Check trading status"""
    try:
        response = requests.get(f"http://localhost:{port}/api/v1/trading/status", timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        return {"error": str(e)}
    return {}

def check_recent_signals(port, limit=10):
    """Check recent signals"""
    try:
        response = requests.get(f"http://localhost:{port}/api/signals/latest?limit={limit}", timeout=5)
        if response.status_code == 200:
            signals = response.json()
            return signals if isinstance(signals, list) else []
    except Exception as e:
        return []
    return []

def analyze_logs(log_path, patterns):
    """Analyze logs for patterns"""
    results = {}
    try:
        if not Path(log_path).exists():
            return {"error": "Log file not found"}
        
        # Read last 1000 lines
        result = subprocess.run(
            ["tail", "-1000", log_path],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        log_content = result.stdout
        
        for pattern_name, pattern in patterns.items():
            matches = [line for line in log_content.split('\n') if pattern in line.lower()]
            results[pattern_name] = {
                "count": len(matches),
                "recent": matches[-5:] if matches else []
            }
    except Exception as e:
        results["error"] = str(e)
    
    return results

def main():
    print("\n" + "="*70)
    print("🔍 COMPREHENSIVE PRODUCTION INVESTIGATION")
    print("="*70)
    
    services = [
        (8000, "Argo Trading Service", "/root/argo-production-green/logs/service.log"),
        (8001, "Prop Firm Trading Service", "/root/argo-production-prop-firm/logs/service.log")
    ]
    
    issues = []
    warnings = []
    
    for port, service_name, log_path in services:
        print(f"\n{'='*70}")
        print(f"📊 {service_name} (Port {port})")
        print("="*70)
        
        # Health check
        print("\n1. Health Status:")
        health = check_service_health(port, service_name)
        print(f"   Status: {health.get('status', 'unknown')}")
        print(f"   Signal Generation: {health.get('signal_generation', 'unknown')}")
        print(f"   Background Task: {health.get('background_task', False)}")
        
        if health.get('status') != 'healthy':
            issues.append(f"{service_name}: Service unhealthy")
        
        # Trading status
        print("\n2. Trading Status:")
        trading = check_trading_status(port, service_name)
        if trading:
            print(f"   Alpaca Connected: {trading.get('alpaca_connected', False)}")
            print(f"   Prop Firm Enabled: {trading.get('prop_firm_enabled', False)}")
            print(f"   Portfolio Value: ${trading.get('portfolio_value', 0):,.2f}" if trading.get('portfolio_value') else "   Portfolio Value: N/A")
            print(f"   Buying Power: ${trading.get('buying_power', 0):,.2f}" if trading.get('buying_power') else "   Buying Power: N/A")
            
            if not trading.get('alpaca_connected'):
                warnings.append(f"{service_name}: Alpaca not connected")
        else:
            warnings.append(f"{service_name}: Could not get trading status")
        
        # Recent signals
        print("\n3. Recent Signals:")
        signals = check_recent_signals(port, limit=5)
        print(f"   Found: {len(signals)} signals")
        if signals:
            for sig in signals[:3]:
                print(f"   - {sig.get('symbol', 'N/A')}: {sig.get('confidence', 0)}% ({sig.get('action', 'N/A')})")
        else:
            warnings.append(f"{service_name}: No recent signals found")
        
        # Log analysis
        print("\n4. Log Analysis:")
        log_patterns = {
            "errors": "error",
            "signals_generated": "generated signal",
            "trades_executed": "trade executed",
            "execution_skipped": "skipping|early exit|no market data",
            "alpaca_issues": "alpaca|connection",
            "data_source_issues": "massive|alpha vantage|data source"
        }
        
        log_analysis = analyze_logs(log_path, log_patterns)
        if "error" not in log_analysis:
            for pattern_name, data in log_analysis.items():
                count = data.get("count", 0)
                print(f"   {pattern_name}: {count} occurrences")
                
                if pattern_name == "errors" and count > 10:
                    issues.append(f"{service_name}: {count} errors in logs")
                elif pattern_name == "signals_generated" and count == 0:
                    warnings.append(f"{service_name}: No signals generated recently")
                elif pattern_name == "trades_executed" and count == 0:
                    warnings.append(f"{service_name}: No trades executed recently")
                elif pattern_name == "execution_skipped" and count > 20:
                    warnings.append(f"{service_name}: Many execution skips ({count})")
        else:
            print(f"   Error analyzing logs: {log_analysis.get('error')}")
    
    # Summary
    print("\n" + "="*70)
    print("📊 INVESTIGATION SUMMARY")
    print("="*70)
    
    if issues:
        print("\n❌ Issues Found:")
        for issue in issues:
            print(f"   - {issue}")
    else:
        print("\n✅ No critical issues found")
    
    if warnings:
        print("\n⚠️  Warnings:")
        for warning in warnings:
            print(f"   - {warning}")
    else:
        print("\n✅ No warnings")
    
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    main()


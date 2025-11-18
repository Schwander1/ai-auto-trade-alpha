#!/usr/bin/env python3
"""
Check Trade Execution Status
Query the running service to check if trades are being executed
"""
import sys
import requests
import json
from datetime import datetime, timedelta
from pathlib import Path

def check_signal_execution_status():
    """Check if signals are being executed"""
    print("\n" + "="*70)
    print("🔍 TRADE EXECUTION STATUS CHECK")
    print("="*70)
    
    # Get recent signals
    try:
        signals_url = "http://localhost:8000/api/signals/latest?limit=20"
        response = requests.get(signals_url, timeout=5)
        if response.status_code == 200:
            signals = response.json()
            print(f"\n📊 Recent Signals: {len(signals)}")
            
            # Analyze signals
            executed_count = 0
            skipped_count = 0
            high_confidence = 0
            
            for sig in signals:
                confidence = sig.get('confidence', 0)
                if confidence >= 75:
                    high_confidence += 1
                
                # Check if signal has order_id (indicates execution attempt)
                if sig.get('order_id'):
                    executed_count += 1
                    print(f"   ✅ {sig.get('symbol')}: {sig.get('action')} @ ${sig.get('price', 0):.2f} ({confidence:.1f}%) - Order ID: {sig.get('order_id')}")
                elif confidence >= 60:
                    skipped_count += 1
                    print(f"   ⏭️  {sig.get('symbol')}: {sig.get('action')} @ ${sig.get('price', 0):.2f} ({confidence:.1f}%) - No order ID")
            
            print(f"\n   High Confidence Signals (≥75%): {high_confidence}")
            print(f"   Signals with Order IDs: {executed_count}")
            print(f"   Signals without Order IDs: {skipped_count}")
            
            return signals
        else:
            print(f"   ❌ Error fetching signals: {response.status_code}")
            return []
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return []

def check_database_for_signals():
    """Check database for signals and execution status"""
    print("\n" + "-"*70)
    print("📊 Database Signal Analysis")
    print("-"*70)
    
    db_paths = [
        Path("argo/data/signals.db"),
        Path("data/signals.db"),
    ]
    
    for db_path in db_paths:
        if db_path.exists():
            try:
                import sqlite3
                conn = sqlite3.connect(str(db_path))
                cursor = conn.cursor()
                
                # Get recent signals
                cursor.execute("""
                    SELECT symbol, action, entry_price, confidence, timestamp, order_id
                    FROM signals
                    ORDER BY timestamp DESC
                    LIMIT 20
                """)
                
                signals = cursor.fetchall()
                print(f"\n   Found {len(signals)} recent signals in database")
                
                executed = 0
                for sig in signals:
                    symbol, action, price, confidence, timestamp, order_id = sig
                    if order_id:
                        executed += 1
                        print(f"   ✅ {symbol}: {action} @ ${price:.2f} ({confidence:.1f}%) - Order: {order_id}")
                    elif confidence >= 60:
                        print(f"   ⏭️  {symbol}: {action} @ ${price:.2f} ({confidence:.1f}%) - No order")
                
                print(f"\n   Signals with orders: {executed}/{len(signals)}")
                
                conn.close()
                return True
            except Exception as e:
                print(f"   ⚠️  Error reading database: {e}")
                return False
    
    print("   ⚠️  Database not found")
    return False

def check_risk_validation():
    """Check risk validation status"""
    print("\n" + "-"*70)
    print("🛡️  Risk Validation Status")
    print("-"*70)
    
    # Get account status
    try:
        status_url = "http://localhost:8000/api/v1/trading/status"
        response = requests.get(status_url, timeout=5)
        if response.status_code == 200:
            status = response.json()
            
            portfolio_value = status.get('portfolio_value', 0)
            buying_power = status.get('buying_power', 0)
            
            print(f"   Portfolio Value: ${portfolio_value:,.2f}")
            print(f"   Buying Power: ${buying_power:,.2f}")
            
            # Check if trading is blocked
            if status.get('trading_blocked', False):
                print("   ⚠️  Trading is BLOCKED")
            else:
                print("   ✅ Trading is NOT blocked")
            
            return status
        else:
            print(f"   ⚠️  Could not check risk status: {response.status_code}")
            return None
    except Exception as e:
        print(f"   ⚠️  Error: {e}")
        return None

def check_service_health():
    """Check service health for execution status"""
    print("\n" + "-"*70)
    print("💚 Service Health Check")
    print("-"*70)
    
    try:
        health_url = "http://localhost:8000/health"
        response = requests.get(health_url, timeout=5)
        if response.status_code == 200:
            health = response.json()
            
            signal_gen = health.get('signal_generation', {})
            print(f"   Signal Generation: {signal_gen.get('status', 'unknown')}")
            print(f"   Background Task: {'Running' if signal_gen.get('background_task_running') else 'Not Running'}")
            
            if signal_gen.get('background_task_error'):
                print(f"   ⚠️  Background Task Error: {signal_gen.get('background_task_error')}")
            
            return health
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def analyze_execution_pattern(signals):
    """Analyze execution patterns"""
    print("\n" + "-"*70)
    print("📈 Execution Pattern Analysis")
    print("-"*70)
    
    if not signals:
        print("   ⚠️  No signals to analyze")
        return
    
    # Group by symbol
    symbol_stats = {}
    for sig in signals:
        symbol = sig.get('symbol', 'UNKNOWN')
        if symbol not in symbol_stats:
            symbol_stats[symbol] = {
                'total': 0,
                'executed': 0,
                'skipped': 0,
                'avg_confidence': 0,
                'actions': []
            }
        
        stats = symbol_stats[symbol]
        stats['total'] += 1
        stats['actions'].append(sig.get('action'))
        stats['avg_confidence'] += sig.get('confidence', 0)
        
        if sig.get('order_id'):
            stats['executed'] += 1
        else:
            stats['skipped'] += 1
    
    # Calculate averages and print
    for symbol, stats in symbol_stats.items():
        stats['avg_confidence'] = stats['avg_confidence'] / stats['total'] if stats['total'] > 0 else 0
        execution_rate = (stats['executed'] / stats['total'] * 100) if stats['total'] > 0 else 0
        
        print(f"\n   {symbol}:")
        print(f"      Total Signals: {stats['total']}")
        print(f"      Executed: {stats['executed']} ({execution_rate:.1f}%)")
        print(f"      Skipped: {stats['skipped']}")
        print(f"      Avg Confidence: {stats['avg_confidence']:.1f}%")
        print(f"      Actions: {', '.join(set(stats['actions']))}")

def main():
    """Main execution"""
    health = check_service_health()
    signals = check_signal_execution_status()
    risk_status = check_risk_validation()
    check_database_for_signals()
    
    if signals:
        analyze_execution_pattern(signals)
    
    print("\n" + "="*70)
    print("📊 SUMMARY")
    print("="*70)
    
    if signals:
        executed = sum(1 for s in signals if s.get('order_id'))
        high_conf = sum(1 for s in signals if s.get('confidence', 0) >= 75)
        print(f"   Recent Signals: {len(signals)}")
        print(f"   High Confidence (≥75%): {high_conf}")
        print(f"   With Order IDs: {executed}")
        print(f"   Without Order IDs: {len(signals) - executed}")
    
    if risk_status:
        if risk_status.get('trading_blocked', False):
            print("\n   ⚠️  WARNING: Trading is blocked!")
        else:
            print("\n   ✅ Trading is not blocked")
    
    print("="*70 + "\n")

if __name__ == "__main__":
    main()


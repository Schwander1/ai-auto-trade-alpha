#!/usr/bin/env python3
"""
Comprehensive Trade Execution Investigation
Checks signal generation, storage, distribution, and execution status
"""
import sys
import json
import sqlite3
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional

def check_signal_database() -> Dict:
    """Check signal database for recent signals and execution status"""
    print("\n" + "="*70)
    print("📊 SIGNAL DATABASE ANALYSIS")
    print("="*70)
    
    db_paths = [
        Path("argo/data/signals.db"),
        Path("data/signals.db"),
        Path("/root/argo-production-green/data/signals.db"),
        Path("/root/argo-production-unified/data/signals_unified.db"),
    ]
    
    for db_path in db_paths:
        if db_path.exists():
            print(f"\n✅ Found database: {db_path}")
            try:
                conn = sqlite3.connect(str(db_path))
                cursor = conn.cursor()
                
                # Get table schema
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                print(f"   Tables: {[t[0] for t in tables]}")
                
                # Check if signals table exists
                table_name = "signals" if ("signals",) in tables else ("signals_unified" if ("signals_unified",) in tables else None)
                if not table_name:
                    print("   ⚠️  No signals table found")
                    conn.close()
                    continue
                
                # Get table schema first
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = [col[1] for col in cursor.fetchall()]
                print(f"   Columns: {columns}")
                
                # Build SELECT query based on available columns
                select_cols = ['signal_id', 'symbol', 'action', 'entry_price', 'confidence', 'timestamp', 'order_id']
                if 'service_type' in columns:
                    select_cols.append('service_type')
                
                # Get recent signals
                cursor.execute(f"""
                    SELECT {', '.join(select_cols)}
                    FROM {table_name}
                    ORDER BY timestamp DESC
                    LIMIT 50
                """)
                
                signals = cursor.fetchall()
                print(f"\n   📈 Recent Signals: {len(signals)}")
                
                if not signals:
                    print("   ⚠️  No signals found in database")
                    conn.close()
                    continue
                
                # Analyze signals
                executed = 0
                no_order = 0
                high_confidence = 0
                recent_signals = []
                
                for sig in signals:
                    signal_id = sig[0]
                    symbol = sig[1]
                    action = sig[2]
                    price = sig[3]
                    confidence = sig[4]
                    timestamp = sig[5]
                    order_id = sig[6] if len(sig) > 6 else None
                    service_type = sig[7] if len(sig) > 7 else None
                    
                    # Check if recent (last 24 hours)
                    try:
                        sig_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        if (datetime.now(sig_time.tzinfo) - sig_time).total_seconds() < 86400:
                            recent_signals.append({
                                'signal_id': signal_id,
                                'symbol': symbol,
                                'action': action,
                                'price': price,
                                'confidence': confidence,
                                'timestamp': timestamp,
                                'order_id': order_id,
                                'service_type': service_type
                            })
                    except:
                        pass
                    
                    if order_id:
                        executed += 1
                    else:
                        no_order += 1
                    
                    if confidence >= 75:
                        high_confidence += 1
                
                print(f"   ✅ Signals with order_id: {executed}")
                print(f"   ⏭️  Signals without order_id: {no_order}")
                print(f"   📊 High confidence (≥75%): {high_confidence}")
                print(f"   🕐 Recent signals (last 24h): {len(recent_signals)}")
                
                # Show recent signals
                if recent_signals:
                    print(f"\n   📋 Recent Signals (last 24h):")
                    for sig in recent_signals[:10]:
                        status = "✅ EXECUTED" if sig['order_id'] else "⏭️  NOT EXECUTED"
                        print(f"      {status} | {sig['symbol']} {sig['action']} @ ${sig['price']:.2f} ({sig['confidence']:.1f}%) | {sig['timestamp']}")
                        if sig['order_id']:
                            print(f"         Order ID: {sig['order_id']}")
                
                conn.close()
                return {
                    'database_path': str(db_path),
                    'total_signals': len(signals),
                    'executed': executed,
                    'not_executed': no_order,
                    'recent_signals': recent_signals
                }
                
            except Exception as e:
                print(f"   ❌ Error reading database: {e}")
                import traceback
                traceback.print_exc()
    
    print("   ⚠️  No signal database found")
    return None

def check_service_health() -> Dict:
    """Check Argo service health and status"""
    print("\n" + "="*70)
    print("💚 SERVICE HEALTH CHECK")
    print("="*70)
    
    services = [
        ("Argo Service", "http://localhost:8000"),
        ("Prop Firm Service", "http://localhost:8001"),
        ("Signal Generator", "http://localhost:7999"),
    ]
    
    results = {}
    for name, base_url in services:
        try:
            health_url = f"{base_url}/health"
            response = requests.get(health_url, timeout=5)
            if response.status_code == 200:
                health = response.json()
                print(f"\n✅ {name}: HEALTHY")
                print(f"   Status: {health.get('status', 'unknown')}")
                
                # Check signal generation status
                if 'signal_generation' in health:
                    sg = health['signal_generation']
                    print(f"   Background Task: {'Running' if sg.get('background_task_running') else 'Not Running'}")
                    if sg.get('background_task_error'):
                        print(f"   ⚠️  Error: {sg.get('background_task_error')}")
                
                results[name] = health
            else:
                print(f"\n⚠️  {name}: HTTP {response.status_code}")
                results[name] = {'status': 'error', 'code': response.status_code}
        except requests.exceptions.ConnectionError:
            print(f"\n❌ {name}: NOT RUNNING (connection refused)")
            results[name] = {'status': 'not_running'}
        except Exception as e:
            print(f"\n❌ {name}: ERROR - {e}")
            results[name] = {'status': 'error', 'error': str(e)}
    
    return results

def check_executor_endpoints() -> Dict:
    """Check if executor endpoints are accessible"""
    print("\n" + "="*70)
    print("🔌 EXECUTOR ENDPOINTS CHECK")
    print("="*70)
    
    endpoints = [
        ("Argo Executor", "http://localhost:8000/api/v1/trading/execute"),
        ("Prop Firm Executor", "http://localhost:8001/api/v1/trading/execute"),
    ]
    
    results = {}
    for name, url in endpoints:
        try:
            # Try to get status first
            status_url = url.replace('/execute', '/status')
            response = requests.get(status_url, timeout=5)
            if response.status_code == 200:
                status = response.json()
                print(f"\n✅ {name}: AVAILABLE")
                print(f"   Status: {status.get('status', 'unknown')}")
                print(f"   Executor ID: {status.get('executor_id', 'unknown')}")
                if 'account' in status:
                    acc = status['account']
                    print(f"   Portfolio: ${acc.get('portfolio_value', 0):,.2f}")
                results[name] = {'available': True, 'status': status}
            else:
                print(f"\n⚠️  {name}: HTTP {response.status_code}")
                results[name] = {'available': False, 'code': response.status_code}
        except requests.exceptions.ConnectionError:
            print(f"\n❌ {name}: NOT AVAILABLE (connection refused)")
            results[name] = {'available': False, 'reason': 'connection_refused'}
        except Exception as e:
            print(f"\n❌ {name}: ERROR - {e}")
            results[name] = {'available': False, 'error': str(e)}
    
    return results

def check_signal_generation_service() -> Dict:
    """Check signal generation service configuration"""
    print("\n" + "="*70)
    print("⚙️  SIGNAL GENERATION SERVICE CONFIG")
    print("="*70)
    
    try:
        # Try to get service status
        response = requests.get("http://localhost:8000/api/v1/signal-generation/status", timeout=5)
        if response.status_code == 200:
            status = response.json()
            print("\n✅ Signal Generation Service Status:")
            print(f"   Auto-execute: {status.get('auto_execute', 'unknown')}")
            print(f"   Trading Engine: {'Available' if status.get('trading_engine_available') else 'Not Available'}")
            print(f"   Distributor: {'Available' if status.get('distributor_available') else 'Not Available'}")
            print(f"   Paused: {status.get('paused', False)}")
            return status
        else:
            print(f"\n⚠️  Could not get service status: HTTP {response.status_code}")
            return {}
    except Exception as e:
        print(f"\n⚠️  Could not check service status: {e}")
        return {}

def check_recent_signals_api() -> List[Dict]:
    """Check recent signals via API"""
    print("\n" + "="*70)
    print("📡 RECENT SIGNALS (API)")
    print("="*70)
    
    try:
        response = requests.get("http://localhost:8000/api/signals/latest?limit=20", timeout=5)
        if response.status_code == 200:
            signals = response.json()
            print(f"\n✅ Retrieved {len(signals)} recent signals")
            
            executed = sum(1 for s in signals if s.get('order_id'))
            high_conf = sum(1 for s in signals if s.get('confidence', 0) >= 75)
            
            print(f"   With order_id: {executed}")
            print(f"   High confidence (≥75%): {high_conf}")
            
            # Show recent signals
            for sig in signals[:5]:
                status = "✅" if sig.get('order_id') else "⏭️"
                print(f"   {status} {sig.get('symbol')} {sig.get('action')} @ ${sig.get('entry_price', 0):.2f} ({sig.get('confidence', 0):.1f}%)")
            
            return signals
        else:
            print(f"\n⚠️  Could not get signals: HTTP {response.status_code}")
            return []
    except Exception as e:
        print(f"\n⚠️  Could not check signals API: {e}")
        return []

def analyze_execution_issues(db_data: Optional[Dict], service_health: Dict, executor_status: Dict) -> Dict:
    """Analyze why trades might not be executing"""
    print("\n" + "="*70)
    print("🔍 EXECUTION ISSUE ANALYSIS")
    print("="*70)
    
    issues = []
    recommendations = []
    
    # Check 1: Are signals being generated?
    if db_data and db_data.get('recent_signals'):
        recent_count = len(db_data['recent_signals'])
        if recent_count == 0:
            issues.append("❌ No signals generated in last 24 hours")
            recommendations.append("Check signal generation service background task")
        else:
            print(f"✅ Signals are being generated ({recent_count} in last 24h)")
    else:
        issues.append("⚠️  Cannot verify signal generation (no database access)")
    
    # Check 2: Are executor endpoints available?
    all_available = all(
        status.get('available', False) 
        for status in executor_status.values()
    )
    if not all_available:
        issues.append("❌ Executor endpoints not available")
        recommendations.append("Start trading executor services on ports 8000/8001")
        recommendations.append("Or disable distributor to use legacy direct execution mode")
    else:
        print("✅ Executor endpoints are available")
    
    # Check 3: Are signals being executed?
    if db_data:
        executed = db_data.get('executed', 0)
        total = db_data.get('total_signals', 0)
        if total > 0:
            execution_rate = (executed / total) * 100
            print(f"📊 Execution rate: {execution_rate:.1f}% ({executed}/{total})")
            
            if execution_rate == 0 and total > 10:
                issues.append("❌ No signals have been executed (0% execution rate)")
                recommendations.append("Check auto_execute configuration")
                recommendations.append("Check risk validation rules")
                recommendations.append("Check trading engine initialization")
    
    # Check 4: Service health
    if 'Argo Service' in service_health:
        argo_health = service_health['Argo Service']
        if argo_health.get('status') != 'healthy':
            issues.append(f"⚠️  Argo service not healthy: {argo_health.get('status')}")
    
    # Check 5: Distributor vs Legacy mode
    print("\n📋 Execution Mode Analysis:")
    if executor_status and any(s.get('available') for s in executor_status.values()):
        print("   Mode: Unified Architecture (Distributor → Executors)")
        print("   ⚠️  If distributor is initialized, signals go to HTTP endpoints")
        print("   ⚠️  If endpoints fail, execution fails silently")
    else:
        print("   Mode: Legacy Direct Execution")
        print("   ✅ Signals execute directly in signal generation service")
    
    return {
        'issues': issues,
        'recommendations': recommendations
    }

def main():
    """Main investigation"""
    print("\n" + "="*70)
    print("🔍 TRADE EXECUTION INVESTIGATION")
    print("="*70)
    print(f"Time: {datetime.now().isoformat()}")
    
    # Run all checks
    db_data = check_signal_database()
    service_health = check_service_health()
    executor_status = check_executor_endpoints()
    service_config = check_signal_generation_service()
    api_signals = check_recent_signals_api()
    
    # Analyze issues
    analysis = analyze_execution_issues(db_data, service_health, executor_status)
    
    # Summary
    print("\n" + "="*70)
    print("📊 SUMMARY")
    print("="*70)
    
    if analysis['issues']:
        print("\n❌ ISSUES FOUND:")
        for issue in analysis['issues']:
            print(f"   {issue}")
    
    if analysis['recommendations']:
        print("\n💡 RECOMMENDATIONS:")
        for rec in analysis['recommendations']:
            print(f"   • {rec}")
    
    if not analysis['issues']:
        print("\n✅ No major issues found")
        print("   System appears to be functioning correctly")
        print("   If trades aren't executing, check:")
        print("   • Risk validation rules")
        print("   • Confidence thresholds")
        print("   • Account status and buying power")
    
    print("="*70 + "\n")

if __name__ == "__main__":
    main()


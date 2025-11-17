#!/usr/bin/env python3
"""
Monitor V11 Performance
Compare live trading performance with V11 backtest expectations
"""
import json
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Optional

async def load_backtest_expectations() -> Dict:
    """Load V11 backtest expectations"""
    reports_dir = Path(__file__).parent.parent / "reports"
    v11_file = None
    
    # Find latest V11 results
    for f in sorted(reports_dir.glob("iterative_v11_*_results.json"), reverse=True):
        v11_file = f
        break
    
    if not v11_file or not v11_file.exists():
        print("⚠️  V11 backtest results not found")
        return {}
    
    with open(v11_file, 'r') as f:
        data = json.load(f)
    
    return {
        'summary': data.get('summary', {}),
        'timestamp': data.get('timestamp', ''),
        'config': data.get('strategy_config', {})
    }

def get_live_performance() -> Dict:
    """Get current live trading performance"""
    # This would connect to your trading database/API
    # For now, return placeholder structure
    return {
        'win_rate': 0.0,
        'total_return': 0.0,
        'sharpe_ratio': 0.0,
        'max_drawdown': 0.0,
        'profit_factor': 0.0,
        'total_trades': 0,
        'period_days': 0
    }

def compare_performance(backtest: Dict, live: Dict) -> Dict:
    """Compare backtest vs live performance"""
    bt_summary = backtest.get('summary', {})
    
    comparisons = {
        'win_rate': {
            'backtest': bt_summary.get('avg_win_rate', 0),
            'live': live.get('win_rate', 0) * 100,
            'difference': 0.0,
            'status': 'unknown'
        },
        'return': {
            'backtest': bt_summary.get('avg_total_return', 0),
            'live': live.get('total_return', 0) * 100,
            'difference': 0.0,
            'status': 'unknown'
        },
        'sharpe': {
            'backtest': bt_summary.get('avg_sharpe_ratio', 0),
            'live': live.get('sharpe_ratio', 0),
            'difference': 0.0,
            'status': 'unknown'
        },
        'drawdown': {
            'backtest': abs(bt_summary.get('avg_max_drawdown', 0)),
            'live': abs(live.get('max_drawdown', 0)) * 100,
            'difference': 0.0,
            'status': 'unknown'
        },
        'profit_factor': {
            'backtest': bt_summary.get('avg_profit_factor', 0),
            'live': live.get('profit_factor', 0),
            'difference': 0.0,
            'status': 'unknown'
        }
    }
    
    # Calculate differences and status
    for metric, data in comparisons.items():
        data['difference'] = data['live'] - data['backtest']
        diff_pct = abs(data['difference']) / max(abs(data['backtest']), 0.01) * 100
        
        if diff_pct < 10:
            data['status'] = '✅ On Track'
        elif diff_pct < 25:
            data['status'] = '⚠️  Monitor'
        else:
            data['status'] = '❌ Review Needed'
    
    return comparisons

def generate_report(backtest: Dict, live: Dict, comparisons: Dict):
    """Generate performance comparison report"""
    print("\n" + "=" * 70)
    print("📊 V11 Performance Monitoring Report")
    print("=" * 70)
    print(f"\n📅 Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📈 Backtest Date: {backtest.get('timestamp', 'Unknown')}")
    print(f"⏱️  Live Trading Period: {live.get('period_days', 0)} days")
    print(f"📊 Total Trades: {live.get('total_trades', 0)}")
    
    print("\n" + "-" * 70)
    print("METRIC COMPARISON")
    print("-" * 70)
    
    print(f"\n{'Metric':<20} {'Backtest':<15} {'Live':<15} {'Difference':<15} {'Status':<15}")
    print("-" * 70)
    
    for metric, data in comparisons.items():
        metric_name = metric.replace('_', ' ').title()
        print(f"{metric_name:<20} "
              f"{data['backtest']:>10.2f}     "
              f"{data['live']:>10.2f}     "
              f"{data['difference']:>+10.2f}     "
              f"{data['status']:<15}")
    
    print("\n" + "-" * 70)
    print("ANALYSIS")
    print("-" * 70)
    
    # Overall status
    on_track = sum(1 for c in comparisons.values() if '✅' in c['status'])
    monitor = sum(1 for c in comparisons.values() if '⚠️' in c['status'])
    review = sum(1 for c in comparisons.values() if '❌' in c['status'])
    
    print(f"\n✅ On Track: {on_track}/5 metrics")
    print(f"⚠️  Monitor: {monitor}/5 metrics")
    print(f"❌ Review Needed: {review}/5 metrics")
    
    if review > 0:
        print("\n⚠️  WARNING: Some metrics significantly deviate from backtest")
        print("   Consider reviewing strategy parameters or market conditions")
    elif monitor > 0:
        print("\n⚠️  Some metrics need monitoring")
        print("   Continue tracking and adjust if trend continues")
    else:
        print("\n✅ All metrics are on track with backtest expectations")
    
    print("\n" + "=" * 70)

async def main():
    """Main monitoring function"""
    print("🔍 Loading V11 Backtest Expectations...")
    backtest = await load_backtest_expectations()
    
    if not backtest:
        print("❌ Could not load backtest expectations")
        return
    
    print("✅ Backtest expectations loaded")
    
    print("\n📊 Fetching Live Trading Performance...")
    live = get_live_performance()
    
    if live['total_trades'] == 0:
        print("⚠️  No live trades found yet")
        print("   Monitoring will be available once trading begins")
        return
    
    print("✅ Live performance data loaded")
    
    print("\n📈 Comparing Performance...")
    comparisons = compare_performance(backtest, live)
    
    generate_report(backtest, live, comparisons)
    
    # Save report
    reports_dir = Path(__file__).parent.parent / "reports"
    reports_dir.mkdir(exist_ok=True)
    
    report_file = reports_dir / f"v11_performance_monitor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'backtest': backtest,
            'live': live,
            'comparisons': comparisons
        }, f, indent=2)
    
    print(f"\n💾 Report saved to: {report_file}")

if __name__ == '__main__':
    asyncio.run(main())


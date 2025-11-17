#!/usr/bin/env python3
"""
Prop Firm Results Analyzer
Analyzes backtest results and provides optimization recommendations
"""
import sys
import json
from pathlib import Path
from typing import Dict, List, Optional
import logging

sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def analyze_results(results_file: str) -> Dict:
    """Analyze prop firm backtest results"""
    results_path = Path(results_file)
    
    if not results_path.exists():
        logger.error(f"Results file not found: {results_file}")
        return None
    
    with open(results_path, 'r') as f:
        results = json.load(f)
    
    print("\n" + "="*80)
    print("📊 PROP FIRM BACKTEST ANALYSIS")
    print("="*80)
    
    summary = results.get('summary', {})
    all_results = results.get('results', {})
    
    print(f"\n📈 Summary:")
    print(f"   Total Symbols: {summary.get('total_symbols', 0)}")
    print(f"   Successful: {summary.get('successful', 0)}")
    print(f"   Compliant: {summary.get('compliant', 0)}")
    print(f"   Non-Compliant: {summary.get('non_compliant', 0)}")
    
    # Analyze each symbol
    compliant_symbols = []
    non_compliant_symbols = []
    
    for symbol, result in all_results.items():
        if result is None:
            continue
        
        metrics = result.get('metrics', {})
        pf_metrics = result.get('prop_firm_metrics', {})
        compliant = result.get('compliant', False)
        
        if compliant:
            compliant_symbols.append({
                'symbol': symbol,
                'return': metrics.get('total_return_pct', 0),
                'win_rate': metrics.get('win_rate_pct', 0),
                'sharpe': metrics.get('sharpe_ratio', 0),
                'drawdown': metrics.get('max_drawdown_pct', 0)
            })
        else:
            non_compliant_symbols.append({
                'symbol': symbol,
                'return': metrics.get('total_return_pct', 0),
                'win_rate': metrics.get('win_rate_pct', 0),
                'sharpe': metrics.get('sharpe_ratio', 0),
                'drawdown': metrics.get('max_drawdown_pct', 0),
                'drawdown_breaches': pf_metrics.get('drawdown_breaches', 0),
                'daily_loss_breaches': pf_metrics.get('daily_loss_breaches', 0),
                'trading_halted': pf_metrics.get('trading_halted', False)
            })
    
    # Print compliant symbols
    if compliant_symbols:
        print(f"\n✅ COMPLIANT SYMBOLS ({len(compliant_symbols)}):")
        print(f"{'Symbol':<10} {'Return':<10} {'Win Rate':<10} {'Sharpe':<10} {'Drawdown':<10}")
        print("-" * 60)
        for s in sorted(compliant_symbols, key=lambda x: x['return'], reverse=True):
            print(f"{s['symbol']:<10} {s['return']:>8.2f}% {s['win_rate']:>8.2f}% {s['sharpe']:>8.2f} {s['drawdown']:>8.2f}%")
    
    # Print non-compliant symbols
    if non_compliant_symbols:
        print(f"\n❌ NON-COMPLIANT SYMBOLS ({len(non_compliant_symbols)}):")
        print(f"{'Symbol':<10} {'Return':<10} {'Win Rate':<10} {'Breaches':<15} {'Halted':<10}")
        print("-" * 70)
        for s in non_compliant_symbols:
            breaches = f"DD:{s['drawdown_breaches']} DL:{s['daily_loss_breaches']}"
            halted = "YES" if s['trading_halted'] else "NO"
            print(f"{s['symbol']:<10} {s['return']:>8.2f}% {s['win_rate']:>8.2f}% {breaches:<15} {halted:<10}")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    
    if non_compliant_symbols:
        print(f"   ⚠️  {len(non_compliant_symbols)} symbols failed compliance")
        print(f"   → Increase confidence threshold to 85%+")
        print(f"   → Reduce position size to 5% max")
        print(f"   → Tighten stop losses")
        print(f"   → Reduce max positions to 3")
    else:
        print(f"   ✅ All symbols are compliant!")
        print(f"   → Consider optimizing for higher returns")
        print(f"   → Test with more symbols")
        print(f"   → Validate with paper trading")
    
    # Best performers
    if compliant_symbols:
        best = max(compliant_symbols, key=lambda x: x['return'])
        print(f"\n🏆 BEST PERFORMER:")
        print(f"   Symbol: {best['symbol']}")
        print(f"   Return: {best['return']:.2f}%")
        print(f"   Win Rate: {best['win_rate']:.2f}%")
        print(f"   Sharpe: {best['sharpe']:.2f}")
    
    print("\n" + "="*80)
    
    return {
        'compliant': compliant_symbols,
        'non_compliant': non_compliant_symbols,
        'summary': summary
    }


def find_latest_results() -> Optional[str]:
    """Find the latest results file"""
    reports_dir = Path(__file__).parent.parent / "reports"
    if not reports_dir.exists():
        return None
    
    results_files = list(reports_dir.glob("prop_firm_backtest_*.json"))
    if not results_files:
        return None
    
    # Return most recent
    return str(max(results_files, key=lambda p: p.stat().st_mtime))


def main():
    """Main function"""
    # Try to find latest results
    latest = find_latest_results()
    
    if latest:
        print(f"📄 Using latest results: {latest}")
        analyze_results(latest)
    else:
        print("❌ No results files found")
        print("   Run: python scripts/run_prop_firm_backtest.py")
        
        # Check if user provided file
        if len(sys.argv) > 1:
            analyze_results(sys.argv[1])


if __name__ == "__main__":
    main()


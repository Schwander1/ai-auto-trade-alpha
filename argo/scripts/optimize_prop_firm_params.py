#!/usr/bin/env python3
"""
Prop Firm Parameter Optimizer
Tests different parameter combinations to find optimal settings
"""
import sys
import asyncio
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import logging

sys.path.insert(0, str(Path(__file__).parent.parent))

from argo.backtest.prop_firm_backtester import PropFirmBacktester

logging.basicConfig(level=logging.WARNING)  # Reduce logging for optimization
logger = logging.getLogger(__name__)


async def test_configuration(
    symbol: str,
    min_confidence: float,
    max_position_size: float,
    max_positions: int
) -> Dict:
    """Test a specific configuration"""
    backtester = PropFirmBacktester(
        initial_capital=25000.0,
        min_confidence=min_confidence,
        max_position_size_pct=max_position_size,
        max_positions=max_positions
    )
    
    metrics = await backtester.run_backtest(symbol)
    
    if metrics is None:
        return None
    
    report = backtester.get_prop_firm_report()
    
    return {
        'symbol': symbol,
        'min_confidence': min_confidence,
        'max_position_size': max_position_size,
        'max_positions': max_positions,
        'total_return': metrics.total_return_pct,
        'win_rate': metrics.win_rate_pct,
        'sharpe': metrics.sharpe_ratio,
        'max_drawdown': metrics.max_drawdown_pct,
        'total_trades': metrics.total_trades,
        'compliant': report['drawdown_compliant'] and report['daily_loss_compliant'],
        'drawdown_breaches': report['drawdown_breaches'],
        'daily_loss_breaches': report['daily_loss_breaches']
    }


async def optimize_parameters(symbol: str = "SPY"):
    """Optimize parameters for prop firm trading"""
    print("\n" + "="*80)
    print(f"🔧 PROP FIRM PARAMETER OPTIMIZATION - {symbol}")
    print("="*80)
    
    # Test configurations
    configurations = [
        # (min_confidence, max_position_size, max_positions)
        (80.0, 10.0, 5),   # Baseline
        (85.0, 10.0, 5),   # Higher confidence
        (80.0, 5.0, 5),    # Smaller positions
        (85.0, 5.0, 5),    # Higher confidence + smaller positions
        (80.0, 10.0, 3),   # Fewer positions
        (85.0, 5.0, 3),    # Conservative
        (90.0, 5.0, 3),    # Very conservative
    ]
    
    results = []
    
    print(f"\n📊 Testing {len(configurations)} configurations...\n")
    
    for i, (conf, pos_size, max_pos) in enumerate(configurations, 1):
        print(f"[{i}/{len(configurations)}] Testing: conf={conf}%, pos={pos_size}%, max_pos={max_pos}")
        
        result = await test_configuration(symbol, conf, pos_size, max_pos)
        
        if result:
            results.append(result)
            status = "✅" if result['compliant'] else "❌"
            print(f"   {status} Return: {result['total_return']:+.2f}%, Win Rate: {result['win_rate']:.2f}%, Trades: {result['total_trades']}")
        else:
            print(f"   ❌ Failed")
    
    # Analyze results
    print("\n" + "="*80)
    print("📊 OPTIMIZATION RESULTS")
    print("="*80)
    
    compliant = [r for r in results if r['compliant']]
    non_compliant = [r for r in results if not r['compliant']]
    
    if compliant:
        print(f"\n✅ COMPLIANT CONFIGURATIONS ({len(compliant)}):")
        print(f"{'Conf':<8} {'Pos%':<8} {'MaxPos':<8} {'Return':<10} {'Win%':<8} {'Sharpe':<8} {'Trades':<8}")
        print("-" * 70)
        
        for r in sorted(compliant, key=lambda x: x['total_return'], reverse=True):
            print(f"{r['min_confidence']:<8.0f} {r['max_position_size']:<8.0f} {r['max_positions']:<8} "
                  f"{r['total_return']:>8.2f}% {r['win_rate']:>6.2f}% {r['sharpe']:>6.2f} {r['total_trades']:>8}")
        
        # Best configuration
        best = max(compliant, key=lambda x: x['total_return'])
        print(f"\n🏆 BEST CONFIGURATION:")
        print(f"   Confidence: {best['min_confidence']}%")
        print(f"   Position Size: {best['max_position_size']}%")
        print(f"   Max Positions: {best['max_positions']}")
        print(f"   Return: {best['total_return']:.2f}%")
        print(f"   Win Rate: {best['win_rate']:.2f}%")
        print(f"   Sharpe: {best['sharpe']:.2f}")
        print(f"   Trades: {best['total_trades']}")
    else:
        print("\n❌ NO COMPLIANT CONFIGURATIONS FOUND")
        print("   → Strategy may be too aggressive for prop firm constraints")
        print("   → Consider:")
        print("     - Increasing confidence threshold to 90%+")
        print("     - Reducing position size to 3-5%")
        print("     - Limiting to 1-2 positions")
        print("     - Reviewing signal quality")
    
    if non_compliant:
        print(f"\n❌ NON-COMPLIANT CONFIGURATIONS ({len(non_compliant)}):")
        for r in non_compliant:
            print(f"   Conf={r['min_confidence']}%, Pos={r['max_position_size']}%, "
                  f"Breaches: DD={r['drawdown_breaches']}, DL={r['daily_loss_breaches']}")
    
    print("\n" + "="*80)
    
    return results


async def main():
    """Main function"""
    symbol = sys.argv[1] if len(sys.argv) > 1 else "SPY"
    await optimize_parameters(symbol)


if __name__ == "__main__":
    asyncio.run(main())


#!/usr/bin/env python3
"""
Quick Prop Firm Backtest
Fast single-symbol test to get initial results
"""
import sys
import asyncio
from pathlib import Path
from datetime import datetime
import logging

sys.path.insert(0, str(Path(__file__).parent.parent))

from argo.backtest.prop_firm_backtester import PropFirmBacktester

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def quick_test():
    """Quick test with SPY"""
    print("\n" + "="*80)
    print("🚀 QUICK PROP FIRM BACKTEST - SPY")
    print("="*80)
    
    backtester = PropFirmBacktester(
        initial_capital=25000.0,
        min_confidence=80.0
    )
    
    print("\n📊 Running backtest...")
    metrics = await backtester.run_backtest("SPY")
    
    if metrics:
        report = backtester.get_prop_firm_report()
        
        print("\n" + "="*80)
        print("📊 RESULTS")
        print("="*80)
        print(f"\n✅ Performance:")
        print(f"   Total Return: {metrics.total_return_pct:+.2f}%")
        print(f"   Win Rate: {metrics.win_rate_pct:.2f}%")
        print(f"   Sharpe Ratio: {metrics.sharpe_ratio:.2f}")
        print(f"   Max Drawdown: {metrics.max_drawdown_pct:.2f}%")
        print(f"   Total Trades: {metrics.total_trades}")
        
        print(f"\n🚨 Prop Firm Compliance:")
        print(f"   Drawdown Compliant: {'✅' if report['drawdown_compliant'] else '❌'} ({report['final_drawdown_pct']:.2f}% / {report['max_drawdown_limit']}%)")
        print(f"   Daily Loss Compliant: {'✅' if report['daily_loss_compliant'] else '❌'}")
        print(f"   Trading Halted: {'❌ YES' if report['trading_halted'] else '✅ NO'}")
        print(f"   Breaches: {report['drawdown_breaches']} drawdown, {report['daily_loss_breaches']} daily loss")
        
        print(f"\n📅 Daily Stats:")
        print(f"   Trading Days: {report['total_trading_days']}")
        print(f"   Profitable Days: {report['profitable_days']}")
        print(f"   Avg Daily Return: {report['avg_daily_return_pct']:+.2f}%")
        
        print(f"\n✅ Overall: {'COMPLIANT' if report['drawdown_compliant'] and report['daily_loss_compliant'] else 'NON-COMPLIANT'}")
    else:
        print("\n❌ Backtest failed")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    asyncio.run(quick_test())


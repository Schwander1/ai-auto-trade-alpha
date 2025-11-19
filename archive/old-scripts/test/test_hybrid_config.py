#!/usr/bin/env python3
"""
Test Hybrid Prop Firm Configuration
Tests the recommended hybrid configuration with tighter stop losses
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


async def test_hybrid_config(symbol: str = "SPY"):
    """Test hybrid configuration"""
    print("\n" + "="*80)
    print(f"🔧 TESTING HYBRID PROP FIRM CONFIGURATION - {symbol}")
    print("="*80)
    
    # Hybrid configuration (recommended from optimization)
    backtester = PropFirmBacktester(
        initial_capital=25000.0,
        min_confidence=82.0,        # Slightly higher than 80%
        max_position_size_pct=3.0,  # Reduced from 10%
        max_positions=3,            # Reduced from 5
    )
    
    print(f"\n📊 Configuration:")
    print(f"   Confidence: 82.0%")
    print(f"   Position Size: 3.0%")
    print(f"   Max Positions: 3")
    print(f"   Initial Capital: $25,000")
    
    print(f"\n🚀 Running backtest...")
    metrics = await backtester.run_backtest(symbol)
    
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
        print(f"   Winning Trades: {metrics.winning_trades}")
        print(f"   Losing Trades: {metrics.losing_trades}")
        
        print(f"\n🚨 Prop Firm Compliance:")
        print(f"   Drawdown Compliant: {'✅' if report['drawdown_compliant'] else '❌'} "
              f"({report['final_drawdown_pct']:.2f}% / {report['max_drawdown_limit']}%)")
        print(f"   Daily Loss Compliant: {'✅' if report['daily_loss_compliant'] else '❌'}")
        print(f"   Trading Halted: {'❌ YES' if report['trading_halted'] else '✅ NO'}")
        print(f"   Drawdown Breaches: {report['drawdown_breaches']}")
        print(f"   Daily Loss Breaches: {report['daily_loss_breaches']}")
        
        if report['daily_loss_breaches'] > 0:
            print(f"   ⚠️  Max Daily Loss: {report['max_daily_loss_pct']:.2f}% (limit: {report['daily_loss_limit']}%)")
        
        print(f"\n📅 Daily Statistics:")
        print(f"   Total Trading Days: {report['total_trading_days']}")
        print(f"   Profitable Days: {report['profitable_days']}")
        print(f"   Losing Days: {report['losing_days']}")
        print(f"   Avg Daily Return: {report['avg_daily_return_pct']:+.2f}%")
        
        print(f"\n💰 Equity:")
        print(f"   Initial Capital: ${report['initial_capital']:,.2f}")
        print(f"   Final Equity: ${report['final_equity']:,.2f}")
        print(f"   Total Return: {report['total_return_pct']:+.2f}%")
        
        compliant = report['drawdown_compliant'] and report['daily_loss_compliant'] and not report['trading_halted']
        
        print(f"\n{'='*80}")
        if compliant:
            print("✅ OVERALL: COMPLIANT - Ready for paper trading!")
        else:
            print("❌ OVERALL: NON-COMPLIANT - Needs further optimization")
            if report['daily_loss_breaches'] > 0:
                print("   → Issue: Daily loss breaches")
                print("   → Solution: Implement tighter stop losses (1.5% max)")
            if report['drawdown_breaches'] > 0:
                print("   → Issue: Drawdown breaches")
                print("   → Solution: Reduce position size further")
        print("="*80)
        
        return {
            'compliant': compliant,
            'metrics': metrics,
            'report': report
        }
    else:
        print("\n❌ Backtest failed")
        return None


async def test_multiple_symbols():
    """Test hybrid configuration with multiple symbols"""
    print("\n" + "="*80)
    print("🚀 TESTING HYBRID CONFIGURATION - MULTIPLE SYMBOLS")
    print("="*80)
    
    symbols = ["SPY", "QQQ", "AAPL"]
    results = {}
    
    for symbol in symbols:
        print(f"\n{'='*80}")
        print(f"📈 Testing {symbol}")
        print(f"{'='*80}")
        
        result = await test_hybrid_config(symbol)
        results[symbol] = result
        
        if result:
            status = "✅ COMPLIANT" if result['compliant'] else "❌ NON-COMPLIANT"
            print(f"\n{symbol}: {status}")
    
    # Summary
    print("\n" + "="*80)
    print("📊 MULTI-SYMBOL SUMMARY")
    print("="*80)
    
    compliant_count = sum(1 for r in results.values() if r and r['compliant'])
    total_count = len([r for r in results.values() if r is not None])
    
    print(f"\n   Total Symbols: {len(symbols)}")
    print(f"   Successful: {total_count}")
    print(f"   Compliant: {compliant_count}")
    print(f"   Non-Compliant: {total_count - compliant_count}")
    
    print(f"\n📈 Performance by Symbol:")
    for symbol, result in results.items():
        if result:
            metrics = result['metrics']
            status = "✅" if result['compliant'] else "❌"
            print(f"   {status} {symbol}: {metrics.total_return_pct:+.2f}% return, "
                  f"{metrics.win_rate_pct:.2f}% win rate, {metrics.total_trades} trades")
    
    print("\n" + "="*80)
    
    return results


async def main():
    """Main function"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--multi":
        await test_multiple_symbols()
    else:
        symbol = sys.argv[1] if len(sys.argv) > 1 else "SPY"
        await test_hybrid_config(symbol)


if __name__ == "__main__":
    asyncio.run(main())


#!/usr/bin/env python3
"""
Prop Firm Backtest Runner
Runs comprehensive backtests with prop firm constraints
"""
import sys
import asyncio
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

sys.path.insert(0, str(Path(__file__).parent.parent))

from argo.backtest.prop_firm_backtester import PropFirmBacktester
from argo.backtest.results_storage import ResultsStorage

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def run_prop_firm_backtest(
    symbol: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    min_confidence: float = 80.0,
    initial_capital: float = 25000.0
) -> Dict:
    """
    Run prop firm backtest for a single symbol
    
    Args:
        symbol: Trading symbol
        start_date: Start date (default: 1 year ago)
        end_date: End date (default: today)
        min_confidence: Minimum confidence threshold (default: 80%)
        initial_capital: Initial capital (default: $25,000)
    
    Returns:
        Dictionary with backtest results and prop firm metrics
    """
    logger.info(f"🚀 Starting prop firm backtest for {symbol}")
    
    # Default date range: 1 year
    if end_date is None:
        end_date = datetime.now()
    if start_date is None:
        start_date = end_date - timedelta(days=365)
    
    # Initialize backtester
    backtester = PropFirmBacktester(
        initial_capital=initial_capital,
        min_confidence=min_confidence
    )
    
    # Run backtest
    metrics = await backtester.run_backtest(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        min_confidence=min_confidence
    )
    
    if metrics is None:
        logger.error(f"❌ Backtest failed for {symbol}")
        return None
    
    # Get prop firm report
    prop_firm_report = backtester.get_prop_firm_report()
    
    # Combine results
    results = {
        'symbol': symbol,
        'start_date': start_date.isoformat() if start_date else None,
        'end_date': end_date.isoformat() if end_date else None,
        'initial_capital': initial_capital,
        'min_confidence': min_confidence,
        'metrics': {
            'total_return_pct': metrics.total_return_pct,
            'annualized_return_pct': metrics.annualized_return_pct,
            'sharpe_ratio': metrics.sharpe_ratio,
            'sortino_ratio': metrics.sortino_ratio,
            'max_drawdown_pct': metrics.max_drawdown_pct,
            'win_rate_pct': metrics.win_rate_pct,
            'profit_factor': metrics.profit_factor,
            'total_trades': metrics.total_trades,
            'winning_trades': metrics.winning_trades,
            'losing_trades': metrics.losing_trades,
            'avg_win_pct': metrics.avg_win_pct,
            'avg_loss_pct': metrics.avg_loss_pct
        },
        'prop_firm_metrics': prop_firm_report,
        'compliant': (
            prop_firm_report['drawdown_compliant'] and
            prop_firm_report['daily_loss_compliant'] and
            not prop_firm_report['trading_halted']
        )
    }
    
    return results


async def run_multi_symbol_backtest(
    symbols: List[str],
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    min_confidence: float = 80.0,
    initial_capital: float = 25000.0
) -> Dict:
    """
    Run prop firm backtests for multiple symbols
    
    Args:
        symbols: List of trading symbols
        start_date: Start date
        end_date: End date
        min_confidence: Minimum confidence threshold
        initial_capital: Initial capital per symbol
    
    Returns:
        Dictionary with results for all symbols
    """
    logger.info(f"🚀 Starting multi-symbol prop firm backtest")
    logger.info(f"   Symbols: {symbols}")
    logger.info(f"   Confidence threshold: {min_confidence}%")
    logger.info(f"   Initial capital: ${initial_capital:,.2f}")
    
    all_results = {}
    compliant_count = 0
    
    for symbol in symbols:
        logger.info(f"\n{'='*70}")
        logger.info(f"📈 Testing {symbol}")
        logger.info(f"{'='*70}")
        
        try:
            results = await run_prop_firm_backtest(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                min_confidence=min_confidence,
                initial_capital=initial_capital
            )
            
            if results:
                all_results[symbol] = results
                if results['compliant']:
                    compliant_count += 1
                
                # Print summary
                logger.info(f"\n✅ {symbol} Results:")
                logger.info(f"   Total Return: {results['metrics']['total_return_pct']:.2f}%")
                logger.info(f"   Win Rate: {results['metrics']['win_rate_pct']:.2f}%")
                logger.info(f"   Max Drawdown: {results['metrics']['max_drawdown_pct']:.2f}%")
                logger.info(f"   Sharpe Ratio: {results['metrics']['sharpe_ratio']:.2f}")
                logger.info(f"   Prop Firm Compliant: {'✅' if results['compliant'] else '❌'}")
                logger.info(f"   Drawdown Compliant: {'✅' if results['prop_firm_metrics']['drawdown_compliant'] else '❌'}")
                logger.info(f"   Daily Loss Compliant: {'✅' if results['prop_firm_metrics']['daily_loss_compliant'] else '❌'}")
            else:
                logger.error(f"❌ Failed to get results for {symbol}")
                all_results[symbol] = None
                
        except Exception as e:
            logger.error(f"❌ Error testing {symbol}: {e}", exc_info=True)
            all_results[symbol] = None
    
    # Summary
    logger.info(f"\n{'='*70}")
    logger.info(f"📊 PROP FIRM BACKTEST SUMMARY")
    logger.info(f"{'='*70}")
    logger.info(f"   Total Symbols: {len(symbols)}")
    logger.info(f"   Successful: {len([r for r in all_results.values() if r is not None])}")
    logger.info(f"   Compliant: {compliant_count}")
    logger.info(f"   Non-Compliant: {len(symbols) - compliant_count}")
    
    return {
        'symbols': symbols,
        'results': all_results,
        'summary': {
            'total_symbols': len(symbols),
            'successful': len([r for r in all_results.values() if r is not None]),
            'compliant': compliant_count,
            'non_compliant': len(symbols) - compliant_count
        }
    }


def save_results(results: Dict, output_file: str = None):
    """Save backtest results to JSON file"""
    if output_file is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"argo/reports/prop_firm_backtest_{timestamp}.json"
    
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info(f"💾 Results saved to {output_path}")
    return output_path


def print_detailed_report(results: Dict):
    """Print detailed prop firm backtest report"""
    print("\n" + "="*80)
    print("📊 PROP FIRM BACKTEST DETAILED REPORT")
    print("="*80)
    
    for symbol, result in results['results'].items():
        if result is None:
            print(f"\n❌ {symbol}: Failed")
            continue
        
        print(f"\n{'='*80}")
        print(f"📈 {symbol}")
        print(f"{'='*80}")
        
        # Performance metrics
        metrics = result['metrics']
        print(f"\n📊 Performance Metrics:")
        print(f"   Total Return: {metrics['total_return_pct']:+.2f}%")
        print(f"   Annualized Return: {metrics['annualized_return_pct']:+.2f}%")
        print(f"   Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
        print(f"   Sortino Ratio: {metrics['sortino_ratio']:.2f}")
        print(f"   Max Drawdown: {metrics['max_drawdown_pct']:.2f}%")
        print(f"   Win Rate: {metrics['win_rate_pct']:.2f}%")
        print(f"   Profit Factor: {metrics['profit_factor']:.2f}")
        print(f"   Total Trades: {metrics['total_trades']}")
        print(f"   Winning Trades: {metrics['winning_trades']}")
        print(f"   Losing Trades: {metrics['losing_trades']}")
        
        # Prop firm metrics
        pf_metrics = result['prop_firm_metrics']
        print(f"\n🚨 Prop Firm Compliance:")
        print(f"   Drawdown Compliant: {'✅' if pf_metrics['drawdown_compliant'] else '❌'}")
        print(f"      Final Drawdown: {pf_metrics['final_drawdown_pct']:.2f}% (limit: {pf_metrics['max_drawdown_limit']}%)")
        print(f"      Drawdown Breaches: {pf_metrics['drawdown_breaches']}")
        print(f"   Daily Loss Compliant: {'✅' if pf_metrics['daily_loss_compliant'] else '❌'}")
        print(f"      Max Daily Loss: {pf_metrics['max_daily_loss_pct']:.2f}% (limit: {pf_metrics['daily_loss_limit']}%)")
        print(f"      Daily Loss Breaches: {pf_metrics['daily_loss_breaches']}")
        print(f"   Trading Halted: {'❌ YES' if pf_metrics['trading_halted'] else '✅ NO'}")
        if pf_metrics['halt_reason']:
            print(f"      Reason: {pf_metrics['halt_reason']}")
        
        print(f"\n📅 Daily Statistics:")
        print(f"   Total Trading Days: {pf_metrics['total_trading_days']}")
        print(f"   Profitable Days: {pf_metrics['profitable_days']}")
        print(f"   Losing Days: {pf_metrics['losing_days']}")
        print(f"   Avg Daily Return: {pf_metrics['avg_daily_return_pct']:+.2f}%")
        
        print(f"\n⚙️  Configuration:")
        print(f"   Initial Capital: ${pf_metrics['initial_capital']:,.2f}")
        print(f"   Final Equity: ${pf_metrics['final_equity']:,.2f}")
        print(f"   Min Confidence: {pf_metrics['min_confidence']}%")
        print(f"   Max Position Size: {pf_metrics['max_position_size_pct']}%")
        print(f"   Max Positions: {pf_metrics['max_positions']}")
        
        print(f"\n✅ Overall Compliance: {'✅ COMPLIANT' if result['compliant'] else '❌ NON-COMPLIANT'}")


async def main():
    """Main function"""
    print("\n" + "="*80)
    print("🚀 PROP FIRM BACKTEST RUNNER")
    print("="*80)
    print()
    
    # Test symbols (focus on liquid, high-volume instruments)
    symbols = [
        "SPY",      # S&P 500 ETF (very liquid)
        "QQQ",      # Nasdaq ETF (very liquid)
        "AAPL",     # Apple (high volume)
        "NVDA",     # NVIDIA (high volume)
        # "BTC-USD",  # Bitcoin (crypto)
        # "ETH-USD",  # Ethereum (crypto)
    ]
    
    # Date range: Use None to get all available data (or specify wider range)
    # For prop firm backtesting, we want sufficient historical data
    end_date = None  # Use all available data up to now
    start_date = None  # Use all available data
    
    # Run backtests
    results = await run_multi_symbol_backtest(
        symbols=symbols,
        start_date=start_date,
        end_date=end_date,
        min_confidence=80.0,  # 80%+ confidence threshold
        initial_capital=25000.0  # $25,000 prop firm account
    )
    
    # Save results
    output_file = save_results(results)
    
    # Print detailed report
    print_detailed_report(results)
    
    print("\n" + "="*80)
    print("✅ PROP FIRM BACKTEST COMPLETE")
    print("="*80)
    print(f"📄 Results saved to: {output_file}")
    print()


if __name__ == "__main__":
    asyncio.run(main())


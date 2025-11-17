#!/usr/bin/env python3
"""
Comprehensive Backtest with Full Data Tracking
Tracks all metrics, iterations, and detailed trade data for complete analysis
"""
import sys
import asyncio
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import logging
import copy

sys.path.insert(0, str(Path(__file__).parent.parent))

from argo.backtest.strategy_backtester import StrategyBacktester
from argo.backtest.data_manager import DataManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Symbols to test
SYMBOLS = [
    "AAPL", "NVDA", "TSLA", "MSFT", "GOOGL", "META", "AMD", "AMZN",
    "SPY", "QQQ",
    "BTC-USD", "ETH-USD"
]

async def run_comprehensive_tracked_backtest(iteration_name: str = "refined_v2"):
    """Run backtest with comprehensive data tracking"""
    
    timestamp = datetime.now().isoformat()
    iteration_id = f"{iteration_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    print('\n' + '='*80)
    print(f'🚀 COMPREHENSIVE BACKTEST - {iteration_name.upper()}')
    print('='*80)
    print(f'Iteration ID: {iteration_id}')
    print(f'Timestamp: {timestamp}')
    print(f'Testing {len(SYMBOLS)} symbols with full data tracking...')
    print('='*80 + '\n')
    
    # Initialize backtester with enhanced cost model
    backtester = StrategyBacktester(
        initial_capital=100000,
        use_enhanced_cost_model=True  # Use EnhancedTransactionCostModel
    )
    
    all_results = {
        'iteration_id': iteration_id,
        'iteration_name': iteration_name,
        'timestamp': timestamp,
        'strategy_config': {
            'min_confidence': 60.0,  # Raised from 55% to 60% for better win rate
            'initial_capital': 100000,
            'symbol_specific_optimizations': True,
            'adaptive_stops': True,
            'trailing_stops': True,
            'position_sizing': True,
            'volume_confirmation': True,  # Enabled for better signal quality
            'enhanced_cost_model': True,  # Using EnhancedTransactionCostModel
            'tighter_stops': True,  # Tighter stops for drawdown reduction
            'optimized_position_sizing': True,  # Optimized to 9% base (from 8%)
            'portfolio_risk_limits': True,  # Portfolio-level drawdown limits
            'symbol_specific_thresholds': True,  # Symbol-specific confidence thresholds
            'dynamic_stop_loss': True,  # Dynamic stop loss tightening based on drawdown
            'fine_tuned_symbol_settings': True,  # Fine-tuned settings for AMD/AMZN/SPY
            'high_confidence_boost': True  # Position size boost for high-confidence signals
        },
        'symbols_tested': SYMBOLS,
        'results': [],
        'summary': {}
    }
    
    detailed_trades = {}
    equity_curves = {}
    
    for i, symbol in enumerate(SYMBOLS, 1):
        print(f'\n[{i}/{len(SYMBOLS)}] 📊 Testing {symbol}...')
        
        try:
            # Reset backtester for each symbol
            backtester.reset()
            
            # Run backtest with updated default confidence
            from argo.backtest.constants import BacktestConstants
            metrics = await backtester.run_backtest(
                symbol=symbol,
                min_confidence=BacktestConstants.DEFAULT_MIN_CONFIDENCE  # Use default 60%
            )
            
            if metrics and metrics.total_trades > 0:
                # Extract all available metrics
                result = {
                    'symbol': symbol,
                    'timestamp': timestamp,
                    'metrics': {
                        'win_rate': float(metrics.win_rate_pct) if metrics.win_rate_pct else 0.0,
                        'total_return': float(metrics.total_return_pct) if metrics.total_return_pct else 0.0,
                        'annualized_return': float(metrics.annualized_return_pct) if metrics.annualized_return_pct else 0.0,
                        'sharpe_ratio': float(metrics.sharpe_ratio) if metrics.sharpe_ratio else 0.0,
                        'sortino_ratio': float(metrics.sortino_ratio) if metrics.sortino_ratio else 0.0,
                        'max_drawdown': float(metrics.max_drawdown_pct) if metrics.max_drawdown_pct else 0.0,
                        'profit_factor': float(metrics.profit_factor) if metrics.profit_factor else 0.0,
                        'total_trades': int(metrics.total_trades) if metrics.total_trades else 0,
                        'winning_trades': int(metrics.winning_trades) if metrics.winning_trades else 0,
                        'losing_trades': int(metrics.losing_trades) if metrics.losing_trades else 0,
                        'avg_win_pct': float(metrics.avg_win_pct) if metrics.avg_win_pct else 0.0,
                        'avg_loss_pct': float(metrics.avg_loss_pct) if metrics.avg_loss_pct else 0.0,
                        'largest_win_pct': float(metrics.largest_win_pct) if metrics.largest_win_pct else 0.0,
                        'largest_loss_pct': float(metrics.largest_loss_pct) if metrics.largest_loss_pct else 0.0,
                    },
                    'trade_details': {
                        'total_trades': len(backtester.trades),
                        'trades': []
                    },
                    'equity_curve': {
                        'data_points': len(backtester.equity_curve),
                        'final_equity': backtester.equity_curve[-1] if backtester.equity_curve else 100000,
                        'peak_equity': max(backtester.equity_curve) if backtester.equity_curve else 100000,
                        'trough_equity': min(backtester.equity_curve) if backtester.equity_curve else 100000
                    }
                }
                
                # Track detailed trade information
                for trade in backtester.trades:
                    if trade.exit_price and trade.pnl is not None:
                        trade_detail = {
                            'entry_date': trade.entry_date.isoformat() if trade.entry_date else None,
                            'exit_date': trade.exit_date.isoformat() if trade.exit_date else None,
                            'entry_price': float(trade.entry_price) if trade.entry_price else 0.0,
                            'exit_price': float(trade.exit_price) if trade.exit_price else 0.0,
                            'quantity': int(trade.quantity) if trade.quantity else 0,
                            'side': trade.side,
                            'pnl': float(trade.pnl) if trade.pnl else 0.0,
                            'pnl_pct': float(trade.pnl_pct) if trade.pnl_pct else 0.0,
                            'confidence': float(trade.confidence) if trade.confidence else 0.0,
                            'days_held': (trade.exit_date - trade.entry_date).days if trade.exit_date and trade.entry_date else 0
                        }
                        result['trade_details']['trades'].append(trade_detail)
                
                # Store equity curve (sample every 10th point to reduce size)
                if backtester.equity_curve:
                    equity_samples = []
                    for idx, equity in enumerate(backtester.equity_curve):
                        if idx % 10 == 0 or idx == len(backtester.equity_curve) - 1:
                            date_str = backtester.dates[idx].isoformat() if idx < len(backtester.dates) else None
                            equity_samples.append({
                                'date': date_str,
                                'equity': float(equity),
                                'index': idx
                            })
                    result['equity_curve']['samples'] = equity_samples
                
                print(f'   ✅ Win Rate: {result["metrics"]["win_rate"]:.2f}%')
                print(f'   ✅ Total Return: {result["metrics"]["total_return"]:.2f}%')
                print(f'   ✅ Sharpe Ratio: {result["metrics"]["sharpe_ratio"]:.2f}')
                print(f'   ✅ Max Drawdown: {result["metrics"]["max_drawdown"]:.2f}%')
                print(f'   ✅ Total Trades: {result["metrics"]["total_trades"]}')
                print(f'   ✅ Profit Factor: {result["metrics"]["profit_factor"]:.2f}')
                
                all_results['results'].append(result)
                detailed_trades[symbol] = result['trade_details']
                equity_curves[symbol] = result['equity_curve']
            else:
                print(f'   ⚠️  No trades generated or backtest failed')
                all_results['results'].append({
                    'symbol': symbol,
                    'timestamp': timestamp,
                    'error': 'No trades generated' if metrics else 'Backtest failed'
                })
                
        except Exception as e:
            logger.error(f"Error backtesting {symbol}: {e}", exc_info=True)
            all_results['results'].append({
                'symbol': symbol,
                'timestamp': timestamp,
                'error': str(e)
            })
    
    # Calculate summary statistics
    valid_results = [r for r in all_results['results'] if 'metrics' in r]
    if valid_results:
        all_results['summary'] = {
            'total_symbols': len(SYMBOLS),
            'successful_symbols': len(valid_results),
            'failed_symbols': len(SYMBOLS) - len(valid_results),
            'avg_win_rate': sum(r['metrics']['win_rate'] for r in valid_results) / len(valid_results),
            'avg_total_return': sum(r['metrics']['total_return'] for r in valid_results) / len(valid_results),
            'avg_sharpe_ratio': sum(r['metrics']['sharpe_ratio'] for r in valid_results) / len(valid_results),
            'avg_max_drawdown': sum(r['metrics']['max_drawdown'] for r in valid_results) / len(valid_results),
            'avg_profit_factor': sum(r['metrics']['profit_factor'] for r in valid_results) / len(valid_results),
            'total_trades_all_symbols': sum(r['metrics']['total_trades'] for r in valid_results),
            'total_winning_trades': sum(r['metrics']['winning_trades'] for r in valid_results),
            'total_losing_trades': sum(r['metrics']['losing_trades'] for r in valid_results),
        }
    
    # Save comprehensive results
    reports_dir = Path(__file__).parent.parent / "reports"
    reports_dir.mkdir(exist_ok=True)
    
    # Save main results
    output_file = reports_dir / f"{iteration_id}_results.json"
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    # Save detailed trades separately (for analysis)
    trades_file = reports_dir / f"{iteration_id}_trades.json"
    with open(trades_file, 'w') as f:
        json.dump(detailed_trades, f, indent=2, ensure_ascii=False)
    
    # Save equity curves separately
    equity_file = reports_dir / f"{iteration_id}_equity_curves.json"
    with open(equity_file, 'w') as f:
        json.dump(equity_curves, f, indent=2, ensure_ascii=False)
    
    # Also update current results for comparison scripts
    current_file = reports_dir / "current_strategy_backtest_results.json"
    with open(current_file, 'w') as f:
        # Convert to format expected by comparison scripts
        comparison_format = {
            'timestamp': timestamp,
            'iteration_id': iteration_id,
            'iteration_name': iteration_name,
            'strategy_version': iteration_name,
            'results': [
                {
                    'symbol': r['symbol'],
                    'config': iteration_name,
                    'method': 'standard',
                    'win_rate': r.get('metrics', {}).get('win_rate', 0),
                    'total_return': r.get('metrics', {}).get('total_return', 0),
                    'sharpe_ratio': r.get('metrics', {}).get('sharpe_ratio', 0),
                    'max_drawdown': r.get('metrics', {}).get('max_drawdown', 0),
                    'total_trades': r.get('metrics', {}).get('total_trades', 0),
                    'profit_factor': r.get('metrics', {}).get('profit_factor', 0),
                    'annualized_return': r.get('metrics', {}).get('annualized_return', 0)
                }
                for r in all_results['results'] if 'metrics' in r
            ]
        }
        json.dump(comparison_format, f, indent=2, ensure_ascii=False)
    
    print(f'\n✅ Results saved:')
    print(f'   Main: {output_file}')
    print(f'   Trades: {trades_file}')
    print(f'   Equity: {equity_file}')
    print(f'   Current: {current_file}')
    
    # Print summary
    if all_results['summary']:
        summary = all_results['summary']
        print(f'\n📊 SUMMARY')
        print('-'*80)
        print(f'Successful Symbols: {summary["successful_symbols"]}/{summary["total_symbols"]}')
        print(f'Avg Win Rate: {summary["avg_win_rate"]:.2f}%')
        print(f'Avg Total Return: {summary["avg_total_return"]:.2f}%')
        print(f'Avg Sharpe Ratio: {summary["avg_sharpe_ratio"]:.2f}')
        print(f'Avg Max Drawdown: {summary["avg_max_drawdown"]:.2f}%')
        print(f'Total Trades: {summary["total_trades_all_symbols"]}')
        print(f'Profit Factor: {summary["avg_profit_factor"]:.2f}')
    
    return all_results

if __name__ == '__main__':
    import sys
    iteration_name = sys.argv[1] if len(sys.argv) > 1 else "refined_v2"
    results = asyncio.run(run_comprehensive_tracked_backtest(iteration_name))
    print('\n✅ Backtest complete!\n')


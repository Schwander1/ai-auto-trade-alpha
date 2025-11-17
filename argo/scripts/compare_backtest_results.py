#!/usr/bin/env python3
"""
Backtest Results Comparison
Compares current strategy results with previous baseline results
"""
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

def load_previous_results() -> Optional[Dict]:
    """Load previous baseline results"""
    prev_file = Path(__file__).parent.parent / "reports" / "comprehensive_backtest_results.json"
    
    if not prev_file.exists():
        print(f"⚠️  Previous results file not found: {prev_file}")
        return None
    
    try:
        with open(prev_file, 'r') as f:
            data = json.load(f)
        return data.get('baseline', [])  # Get baseline results
    except Exception as e:
        print(f"⚠️  Error loading previous results: {e}")
        return None

def load_current_results() -> Optional[List[Dict]]:
    """Load current strategy results"""
    current_file = Path(__file__).parent.parent / "reports" / "current_strategy_backtest_results.json"
    
    if not current_file.exists():
        print(f"⚠️  Current results file not found: {current_file}")
        return None
    
    try:
        with open(current_file, 'r') as f:
            data = json.load(f)
        return data.get('results', [])
    except Exception as e:
        print(f"⚠️  Error loading current results: {e}")
        return None

def compare_results(previous: List[Dict], current: List[Dict]) -> Dict:
    """Compare previous and current results"""
    
    # Create lookup dictionaries by symbol
    prev_by_symbol = {r['symbol']: r for r in previous if 'error' not in r}
    current_by_symbol = {r['symbol']: r for r in current if 'error' not in r}
    
    # Get common symbols
    common_symbols = set(prev_by_symbol.keys()) & set(current_by_symbol.keys())
    
    comparison = {
        'timestamp': datetime.now().isoformat(),
        'symbols_compared': len(common_symbols),
        'symbols': {}
    }
    
    # Overall statistics
    prev_win_rates = [r['win_rate'] for r in prev_by_symbol.values() if 'win_rate' in r]
    current_win_rates = [r['win_rate'] for r in current_by_symbol.values() if 'win_rate' in r]
    
    prev_returns = [r['total_return'] for r in prev_by_symbol.values() if 'total_return' in r]
    current_returns = [r['total_return'] for r in current_by_symbol.values() if 'total_return' in r]
    
    prev_sharpe = [r['sharpe_ratio'] for r in prev_by_symbol.values() if 'sharpe_ratio' in r]
    current_sharpe = [r['sharpe_ratio'] for r in current_by_symbol.values() if 'sharpe_ratio' in r]
    
    comparison['overall'] = {
        'previous': {
            'avg_win_rate': sum(prev_win_rates) / len(prev_win_rates) if prev_win_rates else 0,
            'avg_return': sum(prev_returns) / len(prev_returns) if prev_returns else 0,
            'avg_sharpe': sum(prev_sharpe) / len(prev_sharpe) if prev_sharpe else 0,
            'symbols_tested': len(prev_by_symbol)
        },
        'current': {
            'avg_win_rate': sum(current_win_rates) / len(current_win_rates) if current_win_rates else 0,
            'avg_return': sum(current_returns) / len(current_returns) if current_returns else 0,
            'avg_sharpe': sum(current_sharpe) / len(current_sharpe) if current_sharpe else 0,
            'symbols_tested': len(current_by_symbol)
        }
    }
    
    # Calculate improvements
    if prev_win_rates and current_win_rates:
        comparison['overall']['improvement'] = {
            'win_rate_change': comparison['overall']['current']['avg_win_rate'] - comparison['overall']['previous']['avg_win_rate'],
            'return_change': comparison['overall']['current']['avg_return'] - comparison['overall']['previous']['avg_return'],
            'sharpe_change': comparison['overall']['current']['avg_sharpe'] - comparison['overall']['previous']['avg_sharpe']
        }
    
    # Per-symbol comparison
    for symbol in sorted(common_symbols):
        prev = prev_by_symbol[symbol]
        curr = current_by_symbol[symbol]
        
        comparison['symbols'][symbol] = {
            'previous': {
                'win_rate': prev.get('win_rate', 0),
                'total_return': prev.get('total_return', 0),
                'sharpe_ratio': prev.get('sharpe_ratio', 0),
                'max_drawdown': prev.get('max_drawdown', 0),
                'total_trades': prev.get('total_trades', 0)
            },
            'current': {
                'win_rate': curr.get('win_rate', 0),
                'total_return': curr.get('total_return', 0),
                'sharpe_ratio': curr.get('sharpe_ratio', 0),
                'max_drawdown': curr.get('max_drawdown', 0),
                'total_trades': curr.get('total_trades', 0)
            },
            'change': {
                'win_rate': curr.get('win_rate', 0) - prev.get('win_rate', 0),
                'total_return': curr.get('total_return', 0) - prev.get('total_return', 0),
                'sharpe_ratio': curr.get('sharpe_ratio', 0) - prev.get('sharpe_ratio', 0),
                'max_drawdown': curr.get('max_drawdown', 0) - prev.get('max_drawdown', 0),
                'total_trades': curr.get('total_trades', 0) - prev.get('total_trades', 0)
            }
        }
    
    return comparison

def print_comparison_report(comparison: Dict):
    """Print formatted comparison report"""
    
    print('\n' + '='*80)
    print('📊 BACKTEST RESULTS COMPARISON')
    print('='*80)
    
    # Overall comparison
    overall = comparison.get('overall', {})
    prev = overall.get('previous', {})
    curr = overall.get('current', {})
    improvement = overall.get('improvement', {})
    
    print(f'\n📈 OVERALL PERFORMANCE')
    print('-'*80)
    print(f'{"Metric":<25} {"Previous":<15} {"Current":<15} {"Change":<15}')
    print('-'*80)
    
    if improvement:
        print(f'{"Avg Win Rate (%)":<25} {prev.get("avg_win_rate", 0):>14.2f}% {curr.get("avg_win_rate", 0):>14.2f}% {improvement.get("win_rate_change", 0):>+14.2f}%')
        print(f'{"Avg Total Return (%)":<25} {prev.get("avg_return", 0):>14.2f}% {curr.get("avg_return", 0):>14.2f}% {improvement.get("return_change", 0):>+14.2f}%')
        print(f'{"Avg Sharpe Ratio":<25} {prev.get("avg_sharpe", 0):>14.2f}  {curr.get("avg_sharpe", 0):>14.2f}  {improvement.get("sharpe_change", 0):>+14.2f}')
    
    print(f'\nSymbols Tested: Previous={prev.get("symbols_tested", 0)}, Current={curr.get("symbols_tested", 0)}')
    
    # Per-symbol comparison
    symbols = comparison.get('symbols', {})
    if symbols:
        print(f'\n📊 PER-SYMBOL COMPARISON')
        print('-'*80)
        print(f'{"Symbol":<10} {"Metric":<15} {"Previous":<15} {"Current":<15} {"Change":<15}')
        print('-'*80)
        
        for symbol in sorted(symbols.keys()):
            data = symbols[symbol]
            prev_data = data['previous']
            curr_data = data['current']
            change = data['change']
            
            print(f'\n{symbol}:')
            print(f'  {"Win Rate (%)":<15} {prev_data["win_rate"]:>14.2f}% {curr_data["win_rate"]:>14.2f}% {change["win_rate"]:>+14.2f}%')
            print(f'  {"Return (%)":<15} {prev_data["total_return"]:>14.2f}% {curr_data["total_return"]:>14.2f}% {change["total_return"]:>+14.2f}%')
            print(f'  {"Sharpe Ratio":<15} {prev_data["sharpe_ratio"]:>14.2f}  {curr_data["sharpe_ratio"]:>14.2f}  {change["sharpe_ratio"]:>+14.2f}')
            print(f'  {"Max Drawdown (%)":<15} {prev_data["max_drawdown"]:>14.2f}% {curr_data["max_drawdown"]:>14.2f}% {change["max_drawdown"]:>+14.2f}%')
            print(f'  {"Total Trades":<15} {prev_data["total_trades"]:>14}  {curr_data["total_trades"]:>14}  {change["total_trades"]:>+14}')
    
    print('\n' + '='*80 + '\n')

def main():
    """Main comparison function"""
    
    # Load results
    print("Loading previous baseline results...")
    previous = load_previous_results()
    
    print("Loading current strategy results...")
    current = load_current_results()
    
    if not previous or not current:
        print("❌ Cannot compare: Missing previous or current results")
        print("   Run the backtest first: python scripts/run_current_strategy_backtest.py")
        return
    
    # Compare
    print("Comparing results...")
    comparison = compare_results(previous, current)
    
    # Print report
    print_comparison_report(comparison)
    
    # Save comparison
    output_file = Path(__file__).parent.parent / "reports" / "backtest_comparison.json"
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(comparison, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Comparison saved to: {output_file}\n")

if __name__ == '__main__':
    main()

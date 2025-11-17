#!/usr/bin/env python3
"""
Generate Final Comprehensive Analysis
Compares all iterations: Baseline → Optimized → Refined → Final Refined
"""
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

def load_iteration(file_path: Path) -> Dict:
    """Load iteration results"""
    if not file_path.exists():
        return None
    with open(file_path, 'r') as f:
        return json.load(f)

def extract_metrics(result: Dict) -> Dict:
    """Extract metrics from result (handles different formats)"""
    if 'metrics' in result:
        return result['metrics']
    else:
        return {
            'win_rate': result.get('win_rate', 0),
            'total_return': result.get('total_return', 0),
            'sharpe_ratio': result.get('sharpe_ratio', 0),
            'max_drawdown': result.get('max_drawdown', 0),
            'total_trades': result.get('total_trades', 0),
            'profit_factor': result.get('profit_factor', 0)
        }

def generate_final_analysis():
    """Generate comprehensive final analysis"""
    reports_dir = Path(__file__).parent.parent / "reports"
    
    # Load all iterations
    iterations = {}
    
    # Baseline
    baseline_file = reports_dir / "comprehensive_backtest_results.json"
    if baseline_file.exists():
        data = load_iteration(baseline_file)
        if data:
            iterations['baseline'] = {
                'name': 'Baseline',
                'timestamp': 'baseline',
                'results': data.get('baseline', [])
            }
    
    # Find all tracked iterations
    for file in sorted(reports_dir.glob("*_results.json")):
        if file.name.startswith(('refined_', 'optimized_', 'final_')):
            data = load_iteration(file)
            if data:
                iter_name = data.get('iteration_name', file.stem)
                iterations[iter_name] = {
                    'name': iter_name.replace('_', ' ').title(),
                    'timestamp': data.get('timestamp', 'unknown'),
                    'iteration_id': data.get('iteration_id', file.stem),
                    'results': data.get('results', []),
                    'summary': data.get('summary', {})
                }
    
    # Current (latest)
    current_file = reports_dir / "current_strategy_backtest_results.json"
    if current_file.exists():
        data = load_iteration(current_file)
        if data:
            iter_name = data.get('iteration_name', 'current')
            if iter_name not in iterations:
                iterations[iter_name] = {
                    'name': iter_name.replace('_', ' ').title(),
                    'timestamp': data.get('timestamp', 'unknown'),
                    'results': data.get('results', [])
                }
    
    if not iterations:
        print("❌ No iterations found")
        return
    
    # Build comparison
    analysis = {
        'generated_at': datetime.now().isoformat(),
        'iterations': list(iterations.keys()),
        'overall_comparison': {},
        'symbol_comparison': {},
        'improvements': {}
    }
    
    # Overall comparison
    for iter_name, iter_data in iterations.items():
        results = iter_data.get('results', [])
        valid_results = [r for r in results if 'error' not in r]
        
        if valid_results:
            metrics_list = [extract_metrics(r) for r in valid_results]
            analysis['overall_comparison'][iter_name] = {
                'avg_win_rate': sum(m.get('win_rate', 0) for m in metrics_list) / len(metrics_list),
                'avg_total_return': sum(m.get('total_return', 0) for m in metrics_list) / len(metrics_list),
                'avg_sharpe_ratio': sum(m.get('sharpe_ratio', 0) for m in metrics_list) / len(metrics_list),
                'avg_max_drawdown': sum(m.get('max_drawdown', 0) for m in metrics_list) / len(metrics_list),
                'avg_profit_factor': sum(m.get('profit_factor', 0) for m in metrics_list) / len(metrics_list),
                'total_trades': sum(m.get('total_trades', 0) for m in metrics_list),
                'symbols_tested': len(valid_results)
            }
    
    # Symbol comparison
    symbol_data = {}
    for iter_name, iter_data in iterations.items():
        results = iter_data.get('results', [])
        for result in results:
            if 'error' not in result:
                symbol = result.get('symbol')
                if symbol:
                    if symbol not in symbol_data:
                        symbol_data[symbol] = {}
                    symbol_data[symbol][iter_name] = extract_metrics(result)
    
    analysis['symbol_comparison'] = symbol_data
    
    # Calculate improvements
    if 'baseline' in iterations and len(iterations) > 1:
        baseline_comp = analysis['overall_comparison'].get('baseline', {})
        latest_iter = max([k for k in iterations.keys() if k != 'baseline'], 
                         key=lambda k: iterations[k].get('timestamp', ''))
        latest_comp = analysis['overall_comparison'].get(latest_iter, {})
        
        if baseline_comp and latest_comp:
            analysis['improvements'] = {
                'win_rate_change': latest_comp['avg_win_rate'] - baseline_comp['avg_win_rate'],
                'return_change': latest_comp['avg_total_return'] - baseline_comp['avg_total_return'],
                'sharpe_change': latest_comp['avg_sharpe_ratio'] - baseline_comp['avg_sharpe_ratio'],
                'drawdown_change': latest_comp['avg_max_drawdown'] - baseline_comp['avg_max_drawdown'],
                'profit_factor_change': latest_comp['avg_profit_factor'] - baseline_comp['avg_profit_factor'],
                'trades_change': latest_comp['total_trades'] - baseline_comp['total_trades']
            }
    
    # Save analysis
    output_file = reports_dir / "FINAL_COMPREHENSIVE_ANALYSIS.json"
    with open(output_file, 'w') as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print('\n' + '='*100)
    print('📊 FINAL COMPREHENSIVE ANALYSIS - ALL ITERATIONS')
    print('='*100)
    
    print(f'\n📈 OVERALL PERFORMANCE EVOLUTION')
    print('-'*100)
    print(f'{"Iteration":<20} {"Avg Return":<15} {"Avg Win Rate":<15} {"Avg Sharpe":<15} {"Profit Factor":<15} {"Trades":<10}')
    print('-'*100)
    
    for iter_name in sorted(iterations.keys()):
        comp = analysis['overall_comparison'].get(iter_name, {})
        if comp:
            print(f'{iter_name:<20} {comp["avg_total_return"]:>14.2f}% {comp["avg_win_rate"]:>14.2f}% '
                  f'{comp["avg_sharpe_ratio"]:>14.2f}  {comp["avg_profit_factor"]:>14.2f}  {comp["total_trades"]:>9}')
    
    if analysis['improvements']:
        print(f'\n🎯 FINAL IMPROVEMENTS (Latest vs Baseline)')
        print('-'*100)
        imp = analysis['improvements']
        print(f'Return Change: {imp["return_change"]:+.2f}%')
        print(f'Win Rate Change: {imp["win_rate_change"]:+.2f}%')
        print(f'Sharpe Change: {imp["sharpe_change"]:+.2f}')
        print(f'Profit Factor Change: {imp["profit_factor_change"]:+.2f}')
        print(f'Drawdown Change: {imp["drawdown_change"]:+.2f}%')
    
    # Top symbols
    if 'baseline' in symbol_data and len(iterations) > 1:
        latest_iter = max([k for k in iterations.keys() if k != 'baseline'], 
                         key=lambda k: iterations[k].get('timestamp', ''))
        
        improvements = []
        for symbol, iter_metrics in symbol_data.items():
            if 'baseline' in iter_metrics and latest_iter in iter_metrics:
                base = iter_metrics['baseline']
                latest = iter_metrics[latest_iter]
                improvements.append({
                    'symbol': symbol,
                    'baseline_return': base.get('total_return', 0),
                    'latest_return': latest.get('total_return', 0),
                    'improvement': latest.get('total_return', 0) - base.get('total_return', 0),
                    'latest_win_rate': latest.get('win_rate', 0),
                    'latest_sharpe': latest.get('sharpe_ratio', 0)
                })
        
        improvements.sort(key=lambda x: x['improvement'], reverse=True)
        
        print(f'\n🟢 TOP 5 IMPROVEMENTS (vs Baseline)')
        print('-'*100)
        print(f'{"Symbol":<10} {"Baseline":<12} {"Latest":<12} {"Improvement":<15} {"Win Rate":<12} {"Sharpe":<10}')
        print('-'*100)
        for imp in improvements[:5]:
            print(f'{imp["symbol"]:<10} {imp["baseline_return"]:>11.2f}% {imp["latest_return"]:>11.2f}% '
                  f'{imp["improvement"]:>+14.2f}% {imp["latest_win_rate"]:>11.2f}% {imp["latest_sharpe"]:>9.2f}')
    
    print('\n' + '='*100)
    print(f'✅ Analysis saved to: {output_file}\n')
    
    return analysis

if __name__ == '__main__':
    generate_final_analysis()


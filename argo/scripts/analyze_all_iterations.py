#!/usr/bin/env python3
"""
Comprehensive Analysis of All Backtest Iterations
Loads and compares all tracked iterations with detailed analysis
"""
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from collections import defaultdict

def load_all_iterations() -> Dict[str, Dict]:
    """Load all backtest iterations from reports directory"""
    reports_dir = Path(__file__).parent.parent / "reports"
    
    iterations = {}
    
    # Load baseline
    baseline_file = reports_dir / "comprehensive_backtest_results.json"
    if baseline_file.exists():
        with open(baseline_file, 'r') as f:
            data = json.load(f)
            iterations['baseline'] = {
                'timestamp': 'baseline',
                'results': data.get('baseline', []),
                'type': 'baseline'
            }
    
    # Load all iteration files
    for file in reports_dir.glob("*_results.json"):
        if file.name.startswith("refined_") or file.name.startswith("optimized_"):
            try:
                with open(file, 'r') as f:
                    data = json.load(f)
                    iteration_name = data.get('iteration_name', file.stem)
                    iterations[iteration_name] = {
                        'timestamp': data.get('timestamp', 'unknown'),
                        'iteration_id': data.get('iteration_id', file.stem),
                        'results': data.get('results', []),
                        'summary': data.get('summary', {}),
                        'type': 'tracked'
                    }
            except Exception as e:
                print(f"⚠️  Error loading {file}: {e}")
    
    # Load current results
    current_file = reports_dir / "current_strategy_backtest_results.json"
    if current_file.exists():
        with open(current_file, 'r') as f:
            data = json.load(f)
            iteration_name = data.get('iteration_name', 'current')
            iterations[iteration_name] = {
                'timestamp': data.get('timestamp', 'unknown'),
                'iteration_id': data.get('iteration_id', 'current'),
                'results': data.get('results', []),
                'type': 'current'
            }
    
    return iterations

def analyze_iterations(iterations: Dict[str, Dict]) -> Dict:
    """Comprehensive analysis of all iterations"""
    
    analysis = {
        'timestamp': datetime.now().isoformat(),
        'iterations_analyzed': list(iterations.keys()),
        'comparison': {},
        'trends': {},
        'best_performers': {},
        'worst_performers': {},
        'improvements': {}
    }
    
    # Convert to symbol-based comparison
    symbol_data = defaultdict(lambda: defaultdict(dict))
    
    for iter_name, iter_data in iterations.items():
        results = iter_data.get('results', [])
        for result in results:
            if 'metrics' in result or 'win_rate' in result:
                symbol = result.get('symbol')
                if symbol:
                    if 'metrics' in result:
                        symbol_data[symbol][iter_name] = result['metrics']
                    else:
                        # Legacy format
                        symbol_data[symbol][iter_name] = {
                            'win_rate': result.get('win_rate', 0),
                            'total_return': result.get('total_return', 0),
                            'sharpe_ratio': result.get('sharpe_ratio', 0),
                            'max_drawdown': result.get('max_drawdown', 0),
                            'total_trades': result.get('total_trades', 0)
                        }
    
    # Overall comparison
    for iter_name, iter_data in iterations.items():
        summary = iter_data.get('summary', {})
        if summary:
            analysis['comparison'][iter_name] = {
                'avg_win_rate': summary.get('avg_win_rate', 0),
                'avg_total_return': summary.get('avg_total_return', 0),
                'avg_sharpe_ratio': summary.get('avg_sharpe_ratio', 0),
                'avg_max_drawdown': summary.get('avg_max_drawdown', 0),
                'total_trades': summary.get('total_trades_all_symbols', 0)
            }
        else:
            # Calculate from results
            results = iter_data.get('results', [])
            valid_results = [r for r in results if 'metrics' in r or 'win_rate' in r]
            if valid_results:
                if 'metrics' in valid_results[0]:
                    analysis['comparison'][iter_name] = {
                        'avg_win_rate': sum(r['metrics'].get('win_rate', 0) for r in valid_results) / len(valid_results),
                        'avg_total_return': sum(r['metrics'].get('total_return', 0) for r in valid_results) / len(valid_results),
                        'avg_sharpe_ratio': sum(r['metrics'].get('sharpe_ratio', 0) for r in valid_results) / len(valid_results),
                        'avg_max_drawdown': sum(r['metrics'].get('max_drawdown', 0) for r in valid_results) / len(valid_results),
                        'total_trades': sum(r['metrics'].get('total_trades', 0) for r in valid_results)
                    }
                else:
                    analysis['comparison'][iter_name] = {
                        'avg_win_rate': sum(r.get('win_rate', 0) for r in valid_results) / len(valid_results),
                        'avg_total_return': sum(r.get('total_return', 0) for r in valid_results) / len(valid_results),
                        'avg_sharpe_ratio': sum(r.get('sharpe_ratio', 0) for r in valid_results) / len(valid_results),
                        'avg_max_drawdown': sum(r.get('max_drawdown', 0) for r in valid_results) / len(valid_results),
                        'total_trades': sum(r.get('total_trades', 0) for r in valid_results)
                    }
    
    # Per-symbol analysis
    analysis['symbols'] = {}
    for symbol, iter_results in symbol_data.items():
        baseline_data = iter_results.get('baseline', {})
        latest_iter = max(iter_results.keys(), key=lambda k: iterations.get(k, {}).get('timestamp', ''))
        latest_data = iter_results.get(latest_iter, {})
        
        analysis['symbols'][symbol] = {
            'baseline': baseline_data,
            'latest': {
                'iteration': latest_iter,
                'data': latest_data
            },
            'improvement': {
                'return_change': latest_data.get('total_return', 0) - baseline_data.get('total_return', 0),
                'win_rate_change': latest_data.get('win_rate', 0) - baseline_data.get('win_rate', 0),
                'sharpe_change': latest_data.get('sharpe_ratio', 0) - baseline_data.get('sharpe_ratio', 0)
            },
            'all_iterations': dict(iter_results)
        }
    
    # Find best and worst performers
    if 'baseline' in iterations:
        baseline_results = {r.get('symbol'): r for r in iterations['baseline'].get('results', []) if 'symbol' in r}
        latest_iter_name = max(iterations.keys(), key=lambda k: iterations[k].get('timestamp', ''))
        latest_results = {r.get('symbol'): r for r in iterations[latest_iter_name].get('results', []) if 'symbol' in r}
        
        improvements = []
        for symbol in set(baseline_results.keys()) & set(latest_results.keys()):
            base = baseline_results[symbol]
            latest = latest_results[symbol]
            
            base_return = base.get('total_return', 0) if 'total_return' in base else base.get('metrics', {}).get('total_return', 0)
            latest_return = latest.get('total_return', 0) if 'total_return' in latest else latest.get('metrics', {}).get('total_return', 0)
            
            improvements.append({
                'symbol': symbol,
                'baseline_return': base_return,
                'latest_return': latest_return,
                'improvement': latest_return - base_return
            })
        
        improvements.sort(key=lambda x: x['improvement'], reverse=True)
        analysis['best_performers'] = improvements[:5]
        analysis['worst_performers'] = improvements[-5:]
    
    return analysis

def print_analysis(analysis: Dict):
    """Print comprehensive analysis"""
    print('\n' + '='*100)
    print('📊 COMPREHENSIVE BACKTEST ANALYSIS - ALL ITERATIONS')
    print('='*100)
    
    print(f'\n📈 ITERATIONS ANALYZED: {len(analysis["iterations_analyzed"])}')
    for iter_name in analysis['iterations_analyzed']:
        print(f'   - {iter_name}')
    
    # Overall comparison
    if analysis['comparison']:
        print(f'\n📊 OVERALL PERFORMANCE COMPARISON')
        print('-'*100)
        print(f'{"Iteration":<20} {"Avg Return":<15} {"Avg Win Rate":<15} {"Avg Sharpe":<15} {"Total Trades":<15}')
        print('-'*100)
        
        for iter_name, data in sorted(analysis['comparison'].items()):
            print(f'{iter_name:<20} {data["avg_total_return"]:>14.2f}% {data["avg_win_rate"]:>14.2f}% '
                  f'{data["avg_sharpe_ratio"]:>14.2f}  {data["total_trades"]:>14}')
    
    # Best performers
    if analysis['best_performers']:
        print(f'\n🟢 TOP 5 IMPROVEMENTS (vs Baseline)')
        print('-'*100)
        print(f'{"Symbol":<10} {"Baseline Return":<18} {"Latest Return":<18} {"Improvement":<15}')
        print('-'*100)
        for perf in analysis['best_performers']:
            print(f'{perf["symbol"]:<10} {perf["baseline_return"]:>17.2f}% {perf["latest_return"]:>17.2f}% '
                  f'{perf["improvement"]:>+14.2f}%')
    
    # Worst performers
    if analysis['worst_performers']:
        print(f'\n🔴 BOTTOM 5 PERFORMERS (vs Baseline)')
        print('-'*100)
        print(f'{"Symbol":<10} {"Baseline Return":<18} {"Latest Return":<18} {"Change":<15}')
        print('-'*100)
        for perf in analysis['worst_performers']:
            print(f'{perf["symbol"]:<10} {perf["baseline_return"]:>17.2f}% {perf["latest_return"]:>17.2f}% '
                  f'{perf["improvement"]:>+14.2f}%')
    
    print('\n' + '='*100 + '\n')

def main():
    """Main analysis function"""
    print("Loading all backtest iterations...")
    iterations = load_all_iterations()
    
    if not iterations:
        print("❌ No iterations found")
        return
    
    print(f"Found {len(iterations)} iterations")
    
    print("Analyzing iterations...")
    analysis = analyze_iterations(iterations)
    
    print_analysis(analysis)
    
    # Save analysis
    output_file = Path(__file__).parent.parent / "reports" / "comprehensive_analysis.json"
    with open(output_file, 'w') as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Analysis saved to: {output_file}\n")

if __name__ == '__main__':
    main()


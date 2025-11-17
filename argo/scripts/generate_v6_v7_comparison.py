#!/usr/bin/env python3
"""
Generate Comprehensive Comparison Report: Iterative V6 vs V7
Creates a detailed markdown report comparing the two iterations
"""
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

def load_iteration_results(iteration_id: str) -> Optional[Dict]:
    """Load results for a specific iteration"""
    reports_dir = Path(__file__).parent.parent / "reports"
    
    # Try to find the iteration file
    pattern = f"{iteration_id}_*_results.json"
    files = list(reports_dir.glob(pattern))
    
    if not files:
        # Try current results if it matches
        current_file = reports_dir / "current_strategy_backtest_results.json"
        if current_file.exists():
            with open(current_file, 'r') as f:
                data = json.load(f)
                if data.get('iteration_name') == iteration_id:
                    return data
        return None
    
    # Load the most recent file
    latest_file = max(files, key=lambda p: p.stat().st_mtime)
    with open(latest_file, 'r') as f:
        return json.load(f)

def calculate_summary_stats(results: List[Dict]) -> Dict:
    """Calculate summary statistics from results"""
    valid_results = [r for r in results if 'error' not in r and 'metrics' in r]
    
    if not valid_results:
        return {}
    
    metrics_list = []
    for r in valid_results:
        m = r.get('metrics', {})
        metrics_list.append({
            'win_rate': m.get('win_rate', 0),
            'total_return': m.get('total_return', 0),
            'sharpe_ratio': m.get('sharpe_ratio', 0),
            'max_drawdown': m.get('max_drawdown', 0),
            'profit_factor': m.get('profit_factor', 0),
            'total_trades': m.get('total_trades', 0),
            'winning_trades': m.get('winning_trades', 0),
            'losing_trades': m.get('losing_trades', 0),
            'avg_win_pct': m.get('avg_win_pct', 0),
            'avg_loss_pct': m.get('avg_loss_pct', 0),
        })
    
    return {
        'avg_win_rate': sum(m['win_rate'] for m in metrics_list) / len(metrics_list),
        'avg_total_return': sum(m['total_return'] for m in metrics_list) / len(metrics_list),
        'avg_sharpe_ratio': sum(m['sharpe_ratio'] for m in metrics_list) / len(metrics_list),
        'avg_max_drawdown': sum(m['max_drawdown'] for m in metrics_list) / len(metrics_list),
        'avg_profit_factor': sum(m['profit_factor'] for m in metrics_list) / len(metrics_list),
        'total_trades': sum(m['total_trades'] for m in metrics_list),
        'total_winning_trades': sum(m['winning_trades'] for m in metrics_list),
        'total_losing_trades': sum(m['losing_trades'] for m in metrics_list),
        'avg_win_pct': sum(m['avg_win_pct'] for m in metrics_list) / len(metrics_list),
        'avg_loss_pct': sum(m['avg_loss_pct'] for m in metrics_list) / len(metrics_list),
        'symbols_tested': len(valid_results)
    }

def compare_iterations(v6_data: Dict, v7_data: Dict) -> Dict:
    """Compare v6 and v7 iterations"""
    
    v6_results = v6_data.get('results', [])
    v7_results = v7_data.get('results', [])
    
    # Calculate summaries
    v6_summary = calculate_summary_stats(v6_results)
    v7_summary = calculate_summary_stats(v7_results)
    
    # Create symbol lookup
    v6_by_symbol = {r['symbol']: r for r in v6_results if 'error' not in r}
    v7_by_symbol = {r['symbol']: r for r in v7_results if 'error' not in r}
    common_symbols = set(v6_by_symbol.keys()) & set(v7_by_symbol.keys())
    
    # Per-symbol comparison
    symbol_comparison = {}
    for symbol in sorted(common_symbols):
        v6_result = v6_by_symbol[symbol]
        v7_result = v7_by_symbol[symbol]
        
        v6_metrics = v6_result.get('metrics', {})
        v7_metrics = v7_result.get('metrics', {})
        
        symbol_comparison[symbol] = {
            'v6': {
                'win_rate': v6_metrics.get('win_rate', 0),
                'total_return': v6_metrics.get('total_return', 0),
                'sharpe_ratio': v6_metrics.get('sharpe_ratio', 0),
                'max_drawdown': v6_metrics.get('max_drawdown', 0),
                'profit_factor': v6_metrics.get('profit_factor', 0),
                'total_trades': v6_metrics.get('total_trades', 0),
            },
            'v7': {
                'win_rate': v7_metrics.get('win_rate', 0),
                'total_return': v7_metrics.get('total_return', 0),
                'sharpe_ratio': v7_metrics.get('sharpe_ratio', 0),
                'max_drawdown': v7_metrics.get('max_drawdown', 0),
                'profit_factor': v7_metrics.get('profit_factor', 0),
                'total_trades': v7_metrics.get('total_trades', 0),
            },
            'change': {
                'win_rate': v7_metrics.get('win_rate', 0) - v6_metrics.get('win_rate', 0),
                'total_return': v7_metrics.get('total_return', 0) - v6_metrics.get('total_return', 0),
                'sharpe_ratio': v7_metrics.get('sharpe_ratio', 0) - v6_metrics.get('sharpe_ratio', 0),
                'max_drawdown': v7_metrics.get('max_drawdown', 0) - v6_metrics.get('max_drawdown', 0),
                'profit_factor': v7_metrics.get('profit_factor', 0) - v6_metrics.get('profit_factor', 0),
                'total_trades': v7_metrics.get('total_trades', 0) - v6_metrics.get('total_trades', 0),
            }
        }
    
    return {
        'timestamp': datetime.now().isoformat(),
        'v6': {
            'iteration_id': v6_data.get('iteration_id', 'iterative_v6'),
            'timestamp': v6_data.get('timestamp', 'unknown'),
            'summary': v6_summary
        },
        'v7': {
            'iteration_id': v7_data.get('iteration_id', 'iterative_v7'),
            'timestamp': v7_data.get('timestamp', 'unknown'),
            'summary': v7_summary
        },
        'overall_change': {
            'win_rate': v7_summary.get('avg_win_rate', 0) - v6_summary.get('avg_win_rate', 0),
            'total_return': v7_summary.get('avg_total_return', 0) - v6_summary.get('avg_total_return', 0),
            'sharpe_ratio': v7_summary.get('avg_sharpe_ratio', 0) - v6_summary.get('avg_sharpe_ratio', 0),
            'max_drawdown': v7_summary.get('avg_max_drawdown', 0) - v6_summary.get('avg_max_drawdown', 0),
            'profit_factor': v7_summary.get('avg_profit_factor', 0) - v6_summary.get('avg_profit_factor', 0),
            'total_trades': v7_summary.get('total_trades', 0) - v6_summary.get('total_trades', 0),
        },
        'symbol_comparison': symbol_comparison
    }

def generate_markdown_report(comparison: Dict) -> str:
    """Generate markdown comparison report"""
    
    v6 = comparison['v6']
    v7 = comparison['v7']
    change = comparison['overall_change']
    
    report = f"""# Backtest Comparison Report: Iterative V6 vs V7

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📊 Executive Summary

This report compares the performance of **Iterative V6** and **Iterative V7** backtest iterations.

### Key Metrics Comparison

| Metric | V6 | V7 | Change | Status |
|--------|----|----|--------|--------|
| **Avg Win Rate** | {v6['summary'].get('avg_win_rate', 0):.2f}% | {v7['summary'].get('avg_win_rate', 0):.2f}% | {change.get('win_rate', 0):+.2f}% | {'✅ Improved' if change.get('win_rate', 0) > 0 else '⚠️ Declined' if change.get('win_rate', 0) < 0 else '➡️ Unchanged'} |
| **Avg Total Return** | {v6['summary'].get('avg_total_return', 0):.2f}% | {v7['summary'].get('avg_total_return', 0):.2f}% | {change.get('total_return', 0):+.2f}% | {'✅ Improved' if change.get('total_return', 0) > 0 else '⚠️ Declined' if change.get('total_return', 0) < 0 else '➡️ Unchanged'} |
| **Avg Sharpe Ratio** | {v6['summary'].get('avg_sharpe_ratio', 0):.2f} | {v7['summary'].get('avg_sharpe_ratio', 0):.2f} | {change.get('sharpe_ratio', 0):+.2f} | {'✅ Improved' if change.get('sharpe_ratio', 0) > 0 else '⚠️ Declined' if change.get('sharpe_ratio', 0) < 0 else '➡️ Unchanged'} |
| **Avg Max Drawdown** | {v6['summary'].get('avg_max_drawdown', 0):.2f}% | {v7['summary'].get('avg_max_drawdown', 0):.2f}% | {change.get('max_drawdown', 0):+.2f}% | {'✅ Improved' if change.get('max_drawdown', 0) > 0 else '⚠️ Declined' if change.get('max_drawdown', 0) < 0 else '➡️ Unchanged'} |
| **Avg Profit Factor** | {v6['summary'].get('avg_profit_factor', 0):.2f} | {v7['summary'].get('avg_profit_factor', 0):.2f} | {change.get('profit_factor', 0):+.2f} | {'✅ Improved' if change.get('profit_factor', 0) > 0 else '⚠️ Declined' if change.get('profit_factor', 0) < 0 else '➡️ Unchanged'} |
| **Total Trades** | {v6['summary'].get('total_trades', 0):,} | {v7['summary'].get('total_trades', 0):,} | {change.get('total_trades', 0):+,} | {'✅ More' if change.get('total_trades', 0) > 0 else '⚠️ Fewer' if change.get('total_trades', 0) < 0 else '➡️ Same'} |
| **Symbols Tested** | {v6['summary'].get('symbols_tested', 0)} | {v7['summary'].get('symbols_tested', 0)} | - | - |

---

## 📈 Overall Performance Analysis

### Win Rate
- **V6:** {v6['summary'].get('avg_win_rate', 0):.2f}%
- **V7:** {v7['summary'].get('avg_win_rate', 0):.2f}%
- **Change:** {change.get('win_rate', 0):+.2f} percentage points
- **Analysis:** {'V7 shows improvement in win rate' if change.get('win_rate', 0) > 0 else 'V7 shows decline in win rate' if change.get('win_rate', 0) < 0 else 'Win rate remains stable'}

### Total Return
- **V6:** {v6['summary'].get('avg_total_return', 0):.2f}%
- **V7:** {v7['summary'].get('avg_total_return', 0):.2f}%
- **Change:** {change.get('total_return', 0):+.2f} percentage points
- **Analysis:** {'V7 generates higher returns' if change.get('total_return', 0) > 0 else 'V7 generates lower returns' if change.get('total_return', 0) < 0 else 'Returns remain stable'}

### Risk-Adjusted Returns (Sharpe Ratio)
- **V6:** {v6['summary'].get('avg_sharpe_ratio', 0):.2f}
- **V7:** {v7['summary'].get('avg_sharpe_ratio', 0):.2f}
- **Change:** {change.get('sharpe_ratio', 0):+.2f}
- **Analysis:** {'V7 shows better risk-adjusted returns' if change.get('sharpe_ratio', 0) > 0 else 'V7 shows worse risk-adjusted returns' if change.get('sharpe_ratio', 0) < 0 else 'Risk-adjusted returns remain stable'}

### Maximum Drawdown
- **V6:** {v6['summary'].get('avg_max_drawdown', 0):.2f}%
- **V7:** {v7['summary'].get('avg_max_drawdown', 0):.2f}%
- **Change:** {change.get('max_drawdown', 0):+.2f} percentage points
- **Analysis:** {'V7 shows lower drawdowns (better)' if change.get('max_drawdown', 0) > 0 else 'V7 shows higher drawdowns (worse)' if change.get('max_drawdown', 0) < 0 else 'Drawdowns remain stable'}

### Profit Factor
- **V6:** {v6['summary'].get('avg_profit_factor', 0):.2f}
- **V7:** {v7['summary'].get('avg_profit_factor', 0):.2f}
- **Change:** {change.get('profit_factor', 0):+.2f}
- **Analysis:** {'V7 shows better profit factor' if change.get('profit_factor', 0) > 0 else 'V7 shows worse profit factor' if change.get('profit_factor', 0) < 0 else 'Profit factor remains stable'}

---

## 📊 Per-Symbol Comparison

### Top Performers (V7 vs V6 - Return Improvement)

"""
    
    # Sort symbols by return improvement
    symbol_data = comparison['symbol_comparison']
    sorted_by_return = sorted(
        symbol_data.items(),
        key=lambda x: x[1]['change']['total_return'],
        reverse=True
    )
    
    report += "| Symbol | V6 Return | V7 Return | Change | V6 Win Rate | V7 Win Rate | V6 Sharpe | V7 Sharpe |\n"
    report += "|--------|-----------|-----------|--------|-------------|-------------|-----------|-----------|\n"
    
    for symbol, data in sorted_by_return:
        v6_data = data['v6']
        v7_data = data['v7']
        change_data = data['change']
        
        report += f"| {symbol} | {v6_data['total_return']:.2f}% | {v7_data['total_return']:.2f}% | {change_data['total_return']:+.2f}% | {v6_data['win_rate']:.2f}% | {v7_data['win_rate']:.2f}% | {v6_data['sharpe_ratio']:.2f} | {v7_data['sharpe_ratio']:.2f} |\n"
    
    report += "\n### Detailed Symbol Analysis\n\n"
    
    for symbol, data in sorted_by_return:
        v6_data = data['v6']
        v7_data = data['v7']
        change_data = data['change']
        
        report += f"#### {symbol}\n\n"
        report += f"- **Win Rate:** {v6_data['win_rate']:.2f}% → {v7_data['win_rate']:.2f}% ({change_data['win_rate']:+.2f}%)\n"
        report += f"- **Total Return:** {v6_data['total_return']:.2f}% → {v7_data['total_return']:.2f}% ({change_data['total_return']:+.2f}%)\n"
        report += f"- **Sharpe Ratio:** {v6_data['sharpe_ratio']:.2f} → {v7_data['sharpe_ratio']:.2f} ({change_data['sharpe_ratio']:+.2f})\n"
        report += f"- **Max Drawdown:** {v6_data['max_drawdown']:.2f}% → {v7_data['max_drawdown']:.2f}% ({change_data['max_drawdown']:+.2f}%)\n"
        report += f"- **Profit Factor:** {v6_data['profit_factor']:.2f} → {v7_data['profit_factor']:.2f} ({change_data['profit_factor']:+.2f})\n"
        report += f"- **Total Trades:** {v6_data['total_trades']} → {v7_data['total_trades']} ({change_data['total_trades']:+})\n\n"
    
    report += f"""
---

## 🎯 Key Insights

### Improvements in V7
"""
    
    improvements = []
    if change.get('win_rate', 0) > 0:
        improvements.append(f"- Win rate improved by {change.get('win_rate', 0):.2f} percentage points")
    if change.get('total_return', 0) > 0:
        improvements.append(f"- Total return improved by {change.get('total_return', 0):.2f} percentage points")
    if change.get('sharpe_ratio', 0) > 0:
        improvements.append(f"- Sharpe ratio improved by {change.get('sharpe_ratio', 0):.2f}")
    if change.get('max_drawdown', 0) > 0:
        improvements.append(f"- Max drawdown reduced by {abs(change.get('max_drawdown', 0)):.2f} percentage points")
    if change.get('profit_factor', 0) > 0:
        improvements.append(f"- Profit factor improved by {change.get('profit_factor', 0):.2f}")
    
    if improvements:
        report += "\n".join(improvements) + "\n"
    else:
        report += "- No significant improvements detected\n"
    
    report += "\n### Areas of Concern\n"
    
    concerns = []
    if change.get('win_rate', 0) < 0:
        concerns.append(f"- Win rate declined by {abs(change.get('win_rate', 0)):.2f} percentage points")
    if change.get('total_return', 0) < 0:
        concerns.append(f"- Total return declined by {abs(change.get('total_return', 0)):.2f} percentage points")
    if change.get('sharpe_ratio', 0) < 0:
        concerns.append(f"- Sharpe ratio declined by {abs(change.get('sharpe_ratio', 0)):.2f}")
    if change.get('max_drawdown', 0) < 0:
        concerns.append(f"- Max drawdown increased by {abs(change.get('max_drawdown', 0)):.2f} percentage points")
    if change.get('profit_factor', 0) < 0:
        concerns.append(f"- Profit factor declined by {abs(change.get('profit_factor', 0)):.2f}")
    
    if concerns:
        report += "\n".join(concerns) + "\n"
    else:
        report += "- No significant concerns detected\n"
    
    report += f"""
---

## 📝 Conclusion

**Iteration V7** shows {'overall improvement' if sum([change.get('win_rate', 0), change.get('total_return', 0), change.get('sharpe_ratio', 0)]) > 0 else 'overall decline' if sum([change.get('win_rate', 0), change.get('total_return', 0), change.get('sharpe_ratio', 0)]) < 0 else 'stable performance'} compared to **Iteration V6**.

### Overall Assessment
- **Win Rate:** {'Improved' if change.get('win_rate', 0) > 0 else 'Declined' if change.get('win_rate', 0) < 0 else 'Stable'}
- **Returns:** {'Improved' if change.get('total_return', 0) > 0 else 'Declined' if change.get('total_return', 0) < 0 else 'Stable'}
- **Risk-Adjusted Performance:** {'Improved' if change.get('sharpe_ratio', 0) > 0 else 'Declined' if change.get('sharpe_ratio', 0) < 0 else 'Stable'}

### Recommendation
{'✅ V7 shows improvements and should be considered for further optimization' if change.get('total_return', 0) > 0 and change.get('sharpe_ratio', 0) >= 0 else '⚠️ V7 shows mixed results - consider investigating specific symbol performance' if change.get('total_return', 0) != 0 or change.get('sharpe_ratio', 0) != 0 else '➡️ V7 shows stable performance - minimal changes detected'}

---

**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**V6 Iteration ID:** {v6.get('iteration_id', 'iterative_v6')}
**V7 Iteration ID:** {v7.get('iteration_id', 'iterative_v7')}
"""
    
    return report

def main():
    """Main function to generate comparison report"""
    
    print("Loading Iterative V6 results...")
    v6_data = load_iteration_results("iterative_v6")
    
    print("Loading Iterative V7 results...")
    v7_data = load_iteration_results("iterative_v7")
    
    if not v6_data:
        print("❌ Error: Could not load Iterative V6 results")
        return
    
    if not v7_data:
        print("❌ Error: Could not load Iterative V7 results")
        return
    
    print("Comparing iterations...")
    comparison = compare_iterations(v6_data, v7_data)
    
    print("Generating markdown report...")
    report = generate_markdown_report(comparison)
    
    # Save markdown report
    reports_dir = Path(__file__).parent.parent / "reports"
    reports_dir.mkdir(exist_ok=True)
    
    markdown_file = reports_dir / "V6_V7_COMPARISON_REPORT.md"
    with open(markdown_file, 'w') as f:
        f.write(report)
    
    # Save JSON comparison
    json_file = reports_dir / "v6_v7_comparison.json"
    with open(json_file, 'w') as f:
        json.dump(comparison, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Comparison report generated:")
    print(f"   Markdown: {markdown_file}")
    print(f"   JSON: {json_file}\n")
    
    # Print summary
    change = comparison['overall_change']
    print("📊 Summary:")
    print(f"   Win Rate: {change.get('win_rate', 0):+.2f}%")
    print(f"   Total Return: {change.get('total_return', 0):+.2f}%")
    print(f"   Sharpe Ratio: {change.get('sharpe_ratio', 0):+.2f}")
    print(f"   Max Drawdown: {change.get('max_drawdown', 0):+.2f}%")
    print(f"   Profit Factor: {change.get('profit_factor', 0):+.2f}\n")

if __name__ == '__main__':
    main()


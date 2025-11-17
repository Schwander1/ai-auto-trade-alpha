#!/usr/bin/env python3
"""
Compare V7 (Simple Cost Model) vs V8 (Enhanced Cost Model)
Shows the impact of using EnhancedTransactionCostModel
"""
import json
from pathlib import Path
from typing import Dict, List
from datetime import datetime

def load_iteration_results(iteration_id: str) -> Dict:
    """Load results for a specific iteration"""
    reports_dir = Path(__file__).parent.parent / "reports"
    
    pattern = f"{iteration_id}_*_results.json"
    files = list(reports_dir.glob(pattern))
    
    if not files:
        return {}
    
    latest_file = max(files, key=lambda p: p.stat().st_mtime)
    with open(latest_file, 'r') as f:
        return json.load(f)

def generate_comparison_report(v7_data: Dict, v8_data: Dict) -> str:
    """Generate comparison report"""
    
    v7_summary = v7_data.get('summary', {})
    v8_summary = v8_data.get('summary', {})
    
    v7_results = v7_data.get('results', [])
    v8_results = v8_data.get('results', [])
    
    # Create symbol lookup
    v7_by_symbol = {r['symbol']: r for r in v7_results if 'error' not in r}
    v8_by_symbol = {r['symbol']: r for r in v8_results if 'error' not in r}
    common_symbols = set(v7_by_symbol.keys()) & set(v8_by_symbol.keys())
    
    report = f"""# Enhanced Cost Model Impact Analysis: V7 vs V8

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📊 Executive Summary

This report compares **Iterative V7** (Simple Cost Model) vs **Iterative V8** (Enhanced Transaction Cost Model) to assess the impact of more realistic cost modeling.

### Key Changes in V8
- ✅ **Enhanced Transaction Cost Model** with square-root slippage
- ✅ **Symbol-specific liquidity tiers** (high/medium/low)
- ✅ **Volume-based slippage calculation**
- ✅ **Volatility-adjusted costs**

---

## 📈 Overall Performance Comparison

| Metric | V7 (Simple) | V8 (Enhanced) | Change | Impact |
|--------|-------------|---------------|--------|--------|
| **Avg Win Rate** | {v7_summary.get('avg_win_rate', 0):.2f}% | {v8_summary.get('avg_win_rate', 0):.2f}% | {v8_summary.get('avg_win_rate', 0) - v7_summary.get('avg_win_rate', 0):+.2f}% | {'✅ Improved' if v8_summary.get('avg_win_rate', 0) > v7_summary.get('avg_win_rate', 0) else '⚠️ Declined' if v8_summary.get('avg_win_rate', 0) < v7_summary.get('avg_win_rate', 0) else '➡️ Unchanged'} |
| **Avg Total Return** | {v7_summary.get('avg_total_return', 0):.2f}% | {v8_summary.get('avg_total_return', 0):.2f}% | {v8_summary.get('avg_total_return', 0) - v7_summary.get('avg_total_return', 0):+.2f}% | {'✅ Improved' if v8_summary.get('avg_total_return', 0) > v7_summary.get('avg_total_return', 0) else '⚠️ Declined' if v8_summary.get('avg_total_return', 0) < v7_summary.get('avg_total_return', 0) else '➡️ Unchanged'} |
| **Avg Sharpe Ratio** | {v7_summary.get('avg_sharpe_ratio', 0):.2f} | {v8_summary.get('avg_sharpe_ratio', 0):.2f} | {v8_summary.get('avg_sharpe_ratio', 0) - v7_summary.get('avg_sharpe_ratio', 0):+.2f} | {'✅ Improved' if v8_summary.get('avg_sharpe_ratio', 0) > v7_summary.get('avg_sharpe_ratio', 0) else '⚠️ Declined' if v8_summary.get('avg_sharpe_ratio', 0) < v7_summary.get('avg_sharpe_ratio', 0) else '➡️ Unchanged'} |
| **Avg Max Drawdown** | {v7_summary.get('avg_max_drawdown', 0):.2f}% | {v8_summary.get('avg_max_drawdown', 0):.2f}% | {v8_summary.get('avg_max_drawdown', 0) - v7_summary.get('avg_max_drawdown', 0):+.2f}% | {'✅ Improved' if v8_summary.get('avg_max_drawdown', 0) > v7_summary.get('avg_max_drawdown', 0) else '⚠️ Declined' if v8_summary.get('avg_max_drawdown', 0) < v7_summary.get('avg_max_drawdown', 0) else '➡️ Unchanged'} |
| **Avg Profit Factor** | {v7_summary.get('avg_profit_factor', 0):.2f} | {v8_summary.get('avg_profit_factor', 0):.2f} | {v8_summary.get('avg_profit_factor', 0) - v7_summary.get('avg_profit_factor', 0):+.2f} | {'✅ Improved' if v8_summary.get('avg_profit_factor', 0) > v7_summary.get('avg_profit_factor', 0) else '⚠️ Declined' if v8_summary.get('avg_profit_factor', 0) < v7_summary.get('avg_profit_factor', 0) else '➡️ Unchanged'} |
| **Total Trades** | {v7_summary.get('total_trades_all_symbols', 0):,} | {v8_summary.get('total_trades_all_symbols', 0):,} | {v8_summary.get('total_trades_all_symbols', 0) - v7_summary.get('total_trades_all_symbols', 0):+,} | {'✅ More' if v8_summary.get('total_trades_all_symbols', 0) > v7_summary.get('total_trades_all_symbols', 0) else '⚠️ Fewer' if v8_summary.get('total_trades_all_symbols', 0) < v7_summary.get('total_trades_all_symbols', 0) else '➡️ Same'} |

---

## 💡 Cost Model Impact Analysis

### Expected Impact of Enhanced Cost Model

The Enhanced Transaction Cost Model should:
1. **Increase costs** for low-liquidity symbols (crypto, small-caps)
2. **Decrease costs** for high-liquidity symbols (SPY, QQQ, large-caps)
3. **Better reflect reality** with volume-based slippage
4. **Potentially reduce returns** if costs are higher overall

### Actual Impact

"""
    
    # Calculate cost impact by symbol
    cost_impact = []
    for symbol in sorted(common_symbols):
        v7_result = v7_by_symbol[symbol]
        v8_result = v8_by_symbol[symbol]
        
        v7_metrics = v7_result.get('metrics', {})
        v8_metrics = v8_result.get('metrics', {})
        
        return_change = v8_metrics.get('total_return', 0) - v7_metrics.get('total_return', 0)
        win_rate_change = v8_metrics.get('win_rate', 0) - v7_metrics.get('win_rate', 0)
        trades_change = v8_metrics.get('total_trades', 0) - v7_metrics.get('total_trades', 0)
        
        cost_impact.append({
            'symbol': symbol,
            'return_change': return_change,
            'win_rate_change': win_rate_change,
            'trades_change': trades_change,
            'v7_return': v7_metrics.get('total_return', 0),
            'v8_return': v8_metrics.get('total_return', 0),
        })
    
    # Sort by return impact
    cost_impact.sort(key=lambda x: x['return_change'])
    
    report += "### Symbols Most Affected (Return Impact)\n\n"
    report += "| Symbol | V7 Return | V8 Return | Change | V7 Win Rate | V8 Win Rate | Trades Change |\n"
    report += "|--------|-----------|-----------|--------|-------------|-------------|---------------|\n"
    
    for item in cost_impact:
        v7_result = v7_by_symbol[item['symbol']]
        v8_result = v8_by_symbol[item['symbol']]
        v7_metrics = v7_result.get('metrics', {})
        v8_metrics = v8_result.get('metrics', {})
        
        report += f"| {item['symbol']} | {item['v7_return']:.2f}% | {item['v8_return']:.2f}% | {item['return_change']:+.2f}% | {v7_metrics.get('win_rate', 0):.2f}% | {v8_metrics.get('win_rate', 0):.2f}% | {item['trades_change']:+} |\n"
    
    report += f"""
---

## 🔍 Detailed Analysis

### High-Liquidity Symbols (Expected: Lower Costs)
"""
    
    high_liquidity = ['SPY', 'QQQ', 'AAPL', 'MSFT', 'GOOGL', 'NVDA']
    for symbol in high_liquidity:
        if symbol in common_symbols:
            v7_result = v7_by_symbol[symbol]
            v8_result = v8_by_symbol[symbol]
            v7_metrics = v7_result.get('metrics', {})
            v8_metrics = v8_result.get('metrics', {})
            
            return_change = v8_metrics.get('total_return', 0) - v7_metrics.get('total_return', 0)
            report += f"\n**{symbol}:**\n"
            report += f"- Return: {v7_metrics.get('total_return', 0):.2f}% → {v8_metrics.get('total_return', 0):.2f}% ({return_change:+.2f}%)\n"
            report += f"- Win Rate: {v7_metrics.get('win_rate', 0):.2f}% → {v8_metrics.get('win_rate', 0):.2f}%\n"
            report += f"- Trades: {v7_metrics.get('total_trades', 0)} → {v8_metrics.get('total_trades', 0)}\n"
    
    report += "\n### Low-Liquidity Symbols (Expected: Higher Costs)\n"
    
    low_liquidity = ['BTC-USD', 'ETH-USD', 'META', 'AMD', 'TSLA']
    for symbol in low_liquidity:
        if symbol in common_symbols:
            v7_result = v7_by_symbol[symbol]
            v8_result = v8_by_symbol[symbol]
            v7_metrics = v7_result.get('metrics', {})
            v8_metrics = v8_result.get('metrics', {})
            
            return_change = v8_metrics.get('total_return', 0) - v7_metrics.get('total_return', 0)
            report += f"\n**{symbol}:**\n"
            report += f"- Return: {v7_metrics.get('total_return', 0):.2f}% → {v8_metrics.get('total_return', 0):.2f}% ({return_change:+.2f}%)\n"
            report += f"- Win Rate: {v7_metrics.get('win_rate', 0):.2f}% → {v8_metrics.get('win_rate', 0):.2f}%\n"
            report += f"- Trades: {v7_metrics.get('total_trades', 0)} → {v8_metrics.get('total_trades', 0)}\n"
    
    report += f"""
---

## 📊 Key Findings

### Cost Model Impact Summary

**Overall Impact:** {'Enhanced cost model shows ' + ('improved' if v8_summary.get('avg_total_return', 0) > v7_summary.get('avg_total_return', 0) else 'reduced' if v8_summary.get('avg_total_return', 0) < v7_summary.get('avg_total_return', 0) else 'similar') + ' performance'}

**Return Impact:** {v8_summary.get('avg_total_return', 0) - v7_summary.get('avg_total_return', 0):+.2f} percentage points
**Win Rate Impact:** {v8_summary.get('avg_win_rate', 0) - v7_summary.get('avg_win_rate', 0):+.2f} percentage points
**Sharpe Impact:** {v8_summary.get('avg_sharpe_ratio', 0) - v7_summary.get('avg_sharpe_ratio', 0):+.2f}

### Interpretation

"""
    
    if v8_summary.get('avg_total_return', 0) < v7_summary.get('avg_total_return', 0):
        report += """
**The enhanced cost model shows lower returns**, which is **expected and more realistic**:
- Enhanced model accounts for volume-based slippage
- Symbol-specific costs better reflect real trading
- Lower returns indicate the simple model was **underestimating costs**
- This makes the backtest **more conservative and realistic** ✅
"""
    elif v8_summary.get('avg_total_return', 0) > v7_summary.get('avg_total_return', 0):
        report += """
**The enhanced cost model shows higher returns**, which may indicate:
- Enhanced model provides better cost optimization
- Volume-based slippage may be lower for our trade sizes
- Symbol-specific tiers may favor our trading patterns
- This suggests the simple model was **overestimating costs** for our use case
"""
    else:
        report += """
**The enhanced cost model shows similar performance**, which indicates:
- Both models are producing similar cost estimates
- Trade sizes may be small enough that slippage differences are minimal
- The simple model may have been reasonably accurate for this strategy
"""
    
    report += f"""
---

## 🎯 Recommendations

### Should We Use Enhanced Cost Model?

**Recommendation:** {'✅ **YES** - Use Enhanced Cost Model' if abs(v8_summary.get('avg_total_return', 0) - v7_summary.get('avg_total_return', 0)) > 1.0 else '⚠️ **MAYBE** - Impact is minimal, either model is acceptable'}

**Reasons:**
1. ✅ More realistic cost modeling (industry standard)
2. ✅ Symbol-specific liquidity tiers
3. ✅ Volume-based slippage (square-root model)
4. ✅ Better reflects actual trading conditions

**Trade-offs:**
- {'Slightly lower returns but more realistic' if v8_summary.get('avg_total_return', 0) < v7_summary.get('avg_total_return', 0) else 'Similar or better returns with more accuracy'}
- More complex implementation
- Requires volume and volatility data

---

## 📝 Conclusion

The Enhanced Transaction Cost Model provides **more realistic cost estimates** compared to the simple fixed-percentage model. 

**Key Takeaway:** {'The enhanced model shows ' + ('lower' if v8_summary.get('avg_total_return', 0) < v7_summary.get('avg_total_return', 0) else 'higher' if v8_summary.get('avg_total_return', 0) > v7_summary.get('avg_total_return', 0) else 'similar') + ' returns, which ' + ('makes the backtest more conservative and realistic' if v8_summary.get('avg_total_return', 0) < v7_summary.get('avg_total_return', 0) else 'suggests better cost optimization' if v8_summary.get('avg_total_return', 0) > v7_summary.get('avg_total_return', 0) else 'indicates both models are similar for this strategy') + '.'}

**Recommendation:** Continue using Enhanced Transaction Cost Model for future backtests to ensure realistic cost estimates.

---

**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**V7 Iteration:** {v7_data.get('iteration_id', 'iterative_v7')}
**V8 Iteration:** {v8_data.get('iteration_id', 'iterative_v8')}
"""
    
    return report

def main():
    """Main function"""
    print("Loading V7 results (Simple Cost Model)...")
    v7_data = load_iteration_results("iterative_v7")
    
    print("Loading V8 results (Enhanced Cost Model)...")
    v8_data = load_iteration_results("iterative_v8")
    
    if not v7_data or not v8_data:
        print("❌ Error: Could not load V7 or V8 results")
        return
    
    print("Generating comparison report...")
    report = generate_comparison_report(v7_data, v8_data)
    
    # Save report
    reports_dir = Path(__file__).parent.parent / "reports"
    reports_dir.mkdir(exist_ok=True)
    
    output_file = reports_dir / "V7_V8_ENHANCED_COST_IMPACT.md"
    with open(output_file, 'w') as f:
        f.write(report)
    
    print(f"✅ Comparison report saved to: {output_file}\n")
    
    # Print quick summary
    v7_summary = v7_data.get('summary', {})
    v8_summary = v8_data.get('summary', {})
    
    print("📊 Quick Summary:")
    print(f"   Return: {v7_summary.get('avg_total_return', 0):.2f}% → {v8_summary.get('avg_total_return', 0):.2f}% ({v8_summary.get('avg_total_return', 0) - v7_summary.get('avg_total_return', 0):+.2f}%)")
    print(f"   Win Rate: {v7_summary.get('avg_win_rate', 0):.2f}% → {v8_summary.get('avg_win_rate', 0):.2f}% ({v8_summary.get('avg_win_rate', 0) - v7_summary.get('avg_win_rate', 0):+.2f}%)")
    print(f"   Sharpe: {v7_summary.get('avg_sharpe_ratio', 0):.2f} → {v8_summary.get('avg_sharpe_ratio', 0):.2f} ({v8_summary.get('avg_sharpe_ratio', 0) - v7_summary.get('avg_sharpe_ratio', 0):+.2f})")
    print()

if __name__ == '__main__':
    main()


#!/usr/bin/env python3
"""
Generate Detailed Symbol Analysis
Creates comprehensive analysis for each symbol with trade statistics
"""
import json
from pathlib import Path
from typing import Dict, List
from datetime import datetime
from collections import defaultdict

def load_v7_results() -> Dict:
    """Load V7 backtest results"""
    reports_dir = Path(__file__).parent.parent / "reports"
    
    # Try to find V7 results
    v7_files = list(reports_dir.glob("iterative_v7_*_results.json"))
    if v7_files:
        latest_file = max(v7_files, key=lambda p: p.stat().st_mtime)
        with open(latest_file, 'r') as f:
            return json.load(f)
    
    # Fallback to current
    current_file = reports_dir / "current_strategy_backtest_results.json"
    if current_file.exists():
        with open(current_file, 'r') as f:
            return json.load(f)
    
    return {}

def analyze_symbol_trades(symbol_data: Dict) -> Dict:
    """Analyze trades for a specific symbol"""
    trades = symbol_data.get('trade_details', {}).get('trades', [])
    
    if not trades:
        return {}
    
    # Trade statistics
    winning_trades = [t for t in trades if t.get('pnl', 0) > 0]
    losing_trades = [t for t in trades if t.get('pnl', 0) < 0]
    breakeven_trades = [t for t in trades if t.get('pnl', 0) == 0]
    
    # Days held analysis
    days_held = [t.get('days_held', 0) for t in trades if t.get('days_held') is not None]
    
    # Confidence analysis
    confidences = [t.get('confidence', 0) for t in trades if t.get('confidence', 0) > 0]
    
    # P&L analysis
    pnls = [t.get('pnl', 0) for t in trades]
    pnl_pcts = [t.get('pnl_pct', 0) for t in trades]
    
    # Side analysis
    long_trades = [t for t in trades if t.get('side') == 'LONG']
    short_trades = [t for t in trades if t.get('side') == 'SELL']
    
    analysis = {
        'total_trades': len(trades),
        'winning_trades': len(winning_trades),
        'losing_trades': len(losing_trades),
        'breakeven_trades': len(breakeven_trades),
        'win_rate': (len(winning_trades) / len(trades) * 100) if trades else 0,
        'long_trades': len(long_trades),
        'short_trades': len(short_trades),
        'avg_days_held': sum(days_held) / len(days_held) if days_held else 0,
        'min_days_held': min(days_held) if days_held else 0,
        'max_days_held': max(days_held) if days_held else 0,
        'avg_confidence': sum(confidences) / len(confidences) if confidences else 0,
        'min_confidence': min(confidences) if confidences else 0,
        'max_confidence': max(confidences) if confidences else 0,
        'total_pnl': sum(pnls),
        'avg_pnl': sum(pnls) / len(pnls) if pnls else 0,
        'avg_pnl_pct': sum(pnl_pcts) / len(pnl_pcts) if pnl_pcts else 0,
        'best_trade_pnl': max(pnls) if pnls else 0,
        'worst_trade_pnl': min(pnls) if pnls else 0,
        'best_trade_pct': max(pnl_pcts) if pnl_pcts else 0,
        'worst_trade_pct': min(pnl_pcts) if pnl_pcts else 0,
    }
    
    # Winning trade stats
    if winning_trades:
        winning_pnls = [t.get('pnl', 0) for t in winning_trades]
        winning_pnl_pcts = [t.get('pnl_pct', 0) for t in winning_trades]
        analysis['avg_win_pnl'] = sum(winning_pnls) / len(winning_pnls)
        analysis['avg_win_pct'] = sum(winning_pnl_pcts) / len(winning_pnl_pcts)
        analysis['largest_win_pnl'] = max(winning_pnls)
        analysis['largest_win_pct'] = max(winning_pnl_pcts)
    else:
        analysis['avg_win_pnl'] = 0
        analysis['avg_win_pct'] = 0
        analysis['largest_win_pnl'] = 0
        analysis['largest_win_pct'] = 0
    
    # Losing trade stats
    if losing_trades:
        losing_pnls = [t.get('pnl', 0) for t in losing_trades]
        losing_pnl_pcts = [t.get('pnl_pct', 0) for t in losing_trades]
        analysis['avg_loss_pnl'] = sum(losing_pnls) / len(losing_pnls)
        analysis['avg_loss_pct'] = sum(losing_pnl_pcts) / len(losing_pnl_pcts)
        analysis['largest_loss_pnl'] = min(losing_pnls)
        analysis['largest_loss_pct'] = min(losing_pnl_pcts)
    else:
        analysis['avg_loss_pnl'] = 0
        analysis['avg_loss_pct'] = 0
        analysis['largest_loss_pnl'] = 0
        analysis['largest_loss_pct'] = 0
    
    # Risk/Reward
    if analysis['avg_loss_pct'] != 0:
        analysis['risk_reward_ratio'] = abs(analysis['avg_win_pct'] / analysis['avg_loss_pct'])
    else:
        analysis['risk_reward_ratio'] = 0
    
    return analysis

def generate_detailed_report(v7_data: Dict) -> str:
    """Generate detailed markdown report"""
    
    results = v7_data.get('results', [])
    
    report = f"""# Detailed Symbol Analysis Report - Iterative V7

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Iteration:** {v7_data.get('iteration_name', 'iterative_v7')}
**Timestamp:** {v7_data.get('timestamp', 'unknown')}

---

## 📊 Overview

This report provides detailed trade-level analysis for each symbol tested in Iterative V7.

**Total Symbols Analyzed:** {len(results)}
**Total Trades:** {sum(r.get('metrics', {}).get('total_trades', 0) for r in results if 'error' not in r)}

---

## 📈 Symbol-by-Symbol Analysis

"""
    
    for result in results:
        if 'error' in result:
            continue
        
        symbol = result.get('symbol', 'UNKNOWN')
        metrics = result.get('metrics', {})
        trade_analysis = analyze_symbol_trades(result)
        
        report += f"""### {symbol}

#### Performance Metrics
- **Win Rate:** {metrics.get('win_rate', 0):.2f}%
- **Total Return:** {metrics.get('total_return', 0):.2f}%
- **Sharpe Ratio:** {metrics.get('sharpe_ratio', 0):.2f}
- **Max Drawdown:** {metrics.get('max_drawdown', 0):.2f}%
- **Profit Factor:** {metrics.get('profit_factor', 0):.2f}
- **Sortino Ratio:** {metrics.get('sortino_ratio', 0):.2f}

#### Trade Statistics
- **Total Trades:** {trade_analysis.get('total_trades', 0)}
- **Winning Trades:** {trade_analysis.get('winning_trades', 0)} ({trade_analysis.get('win_rate', 0):.2f}%)
- **Losing Trades:** {trade_analysis.get('losing_trades', 0)}
- **Breakeven Trades:** {trade_analysis.get('breakeven_trades', 0)}
- **Long Trades:** {trade_analysis.get('long_trades', 0)}
- **Short Trades:** {trade_analysis.get('short_trades', 0)}

#### Trade Performance
- **Average P&L:** ${trade_analysis.get('avg_pnl', 0):.2f}
- **Average P&L %:** {trade_analysis.get('avg_pnl_pct', 0):.2f}%
- **Total P&L:** ${trade_analysis.get('total_pnl', 0):.2f}
- **Best Trade:** ${trade_analysis.get('best_trade_pnl', 0):.2f} ({trade_analysis.get('best_trade_pct', 0):.2f}%)
- **Worst Trade:** ${trade_analysis.get('worst_trade_pnl', 0):.2f} ({trade_analysis.get('worst_trade_pct', 0):.2f}%)

#### Winning Trades
- **Average Win:** ${trade_analysis.get('avg_win_pnl', 0):.2f} ({trade_analysis.get('avg_win_pct', 0):.2f}%)
- **Largest Win:** ${trade_analysis.get('largest_win_pnl', 0):.2f} ({trade_analysis.get('largest_win_pct', 0):.2f}%)

#### Losing Trades
- **Average Loss:** ${trade_analysis.get('avg_loss_pnl', 0):.2f} ({trade_analysis.get('avg_loss_pct', 0):.2f}%)
- **Largest Loss:** ${trade_analysis.get('largest_loss_pnl', 0):.2f} ({trade_analysis.get('largest_loss_pct', 0):.2f}%)

#### Risk/Reward
- **Risk/Reward Ratio:** {trade_analysis.get('risk_reward_ratio', 0):.2f}

#### Trade Duration
- **Average Days Held:** {trade_analysis.get('avg_days_held', 0):.1f} days
- **Min Days Held:** {trade_analysis.get('min_days_held', 0)} days
- **Max Days Held:** {trade_analysis.get('max_days_held', 0)} days

#### Signal Confidence
- **Average Confidence:** {trade_analysis.get('avg_confidence', 0):.2f}%
- **Min Confidence:** {trade_analysis.get('min_confidence', 0):.2f}%
- **Max Confidence:** {trade_analysis.get('max_confidence', 0):.2f}%

---

"""
    
    return report

def main():
    """Main function"""
    print("Loading V7 results...")
    v7_data = load_v7_results()
    
    if not v7_data:
        print("❌ Error: Could not load V7 results")
        return
    
    print("Generating detailed analysis...")
    report = generate_detailed_report(v7_data)
    
    # Save report
    reports_dir = Path(__file__).parent.parent / "reports"
    reports_dir.mkdir(exist_ok=True)
    
    output_file = reports_dir / "DETAILED_SYMBOL_ANALYSIS.md"
    with open(output_file, 'w') as f:
        f.write(report)
    
    print(f"✅ Detailed analysis saved to: {output_file}\n")

if __name__ == '__main__':
    main()


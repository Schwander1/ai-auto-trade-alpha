#!/usr/bin/env python3
"""
Generate Visualizations for Backtest Results
Creates charts and graphs for performance analysis
"""
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import sys

def check_dependencies():
    """Check if visualization libraries are available"""
    try:
        import matplotlib
        import matplotlib.pyplot as plt
        import numpy as np
        return True, matplotlib, plt, np
    except ImportError:
        return False, None, None, None

def load_v7_results() -> Dict:
    """Load V7 backtest results"""
    reports_dir = Path(__file__).parent.parent / "reports"
    
    v7_files = list(reports_dir.glob("iterative_v7_*_results.json"))
    if v7_files:
        latest_file = max(v7_files, key=lambda p: p.stat().st_mtime)
        with open(latest_file, 'r') as f:
            return json.load(f)
    
    current_file = reports_dir / "current_strategy_backtest_results.json"
    if current_file.exists():
        with open(current_file, 'r') as f:
            return json.load(f)
    
    return {}

def load_equity_curves() -> Dict:
    """Load equity curve data"""
    reports_dir = Path(__file__).parent.parent / "reports"
    
    v7_files = list(reports_dir.glob("iterative_v7_*_equity_curves.json"))
    if v7_files:
        latest_file = max(v7_files, key=lambda p: p.stat().st_mtime)
        with open(latest_file, 'r') as f:
            return json.load(f)
    
    return {}

def create_performance_charts(v7_data: Dict, output_dir: Path):
    """Create performance visualization charts"""
    available, matplotlib, plt, np = check_dependencies()
    
    if not available:
        print("⚠️  Matplotlib not available. Skipping chart generation.")
        print("   Install with: pip install matplotlib numpy")
        return
    
    results = v7_data.get('results', [])
    valid_results = [r for r in results if 'error' not in r and 'metrics' in r]
    
    if not valid_results:
        print("⚠️  No valid results to visualize")
        return
    
    # Set style
    plt.style.use('dark_background')
    matplotlib.rcParams['figure.figsize'] = (14, 8)
    matplotlib.rcParams['font.size'] = 10
    
    # 1. Performance Metrics Comparison
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Iterative V7 - Performance Metrics by Symbol', fontsize=16, fontweight='bold')
    
    symbols = [r['symbol'] for r in valid_results]
    win_rates = [r['metrics'].get('win_rate', 0) for r in valid_results]
    returns = [r['metrics'].get('total_return', 0) for r in valid_results]
    sharpe_ratios = [r['metrics'].get('sharpe_ratio', 0) for r in valid_results]
    max_drawdowns = [abs(r['metrics'].get('max_drawdown', 0)) for r in valid_results]
    
    # Win Rate
    ax1 = axes[0, 0]
    bars1 = ax1.barh(symbols, win_rates, color='#4bffb5')
    ax1.set_xlabel('Win Rate (%)', fontsize=12)
    ax1.set_title('Win Rate by Symbol', fontsize=12, fontweight='bold')
    ax1.grid(axis='x', alpha=0.3)
    for i, (symbol, rate) in enumerate(zip(symbols, win_rates)):
        ax1.text(rate + 0.5, i, f'{rate:.1f}%', va='center', fontsize=9)
    
    # Total Return
    ax2 = axes[0, 1]
    colors2 = ['#4bffb5' if r > 0 else '#ff4b5c' for r in returns]
    bars2 = ax2.barh(symbols, returns, color=colors2)
    ax2.set_xlabel('Total Return (%)', fontsize=12)
    ax2.set_title('Total Return by Symbol', fontsize=12, fontweight='bold')
    ax2.grid(axis='x', alpha=0.3)
    for i, (symbol, ret) in enumerate(zip(symbols, returns)):
        ax2.text(ret + (max(returns) * 0.02), i, f'{ret:.1f}%', va='center', fontsize=9)
    
    # Sharpe Ratio
    ax3 = axes[1, 0]
    bars3 = ax3.barh(symbols, sharpe_ratios, color='#18e0ff')
    ax3.set_xlabel('Sharpe Ratio', fontsize=12)
    ax3.set_title('Sharpe Ratio by Symbol', fontsize=12, fontweight='bold')
    ax3.grid(axis='x', alpha=0.3)
    for i, (symbol, sharpe) in enumerate(zip(symbols, sharpe_ratios)):
        ax3.text(sharpe + 0.02, i, f'{sharpe:.2f}', va='center', fontsize=9)
    
    # Max Drawdown
    ax4 = axes[1, 1]
    bars4 = ax4.barh(symbols, max_drawdowns, color='#ff4b5c')
    ax4.set_xlabel('Max Drawdown (%)', fontsize=12)
    ax4.set_title('Max Drawdown by Symbol', fontsize=12, fontweight='bold')
    ax4.grid(axis='x', alpha=0.3)
    for i, (symbol, dd) in enumerate(zip(symbols, max_drawdowns)):
        ax4.text(dd + (max(max_drawdowns) * 0.02), i, f'{dd:.1f}%', va='center', fontsize=9)
    
    plt.tight_layout()
    chart1_path = output_dir / "performance_metrics.png"
    plt.savefig(chart1_path, dpi=150, bbox_inches='tight', facecolor='#0f0f1a')
    plt.close()
    print(f"✅ Created: {chart1_path}")
    
    # 2. Trade Statistics
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle('Iterative V7 - Trade Statistics', fontsize=16, fontweight='bold')
    
    total_trades = [r['metrics'].get('total_trades', 0) for r in valid_results]
    winning_trades = [r['metrics'].get('winning_trades', 0) for r in valid_results]
    losing_trades = [r['metrics'].get('losing_trades', 0) for r in valid_results]
    
    # Total Trades
    ax1 = axes[0]
    bars1 = ax1.barh(symbols, total_trades, color='#2962ff')
    ax1.set_xlabel('Number of Trades', fontsize=12)
    ax1.set_title('Total Trades by Symbol', fontsize=12, fontweight='bold')
    ax1.grid(axis='x', alpha=0.3)
    for i, (symbol, count) in enumerate(zip(symbols, total_trades)):
        ax1.text(count + max(total_trades) * 0.01, i, str(count), va='center', fontsize=9)
    
    # Win/Loss Breakdown
    ax2 = axes[1]
    x = np.arange(len(symbols))
    width = 0.35
    bars1 = ax2.barh(x - width/2, winning_trades, width, label='Winning', color='#4bffb5')
    bars2 = ax2.barh(x + width/2, losing_trades, width, label='Losing', color='#ff4b5c')
    ax2.set_xlabel('Number of Trades', fontsize=12)
    ax2.set_title('Winning vs Losing Trades', fontsize=12, fontweight='bold')
    ax2.set_yticks(x)
    ax2.set_yticklabels(symbols)
    ax2.legend()
    ax2.grid(axis='x', alpha=0.3)
    
    plt.tight_layout()
    chart2_path = output_dir / "trade_statistics.png"
    plt.savefig(chart2_path, dpi=150, bbox_inches='tight', facecolor='#0f0f1a')
    plt.close()
    print(f"✅ Created: {chart2_path}")
    
    # 3. Risk/Reward Scatter
    fig, ax = plt.subplots(figsize=(12, 8))
    
    profit_factors = [r['metrics'].get('profit_factor', 0) for r in valid_results]
    avg_win_pct = [r['metrics'].get('avg_win_pct', 0) for r in valid_results]
    avg_loss_pct = [abs(r['metrics'].get('avg_loss_pct', 0)) for r in valid_results]
    
    scatter = ax.scatter(avg_loss_pct, avg_win_pct, s=[pf*200 for pf in profit_factors], 
                        c=returns, cmap='RdYlGn', alpha=0.7, edgecolors='white', linewidth=1.5)
    
    for i, symbol in enumerate(symbols):
        ax.annotate(symbol, (avg_loss_pct[i], avg_win_pct[i]), 
                   fontsize=9, ha='center', va='center', color='white', fontweight='bold')
    
    ax.set_xlabel('Average Loss (%)', fontsize=12)
    ax.set_ylabel('Average Win (%)', fontsize=12)
    ax.set_title('Risk/Reward Analysis (Size = Profit Factor, Color = Return)', 
                fontsize=12, fontweight='bold')
    ax.grid(alpha=0.3)
    plt.colorbar(scatter, label='Total Return (%)')
    
    plt.tight_layout()
    chart3_path = output_dir / "risk_reward_analysis.png"
    plt.savefig(chart3_path, dpi=150, bbox_inches='tight', facecolor='#0f0f1a')
    plt.close()
    print(f"✅ Created: {chart3_path}")
    
    # 4. Equity Curves (if available)
    equity_data = load_equity_curves()
    if equity_data:
        fig, axes = plt.subplots(3, 4, figsize=(20, 15))
        fig.suptitle('Iterative V7 - Equity Curves by Symbol', fontsize=16, fontweight='bold')
        axes = axes.flatten()
        
        for idx, result in enumerate(valid_results[:12]):
            symbol = result['symbol']
            if symbol in equity_data:
                equity_samples = equity_data[symbol].get('samples', [])
                if equity_samples:
                    dates = []
                    equity_values = []
                    for s in equity_samples:
                        if s.get('date') and s['date'] != 'NaT' and s['date'] is not None:
                            try:
                                dates.append(datetime.fromisoformat(s['date']))
                                equity_values.append(s['equity'])
                            except (ValueError, TypeError):
                                continue
                    
                    ax = axes[idx]
                    ax.plot(dates, equity_values, color='#4bffb5', linewidth=2)
                    ax.set_title(symbol, fontsize=10, fontweight='bold')
                    ax.set_ylabel('Equity ($)', fontsize=8)
                    ax.grid(alpha=0.3)
                    ax.tick_params(labelsize=8)
                    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # Hide unused subplots
        for idx in range(len(valid_results), 12):
            axes[idx].axis('off')
        
        plt.tight_layout()
        chart4_path = output_dir / "equity_curves.png"
        plt.savefig(chart4_path, dpi=150, bbox_inches='tight', facecolor='#0f0f1a')
        plt.close()
        print(f"✅ Created: {chart4_path}")

def main():
    """Main function"""
    print("Loading V7 results...")
    v7_data = load_v7_results()
    
    if not v7_data:
        print("❌ Error: Could not load V7 results")
        return
    
    # Create output directory
    reports_dir = Path(__file__).parent.parent / "reports"
    charts_dir = reports_dir / "charts"
    charts_dir.mkdir(exist_ok=True)
    
    print("Generating visualizations...")
    create_performance_charts(v7_data, charts_dir)
    
    print(f"\n✅ All visualizations saved to: {charts_dir}\n")

if __name__ == '__main__':
    main()


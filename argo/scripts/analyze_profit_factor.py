#!/usr/bin/env python3
"""
Analyze Profit Factor Issues
Identifies symbols with poor win/loss ratios and suggests improvements
"""
import json
from pathlib import Path
from typing import Dict, List

def analyze_profit_factor():
    """Analyze profit factor and win/loss ratios"""
    reports_dir = Path(__file__).parent.parent / "reports"
    
    # Load final refined results
    results_file = reports_dir / "final_refined_20251115_140426_results.json"
    if not results_file.exists():
        print("❌ Results file not found")
        return
    
    with open(results_file, 'r') as f:
        data = json.load(f)
    
    analysis = {
        'symbols': {},
        'recommendations': {}
    }
    
    print('\n' + '='*100)
    print('📊 PROFIT FACTOR ANALYSIS')
    print('='*100)
    print(f'\n{"Symbol":<12} {"Profit Factor":<15} {"Win Rate":<12} {"Avg Win":<12} {"Avg Loss":<12} {"Win/Loss Ratio":<15} {"Status":<20}')
    print('-'*100)
    
    for result in data.get('results', []):
        if 'metrics' not in result:
            continue
        
        symbol = result['symbol']
        metrics = result['metrics']
        
        profit_factor = metrics.get('profit_factor', 0)
        win_rate = metrics.get('win_rate', 0)
        avg_win = metrics.get('avg_win_pct', 0)
        avg_loss = abs(metrics.get('avg_loss_pct', 0))
        win_loss_ratio = avg_win / avg_loss if avg_loss > 0 else 0
        
        # Determine status
        if profit_factor >= 1.0:
            status = "✅ Good"
        elif profit_factor >= 0.9:
            status = "⚠️  Needs Improvement"
        elif profit_factor >= 0.7:
            status = "🔴 Poor"
        else:
            status = "❌ Critical"
        
        analysis['symbols'][symbol] = {
            'profit_factor': profit_factor,
            'win_rate': win_rate,
            'avg_win_pct': avg_win,
            'avg_loss_pct': metrics.get('avg_loss_pct', 0),
            'win_loss_ratio': win_loss_ratio,
            'total_trades': metrics.get('total_trades', 0),
            'winning_trades': metrics.get('winning_trades', 0),
            'losing_trades': metrics.get('losing_trades', 0)
        }
        
        # Generate recommendations
        if profit_factor < 1.0:
            if win_loss_ratio < 1.0:
                # Losing more per loss than winning per win - tighten stops
                recommendation = "Tighten stops (reduce stop_multiplier by 0.1-0.2)"
            elif win_rate < 40:
                # Low win rate - improve entry quality or tighten stops
                recommendation = "Improve entry quality or tighten stops slightly"
            else:
                # Good win rate but poor profit factor - increase profit targets
                recommendation = "Increase profit_multiplier by 0.2-0.3"
        else:
            recommendation = "Maintain current parameters"
        
        analysis['recommendations'][symbol] = recommendation
        
        print(f'{symbol:<12} {profit_factor:>14.2f}  {win_rate:>11.2f}% {avg_win:>11.2f}% {avg_loss:>11.2f}% {win_loss_ratio:>14.2f}  {status:<20}')
    
    # Summary
    print('\n' + '='*100)
    print('📋 RECOMMENDATIONS')
    print('='*100)
    
    critical = [s for s, d in analysis['symbols'].items() if d['profit_factor'] < 0.8]
    needs_improvement = [s for s, d in analysis['symbols'].items() if 0.8 <= d['profit_factor'] < 1.0]
    
    if critical:
        print(f'\n🔴 CRITICAL (Profit Factor < 0.8):')
        for symbol in critical:
            data = analysis['symbols'][symbol]
            print(f'   {symbol}: PF={data["profit_factor"]:.2f}, Win/Loss={data["win_loss_ratio"]:.2f}')
            print(f'      → {analysis["recommendations"][symbol]}')
    
    if needs_improvement:
        print(f'\n⚠️  NEEDS IMPROVEMENT (0.8 ≤ Profit Factor < 1.0):')
        for symbol in needs_improvement:
            data = analysis['symbols'][symbol]
            print(f'   {symbol}: PF={data["profit_factor"]:.2f}, Win/Loss={data["win_loss_ratio"]:.2f}')
            print(f'      → {analysis["recommendations"][symbol]}')
    
    # Save analysis
    output_file = reports_dir / "profit_factor_analysis.json"
    with open(output_file, 'w') as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    
    print(f'\n✅ Analysis saved to: {output_file}\n')
    
    return analysis

if __name__ == '__main__':
    analyze_profit_factor()


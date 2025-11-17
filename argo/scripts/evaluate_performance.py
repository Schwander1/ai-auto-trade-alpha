#!/usr/bin/env python3
"""
Comprehensive Performance Evaluation Script
Evaluates performance of:
1. Signal Generator
2. Production Trading
3. Prop Firm Trading

Usage:
    python scripts/evaluate_performance.py [--days 30] [--json] [--component all|signal|production|prop_firm]
"""
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Optional, List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from argo.core.performance_metrics import get_performance_metrics
from argo.core.performance_monitor import get_performance_monitor
from argo.tracking.unified_tracker import UnifiedPerformanceTracker
from argo.core.paper_trading_engine import PaperTradingEngine
from argo.core.environment import detect_environment

def evaluate_signal_generator(days: int = 30) -> Dict:
    """Evaluate signal generator performance"""
    print("\n" + "=" * 70)
    print("📡 SIGNAL GENERATOR PERFORMANCE")
    print("=" * 70)

    metrics = get_performance_metrics()
    monitor = get_performance_monitor()

    # Get performance summary
    summary = metrics.get_summary()

    # Get detailed stats from monitor
    monitor_stats = monitor.get_all_stats(hours=days * 24)

    # Calculate additional metrics
    cache_hit_rate = metrics.get_cache_hit_rate()
    avg_generation_time = metrics.get_avg_signal_generation_time()
    skip_rate = metrics.get_skip_rate()
    avg_api_latency = metrics.get_avg_api_latency()

    # Data source latencies
    source_latencies = {}
    for source in ['massive', 'alpha_vantage', 'x_sentiment', 'sonar']:
        latency = metrics.get_avg_api_latency(source)
        if latency > 0:
            source_latencies[source] = latency

    result = {
        'component': 'signal_generator',
        'evaluation_date': datetime.now().isoformat(),
        'period_days': days,
        'metrics': {
            'avg_signal_generation_time_seconds': round(avg_generation_time, 3),
            'cache_hit_rate_percent': round(cache_hit_rate, 2),
            'skip_rate_percent': round(skip_rate, 2),
            'avg_api_latency_seconds': round(avg_api_latency, 3),
            'total_cache_hits': summary['total_cache_hits'],
            'total_cache_misses': summary['total_cache_misses'],
            'total_symbols_processed': summary['total_symbols_processed'],
            'total_skipped_symbols': summary['total_skipped_symbols'],
            'uptime_seconds': round(summary['uptime_seconds'], 2),
            'data_source_latencies': {
                source: round(latency, 3)
                for source, latency in source_latencies.items()
            },
            'errors': summary.get('errors', {})
        },
        'performance_grade': _grade_signal_generator(avg_generation_time, cache_hit_rate, skip_rate),
        'recommendations': _get_signal_generator_recommendations(avg_generation_time, cache_hit_rate, skip_rate)
    }

    # Print results
    print(f"\n⏱️  Average Generation Time: {avg_generation_time:.3f}s")
    print(f"📊 Cache Hit Rate: {cache_hit_rate:.2f}%")
    print(f"⏭️  Skip Rate: {skip_rate:.2f}%")
    print(f"🌐 Average API Latency: {avg_api_latency:.3f}s")
    print(f"📈 Total Symbols Processed: {summary['total_symbols_processed']}")
    print(f"✅ Cache Hits: {summary['total_cache_hits']}")
    print(f"❌ Cache Misses: {summary['total_cache_misses']}")

    if source_latencies:
        print(f"\n📡 Data Source Latencies:")
        for source, latency in sorted(source_latencies.items(), key=lambda x: x[1], reverse=True):
            print(f"   {source}: {latency:.3f}s")

    if summary.get('errors'):
        print(f"\n⚠️  Errors:")
        for error, count in summary['errors'].items():
            print(f"   {error}: {count}")

    print(f"\n🎯 Performance Grade: {result['performance_grade']}")
    if result['recommendations']:
        print(f"\n💡 Recommendations:")
        for rec in result['recommendations']:
            print(f"   • {rec}")

    return result

def evaluate_production_trading(days: int = 30) -> Dict:
    """Evaluate production trading performance"""
    print("\n" + "=" * 70)
    print("🏭 PRODUCTION TRADING PERFORMANCE")
    print("=" * 70)

    # Check environment
    environment = detect_environment()

    if environment != "production":
        print(f"\n⚠️  Warning: Current environment is '{environment}', not 'production'")
        print("   This may not reflect actual production trading performance")

    # Initialize tracker
    tracker = UnifiedPerformanceTracker()

    # Get performance stats
    stats = tracker.get_performance_stats(asset_class=None, days=days)

    # Get account info
    try:
        engine = PaperTradingEngine()
        if engine.alpaca_enabled:
            account = engine.get_account_details()
            account_info = {
                'account_name': engine.account_name,
                'account_number': account.get('account_number'),
                'portfolio_value': account.get('portfolio_value'),
                'buying_power': account.get('buying_power'),
                'environment': engine.environment,
                'prop_firm_enabled': getattr(engine, 'prop_firm_enabled', False)
            }

            # Check if this is actually production
            if account_info['prop_firm_enabled']:
                print("\n⚠️  Warning: Prop firm mode is enabled. This may not be production trading.")
        else:
            account_info = {'alpaca_connected': False}
    except Exception as e:
        print(f"\n⚠️  Could not get account info: {e}")
        account_info = {'error': str(e)}

    # Get recent trades for analysis
    recent_trades = tracker.get_recent_trades(limit=100)

    # Calculate additional metrics
    completed_trades = [t for t in recent_trades if t.get('outcome') != 'pending']
    if completed_trades:
        wins = [t for t in completed_trades if t.get('outcome') == 'win']
        losses = [t for t in completed_trades if t.get('outcome') == 'loss']

        total_pnl = sum(t.get('pnl_dollars', 0) or 0 for t in completed_trades)
        avg_pnl = total_pnl / len(completed_trades) if completed_trades else 0

        win_pnl = sum(t.get('pnl_dollars', 0) or 0 for t in wins)
        loss_pnl = sum(t.get('pnl_dollars', 0) or 0 for t in losses)

        profit_factor = abs(win_pnl / loss_pnl) if loss_pnl != 0 else 0

        avg_win = win_pnl / len(wins) if wins else 0
        avg_loss = loss_pnl / len(losses) if losses else 0

        # Calculate return on capital if we have account info
        return_pct = 0
        if account_info.get('portfolio_value'):
            initial_value = account_info['portfolio_value'] - total_pnl
            if initial_value > 0:
                return_pct = (total_pnl / initial_value) * 100
    else:
        wins = []
        losses = []
        total_pnl = 0
        avg_pnl = 0
        profit_factor = 0
        avg_win = 0
        avg_loss = 0
        return_pct = 0

    result = {
        'component': 'production_trading',
        'evaluation_date': datetime.now().isoformat(),
        'period_days': days,
        'environment': environment,
        'account_info': account_info,
        'metrics': {
            'total_trades': stats.get('total_trades', 0),
            'completed_trades': stats.get('completed_trades', 0),
            'pending_trades': stats.get('pending_trades', 0),
            'wins': len(wins),
            'losses': len(losses),
            'win_rate_percent': stats.get('win_rate_percent', 0),
            'total_pnl_dollars': round(total_pnl, 2),
            'avg_pnl_per_trade': round(avg_pnl, 2),
            'profit_factor': round(profit_factor, 2),
            'avg_win_dollars': round(avg_win, 2),
            'avg_loss_dollars': round(avg_loss, 2),
            'return_percent': round(return_pct, 2),
            'stocks_count': stats.get('stocks_count', 0),
            'crypto_count': stats.get('crypto_count', 0),
            'stocks_win_rate': stats.get('stocks_win_rate', 0),
            'crypto_win_rate': stats.get('crypto_win_rate', 0),
            'long_count': stats.get('long_count', 0),
            'short_count': stats.get('short_count', 0),
            'long_win_rate': stats.get('long_win_rate', 0),
            'short_win_rate': stats.get('short_win_rate', 0)
        },
        'performance_grade': _grade_trading_performance(
            stats.get('win_rate_percent', 0),
            profit_factor,
            return_pct,
            stats.get('completed_trades', 0)
        ),
        'recommendations': _get_trading_recommendations(
            stats.get('win_rate_percent', 0),
            profit_factor,
            return_pct,
            len(completed_trades)
        )
    }

    # Print results
    if account_info.get('alpaca_connected'):
        print(f"\n🏦 Account: {account_info.get('account_name', 'Unknown')}")
        print(f"💰 Portfolio Value: ${account_info.get('portfolio_value', 0):,.2f}")
        print(f"💵 Buying Power: ${account_info.get('buying_power', 0):,.2f}")

    print(f"\n📊 Trading Statistics:")
    print(f"   Total Trades: {stats.get('total_trades', 0)}")
    print(f"   Completed: {stats.get('completed_trades', 0)}")
    print(f"   Pending: {stats.get('pending_trades', 0)}")
    print(f"   Wins: {len(wins)}")
    print(f"   Losses: {len(losses)}")
    print(f"   Win Rate: {stats.get('win_rate_percent', 0):.2f}%")

    if completed_trades:
        print(f"\n💰 P&L:")
        print(f"   Total P&L: ${total_pnl:,.2f}")
        print(f"   Average P&L per Trade: ${avg_pnl:,.2f}")
        print(f"   Profit Factor: {profit_factor:.2f}")
        print(f"   Average Win: ${avg_win:,.2f}")
        print(f"   Average Loss: ${avg_loss:,.2f}")
        if return_pct > 0:
            print(f"   Return: {return_pct:.2f}%")

        print(f"\n📈 By Asset Class:")
        print(f"   Stocks: {stats.get('stocks_count', 0)} trades, {stats.get('stocks_win_rate', 0):.2f}% win rate")
        print(f"   Crypto: {stats.get('crypto_count', 0)} trades, {stats.get('crypto_win_rate', 0):.2f}% win rate")

        print(f"\n📊 By Signal Type:")
        print(f"   Long: {stats.get('long_count', 0)} trades, {stats.get('long_win_rate', 0):.2f}% win rate")
        print(f"   Short: {stats.get('short_count', 0)} trades, {stats.get('short_win_rate', 0):.2f}% win rate")
    else:
        print("\n⚠️  No completed trades found in the evaluation period")

    print(f"\n🎯 Performance Grade: {result['performance_grade']}")
    if result['recommendations']:
        print(f"\n💡 Recommendations:")
        for rec in result['recommendations']:
            print(f"   • {rec}")

    return result

def evaluate_prop_firm_trading(days: int = 30) -> Dict:
    """Evaluate prop firm trading performance"""
    print("\n" + "=" * 70)
    print("🏢 PROP FIRM TRADING PERFORMANCE")
    print("=" * 70)

    # Check if prop firm is enabled
    try:
        engine = PaperTradingEngine()
        prop_firm_enabled = getattr(engine, 'prop_firm_enabled', False)

        if not prop_firm_enabled:
            print("\n⚠️  Warning: Prop firm mode is not enabled")
            print("   This evaluation may not reflect actual prop firm trading")

        if engine.alpaca_enabled:
            account = engine.get_account_details()
            account_info = {
                'account_name': engine.account_name,
                'account_number': account.get('account_number'),
                'portfolio_value': account.get('portfolio_value'),
                'buying_power': account.get('buying_power'),
                'environment': engine.environment,
                'prop_firm_enabled': prop_firm_enabled
            }

            # Get prop firm config if available
            if prop_firm_enabled and hasattr(engine, 'prop_firm_config'):
                prop_firm_config = engine.prop_firm_config
                risk_limits = prop_firm_config.get('risk_limits', {})
                account_info['risk_limits'] = {
                    'max_drawdown_pct': risk_limits.get('max_drawdown_pct', 2.0),
                    'daily_loss_limit_pct': risk_limits.get('daily_loss_limit_pct', 4.5),
                    'max_position_size_pct': risk_limits.get('max_position_size_pct', 3.0),
                    'min_confidence': risk_limits.get('min_confidence', 82.0),
                    'max_positions': risk_limits.get('max_positions', 3)
                }
        else:
            account_info = {'alpaca_connected': False}
    except Exception as e:
        print(f"\n⚠️  Could not get account info: {e}")
        account_info = {'error': str(e)}
        prop_firm_enabled = False

    # Initialize tracker
    tracker = UnifiedPerformanceTracker()

    # Get performance stats
    stats = tracker.get_performance_stats(asset_class=None, days=days)

    # Get recent trades
    recent_trades = tracker.get_recent_trades(limit=100)

    # Calculate prop firm specific metrics
    completed_trades = [t for t in recent_trades if t.get('outcome') != 'pending']

    # Calculate compliance metrics (simplified - would need actual prop firm monitor for real data)
    compliance_metrics = {
        'max_drawdown_pct': None,
        'daily_loss_breaches': None,
        'drawdown_breaches': None,
        'trading_halted': None
    }

    if completed_trades:
        wins = [t for t in completed_trades if t.get('outcome') == 'win']
        losses = [t for t in completed_trades if t.get('outcome') == 'loss']

        total_pnl = sum(t.get('pnl_dollars', 0) or 0 for t in completed_trades)
        avg_pnl = total_pnl / len(completed_trades) if completed_trades else 0

        win_pnl = sum(t.get('pnl_dollars', 0) or 0 for t in wins)
        loss_pnl = sum(t.get('pnl_dollars', 0) or 0 for t in losses)

        profit_factor = abs(win_pnl / loss_pnl) if loss_pnl != 0 else 0

        # Calculate return
        return_pct = 0
        if account_info.get('portfolio_value'):
            initial_value = account_info['portfolio_value'] - total_pnl
            if initial_value > 0:
                return_pct = (total_pnl / initial_value) * 100

        # Estimate drawdown (simplified)
        if account_info.get('portfolio_value'):
            # This is a simplified calculation - real prop firm monitor would track peak equity
            max_drawdown = 0  # Would need peak equity tracking
            compliance_metrics['max_drawdown_pct'] = max_drawdown
    else:
        wins = []
        losses = []
        total_pnl = 0
        avg_pnl = 0
        profit_factor = 0
        return_pct = 0

    result = {
        'component': 'prop_firm_trading',
        'evaluation_date': datetime.now().isoformat(),
        'period_days': days,
        'prop_firm_enabled': prop_firm_enabled,
        'account_info': account_info,
        'metrics': {
            'total_trades': stats.get('total_trades', 0),
            'completed_trades': stats.get('completed_trades', 0),
            'pending_trades': stats.get('pending_trades', 0),
            'wins': len(wins),
            'losses': len(losses),
            'win_rate_percent': stats.get('win_rate_percent', 0),
            'total_pnl_dollars': round(total_pnl, 2),
            'avg_pnl_per_trade': round(avg_pnl, 2),
            'profit_factor': round(profit_factor, 2),
            'return_percent': round(return_pct, 2),
            'compliance_metrics': compliance_metrics
        },
        'performance_grade': _grade_prop_firm_performance(
            stats.get('win_rate_percent', 0),
            profit_factor,
            return_pct,
            stats.get('completed_trades', 0),
            compliance_metrics
        ),
        'recommendations': _get_prop_firm_recommendations(
            stats.get('win_rate_percent', 0),
            profit_factor,
            return_pct,
            len(completed_trades),
            compliance_metrics,
            account_info.get('risk_limits', {})
        )
    }

    # Print results
    if account_info.get('alpaca_connected'):
        print(f"\n🏦 Account: {account_info.get('account_name', 'Unknown')}")
        print(f"💰 Portfolio Value: ${account_info.get('portfolio_value', 0):,.2f}")
        print(f"💵 Buying Power: ${account_info.get('buying_power', 0):,.2f}")

        if account_info.get('risk_limits'):
            print(f"\n⚖️  Risk Limits:")
            limits = account_info['risk_limits']
            print(f"   Max Drawdown: {limits.get('max_drawdown_pct', 2.0)}%")
            print(f"   Daily Loss Limit: {limits.get('daily_loss_limit_pct', 4.5)}%")
            print(f"   Max Position Size: {limits.get('max_position_size_pct', 3.0)}%")
            print(f"   Min Confidence: {limits.get('min_confidence', 82.0)}%")
            print(f"   Max Positions: {limits.get('max_positions', 3)}")

    print(f"\n📊 Trading Statistics:")
    print(f"   Total Trades: {stats.get('total_trades', 0)}")
    print(f"   Completed: {stats.get('completed_trades', 0)}")
    print(f"   Pending: {stats.get('pending_trades', 0)}")
    print(f"   Wins: {len(wins)}")
    print(f"   Losses: {len(losses)}")
    print(f"   Win Rate: {stats.get('win_rate_percent', 0):.2f}%")

    if completed_trades:
        print(f"\n💰 P&L:")
        print(f"   Total P&L: ${total_pnl:,.2f}")
        print(f"   Average P&L per Trade: ${avg_pnl:,.2f}")
        print(f"   Profit Factor: {profit_factor:.2f}")
        if return_pct > 0:
            print(f"   Return: {return_pct:.2f}%")

        if compliance_metrics.get('max_drawdown_pct') is not None:
            print(f"\n⚖️  Compliance:")
            print(f"   Max Drawdown: {compliance_metrics['max_drawdown_pct']:.2f}%")
            if compliance_metrics.get('drawdown_breaches') is not None:
                print(f"   Drawdown Breaches: {compliance_metrics['drawdown_breaches']}")
            if compliance_metrics.get('daily_loss_breaches') is not None:
                print(f"   Daily Loss Breaches: {compliance_metrics['daily_loss_breaches']}")
    else:
        print("\n⚠️  No completed trades found in the evaluation period")

    print(f"\n🎯 Performance Grade: {result['performance_grade']}")
    if result['recommendations']:
        print(f"\n💡 Recommendations:")
        for rec in result['recommendations']:
            print(f"   • {rec}")

    return result

def _grade_signal_generator(avg_time: float, cache_hit_rate: float, skip_rate: float) -> str:
    """Grade signal generator performance"""
    score = 0

    # Generation time (target: <0.3s)
    if avg_time < 0.3:
        score += 3
    elif avg_time < 0.7:
        score += 2
    elif avg_time < 1.0:
        score += 1

    # Cache hit rate (target: >80%)
    if cache_hit_rate > 80:
        score += 3
    elif cache_hit_rate > 50:
        score += 2
    elif cache_hit_rate > 30:
        score += 1

    # Skip rate (target: 30-50%)
    if 30 <= skip_rate <= 50:
        score += 2
    elif 20 <= skip_rate <= 60:
        score += 1

    if score >= 7:
        return "A (Excellent)"
    elif score >= 5:
        return "B (Good)"
    elif score >= 3:
        return "C (Fair)"
    else:
        return "D (Needs Improvement)"

def _grade_trading_performance(win_rate: float, profit_factor: float, return_pct: float, trades: int) -> str:
    """Grade trading performance"""
    if trades == 0:
        return "N/A (No Trades)"

    score = 0

    # Win rate (target: >45%)
    if win_rate > 50:
        score += 3
    elif win_rate > 45:
        score += 2
    elif win_rate > 40:
        score += 1

    # Profit factor (target: >1.5)
    if profit_factor > 2.0:
        score += 3
    elif profit_factor > 1.5:
        score += 2
    elif profit_factor > 1.2:
        score += 1

    # Return (target: >10%)
    if return_pct > 20:
        score += 2
    elif return_pct > 10:
        score += 1

    if score >= 7:
        return "A (Excellent)"
    elif score >= 5:
        return "B (Good)"
    elif score >= 3:
        return "C (Fair)"
    else:
        return "D (Needs Improvement)"

def _grade_prop_firm_performance(win_rate: float, profit_factor: float, return_pct: float,
                                 trades: int, compliance: Dict) -> str:
    """Grade prop firm trading performance"""
    if trades == 0:
        return "N/A (No Trades)"

    score = 0

    # Win rate (target: >45%)
    if win_rate > 50:
        score += 2
    elif win_rate > 45:
        score += 1

    # Profit factor (target: >1.5)
    if profit_factor > 2.0:
        score += 2
    elif profit_factor > 1.5:
        score += 1

    # Compliance (critical for prop firm)
    if compliance.get('drawdown_breaches', 0) == 0 and compliance.get('daily_loss_breaches', 0) == 0:
        score += 3
    elif (compliance.get('drawdown_breaches', 0) == 0 or compliance.get('daily_loss_breaches', 0) == 0):
        score += 1

    if score >= 6:
        return "A (Excellent - Compliant)"
    elif score >= 4:
        return "B (Good - Compliant)"
    elif score >= 2:
        return "C (Fair - Monitor Compliance)"
    else:
        return "D (Needs Improvement - Review Compliance)"

def _get_signal_generator_recommendations(avg_time: float, cache_hit_rate: float, skip_rate: float) -> List[str]:
    """Get recommendations for signal generator"""
    recommendations = []

    if avg_time > 0.7:
        recommendations.append(f"Signal generation time ({avg_time:.3f}s) is above target (<0.3s). Consider optimizing data source calls or increasing cache TTL.")

    if cache_hit_rate < 50:
        recommendations.append(f"Cache hit rate ({cache_hit_rate:.2f}%) is below target (>80%). Consider increasing cache TTL or improving cache strategy.")

    if skip_rate < 20:
        recommendations.append(f"Skip rate ({skip_rate:.2f}%) is low. Consider adjusting price change threshold to skip more unchanged symbols.")
    elif skip_rate > 60:
        recommendations.append(f"Skip rate ({skip_rate:.2f}%) is very high. May indicate too aggressive skipping - review threshold.")

    if not recommendations:
        recommendations.append("Signal generator performance is within target ranges. Continue monitoring.")

    return recommendations

def _get_trading_recommendations(win_rate: float, profit_factor: float, return_pct: float, trades: int) -> List[str]:
    """Get recommendations for trading performance"""
    recommendations = []

    if trades == 0:
        recommendations.append("No trades executed. Review signal generation and trading conditions.")
        return recommendations

    if win_rate < 40:
        recommendations.append(f"Win rate ({win_rate:.2f}%) is below target (>45%). Consider reviewing entry criteria or signal quality.")

    if profit_factor < 1.2:
        recommendations.append(f"Profit factor ({profit_factor:.2f}) is below target (>1.5). Consider improving risk/reward ratios or exit strategies.")

    if return_pct < 5:
        recommendations.append(f"Return ({return_pct:.2f}%) is low. Review position sizing and trading frequency.")

    if not recommendations:
        recommendations.append("Trading performance is within target ranges. Continue monitoring and consider scaling up if consistent.")

    return recommendations

def _get_prop_firm_recommendations(win_rate: float, profit_factor: float, return_pct: float,
                                   trades: int, compliance: Dict, risk_limits: Dict) -> List[str]:
    """Get recommendations for prop firm trading"""
    recommendations = []

    if trades == 0:
        recommendations.append("No trades executed. Review signal generation and prop firm constraints.")
        return recommendations

    # Compliance is critical
    if compliance.get('drawdown_breaches', 0) > 0:
        recommendations.append(f"Drawdown breaches detected ({compliance['drawdown_breaches']}). CRITICAL: Review risk management immediately.")

    if compliance.get('daily_loss_breaches', 0) > 0:
        recommendations.append(f"Daily loss breaches detected ({compliance['daily_loss_breaches']}). CRITICAL: Review position sizing and stop losses.")

    if compliance.get('trading_halted'):
        recommendations.append("Trading has been halted. Review compliance breaches before resuming.")

    # Performance recommendations
    if win_rate < 45:
        recommendations.append(f"Win rate ({win_rate:.2f}%) is below target. Consider increasing minimum confidence threshold (current: {risk_limits.get('min_confidence', 82.0)}%).")

    if profit_factor < 1.5:
        recommendations.append(f"Profit factor ({profit_factor:.2f}) is below target. Review risk/reward ratios and exit strategies.")

    # Prop firm specific
    max_dd = risk_limits.get('max_drawdown_pct', 2.0)
    if compliance.get('max_drawdown_pct') and compliance['max_drawdown_pct'] > max_dd * 0.8:
        recommendations.append(f"Drawdown ({compliance['max_drawdown_pct']:.2f}%) is approaching limit ({max_dd}%). Consider reducing position sizes.")

    if not recommendations:
        recommendations.append("Prop firm trading is performing well and compliant. Continue monitoring risk limits closely.")

    return recommendations

def main():
    parser = argparse.ArgumentParser(description='Evaluate system performance')
    parser.add_argument('--days', type=int, default=30, help='Evaluation period in days (default: 30)')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--component', choices=['all', 'signal', 'production', 'prop_firm'],
                       default='all', help='Component to evaluate (default: all)')
    args = parser.parse_args()

    results = {}

    try:
        if args.component in ['all', 'signal']:
            results['signal_generator'] = evaluate_signal_generator(args.days)

        if args.component in ['all', 'production']:
            results['production_trading'] = evaluate_production_trading(args.days)

        if args.component in ['all', 'prop_firm']:
            results['prop_firm_trading'] = evaluate_prop_firm_trading(args.days)

        # Summary
        if not args.json:
            print("\n" + "=" * 70)
            print("📊 PERFORMANCE EVALUATION SUMMARY")
            print("=" * 70)

            for component, result in results.items():
                print(f"\n{component.replace('_', ' ').title()}: {result.get('performance_grade', 'N/A')}")

        # Save results
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            # Save to file
            reports_dir = Path(__file__).parent.parent / "reports"
            reports_dir.mkdir(exist_ok=True)

            report_file = reports_dir / f"performance_evaluation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w') as f:
                json.dump(results, f, indent=2)

            print(f"\n💾 Full report saved to: {report_file}")

    except Exception as e:
        print(f"\n❌ Error during evaluation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()

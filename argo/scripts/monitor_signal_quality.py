#!/usr/bin/env python3
"""
Signal Quality Monitoring Dashboard
Monitors signal generation quality, confidence distribution, and performance metrics

Usage:
    python scripts/monitor_signal_quality.py [--hours 24] [--json]
"""
import sys
import argparse
import sqlite3
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List
from collections import defaultdict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_signal_stats(hours: int = 24) -> Dict:
    """Get signal statistics from database with improved error handling"""
    db_path = Path(__file__).parent.parent / "data" / "signals.db"

    if not db_path.exists():
        logger.warning(f"Database not found: {db_path}")
        return {'error': 'Database not found'}

    try:
        conn = sqlite3.connect(str(db_path), timeout=10.0)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
    except sqlite3.Error as e:
        logger.error(f"Database connection error: {e}")
        return {'error': f'Database connection failed: {e}'}

    cutoff_time = (datetime.now() - timedelta(hours=hours)).isoformat()

    # Overall stats
    cursor.execute("""
        SELECT
            COUNT(*) as total,
            AVG(confidence) as avg_confidence,
            MIN(confidence) as min_confidence,
            MAX(confidence) as max_confidence,
            COUNT(CASE WHEN confidence >= 90 THEN 1 END) as high_confidence,
            COUNT(CASE WHEN confidence >= 85 AND confidence < 90 THEN 1 END) as medium_confidence,
            COUNT(CASE WHEN confidence < 85 THEN 1 END) as low_confidence,
            COUNT(DISTINCT symbol) as unique_symbols,
            COUNT(CASE WHEN outcome = 'win' THEN 1 END) as wins,
            COUNT(CASE WHEN outcome = 'loss' THEN 1 END) as losses,
            AVG(profit_loss_pct) as avg_pnl_pct
        FROM signals
        WHERE created_at >= ?
    """, (cutoff_time,))

    overall = dict(cursor.fetchone())

    # Confidence distribution
    cursor.execute("""
        SELECT
            CASE
                WHEN confidence >= 95 THEN '95-100%'
                WHEN confidence >= 90 THEN '90-95%'
                WHEN confidence >= 85 THEN '85-90%'
                WHEN confidence >= 80 THEN '80-85%'
                ELSE '<80%'
            END as confidence_tier,
            COUNT(*) as count,
            AVG(confidence) as avg_confidence,
            COUNT(CASE WHEN outcome = 'win' THEN 1 END) as wins,
            COUNT(CASE WHEN outcome = 'loss' THEN 1 END) as losses
        FROM signals
        WHERE created_at >= ?
        GROUP BY confidence_tier
        ORDER BY confidence_tier DESC
    """, (cutoff_time,))

    confidence_dist = []
    for row in cursor.fetchall():
        tier_data = dict(row)
        total_tier = tier_data['wins'] + tier_data['losses']
        tier_data['win_rate'] = (tier_data['wins'] / total_tier * 100) if total_tier > 0 else 0.0
        confidence_dist.append(tier_data)

    # Symbol performance
    cursor.execute("""
        SELECT
            symbol,
            COUNT(*) as signal_count,
            AVG(confidence) as avg_confidence,
            COUNT(CASE WHEN outcome = 'win' THEN 1 END) as wins,
            COUNT(CASE WHEN outcome = 'loss' THEN 1 END) as losses,
            AVG(profit_loss_pct) as avg_pnl_pct
        FROM signals
        WHERE created_at >= ?
        GROUP BY symbol
        ORDER BY signal_count DESC
        LIMIT 10
    """, (cutoff_time,))

    symbol_perf = []
    for row in cursor.fetchall():
        symbol_data = dict(row)
        total = symbol_data['wins'] + symbol_data['losses']
        symbol_data['win_rate'] = (symbol_data['wins'] / total * 100) if total > 0 else 0.0
        symbol_perf.append(symbol_data)

    # Recent signals
    cursor.execute("""
        SELECT symbol, action, confidence, entry_price, timestamp, outcome, profit_loss_pct
        FROM signals
        WHERE created_at >= ?
        ORDER BY created_at DESC
        LIMIT 20
    """, (cutoff_time,))

    recent_signals = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return {
        'period_hours': hours,
        'timestamp': datetime.now().isoformat(),
        'overall': overall,
        'confidence_distribution': confidence_dist,
        'symbol_performance': symbol_perf,
        'recent_signals': recent_signals
    }

def print_dashboard(stats: Dict, json_output: bool = False):
    """Print monitoring dashboard"""
    if json_output:
        print(json.dumps(stats, indent=2))
        return

    print("=" * 70)
    print("📊 SIGNAL QUALITY MONITORING DASHBOARD")
    print("=" * 70)
    print(f"⏰ Period: Last {stats['period_hours']} hours")
    print(f"📅 Generated: {stats['timestamp']}")
    print()

    overall = stats['overall']
    if 'error' in overall:
        print(f"❌ Error: {overall['error']}")
        return

    print("📈 OVERALL STATISTICS")
    print("-" * 70)
    print(f"Total Signals: {overall['total']}")
    print(f"Unique Symbols: {overall['unique_symbols']}")
    print()
    print(f"Confidence:")
    print(f"  Average: {overall['avg_confidence']:.2f}%")
    print(f"  Range: {overall['min_confidence']:.2f}% - {overall['max_confidence']:.2f}%")
    print()
    print(f"Confidence Distribution:")
    print(f"  High (≥90%): {overall['high_confidence']} ({overall['high_confidence']/overall['total']*100:.1f}%)")
    print(f"  Medium (85-90%): {overall['medium_confidence']} ({overall['medium_confidence']/overall['total']*100:.1f}%)")
    print(f"  Low (<85%): {overall['low_confidence']} ({overall['low_confidence']/overall['total']*100:.1f}%)")
    print()

    if overall['wins'] + overall['losses'] > 0:
        win_rate = (overall['wins'] / (overall['wins'] + overall['losses'])) * 100
        print(f"Performance:")
        print(f"  Wins: {overall['wins']}")
        print(f"  Losses: {overall['losses']}")
        print(f"  Win Rate: {win_rate:.2f}%")
        if overall['avg_pnl_pct']:
            print(f"  Avg P&L: {overall['avg_pnl_pct']:.2f}%")
    print()

    print("📊 CONFIDENCE DISTRIBUTION")
    print("-" * 70)
    print(f"{'Tier':<12} {'Count':<8} {'Avg Conf':<10} {'Wins':<6} {'Losses':<8} {'Win Rate':<10}")
    print("-" * 70)
    for tier in stats['confidence_distribution']:
        print(f"{tier['confidence_tier']:<12} {tier['count']:<8} {tier['avg_confidence']:<10.2f} "
              f"{tier['wins']:<6} {tier['losses']:<8} {tier['win_rate']:<10.2f}%")
    print()

    print("🎯 SYMBOL PERFORMANCE (Top 10)")
    print("-" * 70)
    print(f"{'Symbol':<10} {'Signals':<8} {'Avg Conf':<10} {'Wins':<6} {'Losses':<8} {'Win Rate':<10} {'Avg P&L':<10}")
    print("-" * 70)
    for symbol in stats['symbol_performance']:
        print(f"{symbol['symbol']:<10} {symbol['signal_count']:<8} {symbol['avg_confidence']:<10.2f} "
              f"{symbol['wins']:<6} {symbol['losses']:<8} {symbol['win_rate']:<10.2f}% "
              f"{symbol['avg_pnl_pct']:<10.2f}%" if symbol['avg_pnl_pct'] else f"{'N/A':<10}")
    print()

    print("🕐 RECENT SIGNALS (Last 20)")
    print("-" * 70)
    print(f"{'Symbol':<10} {'Action':<6} {'Conf':<8} {'Price':<10} {'Outcome':<10} {'P&L':<10}")
    print("-" * 70)
    for signal in stats['recent_signals'][:20]:
        outcome = signal['outcome'] or 'pending'
        pnl = f"{signal['profit_loss_pct']:.2f}%" if signal['profit_loss_pct'] else 'N/A'
        print(f"{signal['symbol']:<10} {signal['action']:<6} {signal['confidence']:<8.2f} "
              f"${signal['entry_price']:<9.2f} {outcome:<10} {pnl:<10}")
    print()

    # Quality alerts
    print("⚠️  QUALITY ALERTS")
    print("-" * 70)
    alerts = []

    if overall['avg_confidence'] < 85:
        alerts.append("⚠️  Average confidence is below 85%")

    if overall['high_confidence'] / overall['total'] < 0.3:
        alerts.append("⚠️  Less than 30% of signals are high confidence (≥90%)")

    if overall['wins'] + overall['losses'] > 10:
        win_rate = (overall['wins'] / (overall['wins'] + overall['losses'])) * 100
        if win_rate < 50:
            alerts.append(f"⚠️  Win rate is below 50% ({win_rate:.1f}%)")

    if alerts:
        for alert in alerts:
            print(alert)
    else:
        print("✅ No quality issues detected")
    print()

def main():
    parser = argparse.ArgumentParser(description='Monitor signal quality metrics')
    parser.add_argument('--hours', type=int, default=24, help='Hours to look back (default: 24)')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        stats = get_signal_stats(args.hours)
        
        if 'error' in stats:
            logger.error(f"Error getting signal stats: {stats['error']}")
            print(f"❌ {stats['error']}")
            sys.exit(1)
        
        print_dashboard(stats, args.json)
    except KeyboardInterrupt:
        logger.warning("Signal quality monitoring interrupted by user")
        print("\n⚠️  Monitoring interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

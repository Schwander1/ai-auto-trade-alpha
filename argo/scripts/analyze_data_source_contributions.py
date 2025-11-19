#!/usr/bin/env python3
"""
Analyze data source contributions to signal generation
Identifies which sources are contributing and their confidence levels

Usage:
    python scripts/analyze_data_source_contributions.py [--symbols TSLA,NVDA,AAPL] [--hours 24]
"""
import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from argo.core.signal_generation_service import SignalGenerationService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def analyze_source_contributions(symbols: List[str], hours: int = 24):
    """Analyze data source contributions for given symbols"""
    print("=" * 70)
    print("📊 DATA SOURCE CONTRIBUTION ANALYSIS")
    print("=" * 70)
    print(f"Symbols: {', '.join(symbols)}")
    print(f"Period: Last {hours} hours")
    print()
    
    # Initialize signal generation service
    try:
        service = SignalGenerationService()
    except Exception as e:
        print(f"❌ Error initializing service: {e}")
        return
    
    source_stats = defaultdict(lambda: {
        'count': 0,
        'total_confidence': 0.0,
        'directions': defaultdict(int),
        'symbols': set(),
        'success_rate': 0,
        'failures': 0
    })
    
    print("🔄 Analyzing source contributions...")
    print()
    
    for symbol in symbols:
        print(f"📈 Analyzing {symbol}...")
        
        # Fetch market data and source signals
        try:
            source_signals, market_data_df = await service._fetch_market_data(symbol)
            
            if not source_signals:
                print(f"  ⚠️  No source signals for {symbol}")
                continue
            
            print(f"  ✅ Found {len(source_signals)} source signals:")
            
            for source_name, signal in source_signals.items():
                if signal:
                    stats = source_stats[source_name]
                    stats['count'] += 1
                    stats['total_confidence'] += signal.get('confidence', 0)
                    stats['directions'][signal.get('direction', 'UNKNOWN')] += 1
                    stats['symbols'].add(symbol)
                    
                    confidence = signal.get('confidence', 0)
                    direction = signal.get('direction', 'UNKNOWN')
                    print(f"    • {source_name}: {direction} @ {confidence:.1f}%")
                else:
                    source_stats[source_name]['failures'] += 1
                    print(f"    • {source_name}: ❌ No signal")
            
            print()
            
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}")
            print(f"  ❌ Error: {e}")
            print()
    
    # Print summary
    print("=" * 70)
    print("📊 SOURCE CONTRIBUTION SUMMARY")
    print("=" * 70)
    print()
    
    if not source_stats:
        print("⚠️  No source contributions found")
        return
    
    # Sort by count
    sorted_sources = sorted(source_stats.items(), key=lambda x: x[1]['count'], reverse=True)
    
    print(f"{'Source':<20} {'Signals':<10} {'Avg Conf':<12} {'Success%':<10} {'Directions':<30} {'Symbols':<15}")
    print("-" * 70)
    
    for source_name, stats in sorted_sources:
        avg_confidence = stats['total_confidence'] / stats['count'] if stats['count'] > 0 else 0
        total_attempts = stats['count'] + stats['failures']
        success_rate = (stats['count'] / total_attempts * 100) if total_attempts > 0 else 0
        
        directions_str = ', '.join([f"{d}:{c}" for d, c in stats['directions'].items()])
        symbols_str = ', '.join(sorted(stats['symbols']))
        
        print(f"{source_name:<20} {stats['count']:<10} {avg_confidence:<12.1f} {success_rate:<10.1f} {directions_str:<30} {symbols_str:<15}")
    
    print()
    
    # Recommendations
    print("💡 RECOMMENDATIONS")
    print("-" * 70)
    
    low_contributors = [name for name, stats in source_stats.items() if stats['count'] == 0]
    if low_contributors:
        print(f"⚠️  Sources not contributing: {', '.join(low_contributors)}")
        print("   → Check API keys, network connectivity, or service availability")
    
    low_confidence = [name for name, stats in source_stats.items() 
                     if stats['count'] > 0 and (stats['total_confidence'] / stats['count']) < 60]
    if low_confidence:
        print(f"⚠️  Sources with low average confidence: {', '.join(low_confidence)}")
        print("   → Review signal generation logic or data quality")
    
    if not low_contributors and not low_confidence:
        print("✅ All sources contributing with reasonable confidence")
    
    print()

def main():
    parser = argparse.ArgumentParser(description='Analyze data source contributions')
    parser.add_argument('--symbols', type=str, default='TSLA,NVDA,AAPL,BTC-USD,ETH-USD',
                       help='Comma-separated list of symbols to analyze')
    parser.add_argument('--hours', type=int, default=24, help='Hours to look back')
    args = parser.parse_args()
    
    symbols = [s.strip() for s in args.symbols.split(',')]
    
    import asyncio
    try:
        asyncio.run(analyze_source_contributions(symbols, args.hours))
    except KeyboardInterrupt:
        print("\n⚠️  Analysis interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()


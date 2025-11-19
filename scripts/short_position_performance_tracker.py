#!/usr/bin/env python3
"""
SHORT Position Performance Tracker

Tracks and reports on SHORT position performance:
- SHORT vs LONG P&L comparison
- SHORT position win rate
- Average SHORT position duration
- SHORT position risk metrics
"""

import sys
import os
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from argo.core.paper_trading_engine import PaperTradingEngine
except ImportError:
    print("❌ Could not import required modules")
    sys.exit(1)


class ShortPositionPerformanceTracker:
    """Track SHORT position performance metrics"""
    
    def __init__(self):
        self.engine = None
        self.db_path = self._find_database()
    
    def _find_database(self):
        """Find the signals database"""
        db_paths = [
            Path("data/signals_unified.db"),
            Path("argo/data/signals.db"),
            Path("data/signals.db"),
        ]
        
        for db_path in db_paths:
            if db_path.exists():
                return str(db_path)
        
        return None
    
    def get_current_positions_performance(self) -> Dict:
        """Get performance metrics for current positions"""
        try:
            if not self.engine:
                self.engine = PaperTradingEngine()
            
            if not self.engine.alpaca_enabled:
                return {}
            
            positions = self.engine.get_positions()
            long_positions = [p for p in positions if p.get("side") == "LONG"]
            short_positions = [p for p in positions if p.get("side") == "SHORT"]
            
            long_pnl = [p.get("pnl_pct", 0) for p in long_positions]
            short_pnl = [p.get("pnl_pct", 0) for p in short_positions]
            
            return {
                'long': {
                    'count': len(long_positions),
                    'total_pnl': sum(long_pnl),
                    'avg_pnl': sum(long_pnl) / len(long_pnl) if long_pnl else 0,
                    'positions': long_positions
                },
                'short': {
                    'count': len(short_positions),
                    'total_pnl': sum(short_pnl),
                    'avg_pnl': sum(short_pnl) / len(short_pnl) if short_pnl else 0,
                    'positions': short_positions
                }
            }
            
        except Exception as e:
            print(f"❌ Error getting positions: {e}")
            return {}
    
    def get_sell_signal_statistics(self, days: int = 30) -> Dict:
        """Get statistics on SELL signals"""
        if not self.db_path:
            return {}
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = """
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN order_id IS NOT NULL THEN 1 END) as executed,
                AVG(confidence) as avg_confidence,
                MIN(confidence) as min_confidence,
                MAX(confidence) as max_confidence
            FROM signals
            WHERE action = 'SELL'
            AND timestamp >= datetime('now', '-' || ? || ' days')
            """
            
            cursor.execute(query, (days,))
            result = cursor.fetchone()
            
            if result:
                total, executed, avg_conf, min_conf, max_conf = result
                execution_rate = (executed / total * 100) if total > 0 else 0
                
                return {
                    'total_signals': total,
                    'executed': executed,
                    'execution_rate': execution_rate,
                    'avg_confidence': avg_conf or 0,
                    'min_confidence': min_conf or 0,
                    'max_confidence': max_conf or 0
                }
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Error getting statistics: {e}")
        
        return {}
    
    def compare_long_vs_short(self) -> Dict:
        """Compare LONG vs SHORT performance"""
        positions = self.get_current_positions_performance()
        
        if not positions:
            return {}
        
        long_data = positions.get('long', {})
        short_data = positions.get('short', {})
        
        comparison = {
            'long': {
                'count': long_data.get('count', 0),
                'total_pnl': long_data.get('total_pnl', 0),
                'avg_pnl': long_data.get('avg_pnl', 0),
            },
            'short': {
                'count': short_data.get('count', 0),
                'total_pnl': short_data.get('total_pnl', 0),
                'avg_pnl': short_data.get('avg_pnl', 0),
            }
        }
        
        # Calculate relative performance
        total_positions = comparison['long']['count'] + comparison['short']['count']
        if total_positions > 0:
            comparison['long']['percentage'] = (comparison['long']['count'] / total_positions) * 100
            comparison['short']['percentage'] = (comparison['short']['count'] / total_positions) * 100
        
        return comparison
    
    def generate_report(self) -> Dict:
        """Generate comprehensive performance report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'current_positions': self.get_current_positions_performance(),
            'sell_signal_stats_30d': self.get_sell_signal_statistics(30),
            'sell_signal_stats_7d': self.get_sell_signal_statistics(7),
            'long_vs_short': self.compare_long_vs_short(),
        }
        
        return report
    
    def print_report(self, report: Optional[Dict] = None):
        """Print formatted performance report"""
        if report is None:
            report = self.generate_report()
        
        print("\n" + "=" * 80)
        print("📊 SHORT POSITION PERFORMANCE REPORT")
        print("=" * 80)
        print(f"Generated: {report['timestamp']}")
        
        # Current Positions
        positions = report.get('current_positions', {})
        if positions:
            print("\n📈 CURRENT POSITIONS")
            print("-" * 80)
            
            long_data = positions.get('long', {})
            short_data = positions.get('short', {})
            
            print(f"LONG Positions: {long_data.get('count', 0)}")
            if long_data.get('count', 0) > 0:
                print(f"  Total P&L: {long_data.get('total_pnl', 0):+.2f}%")
                print(f"  Average P&L: {long_data.get('avg_pnl', 0):+.2f}%")
            
            print(f"\nSHORT Positions: {short_data.get('count', 0)}")
            if short_data.get('count', 0) > 0:
                print(f"  Total P&L: {short_data.get('total_pnl', 0):+.2f}%")
                print(f"  Average P&L: {short_data.get('avg_pnl', 0):+.2f}%")
        
        # SELL Signal Statistics
        stats_30d = report.get('sell_signal_stats_30d', {})
        if stats_30d:
            print("\n📉 SELL SIGNAL STATISTICS (30 Days)")
            print("-" * 80)
            print(f"Total Signals: {stats_30d.get('total_signals', 0)}")
            print(f"Executed: {stats_30d.get('executed', 0)}")
            print(f"Execution Rate: {stats_30d.get('execution_rate', 0):.1f}%")
            print(f"Avg Confidence: {stats_30d.get('avg_confidence', 0):.1f}%")
        
        # LONG vs SHORT Comparison
        comparison = report.get('long_vs_short', {})
        if comparison:
            print("\n⚖️  LONG vs SHORT COMPARISON")
            print("-" * 80)
            print(f"LONG: {comparison['long']['count']} positions ({comparison['long'].get('percentage', 0):.1f}%)")
            print(f"  Total P&L: {comparison['long']['total_pnl']:+.2f}%")
            print(f"  Avg P&L: {comparison['long']['avg_pnl']:+.2f}%")
            print(f"\nSHORT: {comparison['short']['count']} positions ({comparison['short'].get('percentage', 0):.1f}%)")
            print(f"  Total P&L: {comparison['short']['total_pnl']:+.2f}%")
            print(f"  Avg P&L: {comparison['short']['avg_pnl']:+.2f}%")
        
        print("\n" + "=" * 80)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Track SHORT position performance")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--output", help="Save report to file")
    
    args = parser.parse_args()
    
    tracker = ShortPositionPerformanceTracker()
    report = tracker.generate_report()
    
    if args.json:
        print(json.dumps(report, indent=2, default=str))
    else:
        tracker.print_report(report)
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        print(f"\n📄 Report saved to: {args.output}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())


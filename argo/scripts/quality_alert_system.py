#!/usr/bin/env python3
"""
Signal Quality Alert System
Monitors signal quality and sends alerts when quality drops below thresholds

Usage:
    python scripts/quality_alert_system.py [--hours 24] [--check-interval 300]
"""
import sys
import argparse
import sqlite3
import logging
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class QualityAlertSystem:
    """Monitor signal quality and send alerts"""
    
    def __init__(self):
        self.db_path = self._get_unified_db_path()
        self.quality_thresholds = {
            'min_avg_confidence': 75.0,
            'min_high_confidence_pct': 30.0,
            'max_low_confidence_pct': 20.0,
            'min_quality_score': 65.0,
        }
        self.alert_history = []
    
    def _get_unified_db_path(self):
        """Get unified database path"""
        db_paths = [
            Path(__file__).parent.parent / "data" / "signals_unified.db",
            Path(__file__).parent.parent.parent / "data" / "signals_unified.db",
        ]
        
        for db_path in db_paths:
            if db_path.exists():
                return db_path
        
        return None
    
    def check_quality(self, hours: int = 24) -> Dict:
        """Check signal quality and return alerts"""
        if not self.db_path:
            return {'error': 'Unified database not found'}
        
        try:
            conn = sqlite3.connect(str(self.db_path), timeout=10.0)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cutoff_time = (datetime.now() - timedelta(hours=hours)).isoformat()
            
            # Get quality metrics (quality_score may not exist)
            try:
                cursor.execute("""
                    SELECT
                        COUNT(*) as total,
                        AVG(confidence) as avg_confidence,
                        COUNT(CASE WHEN confidence >= 90 THEN 1 END) as high_confidence,
                        COUNT(CASE WHEN confidence < 75 THEN 1 END) as low_confidence,
                        AVG(quality_score) as avg_quality_score
                    FROM signals
                    WHERE timestamp >= ?
                """, (cutoff_time,))
            except sqlite3.OperationalError:
                # Fallback if quality_score column doesn't exist
                cursor.execute("""
                    SELECT
                        COUNT(*) as total,
                        AVG(confidence) as avg_confidence,
                        COUNT(CASE WHEN confidence >= 90 THEN 1 END) as high_confidence,
                        COUNT(CASE WHEN confidence < 75 THEN 1 END) as low_confidence,
                        NULL as avg_quality_score
                    FROM signals
                    WHERE timestamp >= ?
                """, (cutoff_time,))
            
            stats = dict(cursor.fetchone())
            conn.close()
            
            if not stats['total'] or stats['total'] == 0:
                return {'alerts': [], 'stats': stats}
            
            # Calculate percentages
            high_confidence_pct = (stats['high_confidence'] / stats['total'] * 100) if stats['total'] > 0 else 0
            low_confidence_pct = (stats['low_confidence'] / stats['total'] * 100) if stats['total'] > 0 else 0
            
            # Check thresholds
            alerts = []
            
            if stats['avg_confidence'] and stats['avg_confidence'] < self.quality_thresholds['min_avg_confidence']:
                alerts.append({
                    'severity': 'WARNING',
                    'metric': 'avg_confidence',
                    'value': stats['avg_confidence'],
                    'threshold': self.quality_thresholds['min_avg_confidence'],
                    'message': f"Average confidence ({stats['avg_confidence']:.1f}%) below threshold ({self.quality_thresholds['min_avg_confidence']}%)"
                })
            
            if high_confidence_pct < self.quality_thresholds['min_high_confidence_pct']:
                alerts.append({
                    'severity': 'WARNING',
                    'metric': 'high_confidence_pct',
                    'value': high_confidence_pct,
                    'threshold': self.quality_thresholds['min_high_confidence_pct'],
                    'message': f"High-confidence signals ({high_confidence_pct:.1f}%) below threshold ({self.quality_thresholds['min_high_confidence_pct']}%)"
                })
            
            if low_confidence_pct > self.quality_thresholds['max_low_confidence_pct']:
                alerts.append({
                    'severity': 'WARNING',
                    'metric': 'low_confidence_pct',
                    'value': low_confidence_pct,
                    'threshold': self.quality_thresholds['max_low_confidence_pct'],
                    'message': f"Low-confidence signals ({low_confidence_pct:.1f}%) above threshold ({self.quality_thresholds['max_low_confidence_pct']}%)"
                })
            
            # Quality score check (may not be available)
            if stats.get('avg_quality_score') and stats['avg_quality_score'] is not None:
                if stats['avg_quality_score'] < self.quality_thresholds['min_quality_score']:
                    alerts.append({
                        'severity': 'WARNING',
                        'metric': 'avg_quality_score',
                        'value': stats['avg_quality_score'],
                        'threshold': self.quality_thresholds['min_quality_score'],
                        'message': f"Average quality score ({stats['avg_quality_score']:.1f}) below threshold ({self.quality_thresholds['min_quality_score']})"
                    })
            
            return {
                'alerts': alerts,
                'stats': {
                    **stats,
                    'high_confidence_pct': high_confidence_pct,
                    'low_confidence_pct': low_confidence_pct
                }
            }
            
        except Exception as e:
            logger.error(f"Error checking quality: {e}")
            return {'error': str(e)}
    
    def print_alerts(self, result: Dict):
        """Print quality alerts"""
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
            return
        
        stats = result.get('stats', {})
        alerts = result.get('alerts', [])
        
        print("=" * 70)
        print("📊 SIGNAL QUALITY ALERT CHECK")
        print("=" * 70)
        print(f"Total Signals: {stats.get('total', 0)}")
        print(f"Average Confidence: {stats.get('avg_confidence', 0):.2f}%")
        print(f"High Confidence: {stats.get('high_confidence_pct', 0):.1f}%")
        print(f"Low Confidence: {stats.get('low_confidence_pct', 0):.1f}%")
        print()
        
        if alerts:
            print("⚠️  QUALITY ALERTS")
            print("-" * 70)
            for alert in alerts:
                print(f"  {alert['severity']}: {alert['message']}")
            print()
            return 1  # Exit code for alerts
        else:
            print("✅ No quality alerts - all metrics within thresholds")
            print()
            return 0

def main():
    parser = argparse.ArgumentParser(description='Signal Quality Alert System')
    parser.add_argument('--hours', type=int, default=24, help='Hours to look back (default: 24)')
    parser.add_argument('--check-interval', type=int, default=300, help='Check interval in seconds (default: 300)')
    parser.add_argument('--continuous', action='store_true', help='Run continuously')
    args = parser.parse_args()
    
    alert_system = QualityAlertSystem()
    
    try:
        if args.continuous:
            print(f"🔄 Running quality alerts continuously (checking every {args.check_interval}s)")
            print("Press Ctrl+C to stop")
            print()
            
            while True:
                result = alert_system.check_quality(args.hours)
                alert_system.print_alerts(result)
                time.sleep(args.check_interval)
        else:
            result = alert_system.check_quality(args.hours)
            sys.exit(alert_system.print_alerts(result))
            
    except KeyboardInterrupt:
        print("\n⚠️  Alert system stopped by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()


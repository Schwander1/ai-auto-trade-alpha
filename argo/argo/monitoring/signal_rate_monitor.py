#!/usr/bin/env python3
"""
Signal Generation Rate Monitor
Monitors signal generation rate and alerts if too low
"""
import asyncio
import sqlite3
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger("SignalRateMonitor")


class SignalRateMonitor:
    """Monitor signal generation rate and alert if too low"""
    
    def __init__(self, db_path: Optional[Path] = None, expected_rate_per_hour: int = 500):
        self.db_path = db_path
        self.expected_rate = expected_rate_per_hour
        self.alert_threshold = 0.5  # Alert if < 50% of expected
        self._running = False
        
        if db_path is None:
            # Auto-detect database path
            if Path("/root/argo-production-unified").exists():
                self.db_path = Path("/root/argo-production-unified/data/signals_unified.db")
            elif Path("/root/argo-production-prop-firm").exists():
                self.db_path = Path("/root/argo-production-prop-firm/data/signals.db")
            else:
                self.db_path = Path(__file__).parent.parent.parent.parent / "data" / "signals_unified.db"
    
    async def check_rate(self) -> Dict:
        """Check current signal generation rate"""
        if not self.db_path or not self.db_path.exists():
            return {
                'status': 'error',
                'error': 'Database not found',
                'db_path': str(self.db_path) if self.db_path else 'None'
            }
        
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Count signals in last hour
            cursor.execute("""
                SELECT COUNT(*) FROM signals 
                WHERE created_at >= datetime('now', '-1 hour')
            """)
            recent_count = cursor.fetchone()[0]
            
            # Count signals in last 24 hours
            cursor.execute("""
                SELECT COUNT(*) FROM signals 
                WHERE created_at >= datetime('now', '-24 hours')
            """)
            last_24h = cursor.fetchone()[0]
            
            # Count signals in last 5 minutes
            cursor.execute("""
                SELECT COUNT(*) FROM signals 
                WHERE created_at >= datetime('now', '-5 minutes')
            """)
            last_5m = cursor.fetchone()[0]
            
            # Calculate rate
            rate_percentage = recent_count / self.expected_rate if self.expected_rate > 0 else 0
            
            # Check if alert needed
            alert = rate_percentage < self.alert_threshold
            
            # Get breakdown by service type
            cursor.execute("""
                SELECT service_type, COUNT(*) FROM signals 
                WHERE created_at >= datetime('now', '-1 hour')
                GROUP BY service_type
            """)
            service_breakdown = dict(cursor.fetchall())
            
            conn.close()
            
            result = {
                'signals_last_hour': recent_count,
                'signals_last_24h': last_24h,
                'signals_last_5m': last_5m,
                'expected_rate': self.expected_rate,
                'rate_percentage': rate_percentage,
                'alert': alert,
                'status': 'OK' if not alert else 'LOW',
                'service_breakdown': service_breakdown,
                'timestamp': datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error checking signal rate: {e}", exc_info=True)
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def monitor_loop(self, interval_seconds: int = 300):
        """Continuously monitor signal rate"""
        self._running = True
        logger.info(f"🚀 Signal rate monitor started (checking every {interval_seconds}s)")
        
        while self._running:
            try:
                result = await self.check_rate()
                
                if result.get('status') == 'error':
                    logger.error(f"❌ Monitor error: {result.get('error')}")
                elif result.get('alert'):
                    logger.warning(
                        f"⚠️  Signal generation rate LOW: {result['signals_last_hour']}/hour "
                        f"(expected: {result['expected_rate']}/hour, "
                        f"{result['rate_percentage']:.1%} of expected)"
                    )
                    logger.warning(f"   Last 5 minutes: {result.get('signals_last_5m', 0)} signals")
                    logger.warning(f"   Service breakdown: {result.get('service_breakdown', {})}")
                else:
                    logger.info(
                        f"✅ Signal generation rate OK: {result['signals_last_hour']}/hour "
                        f"({result['rate_percentage']:.1%} of expected, "
                        f"last 5m: {result.get('signals_last_5m', 0)})"
                    )
                
                await asyncio.sleep(interval_seconds)
                
            except Exception as e:
                logger.error(f"Error in signal rate monitor: {e}", exc_info=True)
                await asyncio.sleep(interval_seconds)
    
    def stop(self):
        """Stop monitoring"""
        self._running = False
        logger.info("🛑 Signal rate monitor stopped")


async def main():
    """Run monitor as standalone"""
    monitor = SignalRateMonitor()
    try:
        await monitor.monitor_loop(interval_seconds=300)
    except KeyboardInterrupt:
        monitor.stop()


if __name__ == "__main__":
    asyncio.run(main())


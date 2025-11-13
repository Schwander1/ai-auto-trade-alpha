#!/usr/bin/env python3
"""
Integrity Monitoring Job
Continuously verifies signal integrity and detects tampering

COMPLIANCE: Automated integrity checks for audit trail verification
"""
import os
import sys
import time
import hashlib
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
import sqlite3

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("IntegrityMonitor")

# Database paths
if os.path.exists("/root/argo-production"):
    BASE_DIR = Path("/root/argo-production")
else:
    BASE_DIR = Path(__file__).parent.parent.parent.parent

DB_FILE = BASE_DIR / "data" / "signals.db"


class IntegrityMonitor:
    """Monitors signal integrity and detects tampering"""
    
    def __init__(self):
        self.db_file = DB_FILE
        self.failed_verifications = []
    
    def run_integrity_check(self, sample_size: Optional[int] = None, full_check: bool = False) -> Dict:
        """
        Run integrity check on signals
        
        Args:
            sample_size: Number of signals to check (None = all if full_check, else 1000)
            full_check: If True, check all signals (for daily checks)
        
        Returns:
            Dictionary with check results
        """
        start_time = time.time()
        
        if full_check:
            logger.info("🔍 Running FULL integrity check (all signals)")
            sample_size = None
        else:
            sample_size = sample_size or 1000
            logger.info(f"🔍 Running integrity check (sample: {sample_size} signals)")
        
        try:
            # Query signals
            signals = self._query_signals(sample_size)
            
            if not signals:
                logger.warning("⚠️  No signals found in database")
                return {
                    'success': True,
                    'total_signals': 0,
                    'checked': 0,
                    'failed': 0,
                    'status': 'PASS',
                    'timestamp': datetime.utcnow().isoformat()
                }
            
            # Verify each signal
            failed_count = 0
            failed_signals = []
            
            for signal in signals:
                is_valid = self._verify_signal_hash(signal)
                if not is_valid:
                    failed_count += 1
                    failed_signals.append({
                        'signal_id': signal.get('signal_id'),
                        'symbol': signal.get('symbol'),
                        'timestamp': signal.get('timestamp')
                    })
                    
                    if failed_count <= 10:  # Log first 10 failures
                        logger.error(f"❌ Hash verification failed: {signal.get('signal_id')}")
            
            # Calculate results
            total_checked = len(signals)
            duration = time.time() - start_time
            
            status = 'PASS' if failed_count == 0 else 'FAIL'
            
            results = {
                'success': failed_count == 0,
                'total_signals': total_checked,
                'checked': total_checked,
                'failed': failed_count,
                'failed_signals': failed_signals[:10],  # Limit to first 10
                'status': status,
                'duration_seconds': round(duration, 2),
                'signals_per_second': round(total_checked / duration, 2) if duration > 0 else 0,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Log results
            if failed_count == 0:
                logger.info(f"✅ Integrity check PASSED: {total_checked} signals verified in {duration:.2f}s")
            else:
                logger.error(f"❌ Integrity check FAILED: {failed_count}/{total_checked} signals failed verification")
                # Trigger alert
                self._trigger_alert(results)
            
            # Record metrics
            self._record_metrics(results)
            
            # Store in integrity log (if PostgreSQL available)
            self._log_integrity_check(results)
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Integrity check failed: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _query_signals(self, limit: Optional[int] = None) -> List[Dict]:
        """Query signals from database"""
        if not self.db_file.exists():
            logger.warning(f"Database not found: {self.db_file}")
            return []
        
        conn = sqlite3.connect(str(self.db_file))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if limit:
            cursor.execute("""
                SELECT signal_id, symbol, action, entry_price, target_price, stop_price,
                       confidence, strategy, timestamp, sha256 as verification_hash
                FROM signals
                ORDER BY RANDOM()
                LIMIT ?
            """, (limit,))
        else:
            cursor.execute("""
                SELECT signal_id, symbol, action, entry_price, target_price, stop_price,
                       confidence, strategy, timestamp, sha256 as verification_hash
                FROM signals
                ORDER BY timestamp DESC
            """)
        
        signals = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return signals
    
    def _verify_signal_hash(self, signal: Dict) -> bool:
        """Verify signal hash matches data"""
        stored_hash = signal.get('verification_hash') or signal.get('sha256')
        if not stored_hash:
            return False
        
        # Recalculate hash
        hash_fields = {
            'signal_id': signal.get('signal_id'),
            'symbol': signal.get('symbol'),
            'action': signal.get('action'),
            'entry_price': signal.get('entry_price'),
            'target_price': signal.get('target_price'),
            'stop_price': signal.get('stop_price'),
            'confidence': signal.get('confidence'),
            'strategy': signal.get('strategy'),
            'timestamp': signal.get('timestamp')
        }
        
        hash_string = json.dumps(hash_fields, sort_keys=True, default=str)
        calculated_hash = hashlib.sha256(hash_string.encode('utf-8')).hexdigest()
        
        return calculated_hash == stored_hash
    
    def _trigger_alert(self, results: Dict):
        """Trigger alert for integrity failures"""
        logger.critical("🚨 INTEGRITY VERIFICATION FAILURE DETECTED")
        logger.critical(f"   Failed signals: {results['failed']}/{results['checked']}")
        logger.critical("   This is a CRITICAL security incident")
        
        # TODO: Send to PagerDuty, Slack, email, etc.
        # For now, just log
        
        # Lock affected signals (read-only) - would need database connection
        # This is a placeholder for production implementation
    
    def _record_metrics(self, results: Dict):
        """Record Prometheus metrics"""
        try:
            from argo.core.metrics import integrity_failed_verifications_total
            integrity_failed_verifications_total.inc(results['failed'])
        except (ImportError, AttributeError):
            pass  # Metrics not available
    
    def _log_integrity_check(self, results: Dict):
        """Log integrity check to database (if PostgreSQL available)"""
        # This would log to integrity_checksum_log table in PostgreSQL
        # For now, just log to file
        log_file = BASE_DIR / "logs" / "integrity_checks.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(log_file, 'a') as f:
            f.write(json.dumps(results) + '\n')


def main():
    """Main execution"""
    import sys
    
    monitor = IntegrityMonitor()
    
    if len(sys.argv) > 1 and sys.argv[1] == 'full':
        # Full check (daily)
        results = monitor.run_integrity_check(full_check=True)
    else:
        # Sample check (hourly)
        sample_size = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
        results = monitor.run_integrity_check(sample_size=sample_size)
    
    # Print results
    print(json.dumps(results, indent=2, default=str))
    
    exit(0 if results.get('success', False) else 1)

if __name__ == '__main__':
    main()


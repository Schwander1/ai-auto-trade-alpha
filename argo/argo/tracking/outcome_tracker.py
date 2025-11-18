#!/usr/bin/env python3
"""
Automated Outcome Tracking Service v5.0
Tracks signal outcomes automatically for ML training and analytics

OPTIMIZATIONS (v5.0):
- Automatic outcome tracking
- Real-time P&L calculation
- Complete historical data
- ML training dataset generation
"""
import sqlite3
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("OutcomeTracker")

# Use relative path that works in both dev and production
# Check for unified database first, then fallback to old locations
if os.path.exists("/root/argo-production-unified"):
    BASE_DIR = Path("/root/argo-production-unified")
    DB_FILE = BASE_DIR / "data" / "signals_unified.db"
elif os.path.exists("/root/argo-production"):
    BASE_DIR = Path("/root/argo-production")
    DB_FILE = BASE_DIR / "data" / "signals.db"
else:
    BASE_DIR = Path(__file__).parent.parent.parent.parent
    DB_FILE = BASE_DIR / "data" / "signals.db"


class OutcomeTracker:
    """Automated outcome tracking for signals"""
    
    def __init__(self):
        self.db_file = DB_FILE
        self._init_database()
    
    def _init_database(self):
        """Initialize database with outcome tracking columns"""
        if not self.db_file.exists():
            logger.warning(f"Database not found at {self.db_file}")
            return
        
        conn = None
        try:
            conn = sqlite3.connect(str(self.db_file))
            cursor = conn.cursor()
            
            # Add outcome columns if they don't exist
            try:
                cursor.execute("ALTER TABLE signals ADD COLUMN outcome TEXT DEFAULT NULL")
            except sqlite3.OperationalError:
                pass  # Column already exists
            
            try:
                cursor.execute("ALTER TABLE signals ADD COLUMN exit_price REAL DEFAULT NULL")
            except sqlite3.OperationalError:
                pass
            
            try:
                cursor.execute("ALTER TABLE signals ADD COLUMN profit_loss_pct REAL DEFAULT NULL")
            except sqlite3.OperationalError:
                pass
            
            try:
                cursor.execute("ALTER TABLE signals ADD COLUMN exit_timestamp TEXT DEFAULT NULL")
            except sqlite3.OperationalError:
                pass
            
            conn.commit()
        except Exception as e:
            logger.error(f"Error initializing database: {e}", exc_info=True)
            if conn:
                try:
                    conn.rollback()
                except Exception:
                    pass
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass
    
    def update_outcome(
        self,
        signal_id: str,
        exit_price: float,
        exit_timestamp: Optional[datetime] = None,
        outcome: Optional[str] = None
    ) -> bool:
        """
        Update signal outcome
        
        Args:
            signal_id: Signal ID
            exit_price: Exit price
            exit_timestamp: Exit timestamp (default: now)
            outcome: Outcome ('win', 'loss', 'expired') - auto-calculated if None
        
        Returns:
            True if updated successfully
        """
        if not self.db_file.exists():
            logger.warning(f"Database not found at {self.db_file}")
            return False
        
        conn = None
        try:
            conn = sqlite3.connect(str(self.db_file))
            cursor = conn.cursor()
            
            # Get signal details
            cursor.execute("""
                SELECT entry_price, target_price, stop_price, action
                FROM signals
                WHERE signal_id = ?
            """, (signal_id,))
            
            result = cursor.fetchone()
            if not result:
                logger.warning(f"Signal {signal_id} not found")
                return False
            
            entry_price, target_price, stop_price, action = result
            
            # Calculate P&L percentage
            if action == 'BUY':
                pnl_pct = ((exit_price - entry_price) / entry_price) * 100
            else:  # SELL
                pnl_pct = ((entry_price - exit_price) / entry_price) * 100
            
            # Determine outcome if not provided
            if outcome is None:
                if target_price and stop_price:
                    if action == 'BUY':
                        if exit_price >= target_price:
                            outcome = 'win'
                        elif exit_price <= stop_price:
                            outcome = 'loss'
                        else:
                            outcome = 'expired'
                    else:  # SELL
                        if exit_price <= target_price:
                            outcome = 'win'
                        elif exit_price >= stop_price:
                            outcome = 'loss'
                        else:
                            outcome = 'expired'
                else:
                    # Simple win/loss based on P&L
                    outcome = 'win' if pnl_pct > 0 else 'loss'
            
            # Update signal
            exit_ts = (exit_timestamp or datetime.utcnow()).isoformat()
            
            cursor.execute("""
                UPDATE signals
                SET outcome = ?,
                    exit_price = ?,
                    profit_loss_pct = ?,
                    exit_timestamp = ?
                WHERE signal_id = ?
            """, (outcome, exit_price, pnl_pct, exit_ts, signal_id))
            
            conn.commit()
            logger.info(f"✅ Updated outcome for signal {signal_id}: {outcome} ({pnl_pct:.2f}%)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update outcome: {e}", exc_info=True)
            if conn:
                try:
                    conn.rollback()
                except Exception:
                    pass
            return False
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass
    
    def track_open_signals(self, current_prices: Dict[str, float]) -> int:
        """
        Track outcomes for open signals based on current prices
        
        Args:
            current_prices: Dict of {symbol: current_price}
        
        Returns:
            Number of signals updated
        """
        if not self.db_file.exists():
            return 0
        
        conn = None
        try:
            conn = sqlite3.connect(str(self.db_file))
            cursor = conn.cursor()
            
            # Get open signals (no outcome yet)
            cursor.execute("""
                SELECT signal_id, symbol, entry_price, target_price, stop_price, action, timestamp
                FROM signals
                WHERE outcome IS NULL
                AND timestamp >= datetime('now', '-30 days')
            """)
            
            signals = cursor.fetchall()
            updated_count = 0
            
            for signal_id, symbol, entry_price, target_price, stop_price, action, timestamp in signals:
                if symbol not in current_prices:
                    continue
                
                current_price = current_prices[symbol]
                
                # Check if target or stop loss hit
                should_exit = False
                outcome = None
                
                if target_price and stop_price:
                    if action == 'BUY':
                        if current_price >= target_price:
                            should_exit = True
                            outcome = 'win'
                        elif current_price <= stop_price:
                            should_exit = True
                            outcome = 'loss'
                    else:  # SELL
                        if current_price <= target_price:
                            should_exit = True
                            outcome = 'win'
                        elif current_price >= stop_price:
                            should_exit = True
                            outcome = 'loss'
                
                # Check for expiration (30 days old)
                signal_date = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                if datetime.utcnow() - signal_date.replace(tzinfo=None) > timedelta(days=30):
                    should_exit = True
                    outcome = 'expired'
                
                if should_exit:
                    if self.update_outcome(signal_id, current_price, outcome=outcome):
                        updated_count += 1
            
            if updated_count > 0:
                logger.info(f"✅ Updated {updated_count} signal outcomes")
            
            return updated_count
            
        except Exception as e:
            logger.error(f"❌ Failed to track open signals: {e}", exc_info=True)
            return 0
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass
    
    def get_outcome_statistics(self, days: int = 30) -> Dict:
        """
        Get outcome statistics for recent signals
        
        Args:
            days: Number of days to look back
        
        Returns:
            Statistics dictionary
        """
        if not self.db_file.exists():
            return {}
        
        conn = None
        try:
            conn = sqlite3.connect(str(self.db_file))
            cursor = conn.cursor()
            
            cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
            
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN outcome = 'win' THEN 1 ELSE 0 END) as wins,
                    SUM(CASE WHEN outcome = 'loss' THEN 1 ELSE 0 END) as losses,
                    SUM(CASE WHEN outcome = 'expired' THEN 1 ELSE 0 END) as expired,
                    AVG(CASE WHEN outcome = 'win' THEN profit_loss_pct END) as avg_win_pct,
                    AVG(CASE WHEN outcome = 'loss' THEN profit_loss_pct END) as avg_loss_pct
                FROM signals
                WHERE timestamp >= ?
                AND outcome IS NOT NULL
            """, (cutoff_date,))
            
            result = cursor.fetchone()
            
            if result:
                total, wins, losses, expired, avg_win, avg_loss = result
                wins = wins or 0
                losses = losses or 0
                expired = expired or 0
                completed = wins + losses + expired
                win_rate = (wins / completed * 100) if completed > 0 else 0
                
                return {
                    'total_signals': total,
                    'completed': completed,
                    'wins': wins or 0,
                    'losses': losses or 0,
                    'expired': expired or 0,
                    'win_rate': round(win_rate, 2),
                    'avg_win_pct': round(avg_win or 0, 2),
                    'avg_loss_pct': round(avg_loss or 0, 2),
                    'period_days': days
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"❌ Failed to get statistics: {e}", exc_info=True)
            return {}
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass


if __name__ == '__main__':
    tracker = OutcomeTracker()
    
    # Example: Get statistics
    stats = tracker.get_outcome_statistics(days=30)
    print(f"Outcome Statistics (30 days):")
    print(f"  Total: {stats.get('total_signals', 0)}")
    print(f"  Wins: {stats.get('wins', 0)}")
    print(f"  Losses: {stats.get('losses', 0)}")
    print(f"  Win Rate: {stats.get('win_rate', 0)}%")


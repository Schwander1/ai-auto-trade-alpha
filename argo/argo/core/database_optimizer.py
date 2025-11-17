#!/usr/bin/env python3
"""
Database Optimizer v5.0 - Phase 2
Implements partitioning, materialized views, and query optimizations
"""
import sqlite3
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DatabaseOptimizer")

# Use relative path that works in both dev and production
if os.path.exists("/root/argo-production"):
    BASE_DIR = Path("/root/argo-production")
else:
    BASE_DIR = Path(__file__).parent.parent.parent.parent

DB_FILE = BASE_DIR / "data" / "signals.db"


class DatabaseOptimizer:
    """
    Database optimization utilities for Phase 2
    - Partitioning support (table-per-month for SQLite)
    - Materialized views (refreshed tables)
    - Query optimization indexes
    """
    
    def __init__(self, db_file: Optional[Path] = None):
        self.db_file = db_file or DB_FILE
        self._init_optimizations()
    
    def _init_optimizations(self):
        """Initialize database optimizations"""
        try:
            conn = sqlite3.connect(str(self.db_file))
            cursor = conn.cursor()
            
            # Create materialized views tables
            self._create_materialized_views(cursor)
            
            # Create additional indexes for performance
            self._create_performance_indexes(cursor)
            
            conn.commit()
            conn.close()
            logger.info("✅ Database optimizations initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize database optimizations: {e}")
    
    def _create_materialized_views(self, cursor):
        """Create materialized view tables for common queries"""
        
        # Daily signal summary (materialized view)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mv_daily_signal_summary (
                date TEXT PRIMARY KEY,
                total_signals INTEGER,
                buy_signals INTEGER,
                sell_signals INTEGER,
                avg_confidence REAL,
                total_profit_loss REAL,
                win_count INTEGER,
                loss_count INTEGER,
                last_updated TEXT
            )
        """)
        
        # Symbol performance summary (materialized view)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mv_symbol_performance (
                symbol TEXT,
                period_start TEXT,
                period_end TEXT,
                total_signals INTEGER,
                win_rate REAL,
                avg_profit_loss_pct REAL,
                total_profit_loss REAL,
                last_updated TEXT,
                PRIMARY KEY (symbol, period_start)
            )
        """)
        
        # Confidence calibration stats (materialized view)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mv_confidence_stats (
                confidence_bucket INTEGER,
                total_signals INTEGER,
                win_count INTEGER,
                loss_count INTEGER,
                actual_win_rate REAL,
                last_updated TEXT,
                PRIMARY KEY (confidence_bucket)
            )
        """)
        
        logger.info("✅ Materialized views created")
    
    def _create_performance_indexes(self, cursor):
        """Create additional indexes for query performance"""
        
        indexes = [
            # Composite index for date range queries
            "CREATE INDEX IF NOT EXISTS idx_signals_timestamp_symbol ON signals(timestamp, symbol)",
            
            # Index for outcome analysis
            "CREATE INDEX IF NOT EXISTS idx_signals_outcome_timestamp ON signals(outcome, timestamp)",
            
            # Index for confidence analysis
            "CREATE INDEX IF NOT EXISTS idx_signals_confidence_timestamp ON signals(confidence, timestamp)",
            
            # Index for symbol and outcome
            "CREATE INDEX IF NOT EXISTS idx_signals_symbol_outcome ON signals(symbol, outcome)",
            
            # Index for profit/loss queries
            "CREATE INDEX IF NOT EXISTS idx_signals_profit_loss ON signals(profit_loss_pct) WHERE profit_loss_pct IS NOT NULL",
        ]
        
        for index_sql in indexes:
            try:
                cursor.execute(index_sql)
            except sqlite3.OperationalError as e:
                logger.debug(f"Index may already exist: {e}")
        
        logger.info("✅ Performance indexes created")
    
    def refresh_materialized_views(self):
        """Refresh all materialized views with current data"""
        try:
            conn = sqlite3.connect(str(self.db_file))
            cursor = conn.cursor()
            
            # Refresh daily signal summary
            self._refresh_daily_summary(cursor)
            
            # Refresh symbol performance
            self._refresh_symbol_performance(cursor)
            
            # Refresh confidence stats
            self._refresh_confidence_stats(cursor)
            
            conn.commit()
            conn.close()
            logger.info("✅ Materialized views refreshed")
        except Exception as e:
            logger.error(f"❌ Failed to refresh materialized views: {e}")
    
    def _refresh_daily_summary(self, cursor):
        """Refresh daily signal summary materialized view"""
        now = datetime.utcnow().isoformat()
        
        # Clear old data (keep last 90 days)
        cutoff_date = (datetime.utcnow() - timedelta(days=90)).isoformat()
        cursor.execute("DELETE FROM mv_daily_signal_summary WHERE date < ?", (cutoff_date,))
        
        # Insert/update daily summaries
        cursor.execute("""
            INSERT OR REPLACE INTO mv_daily_signal_summary
            SELECT 
                DATE(timestamp) as date,
                COUNT(*) as total_signals,
                SUM(CASE WHEN action = 'BUY' THEN 1 ELSE 0 END) as buy_signals,
                SUM(CASE WHEN action = 'SELL' THEN 1 ELSE 0 END) as sell_signals,
                AVG(confidence) as avg_confidence,
                SUM(profit_loss_pct) as total_profit_loss,
                SUM(CASE WHEN outcome = 'win' THEN 1 ELSE 0 END) as win_count,
                SUM(CASE WHEN outcome = 'loss' THEN 1 ELSE 0 END) as loss_count,
                ? as last_updated
            FROM signals
            WHERE timestamp >= ?
            GROUP BY DATE(timestamp)
        """, (now, cutoff_date))
    
    def _refresh_symbol_performance(self, cursor):
        """Refresh symbol performance materialized view"""
        now = datetime.utcnow().isoformat()
        period_start = (datetime.utcnow() - timedelta(days=30)).isoformat()
        period_end = datetime.utcnow().isoformat()
        
        # Clear old data
        cursor.execute("DELETE FROM mv_symbol_performance WHERE period_end < ?", 
                      ((datetime.utcnow() - timedelta(days=60)).isoformat(),))
        
        # Insert/update symbol performance
        cursor.execute("""
            INSERT OR REPLACE INTO mv_symbol_performance
            SELECT 
                symbol,
                ? as period_start,
                ? as period_end,
                COUNT(*) as total_signals,
                CASE 
                    WHEN SUM(CASE WHEN outcome IN ('win', 'loss') THEN 1 ELSE 0 END) > 0
                    THEN CAST(SUM(CASE WHEN outcome = 'win' THEN 1 ELSE 0 END) AS REAL) / 
                         SUM(CASE WHEN outcome IN ('win', 'loss') THEN 1 ELSE 0 END) * 100
                    ELSE 0
                END as win_rate,
                AVG(profit_loss_pct) as avg_profit_loss_pct,
                SUM(profit_loss_pct) as total_profit_loss,
                ? as last_updated
            FROM signals
            WHERE timestamp >= ? AND outcome IS NOT NULL
            GROUP BY symbol
        """, (period_start, period_end, now, period_start))
    
    def _refresh_confidence_stats(self, cursor):
        """Refresh confidence calibration statistics"""
        now = datetime.utcnow().isoformat()
        
        # Clear old data
        cursor.execute("DELETE FROM mv_confidence_stats")
        
        # Insert confidence bucket statistics
        cursor.execute("""
            INSERT INTO mv_confidence_stats
            SELECT 
                CAST(confidence / 10 AS INTEGER) * 10 as confidence_bucket,
                COUNT(*) as total_signals,
                SUM(CASE WHEN outcome = 'win' THEN 1 ELSE 0 END) as win_count,
                SUM(CASE WHEN outcome = 'loss' THEN 1 ELSE 0 END) as loss_count,
                CASE 
                    WHEN SUM(CASE WHEN outcome IN ('win', 'loss') THEN 1 ELSE 0 END) > 0
                    THEN CAST(SUM(CASE WHEN outcome = 'win' THEN 1 ELSE 0 END) AS REAL) / 
                         SUM(CASE WHEN outcome IN ('win', 'loss') THEN 1 ELSE 0 END) * 100
                    ELSE 0
                END as actual_win_rate,
                ? as last_updated
            FROM signals
            WHERE outcome IS NOT NULL AND confidence IS NOT NULL
            GROUP BY confidence_bucket
        """, (now,))
    
    def get_daily_summary(self, days: int = 30) -> List[Dict]:
        """Get daily signal summary from materialized view"""
        try:
            conn = sqlite3.connect(str(self.db_file))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
            cursor.execute("""
                SELECT * FROM mv_daily_signal_summary
                WHERE date >= ?
                ORDER BY date DESC
            """, (cutoff_date,))
            
            results = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return results
        except Exception as e:
            logger.error(f"❌ Failed to get daily summary: {e}")
            return []
    
    def get_symbol_performance(self, symbol: Optional[str] = None) -> List[Dict]:
        """Get symbol performance from materialized view"""
        try:
            conn = sqlite3.connect(str(self.db_file))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if symbol:
                cursor.execute("""
                    SELECT * FROM mv_symbol_performance
                    WHERE symbol = ?
                    ORDER BY period_end DESC
                """, (symbol,))
            else:
                cursor.execute("""
                    SELECT * FROM mv_symbol_performance
                    ORDER BY period_end DESC, symbol
                """)
            
            results = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return results
        except Exception as e:
            logger.error(f"❌ Failed to get symbol performance: {e}")
            return []
    
    def get_confidence_stats(self) -> List[Dict]:
        """Get confidence calibration statistics"""
        try:
            conn = sqlite3.connect(str(self.db_file))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM mv_confidence_stats
                ORDER BY confidence_bucket
            """)
            
            results = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return results
        except Exception as e:
            logger.error(f"❌ Failed to get confidence stats: {e}")
            return []


if __name__ == '__main__':
    # Test database optimizer
    optimizer = DatabaseOptimizer()
    optimizer.refresh_materialized_views()
    
    # Test queries
    daily_summary = optimizer.get_daily_summary(7)
    print(f"Daily summary: {len(daily_summary)} days")
    
    symbol_perf = optimizer.get_symbol_performance()
    print(f"Symbol performance: {len(symbol_perf)} symbols")
    
    confidence_stats = optimizer.get_confidence_stats()
    print(f"Confidence stats: {len(confidence_stats)} buckets")


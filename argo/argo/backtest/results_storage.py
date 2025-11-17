#!/usr/bin/env python3
"""
Results Storage
Stores backtest results in database for analysis
ENHANCED: Added new risk metrics, connection pooling, and query optimization
"""
import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from argo.backtest.base_backtester import BacktestMetrics
from argo.backtest.constants import DatabaseConstants
import logging
import threading

logger = logging.getLogger(__name__)

class ResultsStorage:
    """
    Stores backtest results with connection pooling and enhanced metrics
    ENHANCED: Added new risk metrics, connection pooling, query optimization
    """

    def __init__(self, db_path: str = "argo/data/backtest_results.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._local = threading.local()  # Thread-local storage for connections
        self._init_database()

    def _get_connection(self) -> sqlite3.Connection:
        """Get thread-local database connection with pooling"""
        if not hasattr(self._local, 'connection') or self._local.connection is None:
            conn = sqlite3.connect(
                str(self.db_path),
                timeout=DatabaseConstants.SQLITE_CONNECTION_TIMEOUT,
                check_same_thread=False
            )
            # Optimize SQLite settings
            conn.execute(f"PRAGMA synchronous = {DatabaseConstants.SQLITE_SYNCHRONOUS}")
            conn.execute(f"PRAGMA cache_size = -{DatabaseConstants.SQLITE_CACHE_SIZE_KB}")
            conn.execute(f"PRAGMA temp_store = {DatabaseConstants.SQLITE_TEMP_STORE}")
            conn.execute(f"PRAGMA mmap_size = {DatabaseConstants.SQLITE_MMAP_SIZE_BYTES}")
            conn.row_factory = sqlite3.Row  # Enable column access by name
            self._local.connection = conn
        return self._local.connection

    def _init_database(self):
        """Initialize database tables with enhanced schema"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # ENHANCED: Added new risk metrics columns
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS backtest_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                backtest_id TEXT UNIQUE,
                symbol TEXT NOT NULL,
                start_date TEXT,
                end_date TEXT,
                strategy_type TEXT,
                initial_capital REAL,
                final_capital REAL,
                total_return_pct REAL,
                annualized_return_pct REAL,
                sharpe_ratio REAL,
                sortino_ratio REAL,
                max_drawdown_pct REAL,
                win_rate_pct REAL,
                profit_factor REAL,
                total_trades INTEGER,
                winning_trades INTEGER,
                losing_trades INTEGER,
                avg_win_pct REAL,
                avg_loss_pct REAL,
                largest_win_pct REAL,
                largest_loss_pct REAL,
                -- ENHANCED: New risk metrics
                var_95_pct REAL,
                cvar_95_pct REAL,
                calmar_ratio REAL,
                omega_ratio REAL,
                ulcer_index REAL,
                metrics_json TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create indexes for faster queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_symbol ON backtest_results(symbol)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_strategy_type ON backtest_results(strategy_type)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_created_at ON backtest_results(created_at)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_total_return ON backtest_results(total_return_pct)
        ''')

        conn.commit()
        logger.info("Database initialized with enhanced schema and indexes")

    def save_results(
        self,
        backtest_id: str,
        symbol: str,
        metrics: BacktestMetrics,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        strategy_type: str = "strategy",
        initial_capital: Optional[float] = None
    ):
        """
        Save backtest results with enhanced metrics
        ENHANCED: Includes new risk metrics, uses connection pooling
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        if initial_capital is None:
            initial_capital = 100000.0

        final_capital = initial_capital * (1 + metrics.total_return_pct / 100)

        # ENHANCED: Include all metrics including new risk metrics
        metrics_dict = {
            'total_return_pct': metrics.total_return_pct,
            'annualized_return_pct': metrics.annualized_return_pct,
            'sharpe_ratio': metrics.sharpe_ratio,
            'sortino_ratio': metrics.sortino_ratio,
            'max_drawdown_pct': metrics.max_drawdown_pct,
            'win_rate_pct': metrics.win_rate_pct,
            'profit_factor': metrics.profit_factor,
            'total_trades': metrics.total_trades,
            'winning_trades': metrics.winning_trades,
            'losing_trades': metrics.losing_trades,
            'avg_win_pct': metrics.avg_win_pct,
            'avg_loss_pct': metrics.avg_loss_pct,
            'largest_win_pct': metrics.largest_win_pct,
            'largest_loss_pct': metrics.largest_loss_pct,
            # ENHANCED: New risk metrics
            'var_95_pct': getattr(metrics, 'var_95_pct', 0.0),
            'cvar_95_pct': getattr(metrics, 'cvar_95_pct', 0.0),
            'calmar_ratio': getattr(metrics, 'calmar_ratio', 0.0),
            'omega_ratio': getattr(metrics, 'omega_ratio', 0.0),
            'ulcer_index': getattr(metrics, 'ulcer_index', 0.0)
        }

        cursor.execute('''
            INSERT OR REPLACE INTO backtest_results (
                backtest_id, symbol, start_date, end_date, strategy_type,
                initial_capital, final_capital, total_return_pct,
                annualized_return_pct, sharpe_ratio, sortino_ratio,
                max_drawdown_pct, win_rate_pct, profit_factor,
                total_trades, winning_trades, losing_trades,
                avg_win_pct, avg_loss_pct, largest_win_pct, largest_loss_pct,
                var_95_pct, cvar_95_pct, calmar_ratio, omega_ratio, ulcer_index,
                metrics_json, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (
            backtest_id, symbol,
            start_date.isoformat() if start_date else None,
            end_date.isoformat() if end_date else None,
            strategy_type,
            initial_capital,
            final_capital,
            metrics.total_return_pct,
            metrics.annualized_return_pct,
            metrics.sharpe_ratio,
            metrics.sortino_ratio,
            metrics.max_drawdown_pct,
            metrics.win_rate_pct,
            metrics.profit_factor,
            metrics.total_trades,
            metrics.winning_trades,
            metrics.losing_trades,
            metrics.avg_win_pct,
            metrics.avg_loss_pct,
            metrics.largest_win_pct,
            metrics.largest_loss_pct,
            # ENHANCED: New risk metrics
            getattr(metrics, 'var_95_pct', 0.0),
            getattr(metrics, 'cvar_95_pct', 0.0),
            getattr(metrics, 'calmar_ratio', 0.0),
            getattr(metrics, 'omega_ratio', 0.0),
            getattr(metrics, 'ulcer_index', 0.0),
            json.dumps(metrics_dict)
        ))

        conn.commit()
        logger.info(f"Saved backtest results: {backtest_id} for {symbol}")

    def get_results(
        self,
        backtest_id: Optional[str] = None,
        symbol: Optional[str] = None,
        strategy_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Retrieve backtest results with filtering
        ENHANCED: Optimized queries with indexes
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM backtest_results WHERE 1=1"
        params = []

        if backtest_id:
            query += " AND backtest_id = ?"
            params.append(backtest_id)
        if symbol:
            query += " AND symbol = ?"
            params.append(symbol)
        if strategy_type:
            query += " AND strategy_type = ?"
            params.append(strategy_type)

        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()

        results = []
        for row in rows:
            result = dict(row)
            # Parse JSON metrics
            if result.get('metrics_json'):
                result['metrics'] = json.loads(result['metrics_json'])
            results.append(result)

        return results

    def compare_results(
        self,
        backtest_ids: List[str]
    ) -> Dict:
        """
        Compare multiple backtest results
        ENHANCED: New utility for comparing backtests
        """
        results = []
        for backtest_id in backtest_ids:
            result = self.get_results(backtest_id=backtest_id)
            if result:
                results.append(result[0])

        if len(results) < 2:
            return {"error": "Need at least 2 backtests to compare"}

        comparison = {
            'backtest_ids': backtest_ids,
            'count': len(results),
            'metrics': {}
        }

        # Compare key metrics
        metrics_to_compare = [
            'total_return_pct', 'annualized_return_pct', 'sharpe_ratio',
            'sortino_ratio', 'max_drawdown_pct', 'win_rate_pct',
            'profit_factor', 'calmar_ratio', 'var_95_pct'
        ]

        for metric in metrics_to_compare:
            values = [r.get(metric, 0) for r in results]
            comparison['metrics'][metric] = {
                'values': values,
                'best': max(values) if values else 0,
                'worst': min(values) if values else 0,
                'average': sum(values) / len(values) if values else 0,
                'std_dev': (sum((x - sum(values)/len(values))**2 for x in values) / len(values))**0.5 if len(values) > 1 else 0
            }

        return comparison

    def close(self):
        """Close database connection"""
        if hasattr(self._local, 'connection') and self._local.connection:
            self._local.connection.close()
            self._local.connection = None

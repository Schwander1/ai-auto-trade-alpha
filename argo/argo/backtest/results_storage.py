#!/usr/bin/env python3
"""
Results Storage
Stores backtest results in database for analysis
"""
import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from argo.backtest.base_backtester import BacktestMetrics
import logging

logger = logging.getLogger(__name__)

class ResultsStorage:
    """Stores backtest results"""
    
    def __init__(self, db_path: str = "argo/data/backtest_results.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        
    def _init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
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
                metrics_json TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_results(
        self,
        backtest_id: str,
        symbol: str,
        metrics: BacktestMetrics,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        strategy_type: str = "strategy"
    ):
        """Save backtest results"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
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
            'largest_loss_pct': metrics.largest_loss_pct
        }
        
        cursor.execute('''
            INSERT OR REPLACE INTO backtest_results (
                backtest_id, symbol, start_date, end_date, strategy_type,
                initial_capital, final_capital, total_return_pct,
                annualized_return_pct, sharpe_ratio, sortino_ratio,
                max_drawdown_pct, win_rate_pct, profit_factor,
                total_trades, winning_trades, losing_trades, metrics_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            backtest_id, symbol,
            start_date.isoformat() if start_date else None,
            end_date.isoformat() if end_date else None,
            strategy_type,
            100000,  # initial_capital
            100000 * (1 + metrics.total_return_pct / 100),  # final_capital
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
            json.dumps(metrics_dict)
        ))
        
        conn.commit()
        conn.close()
        logger.info(f"Saved backtest results: {backtest_id}")


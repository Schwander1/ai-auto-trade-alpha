#!/usr/bin/env python3
"""
Database Index Definitions
Centralized database index creation for SQLite
"""
from typing import List, Tuple


class DatabaseIndexes:
    """Database index definitions for signals table"""
    
    SIGNAL_INDEXES: List[Tuple[str, str]] = [
        ('idx_symbol', 'signals(symbol)'),
        ('idx_timestamp', 'signals(timestamp)'),
        ('idx_outcome', 'signals(outcome)'),
        ('idx_confidence', 'signals(confidence)'),
        ('idx_created_at', 'signals(created_at)'),
        ('idx_symbol_timestamp', 'signals(symbol, timestamp)'),
        ('idx_symbol_outcome', 'signals(symbol, outcome)'),
        ('idx_timestamp_outcome', 'signals(timestamp, outcome)'),
        ('idx_symbol_timestamp_confidence', 'signals(symbol, timestamp DESC, confidence DESC)'),
        ('idx_timestamp_outcome_confidence', 'signals(timestamp DESC, outcome, confidence DESC)'),
    ]
    
    @staticmethod
    def create_all_indexes(cursor) -> None:
        """
        Create all indexes for signals table.
        
        Args:
            cursor: SQLite cursor object
        """
        for index_name, index_def in DatabaseIndexes.SIGNAL_INDEXES:
            cursor.execute(f'CREATE INDEX IF NOT EXISTS {index_name} ON {index_def}')


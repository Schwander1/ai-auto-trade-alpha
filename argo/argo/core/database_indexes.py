#!/usr/bin/env python3
"""
Database Index Definitions
Centralized database index creation for SQLite
"""
from typing import List, Tuple


class DatabaseIndexes:
    """Database index definitions for signals table"""
    
    SIGNAL_INDEXES: List[Tuple[str, str]] = [
        # Single column indexes
        ('idx_symbol', 'signals(symbol)'),
        ('idx_timestamp', 'signals(timestamp)'),
        ('idx_outcome', 'signals(outcome)'),
        ('idx_confidence', 'signals(confidence)'),
        ('idx_created_at', 'signals(created_at)'),
        # Composite indexes for common query patterns
        ('idx_symbol_timestamp', 'signals(symbol, timestamp)'),
        ('idx_symbol_outcome', 'signals(symbol, outcome)'),
        ('idx_timestamp_outcome', 'signals(timestamp, outcome)'),
        # Recommended composite indexes for better performance
        ('idx_symbol_confidence', 'signals(symbol, confidence)'),
        ('idx_created_outcome', 'signals(created_at, outcome)'),
        ('idx_confidence_outcome', 'signals(confidence, outcome)'),
        # Complex composite indexes for advanced queries
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


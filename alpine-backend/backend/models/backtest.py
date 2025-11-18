"""Backtest database model"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON, Index, Enum as SQLEnum, ForeignKey, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, validates
from enum import Enum as PyEnum
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from backend.core.database import Base


class BacktestStatus(str, PyEnum):
    """Backtest status enumeration"""
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Backtest(Base):
    """
    Backtest result model
    
    Features:
    - User-specific backtests
    - Status tracking
    - JSON results storage
    - Date range validation
    - Capital and risk management
    """
    __tablename__ = "backtests"

    __table_args__ = (
        # Composite index for common query pattern: user backtests by creation date
        Index('idx_backtest_user_created', 'user_id', 'created_at'),
        # Index for status-based queries
        Index('idx_backtest_status_created', 'status', 'created_at'),
        # Check constraint for date range
        CheckConstraint('end_date > start_date', name='check_date_range'),
        # Check constraint for initial capital
        CheckConstraint('initial_capital > 0', name='check_initial_capital_positive'),
        # Check constraint for risk per trade
        CheckConstraint('risk_per_trade >= 0 AND risk_per_trade <= 1', name='check_risk_per_trade_range'),
    )

    id = Column(Integer, primary_key=True, index=True)
    backtest_id = Column(String(255), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=True)  # Optional: user-specific backtests
    symbol = Column(String(20), nullable=False, index=True)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    initial_capital = Column(Float, nullable=False)
    strategy = Column(String(100), default="default", nullable=False)
    risk_per_trade = Column(Float, default=0.02, nullable=False)  # 0.0 to 1.0 (0% to 100%)
    status = Column(SQLEnum(BacktestStatus), default=BacktestStatus.RUNNING, index=True, nullable=False)
    results = Column(JSON, nullable=True)  # Store backtest results as JSON
    error = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True, nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user: Optional["User"] = relationship("User", backref="backtests", lazy="select")
    
    @validates('backtest_id')
    def validate_backtest_id(self, key: str, backtest_id: str) -> str:
        """Validate backtest ID"""
        if not backtest_id:
            raise ValueError("Backtest ID is required")
        backtest_id = backtest_id.strip()
        if len(backtest_id) > 255:
            raise ValueError("Backtest ID must be 255 characters or less")
        return backtest_id
    
    @validates('symbol')
    def validate_symbol(self, key: str, symbol: str) -> str:
        """Validate symbol format"""
        if not symbol:
            raise ValueError("Symbol is required")
        symbol = symbol.strip().upper()
        if len(symbol) > 20:
            raise ValueError("Symbol must be 20 characters or less")
        return symbol
    
    @validates('strategy')
    def validate_strategy(self, key: str, strategy: str) -> str:
        """Validate strategy name"""
        if not strategy:
            strategy = "default"
        strategy = strategy.strip()
        if len(strategy) > 100:
            raise ValueError("Strategy name must be 100 characters or less")
        return strategy
    
    @validates('initial_capital')
    def validate_initial_capital(self, key: str, initial_capital: float) -> float:
        """Validate initial capital is positive"""
        if initial_capital <= 0:
            raise ValueError("Initial capital must be greater than 0")
        return initial_capital
    
    @validates('risk_per_trade')
    def validate_risk_per_trade(self, key: str, risk_per_trade: float) -> float:
        """Validate risk per trade is in valid range (0-1)"""
        if risk_per_trade < 0 or risk_per_trade > 1:
            raise ValueError("Risk per trade must be between 0 and 1 (0% to 100%)")
        return risk_per_trade
    
    @validates('end_date')
    def validate_end_date(self, key: str, end_date: Any) -> Any:
        """Validate end date is after start date"""
        if hasattr(self, 'start_date') and self.start_date and end_date:
            if end_date <= self.start_date:
                raise ValueError("End date must be after start date")
        return end_date
    
    def mark_completed(self, results: Optional[Dict[str, Any]] = None) -> None:
        """Mark backtest as completed"""
        self.status = BacktestStatus.COMPLETED
        if results is not None:
            self.results = results
        self.completed_at = datetime.now(timezone.utc)
    
    def mark_failed(self, error: str) -> None:
        """Mark backtest as failed"""
        self.status = BacktestStatus.FAILED
        self.error = error
        self.completed_at = datetime.now(timezone.utc)
    
    def __repr__(self) -> str:
        """String representation for debugging"""
        return f"<Backtest(id={self.id}, backtest_id='{self.backtest_id}', symbol='{self.symbol}', status='{self.status}')>"

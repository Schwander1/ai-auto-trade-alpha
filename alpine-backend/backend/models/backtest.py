"""Backtest database model"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON
from sqlalchemy.sql import func
from backend.core.database import Base


class Backtest(Base):
    """Backtest result model"""
    __tablename__ = "backtests"
    
    id = Column(Integer, primary_key=True, index=True)
    backtest_id = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, index=True, nullable=True)  # Optional: user-specific backtests
    symbol = Column(String, nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    initial_capital = Column(Float, nullable=False)
    strategy = Column(String, default="default")
    risk_per_trade = Column(Float, default=0.02)
    status = Column(String, default="running")  # running, completed, failed
    results = Column(JSON, nullable=True)  # Store backtest results as JSON
    error = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)



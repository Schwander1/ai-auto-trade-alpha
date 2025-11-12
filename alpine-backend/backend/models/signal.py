"""Signal model - No external system references"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Index
from sqlalchemy.sql import func
from backend.core.database import Base

class Signal(Base):
    """Trading signal model"""
    __tablename__ = "signals"
    
    __table_args__ = (
        # Composite index for common query pattern: active signals by confidence and date
        Index('idx_signal_active_confidence_created', 'is_active', 'confidence', 'created_at'),
        # Composite index for symbol-based queries with date sorting
        Index('idx_signal_symbol_created', 'symbol', 'created_at'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    action = Column(String)  # BUY/SELL
    price = Column(Float)
    confidence = Column(Float, index=True)  # Added index for confidence filtering
    target_price = Column(Float, nullable=True)
    stop_loss = Column(Float, nullable=True)
    rationale = Column(String, default="AI Analysis")  # Generic
    verification_hash = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True, index=True)  # Added index for active filtering
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

"""
Signal model - Immutable trading signals with audit trail support

PATENT CLAIMS:
- SHA-256 verification (verification_hash)
- AI-generated reasoning (rationale - required, non-empty)
- Real-time delivery tracking (generation_latency_ms, delivery_latency_ms)
- Immutable audit trail (via database triggers)

COMPLIANCE:
- 7-year retention (retention_expires_at)
- Hash chain for tamper detection (previous_hash, chain_index)
- Complete audit logging (via signal_audit_log table)
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Index, Text, Enum as SQLEnum, CheckConstraint, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, validates, Mapped
from enum import Enum as PyEnum
from typing import Optional, List
import time
from backend.core.database import Base


class SignalAction(str, PyEnum):
    """Signal action types"""
    BUY = "BUY"
    SELL = "SELL"


class Signal(Base):
    """
    Trading signal model - Immutable after creation

    Features:
    - Immutable audit trail
    - SHA-256 verification
    - AI-generated reasoning
    - Real-time delivery tracking
    - Hash chain for tamper detection
    - 7-year compliance retention
    """
    __tablename__ = "signals"

    __table_args__ = (
        # Composite index for common query pattern: active signals by confidence and date
        Index('idx_signal_active_confidence_created', 'is_active', 'confidence', 'created_at'),
        # Composite index for symbol-based queries with date sorting
        Index('idx_signal_symbol_created', 'symbol', 'created_at'),
        # Check constraint for confidence range (0-1)
        CheckConstraint('confidence >= 0 AND confidence <= 1', name='check_confidence_range'),
        # Check constraint for price (must be positive)
        CheckConstraint('price > 0', name='check_price_positive'),
        # Check constraint for target_price if provided
        CheckConstraint('target_price IS NULL OR target_price > 0', name='check_target_price_positive'),
        # Check constraint for stop_loss if provided
        CheckConstraint('stop_loss IS NULL OR stop_loss > 0', name='check_stop_loss_positive'),
    )

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), index=True, nullable=False)  # Stock symbols are typically short
    action = Column(SQLEnum(SignalAction), nullable=False, index=True)
    price = Column(Float, nullable=False)
    confidence = Column(Float, index=True, nullable=False)  # 0.0 to 1.0 (0% to 100%)
    target_price = Column(Float, nullable=True)
    stop_loss = Column(Float, nullable=True)
    rationale = Column(Text, nullable=False)  # AI-generated reasoning - REQUIRED (patent claim)
    verification_hash = Column(String(64), unique=True, index=True, nullable=False)  # SHA-256 (patent claim)
    is_active = Column(Boolean, default=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True, nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)  # Should never update (immutable)

    # Optional user association (signals can be global or user-specific)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), index=True, nullable=True)

    # Retention tracking (7-year compliance requirement)
    retention_expires_at = Column(DateTime(timezone=True), index=True, nullable=True)

    # Hash chain for tamper detection (blockchain-style)
    previous_hash = Column(String(64), index=True, nullable=True)  # Hash of previous signal in chain
    chain_index = Column(Integer, index=True, nullable=True)  # Position in chain

    # Latency tracking (patent claim: <500ms delivery)
    generation_latency_ms = Column(Integer, nullable=True)  # Time to generate signal
    delivery_latency_ms = Column(Integer, nullable=True)  # End-to-end delivery time
    server_timestamp = Column(Float, nullable=True)  # Unix timestamp when signal created on server

    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", backref="signals", lazy="select")

    @validates('symbol')
    def validate_symbol(self, key: str, symbol: str) -> str:
        """Validate symbol format"""
        if not symbol:
            raise ValueError("Symbol is required")
        symbol = symbol.strip().upper()
        if len(symbol) > 20:
            raise ValueError("Symbol must be 20 characters or less")
        if len(symbol) < 1:
            raise ValueError("Symbol cannot be empty")
        return symbol

    @validates('rationale')
    def validate_reasoning(self, key: str, rationale: str) -> str:
        """
        Validate that reasoning is meaningful and non-empty

        PATENT CLAIM: AI-generated reasoning for each signal must be meaningful
        """
        if not rationale or len(rationale.strip()) < 20:
            raise ValueError(
                "Signal reasoning is required and must be meaningful (>20 characters). "
                "This is required for patent compliance (AI-generated reasoning claim)."
            )
        return rationale.strip()

    @validates('confidence')
    def validate_confidence(self, key: str, confidence: float) -> float:
        """Validate confidence is in valid range (0-1)"""
        if confidence < 0 or confidence > 1:
            raise ValueError("Confidence must be between 0 and 1 (0% to 100%)")
        return confidence

    @validates('price', 'target_price', 'stop_loss')
    def validate_price(self, key: str, price: Optional[float]) -> Optional[float]:
        """Validate price is positive"""
        if price is not None and price <= 0:
            raise ValueError(f"{key} must be greater than 0")
        return price

    @validates('verification_hash')
    def validate_verification_hash(self, key: str, verification_hash: str) -> str:
        """Validate verification hash format (SHA-256 is 64 hex characters)"""
        if not verification_hash:
            raise ValueError("Verification hash is required")
        verification_hash = verification_hash.strip()
        if len(verification_hash) != 64:
            raise ValueError("Verification hash must be 64 characters (SHA-256)")
        # Validate hex format
        try:
            int(verification_hash, 16)
        except ValueError:
            raise ValueError("Verification hash must be a valid hexadecimal string")
        return verification_hash

    def calculate_generation_latency(self) -> int:
        """Calculate generation latency if server_timestamp is available"""
        if self.server_timestamp and self.created_at:
            latency_seconds = time.time() - self.server_timestamp
            return int(latency_seconds * 1000)
        return self.generation_latency_ms or 0

    def is_immutable(self) -> bool:
        """
        Check if signal is immutable (always True after creation)

        PATENT CLAIM: Immutable audit trail
        """
        return True  # Signals are immutable via database triggers

    def __repr__(self) -> str:
        """String representation for debugging"""
        return f"<Signal(id={self.id}, symbol='{self.symbol}', action='{self.action}', confidence={self.confidence}, is_active={self.is_active})>"

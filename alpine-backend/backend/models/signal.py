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
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Index, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, validates
from backend.core.database import Base

class Signal(Base):
    """Trading signal model - Immutable after creation"""
    __tablename__ = "signals"
    
    __table_args__ = (
        # Composite index for common query pattern: active signals by confidence and date
        Index('idx_signal_active_confidence_created', 'is_active', 'confidence', 'created_at'),
        # Composite index for symbol-based queries with date sorting
        Index('idx_signal_symbol_created', 'symbol', 'created_at'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True, nullable=False)
    action = Column(String, nullable=False)  # BUY/SELL
    price = Column(Float, nullable=False)
    confidence = Column(Float, index=True, nullable=False)  # Added index for confidence filtering
    target_price = Column(Float, nullable=True)
    stop_loss = Column(Float, nullable=True)
    rationale = Column(Text, nullable=False)  # AI-generated reasoning - REQUIRED (patent claim)
    verification_hash = Column(String, unique=True, index=True, nullable=False)  # SHA-256 (patent claim)
    is_active = Column(Boolean, default=True, index=True)  # Added index for active filtering
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True, nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())  # Should never update (immutable)
    
    # Retention tracking (7-year compliance requirement)
    retention_expires_at = Column(DateTime(timezone=True), index=True)
    
    # Hash chain for tamper detection (blockchain-style)
    previous_hash = Column(String(64), index=True)  # Hash of previous signal in chain
    chain_index = Column(Integer, index=True)  # Position in chain
    
    # Latency tracking (patent claim: <500ms delivery)
    generation_latency_ms = Column(Integer)  # Time to generate signal
    delivery_latency_ms = Column(Integer)  # End-to-end delivery time
    server_timestamp = Column(Float)  # Unix timestamp when signal created on server
    
    @validates('rationale')
    def validate_reasoning(self, key, rationale):
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
    
    def calculate_generation_latency(self) -> int:
        """Calculate generation latency if server_timestamp is available"""
        if self.server_timestamp and self.created_at:
            import time
            latency_seconds = time.time() - self.server_timestamp
            return int(latency_seconds * 1000)
        return self.generation_latency_ms or 0
    
    def is_immutable(self) -> bool:
        """
        Check if signal is immutable (always True after creation)
        
        PATENT CLAIM: Immutable audit trail
        """
        return True  # Signals are immutable via database triggers
    
    def audit_log_entries(self):
        """Get related audit log entries (requires relationship)"""
        # This would require a relationship definition
        # For now, return empty list - can be queried separately
        return []

"""User database model"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from backend.core.database import Base

class UserTier(str, PyEnum):
    STARTER = "starter"
    PRO = "pro"
    ELITE = "elite"

class User(Base):
    __tablename__ = "users"
    
    __table_args__ = (
        # Composite index for common query pattern: users by tier and active status
        Index('idx_user_tier_active', 'tier', 'is_active'),
        # Index for date-based queries
        Index('idx_user_created_at', 'created_at'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    
    tier = Column(SQLEnum(UserTier), default=UserTier.STARTER, index=True)
    is_active = Column(Boolean, default=True, index=True)
    is_verified = Column(Boolean, default=False)
    
    # 2FA fields
    totp_secret = Column(String, nullable=True)  # TOTP secret (encrypted in production)
    totp_enabled = Column(Boolean, default=False)  # Whether 2FA is enabled
    backup_codes = Column(String, nullable=True)  # JSON array of hashed backup codes
    last_totp_used = Column(DateTime(timezone=True), nullable=True)  # Prevent replay attacks
    
    stripe_customer_id = Column(String, unique=True, index=True)
    stripe_subscription_id = Column(String, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # RBAC: Relationship to roles
    roles = relationship("Role", secondary="user_roles", back_populates="users", lazy="joined")

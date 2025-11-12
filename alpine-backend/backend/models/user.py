"""User database model"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum, Index
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
    
    stripe_customer_id = Column(String, unique=True, index=True)
    stripe_subscription_id = Column(String, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

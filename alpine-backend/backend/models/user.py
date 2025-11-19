"""User database model"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum, Index, CheckConstraint
from sqlalchemy.orm import relationship, validates, Mapped
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from typing import Optional, List
import re
from backend.core.database import Base

class UserTier(str, PyEnum):
    STARTER = "starter"
    PRO = "pro"
    ELITE = "elite"

class User(Base):
    """
    User database model with authentication, authorization, and subscription support.

    Features:
    - Email-based authentication
    - Role-Based Access Control (RBAC)
    - Two-Factor Authentication (2FA) support
    - Stripe subscription integration
    - User tier management
    """
    __tablename__ = "users"

    __table_args__ = (
        # Composite index for common query pattern: users by tier and active status
        Index('idx_user_tier_active', 'tier', 'is_active'),
        # Index for date-based queries
        Index('idx_user_created_at', 'created_at'),
        # Check constraint for email format (basic validation)
        CheckConstraint("email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}$'", name='check_email_format'),
    )

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)  # bcrypt hash is 60 chars, but allow extra space
    full_name = Column(String(255), nullable=True)

    tier = Column(SQLEnum(UserTier), default=UserTier.STARTER, index=True, nullable=False)
    is_active = Column(Boolean, default=True, index=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    # 2FA fields
    totp_secret = Column(String(32), nullable=True)  # TOTP secret (encrypted in production)
    totp_enabled = Column(Boolean, default=False, nullable=False)  # Whether 2FA is enabled
    backup_codes = Column(String(1000), nullable=True)  # JSON array of hashed backup codes
    last_totp_used = Column(DateTime(timezone=True), nullable=True)  # Prevent replay attacks

    stripe_customer_id = Column(String(255), unique=True, index=True, nullable=True)
    stripe_subscription_id = Column(String(255), index=True, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # RBAC: Relationship to roles
    roles: Mapped[List["Role"]] = relationship(
        "Role",
        secondary="user_roles",
        back_populates="users",
        lazy="joined"
    )

    @validates('email')
    def validate_email(self, key: str, email: str) -> str:
        """Validate email format"""
        if not email:
            raise ValueError("Email is required")
        email = email.lower().strip()
        # Basic email validation regex
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            raise ValueError("Invalid email format")
        if len(email) > 255:
            raise ValueError("Email must be 255 characters or less")
        return email

    @validates('full_name')
    def validate_full_name(self, key: str, full_name: Optional[str]) -> Optional[str]:
        """Validate full name"""
        if full_name is not None:
            full_name = full_name.strip()
            if len(full_name) > 255:
                raise ValueError("Full name must be 255 characters or less")
            if len(full_name) < 1:
                return None
        return full_name

    def __repr__(self) -> str:
        """String representation for debugging"""
        return f"<User(id={self.id}, email='{self.email}', tier='{self.tier}', is_active={self.is_active})>"

"""Notification database model"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Index, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, validates
from enum import Enum as PyEnum
from typing import Optional
from datetime import datetime, timezone
from backend.core.database import Base


class NotificationType(str, PyEnum):
    """Notification type enumeration"""
    INFO = "info"
    WARNING = "warning"
    SUCCESS = "success"
    ERROR = "error"
    SYSTEM = "system"


class Notification(Base):
    """
    User notification model
    
    Features:
    - User-specific notifications
    - Read/unread status tracking
    - Multiple notification types
    - Timestamp tracking
    """
    __tablename__ = "notifications"
    
    __table_args__ = (
        # Composite index for common query pattern: unread notifications by user and date
        Index('idx_notif_user_read_created', 'user_id', 'is_read', 'created_at'),
        # Index for type-based queries
        Index('idx_notif_type_created', 'type', 'created_at'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(SQLEnum(NotificationType), default=NotificationType.INFO, nullable=False, index=True)
    is_read = Column(Boolean, default=False, index=True, nullable=False)
    read_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True, nullable=False)
    
    # Relationship
    user: Optional["User"] = relationship("User", backref="notifications", lazy="select")
    
    @validates('title')
    def validate_title(self, key: str, title: str) -> str:
        """Validate title"""
        if not title:
            raise ValueError("Title is required")
        title = title.strip()
        if len(title) > 255:
            raise ValueError("Title must be 255 characters or less")
        if len(title) < 1:
            raise ValueError("Title cannot be empty")
        return title
    
    @validates('message')
    def validate_message(self, key: str, message: str) -> str:
        """Validate message"""
        if not message:
            raise ValueError("Message is required")
        message = message.strip()
        if len(message) < 1:
            raise ValueError("Message cannot be empty")
        return message
    
    def mark_as_read(self) -> None:
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = datetime.now(timezone.utc)
    
    def __repr__(self) -> str:
        """String representation for debugging"""
        return f"<Notification(id={self.id}, user_id={self.user_id}, type='{self.type}', is_read={self.is_read})>"



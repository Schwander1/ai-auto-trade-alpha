"""Role-Based Access Control (RBAC) models"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Table, ForeignKey, Enum as SQLEnum, Index
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from typing import Optional, List
from backend.core.database import Base

# Association table for many-to-many relationship between users and roles
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True)
)

# Association table for many-to-many relationship between roles and permissions
role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id', ondelete='CASCADE'), primary_key=True)
)


class PermissionEnum(str, PyEnum):
    """System permissions"""
    # User management
    USER_READ = "user:read"
    USER_WRITE = "user:write"
    USER_DELETE = "user:delete"
    
    # Admin permissions
    ADMIN_READ = "admin:read"
    ADMIN_WRITE = "admin:write"
    ADMIN_ANALYTICS = "admin:analytics"
    ADMIN_USERS = "admin:users"
    ADMIN_REVENUE = "admin:revenue"
    
    # Signal permissions
    SIGNAL_READ = "signal:read"
    SIGNAL_WRITE = "signal:write"
    SIGNAL_DELETE = "signal:delete"
    
    # Subscription permissions
    SUBSCRIPTION_READ = "subscription:read"
    SUBSCRIPTION_WRITE = "subscription:write"
    
    # Role management (super admin only)
    ROLE_MANAGE = "role:manage"


class Role(Base):
    """
    Role model for RBAC
    
    Features:
    - Role-based access control
    - System and custom roles
    - Permission associations
    - User associations
    """
    __tablename__ = "roles"
    
    __table_args__ = (
        # Index for system role queries
        Index('idx_role_system', 'is_system'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(String(500), nullable=True)
    is_system = Column(Boolean, default=False, nullable=False, index=True)  # System roles cannot be deleted
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Relationships
    users: List["User"] = relationship(
        "User", 
        secondary=user_roles, 
        back_populates="roles",
        lazy="select"
    )
    permissions: List["Permission"] = relationship(
        "Permission", 
        secondary=role_permissions, 
        back_populates="roles",
        lazy="select"
    )
    
    @validates('name')
    def validate_name(self, key: str, name: str) -> str:
        """Validate role name"""
        if not name:
            raise ValueError("Role name is required")
        name = name.strip().lower()
        if len(name) > 100:
            raise ValueError("Role name must be 100 characters or less")
        if len(name) < 1:
            raise ValueError("Role name cannot be empty")
        # Validate name format (alphanumeric, underscore, hyphen)
        if not all(c.isalnum() or c in ('_', '-') for c in name):
            raise ValueError("Role name can only contain alphanumeric characters, underscores, and hyphens")
        return name
    
    @validates('description')
    def validate_description(self, key: str, description: Optional[str]) -> Optional[str]:
        """Validate role description"""
        if description is not None:
            description = description.strip()
            if len(description) > 500:
                raise ValueError("Description must be 500 characters or less")
            if len(description) < 1:
                return None
        return description
    
    def __repr__(self) -> str:
        """String representation for debugging"""
        return f"<Role(id={self.id}, name='{self.name}', is_system={self.is_system})>"


class Permission(Base):
    """
    Permission model for RBAC
    
    Features:
    - Fine-grained permission control
    - Role associations
    - Permission enumeration support
    """
    __tablename__ = "permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    roles: List["Role"] = relationship(
        "Role", 
        secondary=role_permissions, 
        back_populates="permissions",
        lazy="select"
    )
    
    @validates('name')
    def validate_name(self, key: str, name: str) -> str:
        """Validate permission name"""
        if not name:
            raise ValueError("Permission name is required")
        name = name.strip()
        if len(name) > 100:
            raise ValueError("Permission name must be 100 characters or less")
        if len(name) < 1:
            raise ValueError("Permission name cannot be empty")
        # Validate format (should be like "resource:action")
        if ':' not in name:
            raise ValueError("Permission name must be in format 'resource:action' (e.g., 'user:read')")
        return name
    
    @validates('description')
    def validate_description(self, key: str, description: Optional[str]) -> Optional[str]:
        """Validate permission description"""
        if description is not None:
            description = description.strip()
            if len(description) > 500:
                raise ValueError("Description must be 500 characters or less")
            if len(description) < 1:
                return None
        return description
    
    def __repr__(self) -> str:
        """String representation for debugging"""
        return f"<Permission(id={self.id}, name='{self.name}')>"


# Default roles and permissions
DEFAULT_ROLES = {
    "admin": {
        "description": "Full system access",
        "permissions": [
            PermissionEnum.USER_READ,
            PermissionEnum.USER_WRITE,
            PermissionEnum.USER_DELETE,
            PermissionEnum.ADMIN_READ,
            PermissionEnum.ADMIN_WRITE,
            PermissionEnum.ADMIN_ANALYTICS,
            PermissionEnum.ADMIN_USERS,
            PermissionEnum.ADMIN_REVENUE,
            PermissionEnum.SIGNAL_READ,
            PermissionEnum.SIGNAL_WRITE,
            PermissionEnum.SIGNAL_DELETE,
            PermissionEnum.SUBSCRIPTION_READ,
            PermissionEnum.SUBSCRIPTION_WRITE,
            PermissionEnum.ROLE_MANAGE,
        ]
    },
    "moderator": {
        "description": "User management and content moderation",
        "permissions": [
            PermissionEnum.USER_READ,
            PermissionEnum.USER_WRITE,
            PermissionEnum.ADMIN_READ,
            PermissionEnum.ADMIN_USERS,
            PermissionEnum.SIGNAL_READ,
        ]
    },
    "support": {
        "description": "Read-only access to user data",
        "permissions": [
            PermissionEnum.USER_READ,
            PermissionEnum.ADMIN_READ,
            PermissionEnum.SIGNAL_READ,
        ]
    },
    "user": {
        "description": "Standard user access",
        "permissions": [
            PermissionEnum.SIGNAL_READ,
            PermissionEnum.SUBSCRIPTION_READ,
        ]
    }
}


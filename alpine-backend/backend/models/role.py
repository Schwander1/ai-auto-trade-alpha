"""Role-Based Access Control (RBAC) models"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Table, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum
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
    """Role model for RBAC"""
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    description = Column(String, nullable=True)
    is_system = Column(Boolean, default=False)  # System roles cannot be deleted
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    users = relationship("User", secondary=user_roles, back_populates="roles")
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")


class Permission(Base):
    """Permission model for RBAC"""
    __tablename__ = "permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")


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


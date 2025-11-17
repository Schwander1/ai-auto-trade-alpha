"""Role-Based Access Control (RBAC) utilities"""
from fastapi import HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from backend.core.database import get_db
from backend.models.user import User
from backend.models.role import Role, Permission, PermissionEnum, DEFAULT_ROLES
from backend.api.auth import get_current_user
from backend.core.error_responses import create_error_response, ErrorCodes
from backend.core.security_logging import log_unauthorized_access

logger = logging.getLogger(__name__)


def has_permission(user: User, permission: PermissionEnum) -> bool:
    """
    Check if user has a specific permission
    
    Args:
        user: User object
        permission: Permission to check
    
    Returns:
        True if user has permission, False otherwise
    """
    if not user.roles:
        return False
    
    # Check all user roles for the permission
    for role in user.roles:
        for perm in role.permissions:
            if perm.name == permission.value:
                return True
    
    return False


def has_any_permission(user: User, permissions: List[PermissionEnum]) -> bool:
    """Check if user has any of the specified permissions"""
    return any(has_permission(user, perm) for perm in permissions)


def has_all_permissions(user: User, permissions: List[PermissionEnum]) -> bool:
    """Check if user has all of the specified permissions"""
    return all(has_permission(user, perm) for perm in permissions)


def has_role(user: User, role_name: str) -> bool:
    """
    Check if user has a specific role
    
    Args:
        user: User object
        role_name: Name of role to check
    
    Returns:
        True if user has role, False otherwise
    """
    if not user.roles:
        return False
    
    return any(role.name == role_name for role in user.roles)


def require_permission(permission: PermissionEnum):
    """
    Dependency factory for permission checking
    
    Usage:
        @router.get("/admin/users")
        async def get_users(
            current_user: User = Depends(require_permission(PermissionEnum.ADMIN_USERS))
        ):
            ...
    """
    def _check_permission(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> User:
        # Refresh user roles from database
        db.refresh(current_user, ['roles'])
        
        if not has_permission(current_user, permission):
            log_unauthorized_access(
                user_id=current_user.id,
                email=current_user.email,
                resource=f"permission:{permission.value}",
                request=None
            )
            raise create_error_response(
                ErrorCodes.AUTHZ_001,
                f"Permission required: {permission.value}",
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        return current_user
    
    return _check_permission


def require_role(role_name: str):
    """
    Dependency factory for role checking
    
    Usage:
        @router.get("/admin/analytics")
        async def get_analytics(
            current_user: User = Depends(require_role("admin"))
        ):
            ...
    """
    def _check_role(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> User:
        # Refresh user roles from database
        db.refresh(current_user, ['roles'])
        
        if not has_role(current_user, role_name):
            log_unauthorized_access(
                user_id=current_user.id,
                email=current_user.email,
                resource=f"role:{role_name}",
                request=None
            )
            raise create_error_response(
                ErrorCodes.AUTHZ_002,
                f"Role required: {role_name}",
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        return current_user
    
    return _check_role


def is_admin(user: User, db: Optional[Session] = None) -> bool:
    """
    Check if user is admin (backward compatibility)
    
    Args:
        user: User object
        db: Optional database session to refresh roles
    
    Returns:
        True if user is admin, False otherwise
    """
    if db:
        db.refresh(user, ['roles'])
    
    # Check for admin role
    if has_role(user, "admin"):
        return True
    
    # Backward compatibility: check hardcoded admin emails
    from backend.api.admin import ADMIN_EMAILS
    return user.email in ADMIN_EMAILS


def initialize_default_roles(db: Session):
    """
    Initialize default roles and permissions in database
    
    Args:
        db: Database session
    """
    try:
        # Create permissions
        permission_map = {}
        for perm_enum in PermissionEnum:
            permission = db.query(Permission).filter(Permission.name == perm_enum.value).first()
            if not permission:
                permission = Permission(
                    name=perm_enum.value,
                    description=f"Permission: {perm_enum.value}"
                )
                db.add(permission)
            permission_map[perm_enum] = permission
        
        db.commit()
        
        # Create roles
        for role_name, role_data in DEFAULT_ROLES.items():
            role = db.query(Role).filter(Role.name == role_name).first()
            if not role:
                role = Role(
                    name=role_name,
                    description=role_data["description"],
                    is_system=True
                )
                db.add(role)
                db.flush()
            
            # Assign permissions to role
            for perm_enum in role_data["permissions"]:
                if perm_enum in permission_map:
                    if permission_map[perm_enum] not in role.permissions:
                        role.permissions.append(permission_map[perm_enum])
        
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Error initializing default roles and permissions: {e}", exc_info=True)
        raise


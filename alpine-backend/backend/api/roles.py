"""
Role management API endpoints for RBAC
GET roles, POST assign role, DELETE remove role
Admin only
"""
from fastapi import APIRouter, HTTPException, Depends, status, Header, Request, Response
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import time
import logging

from backend.core.database import get_db
from backend.core.rate_limit import check_rate_limit, get_rate_limit_status
from backend.core.response_formatter import add_rate_limit_headers
from backend.core.security_logging import log_security_event, SecurityEvent
from backend.core.error_responses import create_rate_limit_error
from backend.models.user import User
from backend.models.role import Role, Permission, PermissionEnum
from backend.core.rbac import require_permission, PermissionEnum as PermEnum, initialize_default_roles
from backend.api.auth import get_current_user
from backend.api.admin import require_admin

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/roles", tags=["roles"])

# Rate limiting
RATE_LIMIT_WINDOW = 60
RATE_LIMIT_MAX = 100


class RoleResponse(BaseModel):
    """Role response model"""
    id: int
    name: str
    description: Optional[str] = None
    is_system: bool
    permissions: List[str]
    created_at: str


class AssignRoleRequest(BaseModel):
    """Assign role request"""
    user_id: int = Field(..., description="User ID to assign role to")
    role_name: str = Field(..., description="Role name to assign")


class CreateRoleRequest(BaseModel):
    """Create role request"""
    name: str = Field(..., min_length=1, max_length=50, description="Role name")
    description: Optional[str] = Field(None, max_length=200, description="Role description")
    permissions: List[str] = Field(..., description="List of permission names")


@router.get("", response_model=List[RoleResponse])
async def get_roles(
    request: Request,
    response: Response,
    current_user: User = Depends(require_permission(PermEnum.ROLE_MANAGE)),
    db: Session = Depends(get_db)
):
    """
    Get all roles (admin only)
    """
    # Rate limiting
    client_id = current_user.email
    if not check_rate_limit(client_id):
        raise create_rate_limit_error(request=request)

    # Add rate limit headers
    rate_limit_status = get_rate_limit_status(client_id)
    add_rate_limit_headers(
        response,
        remaining=rate_limit_status["remaining"],
        reset_at=int(time.time()) + rate_limit_status["reset_in"]
    )

    # Log admin action
    log_security_event(
        SecurityEvent.ADMIN_ACTION,
        user_id=current_user.id,
        email=current_user.email,
        details={"action": "view_roles"},
        request=request
    )

    # OPTIMIZATION: Eager load permissions to prevent N+1 queries
    from sqlalchemy.orm import joinedload
    from backend.core.query_optimizer import optimize_query_with_relationships

    query = db.query(Role)
    query = optimize_query_with_relationships(query, Role, relationships=['permissions'], use_selectin=False)
    roles = query.all()

    return [
        RoleResponse(
            id=role.id,
            name=role.name,
            description=role.description,
            is_system=role.is_system,
            permissions=[perm.name for perm in role.permissions],
            created_at=role.created_at.isoformat() if role.created_at else datetime.utcnow().isoformat() + "Z"
        )
        for role in roles
    ]


@router.post("/assign", status_code=200)
async def assign_role(
    assign_data: AssignRoleRequest,
    request: Request,
    response: Response,
    current_user: User = Depends(require_permission(PermEnum.ROLE_MANAGE)),
    db: Session = Depends(get_db)
):
    """
    Assign role to user (admin only)
    """
    # Rate limiting
    client_id = current_user.email
    if not check_rate_limit(client_id):
        raise create_rate_limit_error(request=request)

    # Add rate limit headers
    rate_limit_status = get_rate_limit_status(client_id)
    add_rate_limit_headers(
        response,
        remaining=rate_limit_status["remaining"],
        reset_at=int(time.time()) + rate_limit_status["reset_in"]
    )

    # OPTIMIZATION: Eager load user roles to prevent N+1 queries
    from sqlalchemy.orm import joinedload
    from backend.core.query_optimizer import optimize_query_with_relationships

    query = db.query(User).filter(User.id == assign_data.user_id)
    query = optimize_query_with_relationships(query, User, relationships=['roles'], use_selectin=False)
    user = query.first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get role
    role = db.query(Role).filter(Role.name == assign_data.role_name).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    # Assign role
    if role not in user.roles:
        try:
            user.roles.append(role)
            db.commit()
            db.refresh(user)
        except Exception as e:
            db.rollback()
            logger.error(f"Error assigning role: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to assign role"
            )

        # Log admin action
        log_security_event(
            SecurityEvent.ADMIN_ACTION,
            user_id=current_user.id,
            email=current_user.email,
            details={"action": "assign_role", "target_user_id": user.id, "role": role.name},
            request=request
        )

    return {"message": f"Role {role.name} assigned to user {user.email}"}


@router.delete("/remove", status_code=200)
async def remove_role(
    assign_data: AssignRoleRequest,
    request: Request,
    response: Response,
    current_user: User = Depends(require_permission(PermEnum.ROLE_MANAGE)),
    db: Session = Depends(get_db)
):
    """
    Remove role from user (admin only)
    """
    # Rate limiting
    client_id = current_user.email
    if not check_rate_limit(client_id):
        raise create_rate_limit_error(request=request)

    # OPTIMIZATION: Eager load user roles to prevent N+1 queries
    from sqlalchemy.orm import joinedload
    from backend.core.query_optimizer import optimize_query_with_relationships

    query = db.query(User).filter(User.id == assign_data.user_id)
    query = optimize_query_with_relationships(query, User, relationships=['roles'], use_selectin=False)
    user = query.first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get role
    role = db.query(Role).filter(Role.name == assign_data.role_name).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    # Prevent removing system roles from users (optional safety check)
    if role.is_system and role.name == "admin":
        # OPTIMIZATION: Use optimized query for admin count
        from sqlalchemy.orm import joinedload
        admin_count = db.query(User).join(User.roles).filter(Role.name == "admin").count()
        if admin_count <= 1:
            raise HTTPException(
                status_code=400,
                detail="Cannot remove last admin user"
            )

    # Remove role
    if role in user.roles:
        try:
            user.roles.remove(role)
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Error removing role: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to remove role"
            )

        # Log admin action
        log_security_event(
            SecurityEvent.ADMIN_ACTION,
            user_id=current_user.id,
            email=current_user.email,
            details={"action": "remove_role", "target_user_id": user.id, "role": role.name},
            request=request
        )

    return {"message": f"Role {role.name} removed from user {user.email}"}


@router.post("/initialize", status_code=200)
async def initialize_roles(
    request: Request,
    response: Response,
    current_user: User = Depends(require_permission(PermEnum.ROLE_MANAGE)),
    db: Session = Depends(get_db)
):
    """
    Initialize default roles and permissions (admin only)
    """
    # Rate limiting
    client_id = current_user.email
    if not check_rate_limit(client_id):
        raise create_rate_limit_error(request=request)

    # Initialize default roles
    initialize_default_roles(db)

    # Log admin action
    log_security_event(
        SecurityEvent.ADMIN_ACTION,
        user_id=current_user.id,
        email=current_user.email,
        details={"action": "initialize_roles"},
        request=request
    )

    return {"message": "Default roles and permissions initialized"}

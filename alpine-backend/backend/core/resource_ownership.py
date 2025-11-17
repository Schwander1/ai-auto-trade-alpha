"""Resource ownership verification middleware and utilities"""
from fastapi import HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import Optional, Callable, Any
from backend.core.database import get_db
from backend.models.user import User
from backend.api.auth import get_current_user
from backend.core.security_logging import log_unauthorized_access, SecurityEvent
from backend.core.error_responses import create_error_response, ErrorCodes


async def verify_resource_ownership(
    resource_id: Any,
    resource_model: Any,
    user_id_field: str = "user_id",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Verify that the current user owns the specified resource
    
    Args:
        resource_id: ID of the resource to check
        resource_model: SQLAlchemy model class
        user_id_field: Field name that contains user ID (default: "user_id")
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Resource object if ownership verified
    
    Raises:
        HTTPException: 404 if resource not found, 403 if user doesn't own resource
    """
    # Get resource
    resource = db.query(resource_model).filter(resource_model.id == resource_id).first()
    
    if not resource:
        raise create_error_response(
            ErrorCodes.RESOURCE_001,
            f"Resource not found",
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    # Check ownership
    resource_user_id = getattr(resource, user_id_field, None)
    
    if resource_user_id is None:
        # Resource doesn't have user_id field - allow access (public resource)
        return resource
    
    if resource_user_id != current_user.id:
        # Log unauthorized access attempt
        log_unauthorized_access(
            user_id=current_user.id,
            email=current_user.email,
            resource=f"{resource_model.__name__}:{resource_id}",
            request=None  # Request not available in dependency
        )
        
        raise create_error_response(
            ErrorCodes.AUTHZ_003,
            "You do not have permission to access this resource",
            status_code=status.HTTP_403_FORBIDDEN
        )
    
    return resource


def require_resource_ownership(
    resource_model: Any,
    user_id_field: str = "user_id",
    resource_id_param: str = "resource_id"
):
    """
    Dependency factory for resource ownership verification
    
    Usage:
        @router.get("/signals/{signal_id}")
        async def get_signal(
            signal: Signal = Depends(require_resource_ownership(Signal, "user_id", "signal_id")),
            current_user: User = Depends(get_current_user)
        ):
            return signal
    """
    def _verify_ownership(
        resource_id: Any = Depends(lambda: None),  # Will be overridden by path parameter
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> Any:
        return verify_resource_ownership(
            resource_id=resource_id,
            resource_model=resource_model,
            user_id_field=user_id_field,
            current_user=current_user,
            db=db
        )
    
    return _verify_ownership


async def verify_user_resource(
    target_user_id: int,
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Verify that current user is accessing their own user resource
    
    Args:
        target_user_id: ID of user resource being accessed
        current_user: Current authenticated user
    
    Returns:
        User object if verified
    
    Raises:
        HTTPException: 403 if user doesn't match
    """
    if target_user_id != current_user.id:
        log_unauthorized_access(
            user_id=current_user.id,
            email=current_user.email,
            resource=f"User:{target_user_id}",
            request=None
        )
        
        raise create_error_response(
            ErrorCodes.AUTHZ_003,
            "You can only access your own user data",
            status_code=status.HTTP_403_FORBIDDEN
        )
    
    return current_user


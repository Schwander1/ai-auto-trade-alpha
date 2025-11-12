"""
User management API endpoints for Alpine Backend
GET profile, PUT profile, DELETE account
"""

from fastapi import APIRouter, HTTPException, Depends, status, Header, Request, Response
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
import time
import re

from backend.core.database import get_db
from backend.core.cache import cache_response
from backend.core.input_sanitizer import sanitize_string, sanitize_email
from backend.core.response_formatter import format_error_response, add_rate_limit_headers
from backend.core.security_logging import log_security_event, SecurityEvent
from backend.models.user import User
from backend.core.rate_limit import check_rate_limit, get_rate_limit_status
from backend.api.auth import get_current_user

router = APIRouter(prefix="/api/users", tags=["users"])

# Rate limiting
RATE_LIMIT_WINDOW = 60
RATE_LIMIT_MAX = 100


class UserProfileResponse(BaseModel):
    """User profile response"""
    id: int
    email: str
    full_name: str
    tier: str
    is_active: bool
    is_verified: bool
    created_at: str
    updated_at: Optional[str] = None


class UpdateProfileRequest(BaseModel):
    """Update profile request"""
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    
    @validator('full_name')
    def validate_full_name(cls, v):
        """Validate and sanitize full name"""
        if v is not None:
            v = sanitize_string(v, max_length=100)
            if len(v) < 1:
                raise ValueError("Full name cannot be empty")
        return v
    
    @validator('email')
    def validate_email(cls, v):
        """Validate and sanitize email"""
        if v is not None:
            v = sanitize_email(v)
        return v


class DeleteAccountRequest(BaseModel):
    """Delete account request (requires password confirmation)"""
    password: str = Field(..., description="Password confirmation required")


@router.get("/profile", response_model=UserProfileResponse)
@cache_response(ttl=300)  # Cache user profile for 5 minutes
async def get_profile(
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_user),
    authorization: Optional[str] = Header(None)
):
    """
    Get user profile
    
    **Example Request:**
    ```bash
    curl -X GET "http://localhost:9001/api/users/profile" \
         -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    ```
    
    **Example Response:**
    ```json
    {
      "id": 1,
      "email": "user@example.com",
      "full_name": "John Doe",
      "tier": "starter",
      "is_active": true,
      "is_verified": false,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": null
    }
    ```
    """
    # Rate limiting
    client_id = current_user.email
    if not check_rate_limit(client_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    # Add rate limit headers
    rate_limit_status = get_rate_limit_status(client_id)
    add_rate_limit_headers(
        response,
        remaining=rate_limit_status["remaining"],
        reset_at=int(time.time()) + rate_limit_status["reset_in"]
    )
    
    return UserProfileResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        tier=current_user.tier.value,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at.isoformat() if current_user.created_at else datetime.utcnow().isoformat() + "Z",
        updated_at=current_user.updated_at.isoformat() if current_user.updated_at else None
    )


@router.put("/profile", response_model=UserProfileResponse)
async def update_profile(
    profile_data: UpdateProfileRequest,
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    """
    Update user profile
    
    **Example Request:**
    ```bash
    curl -X PUT "http://localhost:9001/api/users/profile" \
         -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
         -H "Content-Type: application/json" \
         -d '{
           "full_name": "Jane Doe",
           "email": "newemail@example.com"
         }'
    ```
    
    **Example Response:**
    ```json
    {
      "id": 1,
      "email": "newemail@example.com",
      "full_name": "Jane Doe",
      "tier": "starter",
      "is_active": true,
      "is_verified": false,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T11:00:00Z"
    }
    ```
    """
    # Rate limiting
    client_id = current_user.email
    if not check_rate_limit(client_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    # Add rate limit headers
    rate_limit_status = get_rate_limit_status(client_id)
    add_rate_limit_headers(
        response,
        remaining=rate_limit_status["remaining"],
        reset_at=int(time.time()) + rate_limit_status["reset_in"]
    )
    
    # Update fields
    updated = False
    
    if profile_data.full_name is not None:
        # Sanitize full name
        sanitized_name = sanitize_string(profile_data.full_name, max_length=100)
        current_user.full_name = sanitized_name
        updated = True
    
    if profile_data.email is not None and profile_data.email != current_user.email:
        # Sanitize email
        try:
            sanitized_email = sanitize_email(profile_data.email)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        
        # Check if email is already taken
        existing_user = db.query(User).filter(User.email == sanitized_email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Log email change
        log_security_event(
            SecurityEvent.ADMIN_ACTION,
            user_id=current_user.id,
            email=current_user.email,
            details={"action": "email_change", "old_email": current_user.email, "new_email": sanitized_email},
            request=request
        )
        
        current_user.email = sanitized_email
        current_user.is_verified = False  # Require re-verification
        updated = True
    
    if updated:
        current_user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(current_user)
    
    return UserProfileResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        tier=current_user.tier.value,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at.isoformat() if current_user.created_at else datetime.utcnow().isoformat() + "Z",
        updated_at=current_user.updated_at.isoformat() if current_user.updated_at else None
    )


@router.delete("/account", status_code=200)
async def delete_account(
    delete_data: DeleteAccountRequest,
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    """
    Delete user account (requires password confirmation)
    
    **Example Request:**
    ```bash
    curl -X DELETE "http://localhost:9001/api/users/account" \
         -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
         -H "Content-Type: application/json" \
         -d '{
           "password": "SecurePass123!"
         }'
    ```
    
    **Example Response:**
    ```json
    {
      "message": "Account deleted successfully"
    }
    ```
    """
    # Rate limiting
    client_id = current_user.email
    if not check_rate_limit(client_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    # Add rate limit headers
    rate_limit_status = get_rate_limit_status(client_id)
    add_rate_limit_headers(
        response,
        remaining=rate_limit_status["remaining"],
        reset_at=int(time.time()) + rate_limit_status["reset_in"]
    )
    
    # Verify password
    from backend.auth.security import verify_password
    if not verify_password(delete_data.password, current_user.hashed_password):
        log_security_event(
            SecurityEvent.FAILED_LOGIN,
            user_id=current_user.id,
            email=current_user.email,
            details={"reason": "incorrect_password_for_account_deletion"},
            request=request
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password"
        )
    
    # Log account deletion
    log_security_event(
        SecurityEvent.ACCOUNT_DELETED,
        user_id=current_user.id,
        email=current_user.email,
        details={"action": "account_deletion"},
        request=request
    )
    
    # Delete user (soft delete by setting is_active=False)
    current_user.is_active = False
    current_user.updated_at = datetime.utcnow()
    db.commit()
    
    # In production, you might want to:
    # - Cancel Stripe subscription
    # - Delete user data
    # - Send confirmation email
    
    return {"message": "Account deleted successfully"}


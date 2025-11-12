"""
Authentication API endpoints for Alpine Backend
POST signup, POST login, POST logout, GET me
"""

from fastapi import APIRouter, HTTPException, Depends, status, Header
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime, timedelta
import time
import redis

from backend.core.database import get_db
from backend.core.config import settings
from backend.core.rate_limit import check_rate_limit
from backend.core.cache import cache_response
from backend.core.token_blacklist import is_token_blacklisted, blacklist_token
from backend.core.account_lockout import is_account_locked, record_failed_login, clear_failed_attempts
from backend.core.security_logging import log_successful_login, log_failed_login, SecurityEvent
from backend.auth.password_validator import PasswordValidator
from backend.models.user import User, UserTier
from backend.auth.security import verify_password, get_password_hash, create_access_token, verify_token
from fastapi import Request

router = APIRouter(prefix="/api/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

# Rate limiting and token blacklist now handled by backend.core modules
# Imported above: check_rate_limit, is_token_blacklisted, blacklist_token


class SignupRequest(BaseModel):
    """Signup request model"""
    email: EmailStr
    password: str = Field(..., min_length=12, description="Password must be at least 12 characters with uppercase, lowercase, numbers, and special characters")
    full_name: str = Field(..., min_length=1, max_length=100)
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength"""
        is_valid, errors = PasswordValidator.validate_password(v)
        if not is_valid:
            raise ValueError("; ".join(errors))
        return v


class LoginResponse(BaseModel):
    """Login response model"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict
    requires_2fa: bool = False  # Indicates if 2FA verification is required


class UserResponse(BaseModel):
    """User response model"""
    id: int
    email: str
    full_name: str
    tier: str
    is_active: bool
    is_verified: bool
    created_at: str
    updated_at: Optional[str] = None


# Rate limiting is now handled by backend.core.rate_limit module


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    # Check if token is blacklisted (using Redis)
    if is_token_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.email == payload.get("sub")).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    return user


@router.post("/signup", response_model=LoginResponse, status_code=201)
async def signup(
    user_data: SignupRequest,
    request: Request,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    """
    Create a new user account
    
    **Example Request:**
    ```bash
    curl -X POST "http://localhost:9001/api/auth/signup" \
         -H "Content-Type: application/json" \
         -d '{
           "email": "user@example.com",
           "password": "SecurePass123!",
           "full_name": "John Doe"
         }'
    ```
    
    **Example Response:**
    ```json
    {
      "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "token_type": "bearer",
      "expires_in": 86400,
      "user": {
        "id": 1,
        "email": "user@example.com",
        "full_name": "John Doe",
        "tier": "starter"
      }
    }
    ```
    """
    # Rate limiting
    client_id = authorization or request.client.host if request.client else "anonymous"
    if not check_rate_limit(client_id):
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Maximum {RATE_LIMIT_MAX} requests per minute."
        )
    
    # Validate password strength
    is_valid, errors = PasswordValidator.validate_password(user_data.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="; ".join(errors)
        )
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        tier=UserTier.STARTER,
        is_active=True,
        is_verified=False
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create access token
    access_token = create_access_token(data={"sub": new_user.email})
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.JWT_EXPIRATION_HOURS * 3600,
        user={
            "id": new_user.id,
            "email": new_user.email,
            "full_name": new_user.full_name,
            "tier": new_user.tier.value
        }
    )


@router.post("/login", response_model=LoginResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    request: Request,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    """
    Login and get access token
    
    **Example Request:**
    ```bash
    curl -X POST "http://localhost:9001/api/auth/login" \
         -H "Content-Type: application/x-www-form-urlencoded" \
         -d "username=user@example.com&password=SecurePass123!"
    ```
    
    **Example Response:**
    ```json
    {
      "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "token_type": "bearer",
      "expires_in": 86400,
      "user": {
        "id": 1,
        "email": "user@example.com",
        "full_name": "John Doe",
        "tier": "starter"
      }
    }
    ```
    """
    # Rate limiting
    client_id = form_data.username or request.client.host if request.client else "anonymous"
    if not check_rate_limit(client_id):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Too many login attempts."
        )
    
    # Check if account is locked
    if is_account_locked(form_data.username):
        from backend.core.account_lockout import get_lockout_remaining
        remaining = get_lockout_remaining(form_data.username)
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=f"Account locked due to too many failed login attempts. Try again in {remaining // 60} minutes."
        )
    
    # Find user
    user = db.query(User).filter(User.email == form_data.username).first()
    
    # Verify password (always check to prevent user enumeration)
    password_valid = False
    if user:
        password_valid = verify_password(form_data.password, user.hashed_password)
    
    if not user or not password_valid:
        # Record failed login attempt
        record_failed_login(form_data.username, request.client.host if request.client else None, request)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Clear failed attempts on successful login
    clear_failed_attempts(user.email)
    
    # Check if 2FA is enabled
    if user.totp_enabled:
        # Return partial login response indicating 2FA required
        return LoginResponse(
            access_token="",  # No token until 2FA verified
            token_type="bearer",
            expires_in=0,
            user={
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "tier": user.tier.value
            },
            requires_2fa=True  # Indicate 2FA is required
        )
    
    # Log successful login
    log_successful_login(user.id, user.email, request.client.host if request.client else None, request)
    
    # Create access token
    access_token = create_access_token(data={"sub": user.email})
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.JWT_EXPIRATION_HOURS * 3600,
        user={
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "tier": user.tier.value
        }
    )


@router.post("/logout", status_code=200)
async def logout(
    current_user: User = Depends(get_current_user),
    authorization: Optional[str] = Header(None)
):
    """
    Logout and revoke token
    
    **Example Request:**
    ```bash
    curl -X POST "http://localhost:9001/api/auth/logout" \
         -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    ```
    
    **Example Response:**
    ```json
    {
      "message": "Successfully logged out"
    }
    ```
    """
    # Rate limiting
    client_id = current_user.email
    if not check_rate_limit(client_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    # Extract token from authorization header
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        # Add to blacklist (using Redis)
        blacklist_token(token, ttl=settings.JWT_EXPIRATION_HOURS * 3600)
    
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
@cache_response(ttl=300)  # Cache user info for 5 minutes
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user information
    
    **Example Request:**
    ```bash
    curl -X GET "http://localhost:9001/api/auth/me" \
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
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        tier=current_user.tier.value,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at.isoformat() if current_user.created_at else datetime.utcnow().isoformat() + "Z",
        updated_at=current_user.updated_at.isoformat() if current_user.updated_at else None
    )


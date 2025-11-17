"""
Authentication API endpoints for Alpine Backend
POST signup, POST login, POST logout, GET me
"""

from fastapi import APIRouter, HTTPException, Depends, status, Header
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime, timedelta
import time
import redis

from backend.core.database import get_db
from backend.core.config import settings
from backend.core.rate_limit import check_rate_limit
from backend.core.cache import cache_response
from backend.core.cache_constants import CACHE_TTL_USER_PROFILE
from backend.core.token_blacklist import is_token_blacklisted, blacklist_token
from backend.core.response_formatter import format_datetime_iso
from backend.core.account_lockout import is_account_locked, record_failed_login, clear_failed_attempts
from backend.core.security_logging import log_successful_login, log_failed_login, SecurityEvent
from backend.auth.password_validator import PasswordValidator
from backend.models.user import User, UserTier
from backend.auth.security import verify_password, get_password_hash, create_access_token, verify_token
from fastapi import Request

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

# Rate limiting and token blacklist now handled by backend.core modules
# Imported above: check_rate_limit, is_token_blacklisted, blacklist_token
RATE_LIMIT_MAX = 10  # Lower limit for auth endpoints (security)


class SignupRequest(BaseModel):
    """Signup request model"""
    email: EmailStr
    password: str = Field(..., min_length=12, description="Password must be at least 12 characters with uppercase, lowercase, numbers, and special characters")
    full_name: str = Field(..., min_length=1, max_length=100)

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
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
    """Get current authenticated user with caching optimization"""
    from backend.core.error_responses import create_error_response, ErrorCodes

    # Validate token
    _validate_token(token)

    # Extract email from token
    payload = verify_token(token)
    if not payload:
        raise create_error_response(
            ErrorCodes.AUTH_001,
            "Invalid or expired token",
            status_code=status.HTTP_401_UNAUTHORIZED,
            request=None
        )

    email = payload.get("sub")

    # Try to get user from cache first
    user = _get_user_from_cache(email, db)
    if user:
        return user

    # Cache miss - query database and cache result
    user = _get_user_from_database(email, db)
    _cache_user_data(user)

    return user

def _validate_token(token: str):
    """Validate token is not blacklisted"""
    from backend.core.error_responses import create_error_response, ErrorCodes

    if is_token_blacklisted(token):
        raise create_error_response(
            ErrorCodes.AUTH_002,
            "Token has been revoked",
            status_code=status.HTTP_401_UNAUTHORIZED,
            request=None
        )

def _get_user_from_cache(email: str, db: Session) -> Optional[User]:
    """Get user from cache if available and valid"""
    from backend.core.cache import get_cache
    from backend.core.cache_constants import CACHE_TTL_USER_PROFILE

    cache_key = f"user:email:{email}"
    cached_user_data = get_cache(cache_key)

    if cached_user_data:
        # Cache hit - query database to get SQLAlchemy object (needed for relationships)
        user = db.query(User).filter(User.email == email).first()
        if user:
            # Verify cached data matches (quick validation)
            if (user.id == cached_user_data.get("id") and
                user.is_active == cached_user_data.get("is_active", False)):
                # Cache is valid - return user
                return user

    return None

def _get_user_from_database(email: str, db: Session) -> User:
    """Get user from database and validate"""
    from backend.core.error_responses import create_error_response, ErrorCodes

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise create_error_response(
            ErrorCodes.RESOURCE_001,
            "User not found",
            status_code=status.HTTP_404_NOT_FOUND,
            request=None
        )

    if not user.is_active:
        raise create_error_response(
            ErrorCodes.AUTH_005,
            "User account is inactive",
            status_code=status.HTTP_403_FORBIDDEN,
            request=None
        )

    return user

def _cache_user_data(user: User):
    """Cache user data for faster subsequent lookups"""
    from backend.core.cache import set_cache
    from backend.core.cache_constants import CACHE_TTL_USER_PROFILE

    cache_key = f"user:email:{user.email}"
    user_data = {
        "id": user.id,
        "email": user.email,
        "is_active": user.is_active,
        "tier": user.tier.value if hasattr(user.tier, 'value') else str(user.tier)
    }
    set_cache(cache_key, user_data, ttl=CACHE_TTL_USER_PROFILE)


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
    from backend.core.api_utils import get_client_id
    client_id = get_client_id(request, authorization)
    if not check_rate_limit(client_id):
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Maximum {RATE_LIMIT_MAX} requests per minute."
        )

    # Validate input
    _validate_signup_input(user_data)
    
    # Check if user exists
    _check_user_not_exists(user_data.email, db)
    
    # Create user
    new_user = _create_new_user(user_data, db)
    
    # Create and return login response
    return _create_login_response(new_user)


@router.post("/login", response_model=LoginResponse)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
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
    from backend.core.api_utils import get_client_id
    client_id = get_client_id(request, form_data.username)
    if not check_rate_limit(client_id):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Too many login attempts."
        )

    # Check account lockout
    _check_account_not_locked(form_data.username)
    
    # Authenticate user
    user = _authenticate_user(form_data.username, form_data.password, db, request)
    
    # Handle 2FA if enabled
    if user.totp_enabled:
        return _create_2fa_required_response(user)
    
    # Log successful login and create response
    log_successful_login(user.id, user.email, request.client.host if request.client else None, request)
    return _create_login_response(user)


def _validate_signup_input(user_data: SignupRequest):
    """Validate signup input (password strength)"""
    is_valid, errors = PasswordValidator.validate_password(user_data.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="; ".join(errors)
        )

def _check_user_not_exists(email: str, db: Session):
    """Check if user already exists"""
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

def _create_new_user(user_data: SignupRequest, db: Session) -> User:
    """Create new user in database"""
    try:
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
        return new_user
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating user: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user account"
        )

def _create_login_response(user: User) -> LoginResponse:
    """Create login response with access token"""
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

def _check_account_not_locked(username: str):
    """Check if account is locked"""
    if is_account_locked(username):
        from backend.core.account_lockout import get_lockout_remaining
        remaining = get_lockout_remaining(username)
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=f"Account locked due to too many failed login attempts. Try again in {remaining // 60} minutes."
        )

def _authenticate_user(username: str, password: str, db: Session, request: Request) -> User:
    """Authenticate user and return User object"""
    # Find user
    user = db.query(User).filter(User.email == username).first()
    
    # Verify password (always check to prevent user enumeration)
    password_valid = False
    if user:
        password_valid = verify_password(password, user.hashed_password)
    
    if not user or not password_valid:
        # Record failed login attempt
        record_failed_login(username, request.client.host if request.client else None, request)
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
    
    return user

def _create_2fa_required_response(user: User) -> LoginResponse:
    """Create login response indicating 2FA is required"""
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
        raise create_rate_limit_error(request=request)

    # Extract token from authorization header
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        # Add to blacklist (using Redis)
        blacklist_token(token, ttl=settings.JWT_EXPIRATION_HOURS * 3600)

    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
@cache_response(ttl=CACHE_TTL_USER_PROFILE)  # Cache user info for 5 minutes
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
        created_at=format_datetime_iso(current_user.created_at),
        updated_at=format_datetime_iso(current_user.updated_at) if current_user.updated_at else None
    )

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
from backend.models.user import User, UserTier
from backend.auth.security import verify_password, get_password_hash, create_access_token, verify_token

router = APIRouter(prefix="/api/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

# Rate limiting and token blacklist now handled by backend.core modules
# Imported above: check_rate_limit, is_token_blacklisted, blacklist_token


class SignupRequest(BaseModel):
    """Signup request model"""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    full_name: str = Field(..., min_length=1, max_length=100)


class LoginResponse(BaseModel):
    """Login response model"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


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
    client_id = authorization or "anonymous"
    if not check_rate_limit(client_id):
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Maximum {RATE_LIMIT_MAX} requests per minute."
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
    client_id = form_data.username or "anonymous"
    if not check_rate_limit(client_id):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Too many login attempts."
        )
    
    # Find user
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
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


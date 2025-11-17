"""2FA verification endpoint for login"""
from fastapi import APIRouter, HTTPException, Depends, status, Header, Request, Response
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, field_validator
from typing import Optional
import re
import time
import logging

from backend.core.database import get_db

logger = logging.getLogger(__name__)
from backend.core.config import settings
from backend.core.rate_limit import check_rate_limit, get_rate_limit_status
from backend.core.response_formatter import add_rate_limit_headers
from backend.core.input_sanitizer import sanitize_email
from backend.core.security_logging import log_successful_login, log_failed_login, SecurityEvent
from backend.models.user import User
from backend.auth.security import create_access_token
from backend.auth.totp import TOTPManager
import json

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


class Verify2FALoginRequest(BaseModel):
    """Request to verify 2FA during login"""
    email: str = Field(..., description="User email")
    token: str = Field(..., description="TOTP token or backup code", min_length=6, max_length=12)

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate and sanitize email"""
        return sanitize_email(v)

    @field_validator('token')
    @classmethod
    def validate_token(cls, v: str) -> str:
        """Validate token format"""
        if not re.match(r'^[\dA-Za-z]{6,12}$', v):
            raise ValueError("Token must be 6-12 alphanumeric characters")
        return v


@router.post("/verify-2fa", response_model=dict)
async def verify_2fa_login(
    verify_data: Verify2FALoginRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Verify 2FA token during login and complete authentication

    **Example Request:**
    ```json
    {
      "email": "user@example.com",
      "token": "123456"
    }
    ```
    """
    # Rate limiting
    client_id = verify_data.email
    if not check_rate_limit(client_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    # Add rate limit headers
    rate_limit_status = get_rate_limit_status(client_id)
    add_rate_limit_headers(
        response,
        remaining=rate_limit_status["remaining"],
        reset_at=int(time.time()) + rate_limit_status["reset_in"]
    )

    # Find user
    user = db.query(User).filter(User.email == verify_data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if not user.totp_enabled or not user.totp_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is not enabled for this account"
        )

    # Verify TOTP token
    token_valid = TOTPManager.verify_totp(user.totp_secret, verify_data.token)
    backup_code_used = False

    # Try backup code if TOTP fails
    if not token_valid and user.backup_codes:
        backup_codes = json.loads(user.backup_codes)
        if TOTPManager.verify_backup_code(backup_codes, verify_data.token):
            token_valid = True
            backup_code_used = True
            # Remove used backup code
            try:
                backup_codes.remove(TOTPManager.hash_backup_code(verify_data.token))
                user.backup_codes = json.dumps(backup_codes) if backup_codes else None
                db.commit()
            except Exception as e:
                db.rollback()
                logger.error(f"Error updating backup codes: {e}", exc_info=True)
                # Don't fail verification if backup code update fails
                pass

    if not token_valid:
        log_failed_login(user.email, request.client.host if request.client else None, request)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid 2FA token or backup code"
        )

    # Log successful login
    log_successful_login(user.id, user.email, request.client.host if request.client else None, request)

    # Create access token
    access_token = create_access_token(data={"sub": user.email})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.JWT_EXPIRATION_HOURS * 3600,
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "tier": user.tier.value
        },
        "backup_code_used": backup_code_used
    }

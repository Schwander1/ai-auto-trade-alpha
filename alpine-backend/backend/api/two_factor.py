"""2FA (TOTP) API endpoints"""
from fastapi import APIRouter, HTTPException, Depends, status, Header, Request, Response
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, field_validator
from typing import Optional
import json
import re
import time

from backend.core.database import get_db
from backend.core.config import settings
from backend.core.rate_limit import check_rate_limit, get_rate_limit_status
from backend.core.response_formatter import add_rate_limit_headers
from backend.core.security_logging import log_security_event, SecurityEvent
from backend.models.user import User
from backend.api.auth import get_current_user
from backend.auth.totp import TOTPManager

router = APIRouter(prefix="/api/v1/2fa", tags=["2fa"])


class Enable2FARequest(BaseModel):
    """Request to enable 2FA"""
    token: str = Field(..., description="TOTP token to verify setup", min_length=6, max_length=6)

    @field_validator('token')
    @classmethod
    def validate_token(cls, v: str) -> str:
        """Validate TOTP token format"""
        if not re.match(r'^\d{6}$', v):
            raise ValueError("TOTP token must be 6 digits")
        return v


class Verify2FARequest(BaseModel):
    """Request to verify 2FA token"""
    token: str = Field(..., description="TOTP token or backup code", min_length=6, max_length=12)

    @field_validator('token')
    @classmethod
    def validate_token(cls, v: str) -> str:
        """Validate token format (6-digit TOTP or 8-12 char backup code)"""
        if not re.match(r'^[\dA-Za-z]{6,12}$', v):
            raise ValueError("Token must be 6-12 alphanumeric characters")
        return v


class Disable2FARequest(BaseModel):
    """Request to disable 2FA"""
    password: str = Field(..., description="User password for confirmation")
    token: Optional[str] = Field(None, description="TOTP token or backup code if 2FA is enabled")


@router.post("/setup", response_model=dict)
async def setup_2fa(
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    """
    Setup 2FA - Generate secret and QR code

    **Example Response:**
    ```json
    {
      "secret": "JBSWY3DPEHPK3PXP",
      "qr_code": "data:image/png;base64,iVBORw0KG...",
      "backup_codes": ["12345678", "87654321", ...]
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

    # Generate TOTP secret
    secret = TOTPManager.generate_secret()

    # Generate QR code
    uri = TOTPManager.get_totp_uri(secret, current_user.email)
    qr_code = TOTPManager.generate_qr_code(uri)

    # Generate backup codes
    backup_codes = TOTPManager.generate_backup_codes(10)
    hashed_backup_codes = [TOTPManager.hash_backup_code(code) for code in backup_codes]

    # Store secret and backup codes (temporarily, until verified)
    try:
        current_user.totp_secret = secret
        current_user.backup_codes = json.dumps(hashed_backup_codes)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Error setting up 2FA: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to setup 2FA"
        )

    log_security_event(
        SecurityEvent.ADMIN_ACTION,
        user_id=current_user.id,
        email=current_user.email,
        details={"action": "2fa_setup_initiated"},
        request=request
    )

    return {
        "secret": secret,
        "qr_code": f"data:image/png;base64,{qr_code}",
        "backup_codes": backup_codes,  # Show only once
        "message": "Scan QR code with authenticator app, then verify with a token"
    }


@router.post("/enable", response_model=dict)
async def enable_2fa(
    enable_data: Enable2FARequest,
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    """
    Enable 2FA - Verify token and activate

    **Example Request:**
    ```json
    {
      "token": "123456"
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

    if not current_user.totp_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA setup not initiated. Call /setup first."
        )

    # Verify token
    if not TOTPManager.verify_totp(current_user.totp_secret, enable_data.token):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token. Please try again."
        )

    # Enable 2FA
    try:
        current_user.totp_enabled = True
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Error enabling 2FA: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to enable 2FA"
        )

    log_security_event(
        SecurityEvent.ADMIN_ACTION,
        user_id=current_user.id,
        email=current_user.email,
        details={"action": "2fa_enabled"},
        request=request
    )

    return {
        "message": "2FA enabled successfully",
        "enabled": True
    }


@router.post("/verify", response_model=dict)
async def verify_2fa(
    verify_data: Verify2FARequest,
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    """
    Verify 2FA token (used during login)

    **Example Request:**
    ```json
    {
      "token": "123456"
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

    if not current_user.totp_enabled or not current_user.totp_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is not enabled for this account"
        )

    # Try TOTP token first
    if TOTPManager.verify_totp(current_user.totp_secret, verify_data.token):
        # Check for replay attacks (prevent same token being used twice)
        # In production, implement token replay prevention
        return {"verified": True}

    # Try backup code
    if current_user.backup_codes:
        backup_codes = json.loads(current_user.backup_codes)
        if TOTPManager.verify_backup_code(backup_codes, verify_data.token):
            # Remove used backup code
            try:
                backup_codes.remove(TOTPManager.hash_backup_code(verify_data.token))
                current_user.backup_codes = json.dumps(backup_codes) if backup_codes else None
                db.commit()
            except Exception as e:
                db.rollback()
                logger.error(f"Error updating backup codes: {e}", exc_info=True)
                # Don't fail verification if backup code update fails
                pass

            log_security_event(
                SecurityEvent.ADMIN_ACTION,
                user_id=current_user.id,
                email=current_user.email,
                details={"action": "2fa_backup_code_used"},
                request=request
            )

            return {"verified": True, "backup_code_used": True}

    log_security_event(
        SecurityEvent.FAILED_LOGIN,
        user_id=current_user.id,
        email=current_user.email,
        details={"reason": "invalid_2fa_token"},
        request=request
    )

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid token or backup code"
    )


@router.post("/disable", response_model=dict)
async def disable_2fa(
    disable_data: Disable2FARequest,
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    """
    Disable 2FA

    **Example Request:**
    ```json
    {
      "password": "user_password",
      "token": "123456"  // Required if 2FA is enabled
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
    if not verify_password(disable_data.password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password"
        )

    # If 2FA is enabled, require token
    if current_user.totp_enabled:
        if not disable_data.token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="2FA token required to disable 2FA"
            )

        # Verify token
        if not TOTPManager.verify_totp(current_user.totp_secret, disable_data.token):
            # Try backup code
            if current_user.backup_codes:
                backup_codes = json.loads(current_user.backup_codes)
                if not TOTPManager.verify_backup_code(backup_codes, disable_data.token):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid 2FA token or backup code"
                    )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid 2FA token"
                )

    # Disable 2FA
    try:
        current_user.totp_enabled = False
        current_user.totp_secret = None
        current_user.backup_codes = None
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Error disabling 2FA: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to disable 2FA"
        )

    log_security_event(
        SecurityEvent.ADMIN_ACTION,
        user_id=current_user.id,
        email=current_user.email,
        details={"action": "2fa_disabled"},
        request=request
    )

    return {
        "message": "2FA disabled successfully",
        "enabled": False
    }


@router.get("/status", response_model=dict)
async def get_2fa_status(
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_user),
    authorization: Optional[str] = Header(None)
):
    """Get 2FA status for current user"""
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

    return {
        "enabled": current_user.totp_enabled if current_user.totp_enabled else False,
        "has_backup_codes": bool(current_user.backup_codes)
    }

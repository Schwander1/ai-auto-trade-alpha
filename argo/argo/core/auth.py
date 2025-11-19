"""
Authentication utilities for Argo
"""
from fastapi import HTTPException, Request
from typing import Optional
import os

def require_admin_user(request: Request):
    """
    Check if request has admin access
    Uses API key from environment variable
    """
    admin_api_key = os.getenv("ADMIN_API_KEY", "")

    if not admin_api_key:
        # If no admin key set, allow all (development mode)
        # In production, this should be set
        return True

    # Check for API key in header
    api_key = request.headers.get("X-Admin-API-Key")
    if api_key == admin_api_key:
        return True

    # Check for API key in query parameter (less secure, but convenient)
    api_key = request.query_params.get("admin_key")
    if api_key == admin_api_key:
        return True

    raise HTTPException(
        status_code=403,
        detail="Admin access required. Provide X-Admin-API-Key header."
    )

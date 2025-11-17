"""Security monitoring dashboard API"""
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime, timedelta
import json
import os
import logging

from backend.core.database import get_db
from backend.core.cache import cache_response
from backend.core.cache_constants import CACHE_TTL_SECURITY_METRICS
from backend.core.security_logging import SecurityEvent
from backend.api.auth import get_current_user
from backend.api.admin import require_admin
from backend.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/security", tags=["security"])


class SecurityMetrics(BaseModel):
    """Security metrics response"""
    failed_logins_24h: int
    successful_logins_24h: int
    account_lockouts_24h: int
    rate_limit_violations_24h: int
    csrf_violations_24h: int
    suspicious_activities_24h: int
    admin_actions_24h: int
    two_fa_enabled_count: int
    two_fa_usage_24h: int


class SecurityEventLog(BaseModel):
    """Security event log entry"""
    timestamp: str
    event_type: str
    user_id: Optional[int]
    email: Optional[str]
    ip_address: Optional[str]
    details: Dict


@router.get("/metrics", response_model=SecurityMetrics)
@cache_response(ttl=CACHE_TTL_SECURITY_METRICS)  # Cache for 1 minute (security metrics update frequently)
async def get_security_metrics(
    current_user: User = Depends(require_admin),
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Get security metrics for dashboard (admin only)
    """
    # Parse security log file
    security_log_path = "logs/security.log"
    metrics = {
        "failed_logins_24h": 0,
        "successful_logins_24h": 0,
        "account_lockouts_24h": 0,
        "rate_limit_violations_24h": 0,
        "csrf_violations_24h": 0,
        "suspicious_activities_24h": 0,
        "admin_actions_24h": 0,
        "two_fa_enabled_count": 0,
        "two_fa_usage_24h": 0
    }

    if os.path.exists(security_log_path):
        cutoff_time = datetime.utcnow() - timedelta(hours=24)

        with open(security_log_path, 'r') as f:
            for line in f:
                try:
                    event = json.loads(line)
                    event_time = datetime.fromisoformat(event.get("timestamp", ""))

                    if event_time >= cutoff_time:
                        event_type = event.get("event_type", "")

                        if event_type == SecurityEvent.FAILED_LOGIN:
                            metrics["failed_logins_24h"] += 1
                        elif event_type == SecurityEvent.SUCCESSFUL_LOGIN:
                            metrics["successful_logins_24h"] += 1
                        elif event_type == SecurityEvent.ACCOUNT_LOCKED:
                            metrics["account_lockouts_24h"] += 1
                        elif event_type == SecurityEvent.RATE_LIMIT_EXCEEDED:
                            metrics["rate_limit_violations_24h"] += 1
                        elif event_type == SecurityEvent.CSRF_VIOLATION:
                            metrics["csrf_violations_24h"] += 1
                        elif event_type == SecurityEvent.SUSPICIOUS_ACTIVITY:
                            metrics["suspicious_activities_24h"] += 1
                        elif event_type == SecurityEvent.ADMIN_ACTION:
                            metrics["admin_actions_24h"] += 1
                except (json.JSONDecodeError, ValueError):
                    continue

    # Get 2FA statistics
    try:
        from sqlalchemy import func
        metrics["two_fa_enabled_count"] = db.query(func.count(User.id)).filter(User.totp_enabled == True).scalar() or 0
    except Exception as e:
        logger.error(f"Error fetching 2FA statistics: {e}", exc_info=True)
        # Continue with default value if query fails
        metrics["two_fa_enabled_count"] = 0

    return SecurityMetrics(**metrics)


@router.get("/events", response_model=List[SecurityEventLog])
async def get_security_events(
    limit: int = 100,
    event_type: Optional[str] = None,
    current_user: User = Depends(require_admin),
    authorization: Optional[str] = Header(None)
):
    """
    Get recent security events (admin only)
    """
    security_log_path = "logs/security.log"
    events = []

    if os.path.exists(security_log_path):
        with open(security_log_path, 'r') as f:
            for line in f:
                try:
                    event = json.loads(line)

                    # Filter by event type if specified
                    if event_type and event.get("event_type") != event_type:
                        continue

                    events.append(SecurityEventLog(
                        timestamp=event.get("timestamp", ""),
                        event_type=event.get("event_type", ""),
                        user_id=event.get("user_id"),
                        email=event.get("email"),
                        ip_address=event.get("ip_address"),
                        details=event.get("details", {})
                    ))
                except (json.JSONDecodeError, ValueError):
                    continue

    # Return most recent events first
    events.reverse()
    return events[:limit]

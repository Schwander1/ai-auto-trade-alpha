"""
Notifications API endpoints for Alpine Backend
GET unread, POST read, DELETE

Optimizations:
- Thread-safe notification storage
- Efficient pagination
- Cache headers for client-side caching
- Better error handling
"""
import logging
import re
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request, Response
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.api.auth import get_current_user
from backend.core.database import get_db
from backend.core.input_sanitizer import sanitize_string
from backend.core.rate_limit import check_rate_limit, get_rate_limit_status
from backend.core.response_formatter import (
    add_cache_headers,
    add_rate_limit_headers,
    format_datetime_iso,
)
from backend.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/notifications", tags=["notifications"])

# Rate limiting
RATE_LIMIT_WINDOW = 60
RATE_LIMIT_MAX = 100

# Error message constants
INVALID_NOTIFICATION_ID_FORMAT = "Invalid notification ID format"
RATE_LIMIT_EXCEEDED = "Rate limit exceeded"


class NotificationResponse(BaseModel):
    """Notification response model"""
    id: str
    user_id: int
    title: str
    message: str
    type: str  # info, warning, success, error
    is_read: bool
    created_at: str
    read_at: Optional[str] = None


class PaginatedNotificationsResponse(BaseModel):
    """Paginated notifications response"""
    items: List[NotificationResponse]
    total: int
    unread_count: int
    limit: int
    offset: int
    has_more: bool


class MarkReadRequest(BaseModel):
    """Mark notification as read request"""
    notification_ids: List[str] = Field(..., description="List of notification IDs to mark as read")

    @field_validator('notification_ids')
    @classmethod
    def validate_notification_ids(cls, v: List[str]) -> List[str]:
        """Validate notification IDs"""
        if not v:
            raise ValueError("At least one notification ID is required")
        if len(v) > 100:
            raise ValueError("Maximum 100 notification IDs allowed")
        # Sanitize each ID
        sanitized = []
        for nid in v:
            if not isinstance(nid, str) or len(nid) > 100:
                raise ValueError(INVALID_NOTIFICATION_ID_FORMAT)
            # Only allow alphanumeric, hyphens, underscores
            if not re.match(r'^[A-Za-z0-9_-]+$', nid):
                raise ValueError(INVALID_NOTIFICATION_ID_FORMAT)
            sanitized.append(nid)
        return sanitized


def get_user_notifications(user_id: int, db: Session) -> List[Dict]:
    """Get notifications for user from database"""
    from backend.models.notification import Notification

    try:
        notifications = db.query(Notification).filter(
            Notification.user_id == user_id
        ).order_by(Notification.created_at.desc()).all()

        # Convert to dict format for compatibility
        return [
            {
                "id": f"notif-{n.id}",
                "user_id": n.user_id,
                "title": n.title,
                "message": n.message,
                "type": n.type.value if hasattr(n.type, 'value') else str(n.type),  # Handle enum serialization
                "is_read": n.is_read,
                "created_at": format_datetime_iso(n.created_at),
                "read_at": format_datetime_iso(n.read_at) if n.read_at else None
            }
            for n in notifications
        ]
    except Exception as e:
        logger.error(f"Error fetching notifications for user {user_id}: {e}", exc_info=True)
        # Return empty list on error to prevent endpoint failure
        return []


@router.get("/unread", response_model=PaginatedNotificationsResponse)
async def get_unread_notifications(
    request: Request,
    response: Response,
    limit: int = Query(20, ge=1, le=100, description="Number of notifications to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: User = Depends(get_current_user),
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Get unread notifications

    **Example Request:**
    ```bash
    curl -X GET "http://localhost:9001/api/notifications/unread?limit=20" \
         -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    ```

    **Example Response:**
    ```json
    {
      "items": [
        {
          "id": "notif-1234567890",
          "user_id": 1,
          "title": "New Signal Available",
          "message": "A new premium signal for AAPL is available",
          "type": "info",
          "is_read": false,
          "created_at": "2024-01-15T10:30:00Z",
          "read_at": null
        }
      ],
      "total": 5,
      "unread_count": 5,
      "limit": 20,
      "offset": 0,
      "has_more": false
    }
    ```
    """
    # Rate limiting
    client_id = current_user.email
    if not check_rate_limit(client_id):
        raise HTTPException(status_code=429, detail=RATE_LIMIT_EXCEEDED)

    # Add rate limit headers
    rate_limit_status = get_rate_limit_status(client_id)
    add_rate_limit_headers(
        response,
        remaining=rate_limit_status["remaining"],
        reset_at=int(time.time()) + rate_limit_status["reset_in"]
    )

    # OPTIMIZATION: Query unread notifications directly from database with pagination
    # This is much more efficient than fetching all and filtering in Python
    from backend.models.notification import Notification

    try:
        # Count total unread notifications
        total = db.query(func.count(Notification.id)).filter(
            Notification.user_id == current_user.id,
            Notification.is_read == False
        ).scalar() or 0

        # Query unread notifications with pagination (already sorted by created_at DESC via index)
        unread_notifications_db = db.query(Notification).filter(
            Notification.user_id == current_user.id,
            Notification.is_read == False
        ).order_by(Notification.created_at.desc()).offset(offset).limit(limit).all()

        # Convert to dict format
        paginated = [
            {
                "id": f"notif-{n.id}",
                "user_id": n.user_id,
                "title": n.title,
                "message": n.message,
                "type": n.type,
                "is_read": n.is_read,
                "created_at": format_datetime_iso(n.created_at),
                "read_at": format_datetime_iso(n.read_at) if n.read_at else None
            }
            for n in unread_notifications_db
        ]
    except Exception as e:
        logger.error(f"Error fetching unread notifications for user {current_user.id}: {e}", exc_info=True)
        total = 0
        paginated = []

    # OPTIMIZATION: Add cache headers for client-side caching
    from backend.core.response_formatter import add_cache_headers
    add_cache_headers(response, max_age=30, public=False)  # Cache for 30 seconds

    # OPTIMIZATION: Use list comprehension with error handling for serialization
    try:
        items = [NotificationResponse(**n) for n in paginated]
    except Exception as e:
        logger.error(f"Error serializing notifications: {e}")
        # Filter out invalid notifications and continue
        items = []
        for n in paginated:
            try:
                items.append(NotificationResponse(**n))
            except Exception as e:
                logger.warning(
                    f"Skipping invalid notification: {n.get('id', 'unknown')}",
                    exc_info=True,
                    extra={"notification_data": n, "error": str(e)}
                )

    return PaginatedNotificationsResponse(
        items=items,
        total=total,
        unread_count=total,
        limit=limit,
        offset=offset,
        has_more=(offset + limit) < total
    )


@router.post("/read", status_code=200)
async def mark_notifications_read(
    read_data: MarkReadRequest,
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_user),
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Mark notifications as read

    **Example Request:**
    ```bash
    curl -X POST "http://localhost:9001/api/notifications/read" \
         -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
         -H "Content-Type: application/json" \
         -d '{
           "notification_ids": ["notif-1234567890", "notif-1234567891"]
         }'
    ```

    **Example Response:**
    ```json
    {
      "message": "Notifications marked as read",
      "count": 2
    }
    ```
    """
    # Rate limiting
    client_id = current_user.email
    if not check_rate_limit(client_id):
        raise HTTPException(status_code=429, detail=RATE_LIMIT_EXCEEDED)

    # Add rate limit headers
    rate_limit_status = get_rate_limit_status(client_id)
    add_rate_limit_headers(
        response,
        remaining=rate_limit_status["remaining"],
        reset_at=int(time.time()) + rate_limit_status["reset_in"]
    )

    # OPTIMIZATION: Update notifications in database
    from backend.models.notification import Notification

    try:
        # Extract numeric IDs from "notif-{id}" format
        numeric_ids = []
        for nid in read_data.notification_ids:
            if nid.startswith("notif-"):
                try:
                    numeric_ids.append(int(nid.replace("notif-", "")))
                except ValueError:
                    continue

        if not numeric_ids:
            raise HTTPException(status_code=400, detail=INVALID_NOTIFICATION_ID_FORMAT)

        # Update notifications in database
        read_at = datetime.now(timezone.utc)
        count = db.query(Notification).filter(
            Notification.id.in_(numeric_ids),
            Notification.user_id == current_user.id,
            Notification.is_read == False
        ).update({
            Notification.is_read: True,
            Notification.read_at: read_at
        }, synchronize_session=False)

        db.commit()

        if count == 0:
            raise HTTPException(status_code=404, detail="No unread notifications found with provided IDs")

        return {
            "message": "Notifications marked as read",
            "count": count
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error marking notifications as read: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error updating notifications"
        )


@router.delete("/{notification_id}", status_code=200)
async def delete_notification(
    request: Request,
    response: Response,
    notification_id: str,
    current_user: User = Depends(get_current_user),
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Delete a notification

    **Example Request:**
    ```bash
    curl -X DELETE "http://localhost:9001/api/notifications/notif-1234567890" \
         -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    ```

    **Example Response:**
    ```json
    {
      "message": "Notification deleted successfully"
    }
    ```
    """
    # Rate limiting
    client_id = current_user.email
    if not check_rate_limit(client_id):
        raise HTTPException(status_code=429, detail=RATE_LIMIT_EXCEEDED)

    # Add rate limit headers
    rate_limit_status = get_rate_limit_status(client_id)
    add_rate_limit_headers(
        response,
        remaining=rate_limit_status["remaining"],
        reset_at=int(time.time()) + rate_limit_status["reset_in"]
    )

    # Input sanitization - validate notification_id format
    if not notification_id or len(notification_id) > 100:
        raise HTTPException(status_code=400, detail=INVALID_NOTIFICATION_ID_FORMAT)

    # Sanitize notification_id (alphanumeric, hyphens, underscores only)
    if not re.match(r'^[A-Za-z0-9_-]+$', notification_id):
        raise HTTPException(status_code=400, detail=INVALID_NOTIFICATION_ID_FORMAT)

    # OPTIMIZATION: Delete notification from database
    from backend.models.notification import Notification

    try:
        # Extract numeric ID from "notif-{id}" format
        if not notification_id.startswith("notif-"):
            raise HTTPException(status_code=400, detail=INVALID_NOTIFICATION_ID_FORMAT)

        try:
            numeric_id = int(notification_id.replace("notif-", ""))
        except ValueError:
            raise HTTPException(status_code=400, detail=INVALID_NOTIFICATION_ID_FORMAT)

        # Delete notification (only if it belongs to the user)
        notification = db.query(Notification).filter(
            Notification.id == numeric_id,
            Notification.user_id == current_user.id
        ).first()

        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")

        db.delete(notification)
        db.commit()

        return {
            "message": "Notification deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting notification: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error deleting notification"
        )

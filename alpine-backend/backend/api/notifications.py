"""
Notifications API endpoints for Alpine Backend
GET unread, POST read, DELETE
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import time

from backend.core.database import get_db
from backend.models.user import User
from backend.core.rate_limit import check_rate_limit
from backend.api.auth import get_current_user

router = APIRouter(prefix="/api/notifications", tags=["notifications"])

# Rate limiting
RATE_LIMIT_WINDOW = 60
RATE_LIMIT_MAX = 100

# Mock notifications database (in production, use real database)
NOTIFICATIONS_DB = {}


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


def get_user_notifications(user_id: int) -> List[dict]:
    """Get notifications for user"""
    if user_id not in NOTIFICATIONS_DB:
        NOTIFICATIONS_DB[user_id] = []
    return NOTIFICATIONS_DB[user_id]


@router.get("/unread", response_model=PaginatedNotificationsResponse)
async def get_unread_notifications(
    limit: int = Query(20, ge=1, le=100, description="Number of notifications to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: User = Depends(get_current_user),
    authorization: Optional[str] = Header(None)
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
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    # Get user notifications
    all_notifications = get_user_notifications(current_user.id)
    unread_notifications = [n for n in all_notifications if not n.get("is_read", False)]
    
    # Sort by created_at (newest first)
    unread_notifications.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    
    # Paginate
    total = len(unread_notifications)
    paginated = unread_notifications[offset:offset + limit]
    
    return PaginatedNotificationsResponse(
        items=[NotificationResponse(**n) for n in paginated],
        total=total,
        unread_count=total,
        limit=limit,
        offset=offset,
        has_more=offset + limit < total
    )


@router.post("/read", status_code=200)
async def mark_notifications_read(
    read_data: MarkReadRequest,
    current_user: User = Depends(get_current_user),
    authorization: Optional[str] = Header(None)
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
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    # Get user notifications
    notifications = get_user_notifications(current_user.id)
    
    # Mark as read
    count = 0
    for notification in notifications:
        if notification.get("id") in read_data.notification_ids:
            notification["is_read"] = True
            notification["read_at"] = datetime.utcnow().isoformat() + "Z"
            count += 1
    
    if count == 0:
        raise HTTPException(status_code=404, detail="No notifications found with provided IDs")
    
    return {
        "message": "Notifications marked as read",
        "count": count
    }


@router.delete("/{notification_id}", status_code=200)
async def delete_notification(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    authorization: Optional[str] = Header(None)
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
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    # Get user notifications
    notifications = get_user_notifications(current_user.id)
    
    # Find and remove notification
    found = False
    for i, notification in enumerate(notifications):
        if notification.get("id") == notification_id:
            notifications.pop(i)
            found = True
            break
    
    if not found:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return {"message": "Notification deleted successfully"}


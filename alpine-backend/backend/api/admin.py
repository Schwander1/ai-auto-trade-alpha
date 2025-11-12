"""
Admin API endpoints for Alpine Backend
GET analytics, GET users, GET revenue
Protected endpoints - admin only
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timedelta
import time

from backend.core.database import get_db
from backend.models.user import User, UserTier
from backend.api.auth import get_current_user, check_rate_limit

router = APIRouter(prefix="/api/admin", tags=["admin"])

# Rate limiting
RATE_LIMIT_WINDOW = 60
RATE_LIMIT_MAX = 100

# Admin email list (in production, use role-based access control)
ADMIN_EMAILS = ["admin@alpineanalytics.ai"]  # Add your admin email


def is_admin(user: User) -> bool:
    """Check if user is admin"""
    return user.email in ADMIN_EMAILS


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require admin access"""
    if not is_admin(current_user):
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    return current_user


class AnalyticsResponse(BaseModel):
    """Analytics response"""
    total_users: int
    active_users: int
    new_users_today: int
    new_users_this_week: int
    new_users_this_month: int
    users_by_tier: dict
    signals_delivered_today: int
    signals_delivered_this_week: int
    signals_delivered_this_month: int
    api_requests_today: int
    api_requests_this_week: int
    error_rate: float


class UserListResponse(BaseModel):
    """User list response"""
    id: int
    email: str
    full_name: str
    tier: str
    is_active: bool
    is_verified: bool
    created_at: str
    last_login: Optional[str] = None


class PaginatedUsersResponse(BaseModel):
    """Paginated users response"""
    items: List[UserListResponse]
    total: int
    limit: int
    offset: int
    has_more: bool


class RevenueResponse(BaseModel):
    """Revenue response"""
    total_revenue: float
    revenue_today: float
    revenue_this_week: float
    revenue_this_month: float
    revenue_this_year: float
    revenue_by_tier: dict
    active_subscriptions: int
    churn_rate: float
    mrr: float  # Monthly Recurring Revenue


@router.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics(
    current_user: User = Depends(require_admin),
    authorization: Optional[str] = Header(None)
):
    """
    Get platform analytics (admin only)
    
    **Example Request:**
    ```bash
    curl -X GET "http://localhost:9001/api/admin/analytics" \
         -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    ```
    
    **Example Response:**
    ```json
    {
      "total_users": 1247,
      "active_users": 892,
      "new_users_today": 12,
      "new_users_this_week": 87,
      "new_users_this_month": 342,
      "users_by_tier": {
        "starter": 623,
        "pro": 456,
        "elite": 168
      },
      "signals_delivered_today": 1245,
      "signals_delivered_this_week": 8723,
      "signals_delivered_this_month": 34567,
      "api_requests_today": 45678,
      "api_requests_this_week": 312456,
      "error_rate": 0.5
    }
    ```
    """
    # Rate limiting
    client_id = current_user.email
    if not check_rate_limit(client_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    # Get analytics from database (mock data for now)
    from backend.core.database import get_db
    db = next(get_db())
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    
    today = datetime.utcnow().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    new_users_today = db.query(User).filter(User.created_at >= datetime.combine(today, datetime.min.time())).count()
    new_users_this_week = db.query(User).filter(User.created_at >= datetime.combine(week_ago, datetime.min.time())).count()
    new_users_this_month = db.query(User).filter(User.created_at >= datetime.combine(month_ago, datetime.min.time())).count()
    
    # Users by tier
    users_by_tier = {
        "starter": db.query(User).filter(User.tier == UserTier.STARTER).count(),
        "pro": db.query(User).filter(User.tier == UserTier.PRO).count(),
        "elite": db.query(User).filter(User.tier == UserTier.ELITE).count()
    }
    
    return AnalyticsResponse(
        total_users=total_users,
        active_users=active_users,
        new_users_today=new_users_today,
        new_users_this_week=new_users_this_week,
        new_users_this_month=new_users_this_month,
        users_by_tier=users_by_tier,
        signals_delivered_today=1245,  # Mock data
        signals_delivered_this_week=8723,
        signals_delivered_this_month=34567,
        api_requests_today=45678,
        api_requests_this_week=312456,
        error_rate=0.5
    )


@router.get("/users", response_model=PaginatedUsersResponse)
async def get_users(
    limit: int = Query(20, ge=1, le=100, description="Number of users to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    tier: Optional[str] = Query(None, description="Filter by tier"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    current_user: User = Depends(require_admin),
    authorization: Optional[str] = Header(None)
):
    """
    Get all users (admin only)
    
    **Example Request:**
    ```bash
    curl -X GET "http://localhost:9001/api/admin/users?limit=20&tier=pro" \
         -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    ```
    
    **Example Response:**
    ```json
    {
      "items": [
        {
          "id": 1,
          "email": "user@example.com",
          "full_name": "John Doe",
          "tier": "pro",
          "is_active": true,
          "is_verified": false,
          "created_at": "2024-01-15T10:30:00Z",
          "last_login": null
        }
      ],
      "total": 1247,
      "limit": 20,
      "offset": 0,
      "has_more": true
    }
    ```
    """
    # Rate limiting
    client_id = current_user.email
    if not check_rate_limit(client_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    # Get users from database
    from backend.core.database import get_db
    db = next(get_db())
    query = db.query(User)
    
    # Apply filters
    if tier:
        try:
            tier_enum = UserTier(tier)
            query = query.filter(User.tier == tier_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid tier: {tier}")
    
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    # Get total count
    total = query.count()
    
    # Paginate
    users = query.order_by(User.created_at.desc()).offset(offset).limit(limit).all()
    
    return PaginatedUsersResponse(
        items=[
            UserListResponse(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                tier=user.tier.value,
                is_active=user.is_active,
                is_verified=user.is_verified,
                created_at=user.created_at.isoformat() if user.created_at else datetime.utcnow().isoformat() + "Z",
                last_login=None  # Add last_login tracking in production
            )
            for user in users
        ],
        total=total,
        limit=limit,
        offset=offset,
        has_more=offset + limit < total
    )


@router.get("/revenue", response_model=RevenueResponse)
async def get_revenue(
    current_user: User = Depends(require_admin),
    authorization: Optional[str] = Header(None)
):
    """
    Get revenue statistics (admin only)
    
    **Example Request:**
    ```bash
    curl -X GET "http://localhost:9001/api/admin/revenue" \
         -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    ```
    
    **Example Response:**
    ```json
    {
      "total_revenue": 124567.89,
      "revenue_today": 245.50,
      "revenue_this_week": 1723.45,
      "revenue_this_month": 8923.67,
      "revenue_this_year": 124567.89,
      "revenue_by_tier": {
        "starter": 30527.00,
        "pro": 45144.00,
        "elite": 48896.89
      },
      "active_subscriptions": 1247,
      "churn_rate": 2.5,
      "mrr": 8923.67
    }
    ```
    """
    # Rate limiting
    client_id = current_user.email
    if not check_rate_limit(client_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    # Get revenue from database (mock data for now)
    from backend.core.database import get_db
    db = next(get_db())
    
    # Count active subscriptions
    active_subscriptions = db.query(User).filter(
        User.is_active == True,
        User.stripe_subscription_id.isnot(None)
    ).count()
    
    # Calculate revenue by tier (mock calculation)
    from backend.core.config import settings
    starter_count = db.query(User).filter(User.tier == UserTier.STARTER, User.is_active == True).count()
    pro_count = db.query(User).filter(User.tier == UserTier.PRO, User.is_active == True).count()
    elite_count = db.query(User).filter(User.tier == UserTier.ELITE, User.is_active == True).count()
    
    revenue_by_tier = {
        "starter": starter_count * settings.TIER_STARTER_PRICE,
        "pro": pro_count * settings.TIER_PRO_PRICE,
        "elite": elite_count * settings.TIER_ELITE_PRICE
    }
    
    total_revenue = sum(revenue_by_tier.values())
    mrr = total_revenue  # Monthly Recurring Revenue
    
    return RevenueResponse(
        total_revenue=total_revenue,
        revenue_today=245.50,  # Mock data
        revenue_this_week=1723.45,
        revenue_this_month=mrr,
        revenue_this_year=total_revenue * 12,
        revenue_by_tier=revenue_by_tier,
        active_subscriptions=active_subscriptions,
        churn_rate=2.5,  # Mock data
        mrr=mrr
    )

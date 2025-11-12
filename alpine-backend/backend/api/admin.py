"""
Admin API endpoints for Alpine Backend
GET analytics, GET users, GET revenue
Protected endpoints - admin only
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Header
from sqlalchemy.orm import Session
from sqlalchemy import func, Integer
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timedelta
import time

from backend.core.database import get_db
from backend.core.rate_limit import check_rate_limit
from backend.core.cache import cache_response
from backend.models.user import User, UserTier
from backend.api.auth import get_current_user

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
@cache_response(ttl=300)  # Cache for 5 minutes
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
    
    # Get analytics from database - OPTIMIZED: Single query with aggregation (N+1 fix)
    from backend.core.database import get_db
    db = next(get_db())
    
    # Single query to get all user statistics
    today = datetime.utcnow().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    today_start = datetime.combine(today, datetime.min.time())
    week_start = datetime.combine(week_ago, datetime.min.time())
    month_start = datetime.combine(month_ago, datetime.min.time())
    
    # Aggregate all statistics in one query
    stats = db.query(
        func.count(User.id).label('total_users'),
        func.sum(func.cast(User.is_active, Integer)).label('active_users'),
        func.sum(func.cast(User.created_at >= today_start, Integer)).label('new_today'),
        func.sum(func.cast(User.created_at >= week_start, Integer)).label('new_week'),
        func.sum(func.cast(User.created_at >= month_start, Integer)).label('new_month'),
        func.sum(func.cast(User.tier == UserTier.STARTER, Integer)).label('starter_count'),
        func.sum(func.cast(User.tier == UserTier.PRO, Integer)).label('pro_count'),
        func.sum(func.cast(User.tier == UserTier.ELITE, Integer)).label('elite_count')
    ).first()
    
    total_users = stats.total_users or 0
    active_users = stats.active_users or 0
    new_users_today = stats.new_today or 0
    new_users_this_week = stats.new_week or 0
    new_users_this_month = stats.new_month or 0
    
    # Users by tier
    users_by_tier = {
        "starter": stats.starter_count or 0,
        "pro": stats.pro_count or 0,
        "elite": stats.elite_count or 0
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
@cache_response(ttl=300)  # Cache for 5 minutes
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
    
    # OPTIMIZED: Single query for revenue statistics (N+1 fix)
    from backend.core.database import get_db
    from backend.core.config import settings
    db = next(get_db())
    
    # Single aggregated query for all revenue statistics
    revenue_stats = db.query(
        func.sum(func.cast(
            (User.is_active == True) & (User.stripe_subscription_id.isnot(None)),
            Integer
        )).label('active_subscriptions'),
        func.sum(func.cast(
            (User.tier == UserTier.STARTER) & (User.is_active == True),
            Integer
        )).label('starter_count'),
        func.sum(func.cast(
            (User.tier == UserTier.PRO) & (User.is_active == True),
            Integer
        )).label('pro_count'),
        func.sum(func.cast(
            (User.tier == UserTier.ELITE) & (User.is_active == True),
            Integer
        )).label('elite_count')
    ).first()
    
    active_subscriptions = revenue_stats.active_subscriptions or 0
    starter_count = revenue_stats.starter_count or 0
    pro_count = revenue_stats.pro_count or 0
    elite_count = revenue_stats.elite_count or 0
    
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

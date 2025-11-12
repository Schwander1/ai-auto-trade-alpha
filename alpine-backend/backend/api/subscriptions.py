"""
Subscription management API endpoints for Alpine Backend
GET plan, POST upgrade, GET invoices
"""

from fastapi import APIRouter, HTTPException, Depends, status, Query, Header, Request, Response
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
import time
import stripe
import hmac
import hashlib
import logging

from backend.core.database import get_db
from backend.core.config import settings
from backend.core.input_sanitizer import sanitize_tier
from backend.core.response_formatter import add_rate_limit_headers
from backend.core.security_logging import log_security_event, SecurityEvent
from backend.models.user import User, UserTier
from backend.core.rate_limit import check_rate_limit, get_rate_limit_status
from backend.api.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/subscriptions", tags=["subscriptions"])

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

# Rate limiting
RATE_LIMIT_WINDOW = 60
RATE_LIMIT_MAX = 100


class SubscriptionPlanResponse(BaseModel):
    """Subscription plan response"""
    tier: str
    price: int
    features: List[str]
    is_active: bool
    stripe_subscription_id: Optional[str] = None
    current_period_end: Optional[str] = None
    cancel_at_period_end: bool = False


class UpgradeRequest(BaseModel):
    """Upgrade subscription request"""
    tier: str = Field(..., description="Target tier: starter, pro, elite")
    
    @validator('tier')
    def validate_tier(cls, v):
        """Validate and sanitize tier"""
        return sanitize_tier(v)


class InvoiceResponse(BaseModel):
    """Invoice response"""
    id: str
    amount: int
    currency: str
    status: str
    created_at: str
    period_start: Optional[str] = None
    period_end: Optional[str] = None
    invoice_pdf: Optional[str] = None


class PaginatedInvoicesResponse(BaseModel):
    """Paginated invoices response"""
    items: List[InvoiceResponse]
    total: int
    limit: int
    offset: int
    has_more: bool


# Tier features mapping
TIER_FEATURES = {
    "starter": ["Basic signals", "Email support", "1 signal per day"],
    "pro": ["Premium signals", "Priority support", "10 signals per day", "Backtesting"],
    "elite": ["All signals", "24/7 support", "Unlimited signals", "Advanced backtesting", "API access"]
}

# Tier pricing mapping
TIER_PRICES = {
    "starter": settings.TIER_STARTER_PRICE,
    "pro": settings.TIER_PRO_PRICE,
    "elite": settings.TIER_ELITE_PRICE
}


@router.get("/plan", response_model=SubscriptionPlanResponse)
async def get_subscription_plan(
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_user),
    authorization: Optional[str] = Header(None)
):
    """
    Get current subscription plan
    
    **Example Request:**
    ```bash
    curl -X GET "http://localhost:9001/api/subscriptions/plan" \
         -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    ```
    
    **Example Response:**
    ```json
    {
      "tier": "starter",
      "price": 49,
      "features": [
        "Basic signals",
        "Email support",
        "1 signal per day"
      ],
      "is_active": true,
      "stripe_subscription_id": "sub_1234567890",
      "current_period_end": "2024-02-15T10:30:00Z",
      "cancel_at_period_end": false
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
    
    # Get Stripe subscription if exists
    stripe_subscription = None
    current_period_end = None
    cancel_at_period_end = False
    
    if current_user.stripe_subscription_id:
        try:
            stripe_subscription = stripe.Subscription.retrieve(current_user.stripe_subscription_id)
            current_period_end = datetime.fromtimestamp(stripe_subscription.current_period_end).isoformat() + "Z"
            cancel_at_period_end = stripe_subscription.cancel_at_period_end
        except stripe.error.StripeError:
            pass  # Subscription not found or error
    
    return SubscriptionPlanResponse(
        tier=current_user.tier.value,
        price=TIER_PRICES.get(current_user.tier.value, 0),
        features=TIER_FEATURES.get(current_user.tier.value, []),
        is_active=current_user.is_active,
        stripe_subscription_id=current_user.stripe_subscription_id,
        current_period_end=current_period_end,
        cancel_at_period_end=cancel_at_period_end
    )


@router.post("/upgrade", response_model=dict)
async def upgrade_subscription(
    upgrade_data: UpgradeRequest,
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    """
    Upgrade subscription plan
    
    **Example Request:**
    ```bash
    curl -X POST "http://localhost:9001/api/subscriptions/upgrade" \
         -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
         -H "Content-Type: application/json" \
         -d '{
           "tier": "pro"
         }'
    ```
    
    **Example Response:**
    ```json
    {
      "message": "Subscription upgraded successfully",
      "tier": "pro",
      "checkout_url": "https://checkout.stripe.com/pay/cs_..."
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
    
    # Tier is already validated by Pydantic validator
    
    # Check if already at or above requested tier
    tier_order = {"starter": 1, "pro": 2, "elite": 3}
    if tier_order.get(upgrade_data.tier, 0) <= tier_order.get(current_user.tier.value, 0):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Already at or above {upgrade_data.tier} tier"
        )
    
    # Create Stripe checkout session
    try:
        price_id_map = {
            "starter": settings.STRIPE_STARTER_PRICE_ID,  # Founder tier
            "pro": settings.STRIPE_PRO_PRICE_ID,  # Professional tier
            "elite": settings.STRIPE_ELITE_PRICE_ID  # Institutional tier
        }
        
        price_id = price_id_map.get(upgrade_data.tier)
        if not price_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Price ID not configured for tier: {upgrade_data.tier}"
            )
        
        checkout_session = stripe.checkout.Session.create(
            customer=current_user.stripe_customer_id,
            payment_method_types=["card"],
            line_items=[{
                "price": price_id,
                "quantity": 1,
            }],
            mode="subscription",
            success_url=f"{settings.FRONTEND_URL}/subscription/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{settings.FRONTEND_URL}/subscription/cancel",
            metadata={
                "user_id": str(current_user.id),
                "tier": upgrade_data.tier
            }
        )
        
        # Log subscription upgrade attempt
        log_security_event(
            SecurityEvent.ADMIN_ACTION,
            user_id=current_user.id,
            email=current_user.email,
            details={"action": "subscription_upgrade_initiated", "tier": upgrade_data.tier},
            request=request
        )
        
        return {
            "message": "Subscription upgrade initiated",
            "tier": upgrade_data.tier,
            "checkout_url": checkout_session.url
        }
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error during subscription upgrade: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Payment processing error. Please try again later."
        )


@router.get("/invoices", response_model=PaginatedInvoicesResponse)
async def get_invoices(
    request: Request,
    response: Response,
    limit: int = Query(10, ge=1, le=100, description="Number of invoices to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: User = Depends(get_current_user),
    authorization: Optional[str] = Header(None)
):
    """
    Get subscription invoices with pagination
    
    **Example Request:**
    ```bash
    curl -X GET "http://localhost:9001/api/subscriptions/invoices?limit=10&offset=0" \
         -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    ```
    
    **Example Response:**
    ```json
    {
      "items": [
        {
          "id": "in_1234567890",
          "amount": 4900,
          "currency": "usd",
          "status": "paid",
          "created_at": "2024-01-15T10:30:00Z",
          "period_start": "2024-01-01T00:00:00Z",
          "period_end": "2024-02-01T00:00:00Z",
          "invoice_pdf": "https://pay.stripe.com/invoice/..."
        }
      ],
      "total": 5,
      "limit": 10,
      "offset": 0,
      "has_more": false
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
    
    # Get invoices from Stripe
    if not current_user.stripe_customer_id:
        return PaginatedInvoicesResponse(
            items=[],
            total=0,
            limit=limit,
            offset=offset,
            has_more=False
        )
    
    try:
        invoices = stripe.Invoice.list(
            customer=current_user.stripe_customer_id,
            limit=limit,
            starting_after=None  # Implement pagination properly
        )
        
        invoice_items = []
        for invoice in invoices.data:
            invoice_items.append(InvoiceResponse(
                id=invoice.id,
                amount=invoice.amount_paid,
                currency=invoice.currency,
                status=invoice.status,
                created_at=datetime.fromtimestamp(invoice.created).isoformat() + "Z",
                period_start=datetime.fromtimestamp(invoice.period_start).isoformat() + "Z" if invoice.period_start else None,
                period_end=datetime.fromtimestamp(invoice.period_end).isoformat() + "Z" if invoice.period_end else None,
                invoice_pdf=invoice.invoice_pdf
            ))
        
        return PaginatedInvoicesResponse(
            items=invoice_items,
            total=invoices.total_count,
            limit=limit,
            offset=offset,
            has_more=invoices.has_more
        )
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error fetching invoices: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch invoices. Please try again later."
        )


"""Stripe Payment Integration - Production Ready"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import stripe
from backend.core.config import settings

router = APIRouter(prefix="/api/v1/payments", tags=["payments"])

# Use test key for now (replace with real key in production)
stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', 'sk_test_placeholder')

class CheckoutRequest(BaseModel):
    tier: str
    email: str

@router.post("/create-checkout")
async def create_checkout(data: CheckoutRequest):
    """Create Stripe checkout session"""
    
    prices = {
        "starter": {"amount": 4900, "name": "Alpine Starter"},
        "pro": {"amount": 9900, "name": "Alpine Pro"},
        "elite": {"amount": 24900, "name": "Alpine Elite"}
    }
    
    if data.tier not in prices:
        raise HTTPException(status_code=400, detail="Invalid tier")
    
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {'name': prices[data.tier]['name']},
                    'unit_amount': prices[data.tier]['amount'],
                    'recurring': {'interval': 'month'}
                },
                'quantity': 1,
            }],
            mode='subscription',
            success_url='https://alpineanalytics.ai/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url='https://alpineanalytics.ai/pricing',
            customer_email=data.email,
            metadata={'tier': data.tier}
        )
        return {"checkout_url": session.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/plans")
async def get_plans():
    """Get pricing plans"""
    return {
        "plans": [
            {"tier": "starter", "price": 49, "features": ["75%+ signals", "Email", "Basic support"]},
            {"tier": "pro", "price": 99, "popular": True, "features": ["85%+ signals", "SMS", "Priority support", "API"]},
            {"tier": "elite", "price": 249, "features": ["95%+ signals", "Push", "White-glove", "Custom"]}
        ]
    }

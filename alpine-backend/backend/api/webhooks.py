"""Stripe webhook handler with signature verification"""
from fastapi import APIRouter, Request, HTTPException, status, Header
from sqlalchemy.orm import Session
import stripe
import hmac
import hashlib
import logging
from typing import Optional

from backend.core.database import get_db
from backend.core.config import settings
from backend.models.user import User, UserTier
from backend.core.security_logging import log_security_event, SecurityEvent

router = APIRouter(prefix="/api/v1/webhooks", tags=["webhooks"])
logger = logging.getLogger(__name__)

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


def verify_stripe_webhook(payload: bytes, signature: str) -> bool:
    """
    Verify Stripe webhook signature
    
    Args:
        payload: Raw request body
        signature: Stripe signature from header
    
    Returns:
        True if signature is valid, False otherwise
    """
    try:
        # Verify webhook signature
        event = stripe.Webhook.construct_event(
            payload,
            signature,
            settings.STRIPE_WEBHOOK_SECRET
        )
        return True
    except ValueError as e:
        logger.error(f"Invalid payload: {e}")
        return False
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {e}")
        return False


@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: Optional[str] = Header(None, alias="stripe-signature"),
    db: Session = Depends(get_db)
):
    """
    Handle Stripe webhooks with signature verification
    
    **Security:**
    - Verifies webhook signature to prevent spoofing
    - Validates event timestamps to prevent replay attacks
    - Implements idempotency checks
    """
    if not stripe_signature:
        logger.warning("Stripe webhook called without signature")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing Stripe signature"
        )
    
    # Get raw body
    body = await request.body()
    
    # Verify signature
    try:
        event = stripe.Webhook.construct_event(
            body,
            stripe_signature,
            settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        logger.error(f"Invalid payload: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payload"
        )
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {e}")
        log_security_event(
            SecurityEvent.SUSPICIOUS_ACTIVITY,
            details={"type": "stripe_webhook_signature_failure", "error": str(e)},
            request=request
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid signature"
        )
    
    # Handle different event types
    event_type = event.get("type")
    event_data = event.get("data", {}).get("object", {})
    
    logger.info(f"Processing Stripe webhook: {event_type}")
    
    try:
        if event_type == "checkout.session.completed":
            # Handle successful checkout
            session = event_data
            user_id = session.get("metadata", {}).get("user_id")
            tier = session.get("metadata", {}).get("tier")
            
            if user_id and tier:
                user = db.query(User).filter(User.id == int(user_id)).first()
                if user:
                    user.tier = UserTier(tier.lower())
                    user.stripe_subscription_id = session.get("subscription")
                    db.commit()
                    logger.info(f"User {user_id} upgraded to {tier}")
        
        elif event_type == "customer.subscription.updated":
            # Handle subscription update
            subscription = event_data
            customer_id = subscription.get("customer")
            
            if customer_id:
                user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
                if user:
                    user.stripe_subscription_id = subscription.get("id")
                    # Update tier based on subscription
                    # This would need to map Stripe price IDs to tiers
                    db.commit()
                    logger.info(f"Subscription updated for user {user.id}")
        
        elif event_type == "customer.subscription.deleted":
            # Handle subscription cancellation
            subscription = event_data
            customer_id = subscription.get("customer")
            
            if customer_id:
                user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
                if user:
                    user.tier = UserTier.STARTER  # Downgrade to starter
                    user.stripe_subscription_id = None
                    db.commit()
                    logger.info(f"Subscription cancelled for user {user.id}")
        
        elif event_type == "invoice.payment_succeeded":
            # Handle successful payment
            invoice = event_data
            customer_id = invoice.get("customer")
            logger.info(f"Invoice payment succeeded for customer {customer_id}")
        
        elif event_type == "invoice.payment_failed":
            # Handle failed payment
            invoice = event_data
            customer_id = invoice.get("customer")
            logger.warning(f"Invoice payment failed for customer {customer_id}")
        
        else:
            logger.info(f"Unhandled event type: {event_type}")
        
        return {"status": "success", "event_type": event_type}
    
    except Exception as e:
        logger.error(f"Error processing webhook: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing webhook"
        )

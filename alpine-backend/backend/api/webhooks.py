"""Stripe webhook handler with signature verification, idempotency, and replay protection"""
from fastapi import APIRouter, Request, HTTPException, Depends, status, Header
from sqlalchemy.orm import Session
import stripe
import hmac
import hashlib
import logging
from typing import Optional
from datetime import datetime, timedelta

from backend.core.database import get_db
from backend.core.config import settings
from backend.models.user import User, UserTier
from backend.core.security_logging import log_security_event, SecurityEvent
from backend.core.cache import redis_client

router = APIRouter(prefix="/api/v1/webhooks", tags=["webhooks"])
logger = logging.getLogger(__name__)

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

# SECURITY: Webhook idempotency and replay protection
WEBHOOK_EVENT_TTL = 300  # 5 minutes - reject events older than this
WEBHOOK_IDEMPOTENCY_TTL = 86400  # 24 hours - remember processed events


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


def check_webhook_idempotency(event_id: str) -> bool:
    """
    Check if webhook event has already been processed (idempotency)
    
    Args:
        event_id: Stripe event ID
    
    Returns:
        True if event already processed, False otherwise
    """
    if not redis_client:
        # Fallback to in-memory if Redis not available
        if not hasattr(check_webhook_idempotency, '_processed_events'):
            check_webhook_idempotency._processed_events = set()
        return event_id in check_webhook_idempotency._processed_events
    
    try:
        key = f"webhook:processed:{event_id}"
        return redis_client.exists(key) > 0
    except Exception as e:
        logger.error(f"Error checking webhook idempotency: {e}")
        return False


def mark_webhook_processed(event_id: str):
    """
    Mark webhook event as processed (idempotency)
    
    Args:
        event_id: Stripe event ID
    """
    if not redis_client:
        # Fallback to in-memory if Redis not available
        if not hasattr(mark_webhook_processed, '_processed_events'):
            mark_webhook_processed._processed_events = set()
        check_webhook_idempotency._processed_events.add(event_id)
        return
    
    try:
        key = f"webhook:processed:{event_id}"
        redis_client.setex(key, WEBHOOK_IDEMPOTENCY_TTL, "1")
    except Exception as e:
        logger.error(f"Error marking webhook as processed: {e}")


def validate_webhook_timestamp(event_created: int) -> bool:
    """
    Validate webhook event timestamp to prevent replay attacks
    
    Args:
        event_created: Unix timestamp when event was created
    
    Returns:
        True if event is recent enough, False if too old
    """
    event_time = datetime.fromtimestamp(event_created)
    now = datetime.utcnow()
    age = (now - event_time).total_seconds()
    
    if age > WEBHOOK_EVENT_TTL:
        logger.warning(f"Rejected old webhook event: {age:.0f} seconds old (max: {WEBHOOK_EVENT_TTL}s)")
        return False
    
    return True


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
    
    # SECURITY: Check idempotency (prevent duplicate processing)
    event_id = event.get("id")
    if event_id and check_webhook_idempotency(event_id):
        logger.info(f"Webhook event {event_id} already processed, skipping (idempotency)")
        return {"status": "success", "event_type": event.get("type"), "idempotent": True}
    
    # SECURITY: Validate event timestamp (prevent replay attacks)
    event_created = event.get("created")
    if event_created and not validate_webhook_timestamp(event_created):
        log_security_event(
            SecurityEvent.SUSPICIOUS_ACTIVITY,
            details={"type": "stripe_webhook_replay_attempt", "event_id": event_id, "age_seconds": (datetime.utcnow() - datetime.fromtimestamp(event_created)).total_seconds()},
            request=request
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Webhook event is too old (replay attack prevention)"
        )
    
    # Handle different event types
    event_type = event.get("type")
    event_data = event.get("data", {}).get("object", {})
    
    logger.info(f"Processing Stripe webhook: {event_type} (ID: {event_id})")
    
    try:
        if event_type == "checkout.session.completed":
            # Handle successful checkout
            session = event_data
            user_id = session.get("metadata", {}).get("user_id")
            tier = session.get("metadata", {}).get("tier")
            
            if user_id and tier:
                try:
                    user = db.query(User).filter(User.id == int(user_id)).first()
                    if user:
                        user.tier = UserTier(tier.lower())
                        user.stripe_subscription_id = session.get("subscription")
                        db.commit()
                        logger.info(f"User {user_id} upgraded to {tier}")
                except Exception as e:
                    db.rollback()
                    logger.error(f"Error updating user {user_id} for checkout: {e}", exc_info=True)
                    raise
        
        elif event_type == "customer.subscription.updated":
            # Handle subscription update
            subscription = event_data
            customer_id = subscription.get("customer")
            
            if customer_id:
                try:
                    user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
                    if user:
                        user.stripe_subscription_id = subscription.get("id")
                        # Update tier based on subscription
                        # This would need to map Stripe price IDs to tiers
                        db.commit()
                        logger.info(f"Subscription updated for user {user.id}")
                except Exception as e:
                    db.rollback()
                    logger.error(f"Error updating subscription for customer {customer_id}: {e}", exc_info=True)
                    raise
        
        elif event_type == "customer.subscription.deleted":
            # Handle subscription cancellation
            subscription = event_data
            customer_id = subscription.get("customer")
            
            if customer_id:
                try:
                    user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
                    if user:
                        user.tier = UserTier.STARTER  # Downgrade to starter
                        user.stripe_subscription_id = None
                        db.commit()
                        logger.info(f"Subscription cancelled for user {user.id}")
                except Exception as e:
                    db.rollback()
                    logger.error(f"Error cancelling subscription for customer {customer_id}: {e}", exc_info=True)
                    raise
        
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
        
        # SECURITY: Mark event as processed (idempotency) - only after successful processing
        # If marking fails, log but don't fail the webhook (idempotency is best-effort)
        if event_id:
            try:
                mark_webhook_processed(event_id)
            except Exception as e:
                logger.warning(f"Failed to mark webhook {event_id} as processed: {e}", exc_info=True)
                # Don't fail the webhook if idempotency marking fails
        
        return {"status": "success", "event_type": event_type, "event_id": event_id}
    
    except HTTPException:
        # Re-raise HTTP exceptions with rollback
        db.rollback()
        raise
    except Exception as e:
        logger.error(f"Error processing webhook: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing webhook"
        )

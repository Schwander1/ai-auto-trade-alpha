"""Main FastAPI application"""
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
import stripe
import logging
from pydantic import BaseModel

from backend.core.config import settings
from backend.core.database import get_db, engine, Base
from backend.core.metrics import get_metrics
from backend.core.security_headers import SecurityHeadersMiddleware
from backend.core.csrf import CSRFProtectionMiddleware
from backend.core.request_tracking import RequestTrackingMiddleware
from backend.core.request_logging import RequestLoggingMiddleware
from backend.core.metrics_middleware import MetricsMiddleware
from backend.models.user import User, UserTier
from backend.models.signal import Signal
from backend.models.notification import Notification
from backend.models.backtest import Backtest
from backend.auth.security import verify_password, get_password_hash, create_access_token, verify_token

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

# Create database tables
Base.metadata.create_all(bind=engine)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="Alpine Analytics API",
    version="1.0.0",
    description="AI Trading Signal Platform",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_url="/api/v1/openapi.json"
)

# Add middleware (order matters - first added is last executed)
app.add_middleware(SecurityHeadersMiddleware)  # Add security headers
app.add_middleware(CSRFProtectionMiddleware)  # CSRF protection
app.add_middleware(RequestTrackingMiddleware)  # Request ID tracking
app.add_middleware(RequestLoggingMiddleware)  # Request/response logging with PII redaction
app.add_middleware(MetricsMiddleware)  # Prometheus metrics
app.add_middleware(GZipMiddleware, minimum_size=1000)  # Compression

# CORS middleware - Production-ready configuration
from backend.core.config import settings

# CORS configuration - whitelist only trusted origins
ALLOWED_ORIGINS = [
    settings.FRONTEND_URL,
    "http://localhost:3000",
    "http://localhost:3001",
    "http://91.98.153.49:3000",
    "https://91.98.153.49:3000",  # HTTPS variant
]

# Remove any wildcard or unsafe origins
ALLOWED_ORIGINS = [origin for origin in ALLOWED_ORIGINS if origin and origin != "*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With", "X-CSRF-Token", "X-Request-ID"],
    expose_headers=["X-Total-Count", "X-Page-Count", "X-RateLimit-Remaining", "X-Request-ID"],
    max_age=3600,  # Cache preflight requests for 1 hour
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

# ===== PYDANTIC SCHEMAS =====

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str

class UserResponse(BaseModel):
    email: str
    full_name: str
    tier: str
    is_active: bool

class SignalResponse(BaseModel):
    id: int
    symbol: str
    action: str
    price: float
    confidence: float
    created_at: str

# ===== HELPER FUNCTIONS =====

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(User).filter(User.email == payload.get("sub")).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

# ===== HEALTH CHECK =====

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Comprehensive health check with database and Redis connectivity"""
    from sqlalchemy import text
    from backend.core.cache import redis_client
    
    health_status = {
        "status": "healthy",
        "service": "Alpine Analytics API",
        "version": "1.0.0",
        "domain": settings.DOMAIN,
        "checks": {}
    }
    
    # Check database
    try:
        db.execute(text("SELECT 1"))
        health_status["checks"]["database"] = "healthy"
    except Exception as e:
        health_status["checks"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check Redis
    try:
        if redis_client:
            redis_client.ping()
            health_status["checks"]["redis"] = "healthy"
        else:
            health_status["checks"]["redis"] = "not_configured"
    except Exception as e:
        health_status["checks"]["redis"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check secrets manager access
    try:
        import sys
        from pathlib import Path
        shared_path = Path(__file__).parent.parent.parent.parent.parent / "packages" / "shared"
        if shared_path.exists():
            sys.path.insert(0, str(shared_path))
            from utils.secrets_manager import get_secrets_manager
            secrets_manager = get_secrets_manager()
            # Try to access a secret to verify AWS Secrets Manager is working
            test_secret = secrets_manager.get_secret("jwt-secret", service="alpine-backend", required=False)
            if test_secret:
                health_status["checks"]["secrets"] = "healthy"
            else:
                health_status["checks"]["secrets"] = "degraded (using fallback)"
        else:
            health_status["checks"]["secrets"] = "not_configured"
    except Exception as e:
        health_status["checks"]["secrets"] = f"degraded: {str(e)}"
        # Don't mark overall status as degraded for secrets fallback
    
    return health_status


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return get_metrics()


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler with structured error responses"""
    from backend.core.request_tracking import get_request_id
    
    request_id = get_request_id(request)
    
    logger.error(f"Unhandled exception: {exc}", exc_info=True, extra={
        "path": request.url.path,
        "method": request.method,
        "request_id": request_id,
    })
    
    # Don't expose internal error details in production
    error_message = str(exc) if settings.DEBUG else "An error occurred"
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": error_message,
            "path": request.url.path,
            "request_id": request_id
        }
    )

# ===== AUTHENTICATION ENDPOINTS =====

@app.post("/api/auth/signup")
async def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create Stripe customer
    try:
        stripe_customer = stripe.Customer.create(
            email=user_data.email,
            name=user_data.full_name,
            metadata={"source": "alpine_signup"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stripe error: {str(e)}")
    
    # Create user
    user = User(
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        stripe_customer_id=stripe_customer.id,
        tier=UserTier.STARTER
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create token
    access_token = create_access_token(data={"sub": user.email})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "email": user.email,
            "full_name": user.full_name,
            "tier": user.tier.value
        }
    }

@app.post("/api/auth/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.email})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "email": user.email,
            "full_name": user.full_name,
            "tier": user.tier.value
        }
    }

@app.get("/api/auth/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return {
        "email": current_user.email,
        "full_name": current_user.full_name,
        "tier": current_user.tier.value,
        "is_active": current_user.is_active,
        "stripe_customer_id": current_user.stripe_customer_id
    }

# ===== STRIPE PAYMENT ENDPOINTS =====

@app.post("/api/payments/create-checkout-session")
async def create_checkout_session(
    tier: str,
    current_user: User = Depends(get_current_user)
):
    # Price mapping
    prices = {
        "starter": settings.TIER_STARTER_PRICE,
        "pro": settings.TIER_PRO_PRICE,
        "elite": settings.TIER_ELITE_PRICE
    }
    
    price = prices.get(tier.lower())
    if not price:
        raise HTTPException(status_code=400, detail="Invalid tier")
    
    try:
        # Create Stripe checkout session
        session = stripe.checkout.Session.create(
            customer=current_user.stripe_customer_id,
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': f'Alpine Analytics {tier.title()}',
                        'description': f'{tier.title()} tier subscription'
                    },
                    'unit_amount': price * 100,  # Convert to cents
                    'recurring': {'interval': 'month'},
                },
                'quantity': 1,
            }],
            mode='subscription',
            success_url=f'{settings.FRONTEND_URL}/dashboard?session_id={{CHECKOUT_SESSION_ID}}',
            cancel_url=f'{settings.FRONTEND_URL}/pricing',
            metadata={
                'user_id': current_user.id,
                'tier': tier
            }
        )
        
        return {"sessionId": session.id, "url": session.url}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Payment error: {str(e)}")

@app.post("/api/payments/webhook")
async def stripe_webhook(request: dict, db: Session = Depends(get_db)):
    """Handle Stripe webhooks"""
    # This would normally verify the webhook signature
    # For now, simplified version
    
    event_type = request.get('type')
    
    if event_type == 'checkout.session.completed':
        session = request.get('data', {}).get('object', {})
        user_id = session.get('metadata', {}).get('user_id')
        tier = session.get('metadata', {}).get('tier')
        
        if user_id and tier:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user.tier = UserTier(tier.lower())
                user.stripe_subscription_id = session.get('subscription')
                db.commit()
    
    return {"status": "success"}

# ===== SIGNAL ENDPOINTS =====

@app.get("/api/signals/live")
async def get_live_signals(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get live trading signals based on user tier"""
    
    # Confidence thresholds by tier
    thresholds = {
        UserTier.STARTER: 0.75,  # 75%+ confidence
        UserTier.PRO: 0.85,      # 85%+ confidence
        UserTier.ELITE: 0.95     # 95%+ confidence
    }
    
    min_confidence = thresholds.get(current_user.tier, 0.75)
    
    signals = db.query(Signal).filter(
        Signal.is_active == True,
        Signal.confidence >= min_confidence
    ).order_by(Signal.created_at.desc()).limit(limit).all()
    
    return {
        "signals": [
            {
                "id": s.id,
                "symbol": s.symbol,
                "action": s.action,
                "price": s.price,
                "confidence": s.confidence,
                "target_price": s.target_price,
                "stop_loss": s.stop_loss,
                "rationale": s.rationale,
                "created_at": str(s.created_at)
            }
            for s in signals
        ],
        "user_tier": current_user.tier.value,
        "min_confidence": min_confidence,
        "count": len(signals)
    }

@app.post("/api/signals/test")
async def create_test_signal(db: Session = Depends(get_db)):
    """Create a test signal for development"""
    import random
    import hashlib
    from datetime import datetime
    
    symbols = ['AAPL', 'TSLA', 'NVDA', 'MSFT', 'GOOGL']
    actions = ['BUY', 'SELL']
    
    symbol = random.choice(symbols)
    action = random.choice(actions)
    price = round(random.uniform(100, 500), 2)
    confidence = round(random.uniform(0.75, 0.99), 2)
    
    hash_data = f"{symbol}{datetime.utcnow().isoformat()}{confidence}"
    verification_hash = hashlib.sha256(hash_data.encode()).hexdigest()[:16]
    
    signal = Signal(
        symbol=symbol,
        action=action,
        price=price,
        confidence=confidence,
        target_price=price * 1.05 if action == 'BUY' else price * 0.95,
        stop_loss=price * 0.98 if action == 'BUY' else price * 1.02,
        rationale=f"Test signal for {symbol}",
        verification_hash=verification_hash,
        is_active=True
    )
    
    db.add(signal)
    db.commit()
    db.refresh(signal)
    
    return {
        "message": "Test signal created",
        "signal": {
            "symbol": signal.symbol,
            "action": signal.action,
            "confidence": signal.confidence
        }
    }

# ===== ADMIN ENDPOINTS =====

@app.get("/api/admin/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Get platform statistics"""
    total_users = db.query(User).count()
    total_signals = db.query(Signal).count()
    active_signals = db.query(Signal).filter(Signal.is_active == True).count()
    
    return {
        "total_users": total_users,
        "total_signals": total_signals,
        "active_signals": active_signals,
        "platform": "Alpine Analytics"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Payment routes
try:
    from backend.api.payments import router as payment_router
    app.include_router(payment_router)
except:
    pass

# Zapier webhooks

# Zapier webhooks

# Include all API routers
from backend.api import auth, auth_2fa, users, subscriptions, signals as signals_api, notifications, admin, webhooks, two_factor, security_dashboard
app.include_router(auth.router)
app.include_router(auth_2fa.router)
app.include_router(users.router)
app.include_router(subscriptions.router)
app.include_router(signals_api.router)
app.include_router(notifications.router)
app.include_router(admin.router)
app.include_router(webhooks.router)
app.include_router(two_factor.router)
app.include_router(security_dashboard.router)

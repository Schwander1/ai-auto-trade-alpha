"""Main FastAPI application"""
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import stripe
import logging
from pydantic import BaseModel

from backend.core.config import settings
from backend.core.database import get_db, get_engine, Base
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
# Create tables (lazy initialization - engine will be created on first use)
try:
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
except Exception as e:
    import logging
    logging.warning(f"Could not create database tables on startup: {e}. Tables will be created on first use.")

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
# SECURITY: Request size limit must be first to prevent DoS attacks
class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """Limit request body size to prevent DoS attacks"""
    MAX_REQUEST_SIZE = 10 * 1024 * 1024  # 10MB limit
    
    async def dispatch(self, request: Request, call_next):
        # Check Content-Length header if present
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                size = int(content_length)
                if size > self.MAX_REQUEST_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail=f"Request body too large. Maximum size: {self.MAX_REQUEST_SIZE / 1024 / 1024}MB"
                    )
            except ValueError:
                pass  # Invalid content-length, let request proceed
        
        response = await call_next(request)
        return response

app.add_middleware(RequestSizeLimitMiddleware)  # Request size limits (DoS prevention)
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
# NOTE: Use get_current_user from backend.api.auth instead of this duplicate
# This is kept for backward compatibility with legacy endpoints that will be migrated
from backend.api.auth import get_current_user as get_current_user_secure

# ===== HEALTH CHECK =====

# Track startup time for uptime calculation
_STARTUP_TIME = None

def get_startup_time():
    """Get or initialize startup time"""
    global _STARTUP_TIME
    if _STARTUP_TIME is None:
        _STARTUP_TIME = datetime.utcnow()
    return _STARTUP_TIME

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Comprehensive health check with database, Redis, system metrics, and uptime"""
    from sqlalchemy import text
    from backend.core.cache import redis_client
    import asyncio
    from asyncio import TimeoutError
    
    startup_time = get_startup_time()
    uptime_delta = datetime.utcnow() - startup_time
    uptime_seconds = int(uptime_delta.total_seconds())
    days = uptime_seconds // 86400
    hours = (uptime_seconds % 86400) // 3600
    minutes = (uptime_seconds % 3600) // 60
    uptime_formatted = f"{days}d {hours}h {minutes}m"
    
    health_status = {
        "status": "healthy",
        "service": "Alpine Analytics API",
        "version": "1.0.0",
        "domain": settings.DOMAIN,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "uptime_seconds": uptime_seconds,
        "uptime_formatted": uptime_formatted,
        "checks": {},
        "system": {}
    }
    
    # Check database with timeout
    try:
        def check_db_sync():
            db.execute(text("SELECT 1"))
            return True
        
        await asyncio.wait_for(asyncio.to_thread(check_db_sync), timeout=5.0)
        health_status["checks"]["database"] = "healthy"
    except TimeoutError:
        health_status["checks"]["database"] = "unhealthy: timeout"
        health_status["status"] = "degraded"
        logger.error("Database health check timed out")
    except Exception as e:
        health_status["checks"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
        logger.error(f"Database health check failed: {e}")
    
    # Check Redis with timeout
    try:
        if redis_client:
            def check_redis_sync():
                redis_client.ping()
                return True
            
            await asyncio.wait_for(asyncio.to_thread(check_redis_sync), timeout=2.0)
            health_status["checks"]["redis"] = "healthy"
        else:
            health_status["checks"]["redis"] = "not_configured"
    except TimeoutError:
        health_status["checks"]["redis"] = "unhealthy: timeout"
        health_status["status"] = "degraded"
        logger.error("Redis health check timed out")
    except Exception as e:
        health_status["checks"]["redis"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
        logger.error(f"Redis health check failed: {e}")
    
    # Check secrets manager access with timeout
    try:
        async def check_secrets():
            from backend.utils.secrets_manager import get_secrets_manager
            secrets_manager = get_secrets_manager()
            test_secret = secrets_manager.get_secret("jwt-secret", service="alpine-backend", required=False)
            return test_secret is not None
        
        has_secret = await asyncio.wait_for(check_secrets(), timeout=3.0)
        if has_secret:
            health_status["checks"]["secrets"] = "healthy"
        else:
            health_status["checks"]["secrets"] = "degraded (using fallback)"
    except TimeoutError:
        health_status["checks"]["secrets"] = "degraded: timeout"
        logger.warning("Secrets manager check timed out")
    except Exception as e:
        health_status["checks"]["secrets"] = f"degraded: {str(e)}"
        logger.warning(f"Secrets manager check failed: {e}")
        # Don't mark overall status as degraded for secrets fallback
    
    # Get system metrics (CPU, Memory, Disk)
    try:
        import psutil
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        health_status["system"] = {
            "cpu_percent": round(cpu_percent, 1),
            "memory_percent": round(memory.percent, 1),
            "disk_percent": round(disk.percent, 1)
        }
        
        # Mark as degraded if resources are high
        if cpu_percent > 90 or memory.percent > 90:
            health_status["status"] = "degraded"
        if disk.percent > 95:
            health_status["status"] = "unhealthy"
    except ImportError:
        health_status["system"] = {"error": "psutil not available"}
        logger.debug("psutil not available for system metrics")
    except Exception as e:
        health_status["system"] = {"error": str(e)}
        logger.warning(f"System metrics unavailable: {e}")
    
    return health_status


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    try:
        return get_metrics()
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=500,
            content={"error": "Metrics unavailable", "detail": str(e)}
        )


@app.get("/health/readiness")
async def health_readiness(db: Session = Depends(get_db)):
    """Kubernetes readiness probe - returns 200 only if service is ready to handle traffic"""
    from sqlalchemy import text
    from fastapi import HTTPException
    
    try:
        # Quick database check
        db.execute(text("SELECT 1"))
        return {"status": "ready", "timestamp": datetime.utcnow().isoformat() + "Z"}
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Service not ready: {str(e)}")


@app.get("/health/liveness")
async def health_liveness():
    """Kubernetes liveness probe - returns 200 if service is alive"""
    startup_time = get_startup_time()
    uptime_seconds = int((datetime.utcnow() - startup_time).total_seconds())
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "uptime_seconds": uptime_seconds
    }


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

# ===== LEGACY ENDPOINTS (DEPRECATED - Use /api/v1/* routers instead) =====
# These endpoints are kept for backward compatibility but should be migrated to router-based endpoints
# All new endpoints should use the router-based structure in backend/api/

# NOTE: Legacy endpoints below use simplified authentication and may not have all security features
# Migrate to router-based endpoints for full security (token blacklist, rate limiting, etc.)

# ===== LEGACY PAYMENT ENDPOINTS (DEPRECATED) =====
# Use /api/v1/payments/* and /api/v1/webhooks/stripe instead

# ===== LEGACY SIGNAL ENDPOINTS (DEPRECATED) =====
# Use /api/v1/signals/* instead
# Test endpoint removed - use proper signal generation in development

# ===== ADMIN ENDPOINTS =====
# SECURITY FIX: Admin endpoints now require authentication
# Use /api/v1/admin/* router endpoints instead (properly secured)

@app.get("/api/admin/stats")
async def get_stats(
    current_user: User = Depends(get_current_user_secure),
    db: Session = Depends(get_db)
):
    """
    Get platform statistics (ADMIN ONLY)
    
    SECURITY: This endpoint now requires authentication.
    Use /api/v1/admin/analytics for full admin features with proper authorization.
    """
    # Check if user is admin (basic check - use proper RBAC in router endpoints)
    from backend.api.admin import is_admin
    if not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
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
except ImportError:
    # Payment router not available - this is acceptable if payments module is optional
    pass
except Exception as e:
    logger.warning(f"Failed to load payment router: {e}")

# Zapier webhooks

# Zapier webhooks

# Include all API routers
from backend.api import auth, auth_2fa, users, subscriptions, signals as signals_api, notifications, admin, webhooks, two_factor, security_dashboard, external_signal_sync, roles
app.include_router(auth.router)
app.include_router(auth_2fa.router)
app.include_router(users.router)
app.include_router(subscriptions.router)
app.include_router(signals_api.router)
app.include_router(external_signal_sync.router)  # External signal sync endpoint (maintains entity separation)
app.include_router(notifications.router)
app.include_router(admin.router)
app.include_router(webhooks.router)
app.include_router(two_factor.router)
app.include_router(security_dashboard.router)
app.include_router(roles.router)  # RBAC role management

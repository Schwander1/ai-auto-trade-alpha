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
from backend.core.metrics import get_metrics, health_check_duration_seconds, health_check_total, health_check_cache_hits_total
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

# Health check cache (short TTL for near-real-time monitoring)
_health_check_cache = None
_health_check_cache_time = 0
HEALTH_CHECK_CACHE_TTL = 5  # Cache for 5 seconds to reduce load

@app.get("/health")
async def health_check():
    """Comprehensive health check with database, Redis, system metrics, and uptime - optimized with parallel checks and caching"""
    from sqlalchemy import text
    from backend.core.cache import redis_client
    from backend.core.database import get_db
    import asyncio
    from asyncio import TimeoutError
    import time
    
    # Check cache first (short TTL to reduce load while still being responsive)
    global _health_check_cache, _health_check_cache_time
    current_time = time.time()
    if _health_check_cache and (current_time - _health_check_cache_time) < HEALTH_CHECK_CACHE_TTL:
        # Return cached result with updated timestamp
        cached_result = _health_check_cache.copy()
        cached_result["timestamp"] = datetime.utcnow().isoformat() + "Z"
        cached_result["cached"] = True
        health_check_cache_hits_total.labels(endpoint='health').inc()
        health_check_total.labels(endpoint='health', status=cached_result.get('status', 'unknown')).inc()
        return cached_result
    
    start_time = time.time()
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
    
    # Define async check functions for parallel execution
    async def check_database_async():
        """Check database connectivity - optimized with connection reuse"""
        try:
            # Use connection pool directly for better performance
            from backend.core.database import get_engine
            engine = get_engine()
            
            def check_db_sync():
                try:
                    # Use connection pool directly (more efficient than session)
                    with engine.connect() as conn:
                        conn.execute(text("SELECT 1"))
                    return True
                except Exception as e:
                    logger.warning(f"Database check failed: {e}")
                    return False
            
            try:
                db_available = await asyncio.wait_for(asyncio.to_thread(check_db_sync), timeout=5.0)
                return {"status": "healthy" if db_available else "unavailable", "available": db_available}
            except TimeoutError:
                logger.error("Database health check timed out")
                return {"status": "unhealthy: timeout", "available": False}
        except Exception as e:
            logger.warning(f"Database connection unavailable: {e}")
            return {"status": f"unavailable: {str(e)}", "available": False}
    
    async def check_redis_async():
        """Check Redis connectivity"""
        try:
            if redis_client:
                def check_redis_sync():
                    redis_client.ping()
                    return True
                
                await asyncio.wait_for(asyncio.to_thread(check_redis_sync), timeout=2.0)
                return {"status": "healthy", "available": True}
            else:
                return {"status": "not_configured", "available": False}
        except TimeoutError:
            logger.error("Redis health check timed out")
            return {"status": "unhealthy: timeout", "available": False}
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return {"status": f"unhealthy: {str(e)}", "available": False}
    
    async def check_secrets_async():
        """Check secrets manager access"""
        try:
            from backend.utils.secrets_manager import get_secrets_manager
            secrets_manager = get_secrets_manager()
            test_secret = secrets_manager.get_secret("jwt-secret", service="alpine-backend", required=False)
            has_secret = test_secret is not None
            return {"status": "healthy" if has_secret else "degraded (using fallback)", "available": has_secret}
        except TimeoutError:
            logger.warning("Secrets manager check timed out")
            return {"status": "degraded: timeout", "available": False}
        except Exception as e:
            logger.warning(f"Secrets manager check failed: {e}")
            return {"status": f"degraded: {str(e)}", "available": False}
    
    async def get_system_metrics_async():
        """Get system metrics"""
        try:
            import psutil
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "cpu_percent": round(cpu_percent, 1),
                "memory_percent": round(memory.percent, 1),
                "disk_percent": round(disk.percent, 1),
                "error": None
            }
        except ImportError:
            logger.debug("psutil not available for system metrics")
            return {"error": "psutil not available"}
        except Exception as e:
            logger.warning(f"System metrics unavailable: {e}")
            return {"error": str(e)}
    
    # Run all checks in parallel for better performance
    try:
        db_result, redis_result, secrets_result, system_metrics = await asyncio.gather(
            check_database_async(),
            check_redis_async(),
            check_secrets_async(),
            get_system_metrics_async(),
            return_exceptions=True
        )
        
        # Process database result
        if isinstance(db_result, Exception):
            health_status["checks"]["database"] = f"error: {str(db_result)}"
            health_status["status"] = "degraded"
        else:
            health_status["checks"]["database"] = db_result["status"]
            if not db_result.get("available", False):
                health_status["status"] = "degraded"
        
        # Process Redis result
        if isinstance(redis_result, Exception):
            health_status["checks"]["redis"] = f"error: {str(redis_result)}"
            health_status["status"] = "degraded"
        else:
            health_status["checks"]["redis"] = redis_result["status"]
            if redis_result["status"].startswith("unhealthy"):
                health_status["status"] = "degraded"
        
        # Process secrets result (don't mark as degraded for fallback)
        if isinstance(secrets_result, Exception):
            health_status["checks"]["secrets"] = f"error: {str(secrets_result)}"
        else:
            health_status["checks"]["secrets"] = secrets_result["status"]
        
        # Process system metrics
        if isinstance(system_metrics, Exception):
            health_status["system"] = {"error": str(system_metrics)}
        else:
            health_status["system"] = system_metrics
            if "error" not in system_metrics:
                # Mark as degraded if resources are high
                if system_metrics.get("cpu_percent", 0) > 90 or system_metrics.get("memory_percent", 0) > 90:
                    health_status["status"] = "degraded"
                if system_metrics.get("disk_percent", 0) > 95:
                    health_status["status"] = "unhealthy"
    except Exception as e:
        logger.error(f"Health check execution error: {e}")
        health_status["status"] = "unhealthy"
        health_status["error"] = str(e)
    
    # Add response time metric
    response_time_ms = round((time.time() - start_time) * 1000, 2)
    response_time_seconds = response_time_ms / 1000.0
    health_status["response_time_ms"] = response_time_ms
    health_status["cached"] = False
    
    # Record Prometheus metrics
    health_status_value = health_status.get("status", "unknown")
    health_check_duration_seconds.labels(endpoint='health', status=health_status_value).observe(response_time_seconds)
    health_check_total.labels(endpoint='health', status=health_status_value).inc()
    
    # Cache the result
    _health_check_cache = health_status.copy()
    _health_check_cache_time = time.time()
    
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
async def health_readiness():
    """Kubernetes readiness probe - returns 200 only if service is ready to handle traffic"""
    from sqlalchemy import text
    from fastapi import HTTPException
    from backend.core.database import get_db
    
    try:
        # Try to get database connection (optional - don't fail if unavailable)
        db_status = "unknown"
        try:
            db = next(get_db())
            # Quick database check with timeout
            import asyncio
            from asyncio import TimeoutError
            
            def check_db_sync():
                try:
                    db.execute(text("SELECT 1"))
                    return True
                except Exception as e:
                    logger.warning(f"Database check failed: {e}")
                    return False
            
            # Wrap in async with timeout
            try:
                db_available = await asyncio.wait_for(asyncio.to_thread(check_db_sync), timeout=2.0)
                db_status = "connected" if db_available else "unavailable"
            except TimeoutError:
                logger.warning("Database check timed out")
                db_status = "timeout"
        except Exception as e:
            logger.warning(f"Could not get database connection: {e}")
            db_status = "unavailable"
        
        # Service is ready - return 200 even if database is unavailable
        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "database": db_status,
            "note": "Service ready to handle traffic" if db_status == "connected" else "Service ready but database not available"
        }
    except Exception as e:
        logger.error(f"Readiness check error: {e}")
        # Return ready even if check fails - service can still handle basic requests
        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "database": "error",
            "note": f"Service ready but database check failed: {str(e)}"
        }


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
from backend.api import auth, auth_2fa, users, subscriptions, signals as signals_api, notifications, admin, webhooks, two_factor, security_dashboard, external_signal_sync, roles, trading
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
app.include_router(trading.router)  # Trading environment status

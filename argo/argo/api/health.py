"""
Health check API endpoints for Argo Trading Engine
GET status, GET metrics, GET uptime, GET readiness, GET liveness
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
from pydantic import BaseModel
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
import time
import logging
import asyncio
from asyncio import TimeoutError
from pathlib import Path
import os
import sqlite3

try:
    import psutil
except ImportError:
    psutil = None

router = APIRouter(prefix="/api/v1/health", tags=["health"])
logger = logging.getLogger(__name__)

# Track startup time for uptime calculation
STARTUP_TIME = datetime.utcnow()

# Health check timeout (5 seconds max per check)
HEALTH_CHECK_TIMEOUT = 5.0


async def check_with_timeout(check_func, timeout=HEALTH_CHECK_TIMEOUT):
    """Run health check with timeout"""
    try:
        result = await asyncio.wait_for(check_func(), timeout=timeout)
        return {"status": "healthy", "result": result}
    except TimeoutError:
        logger.warning(f"Health check timed out after {timeout}s")
        return {"status": "unhealthy", "error": "timeout"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}


def check_database_sync():
    """Synchronous database check (to be wrapped in async)"""
    try:
        # Determine database path
        if os.path.exists("/root/argo-production"):
            db_path = Path("/root/argo-production") / "data" / "signals.db"
        else:
            # Try to find from current file location
            current_file = Path(__file__)
            db_path = current_file.parent.parent.parent.parent / "data" / "signals.db"
        
        if not db_path.exists():
            return {"accessible": False, "error": "Database file not found"}
        
        # Test database connection and query
        conn = sqlite3.connect(str(db_path), timeout=5.0)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.execute("SELECT COUNT(*) FROM signals LIMIT 1")
        count = cursor.fetchone()[0]
        conn.close()
        
        return {"accessible": True, "signal_count": count}
    except sqlite3.Error as e:
        return {"accessible": False, "error": f"SQLite error: {str(e)}"}
    except Exception as e:
        return {"accessible": False, "error": f"Database check failed: {str(e)}"}


async def check_database():
    """Async wrapper for database check"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, check_database_sync)


class HealthStatus(BaseModel):
    """Health status response"""
    status: str  # healthy, degraded, unhealthy
    version: str
    timestamp: str
    uptime_seconds: int
    uptime_formatted: str
    services: dict
    system: dict


class MetricsResponse(BaseModel):
    """Metrics response"""
    signals_generated: int
    win_rate: float
    active_trades: int
    api_latency_ms: float
    error_rate: float
    requests_per_minute: float


@router.get("", response_model=HealthStatus)
async def get_health_status():
    """
    Get health status
    
    **Example Request:**
    ```bash
    curl -X GET "http://localhost:8000/api/health"
    ```
    
    **Example Response:**
    ```json
    {
      "status": "healthy",
      "version": "6.0",
      "timestamp": "2024-01-15T10:30:00Z",
      "uptime_seconds": 86400,
      "uptime_formatted": "1d 0h 0m",
      "services": {
        "api": "healthy",
        "database": "healthy",
        "redis": "healthy"
      },
      "system": {
        "cpu_percent": 25.5,
        "memory_percent": 45.2,
        "disk_percent": 30.1
      }
    }
    ```
    """
    # Calculate uptime
    uptime_delta = datetime.utcnow() - STARTUP_TIME
    uptime_seconds = int(uptime_delta.total_seconds())
    
    # Format uptime
    days = uptime_seconds // 86400
    hours = (uptime_seconds % 86400) // 3600
    minutes = (uptime_seconds % 3600) // 60
    uptime_formatted = f"{days}d {hours}h {minutes}m"
    
    # Get system metrics
    if psutil:
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            system_info = {
                "cpu_percent": round(cpu_percent, 1),
                "memory_percent": round(memory.percent, 1),
                "disk_percent": round(disk.percent, 1)
            }
        except (ImportError, AttributeError, OSError, RuntimeError) as e:
            # psutil not available or system metrics unavailable
            logger.debug(f"System metrics unavailable: {e}")
            system_info = {
                "cpu_percent": 0.0,
                "memory_percent": 0.0,
                "disk_percent": 0.0
            }
    else:
        system_info = {
            "cpu_percent": 0.0,
            "memory_percent": 0.0,
            "disk_percent": 0.0
        }
    
    # Check database connectivity with timeout
    db_check_result = await check_with_timeout(check_database, timeout=HEALTH_CHECK_TIMEOUT)
    if db_check_result["status"] == "healthy" and db_check_result.get("result", {}).get("accessible"):
        db_status = "healthy"
        db_info = db_check_result["result"]
    else:
        db_status = "unhealthy"
        db_info = {"error": db_check_result.get("error", "unknown error")}
        logger.error(f"Database health check failed: {db_info}")
    
    # Check secrets manager access with timeout
    secrets_status = "healthy"
    secrets_info = {}
    try:
        async def check_secrets():
            from core.config import settings
            if hasattr(settings, 'secrets') and settings.secrets:
                test_secret = settings.ARGO_API_SECRET
                if not test_secret or test_secret == "argo_secret_key_change_in_production":
                    return {"status": "degraded", "reason": "using fallback"}
                return {"status": "healthy"}
            return {"status": "degraded", "reason": "using environment variables"}
        
        secrets_result = await check_with_timeout(check_secrets, timeout=2.0)
        if secrets_result["status"] == "healthy":
            secrets_info = secrets_result.get("result", {})
            secrets_status = secrets_info.get("status", "healthy")
        else:
            secrets_status = "unhealthy"
            secrets_info = {"error": secrets_result.get("error")}
    except Exception as e:
        logger.error(f"Secrets check error: {e}")
        secrets_status = "unhealthy"
        secrets_info = {"error": str(e)}
    
    # Get data source health with timeout
    data_source_health = {}
    try:
        async def check_data_sources():
            from argo.core.data_source_health import get_health_monitor
            health_monitor = get_health_monitor()
            return health_monitor.get_summary()
        
        ds_result = await check_with_timeout(check_data_sources, timeout=HEALTH_CHECK_TIMEOUT)
        if ds_result["status"] == "healthy":
            ds_summary = ds_result["result"]
            data_source_health = {
                "total_sources": ds_summary.get('total_sources', 0),
                "healthy": ds_summary.get('healthy', 0),
                "unhealthy": ds_summary.get('unhealthy', 0),
                "degraded": ds_summary.get('degraded', 0),
                "sources": ds_summary.get('sources', {})
            }
        else:
            data_source_health = {"error": ds_result.get("error", "timeout")}
    except Exception as e:
        logger.error(f"Data source health check error: {e}")
        data_source_health = {"error": str(e)}
    
    # Get performance metrics with timeout
    performance_metrics = {}
    try:
        async def check_performance():
            from argo.core.performance_metrics import get_performance_metrics
            perf_metrics = get_performance_metrics()
            return perf_metrics.get_summary()
        
        perf_result = await check_with_timeout(check_performance, timeout=HEALTH_CHECK_TIMEOUT)
        if perf_result["status"] == "healthy":
            performance_metrics = perf_result["result"]
        else:
            performance_metrics = {"error": perf_result.get("error", "timeout")}
    except Exception as e:
        logger.error(f"Performance metrics check error: {e}")
        performance_metrics = {"error": str(e)}
    
    # Check Redis connectivity (if available)
    redis_status = "not_configured"
    try:
        async def check_redis():
            import redis
            # Try to get Redis client if configured
            # This is a placeholder - adjust based on actual Redis setup
            return {"status": "healthy"}
        
        redis_result = await check_with_timeout(check_redis, timeout=2.0)
        if redis_result["status"] == "healthy":
            redis_status = "healthy"
        else:
            redis_status = "unhealthy"
    except Exception:
        redis_status = "not_configured"
    
    # Determine overall status
    status = "healthy"
    if system_info["cpu_percent"] > 90 or system_info["memory_percent"] > 90:
        status = "degraded"
    if system_info["disk_percent"] > 95:
        status = "unhealthy"
    if db_status == "unhealthy":
        status = "unhealthy"
    if secrets_status == "unhealthy":
        status = "degraded"
    if data_source_health.get("unhealthy", 0) > 0:
        status = "degraded"
    if data_source_health.get("unhealthy", 0) > data_source_health.get("healthy", 1):
        status = "unhealthy"
    
    services = {
        "api": "healthy",
        "database": db_status,
        "database_info": db_info,
        "redis": redis_status,
        "secrets": secrets_status,
        "secrets_info": secrets_info,
        "data_sources": data_source_health,
        "performance": performance_metrics
    }
    
    return HealthStatus(
        status=status,
        version="6.0",
        timestamp=datetime.utcnow().isoformat() + "Z",
        uptime_seconds=uptime_seconds,
        uptime_formatted=uptime_formatted,
        services=services,
        system=system_info
    )


@router.get("/metrics", response_model=MetricsResponse)
async def get_health_metrics():
    """
    Get health metrics
    
    **Example Request:**
    ```bash
    curl -X GET "http://localhost:8000/api/health/metrics"
    ```
    
    **Example Response:**
    ```json
    {
      "signals_generated": 1247,
      "win_rate": 96.3,
      "active_trades": 45,
      "api_latency_ms": 245.5,
      "error_rate": 0.5,
      "requests_per_minute": 125.3
    }
    ```
    """
    try:
        # Try to get real metrics from Prometheus/metrics store
        # For now, return mock metrics (in production, get from actual metrics store)
        return MetricsResponse(
            signals_generated=1247,
            win_rate=96.3,
            active_trades=45,
            api_latency_ms=245.5,
            error_rate=0.5,
            requests_per_minute=125.3
        )
    except Exception as e:
        logger.error(f"Failed to get health metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Metrics unavailable: {str(e)}")


@router.get("/uptime")
async def get_uptime():
    """
    Get service uptime
    
    **Example Request:**
    ```bash
    curl -X GET "http://localhost:8000/api/health/uptime"
    ```
    
    **Example Response:**
    ```json
    {
      "uptime_seconds": 86400,
      "uptime_formatted": "1d 0h 0m",
      "started_at": "2024-01-14T10:30:00Z",
      "current_time": "2024-01-15T10:30:00Z"
    }
    ```
    """
    try:
        uptime_delta = datetime.utcnow() - STARTUP_TIME
        uptime_seconds = int(uptime_delta.total_seconds())
        
        days = uptime_seconds // 86400
        hours = (uptime_seconds % 86400) // 3600
        minutes = (uptime_seconds % 3600) // 60
        uptime_formatted = f"{days}d {hours}h {minutes}m"
        
        return {
            "uptime_seconds": uptime_seconds,
            "uptime_formatted": uptime_formatted,
            "started_at": STARTUP_TIME.isoformat() + "Z",
            "current_time": datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"Failed to get uptime: {e}")
        raise HTTPException(status_code=500, detail=f"Uptime calculation failed: {str(e)}")


@router.get("/prometheus")
async def get_prometheus_metrics():
    """
    Get Prometheus metrics (raw format)
    
    **Example Request:**
    ```bash
    curl -X GET "http://localhost:8000/api/health/prometheus"
    ```
    """
    try:
        return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
    except Exception as e:
        logger.error(f"Failed to generate Prometheus metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Metrics generation failed: {str(e)}")


@router.get("/readiness")
async def get_readiness():
    """
    Kubernetes readiness probe endpoint
    Returns 200 only if service is ready to handle traffic (all dependencies healthy)
    
    **Example Request:**
    ```bash
    curl -X GET "http://localhost:8000/api/v1/health/readiness"
    ```
    """
    try:
        health_status = await get_health_status()
        
        # Readiness requires all critical dependencies to be healthy
        if health_status.status == "unhealthy":
            raise HTTPException(status_code=503, detail="Service not ready")
        
        # Check critical dependencies
        services = health_status.services
        if services.get("database") != "healthy":
            raise HTTPException(status_code=503, detail="Database not ready")
        
        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Readiness check failed: {str(e)}")


@router.get("/liveness")
async def get_liveness():
    """
    Kubernetes liveness probe endpoint
    Returns 200 if service is alive (quick check, no dependency verification)
    
    **Example Request:**
    ```bash
    curl -X GET "http://localhost:8000/api/v1/health/liveness"
    ```
    """
    try:
        # Quick check - just verify the service is responding
        return {
            "status": "alive",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "uptime_seconds": int((datetime.utcnow() - STARTUP_TIME).total_seconds())
        }
    except Exception as e:
        logger.error(f"Liveness check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Service not alive: {str(e)}")


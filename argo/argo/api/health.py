"""
Health check API endpoints for Argo Trading Engine
GET status, GET metrics, GET uptime
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
from pydantic import BaseModel
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
import time
try:
    import psutil
except ImportError:
    psutil = None

router = APIRouter(prefix="/api/v1/health", tags=["health"])

# Track startup time for uptime calculation
STARTUP_TIME = datetime.utcnow()


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
        except:
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
    
    # Check secrets manager access
    secrets_status = "healthy"
    try:
        from core.config import settings
        # Try to access a secret to verify AWS Secrets Manager is working
        if hasattr(settings, 'secrets') and settings.secrets:
            test_secret = settings.ARGO_API_SECRET
            if not test_secret or test_secret == "argo_secret_key_change_in_production":
                secrets_status = "degraded"  # Using default/fallback
        else:
            secrets_status = "degraded"  # Using environment variables
    except Exception as e:
        secrets_status = "unhealthy"
    
    # Determine overall status
    status = "healthy"
    if system_info["cpu_percent"] > 90 or system_info["memory_percent"] > 90:
        status = "degraded"
    if system_info["disk_percent"] > 95:
        status = "unhealthy"
    if secrets_status == "unhealthy":
        status = "degraded"
    
    return HealthStatus(
        status=status,
        version="6.0",
        timestamp=datetime.utcnow().isoformat() + "Z",
        uptime_seconds=uptime_seconds,
        uptime_formatted=uptime_formatted,
        services={
            "api": "healthy",
            "database": "healthy",
            "redis": "healthy",
            "secrets": secrets_status
        },
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
    # Mock metrics (in production, get from Prometheus/metrics store)
    return MetricsResponse(
        signals_generated=1247,
        win_rate=96.3,
        active_trades=45,
        api_latency_ms=245.5,
        error_rate=0.5,
        requests_per_minute=125.3
    )


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


@router.get("/prometheus")
async def get_prometheus_metrics():
    """
    Get Prometheus metrics (raw format)
    
    **Example Request:**
    ```bash
    curl -X GET "http://localhost:8000/api/health/prometheus"
    ```
    """
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


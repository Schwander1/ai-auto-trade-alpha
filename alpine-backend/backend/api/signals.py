"""
Signals API endpoints for Alpine Backend
GET subscribed signals, GET history, GET export

Optimizations:
- Persistent HTTP client with connection pooling
- Efficient caching strategy
- Parallel processing where applicable
- Optimized response serialization
- Better error handling and timeout management
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Header, Response, Request
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc
import time
import asyncio
import json
import csv
import io
import atexit
import logging

try:
    import httpx
except ImportError:
    httpx = None

from backend.core.config import settings
from backend.core.database import get_db
from backend.core.cache import cache_response, get_cache, set_cache
from backend.core.cache_constants import (
    CACHE_TTL_SIGNALS,
    CACHE_TTL_SIGNAL_HISTORY,
    CACHE_TTL_SIGNAL_EXPORT
)
from backend.core.response_formatter import add_rate_limit_headers, add_cache_headers, format_datetime_iso
from backend.core.error_responses import create_rate_limit_error
from backend.models.user import User, UserTier
from backend.models.signal import Signal
from backend.core.rate_limit import check_rate_limit, get_rate_limit_status
from backend.api.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/signals", tags=["signals"])

# Rate limiting
RATE_LIMIT_WINDOW = 60
RATE_LIMIT_MAX = 100

# External Signal Provider API URL
EXTERNAL_SIGNAL_API_URL = getattr(settings, 'EXTERNAL_SIGNAL_API_URL', 'http://178.156.194.174:8000')

# OPTIMIZATION: Use centralized HTTP client factory
from backend.core.http_client import SingletonHTTPClient

async def get_http_client() -> Optional[httpx.AsyncClient]:
    """Get or create persistent HTTP client with connection pooling and optimized settings"""
    return await SingletonHTTPClient.get_client()

async def cleanup_http_client() -> None:
    """Cleanup HTTP client on application shutdown"""
    await SingletonHTTPClient.close_client()

def _sync_cleanup() -> None:
    """Synchronous cleanup wrapper for atexit"""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(cleanup_http_client())
        else:
            loop.run_until_complete(cleanup_http_client())
    except (RuntimeError, AttributeError):
        pass

atexit.register(_sync_cleanup)


class SignalResponse(BaseModel):
    """Signal response model"""
    id: str
    symbol: str
    action: str
    entry_price: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    confidence: float
    type: str
    timestamp: str
    hash: str
    reasoning: Optional[str] = None


class PaginatedSignalsResponse(BaseModel):
    """Paginated signals response"""
    items: List[SignalResponse]
    total: int
    limit: int
    offset: int
    has_more: bool
    user_tier: str


class SignalHistoryResponse(BaseModel):
    """Signal history response"""
    signal_id: str
    symbol: str
    action: str
    entry_price: float
    exit_price: Optional[float] = None
    pnl_pct: Optional[float] = None
    status: str
    created_at: str
    closed_at: Optional[str] = None


def get_tier_signal_limit(tier: UserTier) -> int:
    """Get signal limit based on user tier"""
    limits = {
        UserTier.STARTER: 1,
        UserTier.PRO: 10,
        UserTier.ELITE: 999999  # Unlimited
    }
    return limits.get(tier, 1)


async def fetch_signals_from_external_provider(
    limit: int = 10,
    premium_only: bool = False,
    offset: Optional[int] = None
) -> List[Dict[str, Any]]:
    """Fetch signals from external signal provider API with optimized error handling

    Args:
        limit: Maximum number of signals to fetch
        premium_only: Filter premium signals only
        offset: Optional offset for pagination (if supported by external API)

    Returns:
        List of signal dictionaries

    Raises:
        HTTPException: If the external API is unavailable or returns an error
    """
    if not httpx:
        # Fallback to mock data if httpx not available
        logger.warning("httpx not available, returning mock data")
        return [
            {
                "id": f"SIG-{i}",
                "symbol": "AAPL",
                "action": "BUY",
                "entry_price": 175.50,
                "confidence": 97.2,
                "type": "PREMIUM",
                "timestamp": format_datetime_iso(datetime.utcnow()),
                "hash": "abc123"
            }
            for i in range(limit)
        ]

    client = await get_http_client()
    if not client:
        raise HTTPException(
            status_code=503,
            detail="HTTP client not available"
        )

    # Build query parameters
    params: Dict[str, Any] = {"limit": limit}
    if premium_only:
        params["premium_only"] = True
    if offset is not None:
        params["offset"] = offset

    try:
        response = await client.get(
            f"{EXTERNAL_SIGNAL_API_URL}/api/signals/latest",
            params=params
        )
        response.raise_for_status()
        data = response.json()

        # Validate response is a list
        if not isinstance(data, list):
            logger.error(f"Unexpected response format from external API: {type(data)}")
            raise HTTPException(
                status_code=502,
                detail="Invalid response format from external signal provider"
            )

        return data

    except httpx.TimeoutException as e:
        logger.error(f"Timeout fetching signals from external provider: {e}")
        raise HTTPException(
            status_code=504,
            detail="External signal provider timeout. Please try again later."
        )
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error from external provider: {e.response.status_code} - {e.response.text}")
        raise HTTPException(
            status_code=502,
            detail=f"External signal provider returned error: {e.response.status_code}"
        )
    except httpx.RequestError as e:
        logger.error(f"Request error fetching signals: {e}")
        raise HTTPException(
            status_code=503,
            detail="Failed to connect to external signal provider. Please try again later."
        )
    except Exception as e:
        logger.error(f"Unexpected error fetching signals: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while fetching signals."
        )


@router.get("/subscribed", response_model=PaginatedSignalsResponse)
@cache_response(ttl=CACHE_TTL_SIGNALS)  # Cache for 1 minute (signals update frequently)
async def get_subscribed_signals(
    request: Request,
    response: Response,
    limit: int = Query(10, ge=1, le=100, description="Number of signals to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    premium_only: bool = Query(False, description="Filter premium signals only"),
    current_user: User = Depends(get_current_user),
    authorization: Optional[str] = Header(None)
):
    """
    Get subscribed signals based on user tier

    **Example Request:**
    ```bash
    curl -X GET "http://localhost:9001/api/signals/subscribed?limit=10&premium_only=true" \
         -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    ```

    **Example Response:**
    ```json
    {
      "items": [
        {
          "id": "SIG-1234567890",
          "symbol": "AAPL",
          "action": "BUY",
          "entry_price": 175.50,
          "confidence": 97.2,
          "type": "PREMIUM",
          "timestamp": "2024-01-15T10:30:00Z",
          "hash": "abc123..."
        }
      ],
      "total": 45,
      "limit": 10,
      "offset": 0,
      "has_more": true,
      "user_tier": "pro"
    }
    ```
    """
    # Rate limiting and headers
    _apply_rate_limiting(request, response, current_user.email)

    # Check and adjust tier limits
    limit = _adjust_limit_for_tier(limit, current_user.tier)

    # Fetch and cache signals
    cached_signals = await _fetch_and_cache_signals(premium_only, current_user.tier)

    # Paginate and serialize
    items, total = _paginate_and_serialize_signals(cached_signals, offset, limit)

    # Add cache headers
    add_cache_headers(response, max_age=30, public=False)

    return PaginatedSignalsResponse(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
        has_more=(offset + limit) < total,
        user_tier=current_user.tier.value
    )

def _apply_rate_limiting(request: Request, response: Response, client_id: str):
    """Apply rate limiting and add headers"""
    if not check_rate_limit(client_id):
        raise create_rate_limit_error(request=request)

    rate_limit_status = get_rate_limit_status(client_id)
    add_rate_limit_headers(
        response,
        remaining=rate_limit_status["remaining"],
        reset_at=int(time.time()) + rate_limit_status["reset_in"]
    )

def _adjust_limit_for_tier(limit: int, tier: UserTier) -> int:
    """Adjust limit based on user tier"""
    tier_limit = get_tier_signal_limit(tier)
    return min(limit, tier_limit)

async def _fetch_and_cache_signals(premium_only: bool, tier: UserTier) -> List[Dict[str, Any]]:
    """Fetch signals from external provider and cache them"""
    cache_key = f"signals:all:{premium_only}:{tier.value}"
    cached_signals = get_cache(cache_key)

    if cached_signals is None:
        try:
            cached_signals = await fetch_signals_from_external_provider(
                limit=1000,  # Fetch reasonable max for caching
                premium_only=premium_only
            )
            # Cache for configured TTL
            set_cache(cache_key, cached_signals, ttl=CACHE_TTL_SIGNALS)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching signals from external provider: {e}")
            raise HTTPException(
                status_code=503,
                detail="Failed to fetch signals. Please try again later."
            )

    return cached_signals

def _paginate_and_serialize_signals(
    cached_signals: List[Dict[str, Any]],
    offset: int,
    limit: int
) -> tuple[List[SignalResponse], int]:
    """Paginate signals and serialize to response models"""
    total = len(cached_signals)
    start_idx = min(offset, total)
    end_idx = min(offset + limit, total)
    paginated = cached_signals[start_idx:end_idx]

    # Serialize with error handling
    items = []
    for signal in paginated:
        try:
            items.append(SignalResponse(**signal))
        except Exception as e:
            logger.warning(f"Skipping invalid signal: {signal.get('id', 'unknown')}: {e}")

    return items, total


@router.get("/history", response_model=List[SignalHistoryResponse])
@cache_response(ttl=CACHE_TTL_SIGNAL_HISTORY)  # Cache for 5 minutes
async def get_signal_history(
    request: Request,
    response: Response,
    limit: int = Query(50, ge=1, le=500, description="Number of historical signals"),
    days: int = Query(30, ge=1, le=365, description="Number of days to look back"),
    current_user: User = Depends(get_current_user),
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Get signal history for user

    Returns historical signals from the database, ordered by creation date (newest first).
    Note: exit_price, pnl_pct, and closed_at are not yet available in the Signal model
    and will be None. These fields will be populated when trading execution data is integrated.

    **Example Request:**
    ```bash
    curl -X GET "http://localhost:9001/api/signals/history?limit=50&days=30" \
         -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    ```

    **Example Response:**
    ```json
    [
      {
        "signal_id": "SIG-1234567890",
        "symbol": "AAPL",
        "action": "BUY",
        "entry_price": 175.50,
        "exit_price": null,
        "pnl_pct": null,
        "status": "active",
        "created_at": "2024-01-15T10:30:00Z",
        "closed_at": null
      }
    ]
    ```
    """
    # Rate limiting and headers
    _apply_rate_limiting(request, response, current_user.email)
    
    try:
        # Calculate date range and query signals
        start_date = datetime.utcnow() - timedelta(days=days)
        signals = _query_signal_history(db, start_date, limit)
        
        # Map to response format
        history = _map_signals_to_history(signals)
        
        # Add cache headers
        add_cache_headers(response, max_age=60, public=False)
        
        return history
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching signal history: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while fetching signal history. Please try again later."
        )

def _query_signal_history(db: Session, start_date: datetime, limit: int) -> List[Signal]:
    """Query signal history from database"""
    history_limit = min(limit, 500)  # Reasonable limit
    
    return db.query(Signal).filter(
        Signal.created_at >= start_date
    ).order_by(
        desc(Signal.created_at)
    ).limit(history_limit).all()

def _map_signals_to_history(signals: List[Signal]) -> List[SignalHistoryResponse]:
    """Map database signals to history response format"""
    history = []
    for signal in signals:
        created_at_str = format_datetime_iso(signal.created_at)
        status = "active" if signal.is_active else "closed"
        
        history.append(
            SignalHistoryResponse(
                signal_id=f"SIG-{signal.id}",
                symbol=signal.symbol,
                action=signal.action,
                entry_price=signal.price,
                exit_price=None,  # Not available in Signal model yet
                pnl_pct=None,  # Not available in Signal model yet
                status=status,
                created_at=created_at_str,
                closed_at=None  # Not available in Signal model yet
            )
        )
    
    return history


@router.get("/export")
async def export_signals(
    request: Request,
    response: Response,
    format: str = Query("csv", description="Export format: csv, json"),
    days: int = Query(30, ge=1, le=365, description="Number of days to export"),
    current_user: User = Depends(get_current_user),
    authorization: Optional[str] = Header(None)
):
    """
    Export signals to CSV or JSON

    **Example Request:**
    ```bash
    curl -X GET "http://localhost:9001/api/signals/export?format=csv&days=30" \
         -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
         -o signals.csv
    ```
    """
    # Rate limiting
    client_id = current_user.email
    if not check_rate_limit(client_id):
        raise create_rate_limit_error(request=request)

    # Add rate limit headers
    rate_limit_status = get_rate_limit_status(client_id)
    add_rate_limit_headers(
        response,
        remaining=rate_limit_status["remaining"],
        reset_at=int(time.time()) + rate_limit_status["reset_in"]
    )

    # Validate and sanitize format
    export_format = format.lower().strip()
    if export_format not in ["csv", "json"]:
        raise HTTPException(status_code=400, detail="Invalid format. Must be 'csv' or 'json'")

    # OPTIMIZATION: Check cache first for export data
    cache_key = f"signals:export:{export_format}"
    cached_export = get_cache(cache_key)

    if cached_export is None:
    # Fetch signals
    try:
        signals = await fetch_signals_from_external_provider(limit=1000, premium_only=False)
        except HTTPException:
            raise
    except Exception as e:
        logger.error(f"Error fetching signals for export: {e}")
        raise HTTPException(
            status_code=503,
            detail="Failed to fetch signals for export. Please try again later."
        )

        # Generate export content
        if export_format == "csv":
            # OPTIMIZATION: Use list comprehension for CSV generation
        output = io.StringIO()
            fieldnames = ["id", "symbol", "action", "entry_price", "confidence", "timestamp"]
            writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

            # OPTIMIZATION: Batch write rows for better performance
            rows = [
                {
                "id": signal.get("id", ""),
                "symbol": signal.get("symbol", ""),
                "action": signal.get("action", ""),
                "entry_price": signal.get("entry_price", 0),
                "confidence": signal.get("confidence", 0),
                "timestamp": signal.get("timestamp", "")
                }
                for signal in signals
            ]
            writer.writerows(rows)

            cached_export = output.getvalue()
            # Cache CSV for 30 seconds
            set_cache(cache_key, cached_export, ttl=CACHE_TTL_SIGNAL_EXPORT)
    else:
            # OPTIMIZATION: Use orjson if available for faster JSON serialization
            try:
                import orjson
                cached_export = orjson.dumps(signals, option=orjson.OPT_INDENT_2).decode()
            except ImportError:
                cached_export = json.dumps(signals, indent=2, default=str)
            # Cache JSON for 30 seconds
            set_cache(cache_key, cached_export, ttl=CACHE_TTL_SIGNAL_EXPORT)

    # Create response with appropriate content type
    filename = f"signals_{datetime.utcnow().strftime('%Y%m%d')}.{export_format}"
    media_type = "text/csv" if export_format == "csv" else "application/json"

    export_response = Response(
        content=cached_export,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

        # Add rate limit headers
        add_rate_limit_headers(
        export_response,
            remaining=rate_limit_status["remaining"],
            reset_at=int(time.time()) + rate_limit_status["reset_in"]
        )

    return export_response

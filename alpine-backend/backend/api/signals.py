"""
Signals API endpoints for Alpine Backend
GET subscribed signals, GET history, GET export
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Header, Response, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime, timedelta
import time
import re
try:
    import httpx
except ImportError:
    httpx = None
import csv
import io

from backend.core.database import get_db
from backend.core.config import settings
from backend.core.cache import cache_response
from backend.core.input_sanitizer import sanitize_symbol, sanitize_action
from backend.core.response_formatter import add_rate_limit_headers
from backend.models.user import User, UserTier
from backend.core.rate_limit import check_rate_limit, get_rate_limit_status
from backend.api.auth import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/signals", tags=["signals"])

# Rate limiting
RATE_LIMIT_WINDOW = 60
RATE_LIMIT_MAX = 100

# Argo API URL
ARGO_API_URL = getattr(settings, 'ARGO_API_URL', 'http://178.156.194.174:8000')


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


async def fetch_signals_from_argo(limit: int = 10, premium_only: bool = False) -> List[dict]:
    """Fetch signals from Argo API"""
    if not httpx:
        # Fallback to mock data if httpx not available
        return [
            {
                "id": f"SIG-{i}",
                "symbol": "AAPL",
                "action": "BUY",
                "entry_price": 175.50,
                "confidence": 97.2,
                "type": "PREMIUM",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "hash": "abc123"
            }
            for i in range(limit)
        ]
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            params = {"limit": limit}
            if premium_only:
                params["premium_only"] = True
            
            response = await client.get(f"{ARGO_API_URL}/api/signals/latest", params=params)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Failed to fetch signals from Argo: {str(e)}"
        )


@router.get("/subscribed", response_model=PaginatedSignalsResponse)
@cache_response(ttl=60)  # Cache for 1 minute (signals update frequently)
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
    
    # Check tier limits
    tier_limit = get_tier_signal_limit(current_user.tier)
    if limit > tier_limit:
        limit = tier_limit
    
    # Fetch signals from Argo
    try:
        signals = await fetch_signals_from_argo(limit=limit + offset, premium_only=premium_only)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching signals from Argo: {e}")
        raise HTTPException(
            status_code=503,
            detail="Failed to fetch signals. Please try again later."
        )
    
    # Apply pagination
    total = len(signals)
    paginated = signals[offset:offset + limit]
    
    return PaginatedSignalsResponse(
        items=[SignalResponse(**s) for s in paginated],
        total=total,
        limit=limit,
        offset=offset,
        has_more=offset + limit < total,
        user_tier=current_user.tier.value
    )


@router.get("/history", response_model=List[SignalHistoryResponse])
async def get_signal_history(
    request: Request,
    response: Response,
    limit: int = Query(50, ge=1, le=500, description="Number of historical signals"),
    days: int = Query(30, ge=1, le=365, description="Number of days to look back"),
    current_user: User = Depends(get_current_user),
    authorization: Optional[str] = Header(None)
):
    """
    Get signal history for user
    
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
        "exit_price": 184.25,
        "pnl_pct": 4.98,
        "status": "closed",
        "created_at": "2024-01-15T10:30:00Z",
        "closed_at": "2024-01-20T14:30:00Z"
      }
    ]
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
    
    # Mock history data (in production, fetch from database)
    history = []
    start_date = datetime.utcnow() - timedelta(days=days)
    
    for i in range(min(limit, 50)):  # Limit to 50 for demo
        signal_date = start_date + timedelta(days=i * (days / limit))
        history.append(SignalHistoryResponse(
            signal_id=f"SIG-{int(signal_date.timestamp() * 1000)}",
            symbol=["AAPL", "NVDA", "BTC-USD", "ETH-USD"][i % 4],
            action="BUY" if i % 2 == 0 else "SELL",
            entry_price=175.50 + (i * 0.5),
            exit_price=184.25 + (i * 0.5) if i % 3 == 0 else None,
            pnl_pct=4.98 + (i * 0.1) if i % 3 == 0 else None,
            status="closed" if i % 3 == 0 else "active",
            created_at=signal_date.isoformat() + "Z",
            closed_at=(signal_date + timedelta(days=5)).isoformat() + "Z" if i % 3 == 0 else None
        ))
    
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
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    # Add rate limit headers
    rate_limit_status = get_rate_limit_status(client_id)
    add_rate_limit_headers(
        response,
        remaining=rate_limit_status["remaining"],
        reset_at=int(time.time()) + rate_limit_status["reset_in"]
    )
    
    # Validate and sanitize format
    format = format.lower().strip()
    if format not in ["csv", "json"]:
        raise HTTPException(status_code=400, detail="Invalid format. Must be 'csv' or 'json'")
    
    # Fetch signals
    try:
        signals = await fetch_signals_from_argo(limit=1000, premium_only=False)
    except Exception as e:
        logger.error(f"Error fetching signals for export: {e}")
        raise HTTPException(
            status_code=503,
            detail="Failed to fetch signals for export. Please try again later."
        )
    
    if format == "csv":
        # Generate CSV
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=["id", "symbol", "action", "entry_price", "confidence", "timestamp"])
        writer.writeheader()
        for signal in signals:
            writer.writerow({
                "id": signal.get("id", ""),
                "symbol": signal.get("symbol", ""),
                "action": signal.get("action", ""),
                "entry_price": signal.get("entry_price", 0),
                "confidence": signal.get("confidence", 0),
                "timestamp": signal.get("timestamp", "")
            })
        
        csv_response = Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=signals_{datetime.utcnow().strftime('%Y%m%d')}.csv"}
        )
        # Add rate limit headers
        add_rate_limit_headers(
            csv_response,
            remaining=rate_limit_status["remaining"],
            reset_at=int(time.time()) + rate_limit_status["reset_in"]
        )
        return csv_response
    else:
        # Return JSON
        import json as json_lib
        json_response = Response(
            content=json_lib.dumps(signals, indent=2, default=str),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=signals_{datetime.utcnow().strftime('%Y%m%d')}.json"}
        )
        # Add rate limit headers
        add_rate_limit_headers(
            json_response,
            remaining=rate_limit_status["remaining"],
            reset_at=int(time.time()) + rate_limit_status["reset_in"]
        )
        return json_response


"""
Signals API endpoints for Argo Trading Engine
GET all, GET by ID, GET latest, GET stats
"""

from fastapi import APIRouter, HTTPException, Query, Depends, Header, Request, Response
from typing import Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, validator
import hashlib
import json
import hmac
import time
import re
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/signals", tags=["signals"])

# Rate limiting storage (in production, use Redis)
rate_limit_store = {}
RATE_LIMIT_WINDOW = 60  # 1 minute
RATE_LIMIT_MAX = 100

# HMAC authentication for Argo
import os
ARGO_API_SECRET = os.getenv("ARGO_API_SECRET", "argo_secret_key_change_in_production")
if ARGO_API_SECRET == "argo_secret_key_change_in_production":
    import warnings
    warnings.warn("ARGO_API_SECRET is using default value. Set ARGO_API_SECRET environment variable in production!")


class SignalResponse(BaseModel):
    """Signal response model"""
    id: str
    symbol: str
    action: str  # BUY or SELL
    entry_price: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    confidence: float = Field(..., ge=0, le=100)
    type: str  # PREMIUM or STANDARD
    timestamp: str
    hash: str
    regime: Optional[str] = None
    regime_strength: Optional[float] = None
    status: Optional[str] = "active"
    reasoning: Optional[str] = None


class SignalStatsResponse(BaseModel):
    """Signal statistics response"""
    total_signals: int
    active_signals: int
    closed_signals: int
    win_rate: float
    avg_confidence: float
    premium_count: int
    standard_count: int
    total_profit_pct: float
    best_performer: Optional[str] = None
    worst_performer: Optional[str] = None


class PaginatedResponse(BaseModel):
    """Paginated response wrapper"""
    items: List[SignalResponse]
    total: int
    limit: int
    offset: int
    has_more: bool


# Mock signal database (in production, use real database)
SIGNALS_DB = []


def generate_signal_id() -> str:
    """Generate unique signal ID"""
    return f"SIG-{int(time.time() * 1000)}"


def generate_signal_hash(signal: dict) -> str:
    """Generate SHA-256 hash for signal verification"""
    signal_str = json.dumps(signal, sort_keys=True)
    return hashlib.sha256(signal_str.encode()).hexdigest()


def verify_hmac(authorization: Optional[str] = Header(None)) -> bool:
    """Verify HMAC authentication"""
    if not authorization:
        return False
    try:
        # Format: HMAC timestamp:signature
        parts = authorization.split(":")
        if len(parts) != 2:
            return False
        timestamp, signature = parts
        # Check timestamp is within 5 minutes
        if abs(time.time() - int(timestamp)) > 300:
            return False
        # Verify signature
        expected = hmac.new(
            ARGO_API_SECRET.encode(),
            timestamp.encode(),
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected, signature)
    except:
        return False


def check_rate_limit(client_id: str = "default") -> bool:
    """Check rate limit (100 req/min)"""
    now = time.time()
    if client_id not in rate_limit_store:
        rate_limit_store[client_id] = []
    
    # Remove old requests outside window
    rate_limit_store[client_id] = [
        req_time for req_time in rate_limit_store[client_id]
        if now - req_time < RATE_LIMIT_WINDOW
    ]
    
    # Check limit
    if len(rate_limit_store[client_id]) >= RATE_LIMIT_MAX:
        return False
    
    # Add current request
    rate_limit_store[client_id].append(now)
    return True


@router.get("", response_model=PaginatedResponse)
async def get_all_signals(
    request: Request,
    response: Response,
    limit: int = Query(10, ge=1, le=100, description="Number of signals to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    premium_only: bool = Query(False, description="Filter premium signals only"),
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    action: Optional[str] = Query(None, description="Filter by action (BUY/SELL)"),
    authorization: Optional[str] = Header(None)
):
    """
    Get all signals with pagination and filtering
    
    **Example Request:**
    ```bash
    curl -X GET "http://localhost:8000/api/signals?limit=10&offset=0&premium_only=true" \
         -H "Authorization: HMAC 1234567890:signature"
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
          "stop_loss": 171.00,
          "take_profit": 184.25,
          "confidence": 97.2,
          "type": "PREMIUM",
          "timestamp": "2024-01-15T10:30:00Z",
          "hash": "abc123...",
          "status": "active"
        }
      ],
      "total": 100,
      "limit": 10,
      "offset": 0,
      "has_more": true
    }
    ```
    """
    # Rate limiting
    client_id = request.client.host if request.client else "anonymous"
    if not check_rate_limit(client_id):
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Maximum {RATE_LIMIT_MAX} requests per minute."
        )
    
    # Input sanitization
    try:
        if symbol:
            # Sanitize symbol (uppercase, alphanumeric and hyphens only)
            symbol = symbol.upper().strip()
            if not re.match(r'^[A-Z0-9_-]+$', symbol) or len(symbol) > 20:
                raise HTTPException(status_code=400, detail="Invalid symbol format")
        
        if action:
            # Sanitize action (BUY or SELL only)
            action = action.upper().strip()
            if action not in ["BUY", "SELL"]:
                raise HTTPException(status_code=400, detail="Invalid action. Must be BUY or SELL")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Input sanitization error: {e}")
        raise HTTPException(status_code=400, detail="Invalid input parameters")
    
    # Filter signals
    filtered = SIGNALS_DB.copy()
    
    if premium_only:
        filtered = [s for s in filtered if s.get("confidence", 0) >= 95]
    
    if symbol:
        filtered = [s for s in filtered if s.get("symbol") == symbol]
    
    if action:
        filtered = [s for s in filtered if s.get("action") == action]
    
    # Paginate
    total = len(filtered)
    paginated = filtered[offset:offset + limit]
    
    # Add rate limit headers
    remaining = max(0, RATE_LIMIT_MAX - len(rate_limit_store.get(client_id, [])))
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Limit"] = str(RATE_LIMIT_MAX)
    
    return PaginatedResponse(
        items=[SignalResponse(**s) for s in paginated],
        total=total,
        limit=limit,
        offset=offset,
        has_more=offset + limit < total
    )


@router.get("/{signal_id}", response_model=SignalResponse)
async def get_signal_by_id(
    request: Request,
    response: Response,
    signal_id: str,
    authorization: Optional[str] = Header(None)
):
    """
    Get signal by ID
    
    **Example Request:**
    ```bash
    curl -X GET "http://localhost:8000/api/signals/SIG-1234567890" \
         -H "Authorization: HMAC 1234567890:signature"
    ```
    
    **Example Response:**
    ```json
    {
      "id": "SIG-1234567890",
      "symbol": "AAPL",
      "action": "BUY",
      "entry_price": 175.50,
      "stop_loss": 171.00,
      "take_profit": 184.25,
      "confidence": 97.2,
      "type": "PREMIUM",
      "timestamp": "2024-01-15T10:30:00Z",
      "hash": "abc123...",
      "status": "active"
    }
    ```
    """
    # Rate limiting
    client_id = request.client.host if request.client else "anonymous"
    if not check_rate_limit(client_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    # Input sanitization - validate signal_id format
    if not signal_id or len(signal_id) > 100:
        raise HTTPException(status_code=400, detail="Invalid signal ID format")
    
    # Sanitize signal_id (alphanumeric, hyphens, underscores only)
    if not re.match(r'^[A-Za-z0-9_-]+$', signal_id):
        raise HTTPException(status_code=400, detail="Invalid signal ID format")
    
    # Find signal
    signal = next((s for s in SIGNALS_DB if s.get("id") == signal_id), None)
    
    if not signal:
        raise HTTPException(status_code=404, detail=f"Signal {signal_id} not found")
    
    # Add rate limit headers
    remaining = max(0, RATE_LIMIT_MAX - len(rate_limit_store.get(client_id, [])))
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Limit"] = str(RATE_LIMIT_MAX)
    
    return SignalResponse(**signal)


@router.get("/latest", response_model=List[SignalResponse])
async def get_latest_signals(
    request: Request,
    response: Response,
    limit: int = Query(10, ge=1, le=100, description="Number of latest signals"),
    premium_only: bool = Query(False, description="Filter premium signals only"),
    authorization: Optional[str] = Header(None)
):
    """
    Get latest signals (returns array directly for frontend compatibility)
    
    **Example Request:**
    ```bash
    curl -X GET "http://localhost:8000/api/signals/latest?limit=5&premium_only=true"
    ```
    
    **Example Response:**
    ```json
    [
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
    ]
    ```
    """
    # Rate limiting
    client_id = request.client.host if request.client else "anonymous"
    if not check_rate_limit(client_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    # Get latest signals
    filtered = SIGNALS_DB.copy()
    
    if premium_only:
        filtered = [s for s in filtered if s.get("confidence", 0) >= 95]
    
    # Sort by timestamp (newest first)
    filtered.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    
    # Limit
    limited = filtered[:limit]
    
    # Add rate limit headers
    remaining = max(0, RATE_LIMIT_MAX - len(rate_limit_store.get(client_id, [])))
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Limit"] = str(RATE_LIMIT_MAX)
    
    return [SignalResponse(**s) for s in limited]


@router.get("/stats", response_model=SignalStatsResponse)
async def get_signal_stats(
    request: Request,
    response: Response,
    authorization: Optional[str] = Header(None)
):
    """
    Get signal statistics
    
    **Example Request:**
    ```bash
    curl -X GET "http://localhost:8000/api/signals/stats" \
         -H "Authorization: HMAC 1234567890:signature"
    ```
    
    **Example Response:**
    ```json
    {
      "total_signals": 1247,
      "active_signals": 45,
      "closed_signals": 1202,
      "win_rate": 96.3,
      "avg_confidence": 94.7,
      "premium_count": 623,
      "standard_count": 624,
      "total_profit_pct": 1245.8,
      "best_performer": "NVDA",
      "worst_performer": "TSLA"
    }
    ```
    """
    # Rate limiting
    client_id = request.client.host if request.client else "anonymous"
    if not check_rate_limit(client_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    # Calculate stats
    total = len(SIGNALS_DB)
    active = len([s for s in SIGNALS_DB if s.get("status") == "active"])
    closed = len([s for s in SIGNALS_DB if s.get("status") == "closed"])
    premium = len([s for s in SIGNALS_DB if s.get("confidence", 0) >= 95])
    standard = total - premium
    
    # Calculate win rate (mock data)
    win_rate = 96.3 if total > 0 else 0.0
    avg_confidence = sum(s.get("confidence", 0) for s in SIGNALS_DB) / total if total > 0 else 0.0
    
    # Add rate limit headers
    remaining = max(0, RATE_LIMIT_MAX - len(rate_limit_store.get(client_id, [])))
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Limit"] = str(RATE_LIMIT_MAX)
    
    return SignalStatsResponse(
        total_signals=total,
        active_signals=active,
        closed_signals=closed,
        win_rate=win_rate,
        avg_confidence=round(avg_confidence, 2),
        premium_count=premium,
        standard_count=standard,
        total_profit_pct=1245.8,  # Mock data
        best_performer="NVDA",
        worst_performer="TSLA"
    )


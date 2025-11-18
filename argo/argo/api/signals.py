"""
Signals API endpoints for Argo Trading Engine
GET all, GET by ID, GET latest, GET stats
"""

from fastapi import APIRouter, HTTPException, Query, Depends, Header, Request, Response
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, validator
import hashlib
import json
import hmac
import time
import re
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/signals", tags=["signals"])

# Use Redis-based rate limiting from core
try:
    from argo.core.rate_limit import check_rate_limit, add_rate_limit_headers, get_rate_limit_status
except ImportError:
    # Fallback if running from argo directory
    from core.rate_limit import check_rate_limit, add_rate_limit_headers, get_rate_limit_status
RATE_LIMIT_WINDOW = 60  # 1 minute
RATE_LIMIT_MAX = 100

# HMAC authentication for Argo
import os
from argo.core.environment import detect_environment

ARGO_API_SECRET = os.getenv("ARGO_API_SECRET", "argo_secret_key_change_in_production")

# SECURITY: Fail fast if default secret is used in production
if ARGO_API_SECRET == "argo_secret_key_change_in_production":
    env = detect_environment()
    if env == "production":
        raise ValueError(
            "CRITICAL SECURITY ERROR: ARGO_API_SECRET is using default value in production! "
            "Set ARGO_API_SECRET environment variable or configure in AWS Secrets Manager."
        )
    else:
        import warnings
        warnings.warn(
            "ARGO_API_SECRET is using default value. "
            "Set ARGO_API_SECRET environment variable before deploying to production!",
            UserWarning
        )


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
    except (ValueError, TypeError, AttributeError, KeyError) as e:
        # Invalid signature format or missing data
        logger.debug(f"Signature verification failed: {e}")
        return False


# Rate limiting now handled by argo.core.rate_limit module


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
    client_id = _get_client_id(request)
    _check_rate_limit(client_id)
    
    # Input sanitization
    sanitized_params = _sanitize_input_params(symbol, action)
    
    # Filter signals
    filtered_signals = _filter_signals(sanitized_params, premium_only)
    
    # Paginate
    paginated_result = _paginate_signals(filtered_signals, limit, offset)
    
    # Add rate limit headers
    _add_rate_limit_headers(response, client_id)
    
    return paginated_result


def _get_client_id(request: Request) -> str:
    """Extract client ID from request"""
    return request.client.host if request.client else "anonymous"


def _check_rate_limit(client_id: str):
    """Check and enforce rate limiting"""
    if not check_rate_limit(client_id, RATE_LIMIT_MAX, RATE_LIMIT_WINDOW):
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Maximum {RATE_LIMIT_MAX} requests per minute."
        )


def _sanitize_input_params(symbol: Optional[str], action: Optional[str]) -> Dict:
    """Sanitize and validate input parameters"""
    sanitized = {}
    
    if symbol:
        symbol = symbol.upper().strip()
        if not re.match(r'^[A-Z0-9_-]+$', symbol) or len(symbol) > 20:
            raise HTTPException(status_code=400, detail="Invalid symbol format")
        sanitized['symbol'] = symbol
    
    if action:
        action = action.upper().strip()
        if action not in ["BUY", "SELL"]:
            raise HTTPException(status_code=400, detail="Invalid action. Must be BUY or SELL")
        sanitized['action'] = action
    
    return sanitized


def _filter_signals(sanitized_params: Dict, premium_only: bool) -> List:
    """Filter signals based on criteria"""
    filtered = SIGNALS_DB.copy()
    
    if premium_only:
        filtered = [s for s in filtered if s.get("confidence", 0) >= 95]
    
    if sanitized_params.get('symbol'):
        filtered = [s for s in filtered if s.get("symbol") == sanitized_params['symbol']]
    
    if sanitized_params.get('action'):
        filtered = [s for s in filtered if s.get("action") == sanitized_params['action']]
    
    return filtered


def _paginate_signals(filtered_signals: List, limit: int, offset: int) -> PaginatedResponse:
    """Paginate filtered signals"""
    total = len(filtered_signals)
    paginated = filtered_signals[offset:offset + limit]
    
    return PaginatedResponse(
        items=[SignalResponse(**s) for s in paginated],
        total=total,
        limit=limit,
        offset=offset,
        has_more=offset + limit < total
    )


def _add_rate_limit_headers(response: Response, client_id: str):
    """Add rate limit headers to response"""
    # Note: rate_limit_store may not be available if using Redis-based rate limiting
    # This is a fallback for when rate_limit_store is not available
    try:
        from argo.core.rate_limit import get_rate_limit_status
        status = get_rate_limit_status(client_id, RATE_LIMIT_MAX, RATE_LIMIT_WINDOW)
        remaining = status.get('remaining', RATE_LIMIT_MAX)
    except (ImportError, AttributeError):
        # Fallback if rate limit status is not available
        remaining = RATE_LIMIT_MAX
    
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Limit"] = str(RATE_LIMIT_MAX)


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
    if not check_rate_limit(client_id, RATE_LIMIT_MAX, RATE_LIMIT_WINDOW):
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
    try:
        from argo.core.rate_limit import get_rate_limit_status
        rate_status = get_rate_limit_status(client_id)
        remaining = rate_status.get('remaining', RATE_LIMIT_MAX)
    except (ImportError, AttributeError):
        # Fallback if rate limit module doesn't have get_rate_limit_status
        remaining = RATE_LIMIT_MAX
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
    if not check_rate_limit(client_id, RATE_LIMIT_MAX, RATE_LIMIT_WINDOW):
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
    try:
        from argo.core.rate_limit import get_rate_limit_status
        rate_status = get_rate_limit_status(client_id)
        remaining = rate_status.get('remaining', RATE_LIMIT_MAX)
    except (ImportError, AttributeError):
        # Fallback if rate limit module doesn't have get_rate_limit_status
        remaining = RATE_LIMIT_MAX
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
    Get signal statistics from database
    
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
      "win_rate": 45.2,
      "avg_confidence": 89.5,
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
    if not check_rate_limit(client_id, RATE_LIMIT_MAX, RATE_LIMIT_WINDOW):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    # Query real database
    try:
        from pathlib import Path
        import sqlite3
        
        # Get database path
        if os.path.exists("/root/argo-production"):
            db_path = Path("/root/argo-production") / "data" / "signals.db"
        else:
            db_path = Path(__file__).parent.parent.parent / "data" / "signals.db"
        
        if not db_path.exists():
            logger.warning(f"Database not found: {db_path}, returning empty stats")
            return SignalStatsResponse(
                total_signals=0,
                active_signals=0,
                closed_signals=0,
                win_rate=0.0,
                avg_confidence=0.0,
                premium_count=0,
                standard_count=0,
                total_profit_pct=0.0,
                best_performer=None,
                worst_performer=None
            )
        
        conn = sqlite3.connect(str(db_path), timeout=10.0)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get total signals
        cursor.execute("SELECT COUNT(*) as total FROM signals")
        total = cursor.fetchone()['total']
        
        # Get active/closed signals (based on outcome)
        cursor.execute("""
            SELECT 
                COUNT(CASE WHEN outcome IS NULL THEN 1 END) as active,
                COUNT(CASE WHEN outcome IS NOT NULL THEN 1 END) as closed
            FROM signals
        """)
        status_row = cursor.fetchone()
        active = status_row['active'] if status_row else 0
        closed = status_row['closed'] if status_row else 0
        
        # Get confidence stats
        cursor.execute("""
            SELECT 
                AVG(confidence) as avg_confidence,
                COUNT(CASE WHEN confidence >= 95 THEN 1 END) as premium,
                COUNT(CASE WHEN confidence < 95 THEN 1 END) as standard
            FROM signals
        """)
        conf_row = cursor.fetchone()
        avg_confidence = conf_row['avg_confidence'] if conf_row and conf_row['avg_confidence'] else 0.0
        premium = conf_row['premium'] if conf_row else 0
        standard = conf_row['standard'] if conf_row else 0
        
        # Calculate win rate from completed trades
        cursor.execute("""
            SELECT 
                COUNT(*) as total_completed,
                COUNT(CASE WHEN outcome = 'win' THEN 1 END) as wins
            FROM signals
            WHERE outcome IS NOT NULL
        """)
        win_row = cursor.fetchone()
        total_completed = win_row['total_completed'] if win_row else 0
        wins = win_row['wins'] if win_row else 0
        win_rate = (wins / total_completed * 100) if total_completed > 0 else 0.0
        
        # Get total profit
        cursor.execute("""
            SELECT SUM(profit_loss_pct) as total_profit
            FROM signals
            WHERE profit_loss_pct IS NOT NULL
        """)
        profit_row = cursor.fetchone()
        total_profit_pct = profit_row['total_profit'] if profit_row and profit_row['total_profit'] else 0.0
        
        # Get best and worst performers
        cursor.execute("""
            SELECT 
                symbol,
                AVG(profit_loss_pct) as avg_pnl,
                COUNT(*) as trade_count
            FROM signals
            WHERE profit_loss_pct IS NOT NULL
            GROUP BY symbol
            HAVING trade_count >= 5
            ORDER BY avg_pnl DESC
            LIMIT 1
        """)
        best_row = cursor.fetchone()
        best_performer = best_row['symbol'] if best_row else None
        
        cursor.execute("""
            SELECT 
                symbol,
                AVG(profit_loss_pct) as avg_pnl,
                COUNT(*) as trade_count
            FROM signals
            WHERE profit_loss_pct IS NOT NULL
            GROUP BY symbol
            HAVING trade_count >= 5
            ORDER BY avg_pnl ASC
            LIMIT 1
        """)
        worst_row = cursor.fetchone()
        worst_performer = worst_row['symbol'] if worst_row else None
        
        conn.close()
        
    except Exception as e:
        logger.error(f"Error querying signal stats from database: {e}", exc_info=True)
        # Return empty stats on error
        return SignalStatsResponse(
            total_signals=0,
            active_signals=0,
            closed_signals=0,
            win_rate=0.0,
            avg_confidence=0.0,
            premium_count=0,
            standard_count=0,
            total_profit_pct=0.0,
            best_performer=None,
            worst_performer=None
        )
    
    # Add rate limit headers
    remaining = max(0, RATE_LIMIT_MAX - len(rate_limit_store.get(client_id, [])))
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Limit"] = str(RATE_LIMIT_MAX)
    
    return SignalStatsResponse(
        total_signals=total,
        active_signals=active,
        closed_signals=closed,
        win_rate=round(win_rate, 2),
        avg_confidence=round(avg_confidence, 2),
        premium_count=premium,
        standard_count=standard,
        total_profit_pct=round(total_profit_pct, 2),
        best_performer=best_performer,
        worst_performer=worst_performer
    )


"""
Trading status API endpoints for Alpine Backend
Proxies trading environment and account status from Argo API

Optimizations:
- Reuses shared HTTP client from signals.py for connection pooling
- Efficient caching strategy
- Better error handling and timeout management
"""
from fastapi import APIRouter, HTTPException, Depends, Header, Response, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import logging
import time

from backend.core.database import get_db
from backend.core.config import settings
from backend.core.cache import cache_response
from backend.core.cache_constants import CACHE_TTL_TRADING_STATUS
from backend.core.response_formatter import add_rate_limit_headers, add_cache_headers
from backend.core.error_responses import create_rate_limit_error
from backend.core.rate_limit import check_rate_limit, get_rate_limit_status
from backend.api.auth import get_current_user
from backend.api.signals import get_http_client  # Reuse shared HTTP client
from backend.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/trading", tags=["trading"])

# Rate limiting
RATE_LIMIT_WINDOW = 60
RATE_LIMIT_MAX = 30  # Lower limit for trading status endpoint

# External Signal Provider API URL
EXTERNAL_SIGNAL_API_URL = getattr(settings, 'EXTERNAL_SIGNAL_API_URL', 'http://178.156.194.174:8000')
EXTERNAL_SIGNAL_API_KEY = getattr(settings, 'EXTERNAL_SIGNAL_API_KEY', '')


class TradingStatusResponse(BaseModel):
    """Trading status response model"""
    environment: str
    trading_mode: str
    account_name: Optional[str] = None
    account_number: Optional[str] = None
    portfolio_value: Optional[float] = None
    buying_power: Optional[float] = None
    prop_firm_enabled: bool = False
    alpaca_connected: bool = False
    account_status: Optional[str] = None


@router.get("/status", response_model=TradingStatusResponse)
@cache_response(ttl=CACHE_TTL_TRADING_STATUS)  # Cache for 30 seconds (trading status changes infrequently)
async def get_trading_status(
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_user),
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Get trading environment and account status from Argo API

    This endpoint proxies the trading status from the Argo Trading Engine,
    providing information about:
    - Current environment (development/production)
    - Trading mode (dev/production/prop_firm/simulation)
    - Account details (if connected)
    - Prop firm mode status

    **Authentication Required:** Yes

    **Example Request:**
    ```bash
    curl -X GET "http://localhost:8001/api/v1/trading/status" \
         -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    ```

    **Example Response:**
    ```json
    {
      "environment": "production",
      "trading_mode": "prop_firm",
      "account_name": "Prop Firm Test Account",
      "account_number": "ABC123",
      "portfolio_value": 100000.00,
      "buying_power": 100000.00,
      "prop_firm_enabled": true,
      "alpaca_connected": true,
      "account_status": "ACTIVE"
    }
    ```
    """
    # Rate limiting
    client_id = current_user.email
    if not check_rate_limit(client_id, window=RATE_LIMIT_WINDOW, max_requests=RATE_LIMIT_MAX):
        raise create_rate_limit_error(request=request)

    # Add rate limit headers
    rate_limit_status = get_rate_limit_status(client_id, window=RATE_LIMIT_WINDOW, max_requests=RATE_LIMIT_MAX)
    add_rate_limit_headers(
        response,
        remaining=rate_limit_status["remaining"],
        reset_at=int(time.time()) + rate_limit_status["reset_in"]
    )

    # OPTIMIZATION: Use shared HTTP client for connection pooling
    try:
        import httpx
    except ImportError:
        raise HTTPException(
            status_code=503,
            detail="HTTP client not available"
    )

    # Query Argo API for trading status
    try:
        argo_url = f"{EXTERNAL_SIGNAL_API_URL}/api/v1/trading/status"
        headers = {}

        # Add API key if configured
        if EXTERNAL_SIGNAL_API_KEY:
            headers["X-API-Key"] = EXTERNAL_SIGNAL_API_KEY

        # OPTIMIZATION: Reuse shared HTTP client instead of creating new one
        client = await get_http_client()
        if not client:
            raise HTTPException(
                status_code=503,
                detail="HTTP client not available"
            )

        argo_response = await client.get(argo_url, headers=headers, timeout=10.0)
        argo_response.raise_for_status()
        trading_data = argo_response.json()

        # Add cache headers for client-side caching
        add_cache_headers(response, max_age=30, public=False)  # Cache for 30 seconds

        # Return the trading status
        return TradingStatusResponse(
            environment=trading_data.get("environment", "unknown"),
            trading_mode=trading_data.get("trading_mode", "simulation"),
            account_name=trading_data.get("account_name"),
            account_number=trading_data.get("account_number"),
            portfolio_value=trading_data.get("portfolio_value"),
            buying_power=trading_data.get("buying_power"),
            prop_firm_enabled=trading_data.get("prop_firm_enabled", False),
            alpaca_connected=trading_data.get("alpaca_connected", False),
            account_status=trading_data.get("account_status")
        )

    except httpx.TimeoutException:
        logger.error("Timeout querying Argo API for trading status")
        raise HTTPException(
            status_code=504,
            detail="Trading status service unavailable (timeout). Please try again later."
        )
    except httpx.HTTPStatusError as e:
        logger.error(f"Argo API returned error: {e.response.status_code} - {e.response.text}")
        raise HTTPException(
            status_code=502,
            detail=f"Trading status service returned error: {e.response.status_code}"
        )
    except httpx.RequestError as e:
        logger.error(f"Failed to connect to Argo API: {e}")
        raise HTTPException(
            status_code=503,
            detail="Trading status service unavailable (connection error). Please try again later."
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting trading status: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while getting trading status."
        )

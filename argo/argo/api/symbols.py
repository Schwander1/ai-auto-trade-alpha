"""
Symbols API endpoints for Argo Trading Engine
GET available symbols, GET data for symbol
"""

from fastapi import APIRouter, HTTPException, Query, Header
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import time

router = APIRouter(prefix="/api/symbols", tags=["symbols"])

# Rate limiting
rate_limit_store = {}
RATE_LIMIT_WINDOW = 60
RATE_LIMIT_MAX = 100


class SymbolInfo(BaseModel):
    """Symbol information"""
    symbol: str
    name: str
    type: str  # stock, crypto, forex, commodity
    exchange: Optional[str] = None
    currency: str
    is_active: bool
    min_trade_size: Optional[float] = None
    price_precision: int = 2


class SymbolData(BaseModel):
    """Symbol price data"""
    symbol: str
    current_price: float
    change_24h: float
    change_24h_pct: float
    volume_24h: Optional[float] = None
    high_24h: Optional[float] = None
    low_24h: Optional[float] = None
    timestamp: str


class SymbolHistoryPoint(BaseModel):
    """Historical price point"""
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: Optional[float] = None


class SymbolHistoryResponse(BaseModel):
    """Symbol history response"""
    symbol: str
    timeframe: str
    points: List[SymbolHistoryPoint]
    total_points: int


# Mock symbol database
AVAILABLE_SYMBOLS = {
    "AAPL": {"name": "Apple Inc.", "type": "stock", "exchange": "NASDAQ", "currency": "USD"},
    "NVDA": {"name": "NVIDIA Corporation", "type": "stock", "exchange": "NASDAQ", "currency": "USD"},
    "TSLA": {"name": "Tesla Inc.", "type": "stock", "exchange": "NASDAQ", "currency": "USD"},
    "MSFT": {"name": "Microsoft Corporation", "type": "stock", "exchange": "NASDAQ", "currency": "USD"},
    "GOOGL": {"name": "Alphabet Inc.", "type": "stock", "exchange": "NASDAQ", "currency": "USD"},
    "BTC-USD": {"name": "Bitcoin", "type": "crypto", "exchange": "Crypto", "currency": "USD"},
    "ETH-USD": {"name": "Ethereum", "type": "crypto", "exchange": "Crypto", "currency": "USD"},
    "SOL-USD": {"name": "Solana", "type": "crypto", "exchange": "Crypto", "currency": "USD"},
}

# Mock price data
PRICE_DATA = {
    "AAPL": 175.50,
    "NVDA": 495.10,
    "TSLA": 242.30,
    "MSFT": 378.20,
    "GOOGL": 142.80,
    "BTC-USD": 67500,
    "ETH-USD": 3250,
    "SOL-USD": 145.20,
}


def check_rate_limit(client_id: str = "default") -> bool:
    """Check rate limit"""
    now = time.time()
    if client_id not in rate_limit_store:
        rate_limit_store[client_id] = []
    
    rate_limit_store[client_id] = [
        req_time for req_time in rate_limit_store[client_id]
        if now - req_time < RATE_LIMIT_WINDOW
    ]
    
    if len(rate_limit_store[client_id]) >= RATE_LIMIT_MAX:
        return False
    
    rate_limit_store[client_id].append(now)
    return True


@router.get("", response_model=List[SymbolInfo])
async def get_available_symbols(
    type: Optional[str] = Query(None, description="Filter by type: stock, crypto, forex, commodity"),
    exchange: Optional[str] = Query(None, description="Filter by exchange"),
    authorization: Optional[str] = Header(None)
):
    """
    Get all available symbols
    
    **Example Request:**
    ```bash
    curl -X GET "http://localhost:8000/api/symbols?type=crypto" \
         -H "Authorization: HMAC 1234567890:signature"
    ```
    
    **Example Response:**
    ```json
    [
      {
        "symbol": "BTC-USD",
        "name": "Bitcoin",
        "type": "crypto",
        "exchange": "Crypto",
        "currency": "USD",
        "is_active": true,
        "price_precision": 2
      }
    ]
    ```
    """
    # Rate limiting
    client_id = authorization or "anonymous"
    if not check_rate_limit(client_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    # Filter symbols
    symbols = []
    for symbol, info in AVAILABLE_SYMBOLS.items():
        if type and info["type"] != type:
            continue
        if exchange and info.get("exchange") != exchange:
            continue
        
        symbols.append(SymbolInfo(
            symbol=symbol,
            name=info["name"],
            type=info["type"],
            exchange=info.get("exchange"),
            currency=info.get("currency", "USD"),
            is_active=True,
            price_precision=2
        ))
    
    return symbols


@router.get("/{symbol}", response_model=SymbolData)
async def get_symbol_data(
    symbol: str,
    authorization: Optional[str] = Header(None)
):
    """
    Get current data for a symbol
    
    **Example Request:**
    ```bash
    curl -X GET "http://localhost:8000/api/symbols/AAPL" \
         -H "Authorization: HMAC 1234567890:signature"
    ```
    
    **Example Response:**
    ```json
    {
      "symbol": "AAPL",
      "current_price": 175.50,
      "change_24h": 2.30,
      "change_24h_pct": 1.33,
      "volume_24h": 45234567,
      "high_24h": 176.20,
      "low_24h": 173.10,
      "timestamp": "2024-01-15T10:30:00Z"
    }
    ```
    """
    # Rate limiting
    client_id = authorization or "anonymous"
    if not check_rate_limit(client_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    # Check if symbol exists
    if symbol.upper() not in AVAILABLE_SYMBOLS:
        raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")
    
    symbol_upper = symbol.upper()
    current_price = PRICE_DATA.get(symbol_upper, 0)
    
    # Mock 24h change
    change_24h = current_price * 0.0133  # 1.33% change
    change_24h_pct = 1.33
    
    return SymbolData(
        symbol=symbol_upper,
        current_price=current_price,
        change_24h=round(change_24h, 2),
        change_24h_pct=round(change_24h_pct, 2),
        volume_24h=45234567.0,
        high_24h=round(current_price * 1.004, 2),
        low_24h=round(current_price * 0.986, 2),
        timestamp=datetime.utcnow().isoformat() + "Z"
    )


@router.get("/{symbol}/history", response_model=SymbolHistoryResponse)
async def get_symbol_history(
    symbol: str,
    timeframe: str = Query("1d", description="Timeframe: 1h, 4h, 1d, 1w, 1m"),
    limit: int = Query(100, ge=1, le=1000, description="Number of data points"),
    authorization: Optional[str] = Header(None)
):
    """
    Get historical price data for a symbol
    
    **Example Request:**
    ```bash
    curl -X GET "http://localhost:8000/api/symbols/AAPL/history?timeframe=1d&limit=30" \
         -H "Authorization: HMAC 1234567890:signature"
    ```
    
    **Example Response:**
    ```json
    {
      "symbol": "AAPL",
      "timeframe": "1d",
      "points": [
        {
          "timestamp": "2024-01-15T00:00:00Z",
          "open": 174.20,
          "high": 176.50,
          "low": 173.80,
          "close": 175.50,
          "volume": 45234567
        }
      ],
      "total_points": 30
    }
    ```
    """
    # Rate limiting
    client_id = authorization or "anonymous"
    if not check_rate_limit(client_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    # Check if symbol exists
    if symbol.upper() not in AVAILABLE_SYMBOLS:
        raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")
    
    # Validate timeframe
    valid_timeframes = ["1h", "4h", "1d", "1w", "1m"]
    if timeframe not in valid_timeframes:
        raise HTTPException(status_code=400, detail=f"Invalid timeframe. Must be one of: {', '.join(valid_timeframes)}")
    
    symbol_upper = symbol.upper()
    base_price = PRICE_DATA.get(symbol_upper, 100)
    
    # Generate historical data points
    points = []
    timeframe_hours = {"1h": 1, "4h": 4, "1d": 24, "1w": 168, "1m": 720}
    hours = timeframe_hours.get(timeframe, 24)
    
    for i in range(limit):
        timestamp = datetime.utcnow() - timedelta(hours=hours * (limit - i))
        # Simulate price movement
        price_variation = (i % 10 - 5) * 0.01
        open_price = base_price * (1 + price_variation)
        high_price = open_price * 1.02
        low_price = open_price * 0.98
        close_price = open_price * 1.005
        
        points.append(SymbolHistoryPoint(
            timestamp=timestamp.isoformat() + "Z",
            open=round(open_price, 2),
            high=round(high_price, 2),
            low=round(low_price, 2),
            close=round(close_price, 2),
            volume=45234567.0
        ))
    
    return SymbolHistoryResponse(
        symbol=symbol_upper,
        timeframe=timeframe,
        points=points,
        total_points=len(points)
    )


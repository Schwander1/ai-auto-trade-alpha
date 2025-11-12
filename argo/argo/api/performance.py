"""
Performance API endpoints for Argo Trading Engine
GET win rate, GET ROI, GET equity curve
"""

from fastapi import APIRouter, HTTPException, Query, Header
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import time

router = APIRouter(prefix="/api/performance", tags=["performance"])

# Rate limiting
rate_limit_store = {}
RATE_LIMIT_WINDOW = 60
RATE_LIMIT_MAX = 100


class WinRateResponse(BaseModel):
    """Win rate response"""
    overall_win_rate: float = Field(..., ge=0, le=100, description="Overall win rate percentage")
    period: str
    total_trades: int
    winning_trades: int
    losing_trades: int
    by_symbol: Dict[str, float] = Field(default_factory=dict, description="Win rate by symbol")
    by_timeframe: Dict[str, float] = Field(default_factory=dict, description="Win rate by timeframe")


class ROIResponse(BaseModel):
    """ROI response"""
    total_roi: float = Field(..., description="Total ROI percentage")
    period: str
    initial_capital: float
    current_value: float
    profit_loss: float
    annualized_roi: Optional[float] = None
    monthly_roi: Optional[float] = None
    by_symbol: Dict[str, float] = Field(default_factory=dict, description="ROI by symbol")


class EquityCurvePoint(BaseModel):
    """Equity curve data point"""
    date: str
    equity: float
    drawdown: float
    trades: int


class EquityCurveResponse(BaseModel):
    """Equity curve response"""
    points: List[EquityCurvePoint]
    period: str
    peak_equity: float
    max_drawdown: float
    max_drawdown_date: Optional[str] = None


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


@router.get("/win-rate", response_model=WinRateResponse)
async def get_win_rate(
    period: str = Query("all", description="Time period: all, 1d, 7d, 30d, 90d, 1y"),
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    authorization: Optional[str] = Header(None)
):
    """
    Get win rate statistics
    
    **Example Request:**
    ```bash
    curl -X GET "http://localhost:8000/api/performance/win-rate?period=30d" \
         -H "Authorization: HMAC 1234567890:signature"
    ```
    
    **Example Response:**
    ```json
    {
      "overall_win_rate": 96.3,
      "period": "30d",
      "total_trades": 1247,
      "winning_trades": 1201,
      "losing_trades": 46,
      "by_symbol": {
        "AAPL": 97.2,
        "NVDA": 95.8,
        "BTC-USD": 96.5
      },
      "by_timeframe": {
        "1h": 94.5,
        "4h": 96.8,
        "1d": 97.2
      }
    }
    ```
    """
    # Rate limiting
    client_id = authorization or "anonymous"
    if not check_rate_limit(client_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    # Validate period
    valid_periods = ["all", "1d", "7d", "30d", "90d", "1y"]
    if period not in valid_periods:
        raise HTTPException(status_code=400, detail=f"Invalid period. Must be one of: {', '.join(valid_periods)}")
    
    # Mock data (in production, calculate from database)
    return WinRateResponse(
        overall_win_rate=96.3,
        period=period,
        total_trades=1247,
        winning_trades=1201,
        losing_trades=46,
        by_symbol={
            "AAPL": 97.2,
            "NVDA": 95.8,
            "BTC-USD": 96.5,
            "ETH-USD": 94.2
        },
        by_timeframe={
            "1h": 94.5,
            "4h": 96.8,
            "1d": 97.2
        }
    )


@router.get("/roi", response_model=ROIResponse)
async def get_roi(
    period: str = Query("all", description="Time period: all, 1d, 7d, 30d, 90d, 1y"),
    initial_capital: float = Query(10000, ge=1000, description="Initial capital for ROI calculation"),
    authorization: Optional[str] = Header(None)
):
    """
    Get ROI statistics
    
    **Example Request:**
    ```bash
    curl -X GET "http://localhost:8000/api/performance/roi?period=30d&initial_capital=10000" \
         -H "Authorization: HMAC 1234567890:signature"
    ```
    
    **Example Response:**
    ```json
    {
      "total_roi": 24.5,
      "period": "30d",
      "initial_capital": 10000,
      "current_value": 12450,
      "profit_loss": 2450,
      "annualized_roi": 298.2,
      "monthly_roi": 24.5,
      "by_symbol": {
        "AAPL": 12.3,
        "NVDA": 18.7,
        "BTC-USD": 15.2
      }
    }
    ```
    """
    # Rate limiting
    client_id = authorization or "anonymous"
    if not check_rate_limit(client_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    # Validate period
    valid_periods = ["all", "1d", "7d", "30d", "90d", "1y"]
    if period not in valid_periods:
        raise HTTPException(status_code=400, detail=f"Invalid period. Must be one of: {', '.join(valid_periods)}")
    
    # Calculate ROI (mock data)
    roi_pct = 24.5
    current_value = initial_capital * (1 + roi_pct / 100)
    profit_loss = current_value - initial_capital
    
    # Annualized ROI calculation
    days_map = {"1d": 1, "7d": 7, "30d": 30, "90d": 90, "1y": 365, "all": 365}
    days = days_map.get(period, 365)
    annualized = ((1 + roi_pct / 100) ** (365 / days) - 1) * 100 if days > 0 else roi_pct
    
    return ROIResponse(
        total_roi=roi_pct,
        period=period,
        initial_capital=initial_capital,
        current_value=round(current_value, 2),
        profit_loss=round(profit_loss, 2),
        annualized_roi=round(annualized, 2),
        monthly_roi=roi_pct if period == "30d" else None,
        by_symbol={
            "AAPL": 12.3,
            "NVDA": 18.7,
            "BTC-USD": 15.2,
            "ETH-USD": 10.5
        }
    )


@router.get("/equity-curve", response_model=EquityCurveResponse)
async def get_equity_curve(
    period: str = Query("30d", description="Time period: 7d, 30d, 90d, 1y, all"),
    initial_capital: float = Query(10000, ge=1000, description="Initial capital"),
    authorization: Optional[str] = Header(None)
):
    """
    Get equity curve data
    
    **Example Request:**
    ```bash
    curl -X GET "http://localhost:8000/api/performance/equity-curve?period=30d&initial_capital=10000" \
         -H "Authorization: HMAC 1234567890:signature"
    ```
    
    **Example Response:**
    ```json
    {
      "points": [
        {
          "date": "2024-01-01T00:00:00Z",
          "equity": 10000,
          "drawdown": 0,
          "trades": 0
        },
        {
          "date": "2024-01-15T00:00:00Z",
          "equity": 12450,
          "drawdown": 2.1,
          "trades": 45
        }
      ],
      "period": "30d",
      "peak_equity": 12500,
      "max_drawdown": 5.2,
      "max_drawdown_date": "2024-01-10T00:00:00Z"
    }
    ```
    """
    # Rate limiting
    client_id = authorization or "anonymous"
    if not check_rate_limit(client_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    # Validate period
    valid_periods = ["7d", "30d", "90d", "1y", "all"]
    if period not in valid_periods:
        raise HTTPException(status_code=400, detail=f"Invalid period. Must be one of: {', '.join(valid_periods)}")
    
    # Generate equity curve points
    days_map = {"7d": 7, "30d": 30, "90d": 90, "1y": 365, "all": 365}
    days = days_map.get(period, 30)
    points = []
    
    peak_equity = initial_capital
    max_drawdown = 0
    max_drawdown_date = None
    
    for i in range(days):
        date = datetime.utcnow() - timedelta(days=days - i)
        # Simulate equity growth with some volatility
        growth_factor = 1 + (i * 0.008) + (i % 7 - 3) * 0.002
        equity = initial_capital * growth_factor
        
        if equity > peak_equity:
            peak_equity = equity
        
        drawdown = ((peak_equity - equity) / peak_equity) * 100
        if drawdown > max_drawdown:
            max_drawdown = drawdown
            max_drawdown_date = date.isoformat() + "Z"
        
        points.append(EquityCurvePoint(
            date=date.isoformat() + "Z",
            equity=round(equity, 2),
            drawdown=round(drawdown, 2),
            trades=i * 2
        ))
    
    return EquityCurveResponse(
        points=points,
        period=period,
        peak_equity=round(peak_equity, 2),
        max_drawdown=round(max_drawdown, 2),
        max_drawdown_date=max_drawdown_date
    )

"""
Backtest API endpoints for Argo Trading Engine
POST backtest config, GET results
"""

from fastapi import APIRouter, HTTPException, Query, Depends, Header
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import time

router = APIRouter(prefix="/api/v1/backtest", tags=["backtest"])

# Rate limiting
rate_limit_store = {}
RATE_LIMIT_WINDOW = 60
RATE_LIMIT_MAX = 100


class BacktestConfig(BaseModel):
    """Backtest configuration"""
    symbol: str = Field(..., description="Symbol to backtest")
    start_date: str = Field(..., description="Start date (YYYY-MM-DD)")
    end_date: str = Field(..., description="End date (YYYY-MM-DD)")
    initial_capital: float = Field(10000, ge=1000, description="Initial capital")
    strategy: str = Field("default", description="Strategy name")
    risk_per_trade: float = Field(0.02, ge=0.01, le=0.1, description="Risk per trade (1-10%)")
    stop_loss_pct: Optional[float] = Field(0.05, ge=0.01, le=0.2, description="Stop loss percentage")
    take_profit_pct: Optional[float] = Field(0.10, ge=0.01, le=0.5, description="Take profit percentage")


class BacktestResult(BaseModel):
    """Backtest result"""
    backtest_id: str
    status: str  # running, completed, failed
    config: BacktestConfig
    results: Optional[Dict[str, Any]] = None
    created_at: str
    completed_at: Optional[str] = None
    error: Optional[str] = None


class BacktestMetrics(BaseModel):
    """Backtest performance metrics"""
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_return: float
    annualized_return: float
    sharpe_ratio: float
    max_drawdown: float
    profit_factor: float
    avg_win: float
    avg_loss: float
    equity_curve: List[Dict[str, float]]


# Mock backtest storage
BACKTESTS_DB = {}


# Rate limiting now handled by argo.core.rate_limit module


@router.post("", response_model=BacktestResult, status_code=201)
async def create_backtest(
    config: BacktestConfig,
    authorization: Optional[str] = Header(None)
):
    """
    Create a new backtest
    
    **Example Request:**
    ```bash
    curl -X POST "http://localhost:8000/api/backtest" \
         -H "Content-Type: application/json" \
         -H "Authorization: HMAC 1234567890:signature" \
         -d '{
           "symbol": "AAPL",
           "start_date": "2023-01-01",
           "end_date": "2023-12-31",
           "initial_capital": 10000,
           "strategy": "default",
           "risk_per_trade": 0.02
         }'
    ```
    
    **Example Response:**
    ```json
    {
      "backtest_id": "BT-1234567890",
      "status": "running",
      "config": {
        "symbol": "AAPL",
        "start_date": "2023-01-01",
        "end_date": "2023-12-31",
        "initial_capital": 10000,
        "strategy": "default",
        "risk_per_trade": 0.02
      },
      "created_at": "2024-01-15T10:30:00Z",
      "completed_at": null
    }
    ```
    """
    # Rate limiting
    client_id = authorization or "anonymous"
    if not check_rate_limit(client_id, RATE_LIMIT_MAX, RATE_LIMIT_WINDOW):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    # Validate dates
    try:
        start = datetime.fromisoformat(config.start_date)
        end = datetime.fromisoformat(config.end_date)
        if start >= end:
            raise HTTPException(status_code=400, detail="Start date must be before end date")
        if (end - start).days > 365:
            raise HTTPException(status_code=400, detail="Backtest period cannot exceed 1 year")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    # Create backtest
    backtest_id = f"BT-{int(time.time() * 1000)}"
    backtest = BacktestResult(
        backtest_id=backtest_id,
        status="running",
        config=config,
        created_at=datetime.utcnow().isoformat() + "Z"
    )
    
    BACKTESTS_DB[backtest_id] = backtest.dict()
    
    # Simulate backtest completion (in production, run async)
    # For now, return immediately with running status
    
    return backtest


@router.get("/{backtest_id}", response_model=BacktestResult)
async def get_backtest_result(
    backtest_id: str,
    authorization: Optional[str] = Header(None)
):
    """
    Get backtest result by ID
    
    **Example Request:**
    ```bash
    curl -X GET "http://localhost:8000/api/backtest/BT-1234567890" \
         -H "Authorization: HMAC 1234567890:signature"
    ```
    
    **Example Response:**
    ```json
    {
      "backtest_id": "BT-1234567890",
      "status": "completed",
      "config": {...},
      "results": {
        "total_trades": 45,
        "win_rate": 96.3,
        "total_return": 24.5,
        "sharpe_ratio": 2.1
      },
      "created_at": "2024-01-15T10:30:00Z",
      "completed_at": "2024-01-15T10:35:00Z"
    }
    ```
    """
    # Rate limiting
    client_id = authorization or "anonymous"
    if not check_rate_limit(client_id, RATE_LIMIT_MAX, RATE_LIMIT_WINDOW):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    # Find backtest
    backtest = BACKTESTS_DB.get(backtest_id)
    if not backtest:
        raise HTTPException(status_code=404, detail=f"Backtest {backtest_id} not found")
    
    # If running, simulate completion with mock results
    if backtest.get("status") == "running":
        backtest["status"] = "completed"
        backtest["completed_at"] = datetime.utcnow().isoformat() + "Z"
        backtest["results"] = {
            "total_trades": 45,
            "winning_trades": 43,
            "losing_trades": 2,
            "win_rate": 95.6,
            "total_return": 24.5,
            "annualized_return": 28.2,
            "sharpe_ratio": 2.1,
            "max_drawdown": 5.2,
            "profit_factor": 12.5,
            "avg_win": 2.8,
            "avg_loss": -1.2
        }
        BACKTESTS_DB[backtest_id] = backtest
    
    return BacktestResult(**backtest)


@router.get("/{backtest_id}/metrics", response_model=BacktestMetrics)
async def get_backtest_metrics(
    backtest_id: str,
    authorization: Optional[str] = Header(None)
):
    """
    Get detailed backtest metrics
    
    **Example Request:**
    ```bash
    curl -X GET "http://localhost:8000/api/backtest/BT-1234567890/metrics" \
         -H "Authorization: HMAC 1234567890:signature"
    ```
    """
    # Rate limiting
    client_id = authorization or "anonymous"
    if not check_rate_limit(client_id, RATE_LIMIT_MAX, RATE_LIMIT_WINDOW):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    # Find backtest
    backtest = BACKTESTS_DB.get(backtest_id)
    if not backtest:
        raise HTTPException(status_code=404, detail=f"Backtest {backtest_id} not found")
    
    if backtest.get("status") != "completed":
        raise HTTPException(status_code=400, detail="Backtest not completed yet")
    
    results = backtest.get("results", {})
    
    # Generate mock equity curve
    equity_curve = []
    initial = backtest["config"]["initial_capital"]
    for i in range(30):
        equity_curve.append({
            "date": (datetime.utcnow() - timedelta(days=30-i)).isoformat(),
            "equity": initial * (1 + (i * 0.01))
        })
    
    return BacktestMetrics(
        total_trades=results.get("total_trades", 0),
        winning_trades=results.get("winning_trades", 0),
        losing_trades=results.get("losing_trades", 0),
        win_rate=results.get("win_rate", 0.0),
        total_return=results.get("total_return", 0.0),
        annualized_return=results.get("annualized_return", 0.0),
        sharpe_ratio=results.get("sharpe_ratio", 0.0),
        max_drawdown=results.get("max_drawdown", 0.0),
        profit_factor=results.get("profit_factor", 0.0),
        avg_win=results.get("avg_win", 0.0),
        avg_loss=results.get("avg_loss", 0.0),
        equity_curve=equity_curve
    )


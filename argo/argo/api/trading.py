"""
Trading status API endpoints
Exposes trading environment, account status, and prop firm mode information
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import json
import os
import logging
from pathlib import Path

try:
    from argo.core.paper_trading_engine import PaperTradingEngine
    from argo.core.environment import detect_environment, get_environment_info
except ImportError:
    # Fallback for different import paths
    from core.paper_trading_engine import PaperTradingEngine
    from core.environment import detect_environment, get_environment_info

router = APIRouter(prefix="/api/v1/trading", tags=["trading"])
logger = logging.getLogger(__name__)


class TradingStatusResponse(BaseModel):
    """Trading status response model"""
    environment: str  # 'development' or 'production'
    trading_mode: str  # 'dev', 'production', 'prop_firm', or 'simulation'
    account_name: Optional[str] = None
    account_number: Optional[str] = None
    portfolio_value: Optional[float] = None
    buying_power: Optional[float] = None
    prop_firm_enabled: bool = False
    alpaca_connected: bool = False
    account_status: Optional[str] = None


@router.get("/status", response_model=TradingStatusResponse)
async def get_trading_status():
    """
    Get current trading environment and account status
    
    Returns information about:
    - Current environment (development/production)
    - Trading mode (dev/production/prop_firm/simulation)
    - Account details (if connected)
    - Prop firm mode status
    
    **Example Request:**
    ```bash
    curl -X GET "http://localhost:8000/api/v1/trading/status"
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
    try:
        # Detect environment
        environment = detect_environment()
        env_info = get_environment_info()
        
        # Initialize trading engine to get account info and prop firm status
        try:
            engine = PaperTradingEngine()
            
            # Check prop firm status from engine
            prop_firm_enabled = getattr(engine, 'prop_firm_enabled', False)
            
            if engine.alpaca_enabled:
                # Get account details
                account = engine.get_account_details()
                
                # Determine trading mode
                if prop_firm_enabled:
                    trading_mode = "prop_firm"
                elif environment == "production":
                    trading_mode = "production"
                elif environment == "development":
                    trading_mode = "dev"
                else:
                    trading_mode = "simulation"
                
                return TradingStatusResponse(
                    environment=environment,
                    trading_mode=trading_mode,
                    account_name=engine.account_name,
                    account_number=account.get("account_number"),
                    portfolio_value=account.get("portfolio_value"),
                    buying_power=account.get("buying_power"),
                    prop_firm_enabled=prop_firm_enabled,
                    alpaca_connected=True,
                    account_status=account.get("status")
                )
            else:
                # Alpaca not connected - simulation mode
                trading_mode = "prop_firm" if prop_firm_enabled else "simulation"
                
                return TradingStatusResponse(
                    environment=environment,
                    trading_mode=trading_mode,
                    account_name=None,
                    account_number=None,
                    portfolio_value=None,
                    buying_power=None,
                    prop_firm_enabled=prop_firm_enabled,
                    alpaca_connected=False,
                    account_status=None
                )
                
        except Exception as e:
            logger.warning(f"Failed to initialize trading engine: {e}")
            # Return status without account details
            trading_mode = "prop_firm" if prop_firm_enabled else "simulation"
            
            return TradingStatusResponse(
                environment=environment,
                trading_mode=trading_mode,
                account_name=None,
                account_number=None,
                portfolio_value=None,
                buying_power=None,
                prop_firm_enabled=prop_firm_enabled,
                alpaca_connected=False,
                account_status=None
            )
            
    except Exception as e:
        logger.error(f"Error getting trading status: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get trading status: {str(e)}"
        )


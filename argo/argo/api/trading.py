"""
Trading status API endpoints
Exposes trading environment, account status, and prop firm mode information
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import json
import os
import logging
from pathlib import Path

try:
    from argo.core.paper_trading_engine import PaperTradingEngine
    from argo.core.environment import detect_environment, get_environment_info
    from argo.core.signal_generation_service import get_signal_service
except ImportError:
    # Fallback for different import paths
    from core.paper_trading_engine import PaperTradingEngine
    from core.environment import detect_environment, get_environment_info
    from core.signal_generation_service import get_signal_service

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


@router.post("/execute")
async def execute_signal(signal: Dict[str, Any]):
    """
    Execute a trading signal
    
    This endpoint receives signals from the Signal Distributor and executes them
    using the signal generation service's trading engine.
    
    **Example Request:**
    ```bash
    curl -X POST "http://localhost:8000/api/v1/trading/execute" \
         -H "Content-Type: application/json" \
         -d '{
           "symbol": "AAPL",
           "action": "BUY",
           "entry_price": 175.50,
           "confidence": 95.5,
           ...
         }'
    ```
    
    **Example Response:**
    ```json
    {
      "success": true,
      "order_id": "abc123",
      "executor_id": "argo"
    }
    ```
    """
    try:
        # Get signal generation service (which has the trading engine)
        signal_service = get_signal_service()
        
        if not signal_service:
            logger.error("Signal generation service not available")
            return JSONResponse(
                status_code=503,
                content={
                    "success": False,
                    "error": "Signal generation service not available",
                    "executor_id": "argo"
                }
            )
        
        # Check if trading engine is available
        if not signal_service.trading_engine:
            logger.warning("Trading engine not available for signal execution")
            return JSONResponse(
                status_code=503,
                content={
                    "success": False,
                    "error": "Trading engine not available",
                    "executor_id": "argo"
                }
            )
        
        # Get account and positions for execution
        account = signal_service.trading_engine.get_account_details()
        if not account:
            logger.error("Failed to get account details")
            return JSONResponse(
                status_code=503,
                content={
                    "success": False,
                    "error": "Failed to get account details",
                    "executor_id": "argo"
                }
            )
        
        # Get existing positions
        positions = signal_service.trading_engine.get_positions()
        existing_positions = [p for p in positions] if positions else []
        
        # Execute the signal
        logger.info(f"🚀 Executing signal: {signal.get('symbol')} {signal.get('action')} @ ${signal.get('entry_price', 0):.2f} ({signal.get('confidence', 0):.1f}% confidence)")
        
        # Add more detailed error handling
        try:
            order_id = signal_service.trading_engine.execute_signal(
                signal, 
                existing_positions=existing_positions
            )
            
            if order_id:
                logger.info(f"✅ Trade executed: Order ID {order_id}")
                # Update signal in database with order_id if possible
                try:
                    signal_id = signal.get('signal_id')
                    if signal_id and hasattr(signal_service, 'tracker'):
                        # Try to update signal with order_id
                        pass  # Signal tracker update can be done here if needed
                except Exception as e:
                    logger.debug(f"Could not update signal with order_id: {e}")
                
                return {
                    "success": True,
                    "order_id": str(order_id),
                    "executor_id": "argo"
                }
            else:
                logger.warning(f"⚠️  Trade execution returned no order ID for {signal.get('symbol')}")
                # Check if it's a validation issue
                error_msg = "Trade execution failed (no order ID returned). This could be due to: risk validation, position limits, market hours, or insufficient buying power."
                return JSONResponse(
                    status_code=400,
                    content={
                        "success": False,
                        "error": error_msg,
                        "executor_id": "argo",
                        "symbol": signal.get('symbol'),
                        "confidence": signal.get('confidence', 0)
                    }
                )
        except Exception as exec_error:
            logger.error(f"❌ Error during trade execution: {exec_error}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": f"Execution error: {str(exec_error)}",
                    "executor_id": "argo"
                }
            )
            
    except Exception as e:
        logger.error(f"❌ Error executing signal: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e),
                "executor_id": "argo"
            }
        )


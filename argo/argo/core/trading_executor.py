#!/usr/bin/env python3
"""
Trading Executor Service
Lightweight service that executes trades from signals, doesn't generate signals
"""
import json
import logging
import os
from pathlib import Path
from typing import Dict, Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TradingExecutor")

app = FastAPI(title="Trading Executor", version="1.0.0")

# Global executor instance
_executor = None


class TradingExecutor:
    """Lightweight trading executor - only executes trades"""
    
    def __init__(self, config_path: str, executor_id: str):
        self.config_path = config_path
        self.executor_id = executor_id
        self._load_config()
        self._init_trading_engine()
        logger.info(f"✅ Trading Executor '{executor_id}' initialized")
    
    def _load_config(self):
        """Load executor configuration"""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        with open(self.config_path) as f:
            self.config = json.load(f)
        
        self.trading_config = self.config.get("trading", {})
        self.prop_firm_config = self.config.get("prop_firm", {})
        self.prop_firm_enabled = self.prop_firm_config.get("enabled", False)
    
    def _init_trading_engine(self):
        """Initialize trading engine for this executor"""
        from argo.core.paper_trading_engine import PaperTradingEngine
        self.trading_engine = PaperTradingEngine(self.config_path)
        logger.info(f"✅ Trading engine initialized for {self.executor_id}")
    
    def validate_signal(self, signal: Dict) -> tuple[bool, str]:
        """Validate signal meets executor requirements"""
        # Check confidence threshold
        min_confidence = self.trading_config.get('min_confidence', 75.0)
        if self.prop_firm_enabled:
            risk_limits = self.prop_firm_config.get('risk_limits', {})
            min_confidence = risk_limits.get('min_confidence', 82.0)
        
        if signal.get('confidence', 0) < min_confidence:
            return False, f"Confidence {signal.get('confidence')} below threshold {min_confidence}"
        
        # Prop firm specific checks
        if self.prop_firm_enabled:
            # Skip crisis signals
            if signal.get('regime') == 'CRISIS':
                return False, "Prop firm skips CRISIS regime signals"
            
            # Additional prop firm validations can go here
        
        return True, "OK"
    
    def execute_signal(self, signal: Dict) -> Optional[str]:
        """Execute signal on this executor's account"""
        # Validate signal
        is_valid, reason = self.validate_signal(signal)
        if not is_valid:
            logger.warning(f"Signal validation failed for {self.executor_id}: {reason}")
            return None
        
        try:
            # Get account and positions
            account = self.trading_engine.get_account_details()
            if not account:
                logger.error(f"Failed to get account details for {self.executor_id}")
                return None
            
            # Get existing positions
            positions = self.trading_engine.get_positions()
            existing_positions = [p for p in positions] if positions else []
            
            # Execute trade
            order_id = self.trading_engine.execute_signal(signal, existing_positions=existing_positions)
            
            if order_id:
                logger.info(f"✅ Trade executed on {self.executor_id}: Order ID {order_id}")
                return str(order_id)
            else:
                logger.warning(f"⚠️  Trade execution returned no order ID for {self.executor_id}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error executing signal on {self.executor_id}: {e}", exc_info=True)
            return None


def get_executor() -> Optional[TradingExecutor]:
    """Get global executor instance"""
    return _executor


@app.on_event("startup")
async def startup():
    """Initialize executor on startup"""
    global _executor
    
    # Determine executor ID and config path from environment
    executor_id = os.getenv("EXECUTOR_ID", "argo")
    config_path = os.getenv("EXECUTOR_CONFIG_PATH")
    
    if not config_path:
        # Auto-detect based on executor_id
        if executor_id == "prop_firm":
            config_path = "/root/argo-production-prop-firm/config.json"
        else:
            config_path = "/root/argo-production-green/config.json"
    
    if not os.path.exists(config_path):
        logger.error(f"❌ Config file not found: {config_path}")
        logger.error("Set EXECUTOR_CONFIG_PATH environment variable")
        return
    
    try:
        _executor = TradingExecutor(config_path, executor_id)
        logger.info(f"✅ Executor '{executor_id}' started successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize executor: {e}", exc_info=True)


@app.post("/api/v1/trading/execute")
async def execute_signal(signal: Dict):
    """Execute signal endpoint"""
    if _executor is None:
        raise HTTPException(status_code=503, detail="Executor not initialized")
    
    try:
        order_id = _executor.execute_signal(signal)
        if order_id:
            return {
                "success": True,
                "order_id": order_id,
                "executor_id": _executor.executor_id
            }
        else:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": "Trade execution failed",
                    "executor_id": _executor.executor_id
                }
            )
    except Exception as e:
        logger.error(f"Error in execute endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/trading/status")
async def get_status():
    """Get executor status"""
    if _executor is None:
        return {
            "status": "not_initialized",
            "executor_id": os.getenv("EXECUTOR_ID", "unknown")
        }
    
    try:
        account = _executor.trading_engine.get_account_details()
        positions = _executor.trading_engine.get_positions()
        
        return {
            "status": "active",
            "executor_id": _executor.executor_id,
            "account": account,
            "positions_count": len(positions) if positions else 0,
            "prop_firm_enabled": _executor.prop_firm_enabled
        }
    except Exception as e:
        logger.error(f"Error getting status: {e}", exc_info=True)
        return {
            "status": "error",
            "executor_id": _executor.executor_id,
            "error": str(e)
        }


@app.get("/health")
async def health():
    """Health check endpoint"""
    if _executor is None:
        return {"status": "unhealthy", "reason": "executor_not_initialized"}
    
    try:
        # Quick health check
        account = _executor.trading_engine.get_account_details()
        if account:
            return {
                "status": "healthy",
                "executor_id": _executor.executor_id,
                "version": "1.0.0"
            }
        else:
            return {"status": "unhealthy", "reason": "account_unavailable"}
    except Exception as e:
        return {"status": "unhealthy", "reason": str(e)}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)


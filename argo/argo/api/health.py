#!/usr/bin/env python3
"""
Production Health Check Endpoint
Provides comprehensive health check for production monitoring
"""
import logging
import asyncio
from datetime import datetime
from typing import Dict, Optional
from asyncio import TimeoutError
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/health", tags=["health"])

# Health check timeout configuration
HEALTH_CHECK_TIMEOUT = 5.0  # 5 seconds timeout for each check

class HealthStatus(BaseModel):
    """Health status response"""
    status: str  # 'healthy', 'degraded', 'unhealthy'
    timestamp: str
    version: str
    components: Dict
    checks: Dict

async def check_with_timeout(check_func, timeout: float = HEALTH_CHECK_TIMEOUT, component_name: str = "unknown"):
    """
    Execute a health check with timeout handling
    
    Args:
        check_func: Async function to execute
        timeout: Timeout in seconds
        component_name: Name of component being checked (for logging)
    
    Returns:
        Dict with status and result/error
    """
    try:
        result = await asyncio.wait_for(check_func(), timeout=timeout)
        return {"status": "healthy", "result": result}
    except TimeoutError:
        logger.warning(f"Health check for {component_name} timed out after {timeout}s")
        return {"status": "unhealthy", "error": f"timeout after {timeout}s"}
    except Exception as e:
        logger.error(f"Health check for {component_name} failed: {e}")
        return {"status": "unhealthy", "error": str(e)}

@router.get("/", response_model=HealthStatus)
async def health_check():
    """
    Comprehensive health check endpoint with timeout handling

    Returns:
        Health status with component checks
    """
    checks = {}
    components = {}
    overall_status = 'healthy'

    # Check signal generation service with timeout
    async def check_signal_service():
        from argo.core.signal_generation_service import SignalGenerationService
        service = SignalGenerationService()
        return {
            'status': 'healthy' if service.running else 'degraded',
            'running': service.running
        }
    
    result = await check_with_timeout(check_signal_service, component_name="signal_generation")
    if result["status"] == "healthy":
        components['signal_generation'] = result["result"]
        if not result["result"].get('running', False):
            overall_status = 'degraded'
    else:
        components['signal_generation'] = {
            'status': 'unhealthy',
            'error': result.get('error', 'unknown error')
        }
        overall_status = 'unhealthy'

    # Check database with timeout
    async def check_database():
        from pathlib import Path
        import sqlite3
        
        db_path = Path(__file__).parent.parent.parent / "data" / "signals.db"
        if not db_path.exists():
            return {
                'status': 'degraded',
                'error': 'Database file not found'
            }
        
        # Run database check in thread pool to avoid blocking
        def db_check_sync():
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM signals")
            signal_count = cursor.fetchone()[0]
            conn.close()
            return signal_count
        
        signal_count = await asyncio.to_thread(db_check_sync)
        return {
            'status': 'healthy',
            'signal_count': signal_count
        }
    
    result = await check_with_timeout(check_database, component_name="database")
    if result["status"] == "healthy":
        components['database'] = result["result"]
    else:
        components['database'] = {
            'status': 'unhealthy',
            'error': result.get('error', 'unknown error')
        }
        if overall_status == 'healthy':
            overall_status = 'degraded'

    # Check Alpine sync with timeout
    async def check_alpine_sync():
        from argo.core.alpine_sync import AlpineSyncService
        sync_service = AlpineSyncService()
        if sync_service._sync_enabled:
            health_ok = await sync_service.check_health()
            return {
                'status': 'healthy' if health_ok else 'degraded',
                'enabled': True,
                'alpine_reachable': health_ok
            }
        else:
            return {
                'status': 'degraded',
                'enabled': False,
                'reason': 'Sync disabled or not configured'
            }
    
    result = await check_with_timeout(check_alpine_sync, component_name="alpine_sync")
    if result["status"] == "healthy":
        components['alpine_sync'] = result["result"]
        if not result["result"].get('alpine_reachable', False) and result["result"].get('enabled', False):
            if overall_status == 'healthy':
                overall_status = 'degraded'
    else:
        components['alpine_sync'] = {
            'status': 'unhealthy',
            'error': result.get('error', 'unknown error')
        }
        if overall_status == 'healthy':
            overall_status = 'degraded'

    # Check trading engine with timeout
    async def check_trading_engine():
        from argo.core.paper_trading_engine import PaperTradingEngine
        engine = PaperTradingEngine()
        if engine.alpaca_enabled:
            account = engine.get_account_details()
            return {
                'status': 'healthy',
                'alpaca_connected': True,
                'account_status': account.get('status', 'unknown') if account else 'unknown'
            }
        else:
            return {
                'status': 'degraded',
                'alpaca_connected': False,
                'reason': 'Alpaca not connected'
            }
    
    result = await check_with_timeout(check_trading_engine, component_name="trading_engine")
    if result["status"] == "healthy":
        components['trading_engine'] = result["result"]
    else:
        components['trading_engine'] = {
            'status': 'unhealthy',
            'error': result.get('error', 'unknown error')
        }
        if overall_status == 'healthy':
            overall_status = 'degraded'

    # Check prop firm monitor (if enabled) with timeout
    async def check_prop_firm():
        from argo.core.config_loader import ConfigLoader
        config, _ = ConfigLoader.load_config()
        prop_firm_enabled = config.get('prop_firm', {}).get('enabled', False)

        if prop_firm_enabled:
            from argo.risk.prop_firm_risk_monitor import PropFirmRiskMonitor
            risk_limits = config.get('prop_firm', {}).get('risk_limits', {})
            monitor = PropFirmRiskMonitor(risk_limits)
            stats = monitor.get_monitoring_stats()

            return {
                'status': 'healthy',
                'enabled': True,
                'monitoring_active': stats.get('monitoring_active', False),
                'risk_level': stats.get('current_risk_level', 'normal')
            }
        else:
            return {
                'status': 'healthy',
                'enabled': False
            }
    
    result = await check_with_timeout(check_prop_firm, component_name="prop_firm_monitor")
    if result["status"] == "healthy":
        components['prop_firm_monitor'] = result["result"]
    else:
        components['prop_firm_monitor'] = {
            'status': 'degraded',
            'error': result.get('error', 'unknown error')
        }

    # Overall checks
    checks['overall'] = {
        'status': overall_status,
        'timestamp': datetime.now().isoformat()
    }

    return HealthStatus(
        status=overall_status,
        timestamp=datetime.now().isoformat(),
        version='1.0.0',
        components=components,
        checks=checks
    )

@router.get("/simple")
async def simple_health_check():
    """
    Simple health check (for load balancers)

    Returns:
        200 OK if healthy, 503 if unhealthy
    """
    try:
        # Quick check - just verify service is importable
        from argo.core.signal_generation_service import SignalGenerationService
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

#!/usr/bin/env python3
"""
Production Health Check Endpoint
Provides comprehensive health check for production monitoring
"""
import logging
from datetime import datetime
from typing import Dict, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/health", tags=["health"])

class HealthStatus(BaseModel):
    """Health status response"""
    status: str  # 'healthy', 'degraded', 'unhealthy'
    timestamp: str
    version: str
    components: Dict
    checks: Dict

@router.get("/", response_model=HealthStatus)
async def health_check():
    """
    Comprehensive health check endpoint

    Returns:
        Health status with component checks
    """
    checks = {}
    components = {}
    overall_status = 'healthy'

    # Check signal generation service
    try:
        from argo.core.signal_generation_service import SignalGenerationService
        service = SignalGenerationService()
        components['signal_generation'] = {
            'status': 'healthy' if service.running else 'degraded',
            'running': service.running
        }
        if not service.running:
            overall_status = 'degraded'
    except Exception as e:
        components['signal_generation'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
        overall_status = 'unhealthy'

    # Check database
    try:
        from pathlib import Path
        db_path = Path(__file__).parent.parent.parent / "data" / "signals.db"
        if db_path.exists():
            import sqlite3
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM signals")
            signal_count = cursor.fetchone()[0]
            conn.close()
            components['database'] = {
                'status': 'healthy',
                'signal_count': signal_count
            }
        else:
            components['database'] = {
                'status': 'degraded',
                'error': 'Database file not found'
            }
            if overall_status == 'healthy':
                overall_status = 'degraded'
    except Exception as e:
        components['database'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
        overall_status = 'unhealthy'

    # Check Alpine sync
    try:
        from argo.core.alpine_sync import AlpineSyncService
        sync_service = AlpineSyncService()
        if sync_service._sync_enabled:
            health_ok = await sync_service.check_health()
            components['alpine_sync'] = {
                'status': 'healthy' if health_ok else 'degraded',
                'enabled': True,
                'alpine_reachable': health_ok
            }
            if not health_ok:
                if overall_status == 'healthy':
                    overall_status = 'degraded'
        else:
            components['alpine_sync'] = {
                'status': 'degraded',
                'enabled': False,
                'reason': 'Sync disabled or not configured'
            }
    except Exception as e:
        components['alpine_sync'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
        if overall_status == 'healthy':
            overall_status = 'degraded'

    # Check trading engine
    try:
        from argo.core.paper_trading_engine import PaperTradingEngine
        engine = PaperTradingEngine()
        if engine.alpaca_enabled:
            account = engine.get_account_details()
            components['trading_engine'] = {
                'status': 'healthy',
                'alpaca_connected': True,
                'account_status': account.get('status', 'unknown') if account else 'unknown'
            }
        else:
            components['trading_engine'] = {
                'status': 'degraded',
                'alpaca_connected': False,
                'reason': 'Alpaca not connected'
            }
    except Exception as e:
        components['trading_engine'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
        if overall_status == 'healthy':
            overall_status = 'degraded'

    # Check prop firm monitor (if enabled)
    try:
        from argo.core.config_loader import ConfigLoader
        config, _ = ConfigLoader.load_config()
        prop_firm_enabled = config.get('prop_firm', {}).get('enabled', False)

        if prop_firm_enabled:
            from argo.risk.prop_firm_risk_monitor import PropFirmRiskMonitor
            risk_limits = config.get('prop_firm', {}).get('risk_limits', {})
            monitor = PropFirmRiskMonitor(risk_limits)
            stats = monitor.get_monitoring_stats()

            components['prop_firm_monitor'] = {
                'status': 'healthy',
                'enabled': True,
                'monitoring_active': stats.get('monitoring_active', False),
                'risk_level': stats.get('current_risk_level', 'normal')
            }
        else:
            components['prop_firm_monitor'] = {
                'status': 'healthy',
                'enabled': False
            }
    except Exception as e:
        components['prop_firm_monitor'] = {
            'status': 'degraded',
            'error': str(e)
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

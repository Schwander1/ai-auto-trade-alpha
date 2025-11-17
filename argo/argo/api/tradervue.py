"""
Tradervue API endpoints
Provides access to Tradervue metrics, widgets, and sync functionality
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime, timedelta

from argo.integrations.tradervue_integration import get_tradervue_integration

router = APIRouter(prefix="/api/v1/tradervue", tags=["tradervue"])


@router.get("/metrics")
async def get_tradervue_metrics(
    days: int = Query(30, ge=1, le=365, description="Number of days to look back")
):
    """
    Get performance metrics from Tradervue
    
    Returns performance metrics including win rate, ROI, equity curve, etc.
    """
    integration = get_tradervue_integration()
    
    if not integration.client.enabled:
        raise HTTPException(status_code=503, detail="Tradervue integration not enabled")
    
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    
    metrics = integration.get_performance_metrics(start_date, end_date)
    
    if metrics:
        return {
            "status": "success",
            "period": {
                "start_date": start_date,
                "end_date": end_date,
                "days": days
            },
            "metrics": metrics
        }
    else:
        raise HTTPException(status_code=404, detail="Metrics not available from Tradervue API")


@router.get("/widget-url")
async def get_widget_url(
    widget_type: str = Query("equity", description="Widget type: equity, trades, performance"),
    width: int = Query(600, ge=100, le=1200, description="Widget width in pixels"),
    height: int = Query(400, ge=100, le=800, description="Widget height in pixels")
):
    """
    Get Tradervue widget URL for embedding in frontend
    
    Widget types:
    - equity: Equity curve chart
    - trades: Trade list
    - performance: Performance metrics
    """
    integration = get_tradervue_integration()
    
    if not integration.client.enabled:
        raise HTTPException(status_code=503, detail="Tradervue integration not enabled")
    
    url = integration.client.get_widget_url(widget_type, width, height)
    
    if url:
        return {
            "status": "success",
            "widget_url": url,
            "widget_type": widget_type,
            "width": width,
            "height": height
        }
    else:
        raise HTTPException(status_code=404, detail="Widget URL not available")


@router.get("/profile-url")
async def get_profile_url():
    """
    Get Tradervue public profile URL
    
    Returns the public profile URL that can be shared with clients/investors
    """
    integration = get_tradervue_integration()
    
    if not integration.client.enabled:
        raise HTTPException(status_code=503, detail="Tradervue integration not enabled")
    
    url = integration.get_profile_url()
    
    if url:
        return {
            "status": "success",
            "profile_url": url
        }
    else:
        raise HTTPException(status_code=404, detail="Profile URL not available")


@router.post("/sync")
async def sync_trades(
    days: int = Query(30, ge=1, le=365, description="Number of days to sync")
):
    """
    Manually trigger trade sync to Tradervue
    
    Syncs recent trades from UnifiedPerformanceTracker to Tradervue.
    This is useful for:
    - Initial setup
    - Backfilling historical trades
    - Re-syncing after errors
    """
    integration = get_tradervue_integration()
    
    if not integration.client.enabled:
        raise HTTPException(status_code=503, detail="Tradervue integration not enabled")
    
    stats = integration.sync_recent_trades(days=days)
    
    return {
        "status": "success",
        "message": f"Sync completed: {stats['synced']} synced, {stats['failed']} failed, {stats['skipped']} skipped",
        "stats": stats,
        "period_days": days
    }


@router.get("/status")
async def get_tradervue_status():
    """
    Get Tradervue integration status
    
    Returns whether Tradervue is enabled and configured
    """
    integration = get_tradervue_integration()
    
    return {
        "status": "enabled" if integration.client.enabled else "disabled",
        "enabled": integration.client.enabled,
        "username": integration.client.username if integration.client.enabled else None,
        "profile_url": integration.get_profile_url() if integration.client.enabled else None
    }


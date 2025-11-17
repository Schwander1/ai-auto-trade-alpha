#!/usr/bin/env python3
"""
Debug API Endpoints
REST API endpoints for debugging signal generation
"""
from fastapi import APIRouter, HTTPException
from typing import Optional, Dict, List
from pydantic import BaseModel
from datetime import datetime
import json
from pathlib import Path

router = APIRouter(prefix="/api/debug", tags=["debug"])

class TraceRequest(BaseModel):
    symbol: str
    index: Optional[int] = 200

class TraceResponse(BaseModel):
    success: bool
    traces: List[Dict]
    stats: Dict

@router.get("/traces")
async def get_traces(symbol: Optional[str] = None, limit: int = 100):
    """Get signal generation traces"""
    try:
        from argo.backtest.signal_tracer import get_tracer
        tracer = get_tracer()
        
        if symbol:
            traces = tracer.get_traces_for_symbol(symbol)[-limit:]
        else:
            traces = tracer.traces[-limit:]
        
        return {
            "success": True,
            "traces": traces,
            "count": len(traces)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_trace_stats():
    """Get tracing statistics"""
    try:
        from argo.backtest.signal_tracer import get_tracer
        tracer = get_tracer()
        return {
            "success": True,
            "stats": tracer.get_stats()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/trace-symbol")
async def trace_symbol(request: TraceRequest):
    """Trace signal generation for a specific symbol and index"""
    try:
        import asyncio
        from argo.scripts.debug_signal_generation import debug_signal_pipeline
        
        # Run debug pipeline
        await debug_signal_pipeline(request.symbol, request.index)
        
        # Get traces
        from argo.backtest.signal_tracer import get_tracer
        tracer = get_tracer()
        traces = tracer.get_traces_for_symbol(request.symbol)
        
        return {
            "success": True,
            "symbol": request.symbol,
            "index": request.index,
            "traces": traces,
            "stats": tracer.get_stats()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/report")
async def get_trace_report():
    """Get full trace report"""
    try:
        report_file = Path('argo/reports/signal_debug_report.json')
        if not report_file.exists():
            raise HTTPException(status_code=404, detail="Report not found")
        
        with open(report_file, 'r') as f:
            report = json.load(f)
        
        return {
            "success": True,
            "report": report
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/clear-traces")
async def clear_traces():
    """Clear all traces"""
    try:
        from argo.backtest.signal_tracer import get_tracer
        tracer = get_tracer()
        tracer.clear()
        return {"success": True, "message": "Traces cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


"""
Execution Dashboard API - Admin Only Access
Provides execution metrics, queue status, and account monitoring
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
import sqlite3
from pathlib import Path
import json
import logging
import asyncio

from argo.core.auth import require_admin_user
from argo.core.signal_queue import SignalQueue, QueueStatus
from argo.core.account_state_monitor import AccountStateMonitor

logger = logging.getLogger("ExecutionDashboard")

router = APIRouter(prefix="/api/v1/execution", tags=["execution"])

# Global instances (will be initialized in startup)
_signal_queue: Optional[SignalQueue] = None
_account_monitor: Optional[AccountStateMonitor] = None

def get_signal_queue() -> SignalQueue:
    """Get signal queue instance"""
    global _signal_queue
    if _signal_queue is None:
        _signal_queue = SignalQueue()
    return _signal_queue

def get_account_monitor() -> AccountStateMonitor:
    """Get account monitor instance"""
    global _account_monitor
    if _account_monitor is None:
        _account_monitor = AccountStateMonitor()
    return _account_monitor

@router.get("/metrics")
async def get_execution_metrics(
    hours: int = 24,
    request: Optional[Request] = None,
    admin: bool = Depends(require_admin_user)
):
    """Get execution metrics - Admin only"""
    try:
        # Get queue stats
        queue = get_signal_queue()
        queue_stats = queue.get_queue_stats()

        # Get additional metrics from database
        conn = sqlite3.connect(str(queue.db_path), timeout=10.0)
        cursor = conn.cursor()

        # Get signals generated in last N hours
        cutoff_time = (datetime.now() - timedelta(hours=hours)).isoformat()
        cursor.execute('''
            SELECT COUNT(*) FROM signal_queue
            WHERE queued_at > ?
        ''', (cutoff_time,))
        signals_generated = cursor.fetchone()[0]

        # Get execution rate from last N hours
        cursor.execute('''
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN status = 'executed' THEN 1 ELSE 0 END) as executed
            FROM signal_queue
            WHERE queued_at > ?
        ''', (cutoff_time,))
        row = cursor.fetchone()
        total_recent = row[0] or 0
        executed_recent = row[1] or 0
        execution_rate = (executed_recent / total_recent * 100) if total_recent > 0 else 0

        conn.close()

        return {
            "execution_rate": round(execution_rate, 2),
            "signals_generated": signals_generated,
            "signals_executed": executed_recent,
            "queue_pending": queue_stats.get('pending', 0),
            "queue_ready": queue_stats.get('ready', 0),
            "queue_executing": queue_stats.get('executing', 0),
            "queue_executed": queue_stats.get('executed', 0),
            "queue_expired": queue_stats.get('expired', 0),
            "queue_cancelled": queue_stats.get('cancelled', 0),
            "total_in_queue": sum(queue_stats.values()),
            "hours": hours,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting execution metrics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/queue")
async def get_queue_status(
    status: Optional[str] = None,
    limit: int = 50,
    request: Optional[Request] = None,
    admin: bool = Depends(require_admin_user)
):
    """Get signal queue status - Admin only"""
    try:
        queue = get_signal_queue()

        # Get queue stats
        stats = queue.get_queue_stats()

        # Get queued signals
        conn = sqlite3.connect(str(queue.db_path), timeout=10.0)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = "SELECT * FROM signal_queue WHERE 1=1"
        params = []

        if status:
            query += " AND status = ?"
            params.append(status)

        query += " ORDER BY priority DESC, queued_at DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        signals = []
        for row in cursor.fetchall():
            signals.append({
                "signal_id": row['signal_id'],
                "symbol": row['symbol'],
                "action": row['action'],
                "confidence": row['confidence'],
                "priority": row['priority'],
                "status": row['status'],
                "queued_at": row['queued_at'],
                "expires_at": row['expires_at'],
                "conditions": json.loads(row['conditions']),
                "retry_count": row['retry_count']
            })

        conn.close()

        return {
            "stats": stats,
            "signals": signals,
            "count": len(signals)
        }
    except Exception as e:
        logger.error(f"Error getting queue status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/account-states")
async def get_account_states(
    request: Optional[Request] = None,
    admin: bool = Depends(require_admin_user)
):
    """Get current account states - Admin only"""
    try:
        monitor = get_account_monitor()
        states = monitor.get_current_states()

        result = {}
        for executor_id, state in states.items():
            result[executor_id] = {
                "executor_id": state.executor_id,
                "buying_power": state.buying_power,
                "cash": state.cash,
                "portfolio_value": state.portfolio_value,
                "positions_count": state.positions_count,
                "timestamp": state.timestamp
            }

        return result
    except Exception as e:
        logger.error(f"Error getting account states: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recent-activity")
async def get_recent_activity(
    limit: int = 50,
    request: Optional[Request] = None,
    admin: bool = Depends(require_admin_user)
):
    """Get recent execution activity - Admin only"""
    try:
        queue = get_signal_queue()
        conn = sqlite3.connect(str(queue.db_path), timeout=10.0)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM signal_queue
            WHERE status IN ('executed', 'ready', 'expired')
            ORDER BY queued_at DESC
            LIMIT ?
        ''', (limit,))

        activities = []
        for row in cursor.fetchall():
            activities.append({
                "signal_id": row['signal_id'],
                "symbol": row['symbol'],
                "action": row['action'],
                "status": row['status'],
                "timestamp": row['executed_at'] or row['queued_at'],
                "confidence": row['confidence']
            })

        conn.close()
        return {"activities": activities, "count": len(activities)}
    except Exception as e:
        logger.error(f"Error getting recent activity: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/rejection-reasons")
async def get_rejection_reasons(
    hours: int = 24,
    request: Optional[Request] = None,
    admin: bool = Depends(require_admin_user)
):
    """Get rejection reasons analysis - Admin only"""
    try:
        queue = get_signal_queue()
        conn = sqlite3.connect(str(queue.db_path), timeout=10.0)
        cursor = conn.cursor()

        cutoff_time = (datetime.now() - timedelta(hours=hours)).isoformat()
        cursor.execute('''
            SELECT execution_error, COUNT(*) as count
            FROM signal_queue
            WHERE execution_error IS NOT NULL
              AND queued_at > ?
            GROUP BY execution_error
            ORDER BY count DESC
        ''', (cutoff_time,))

        reasons = {}
        for row in cursor.fetchall():
            error = row[0] or "Unknown"
            count = row[1]
            reasons[error] = count

        conn.close()
        return {"reasons": reasons, "hours": hours, "timestamp": datetime.now().isoformat()}
    except Exception as e:
        logger.error(f"Error getting rejection reasons: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard")
async def get_dashboard(
    request: Optional[Request] = None,
    admin: bool = Depends(require_admin_user)
):
    """Get HTML dashboard - Admin only"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Execution Dashboard - Admin Only</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: #0a0a0a;
                color: #e0e0e0;
                margin: 0;
                padding: 20px;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            h1 {
                color: #00ffff;
                border-bottom: 2px solid #00ffff;
                padding-bottom: 10px;
            }
            .stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin: 20px 0;
            }
            .stat-card {
                background: #1a1a1a;
                border: 1px solid #333;
                border-radius: 8px;
                padding: 20px;
            }
            .stat-value {
                font-size: 2em;
                font-weight: bold;
                color: #00ffff;
            }
            .stat-label {
                color: #888;
                margin-top: 5px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Execution Dashboard</h1>
            <p>Admin access verified. Dashboard data loading...</p>
            <div class="stats" id="stats"></div>
        </div>
        <script>
            async function loadDashboard() {
                try {
                    const [metrics, queue, accounts] = await Promise.all([
                        fetch('/api/v1/execution/metrics').then(r => r.json()),
                        fetch('/api/v1/execution/queue').then(r => r.json()),
                        fetch('/api/v1/execution/account-states').then(r => r.json())
                    ]);

                    const statsDiv = document.getElementById('stats');
                    statsDiv.innerHTML = `
                        <div class="stat-card">
                            <div class="stat-value">${metrics.execution_rate}%</div>
                            <div class="stat-label">Execution Rate</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">${queue.stats.pending}</div>
                            <div class="stat-label">Pending Signals</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">${queue.stats.ready}</div>
                            <div class="stat-label">Ready Signals</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">${Object.keys(accounts).length}</div>
                            <div class="stat-label">Active Executors</div>
                        </div>
                    `;
                } catch (error) {
                    console.error('Error loading dashboard:', error);
                }
            }
            loadDashboard();
            setInterval(loadDashboard, 5000);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

"""
Win Rate Validation API Endpoints
"""

from fastapi import APIRouter, Query, HTTPException, Header
from typing import Optional
from pydantic import BaseModel

from argo.validation.win_rate_validator import (
    WinRateValidator,
    ValidationMethodology
)
from argo.validation.reconciliation import ReconciliationSystem
from argo.validation.data_quality import DataQualityValidator
from argo.validation.signal_lifecycle import SignalLifecycleTracker

try:
    from argo.tracking.unified_tracker import UnifiedPerformanceTracker
    from argo.core.signal_tracker import SignalTracker
except ImportError:
    UnifiedPerformanceTracker = None
    SignalTracker = None

router = APIRouter(prefix="/api/v1/validation", tags=["validation"])


class ValidationResponse(BaseModel):
    """Validation response model"""
    overall_win_rate: float
    period: str
    total_trades: int
    completed_trades: int
    wins: int
    losses: int
    breakdown: dict
    statistics: Optional[dict] = None
    performance_metrics: dict
    verification: dict
    methodology: dict


@router.get("/win-rate", response_model=ValidationResponse)
async def get_win_rate_validation(
    period_days: int = Query(30, ge=1, le=365, description="Period in days"),
    methodology: str = Query("completed_trades", description="Validation methodology"),
    min_confidence: Optional[float] = Query(None, ge=0, le=100, description="Minimum confidence threshold"),
    asset_class: Optional[str] = Query(None, description="Filter by asset class"),
    format: str = Query("json", regex="^(json|markdown)$", description="Output format")
):
    """
    Get comprehensive win rate validation report
    
    **Methodologies:**
    - `completed_trades`: Only closed trades (default)
    - `all_signals`: All signals including pending
    - `confidence_weighted`: Weighted by confidence
    - `time_weighted`: Weighted by holding period
    - `regime_based`: By market regime
    
    **Example Request:**
    ```bash
    curl -X GET "http://localhost:8000/api/v1/validation/win-rate?period=30&methodology=completed_trades"
    ```
    """
    try:
        method = ValidationMethodology(methodology)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid methodology. Must be one of: {[m.value for m in ValidationMethodology]}"
        )
    
    validator = WinRateValidator()
    report = validator.validate_win_rate(
        period_days=period_days,
        methodology=method,
        min_confidence=min_confidence,
        asset_class=asset_class,
        include_statistics=True
    )
    
    if format == "markdown":
        from dataclasses import asdict
        report_dict = asdict(report)
        markdown = validator._format_markdown(validator.generate_investor_report(period_days))
        return {"markdown": markdown, "report": report_dict}
    
    from dataclasses import asdict
    report_dict = asdict(report)
    
    return ValidationResponse(
        overall_win_rate=report.overall_win_rate,
        period=f"{period_days}d",
        total_trades=report.total_signals,
        completed_trades=report.completed_trades,
        wins=report.wins,
        losses=report.losses,
        breakdown=asdict(report.breakdown),
        statistics=asdict(report.statistics) if report.statistics else None,
        performance_metrics={
            "total_pnl_dollars": report.total_pnl_dollars,
            "total_pnl_percent": report.total_pnl_percent,
            "avg_win_pct": report.avg_win_pct,
            "avg_loss_pct": report.avg_loss_pct,
            "profit_factor": report.profit_factor,
            "sharpe_ratio": report.sharpe_ratio,
            "max_drawdown": report.max_drawdown
        },
        verification={
            "all_verified": report.all_verified,
            "master_hash": report.master_hash,
            "verification_timestamp": report.verification_timestamp
        },
        methodology={
            "methodology": report.methodology,
            "notes": report.methodology_notes,
            "exclusions": report.exclusions,
            "assumptions": report.assumptions
        }
    )


@router.get("/investor-report")
async def get_investor_report(
    period_days: int = Query(30, ge=1, le=365, description="Period in days"),
    format: str = Query("json", regex="^(json|markdown|pdf)$", description="Output format")
):
    """
    Get investor-ready validation report
    
    **Example Request:**
    ```bash
    curl -X GET "http://localhost:8000/api/v1/validation/investor-report?period=30&format=markdown"
    ```
    """
    validator = WinRateValidator()
    report = validator.generate_investor_report(period_days=period_days, output_format=format)
    
    return report


@router.get("/signal-conversion")
async def get_signal_conversion_stats(
    period_days: int = Query(30, ge=1, le=365, description="Period in days")
):
    """
    Get signal-to-trade conversion statistics
    
    **Example Request:**
    ```bash
    curl -X GET "http://localhost:8000/api/v1/validation/signal-conversion?period=30"
    ```
    """
    tracker = SignalLifecycleTracker()
    stats = tracker.get_conversion_stats(period_days=period_days)
    
    return stats


@router.get("/reconciliation")
async def get_reconciliation_report(
    period_days: int = Query(30, ge=1, le=365, description="Period in days"),
    auto_fix: bool = Query(False, description="Automatically fix issues")
):
    """
    Get reconciliation report comparing trades with Alpaca records
    
    **Example Request:**
    ```bash
    curl -X GET "http://localhost:8000/api/v1/validation/reconciliation?period=30"
    ```
    """
    if not UnifiedPerformanceTracker:
        raise HTTPException(status_code=503, detail="Performance tracker not available")
    
    tracker = UnifiedPerformanceTracker()
    # Note: trading_engine would need to be passed in production
    reconciliation = ReconciliationSystem(tracker, trading_engine=None)
    
    report = reconciliation.get_reconciliation_report(period_days=period_days)
    
    return report


@router.get("/data-quality")
async def get_data_quality_report(
    period_days: int = Query(30, ge=1, le=365, description="Period in days"),
    auto_fix: bool = Query(False, description="Automatically fix issues")
):
    """
    Get data quality validation report
    
    **Example Request:**
    ```bash
    curl -X GET "http://localhost:8000/api/v1/validation/data-quality?period=30"
    ```
    """
    if not UnifiedPerformanceTracker:
        raise HTTPException(status_code=503, detail="Performance tracker not available")
    
    tracker = UnifiedPerformanceTracker()
    validator = DataQualityValidator(tracker)
    
    report = validator.get_quality_report(period_days=period_days)
    
    return report


@router.post("/reconcile")
async def run_reconciliation(
    period_days: int = Query(30, ge=1, le=365),
    auto_fix: bool = Query(False)
):
    """
    Run reconciliation and optionally fix issues
    
    **Example Request:**
    ```bash
    curl -X POST "http://localhost:8000/api/v1/validation/reconcile?period=30&auto_fix=false"
    ```
    """
    if not UnifiedPerformanceTracker:
        raise HTTPException(status_code=503, detail="Performance tracker not available")
    
    tracker = UnifiedPerformanceTracker()
    reconciliation = ReconciliationSystem(tracker, trading_engine=None)
    
    result = reconciliation.reconcile_trades(period_days=period_days, auto_fix=auto_fix)
    
    from dataclasses import asdict
    return asdict(result)


@router.post("/validate-quality")
async def run_quality_validation(
    period_days: int = Query(30, ge=1, le=365),
    auto_fix: bool = Query(False)
):
    """
    Run data quality validation and optionally fix issues
    
    **Example Request:**
    ```bash
    curl -X POST "http://localhost:8000/api/v1/validation/validate-quality?period=30&auto_fix=false"
    ```
    """
    if not UnifiedPerformanceTracker:
        raise HTTPException(status_code=503, detail="Performance tracker not available")
    
    tracker = UnifiedPerformanceTracker()
    validator = DataQualityValidator(tracker)
    
    result = validator.validate_data_quality(period_days=period_days, auto_fix=auto_fix)
    
    from dataclasses import asdict
    return asdict(result)

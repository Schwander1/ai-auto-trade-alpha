"""
Reconciliation System
Verifies trade data against Alpaca broker records
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from argo.tracking.unified_tracker import UnifiedPerformanceTracker, Trade

logger = logging.getLogger(__name__)


@dataclass
class ReconciliationIssue:
    """Represents a reconciliation issue"""
    trade_id: str
    issue_type: str  # missing_order, price_mismatch, quantity_mismatch, status_mismatch
    severity: str  # critical, warning, info
    description: str
    expected_value: Optional[any] = None
    actual_value: Optional[any] = None
    alpaca_order_id: Optional[str] = None


@dataclass
class ReconciliationResult:
    """Result of reconciliation process"""
    total_trades: int
    verified_trades: int
    issues: List[ReconciliationIssue]
    reconciliation_timestamp: str
    success_rate: float


class ReconciliationSystem:
    """
    Reconciles trade data with Alpaca broker records
    """
    
    def __init__(
        self,
        performance_tracker: UnifiedPerformanceTracker,
        trading_engine=None
    ):
        self.performance_tracker = performance_tracker
        self.trading_engine = trading_engine
    
    def reconcile_trades(
        self,
        period_days: int = 30,
        auto_fix: bool = False
    ) -> ReconciliationResult:
        """
        Reconcile trades with Alpaca records
        
        Args:
            period_days: Number of days to reconcile
            auto_fix: Whether to automatically fix issues
        
        Returns:
            ReconciliationResult with issues found
        """
        trades = self.performance_tracker._get_recent_trades(days=period_days)
        issues = []
        verified_count = 0
        
        for trade in trades:
            if not trade.alpaca_order_id:
                issues.append(ReconciliationIssue(
                    trade_id=trade.id,
                    issue_type="missing_order_id",
                    severity="warning",
                    description="Trade has no Alpaca order ID"
                ))
                continue
            
            # Verify with Alpaca if trading engine available
            if self.trading_engine:
                order_status = self._get_order_status(trade.alpaca_order_id)
                
                if not order_status:
                    issues.append(ReconciliationIssue(
                        trade_id=trade.id,
                        issue_type="missing_order",
                        severity="critical",
                        description=f"Order {trade.alpaca_order_id} not found in Alpaca",
                        alpaca_order_id=trade.alpaca_order_id
                    ))
                    continue
                
                # Verify order details
                trade_issues = self._verify_order_details(trade, order_status)
                issues.extend(trade_issues)
                
                if not trade_issues:
                    verified_count += 1
                
                # Auto-fix if enabled
                if auto_fix and trade_issues:
                    self._auto_fix_issues(trade, trade_issues, order_status)
            else:
                # No trading engine, can't verify
                issues.append(ReconciliationIssue(
                    trade_id=trade.id,
                    issue_type="no_trading_engine",
                    severity="info",
                    description="Trading engine not available for verification"
                ))
        
        success_rate = (verified_count / len(trades) * 100) if trades else 0
        
        return ReconciliationResult(
            total_trades=len(trades),
            verified_trades=verified_count,
            issues=issues,
            reconciliation_timestamp=datetime.utcnow().isoformat(),
            success_rate=round(success_rate, 2)
        )
    
    def _get_order_status(self, order_id: str) -> Optional[Dict]:
        """Get order status from trading engine"""
        if not self.trading_engine:
            return None
        
        try:
            return self.trading_engine.get_order_status(order_id)
        except Exception as e:
            logger.warning(f"Error getting order status for {order_id}: {e}")
            return None
    
    def _verify_order_details(
        self,
        trade: Trade,
        order_status: Dict
    ) -> List[ReconciliationIssue]:
        """Verify trade details against order status"""
        issues = []
        
        # Verify symbol
        if order_status.get('symbol') != trade.symbol:
            issues.append(ReconciliationIssue(
                trade_id=trade.id,
                issue_type="symbol_mismatch",
                severity="critical",
                description=f"Symbol mismatch: expected {trade.symbol}, got {order_status.get('symbol')}",
                expected_value=trade.symbol,
                actual_value=order_status.get('symbol'),
                alpaca_order_id=trade.alpaca_order_id
            ))
        
        # Verify quantity (allow small differences for partial fills)
        order_qty = order_status.get('filled_qty') or order_status.get('qty', 0)
        if abs(order_qty - trade.quantity) > 0.01:  # Allow 0.01 difference
            issues.append(ReconciliationIssue(
                trade_id=trade.id,
                issue_type="quantity_mismatch",
                severity="warning",
                description=f"Quantity mismatch: expected {trade.quantity}, got {order_qty}",
                expected_value=trade.quantity,
                actual_value=order_qty,
                alpaca_order_id=trade.alpaca_order_id
            ))
        
        # Verify entry price (allow small slippage)
        filled_price = order_status.get('filled_avg_price')
        if filled_price and trade.actual_entry_price:
            price_diff = abs(filled_price - trade.actual_entry_price)
            price_diff_pct = (price_diff / trade.actual_entry_price) * 100
            
            # Allow up to 1% difference (slippage)
            if price_diff_pct > 1.0:
                issues.append(ReconciliationIssue(
                    trade_id=trade.id,
                    issue_type="price_mismatch",
                    severity="warning",
                    description=f"Entry price mismatch: expected {trade.actual_entry_price}, got {filled_price} ({price_diff_pct:.2f}% difference)",
                    expected_value=trade.actual_entry_price,
                    actual_value=filled_price,
                    alpaca_order_id=trade.alpaca_order_id
                ))
        
        # Verify order status
        order_status_str = order_status.get('status', '').lower()
        if order_status_str in ['rejected', 'canceled', 'expired']:
            issues.append(ReconciliationIssue(
                trade_id=trade.id,
                issue_type="status_mismatch",
                severity="critical",
                description=f"Order status is {order_status_str} but trade is recorded as executed",
                expected_value="filled",
                actual_value=order_status_str,
                alpaca_order_id=trade.alpaca_order_id
            ))
        
        return issues
    
    def _auto_fix_issues(
        self,
        trade: Trade,
        issues: List[ReconciliationIssue],
        order_status: Dict
    ):
        """Automatically fix reconciliation issues"""
        for issue in issues:
            if issue.issue_type == "quantity_mismatch" and issue.actual_value:
                # Update quantity
                trade.quantity = issue.actual_value
                trade.filled_qty = issue.actual_value
                trade.partial_fill = issue.actual_value < trade.quantity
            
            elif issue.issue_type == "price_mismatch" and issue.actual_value:
                # Update entry price
                old_price = trade.actual_entry_price
                trade.actual_entry_price = issue.actual_value
                trade.entry_price = issue.actual_value
                
                # Recalculate slippage
                if trade.signal_entry_price:
                    trade.slippage_entry = trade.actual_entry_price - trade.signal_entry_price
                    trade.slippage_entry_pct = ((trade.actual_entry_price - trade.signal_entry_price) / trade.signal_entry_price) * 100
                
                # Recalculate P&L if trade is closed
                if trade.exit_price:
                    if trade.signal_type == "long":
                        trade.pnl_dollars = (trade.actual_exit_price - trade.actual_entry_price) * trade.quantity
                        trade.pnl_percent = ((trade.actual_exit_price - trade.actual_entry_price) / trade.actual_entry_price) * 100
                    else:
                        trade.pnl_dollars = (trade.actual_entry_price - trade.actual_exit_price) * trade.quantity
                        trade.pnl_percent = ((trade.actual_entry_price - trade.actual_exit_price) / trade.actual_entry_price) * 100
                    
                    trade.outcome = "win" if trade.pnl_dollars > 0 else "loss"
            
            elif issue.issue_type == "status_mismatch":
                # Mark trade as cancelled/rejected
                if issue.actual_value in ['rejected', 'canceled', 'expired']:
                    trade.cancelled = True
                    trade.outcome = "pending"
                    if issue.actual_value == 'rejected':
                        trade.rejection_reason = order_status.get('reject_reason', 'Unknown')
        
        # Save updated trade
        self.performance_tracker._store_trade(trade)
    
    def get_reconciliation_report(
        self,
        period_days: int = 30
    ) -> Dict:
        """Get reconciliation report"""
        result = self.reconcile_trades(period_days=period_days)
        
        # Group issues by type
        issues_by_type = {}
        for issue in result.issues:
            if issue.issue_type not in issues_by_type:
                issues_by_type[issue.issue_type] = []
            issues_by_type[issue.issue_type].append(issue)
        
        # Group issues by severity
        critical_issues = [i for i in result.issues if i.severity == "critical"]
        warning_issues = [i for i in result.issues if i.severity == "warning"]
        info_issues = [i for i in result.issues if i.severity == "info"]
        
        return {
            "reconciliation_timestamp": result.reconciliation_timestamp,
            "total_trades": result.total_trades,
            "verified_trades": result.verified_trades,
            "success_rate": result.success_rate,
            "issues_summary": {
                "total": len(result.issues),
                "critical": len(critical_issues),
                "warning": len(warning_issues),
                "info": len(info_issues)
            },
            "issues_by_type": {
                issue_type: len(issues)
                for issue_type, issues in issues_by_type.items()
            },
            "critical_issues": [
                {
                    "trade_id": i.trade_id,
                    "description": i.description,
                    "alpaca_order_id": i.alpaca_order_id
                }
                for i in critical_issues
            ],
            "all_issues": [
                {
                    "trade_id": i.trade_id,
                    "issue_type": i.issue_type,
                    "severity": i.severity,
                    "description": i.description,
                    "expected_value": i.expected_value,
                    "actual_value": i.actual_value
                }
                for i in result.issues
            ]
        }


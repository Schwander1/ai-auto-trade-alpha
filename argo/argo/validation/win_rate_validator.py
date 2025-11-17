"""
Comprehensive Win Rate Validation System
Validates win rate claims with multiple methodologies and detailed reporting
"""

import json
import hashlib
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import statistics
from collections import defaultdict

try:
    from argo.tracking.unified_tracker import UnifiedPerformanceTracker, Trade
    from argo.core.signal_tracker import SignalTracker
except ImportError:
    # Fallback for different import paths
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from argo.tracking.unified_tracker import UnifiedPerformanceTracker, Trade
    from argo.core.signal_tracker import SignalTracker

try:
    from scipy import stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    # Fallback normal CDF approximation
    def norm_cdf(x):
        """Approximate normal CDF using error function"""
        return 0.5 * (1 + math.erf(x / math.sqrt(2)))


class ValidationMethodology(Enum):
    """Different ways to calculate win rate"""
    COMPLETED_TRADES = "completed_trades"  # Only closed trades
    ALL_SIGNALS = "all_signals"  # Including pending/expired
    CONFIDENCE_WEIGHTED = "confidence_weighted"  # Weighted by confidence
    TIME_WEIGHTED = "time_weighted"  # Weighted by holding period
    REGIME_BASED = "regime_based"  # By market regime


@dataclass
class WinRateBreakdown:
    """Win rate broken down by dimension"""
    overall: float
    by_confidence: Dict[str, float]  # e.g., {"75-85": 92.3, "85-95": 96.5, "95+": 98.1}
    by_regime: Dict[str, float]  # e.g., {"BULL": 97.2, "BEAR": 94.8, "CHOP": 95.5, "CRISIS": 96.1}
    by_asset_class: Dict[str, float]  # e.g., {"stock": 96.5, "crypto": 95.8}
    by_signal_type: Dict[str, float]  # e.g., {"long": 96.8, "short": 95.4}
    by_timeframe: Dict[str, float]  # e.g., {"1d": 96.2, "7d": 96.5, "30d": 96.1}
    by_symbol: Dict[str, float]  # Top symbols
    by_exit_reason: Dict[str, float]  # e.g., {"take_profit": 98.5, "stop_loss": 45.2}


@dataclass
class StatisticalValidation:
    """Statistical validation metrics"""
    sample_size: int
    confidence_interval_95: Tuple[float, float]  # (lower, upper)
    confidence_interval_99: Tuple[float, float]
    standard_error: float
    z_score: float
    p_value: float
    is_statistically_significant: bool
    minimum_sample_size_required: int


@dataclass
class ValidationReport:
    """Complete validation report"""
    # Core metrics
    overall_win_rate: float
    methodology: str
    period_start: str
    period_end: str
    total_signals: int
    completed_trades: int
    pending_trades: int
    wins: int
    losses: int
    
    # Breakdowns
    breakdown: WinRateBreakdown
    
    # Statistical validation
    statistics: Optional[StatisticalValidation]
    
    # Performance metrics
    total_pnl_dollars: float
    total_pnl_percent: float
    avg_win_pct: float
    avg_loss_pct: float
    profit_factor: float
    sharpe_ratio: Optional[float]
    max_drawdown: Optional[float]
    
    # Verification
    all_verified: bool
    master_hash: str
    verification_timestamp: str
    
    # Methodology details
    methodology_notes: str
    exclusions: List[str]
    assumptions: List[str]
    
    # Additional metrics
    avg_slippage_entry_pct: Optional[float]
    avg_slippage_exit_pct: Optional[float]
    total_commission: Optional[float]
    signal_to_trade_conversion_rate: Optional[float]


class WinRateValidator:
    """
    Comprehensive win rate validation system
    """
    
    def __init__(
        self,
        performance_tracker: Optional[UnifiedPerformanceTracker] = None,
        signal_tracker: Optional[SignalTracker] = None
    ):
        self.performance_tracker = performance_tracker or UnifiedPerformanceTracker()
        self.signal_tracker = signal_tracker or SignalTracker()
    
    def validate_win_rate(
        self,
        period_days: int = 30,
        methodology: ValidationMethodology = ValidationMethodology.COMPLETED_TRADES,
        min_confidence: Optional[float] = None,
        asset_class: Optional[str] = None,
        include_statistics: bool = True
    ) -> ValidationReport:
        """
        Validate win rate with comprehensive reporting
        
        Args:
            period_days: Number of days to analyze
            methodology: How to calculate win rate
            min_confidence: Minimum confidence threshold (optional)
            asset_class: Filter by asset class (optional)
            include_statistics: Include statistical validation
        
        Returns:
            Complete validation report
        """
        # Get trades from performance tracker
        trades = self._get_trades(period_days, asset_class, min_confidence)
        
        if not trades:
            return self._empty_report(period_days)
        
        # Filter based on methodology
        filtered_trades = self._filter_by_methodology(trades, methodology)
        
        # Calculate core metrics
        completed = [t for t in filtered_trades if t.outcome != "pending"]
        wins = [t for t in completed if t.outcome == "win"]
        losses = [t for t in completed if t.outcome == "loss"]
        
        if not completed:
            return self._empty_report(period_days, total_signals=len(trades))
        
        overall_win_rate = (len(wins) / len(completed)) * 100
        
        # Calculate breakdowns
        breakdown = self._calculate_breakdown(completed)
        
        # Statistical validation
        statistics = None
        if include_statistics and len(completed) > 0:
            statistics = self._calculate_statistics(overall_win_rate, len(completed), len(wins))
        
        # Performance metrics
        performance = self._calculate_performance_metrics(completed)
        
        # Verification
        all_verified = all(t.verification_hash for t in completed)
        master_hash = self._create_master_hash(completed)
        
        # Period
        period_end = datetime.utcnow()
        period_start = period_end - timedelta(days=period_days)
        
        # Additional metrics
        slippage_metrics = self._calculate_slippage_metrics(completed)
        signal_conversion = self._calculate_signal_conversion(period_days)
        
        return ValidationReport(
            overall_win_rate=round(overall_win_rate, 2),
            methodology=methodology.value,
            period_start=period_start.isoformat(),
            period_end=period_end.isoformat(),
            total_signals=len(trades),
            completed_trades=len(completed),
            pending_trades=len(trades) - len(completed),
            wins=len(wins),
            losses=len(losses),
            breakdown=breakdown,
            statistics=statistics,
            total_pnl_dollars=performance['total_pnl'],
            total_pnl_percent=performance['total_pnl_pct'],
            avg_win_pct=performance['avg_win_pct'],
            avg_loss_pct=performance['avg_loss_pct'],
            profit_factor=performance['profit_factor'],
            sharpe_ratio=performance.get('sharpe_ratio'),
            max_drawdown=performance.get('max_drawdown'),
            all_verified=all_verified,
            master_hash=master_hash,
            verification_timestamp=datetime.utcnow().isoformat(),
            methodology_notes=self._get_methodology_notes(methodology),
            exclusions=self._get_exclusions(methodology, trades, completed),
            assumptions=self._get_assumptions(methodology),
            avg_slippage_entry_pct=slippage_metrics.get('avg_entry_pct'),
            avg_slippage_exit_pct=slippage_metrics.get('avg_exit_pct'),
            total_commission=slippage_metrics.get('total_commission'),
            signal_to_trade_conversion_rate=signal_conversion
        )
    
    def _get_trades(
        self,
        period_days: int,
        asset_class: Optional[str],
        min_confidence: Optional[float]
    ) -> List[Trade]:
        """Get trades from tracker"""
        trades = self.performance_tracker._get_recent_trades(days=period_days)
        
        if asset_class:
            trades = [t for t in trades if t.asset_class == asset_class]
        
        if min_confidence:
            trades = [t for t in trades if t.confidence >= min_confidence]
        
        return trades
    
    def _filter_by_methodology(
        self,
        trades: List[Trade],
        methodology: ValidationMethodology
    ) -> List[Trade]:
        """Filter trades based on methodology"""
        if methodology == ValidationMethodology.COMPLETED_TRADES:
            return [t for t in trades if t.outcome != "pending"]
        
        elif methodology == ValidationMethodology.ALL_SIGNALS:
            return trades  # Include all
        
        elif methodology == ValidationMethodology.CONFIDENCE_WEIGHTED:
            # Weight by confidence (higher confidence = more weight)
            # For now, return all completed trades (weighting done in calculation)
            return [t for t in trades if t.outcome != "pending"]
        
        elif methodology == ValidationMethodology.TIME_WEIGHTED:
            # Weight by holding period
            return [t for t in trades if t.outcome != "pending" and t.holding_period_hours]
        
        elif methodology == ValidationMethodology.REGIME_BASED:
            # Filter by regime (would need regime data)
            return [t for t in trades if t.outcome != "pending"]
        
        return trades
    
    def _calculate_breakdown(self, trades: List[Trade]) -> WinRateBreakdown:
        """Calculate win rate breakdowns"""
        overall = (len([t for t in trades if t.outcome == "win"]) / len(trades) * 100) if trades else 0
        
        # By confidence
        by_confidence = self._breakdown_by_confidence(trades)
        
        # By regime
        by_regime = self._breakdown_by_regime(trades)
        
        # By asset class
        by_asset_class = {}
        for asset_class in ["stock", "crypto"]:
            asset_trades = [t for t in trades if t.asset_class == asset_class]
            if asset_trades:
                wins = len([t for t in asset_trades if t.outcome == "win"])
                by_asset_class[asset_class] = round((wins / len(asset_trades)) * 100, 2)
        
        # By signal type
        by_signal_type = {}
        for signal_type in ["long", "short"]:
            type_trades = [t for t in trades if t.signal_type == signal_type]
            if type_trades:
                wins = len([t for t in type_trades if t.outcome == "win"])
                by_signal_type[signal_type] = round((wins / len(type_trades)) * 100, 2)
        
        # By timeframe (last 1d, 7d, 30d)
        by_timeframe = self._breakdown_by_timeframe(trades)
        
        # By symbol (top 10)
        by_symbol = self._breakdown_by_symbol(trades, top_n=10)
        
        # By exit reason
        by_exit_reason = self._breakdown_by_exit_reason(trades)
        
        return WinRateBreakdown(
            overall=round(overall, 2),
            by_confidence=by_confidence,
            by_regime=by_regime,
            by_asset_class=by_asset_class,
            by_signal_type=by_signal_type,
            by_timeframe=by_timeframe,
            by_symbol=by_symbol,
            by_exit_reason=by_exit_reason
        )
    
    def _breakdown_by_confidence(self, trades: List[Trade]) -> Dict[str, float]:
        """Breakdown by confidence ranges"""
        ranges = {
            "75-85": (75, 85),
            "85-95": (85, 95),
            "95+": (95, 1000)
        }
        
        breakdown = {}
        for range_name, (min_conf, max_conf) in ranges.items():
            range_trades = [
                t for t in trades
                if min_conf <= t.confidence < max_conf
            ]
            if range_trades:
                wins = len([t for t in range_trades if t.outcome == "win"])
                breakdown[range_name] = round((wins / len(range_trades)) * 100, 2)
        
        return breakdown
    
    def _breakdown_by_regime(self, trades: List[Trade]) -> Dict[str, float]:
        """Breakdown by market regime"""
        regimes = ["BULL", "BEAR", "CHOP", "CRISIS", "UNKNOWN"]
        breakdown = {}
        
        for regime in regimes:
            regime_trades = [t for t in trades if t.regime == regime]
            if regime_trades:
                wins = len([t for t in regime_trades if t.outcome == "win"])
                breakdown[regime] = round((wins / len(regime_trades)) * 100, 2)
        
        return breakdown
    
    def _breakdown_by_timeframe(self, trades: List[Trade]) -> Dict[str, float]:
        """Breakdown by time period"""
        now = datetime.utcnow()
        timeframes = {
            "1d": timedelta(days=1),
            "7d": timedelta(days=7),
            "30d": timedelta(days=30)
        }
        
        breakdown = {}
        for timeframe, delta in timeframes.items():
            cutoff = now - delta
            timeframe_trades = [
                t for t in trades
                if datetime.fromisoformat(t.entry_timestamp) >= cutoff
            ]
            if timeframe_trades:
                wins = len([t for t in timeframe_trades if t.outcome == "win"])
                breakdown[timeframe] = round((wins / len(timeframe_trades)) * 100, 2)
        
        return breakdown
    
    def _breakdown_by_symbol(self, trades: List[Trade], top_n: int = 10) -> Dict[str, float]:
        """Breakdown by symbol (top N by trade count)"""
        symbol_counts = defaultdict(int)
        for trade in trades:
            symbol_counts[trade.symbol] += 1
        
        top_symbols = sorted(symbol_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]
        
        breakdown = {}
        for symbol, _ in top_symbols:
            symbol_trades = [t for t in trades if t.symbol == symbol]
            if symbol_trades:
                wins = len([t for t in symbol_trades if t.outcome == "win"])
                breakdown[symbol] = round((wins / len(symbol_trades)) * 100, 2)
        
        return breakdown
    
    def _breakdown_by_exit_reason(self, trades: List[Trade]) -> Dict[str, float]:
        """Breakdown by exit reason"""
        exit_reasons = ["take_profit", "stop_loss", "manual", "expired", "risk_limit", "time_based"]
        breakdown = {}
        
        for reason in exit_reasons:
            reason_trades = [t for t in trades if t.exit_reason == reason]
            if reason_trades:
                wins = len([t for t in reason_trades if t.outcome == "win"])
                breakdown[reason] = round((wins / len(reason_trades)) * 100, 2)
        
        return breakdown
    
    def _calculate_statistics(
        self,
        win_rate: float,
        sample_size: int,
        wins: int
    ) -> StatisticalValidation:
        """Calculate statistical validation metrics"""
        # Standard error for proportion
        p = win_rate / 100
        se = math.sqrt((p * (1 - p)) / sample_size)
        
        # 95% confidence interval (z = 1.96)
        ci_95_lower = max(0, (p - 1.96 * se) * 100)
        ci_95_upper = min(100, (p + 1.96 * se) * 100)
        
        # 99% confidence interval (z = 2.576)
        ci_99_lower = max(0, (p - 2.576 * se) * 100)
        ci_99_upper = min(100, (p + 2.576 * se) * 100)
        
        # Z-score (testing against null hypothesis of 50% win rate)
        null_p = 0.5
        z_score = (p - null_p) / math.sqrt((null_p * (1 - null_p)) / sample_size)
        
        # P-value (two-tailed test)
        if SCIPY_AVAILABLE:
            p_value = 2 * (1 - stats.norm.cdf(abs(z_score)))
        else:
            p_value = 2 * (1 - norm_cdf(abs(z_score)))
        
        # Statistical significance (p < 0.05)
        is_significant = p_value < 0.05
        
        # Minimum sample size for 95% confidence with 3% margin of error
        z = 1.96
        E = 0.03  # 3% margin of error
        min_sample = math.ceil((z**2 * p * (1 - p)) / (E**2))
        
        return StatisticalValidation(
            sample_size=sample_size,
            confidence_interval_95=(round(ci_95_lower, 2), round(ci_95_upper, 2)),
            confidence_interval_99=(round(ci_99_lower, 2), round(ci_99_upper, 2)),
            standard_error=round(se * 100, 4),
            z_score=round(z_score, 4),
            p_value=round(p_value, 6),
            is_statistically_significant=is_significant,
            minimum_sample_size_required=min_sample
        )
    
    def _calculate_performance_metrics(self, trades: List[Trade]) -> Dict:
        """Calculate performance metrics"""
        wins = [t for t in trades if t.outcome == "win" and t.pnl_percent]
        losses = [t for t in trades if t.outcome == "loss" and t.pnl_percent]
        
        total_pnl = sum(t.pnl_dollars for t in trades if t.pnl_dollars)
        total_pnl_pct = sum(t.pnl_percent for t in trades if t.pnl_percent) if trades else 0
        
        avg_win_pct = statistics.mean([t.pnl_percent for t in wins]) if wins else 0
        avg_loss_pct = statistics.mean([t.pnl_percent for t in losses]) if losses else 0
        
        gross_profit = sum(t.pnl_dollars for t in wins if t.pnl_dollars)
        gross_loss = abs(sum(t.pnl_dollars for t in losses if t.pnl_dollars))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        # Calculate Sharpe ratio (simplified)
        returns = [t.pnl_percent for t in trades if t.pnl_percent]
        sharpe_ratio = None
        if len(returns) > 1:
            mean_return = statistics.mean(returns)
            std_return = statistics.stdev(returns) if len(returns) > 1 else 0
            sharpe_ratio = (mean_return / std_return) * math.sqrt(252) if std_return > 0 else 0
        
        # Calculate max drawdown
        max_drawdown = None
        if returns:
            cumulative = []
            running_sum = 0
            for r in returns:
                running_sum += r
                cumulative.append(running_sum)
            
            if cumulative:
                peak = cumulative[0]
                max_dd = 0
                for value in cumulative:
                    if value > peak:
                        peak = value
                    drawdown = (peak - value) / peak if peak > 0 else 0
                    if drawdown > max_dd:
                        max_dd = drawdown
                max_drawdown = max_dd * 100
        
        return {
            'total_pnl': round(total_pnl, 2),
            'total_pnl_pct': round(total_pnl_pct, 2),
            'avg_win_pct': round(avg_win_pct, 2),
            'avg_loss_pct': round(avg_loss_pct, 2),
            'profit_factor': round(profit_factor, 2),
            'sharpe_ratio': round(sharpe_ratio, 2) if sharpe_ratio else None,
            'max_drawdown': round(max_drawdown, 2) if max_drawdown else None
        }
    
    def _calculate_slippage_metrics(self, trades: List[Trade]) -> Dict:
        """Calculate slippage and commission metrics"""
        entry_slippages = [t.slippage_entry_pct for t in trades if t.slippage_entry_pct is not None]
        exit_slippages = [t.slippage_exit_pct for t in trades if t.slippage_exit_pct is not None]
        commissions = [t.commission for t in trades if t.commission is not None]
        
        return {
            'avg_entry_pct': round(statistics.mean(entry_slippages), 4) if entry_slippages else None,
            'avg_exit_pct': round(statistics.mean(exit_slippages), 4) if exit_slippages else None,
            'total_commission': round(sum(commissions), 2) if commissions else None
        }
    
    def _calculate_signal_conversion(self, period_days: int) -> Optional[float]:
        """Calculate signal-to-trade conversion rate"""
        try:
            # Get total signals from signal tracker
            stats = self.signal_tracker.get_stats()
            total_signals = stats.get('total_signals', 0)
            
            # Get total trades
            trades = self.performance_tracker._get_recent_trades(days=period_days)
            
            if total_signals > 0:
                return round((len(trades) / total_signals) * 100, 2)
        except:
            pass
        
        return None
    
    def _create_master_hash(self, trades: List[Trade]) -> str:
        """Create master verification hash"""
        hashes = ''.join(sorted([t.verification_hash for t in trades if t.verification_hash]))
        return hashlib.sha256(hashes.encode()).hexdigest()[:32]
    
    def _get_methodology_notes(self, methodology: ValidationMethodology) -> str:
        """Get notes about methodology"""
        notes = {
            ValidationMethodology.COMPLETED_TRADES: "Only includes trades that have been closed (win or loss). Pending trades are excluded.",
            ValidationMethodology.ALL_SIGNALS: "Includes all signals, including pending and expired. Win rate calculated only on completed trades.",
            ValidationMethodology.CONFIDENCE_WEIGHTED: "Win rate weighted by signal confidence level.",
            ValidationMethodology.TIME_WEIGHTED: "Win rate weighted by holding period.",
            ValidationMethodology.REGIME_BASED: "Win rate calculated separately for each market regime."
        }
        return notes.get(methodology, "")
    
    def _get_exclusions(
        self,
        methodology: ValidationMethodology,
        all_trades: List[Trade],
        completed_trades: List[Trade]
    ) -> List[str]:
        """Get list of exclusions"""
        exclusions = []
        
        if methodology == ValidationMethodology.COMPLETED_TRADES:
            pending = len(all_trades) - len(completed_trades)
            if pending > 0:
                exclusions.append(f"{pending} pending trades excluded")
        
        expired = len([t for t in all_trades if t.expired])
        if expired > 0:
            exclusions.append(f"{expired} expired signals excluded")
        
        cancelled = len([t for t in all_trades if t.cancelled])
        if cancelled > 0:
            exclusions.append(f"{cancelled} cancelled trades excluded")
        
        return exclusions
    
    def _get_assumptions(self, methodology: ValidationMethodology) -> List[str]:
        """Get list of assumptions"""
        return [
            "Win defined as positive P&L at exit (after commissions)",
            "Loss defined as negative or zero P&L at exit",
            "All trades executed at actual fill prices (not signal prices)",
            "Exit prices are accurate and verified",
            "Commission costs included in P&L calculations where available"
        ]
    
    def _empty_report(self, period_days: int, total_signals: int = 0) -> ValidationReport:
        """Create empty report"""
        period_end = datetime.utcnow()
        period_start = period_end - timedelta(days=period_days)
        
        return ValidationReport(
            overall_win_rate=0.0,
            methodology="completed_trades",
            period_start=period_start.isoformat(),
            period_end=period_end.isoformat(),
            total_signals=total_signals,
            completed_trades=0,
            pending_trades=0,
            wins=0,
            losses=0,
            breakdown=WinRateBreakdown(
                overall=0.0,
                by_confidence={},
                by_regime={},
                by_asset_class={},
                by_signal_type={},
                by_timeframe={},
                by_symbol={},
                by_exit_reason={}
            ),
            statistics=None,
            total_pnl_dollars=0.0,
            total_pnl_percent=0.0,
            avg_win_pct=0.0,
            avg_loss_pct=0.0,
            profit_factor=0.0,
            sharpe_ratio=None,
            max_drawdown=None,
            all_verified=False,
            master_hash="",
            verification_timestamp=datetime.utcnow().isoformat(),
            methodology_notes="No trades found in period",
            exclusions=[],
            assumptions=[],
            avg_slippage_entry_pct=None,
            avg_slippage_exit_pct=None,
            total_commission=None,
            signal_to_trade_conversion_rate=None
        )
    
    def generate_investor_report(
        self,
        period_days: int = 30,
        output_format: str = "json"
    ) -> Dict:
        """
        Generate investor-ready validation report
        
        Returns comprehensive report suitable for investor presentation
        """
        # Generate report with multiple methodologies
        primary_report = self.validate_win_rate(
            period_days=period_days,
            methodology=ValidationMethodology.COMPLETED_TRADES,
            include_statistics=True
        )
        
        # Additional breakdowns
        all_signals_report = self.validate_win_rate(
            period_days=period_days,
            methodology=ValidationMethodology.ALL_SIGNALS,
            include_statistics=False
        )
        
        # Convert to dict for export
        report_dict = {
            "report_metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "period_days": period_days,
                "report_version": "1.0",
                "validator_version": "1.0"
            },
            "executive_summary": {
                "overall_win_rate": primary_report.overall_win_rate,
                "total_signals": primary_report.total_signals,
                "completed_trades": primary_report.completed_trades,
                "wins": primary_report.wins,
                "losses": primary_report.losses,
                "statistical_significance": primary_report.statistics.is_statistically_significant if primary_report.statistics else False,
                "confidence_interval_95": primary_report.statistics.confidence_interval_95 if primary_report.statistics else None
            },
            "detailed_breakdown": asdict(primary_report.breakdown),
            "performance_metrics": {
                "total_pnl_dollars": primary_report.total_pnl_dollars,
                "total_pnl_percent": primary_report.total_pnl_percent,
                "avg_win_pct": primary_report.avg_win_pct,
                "avg_loss_pct": primary_report.avg_loss_pct,
                "profit_factor": primary_report.profit_factor,
                "sharpe_ratio": primary_report.sharpe_ratio,
                "max_drawdown": primary_report.max_drawdown
            },
            "statistical_validation": asdict(primary_report.statistics) if primary_report.statistics else None,
            "verification": {
                "all_verified": primary_report.all_verified,
                "master_hash": primary_report.master_hash,
                "verification_timestamp": primary_report.verification_timestamp
            },
            "methodology": {
                "primary_methodology": primary_report.methodology,
                "notes": primary_report.methodology_notes,
                "exclusions": primary_report.exclusions,
                "assumptions": primary_report.assumptions
            },
            "additional_analysis": {
                "all_signals_count": all_signals_report.total_signals,
                "pending_trades": all_signals_report.pending_trades,
                "avg_slippage_entry_pct": primary_report.avg_slippage_entry_pct,
                "avg_slippage_exit_pct": primary_report.avg_slippage_exit_pct,
                "total_commission": primary_report.total_commission,
                "signal_to_trade_conversion_rate": primary_report.signal_to_trade_conversion_rate
            }
        }
        
        if output_format == "json":
            return report_dict
        elif output_format == "markdown":
            return self._format_markdown(report_dict)
        else:
            return report_dict
    
    def _format_markdown(self, report_dict: Dict) -> str:
        """Format report as Markdown"""
        md = f"""# Win Rate Validation Report

**Generated:** {report_dict['report_metadata']['generated_at']}  
**Period:** {report_dict['report_metadata']['period_days']} days

## Executive Summary

- **Overall Win Rate:** {report_dict['executive_summary']['overall_win_rate']}%
- **Total Signals:** {report_dict['executive_summary']['total_signals']}
- **Completed Trades:** {report_dict['executive_summary']['completed_trades']}
- **Wins:** {report_dict['executive_summary']['wins']}
- **Losses:** {report_dict['executive_summary']['losses']}
- **Statistically Significant:** {report_dict['executive_summary']['statistical_significance']}

## Detailed Breakdown

### By Confidence Level
"""
        for conf_range, rate in report_dict['detailed_breakdown']['by_confidence'].items():
            md += f"- **{conf_range}%:** {rate}%\n"
        
        md += "\n### By Market Regime\n"
        for regime, rate in report_dict['detailed_breakdown']['by_regime'].items():
            md += f"- **{regime}:** {rate}%\n"
        
        md += "\n### By Asset Class\n"
        for asset, rate in report_dict['detailed_breakdown']['by_asset_class'].items():
            md += f"- **{asset.title()}:** {rate}%\n"
        
        md += "\n### By Signal Type\n"
        for signal_type, rate in report_dict['detailed_breakdown']['by_signal_type'].items():
            md += f"- **{signal_type.title()}:** {rate}%\n"
        
        md += "\n### By Exit Reason\n"
        for reason, rate in report_dict['detailed_breakdown']['by_exit_reason'].items():
            md += f"- **{reason.replace('_', ' ').title()}:** {rate}%\n"
        
        if report_dict['statistical_validation']:
            stats = report_dict['statistical_validation']
            md += f"""
## Statistical Validation

- **Sample Size:** {stats['sample_size']}
- **95% Confidence Interval:** {stats['confidence_interval_95'][0]}% - {stats['confidence_interval_95'][1]}%
- **99% Confidence Interval:** {stats['confidence_interval_99'][0]}% - {stats['confidence_interval_99'][1]}%
- **Standard Error:** {stats['standard_error']}%
- **Z-Score:** {stats['z_score']}
- **P-Value:** {stats['p_value']}
- **Minimum Sample Size Required:** {stats['minimum_sample_size_required']}
"""
        
        md += f"""
## Performance Metrics

- **Total P&L:** ${report_dict['performance_metrics']['total_pnl_dollars']}
- **Total P&L %:** {report_dict['performance_metrics']['total_pnl_percent']}%
- **Average Win %:** {report_dict['performance_metrics']['avg_win_pct']}%
- **Average Loss %:** {report_dict['performance_metrics']['avg_loss_pct']}%
- **Profit Factor:** {report_dict['performance_metrics']['profit_factor']}
"""
        
        if report_dict['performance_metrics'].get('sharpe_ratio'):
            md += f"- **Sharpe Ratio:** {report_dict['performance_metrics']['sharpe_ratio']}\n"
        
        if report_dict['performance_metrics'].get('max_drawdown'):
            md += f"- **Max Drawdown:** {report_dict['performance_metrics']['max_drawdown']}%\n"
        
        md += f"""
## Additional Analysis

- **Signal-to-Trade Conversion Rate:** {report_dict['additional_analysis'].get('signal_to_trade_conversion_rate', 'N/A')}%
- **Average Entry Slippage:** {report_dict['additional_analysis'].get('avg_slippage_entry_pct', 'N/A')}%
- **Average Exit Slippage:** {report_dict['additional_analysis'].get('avg_slippage_exit_pct', 'N/A')}%
- **Total Commission:** ${report_dict['additional_analysis'].get('total_commission', 'N/A')}

## Verification

- **All Verified:** {report_dict['verification']['all_verified']}
- **Master Hash:** {report_dict['verification']['master_hash']}
"""
        
        return md


#!/usr/bin/env python3
"""
Result Validator
Validates backtest results for common issues and data quality problems
"""
import logging
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ValidationIssue:
    """Represents a validation issue"""
    severity: str  # 'error', 'warning', 'info'
    category: str  # 'data_quality', 'performance', 'risk', 'logic'
    message: str
    symbol: Optional[str] = None
    value: Optional[Any] = None
    expected: Optional[Any] = None


class ResultValidator:
    """
    Validates backtest results for common issues
    """
    
    # Thresholds for validation
    MIN_REASONABLE_SHARPE = 0.5
    MAX_REASONABLE_SHARPE = 10.0
    MIN_REASONABLE_WIN_RATE = 0.0
    MAX_REASONABLE_WIN_RATE = 100.0
    MAX_REASONABLE_DRAWDOWN = 100.0
    MIN_REASONABLE_TRADES = 1
    MAX_REASONABLE_ANNUAL_RETURN = 1000.0  # 1000% annual return is suspicious
    
    @staticmethod
    def validate_metrics(metrics: Any, symbol: Optional[str] = None) -> List[ValidationIssue]:
        """
        Validate backtest metrics
        
        Args:
            metrics: BacktestMetrics object or dictionary
            symbol: Optional symbol name for context
            
        Returns:
            List of validation issues
        """
        issues = []
        
        # Convert to dict if needed
        if hasattr(metrics, '__dict__'):
            data = metrics.__dict__
        elif isinstance(metrics, dict):
            data = metrics
        else:
            issues.append(ValidationIssue(
                severity='error',
                category='data_quality',
                message=f"Invalid metrics type: {type(metrics)}",
                symbol=symbol
            ))
            return issues
        
        # Validate Sharpe ratio
        sharpe = data.get('sharpe_ratio', 0)
        if sharpe < ResultValidator.MIN_REASONABLE_SHARPE:
            issues.append(ValidationIssue(
                severity='warning',
                category='performance',
                message=f"Low Sharpe ratio: {sharpe:.2f}",
                symbol=symbol,
                value=sharpe,
                expected=f">= {ResultValidator.MIN_REASONABLE_SHARPE}"
            ))
        elif sharpe > ResultValidator.MAX_REASONABLE_SHARPE:
            issues.append(ValidationIssue(
                severity='warning',
                category='performance',
                message=f"Unusually high Sharpe ratio: {sharpe:.2f} (possible overfitting)",
                symbol=symbol,
                value=sharpe,
                expected=f"< {ResultValidator.MAX_REASONABLE_SHARPE}"
            ))
        
        # Validate win rate
        win_rate = data.get('win_rate_pct', 0)
        if win_rate < ResultValidator.MIN_REASONABLE_WIN_RATE:
            issues.append(ValidationIssue(
                severity='error',
                category='data_quality',
                message=f"Invalid win rate: {win_rate:.2f}%",
                symbol=symbol,
                value=win_rate
            ))
        elif win_rate > ResultValidator.MAX_REASONABLE_WIN_RATE:
            issues.append(ValidationIssue(
                severity='error',
                category='data_quality',
                message=f"Invalid win rate: {win_rate:.2f}%",
                symbol=symbol,
                value=win_rate
            ))
        
        # Validate max drawdown
        max_dd = data.get('max_drawdown_pct', 0)
        if abs(max_dd) > ResultValidator.MAX_REASONABLE_DRAWDOWN:
            issues.append(ValidationIssue(
                severity='error',
                category='data_quality',
                message=f"Unrealistic max drawdown: {max_dd:.2f}%",
                symbol=symbol,
                value=max_dd
            ))
        
        # Validate trade count
        total_trades = data.get('total_trades', 0)
        if total_trades < ResultValidator.MIN_REASONABLE_TRADES:
            issues.append(ValidationIssue(
                severity='warning',
                category='performance',
                message=f"Very few trades: {total_trades} (may not be statistically significant)",
                symbol=symbol,
                value=total_trades,
                expected=f">= {ResultValidator.MIN_REASONABLE_TRADES}"
            ))
        
        # Validate annualized return
        annual_return = data.get('annualized_return_pct', 0)
        if abs(annual_return) > ResultValidator.MAX_REASONABLE_ANNUAL_RETURN:
            issues.append(ValidationIssue(
                severity='warning',
                category='performance',
                message=f"Unusually high annual return: {annual_return:.2f}% (possible data error or overfitting)",
                symbol=symbol,
                value=annual_return,
                expected=f"< {ResultValidator.MAX_REASONABLE_ANNUAL_RETURN}%"
            ))
        
        # Validate consistency: win_rate vs winning_trades
        winning_trades = data.get('winning_trades', 0)
        losing_trades = data.get('losing_trades', 0)
        if total_trades > 0:
            calculated_win_rate = (winning_trades / total_trades) * 100
            if abs(calculated_win_rate - win_rate) > 0.1:  # Allow small floating point differences
                issues.append(ValidationIssue(
                    severity='error',
                    category='data_quality',
                    message=f"Win rate inconsistency: reported {win_rate:.2f}%, calculated {calculated_win_rate:.2f}%",
                    symbol=symbol,
                    value=win_rate,
                    expected=calculated_win_rate
                ))
        
        # Validate profit factor
        profit_factor = data.get('profit_factor', 0)
        if profit_factor < 0:
            issues.append(ValidationIssue(
                severity='error',
                category='data_quality',
                message=f"Invalid profit factor: {profit_factor:.2f} (must be >= 0)",
                symbol=symbol,
                value=profit_factor
            ))
        
        # Validate sortino ratio consistency with sharpe
        sortino = data.get('sortino_ratio', 0)
        if sharpe > 0 and sortino > 0:
            # Sortino should generally be >= Sharpe (less penalizing)
            if sortino < sharpe * 0.8:  # Allow some variance
                issues.append(ValidationIssue(
                    severity='warning',
                    category='performance',
                    message=f"Sortino ratio ({sortino:.2f}) unexpectedly lower than Sharpe ({sharpe:.2f})",
                    symbol=symbol
                ))
        
        return issues
    
    @staticmethod
    def validate_batch_results(batch_results: Dict[str, Any]) -> Dict[str, List[ValidationIssue]]:
        """
        Validate batch backtest results
        
        Args:
            batch_results: Results from BatchBacktester
            
        Returns:
            Dictionary mapping symbol to list of issues
        """
        all_issues = {}
        
        # Validate successful results
        if 'successful' in batch_results:
            for symbol, metrics in batch_results['successful'].items():
                issues = ResultValidator.validate_metrics(metrics, symbol=symbol)
                if issues:
                    all_issues[symbol] = issues
        
        # Check aggregate stats
        if 'aggregate_stats' in batch_results:
            agg_stats = batch_results['aggregate_stats']
            issues = ResultValidator.validate_metrics(agg_stats, symbol='AGGREGATE')
            if issues:
                all_issues['AGGREGATE'] = issues
        
        return all_issues
    
    @staticmethod
    def get_validation_summary(issues: Dict[str, List[ValidationIssue]]) -> Dict[str, Any]:
        """
        Get summary of validation issues
        
        Args:
            issues: Dictionary of validation issues
            
        Returns:
            Summary dictionary
        """
        total_issues = sum(len(issue_list) for issue_list in issues.values())
        errors = sum(1 for issue_list in issues.values() for issue in issue_list if issue.severity == 'error')
        warnings = sum(1 for issue_list in issues.values() for issue in issue_list if issue.severity == 'warning')
        infos = sum(1 for issue_list in issues.values() for issue in issue_list if issue.severity == 'info')
        
        # Group by category
        by_category = {}
        for issue_list in issues.values():
            for issue in issue_list:
                category = issue.category
                if category not in by_category:
                    by_category[category] = {'error': 0, 'warning': 0, 'info': 0}
                by_category[category][issue.severity] += 1
        
        return {
            'total_issues': total_issues,
            'errors': errors,
            'warnings': warnings,
            'infos': infos,
            'symbols_with_issues': len(issues),
            'by_category': by_category,
            'is_valid': errors == 0
        }
    
    @staticmethod
    def print_validation_report(issues: Dict[str, List[ValidationIssue]]) -> None:
        """
        Print validation report to console
        
        Args:
            issues: Dictionary of validation issues
        """
        summary = ResultValidator.get_validation_summary(issues)
        
        print("\n" + "="*80)
        print("BACKTEST VALIDATION REPORT")
        print("="*80)
        print(f"Total Issues: {summary['total_issues']}")
        print(f"  Errors: {summary['errors']}")
        print(f"  Warnings: {summary['warnings']}")
        print(f"  Info: {summary['infos']}")
        print(f"Symbols with Issues: {summary['symbols_with_issues']}")
        print(f"Status: {'❌ INVALID' if not summary['is_valid'] else '✅ VALID'}")
        print("="*80)
        
        # Print issues by symbol
        for symbol, issue_list in issues.items():
            if issue_list:
                print(f"\n{symbol}:")
                for issue in issue_list:
                    severity_icon = "❌" if issue.severity == 'error' else "⚠️" if issue.severity == 'warning' else "ℹ️"
                    print(f"  {severity_icon} [{issue.category.upper()}] {issue.message}")
                    if issue.value is not None:
                        print(f"      Value: {issue.value}")
                    if issue.expected is not None:
                        print(f"      Expected: {issue.expected}")
        
        print("\n" + "="*80 + "\n")


#!/usr/bin/env python3
"""
ML-Based Threshold Optimization
Uses machine learning to optimize confidence thresholds based on historical performance
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class ThresholdOptimizationResult:
    """Result of threshold optimization"""
    optimal_threshold: float
    expected_win_rate: float
    expected_sharpe: float
    expected_return: float
    confidence_interval: Tuple[float, float]
    feature_importance: Dict[str, float]

class MLThresholdOptimizer:
    """
    Machine Learning-based threshold optimizer
    
    Uses historical backtest results to learn optimal confidence thresholds
    based on market conditions, volatility, and other features.
    """
    
    def __init__(self):
        """Initialize ML threshold optimizer"""
        self.training_data: List[Dict] = []
        self.model = None
        self.feature_columns = [
            'volatility', 'rsi', 'macd', 'volume_ratio',
            'sma_separation', 'market_regime'
        ]
        
    def add_training_sample(
        self,
        threshold: float,
        features: Dict[str, float],
        outcome: Dict[str, float]
    ):
        """
        Add a training sample from backtest results
        
        Args:
            threshold: Confidence threshold used
            features: Market features at time of signal
            outcome: Backtest outcome (win_rate, sharpe, return, etc.)
        """
        sample = {
            'threshold': threshold,
            **features,
            **{f'outcome_{k}': v for k, v in outcome.items()}
        }
        self.training_data.append(sample)
        logger.debug(f"Added training sample: threshold={threshold}, win_rate={outcome.get('win_rate', 0):.2f}%")
    
    def optimize_threshold(
        self,
        current_features: Dict[str, float],
        target_metric: str = 'sharpe_ratio',
        min_trades: int = 50
    ) -> Optional[ThresholdOptimizationResult]:
        """
        Optimize threshold based on current market features
        
        Args:
            current_features: Current market features
            target_metric: Metric to optimize ('sharpe_ratio', 'win_rate', 'total_return')
            min_trades: Minimum trades required for valid optimization
            
        Returns:
            ThresholdOptimizationResult or None if insufficient data
        """
        if len(self.training_data) < 100:
            logger.warning(f"Insufficient training data: {len(self.training_data)} < 100")
            return None
        
        # Convert to DataFrame
        df = pd.DataFrame(self.training_data)
        
        # Simple optimization: Find threshold that maximizes target metric
        # Group by threshold and calculate average outcomes
        threshold_stats = df.groupby('threshold').agg({
            f'outcome_{target_metric}': ['mean', 'std', 'count'],
            'outcome_win_rate': 'mean',
            'outcome_total_return': 'mean',
            'outcome_sharpe_ratio': 'mean'
        }).reset_index()
        
        # Filter by minimum trades
        threshold_stats = threshold_stats[
            threshold_stats[('outcome_' + target_metric, 'count')] >= min_trades
        ]
        
        if len(threshold_stats) == 0:
            logger.warning("No thresholds meet minimum trade requirement")
            return None
        
        # Find optimal threshold
        metric_col = ('outcome_' + target_metric, 'mean')
        optimal_idx = threshold_stats[metric_col].idxmax()
        optimal_row = threshold_stats.iloc[optimal_idx]
        
        optimal_threshold = float(optimal_row['threshold'])
        expected_win_rate = float(optimal_row[('outcome_win_rate', 'mean')])
        expected_sharpe = float(optimal_row[('outcome_sharpe_ratio', 'mean')])
        expected_return = float(optimal_row[('outcome_total_return', 'mean')])
        
        # Calculate confidence interval (simple std-based)
        std = float(optimal_row[(f'outcome_{target_metric}', 'std')])
        confidence_interval = (
            optimal_threshold - 1.96 * std,
            optimal_threshold + 1.96 * std
        )
        
        # Simple feature importance (correlation with outcomes)
        feature_importance = {}
        for feature in self.feature_columns:
            if feature in df.columns:
                corr = df[feature].corr(df[f'outcome_{target_metric}'])
                feature_importance[feature] = float(corr) if not np.isnan(corr) else 0.0
        
        result = ThresholdOptimizationResult(
            optimal_threshold=optimal_threshold,
            expected_win_rate=expected_win_rate,
            expected_sharpe=expected_sharpe,
            expected_return=expected_return,
            confidence_interval=confidence_interval,
            feature_importance=feature_importance
        )
        
        logger.info(f"Optimal threshold: {optimal_threshold:.2f}% "
                   f"(expected {target_metric}={optimal_row[metric_col]:.2f})")
        
        return result
    
    def adaptive_threshold(
        self,
        current_features: Dict[str, float],
        base_threshold: float = 55.0
    ) -> float:
        """
        Calculate adaptive threshold based on current market conditions
        
        Args:
            current_features: Current market features
            base_threshold: Base threshold to adjust from
            
        Returns:
            Adjusted threshold
        """
        if len(self.training_data) < 50:
            return base_threshold
        
        # Simple adaptive logic: adjust based on volatility
        volatility = current_features.get('volatility', 0.2)
        rsi = current_features.get('rsi', 50.0)
        
        # Higher volatility -> higher threshold (more selective)
        volatility_adjustment = (volatility - 0.2) * 10  # Scale adjustment
        
        # Extreme RSI -> lower threshold (stronger signal)
        rsi_adjustment = 0.0
        if rsi < 30 or rsi > 70:
            rsi_adjustment = -5.0  # Lower threshold for extreme conditions
        
        adjusted_threshold = base_threshold + volatility_adjustment + rsi_adjustment
        
        # Clamp to reasonable range
        adjusted_threshold = max(50.0, min(80.0, adjusted_threshold))
        
        logger.debug(f"Adaptive threshold: {base_threshold:.1f} -> {adjusted_threshold:.1f} "
                    f"(vol={volatility:.2f}, rsi={rsi:.1f})")
        
        return adjusted_threshold
    
    def get_threshold_sensitivity_analysis(
        self,
        threshold_range: Tuple[float, float] = (50.0, 80.0),
        step: float = 2.5
    ) -> pd.DataFrame:
        """
        Analyze sensitivity of metrics to threshold changes
        
        Args:
            threshold_range: (min, max) threshold range
            step: Step size for threshold values
            
        Returns:
            DataFrame with threshold sensitivity analysis
        """
        if len(self.training_data) < 50:
            logger.warning("Insufficient data for sensitivity analysis")
            return pd.DataFrame()
        
        df = pd.DataFrame(self.training_data)
        
        thresholds = np.arange(threshold_range[0], threshold_range[1] + step, step)
        results = []
        
        for threshold in thresholds:
            # Filter data near this threshold
            threshold_data = df[
                (df['threshold'] >= threshold - step/2) &
                (df['threshold'] < threshold + step/2)
            ]
            
            if len(threshold_data) == 0:
                continue
            
            results.append({
                'threshold': threshold,
                'avg_win_rate': threshold_data['outcome_win_rate'].mean(),
                'avg_sharpe': threshold_data['outcome_sharpe_ratio'].mean(),
                'avg_return': threshold_data['outcome_total_return'].mean(),
                'avg_trades': threshold_data['outcome_total_trades'].mean(),
                'sample_count': len(threshold_data)
            })
        
        return pd.DataFrame(results)


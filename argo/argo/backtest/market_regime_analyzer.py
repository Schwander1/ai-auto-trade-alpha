#!/usr/bin/env python3
"""
Market Regime Analyzer v5.0
Analyzes market characteristics across different time periods
Documents regime-specific accuracy and sets realistic expectations
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class MarketRegimeAnalyzer:
    """
    Analyzes market regimes and their impact on trading accuracy
    Helps explain accuracy variations and set realistic expectations
    """
    
    def __init__(self):
        self.regime_characteristics = {}
    
    def analyze_period(
        self,
        df: pd.DataFrame,
        period_name: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """
        Analyze market characteristics for a specific period
        
        Args:
            df: Price data DataFrame
            period_name: Name of the period (e.g., "2023-2024", "2025-11-15")
            start_date: Start of period (if None, uses df start)
            end_date: End of period (if None, uses df end)
        
        Returns:
            Dict with regime characteristics
        """
        # Filter data
        if start_date:
            df = df[df.index >= start_date]
        if end_date:
            df = df[df.index <= end_date]
        
        if len(df) < 50:
            logger.warning(f"Insufficient data for period {period_name}")
            return {}
        
        # Calculate characteristics
        returns = df['Close'].pct_change().dropna()
        volatility = returns.std() * np.sqrt(252)  # Annualized volatility
        
        # Trend strength
        sma_20 = df['Close'].rolling(20).mean()
        sma_50 = df['Close'].rolling(50).mean()
        trend_alignment = (sma_20 > sma_50).sum() / len(sma_20.dropna())
        
        # Volatility regime
        vol_percentile = self._calculate_volatility_percentile(df, volatility)
        
        # Market direction
        total_return = (df['Close'].iloc[-1] / df['Close'].iloc[0] - 1) * 100
        direction = "Bull" if total_return > 5 else "Bear" if total_return < -5 else "Sideways"
        
        # Drawdown analysis
        peak = df['Close'].expanding().max()
        drawdown = (df['Close'] - peak) / peak * 100
        max_drawdown = drawdown.min()
        
        # Volume analysis
        if 'Volume' in df.columns:
            avg_volume = df['Volume'].mean()
            volume_trend = "Increasing" if df['Volume'].iloc[-20:].mean() > df['Volume'].iloc[:20].mean() else "Decreasing"
        else:
            avg_volume = None
            volume_trend = "Unknown"
        
        characteristics = {
            'period_name': period_name,
            'start_date': df.index[0] if start_date is None else start_date,
            'end_date': df.index[-1] if end_date is None else end_date,
            'total_return_pct': total_return,
            'direction': direction,
            'volatility_annualized': volatility * 100,
            'volatility_regime': vol_percentile,
            'trend_strength': trend_alignment,
            'max_drawdown_pct': abs(max_drawdown),
            'avg_volume': avg_volume,
            'volume_trend': volume_trend,
            'trading_difficulty': self._assess_difficulty(
                volatility, trend_alignment, abs(max_drawdown)
            ),
            'expected_accuracy_range': self._estimate_accuracy_range(
                volatility, trend_alignment, direction
            )
        }
        
        self.regime_characteristics[period_name] = characteristics
        return characteristics
    
    def _calculate_volatility_percentile(self, df: pd.DataFrame, current_vol: float) -> str:
        """Calculate volatility percentile"""
        # Calculate rolling volatility
        returns = df['Close'].pct_change().dropna()
        rolling_vol = returns.rolling(20).std() * np.sqrt(252)
        rolling_vol = rolling_vol.dropna()
        
        if len(rolling_vol) == 0:
            return "Unknown"
        
        percentile = (rolling_vol < current_vol).sum() / len(rolling_vol) * 100
        
        if percentile < 25:
            return "Low"
        elif percentile < 50:
            return "Below Average"
        elif percentile < 75:
            return "Above Average"
        else:
            return "High"
    
    def _assess_difficulty(
        self,
        volatility: float,
        trend_strength: float,
        max_drawdown: float
    ) -> str:
        """Assess trading difficulty based on market characteristics"""
        # High volatility + weak trends + large drawdowns = difficult
        difficulty_score = 0
        
        if volatility > 0.25:  # 25% annualized volatility
            difficulty_score += 2
        elif volatility > 0.15:
            difficulty_score += 1
        
        if trend_strength < 0.5:  # Weak trend
            difficulty_score += 2
        elif trend_strength < 0.6:
            difficulty_score += 1
        
        if max_drawdown > 20:
            difficulty_score += 2
        elif max_drawdown > 10:
            difficulty_score += 1
        
        if difficulty_score >= 5:
            return "Very Difficult"
        elif difficulty_score >= 3:
            return "Difficult"
        elif difficulty_score >= 1:
            return "Moderate"
        else:
            return "Easy"
    
    def _estimate_accuracy_range(
        self,
        volatility: float,
        trend_strength: float,
        direction: str
    ) -> Dict[str, float]:
        """Estimate expected accuracy range based on regime"""
        # Base accuracy
        base_accuracy = 75.0
        
        # Adjustments
        if direction == "Bull" and trend_strength > 0.6:
            base_accuracy += 10  # Strong bull market
        elif direction == "Bear" and trend_strength < 0.4:
            base_accuracy -= 5  # Strong bear market
        elif direction == "Sideways":
            base_accuracy -= 5  # Sideways is harder
        
        if volatility > 0.25:
            base_accuracy -= 5  # High volatility reduces accuracy
        elif volatility < 0.15:
            base_accuracy += 3  # Low volatility helps
        
        # Return range
        return {
            'min': max(60, base_accuracy - 5),
            'expected': base_accuracy,
            'max': min(95, base_accuracy + 5)
        }
    
    def compare_regimes(self, period1: str, period2: str) -> Dict:
        """Compare two market regimes"""
        if period1 not in self.regime_characteristics:
            logger.error(f"Period {period1} not found")
            return {}
        if period2 not in self.regime_characteristics:
            logger.error(f"Period {period2} not found")
            return {}
        
        r1 = self.regime_characteristics[period1]
        r2 = self.regime_characteristics[period2]
        
        comparison = {
            'period1': period1,
            'period2': period2,
            'return_diff': r2['total_return_pct'] - r1['total_return_pct'],
            'volatility_diff': r2['volatility_annualized'] - r1['volatility_annualized'],
            'trend_strength_diff': r2['trend_strength'] - r1['trend_strength'],
            'difficulty_change': f"{r1['trading_difficulty']} → {r2['trading_difficulty']}",
            'expected_accuracy_change': {
                'period1': r1['expected_accuracy_range'],
                'period2': r2['expected_accuracy_range'],
                'change': {
                    'min': r2['expected_accuracy_range']['min'] - r1['expected_accuracy_range']['min'],
                    'expected': r2['expected_accuracy_range']['expected'] - r1['expected_accuracy_range']['expected'],
                    'max': r2['expected_accuracy_range']['max'] - r1['expected_accuracy_range']['max']
                }
            }
        }
        
        return comparison
    
    def generate_regime_report(self) -> str:
        """Generate human-readable regime analysis report"""
        report = ["=" * 70]
        report.append("MARKET REGIME ANALYSIS REPORT")
        report.append("=" * 70)
        report.append("")
        
        for period_name, characteristics in self.regime_characteristics.items():
            report.append(f"Period: {period_name}")
            report.append(f"  Date Range: {characteristics['start_date']} to {characteristics['end_date']}")
            report.append(f"  Total Return: {characteristics['total_return_pct']:.2f}%")
            report.append(f"  Direction: {characteristics['direction']}")
            report.append(f"  Volatility: {characteristics['volatility_annualized']:.2f}% (annualized)")
            report.append(f"  Volatility Regime: {characteristics['volatility_regime']}")
            report.append(f"  Trend Strength: {characteristics['trend_strength']:.2%}")
            report.append(f"  Max Drawdown: {characteristics['max_drawdown_pct']:.2f}%")
            report.append(f"  Trading Difficulty: {characteristics['trading_difficulty']}")
            report.append(f"  Expected Accuracy Range: {characteristics['expected_accuracy_range']['min']:.1f}% - {characteristics['expected_accuracy_range']['max']:.1f}%")
            report.append(f"  Expected Accuracy: {characteristics['expected_accuracy_range']['expected']:.1f}%")
            report.append("")
        
        return "\n".join(report)


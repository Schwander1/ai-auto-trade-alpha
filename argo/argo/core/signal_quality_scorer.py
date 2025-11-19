#!/usr/bin/env python3
"""
Signal Quality Scoring System
Calculates composite quality score for signals based on multiple factors

Quality Score Components:
1. Confidence score (0-40 points)
2. Data source agreement (0-20 points)
3. Regime alignment (0-15 points)
4. Historical performance (0-15 points)
5. Risk-reward ratio (0-10 points)

Total: 0-100 points
"""
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

class SignalQualityScorer:
    """Calculate composite quality score for signals"""

    def __init__(self):
        self.db_path = Path(__file__).parent.parent.parent / "data" / "signals.db"
        self._historical_performance_cache = {}
        self._cache_ttl = 3600  # 1 hour cache

    def calculate_quality_score(self, signal: Dict) -> Dict:
        """
        Calculate composite quality score for a signal

        Args:
            signal: Signal dictionary with confidence, regime, etc.

        Returns:
            Dictionary with quality_score and component breakdown
        """
        components = {}

        # 1. Confidence score (0-40 points)
        confidence = signal.get('confidence', 75)
        components['confidence'] = self._score_confidence(confidence)

        # 2. Data source agreement (0-20 points)
        sources_count = signal.get('sources_count', 1)
        consensus_agreement = signal.get('consensus_agreement', 0.5)
        components['source_agreement'] = self._score_source_agreement(sources_count, consensus_agreement)

        # 3. Regime alignment (0-15 points)
        regime = signal.get('regime', 'UNKNOWN')
        components['regime_alignment'] = self._score_regime_alignment(regime, confidence)

        # 4. Historical performance (0-15 points)
        symbol = signal.get('symbol', '')
        components['historical_performance'] = self._score_historical_performance(symbol, confidence)

        # 5. Risk-reward ratio (0-10 points)
        entry_price = signal.get('entry_price', 0)
        stop_price = signal.get('stop_price')
        target_price = signal.get('target_price')
        components['risk_reward'] = self._score_risk_reward(entry_price, stop_price, target_price)

        # Calculate total score
        total_score = sum(components.values())

        # IMPROVEMENT: Stricter quality tiers - require higher scores for good quality
        # Determine quality tier
        if total_score >= 85:
            quality_tier = 'EXCELLENT'
        elif total_score >= 75:
            quality_tier = 'HIGH'
        elif total_score >= 65:
            quality_tier = 'GOOD'
        elif total_score >= 50:
            quality_tier = 'FAIR'
        else:
            quality_tier = 'POOR'
        
        # IMPROVEMENT: Log warning for low-quality signals
        if quality_tier in ['FAIR', 'POOR']:
            logger.warning(
                f"⚠️  Low quality signal detected: {signal.get('symbol', 'UNKNOWN')} "
                f"quality_score={total_score:.1f} ({quality_tier})"
            )

        return {
            'quality_score': round(total_score, 2),
            'quality_tier': quality_tier,
            'components': components,
            'max_score': 100.0
        }

    def _score_confidence(self, confidence: float) -> float:
        """Score confidence component (0-40 points)"""
        if confidence >= 95:
            return 40.0
        elif confidence >= 90:
            return 35.0
        elif confidence >= 85:
            return 30.0
        elif confidence >= 80:
            return 25.0
        elif confidence >= 75:
            return 20.0
        else:
            return max(0, (confidence / 75) * 20)

    def _score_source_agreement(self, sources_count: int, consensus_agreement: float) -> float:
        """Score data source agreement (0-20 points)"""
        # More sources = better (up to 6 sources)
        source_score = min(sources_count / 6 * 10, 10.0)

        # Higher agreement = better
        agreement_score = consensus_agreement * 10

        return source_score + agreement_score

    def _score_regime_alignment(self, regime: str, confidence: float) -> float:
        """Score regime alignment (0-15 points)"""
        # Regime-specific scoring
        regime_scores = {
            'BULL': 12.0,
            'BEAR': 12.0,
            'TRENDING': 12.0,
            'CHOP': 8.0,
            'CONSOLIDATION': 8.0,
            'CRISIS': 6.0,
            'VOLATILE': 10.0,
            'UNKNOWN': 5.0
        }

        base_score = regime_scores.get(regime, 5.0)

        # Adjust based on confidence
        if confidence >= 90:
            return base_score
        elif confidence >= 85:
            return base_score * 0.9
        elif confidence >= 80:
            return base_score * 0.8
        else:
            return base_score * 0.7

    def _score_historical_performance(self, symbol: str, confidence: float) -> float:
        """Score historical performance (0-15 points)"""
        if not symbol:
            return 7.5  # Neutral score

        # Get historical win rate for this symbol at this confidence level
        win_rate = self._get_historical_win_rate(symbol, confidence)

        if win_rate >= 0.70:
            return 15.0
        elif win_rate >= 0.60:
            return 12.0
        elif win_rate >= 0.50:
            return 10.0
        elif win_rate >= 0.40:
            return 7.5
        elif win_rate > 0:
            return 5.0
        else:
            return 7.5  # Neutral if no history

    def _score_risk_reward(self, entry_price: float, stop_price: Optional[float],
                          target_price: Optional[float]) -> float:
        """Score risk-reward ratio (0-10 points)"""
        if not entry_price or not stop_price or not target_price:
            return 5.0  # Neutral score

        # Calculate risk and reward
        if entry_price > stop_price:  # Long position
            risk = entry_price - stop_price
            reward = target_price - entry_price
        else:  # Short position
            risk = stop_price - entry_price
            reward = entry_price - target_price

        if risk <= 0:
            return 5.0

        risk_reward_ratio = reward / risk

        # Score based on risk-reward ratio
        if risk_reward_ratio >= 3.0:
            return 10.0
        elif risk_reward_ratio >= 2.0:
            return 8.5
        elif risk_reward_ratio >= 1.5:
            return 7.0
        elif risk_reward_ratio >= 1.0:
            return 5.0
        else:
            return 3.0

    def _get_historical_win_rate(self, symbol: str, confidence: float) -> float:
        """Get historical win rate for symbol at similar confidence level"""
        cache_key = f"{symbol}_{int(confidence // 5) * 5}"  # Round to nearest 5%

        # Check cache
        if cache_key in self._historical_performance_cache:
            cached_data, cached_time = self._historical_performance_cache[cache_key]
            if (datetime.now() - cached_time).total_seconds() < self._cache_ttl:
                return cached_data

        if not self.db_path.exists():
            logger.debug(f"Database not found: {self.db_path}, returning neutral win rate")
            return 0.5  # Neutral if no database

        try:
            conn = sqlite3.connect(str(self.db_path), timeout=10.0)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Get signals from last 30 days with similar confidence
            cutoff_time = (datetime.now() - timedelta(days=30)).isoformat()
            confidence_range = (max(0, confidence - 5), min(100, confidence + 5))

            # Use timestamp column for signal-based queries (created_at is DB insertion time)
            cursor.execute("""
                SELECT
                    COUNT(*) as total,
                    COUNT(CASE WHEN outcome = 'win' THEN 1 END) as wins
                FROM signals
                WHERE symbol = ?
                  AND timestamp >= ?
                  AND confidence >= ?
                  AND confidence <= ?
                  AND outcome IS NOT NULL
            """, (symbol, cutoff_time, confidence_range[0], confidence_range[1]))

            row = cursor.fetchone()
            conn.close()

            if row and row['total'] > 0:
                win_rate = row['wins'] / row['total']
                # Cache result
                self._historical_performance_cache[cache_key] = (win_rate, datetime.now())
                logger.debug(f"Historical win rate for {symbol} at {confidence}%: {win_rate:.2%}")
                return win_rate
            else:
                logger.debug(f"No historical data for {symbol} at {confidence}% confidence")
                return 0.5  # Neutral if no history
        except sqlite3.Error as e:
            logger.warning(f"Database error getting historical win rate for {symbol}: {e}")
            return 0.5
        except Exception as e:
            logger.error(f"Unexpected error getting historical win rate for {symbol}: {e}", exc_info=True)
            return 0.5

    def get_quality_trend(self, hours: int = 24) -> Dict:
        """Get quality score trend over time"""
        if not self.db_path.exists():
            return {'error': 'Database not found'}

        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cutoff_time = (datetime.now() - timedelta(hours=hours)).isoformat()

            # Use timestamp column for signal-based queries
            cursor.execute("""
                SELECT
                    strftime('%Y-%m-%d %H:00:00', timestamp) as hour,
                    COUNT(*) as count,
                    AVG(confidence) as avg_confidence
                FROM signals
                WHERE timestamp >= ?
                GROUP BY hour
                ORDER BY hour
            """, (cutoff_time,))

            trend = []
            for row in cursor.fetchall():
                trend.append({
                    'hour': row['hour'],
                    'count': row['count'],
                    'avg_confidence': row['avg_confidence']
                })

            conn.close()
            return {'trend': trend, 'period_hours': hours}
        except Exception as e:
            logger.error(f"Error getting quality trend: {e}")
            return {'error': str(e)}

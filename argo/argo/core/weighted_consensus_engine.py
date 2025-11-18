#!/usr/bin/env python3
"""
TRADE SECRET - PROPRIETARY ALGORITHM
Alpine Analytics LLC - Confidential

Weighted Consensus Engine v2.0
Performance: +565% over 20 years (9.94% CAGR)

This code contains proprietary algorithms and trade secrets.
Unauthorized disclosure, copying, or use is strictly prohibited.

PATENT-PENDING TECHNOLOGY
Patent Application: [Application Number]
Filing Date: [Date]

This code implements patent-pending technology.
Unauthorized use may infringe on pending patent rights.
"""
import json
import logging
import os
import hashlib
from pathlib import Path
from typing import Dict, Optional
from collections import defaultdict
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AlpineConsensus")


def _get_config_path():
    """Get config path for dev or production"""
    # Check environment variable first (highest priority)
    config_path = os.getenv("ARGO_CONFIG_PATH")
    if config_path and os.path.exists(config_path):
        return config_path

    # Check current working directory (for services running from their deployment directory)
    # This ensures prop firm service loads its own config
    cwd = Path.cwd()
    cwd_config = cwd / "config.json"
    if cwd_config.exists():
        return str(cwd_config)

    # Check production paths (in order of preference)
    # Only check these if we're not in a deployment directory
    prod_paths = [
        "/root/argo-production-prop-firm/config.json",  # Prop firm service
        "/root/argo-production-green/config.json",  # Regular trading (green)
        "/root/argo-production-blue/config.json",  # Regular trading (blue)
        "/root/argo-production/config.json",  # Legacy
    ]

    for prod_path in prod_paths:
        if os.path.exists(prod_path):
            return prod_path

    # Check dev path (argo/config.json)
    dev_path = Path(__file__).parent.parent.parent / "config.json"
    if dev_path.exists():
        return str(dev_path)

    # Fallback to production path (will fail gracefully if not exists)
    return "/root/argo-production/config.json"


class WeightedConsensusEngine:
    """
    Combines 4 data sources with weighted voting:
    - Massive.com (40%): Primary market data
    - Alpha Vantage (25%): Technical indicators
    - X Sentiment (20%): Social sentiment
    - Sonar AI (15%): AI analysis
    """

    def __init__(self, config_path=None):
        if config_path is None:
            config_path = _get_config_path()

        try:
            with open(config_path) as f:
                self.config = json.load(f)
        except FileNotFoundError:
            logger.warning(f"⚠️  Config file not found: {config_path}, using defaults")
            self.config = {
                "strategy": {
                    "weight_massive": 0.4,
                    "weight_alpha_vantage": 0.25,
                    "weight_x_sentiment": 0.2,
                    "weight_sonar": 0.15,
                },
                "trading": {"min_confidence": 75.0, "profit_target": 0.05, "stop_loss": 0.03},
            }

        # Check feature flag for optimized weights
        try:
            from argo.core.feature_flags import get_feature_flags

            feature_flags = get_feature_flags()

            if feature_flags.is_enabled("optimized_weights"):
                # Use optimized weights (from Perplexity analysis)
                optimized_weights = {
                    "massive": 0.50,  # ↑ from 0.40
                    "alpaca_pro": 0.50,  # ↑ from 0.40
                    "alpha_vantage": 0.30,  # ↑ from 0.25
                    "yfinance": 0.30,  # ↑ from 0.25
                    "x_sentiment": 0.15,  # ↓ from 0.20
                    "sonar": 0.05,  # ↓ from 0.15
                    "chinese_models": 0.10,  # 10% (20% off-hours)
                }
                self.weights = optimized_weights
                logger.info("✅ Using OPTIMIZED weights (feature flag enabled)")
            else:
                # Use original weights from config
                self.weights = {
                    "massive": self.config["strategy"]["weight_massive"],
                    "alpaca_pro": self.config["strategy"][
                        "weight_massive"
                    ],  # Same weight as Massive
                    "alpha_vantage": self.config["strategy"]["weight_alpha_vantage"],
                    "yfinance": self.config["strategy"][
                        "weight_alpha_vantage"
                    ],  # Same weight as Alpha Vantage
                    "x_sentiment": self.config["strategy"]["weight_x_sentiment"],
                    "sonar": self.config["strategy"]["weight_sonar"],
                    "chinese_models": self.config["strategy"].get(
                        "weight_chinese_models", 0.10
                    ),  # 10% default
                }
                logger.info("Using original weights from config")
        except Exception as e:
            logger.warning(f"⚠️  Could not load feature flags: {e}, using config weights")
            # Fallback to config weights
            self.weights = {
                "massive": self.config["strategy"]["weight_massive"],
                "alpaca_pro": self.config["strategy"]["weight_massive"],
                "alpha_vantage": self.config["strategy"]["weight_alpha_vantage"],
                "yfinance": self.config["strategy"]["weight_alpha_vantage"],
                "x_sentiment": self.config["strategy"]["weight_x_sentiment"],
                "sonar": self.config["strategy"]["weight_sonar"],
                "chinese_models": self.config["strategy"].get("weight_chinese_models", 0.10),
            }

        # OPTIMIZATION 6: Consensus calculation caching
        self._consensus_cache: Dict[str, tuple] = {}  # {hash: (consensus, timestamp)}
        self._cache_ttl = 60  # 1 minute cache
        self._max_cache_size = 1000  # Max cache entries

        logger.info("✅ Alpine Analytics Consensus Engine initialized")
        logger.info(f"   Weights: {self.weights}")
        logger.info(f"   Performance: +565% (9.94% CAGR)")

    def _hash_signals(self, signals: Dict, regime: Optional[str]) -> str:
        """Create hash of signals for cache key (OPTIMIZATION 6)"""
        # Sort signals for consistent hashing
        sorted_signals = json.dumps(signals, sort_keys=True, default=str)
        cache_key = f"{sorted_signals}:{regime}"
        return hashlib.md5(cache_key.encode()).hexdigest()

    def _cleanup_cache(self):
        """Clean up old cache entries (OPTIMIZATION 6)"""
        # OPTIMIZATION: Single datetime call, use dict comprehension for cleanup
        now = datetime.now(timezone.utc)

        # Remove expired entries using dict comprehension (more efficient)
        self._consensus_cache = {
            key: (consensus, timestamp)
            for key, (consensus, timestamp) in self._consensus_cache.items()
            if (now - timestamp).total_seconds() < self._cache_ttl
        }

        # Also limit cache size (optimized: use dict comprehension instead of list slicing)
        if len(self._consensus_cache) > self._max_cache_size:
            # Remove oldest entries (simple FIFO) - convert to list once, slice once
            all_keys = list(self._consensus_cache.keys())
            keys_to_keep = all_keys[-(self._max_cache_size) :]  # Keep last N entries
            self._consensus_cache = {key: self._consensus_cache[key] for key in keys_to_keep}

    def calculate_consensus(self, signals: Dict, regime: Optional[str] = None) -> Optional[Dict]:
        """
        Weighted consensus algorithm with optional regime-based weights and caching:
        weighted_vote = confidence × source_weight

        OPTIMIZATION 6: Caches consensus calculations for identical inputs

        Args:
            signals: Dict of source signals
            regime: Optional market regime for regime-based weight adaptation
        """
        # OPTIMIZATION 6: Check cache first
        # OPTIMIZATION: Single datetime call for both cache check and storage
        now = datetime.now(timezone.utc)
        cache_key = self._hash_signals(signals, regime)
        if cache_key in self._consensus_cache:
            cached_consensus, timestamp = self._consensus_cache[cache_key]
            if (now - timestamp).total_seconds() < self._cache_ttl:
                logger.debug("✅ Using cached consensus")
                return cached_consensus

        # Check for regime-based weights if enabled
        try:
            from argo.core.feature_flags import get_feature_flags
            from argo.core.regime_detector import get_regime_weights, map_legacy_regime_to_enhanced

            feature_flags = get_feature_flags()

            # Use regime-based weights if enabled
            if feature_flags.is_enabled("regime_based_weights") and regime:
                # Map legacy regime to enhanced if needed
                enhanced_regime = map_legacy_regime_to_enhanced(regime)
                regime_weights = get_regime_weights(enhanced_regime)

                # Map to actual source names
                active_weights = {
                    "massive": regime_weights.get("massive", 0.50),
                    "alpaca_pro": regime_weights.get("massive", 0.50),
                    "alpha_vantage": regime_weights.get("alpha_vantage", 0.30),
                    "yfinance": regime_weights.get("alpha_vantage", 0.30),
                    "x_sentiment": regime_weights.get("xai_grok", 0.15),
                    "sonar": regime_weights.get("sonar", 0.05),
                    "chinese_models": regime_weights.get("chinese_models", 0.10),
                }
                logger.debug(f"Using regime-based weights for {enhanced_regime}: {active_weights}")
            else:
                active_weights = self.weights
        except Exception as e:
            logger.debug(f"Could not load regime-based weights: {e}, using default weights")
            active_weights = self.weights

        valid = {k: v for k, v in signals.items() if v and k in active_weights}

        if not valid:
            return None

        long_votes = {}
        short_votes = {}

        # IMPROVEMENT: Handle single-source NEUTRAL signals specially
        # If only 1 source with high-confidence NEUTRAL, use it directly
        if len(valid) == 1:
            source, signal = next(iter(valid.items()))
            direction = signal.get("direction")
            confidence = signal.get("confidence", 0)
            
            # For single high-confidence NEUTRAL signal, use it directly
            if direction == "NEUTRAL" and confidence >= 0.65:
                return {
                    "direction": "NEUTRAL",
                    "confidence": round(confidence * 100, 2),
                    "total_long_vote": confidence * 0.55,
                    "total_short_vote": confidence * 0.45,
                    "sources": 1,
                    "agreement": round(confidence * 100, 2),
                }
            # For single directional signal, use it directly if confidence is reasonable
            elif direction in ["LONG", "SHORT"] and confidence >= 0.60:
                return {
                    "direction": direction,
                    "confidence": round(confidence * 100, 2),
                    "total_long_vote": confidence if direction == "LONG" else 0,
                    "total_short_vote": confidence if direction == "SHORT" else 0,
                    "sources": 1,
                    "agreement": round(confidence * 100, 2),
                }

        # IMPROVEMENT: Track NEUTRAL signals separately for better handling
        neutral_signals = []
        for source, signal in valid.items():
            direction = signal.get("direction")
            confidence = signal.get("confidence", 0)
            weight = active_weights[source]
            vote = confidence * weight

            if direction == "LONG":
                long_votes[source] = vote
            elif direction == "SHORT":
                short_votes[source] = vote
            elif direction == "NEUTRAL":
                # IMPROVEMENT: Store NEUTRAL signals for special handling
                neutral_signals.append((source, signal, vote, weight))
        
        # IMPROVEMENT: Handle NEUTRAL signals intelligently
        # If we have high-confidence NEUTRAL signals and no clear directional consensus,
        # use NEUTRAL directly instead of splitting
        if neutral_signals:
            # Check if we have high-confidence NEUTRAL signals
            high_confidence_neutral = [n for n in neutral_signals if n[1].get("confidence", 0) >= 0.70]
            
            # If we have high-confidence NEUTRAL and no strong directional signals, use NEUTRAL
            if high_confidence_neutral and not long_votes and not short_votes:
                # All sources are NEUTRAL with high confidence - use directly
                avg_neutral_confidence = sum(n[1].get("confidence", 0) for n in neutral_signals) / len(neutral_signals)
                total_neutral_weight = sum(n[3] for n in neutral_signals)
                return {
                    "direction": "NEUTRAL",
                    "confidence": round(avg_neutral_confidence * 100, 2),
                    "total_long_vote": avg_neutral_confidence * total_neutral_weight * 0.55,
                    "total_short_vote": avg_neutral_confidence * total_neutral_weight * 0.45,
                    "sources": len(neutral_signals),
                    "agreement": round(avg_neutral_confidence * 100, 2),
                }
            else:
                # Split NEUTRAL votes only if we have directional signals to balance
                # Only split high-confidence NEUTRAL (>= 70%) if we have directional signals
                for source, signal, vote, weight in neutral_signals:
                    neutral_confidence = signal.get("confidence", 0)
                    if neutral_confidence >= 0.70 and (long_votes or short_votes):
                        # High-confidence NEUTRAL with directional signals - split with trend bias
                        # Determine trend from existing directional signals
                        if sum(long_votes.values()) > sum(short_votes.values()):
                            # Bias toward LONG
                            neutral_long = vote * 0.60
                            neutral_short = vote * 0.40
                        else:
                            # Bias toward SHORT or neutral
                            neutral_long = vote * 0.50
                            neutral_short = vote * 0.50
                        long_votes[source] = neutral_long
                        short_votes[source] = neutral_short
                    elif neutral_confidence >= 0.55:
                        # Lower confidence NEUTRAL - split proportionally
                        neutral_long = vote * 0.55
                        neutral_short = vote * 0.45
                        long_votes[source] = neutral_long
                        short_votes[source] = neutral_short

        total_long = sum(long_votes.values())
        total_short = sum(short_votes.values())

        # Calculate sum of weights for sources that actually provided signals
        # This allows consensus to work even when some sources fail
        active_weights_sum = sum(active_weights[source] for source in valid.keys())

        if active_weights_sum == 0:
            return None

        if total_long > total_short and total_long > 0:
            consensus_direction = "LONG"
            # Divide by active weights sum, not all weights (fixes bug when sources fail)
            consensus_confidence = total_long / active_weights_sum * 100
        elif total_short > total_long and total_short > 0:
            consensus_direction = "SHORT"
            # Divide by active weights sum, not all weights (fixes bug when sources fail)
            consensus_confidence = total_short / active_weights_sum * 100
        else:
            # If we have NEUTRAL signals but no clear direction, return None
            # This maintains the original behavior for truly neutral markets
            return None

        consensus = {
            "direction": consensus_direction,
            "confidence": round(consensus_confidence, 2),
            "total_long_vote": round(total_long, 4),
            "total_short_vote": round(total_short, 4),
            "sources": len(valid),
            "agreement": round(max(total_long, total_short) / active_weights_sum * 100, 2),
        }

        # OPTIMIZATION 6: Cache result
        # OPTIMIZATION: Reuse 'now' variable from earlier instead of new datetime call
        if consensus:
            self._consensus_cache[cache_key] = (consensus, now)
            # Cleanup old cache entries periodically
            if len(self._consensus_cache) % 100 == 0:  # Cleanup every 100 entries
                self._cleanup_cache()

        return consensus


if __name__ == "__main__":
    engine = WeightedConsensusEngine()

    # Test with mock signals
    test_signals = {
        "massive": {"direction": "LONG", "confidence": 85},
        "alpha_vantage": {"direction": "LONG", "confidence": 80},
        "x_sentiment": {"direction": "LONG", "confidence": 75},
        "sonar": {"direction": "LONG", "confidence": 90},
    }

    consensus = engine.calculate_consensus(test_signals)
    print(json.dumps(consensus, indent=2))

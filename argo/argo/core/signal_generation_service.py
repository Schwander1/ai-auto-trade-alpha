#!/usr/bin/env python3
"""
TRADE SECRET - PROPRIETARY ALGORITHM
Alpine Analytics LLC - Confidential

Automatic Signal Generation Service
Generates signals every 5 seconds using Weighted Consensus v6.0

This code contains proprietary algorithms and trade secrets.
Unauthorized disclosure, copying, or use is strictly prohibited.

PATENT-PENDING TECHNOLOGY
Patent Application: [Application Number]
Filing Date: [Date]

This code implements patent-pending technology.
Unauthorized use may infringe on pending patent rights.
"""
import asyncio
import json
import logging
import os
import platform
import subprocess
import sys
import hashlib
import pandas as pd
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import SignalTracker with path handling
try:
    from argo.core.signal_tracker import SignalTracker
except ImportError:
    from core.signal_tracker import SignalTracker
from argo.core.weighted_consensus_engine import WeightedConsensusEngine
from argo.core.regime_detector import detect_regime, adjust_confidence
from argo.ai.explainer import SignalExplainer

# Data sources
from argo.core.data_sources.massive_source import MassiveDataSource
from argo.core.data_sources.alpha_vantage_source import AlphaVantageDataSource
from argo.core.data_sources.xai_grok_source import XAIGrokDataSource
from argo.core.data_sources.sonar_source import SonarDataSource
from argo.core.data_sources.alpaca_pro_source import AlpacaProDataSource
from argo.core.data_sources.yfinance_source import YFinanceDataSource
from argo.core.data_sources.chinese_models_source import ChineseModelsDataSource

# Enhancements
from argo.validation.data_quality import DataQualityMonitor
from argo.risk.prop_firm_risk_monitor import PropFirmRiskMonitor
from argo.core.adaptive_weight_manager import AdaptiveWeightManager
from argo.core.performance_budget_monitor import get_performance_monitor

# Enhanced Tradervue integration
try:
    from argo.integrations.tradervue_integration import get_tradervue_integration

    TRADERVUE_INTEGRATION_AVAILABLE = True
except ImportError:
    TRADERVUE_INTEGRATION_AVAILABLE = False

# Config - import at runtime to avoid circular imports

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SignalGenerationService")

# Trading symbols to monitor
DEFAULT_SYMBOLS = ["AAPL", "NVDA", "TSLA", "MSFT", "BTC-USD", "ETH-USD"]


class SignalGenerationService:
    """
    Automatic signal generation service
    - Generates signals every 5 seconds
    - Uses Weighted Consensus v6.0
    - Stores signals with SHA-256 verification
    - Includes AI-generated reasoning
    """

    def __init__(self):
        self.tracker = SignalTracker()
        # Initialize risk_monitor attribute early to avoid AttributeError
        self.risk_monitor = None
        self.prop_firm_mode = False
        self.prop_firm_config = None
        self._init_consensus_engine()
        self._init_environment()
        self._init_data_sources()
        self._init_trading_engine()
        self._init_performance_tracking()
        self._init_alpine_sync()
        logger.info("✅ Signal Generation Service initialized")

    def _init_consensus_engine(self):
        """Initialize consensus engine with config"""
        try:
            self.consensus_engine = WeightedConsensusEngine()
            # Get trading config from consensus engine
            self.trading_config = self.consensus_engine.config.get("trading", {})
        except Exception as e:
            logger.warning(f"⚠️  Could not load consensus engine config: {e}")
            self._init_fallback_consensus_engine()
            self.trading_config = {}

        self.explainer = SignalExplainer()
        self.running = False
        self._paused = False  # Paused due to Cursor/computer state (dev only)

        # OPTIMIZATION: Caching for consensus and reasoning
        self._consensus_cache = {}  # Cache consensus calculations
        self._consensus_cache_ttl = 300  # 5 minute cache
        self._reasoning_cache = {}  # Cache AI reasoning
        self._reasoning_cache_ttl = 3600  # 1 hour cache

        # OPTIMIZATION: Track last prices to skip unchanged symbols
        self._last_prices: Dict[str, float] = {}  # {symbol: last_price}
        self._last_signals: Dict[str, Dict] = {}  # {symbol: last_signal}
        self._price_change_threshold = 0.005  # 0.5% change threshold

        # OPTIMIZATION: Priority-based symbol processing
        self._symbol_volatility: Dict[str, float] = {}  # Track volatility for prioritization

        # OPTIMIZATION: Adaptive confidence thresholds (Strategy C)
        try:
            from argo.core.feature_flags import get_feature_flags

            feature_flags = get_feature_flags()

            if feature_flags.is_enabled("confidence_threshold_88"):
                # Use 88% threshold with regime-based adaptation
                self.confidence_threshold = 88.0
                logger.info("✅ Using 88% confidence threshold (feature flag enabled)")
            else:
                self.confidence_threshold = self.trading_config.get("min_confidence", 75.0)

            # Adaptive threshold by regime
            self.regime_thresholds = {
                "TRENDING": 85.0,  # Lower in trending markets
                "CONSOLIDATION": 90.0,  # Higher in choppy markets
                "VOLATILE": 88.0,  # Standard
                "UNKNOWN": 88.0,
                # Legacy regime mappings
                "BULL": 85.0,
                "BEAR": 85.0,
                "CHOP": 90.0,
                "CRISIS": 88.0,
            }
        except Exception as e:
            logger.warning(f"⚠️  Could not load feature flags for confidence threshold: {e}")
            self.confidence_threshold = self.trading_config.get("min_confidence", 75.0)
            self.regime_thresholds = {
                "TRENDING": 75.0,
                "CONSOLIDATION": 75.0,
                "VOLATILE": 75.0,
                "UNKNOWN": 75.0,
            }

        # OPTIMIZATION: Redis cache for distributed caching
        try:
            from argo.core.redis_cache import get_redis_cache

            self.redis_cache = get_redis_cache()
        except ImportError:
            self.redis_cache = None

        # OPTIMIZATION: Adaptive cache TTL
        try:
            from argo.core.adaptive_cache_ttl import get_adaptive_ttl

            self.adaptive_ttl = get_adaptive_ttl()
        except ImportError:
            self.adaptive_ttl = None

        # OPTIMIZATION: Request coalescing
        try:
            from argo.core.request_coalescer import RequestCoalescer

            self.request_coalescer = RequestCoalescer(ttl_seconds=5)
        except ImportError:
            self.request_coalescer = None

        # OPTIMIZATION: Performance metrics
        try:
            from argo.core.performance_metrics import get_performance_metrics

            self.performance_metrics = get_performance_metrics()
        except ImportError:
            self.performance_metrics = None

        # OPTIMIZATION 7: Regime detection caching (with size limits)
        self._regime_cache: Dict[str, tuple] = {}  # {data_hash: (regime, timestamp)}
        self._regime_cache_max_size = 500  # Max 500 entries
        self._regime_cache_ttl = 300  # 5 minute TTL

        # OPTIMIZATION 11: JSON serialization cache
        try:
            from argo.core.json_cache import get_json_cache

            self.json_cache = get_json_cache()
        except ImportError:
            self.json_cache = None

        # OPTIMIZATION 12: AI reasoning cache
        self._reasoning_cache: Dict[str, tuple] = {}  # {signal_hash: (reasoning, timestamp)}

        # OPTIMIZATION 13: Component change tracking
        self._component_cache: Dict[str, Any] = {}  # {symbol:component: value}

        # OPTIMIZATION 10: Symbol success tracking for adaptive processing
        self._symbol_success_tracking: Dict[str, list] = {}  # {symbol: [success_history]}

    def _init_fallback_consensus_engine(self):
        """Initialize fallback consensus engine with defaults"""
        self.consensus_engine = WeightedConsensusEngine.__new__(WeightedConsensusEngine)
        self.consensus_engine.weights = {
            "massive": 0.40,
            "alpha_vantage": 0.25,
            "x_sentiment": 0.20,
            "sonar": 0.15,
        }
        self.consensus_engine.calculate_consensus = lambda signals: self._simple_consensus(signals)

    def _init_environment(self):
        """Initialize environment detection and cursor awareness"""
        from argo.core.environment import detect_environment, get_environment_info
        import os

        self.environment = detect_environment()
        env_info = get_environment_info()
        logger.info(f"🌍 Signal Generation Service - Environment: {self.environment}")
        logger.debug(f"   Environment details: {env_info}")

        # Cursor/computer awareness (development only)
        # Allow forcing 24/7 mode via environment variable or config
        force_24_7 = os.getenv("ARGO_24_7_MODE", "").lower() in ["true", "1", "yes"]

        # Also check config for 24/7 mode setting (check after consensus engine is initialized)
        if not force_24_7 and hasattr(self, "trading_config"):
            force_24_7 = self.trading_config.get("force_24_7_mode", False)

        if force_24_7:
            self._cursor_aware = False
            logger.info("🚀 24/7 mode enabled: Signal generation will run continuously")
        else:
            self._cursor_aware = self.environment == "development"
        if self._cursor_aware:
                logger.info(
                    "💡 Development mode: Trading will pause when Cursor is closed or computer is asleep"
                )
                logger.info(
                    "   Set ARGO_24_7_MODE=true or config.trading.force_24_7_mode=true to enable 24/7 signal generation"
                )

    def _init_trading_engine(self):
        """Initialize trading engine if auto-execution is enabled"""
        self.auto_execute = self.trading_config.get("auto_execute", False)
        self.trading_engine = None
        self._positions_cache = None
        self._positions_cache_time = None
        self._positions_cache_ttl = 30  # Cache positions for 30 seconds

        # Peak equity tracking for drawdown calculation
        self._peak_equity = None
        self._daily_start_equity = None
        self._daily_loss_limit_pct = self.trading_config.get("daily_loss_limit_pct", 5.0)
        self._trading_paused = False

        if not self.auto_execute:
            return

        try:
            from argo.core.paper_trading_engine import PaperTradingEngine

            self.trading_engine = PaperTradingEngine()
            self._validate_trading_engine()
        except Exception as e:
            logger.warning(f"⚠️  Trading engine not available: {e}")
            self.auto_execute = False

    def _validate_trading_engine(self):
        """Validate trading engine initialization and log status"""
        if self.trading_engine.alpaca_enabled:
            account = self.trading_engine.get_account_details()
            if account:
                logger.info(
                    f"✅ Trading engine initialized - auto-execution enabled ({self.environment})"
                )
                logger.info(f"   Account: {self.trading_engine.account_name}")
                logger.info(
                    f"   Portfolio: ${account['portfolio_value']:,.2f} | Buying Power: ${account['buying_power']:,.2f}"
                )
            else:
                logger.info("✅ Trading engine initialized - auto-execution enabled")
        else:
            logger.warning(
                "⚠️  Trading engine initialized but Alpaca not connected - simulation mode"
            )
            self.auto_execute = False

    def _init_performance_tracking(self):
        """Initialize performance tracking"""
        self._performance_tracker = None
        self._lifecycle_tracker = None
        self._confidence_calibrator = None

        try:
            from argo.tracking.unified_tracker import UnifiedPerformanceTracker

            self._performance_tracker = UnifiedPerformanceTracker()
        except Exception as e:
            logger.debug(f"Performance tracker not available: {e}")

        try:
            from argo.validation.signal_lifecycle import SignalLifecycleTracker

            self._lifecycle_tracker = SignalLifecycleTracker()
        except Exception as e:
            logger.debug(f"Lifecycle tracker not available: {e}")

        # Initialize confidence calibrator (v5.0 optimization)
        try:
            from argo.ml.confidence_calibrator import ConfidenceCalibrator

            self._confidence_calibrator = ConfidenceCalibrator()
            logger.info("✅ Confidence calibrator initialized")
        except Exception as e:
            logger.debug(f"Confidence calibrator not available: {e}")

        # Initialize outcome tracker (v5.0 optimization)
        try:
            from argo.tracking.outcome_tracker import OutcomeTracker

            self._outcome_tracker = OutcomeTracker()
            self._last_outcome_check = None
        except Exception as e:
            logger.debug(f"Outcome tracker not available: {e}")
            self._outcome_tracker = None

        # Initialize signal quality scorer
        try:
            from argo.core.signal_quality_scorer import SignalQualityScorer

            self._quality_scorer = SignalQualityScorer()
            logger.info("✅ Signal quality scorer initialized")
        except Exception as e:
            logger.debug(f"Signal quality scorer not available: {e}")
            self._quality_scorer = None

        # Set outcome check interval
        self._outcome_check_interval = 300  # Check every 5 minutes
        if self._outcome_tracker:
            logger.info("✅ Outcome tracker initialized")

    def _init_alpine_sync(self):
        """Initialize Alpine backend sync service"""
        try:
            from argo.core.alpine_sync import get_alpine_sync_service

            self.alpine_sync = get_alpine_sync_service()
            logger.info("✅ Alpine sync service initialized")
        except Exception as e:
            logger.warning(f"⚠️  Alpine sync service not available: {e}")
            self.alpine_sync = None

    def _simple_consensus(self, signals):
        """Fallback consensus calculation if config.json not available"""
        if not signals:
            return None

        long_votes = 0
        short_votes = 0
        total_weight = 0

        for source, signal in signals.items():
            weight = self.consensus_engine.weights.get(source, 0)
            direction = signal.get("direction", "NEUTRAL")
            confidence = signal.get("confidence", 0)
            vote = confidence * weight

            if direction == "LONG":
                long_votes += vote
            elif direction == "SHORT":
                short_votes += vote

            total_weight += weight

        if long_votes > short_votes and long_votes > 0:
            return {
                "direction": "LONG",
                "confidence": (long_votes / total_weight * 100) if total_weight > 0 else 0,
                "sources": len(signals),
                "agreement": (long_votes / total_weight * 100) if total_weight > 0 else 0,
            }
        elif short_votes > long_votes and short_votes > 0:
            return {
                "direction": "SHORT",
                "confidence": (short_votes / total_weight * 100) if total_weight > 0 else 0,
                "sources": len(signals),
                "agreement": (short_votes / total_weight * 100) if total_weight > 0 else 0,
            }

        return None

    def _init_data_sources(self):
        """Initialize all data sources with API keys from AWS Secrets Manager, config.json, or env"""
        self.data_sources = {}

        try:
            get_secret = self._get_secrets_manager()
            config_api_keys, config_path = self._load_config_api_keys()

            # Initialize each data source
            self._init_massive_source(get_secret, config_api_keys)
            self._init_alpha_vantage_source(get_secret, config_api_keys)
            self._init_xai_grok_source(get_secret, config_api_keys)
            self._init_sonar_source(get_secret, config_api_keys)
            self._init_alpaca_pro_source(config_path)
            self._init_yfinance_source()
            self._init_chinese_models_source(config_path)

            self._log_data_source_summary()

            # Initialize health monitoring
            from argo.core.data_source_health import get_health_monitor

            self.health_monitor = get_health_monitor()

            # Initialize enhancements
            self._init_enhancements(config_path)

        except Exception as e:
            logger.error(f"❌ Error initializing data sources: {e}")

    def _get_secrets_manager(self):
        """Get secrets manager function if available"""
        try:
            from argo.utils.secrets_manager import get_secret

            return get_secret
        except ImportError:
            return None

    def _load_config_api_keys(self):
        """Load API keys from config.json using unified config loader"""
        try:
            from argo.core.config_loader import ConfigLoader

            config_api_keys = ConfigLoader.load_api_keys()
            _, config_path = ConfigLoader.load_config()
            return config_api_keys, config_path
        except Exception as e:
            logger.warning(f"⚠️  Could not load API keys from config.json: {e}", exc_info=True)
            return {}, None

    def _resolve_api_key(
        self,
        source_name: str,
        secret_keys: List[str],
        env_keys: List[str],
        config_key: str,
        get_secret,
        config_api_keys: Dict,
        validator=None,
    ) -> Optional[str]:
        """Resolve API key from multiple sources (AWS Secrets → env → config)"""
        # Try AWS Secrets Manager first
        if get_secret:
            for secret_key in secret_keys:
                api_key = get_secret(secret_key, service="argo")
                if api_key:
                    logger.debug(f"{source_name} API key found in AWS Secrets Manager")
                    return api_key

        # Try environment variables
        for env_key in env_keys:
            api_key = os.getenv(env_key)
            if api_key:
                logger.debug(f"{source_name} API key found in environment variable")
                return api_key

        # Try config.json
        if config_key and config_key in config_api_keys:
            api_key = config_api_keys[config_key]
            if api_key:
                if validator:
                    api_key = validator(api_key, source_name)
                if api_key:
                    logger.info(f"✅ {source_name} API key found in config.json")
                    return api_key

        return None

    def _validate_massive_key(self, api_key: str, source_name: str) -> Optional[str]:
        """Validate Massive.com API key format"""
        key_len = len(api_key)
        has_dash = "-" in api_key
        should_reject = has_dash or key_len > 40

        logger.info(
            f"🔍 Massive key validation: len={key_len}, has_dash={has_dash}, should_reject={should_reject}"
        )

        if should_reject:
            logger.warning("⚠️  Config has S3 access key, not Massive.com REST API key.")
            logger.warning(
                "   S3 keys are for flat files. Need REST API key from Massive.com dashboard."
            )
            logger.warning("   Get your REST API key from: https://massive.com/dashboard")
            return None

        logger.info(
            f"✅ Massive.com REST API key found in config.json: {api_key[:10]}... (len={key_len})"
        )
        return api_key

    def _init_massive_source(self, get_secret, config_api_keys: Dict):
        """Initialize Massive (Polygon.io) data source - 40% weight"""
        try:
            # For Massive, prefer config.json over AWS Secrets Manager
            # (AWS key may be outdated, config.json has validated key)
            polygon_key = None

            # Try config.json first for Massive
            if "massive" in config_api_keys:
                config_key = config_api_keys["massive"]
                if config_key:
                    validated_key = self._validate_massive_key(config_key, "Massive")
                    if validated_key:
                        polygon_key = validated_key
                        logger.info("✅ Massive API key found in config.json (preferred)")

            # Fallback to AWS Secrets Manager if config.json not available
            if not polygon_key and get_secret:
                polygon_key = self._resolve_api_key(
                    "Massive",
                    ["massive-api-key", "polygon-api-key"],  # Check both new and legacy names
                    ["MASSIVE_API_KEY", "POLYGON_API_KEY"],
                    None,  # Don't check config.json again
                    get_secret,
                    {},  # Empty config_api_keys since we already checked
                    self._validate_massive_key,
                )

            if polygon_key:
                self.data_sources["massive"] = MassiveDataSource(polygon_key)
                logger.info("✅ Massive data source initialized")
            else:
                logger.warning(
                    "⚠️  Massive API key not found in AWS Secrets, env vars, or config.json"
                )
        except Exception as e:
            logger.warning(f"⚠️  Massive init error: {e}", exc_info=True)

    def _init_alpha_vantage_source(self, get_secret, config_api_keys: Dict):
        """Initialize Alpha Vantage data source - 25% weight"""
        try:
            alpha_key = self._resolve_api_key(
                "Alpha Vantage",
                ["alpha-vantage-api-key"],
                ["ALPHA_VANTAGE_API_KEY"],
                "alpha_vantage",
                get_secret,
                config_api_keys,
            )

            if alpha_key:
                self.data_sources["alpha_vantage"] = AlphaVantageDataSource(alpha_key)
                logger.info("✅ Alpha Vantage data source initialized")
            else:
                logger.warning("⚠️  Alpha Vantage API key not found")
        except Exception as e:
            logger.warning(f"Alpha Vantage init error: {e}")

    def _init_xai_grok_source(self, get_secret, config_api_keys: Dict):
        """Initialize XAI Grok data source - 20% weight"""
        try:
            # Priority: config.json > environment variable > AWS Secrets Manager
            xai_key = config_api_keys.get("xai") or os.getenv("XAI_API_KEY")
            if not xai_key and get_secret:
                xai_key = get_secret("xai-api-key", service="argo")

            if xai_key:
                logger.info(
                    f"🔑 xAI Grok key source: {'config.json' if config_api_keys.get('xai') else 'env' if os.getenv('XAI_API_KEY') else 'AWS Secrets Manager'}"
                )
                logger.debug(f"   Key: {xai_key[:20]}...{xai_key[-10:]}")
                self.data_sources["x_sentiment"] = XAIGrokDataSource(xai_key)
                logger.info("✅ XAI Grok data source initialized")
            else:
                logger.warning("⚠️  XAI Grok API key not found")
        except Exception as e:
            logger.warning(f"XAI Grok init error: {e}")

    def _init_sonar_source(self, get_secret, config_api_keys: Dict):
        """Initialize Sonar AI (Perplexity) data source - 15% weight"""
        try:
            sonar_key = self._resolve_api_key(
                "Sonar AI",
                ["perplexity-api-key"],
                ["PERPLEXITY_API_KEY"],
                "sonar",
                get_secret,
                config_api_keys,
            )

            if sonar_key:
                self.data_sources["sonar"] = SonarDataSource(sonar_key)
                logger.info("✅ Sonar AI data source initialized")
            else:
                logger.warning("⚠️  Sonar AI API key not found")
        except Exception as e:
            logger.warning(f"Sonar init error: {e}")

    def _init_alpaca_pro_source(self, config_path: Optional[str]):
        """Initialize Alpaca Pro data source - supplements Massive.com"""
        try:
            alpaca_api_key = None
            alpaca_secret_key = None

            if config_path:
                with open(config_path) as f:
                    config = json.load(f)
                    alpaca_config = config.get("alpaca", {})
                    # Try production first, then dev
                    if self.environment == "production":
                        alpaca_api_key = alpaca_config.get("production", {}).get("api_key")
                        alpaca_secret_key = alpaca_config.get("production", {}).get("secret_key")
                    else:
                        alpaca_api_key = alpaca_config.get("dev", {}).get("api_key")
                        alpaca_secret_key = alpaca_config.get("dev", {}).get("secret_key")

            # Also try environment variables
            alpaca_api_key = alpaca_api_key or os.getenv("ALPACA_API_KEY")
            alpaca_secret_key = alpaca_secret_key or os.getenv("ALPACA_SECRET_KEY")

            if alpaca_api_key and alpaca_secret_key:
                self.data_sources["alpaca_pro"] = AlpacaProDataSource(
                    alpaca_api_key, alpaca_secret_key
                )
                logger.info("✅ Alpaca Pro data source initialized (supplements Massive.com)")
            else:
                logger.debug("⚠️  Alpaca Pro credentials not found - will use Massive.com only")
        except Exception as e:
            logger.warning(f"Alpaca Pro init error: {e}")

    def _init_yfinance_source(self):
        """Initialize yfinance data source - supplements Alpha Vantage"""
        try:
            self.data_sources["yfinance"] = YFinanceDataSource()
            if self.data_sources["yfinance"].enabled:
                logger.info("✅ yfinance data source initialized (supplements Alpha Vantage)")
        except Exception as e:
            logger.warning(f"yfinance init error: {e}")

    def _init_chinese_models_source(self, config_path: Optional[str]):
        """Initialize Chinese Models data source - 10% weight (20% off-hours)"""
        try:
            # Check feature flag
            try:
                from argo.core.feature_flags import get_feature_flags

                feature_flags = get_feature_flags()
                if not feature_flags.is_enabled("chinese_models_enabled"):
                    logger.info("ℹ️  Chinese models disabled by feature flag")
                    return
            except:
                pass

            config = {}
            if config_path:
                with open(config_path) as f:
                    full_config = json.load(f)
                    chinese_config = full_config.get("chinese_models", {})
                    if chinese_config.get("enabled", False):
                        # Load configuration with API keys
                        qwen_config = chinese_config.get("qwen", {})
                        glm_config = chinese_config.get("glm", {})
                        baichuan_config = chinese_config.get("baichuan", {})

                        config = {
                            # Qwen configuration
                            "qwen_api_key": qwen_config.get("api_key", ""),
                            "qwen_access_key_id": qwen_config.get("access_key_id", ""),
                            "qwen_access_key_secret": qwen_config.get("access_key_secret", ""),
                            "qwen_enabled": qwen_config.get("enabled", False),
                            "qwen_model": qwen_config.get("model", "qwen-turbo"),
                            "qwen_rpm": qwen_config.get("requests_per_minute", 20),
                            "qwen_cost": qwen_config.get("cost_per_request", 0.002),
                            "qwen_budget": qwen_config.get("daily_budget", 50.0),
                            # GLM configuration
                            "glm_api_key": glm_config.get("api_key", ""),
                            "glm_enabled": glm_config.get("enabled", False),
                            "glm_model": glm_config.get("model", "glm-4.5-air"),
                            "glm_rpm": glm_config.get("requests_per_minute", 30),
                            "glm_cost": glm_config.get("cost_per_request", 0.001),
                            "glm_budget": glm_config.get("daily_budget", 30.0),
                            # Baichuan/DeepSeek configuration
                            "baichuan_api_key": baichuan_config.get("api_key", ""),
                            "baichuan_enabled": baichuan_config.get("enabled", False),
                            "baichuan_model": baichuan_config.get("model", "deepseek-chat"),
                            "baichuan_rpm": baichuan_config.get("requests_per_minute", 25),
                            "baichuan_cost": baichuan_config.get("cost_per_request", 0.0015),
                            "baichuan_budget": baichuan_config.get("daily_budget", 20.0),
                            # Cache configuration
                            "cache_ttl_market": chinese_config.get("cache_ttl_market_hours", 120),
                            "cache_ttl_off": chinese_config.get("cache_ttl_off_hours", 60),
                        }

            if config or True:  # Initialize even without config (will use defaults)
                self.data_sources["chinese_models"] = ChineseModelsDataSource(config)
                logger.info("✅ Chinese Models data source initialized (10% weight, 20% off-hours)")
        except Exception as e:
            logger.warning(f"Chinese Models init error: {e}", exc_info=True)

    def _init_enhancements(self, config_path: Optional[str]):
        """Initialize all enhancement modules"""
        try:
            config = {}
            if config_path:
                with open(config_path) as f:
                    full_config = json.load(f)
                    config = full_config

            # Initialize Data Quality Monitor
            try:
                from argo.core.feature_flags import get_feature_flags

                feature_flags = get_feature_flags()
                if feature_flags.is_enabled("data_quality_validation"):
                    self.data_quality_monitor = DataQualityMonitor()
                    # Update thresholds from config if available
                    if "enhancements" in config and "data_quality" in config["enhancements"]:
                        dq_config = config["enhancements"]["data_quality"]
                        self.data_quality_monitor.quality_thresholds.update(
                            {
                                "max_staleness_seconds": dq_config.get(
                                    "max_staleness_seconds", 300
                                ),
                                "max_price_deviation_pct": dq_config.get(
                                    "max_price_deviation_pct", 5.0
                                ),
                                "min_confidence": dq_config.get("min_confidence", 60.0),
                            }
                        )
                    logger.info("✅ Data Quality Monitor initialized")
                else:
                    self.data_quality_monitor = None
            except Exception as e:
                logger.warning(f"Data Quality Monitor init error: {e}")
                self.data_quality_monitor = None

            # Initialize Risk Monitor (with prop firm support)
            try:
                if feature_flags.is_enabled("risk_monitoring"):
                    # Check if prop firm mode is enabled
                    prop_firm_config = config.get("prop_firm", {})
                    prop_firm_enabled = prop_firm_config.get("enabled", False)

                    if prop_firm_enabled:
                        # Use prop firm configuration
                        risk_limits = prop_firm_config.get("risk_limits", {})
                        risk_monitor_config = {
                            "max_drawdown_pct": risk_limits.get("max_drawdown_pct", 2.0),
                            "daily_loss_limit_pct": risk_limits.get("daily_loss_limit_pct", 4.5),
                            "initial_capital": 25000.0,  # Default, will be updated from account
                        }
                        self.risk_monitor = PropFirmRiskMonitor(risk_monitor_config)
                        self.prop_firm_mode = True
                        self.prop_firm_config = prop_firm_config

                        # Update confidence threshold for prop firm mode
                        prop_min_confidence = risk_limits.get("min_confidence", 82.0)
                        if prop_min_confidence > self.confidence_threshold:
                            self.confidence_threshold = prop_min_confidence
                            logger.info(
                                f"✅ Updated confidence threshold to {prop_min_confidence}% for prop firm mode"
                            )

                        logger.info("✅ Prop Firm Risk Monitor initialized (PROP FIRM MODE)")
                    else:
                        # Use standard risk monitoring
                        risk_config = config.get("enhancements", {}).get("risk_monitoring", {})
                        trading_config = config.get("trading", {})
                        risk_monitor_config = {
                            "max_drawdown_pct": risk_config.get(
                                "max_drawdown_pct", trading_config.get("max_drawdown_pct", 2.0)
                            ),
                            "daily_loss_limit_pct": risk_config.get(
                                "daily_loss_limit_pct",
                                trading_config.get("daily_loss_limit_pct", 4.5),
                            ),
                            "initial_capital": 25000.0,
                        }
                        self.risk_monitor = PropFirmRiskMonitor(risk_monitor_config)
                        self.prop_firm_mode = False
                        logger.info("✅ Prop Firm Risk Monitor initialized (STANDARD MODE)")
                else:
                    self.risk_monitor = None
                    self.prop_firm_mode = False
            except Exception as e:
                logger.warning(f"Risk Monitor init error: {e}")
                self.risk_monitor = None
                self.prop_firm_mode = False

            # Initialize Adaptive Weight Manager
            try:
                if feature_flags.is_enabled("adaptive_weights"):
                    # Get initial weights from consensus engine
                    initial_weights = {
                        "massive": 0.4,
                        "alpaca_pro": 0.4,
                        "alpha_vantage": 0.25,
                        "yfinance": 0.25,
                        "x_sentiment": 0.2,
                        "sonar": 0.15,
                        "chinese_models": 0.10,
                    }
                    # Update from config if available
                    strategy_config = config.get("strategy", {})
                    if "weight_massive" in strategy_config:
                        initial_weights["massive"] = strategy_config["weight_massive"]
                    if "weight_chinese_models" in strategy_config:
                        initial_weights["chinese_models"] = strategy_config["weight_chinese_models"]

                    self.adaptive_weight_manager = AdaptiveWeightManager(initial_weights)
                    logger.info("✅ Adaptive Weight Manager initialized")
                else:
                    self.adaptive_weight_manager = None
            except Exception as e:
                logger.warning(f"Adaptive Weight Manager init error: {e}")
                self.adaptive_weight_manager = None

            # Initialize Performance Monitor
            try:
                if feature_flags.is_enabled("performance_monitoring"):
                    # Pass config to performance monitor so it can read budgets (force reload to use new config)
                    self.performance_monitor = get_performance_monitor(
                        config=config, force_reload=True
                    )
                    # Budgets are now loaded from config in PerformanceMonitor.__init__
                    if "enhancements" in config and "performance_budgets" in config["enhancements"]:
                        perf_config = config["enhancements"]["performance_budgets"]
                        signal_max = perf_config.get("signal_generation_max_ms", 10000)
                        fetch_max = perf_config.get("data_source_fetch_max_ms", 5000)
                        logger.info(
                            f"✅ Performance Monitor initialized with budgets from config: signal_generation={signal_max}ms, data_source_fetch={fetch_max}ms"
                        )
                    logger.info("✅ Performance Monitor initialized")
                else:
                    self.performance_monitor = None
            except Exception as e:
                logger.warning(f"Performance Monitor init error: {e}")
                self.performance_monitor = None

        except Exception as e:
            logger.error(f"Error initializing enhancements: {e}", exc_info=True)

    def _log_data_source_summary(self):
        """Log summary of initialized data sources"""
        if not self.data_sources:
            logger.warning("⚠️  No data sources initialized - using fallback mode")
        else:
            logger.info(
                f"✅ Initialized {len(self.data_sources)} data source(s): {', '.join(self.data_sources.keys())}"
            )

    async def generate_signal_for_symbol(self, symbol: str) -> Optional[Dict]:
        """
        Generate a signal for a single symbol using weighted consensus
        OPTIMIZED: Parallel data source fetching, early exit, caching, eliminated redundant API calls,
        skip unchanged symbols, priority-based processing

        Returns:
            Dict with signal data or None if no valid signal
        """
        # Performance monitoring
        perf_context = self._start_performance_monitoring()

        try:
            # Early exit: Check cached signal if symbol hasn't changed
            cached_signal = self._check_cached_signal(symbol)
            if cached_signal:
                return cached_signal

            # Step 1: Fetch and validate market data
            source_signals, market_data_df = await self._fetch_and_validate_market_data(symbol)
            if not source_signals:
                return None

            # Early exit: Check price change threshold
            cached_signal = self._check_price_change_threshold(symbol, market_data_df)
            if cached_signal:
                return cached_signal

            # Early exit: Incremental confidence check
            if self._should_exit_early_on_confidence(source_signals, symbol):
                return None

            # Step 2: Fetch independent sources and validate
            source_signals = await self._fetch_and_validate_all_sources(
                symbol, source_signals, market_data_df
            )
            if not source_signals:
                return None

            # Step 3: Calculate consensus and validate threshold
            consensus, regime = await self._calculate_and_validate_consensus(
                symbol, source_signals, market_data_df
            )
            if not consensus:
                return None

            # Step 4: Build and finalize signal
            signal = await self._build_and_finalize_signal(
                symbol, consensus, source_signals, market_data_df
            )

            return signal

        except Exception as e:
            logger.error(f"❌ Error generating signal for {symbol}: {e}")
            return None
        finally:
            self._stop_performance_monitoring(perf_context)

    def _start_performance_monitoring(self):
        """Start performance monitoring context"""
        if self.performance_monitor:
            perf_context = self.performance_monitor.measure("signal_generation")
            perf_context.__enter__()
            return perf_context
        return None

    def _stop_performance_monitoring(self, perf_context):
        """Stop performance monitoring context"""
        if perf_context:
            perf_context.__exit__(None, None, None)

    def _check_cached_signal(self, symbol: str) -> Optional[Dict]:
        """Check if we should return cached signal (early exit optimization)"""
        if self._should_skip_symbol(symbol):
            cached_signal = self._last_signals.get(symbol)
            if cached_signal:
                logger.debug(
                    f"⏭️  Skipping {symbol} - price change < {self._price_change_threshold*100}%"
                )
                return cached_signal
        return None

    async def _fetch_and_validate_market_data(self, symbol: str) -> Tuple[Dict, Optional[Any]]:
        """Fetch market data signals and optimize DataFrame memory"""
        source_signals = {}
        market_data_df = await self._fetch_market_data_signals(symbol, source_signals)

        # Optimize DataFrame memory usage
        if market_data_df is not None:
            market_data_df = self._optimize_dataframe_memory(market_data_df)

        # Early exit if no market data
        if not source_signals:
            logger.warning(
                f"⚠️  Early exit: No source signals generated for {symbol} (market data fetch may have failed)"
            )
            return {}, None

        return source_signals, market_data_df

    def _check_price_change_threshold(
        self, symbol: str, market_data_df: Optional[Any]
    ) -> Optional[Dict]:
        """Check if price has changed significantly (early exit optimization)"""
        if market_data_df is not None and len(market_data_df) > 0:
            current_price = float(market_data_df.iloc[-1]["Close"])
            if symbol in self._last_prices and symbol in self._last_signals:
                price_change = (
                    abs(current_price - self._last_prices[symbol]) / self._last_prices[symbol]
                )
                if price_change < self._price_change_threshold:
                    logger.debug(
                        f"⏭️  Skipping {symbol} - price change {price_change*100:.2f}% < {self._price_change_threshold*100}%"
                    )
                    if self.performance_metrics:
                        self.performance_metrics.record_skipped_symbol()
                    return self._last_signals[symbol]
        return None

    def _should_exit_early_on_confidence(self, source_signals: Dict, symbol: str) -> bool:
        """Check if we should exit early based on incremental confidence (early exit optimization)"""
        try:
            from argo.core.feature_flags import get_feature_flags

            feature_flags = get_feature_flags()

            if feature_flags.is_enabled("incremental_confidence"):
                # Early exit check after primary sources (80% weight: Massive + Alpha)
                partial_consensus = self._calculate_partial_consensus(source_signals, symbol)
                if partial_consensus:
                    max_possible = self._calculate_max_possible_confidence(
                        source_signals, remaining_weight=0.20  # xAI + Sonar remaining
                    )
                    threshold = self.confidence_threshold
                    if max_possible < threshold:
                        logger.debug(
                            f"⏭️  Early exit: Max possible confidence ({max_possible:.1f}%) < {threshold}% threshold for {symbol}"
                        )
                        return True
        except Exception as e:
            logger.debug(f"Could not check incremental confidence: {e}")
        return False

    async def _fetch_and_validate_all_sources(
        self, symbol: str, source_signals: Dict, market_data_df: Optional[Any]
    ) -> Dict:
        """Fetch independent sources and validate with data quality monitor"""
        # Fetch independent sources in parallel
        await self._fetch_independent_source_signals(symbol, source_signals, market_data_df)

        # Validate source signals with data quality monitor (batched)
        if self.data_quality_monitor:
            validated_signals = await self._validate_signals_batch(
                list(source_signals.items()),
                {
                    "price": (
                        market_data_df.iloc[-1]["Close"]
                        if market_data_df is not None and len(market_data_df) > 0
                        else None
                    )
                },
            )
            source_signals = {name: sig for name, sig in validated_signals}
            if not source_signals:
                logger.warning(f"⚠️  All signals rejected by data quality monitor for {symbol}")
                return {}

        return source_signals

    async def _calculate_and_validate_consensus(
        self, symbol: str, source_signals: Dict, market_data_df: Optional[Any]
    ) -> Tuple[Optional[Dict], str]:
        """Calculate weighted consensus and validate against threshold"""
        # Get regime with caching
        regime = await self._get_cached_regime(market_data_df, symbol)

        # Calculate consensus
        consensus = self._calculate_consensus(source_signals, symbol, regime)
        if not consensus:
            logger.warning(
                f"⚠️  No consensus calculated for {symbol} - source signals: {list(source_signals.keys())}"
            )
            return None, regime

        # Apply adaptive threshold check
        threshold = self.regime_thresholds.get(regime, self.confidence_threshold)
        if consensus["confidence"] < threshold:
            logger.warning(
                f"⚠️  Consensus confidence {consensus['confidence']:.1f}% below {threshold}% threshold for {symbol} ({regime}) - source signals: {list(source_signals.keys())}"
            )
            return None, regime

        return consensus, regime

    async def _build_and_finalize_signal(
        self, symbol: str, consensus: Dict, source_signals: Dict, market_data_df: Optional[Any]
    ) -> Dict:
        """Build final signal, apply regime adjustment, generate reasoning, and update cache"""
        # Apply regime detection and adjust confidence
        consensus = await self._apply_regime_adjustment(consensus, symbol, market_data_df)

        # Build final signal
        signal = self._build_signal(symbol, consensus, source_signals)

        # Generate AI reasoning (with caching)
        signal["reasoning"] = self._generate_reasoning(signal, consensus)

        # Update last price and signal cache
        if market_data_df is not None and len(market_data_df) > 0:
            current_price = float(market_data_df.iloc[-1]["Close"])
            self._last_prices[symbol] = current_price
            self._last_signals[symbol] = signal

            # Update volatility tracking
            self._update_volatility(symbol, market_data_df)

        return signal

    def _should_skip_symbol(self, symbol: str) -> bool:
        """Check if symbol should be skipped (price hasn't changed significantly)"""
        if symbol not in self._last_prices or symbol not in self._last_signals:
            return False  # First time, don't skip

        # Get current price from cache or return False to fetch
        # This is a quick check - we'll verify after fetching market data
        return False  # Always fetch to check, but we'll use this in generate_signals_cycle

    def _update_volatility(self, symbol: str, df):
        """Update volatility tracking for priority-based processing (OPTIMIZED: vectorized)"""
        try:
            if len(df) < 5:
                return

            # OPTIMIZATION: Vectorized volatility calculation (5-10x faster than list comprehension)
            # Calculate recent volatility (last 5 days) using pandas vectorized operations
            recent_prices = df["Close"].tail(5)
            price_changes = recent_prices.pct_change().abs()
            volatility = (
                price_changes.mean()
                if len(price_changes) > 0 and not price_changes.isna().all()
                else 0.0
            )

            # Handle NaN values (first row will be NaN from pct_change)
            if pd.isna(volatility):
                volatility = 0.0

            self._symbol_volatility[symbol] = float(volatility)
        except Exception:
            pass

    async def _fetch_all_source_signals(self, symbol: str) -> Tuple[Dict[str, Dict], Optional[Any]]:
        """Fetch signals from all available data sources"""
        source_signals = {}
        market_data_df = None

        # Fetch market data sources (sequential with fallback)
        market_data_df = await self._fetch_market_data_signals(symbol, source_signals)

        # Fetch independent sources in parallel (pass market_data_df for Chinese models)
        await self._fetch_independent_source_signals(symbol, source_signals, market_data_df)

        return source_signals, market_data_df

    async def _fetch_market_data_signals(self, symbol: str, source_signals: Dict) -> Optional[Any]:
        """
        Fetch market data signals with parallel fetching (race condition pattern)
        OPTIMIZATION: Fetches from multiple sources in parallel, uses first successful response
        """
        market_data_df = None
        tasks = []
        task_metadata = {}

        # OPTIMIZATION: Fetch from all available sources in parallel
        if "alpaca_pro" in self.data_sources:
            task = asyncio.create_task(
                self.data_sources["alpaca_pro"].fetch_price_data(symbol, days=200)
            )
            tasks.append(task)
            task_metadata[id(task)] = "alpaca_pro"

        if "massive" in self.data_sources:
            task = asyncio.create_task(
                self.data_sources["massive"].fetch_price_data(symbol, days=200)
            )
            tasks.append(task)
            task_metadata[id(task)] = "massive"

        if not tasks:
            return None

        # Race: Use first successful response (with 30 second timeout for 200 days of data)
        try:
            done, pending = await asyncio.wait(
                tasks, return_when=asyncio.FIRST_COMPLETED, timeout=30.0
            )

            # Get first successful result from completed tasks
            for task in done:
                try:
                    result = await task
                    # Check if result is a DataFrame with data (not an exception)
                    if result is not None and not isinstance(result, Exception):
                        # Check if it's a DataFrame and has data
                        if hasattr(result, "empty") and not result.empty:
                            source_name = task_metadata[id(task)]
                            market_data_df = result

                            # Generate signal from successful source
                            signal = self.data_sources[source_name].generate_signal(
                                market_data_df, symbol
                            )
                            if signal:
                                source_signals[source_name] = signal
                                logger.info(
                                    f"✅ {source_name} signal for {symbol}: {signal.get('direction')} @ {signal.get('confidence')}%"
                                )

                            # Cancel remaining tasks since we got a valid result
                            for pending_task in pending:
                                pending_task.cancel()
                                try:
                                    await pending_task
                                except asyncio.CancelledError:
                                    pass

                            return market_data_df
                except asyncio.CancelledError:
                    # Task was cancelled, skip it
                    pass
                except Exception as e:
                    logger.debug(
                        f"Market data source {task_metadata.get(id(task), 'unknown')} error for {symbol}: {e}"
                    )

            # If no successful result from completed tasks, wait for remaining tasks
            if not market_data_df and pending:
                logger.debug(
                    f"⏳ No valid data from completed tasks, waiting for remaining {len(pending)} task(s) for {symbol}"
                )
                try:
                    # Wait for remaining tasks with shorter timeout
                    remaining_done, remaining_pending = await asyncio.wait(
                        pending, return_when=asyncio.ALL_COMPLETED, timeout=20.0
                    )

                    # Check remaining tasks
                    for task in remaining_done:
                        try:
                            result = await task
                            if result is not None and not isinstance(result, Exception):
                                if hasattr(result, "empty") and not result.empty:
                                    source_name = task_metadata[id(task)]
                                    market_data_df = result
                                    signal = self.data_sources[source_name].generate_signal(
                                        market_data_df, symbol
                                    )
                                    if signal:
                                        source_signals[source_name] = signal
                                        logger.info(
                                            f"✅ {source_name} signal for {symbol}: {signal.get('direction')} @ {signal.get('confidence')}%"
                                        )
                                    return market_data_df
                        except asyncio.CancelledError:
                            pass
                        except Exception as e:
                            logger.debug(
                                f"Market data source {task_metadata.get(id(task), 'unknown')} error for {symbol}: {e}"
                            )

                    # Cancel any still-pending tasks
                    for task in remaining_pending:
                        task.cancel()
                        try:
                            await task
                        except asyncio.CancelledError:
                            pass

                except asyncio.TimeoutError:
                    logger.debug(f"⏱️  Remaining tasks timed out for {symbol}")
                    # Cancel remaining tasks
                    for task in pending:
                        task.cancel()
                        try:
                            await task
                        except asyncio.CancelledError:
                            pass
            else:
                # No pending tasks, cancel them if we didn't get a result
                for task in pending:
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass

        except asyncio.TimeoutError:
            logger.warning(f"⚠️  Market data fetch timeout for {symbol} (30s timeout exceeded)")
            # Cancel all tasks
            for task in tasks:
                task.cancel()

        if not market_data_df:
            logger.warning(
                f"⚠️  No market data retrieved for {symbol} - all data sources failed or timed out"
            )

        return market_data_df

    async def _fetch_independent_source_signals(
        self, symbol: str, source_signals: Dict, market_data_df=None
    ):
        """Fetch independent data sources in parallel"""
        independent_tasks = []
        task_metadata = {}

        # Prepare market data for Chinese models
        market_data = {}
        if market_data_df is not None and len(market_data_df) > 0:
            try:
                market_data = {
                    "price": float(market_data_df.iloc[-1]["Close"]),
                    "bid": float(market_data_df.iloc[-1]["Close"]) * 0.9999,
                    "ask": float(market_data_df.iloc[-1]["Close"]) * 1.0001,
                    "volatility": 0.02,
                    "avg_volume": 1000000,
                }
            except Exception:
                pass

        # Create tasks for parallel execution
        if "yfinance" in self.data_sources:
            task = asyncio.create_task(
                asyncio.to_thread(self.data_sources["yfinance"].fetch_technical_indicators, symbol)
            )
            independent_tasks.append(task)
            task_metadata[id(task)] = ("yfinance", "indicators")

        if "alpha_vantage" in self.data_sources:
            task = asyncio.create_task(
                self.data_sources["alpha_vantage"].fetch_technical_indicators(symbol)
            )
            independent_tasks.append(task)
            task_metadata[id(task)] = ("alpha_vantage", "indicators")

        if "x_sentiment" in self.data_sources:
            task = asyncio.create_task(self.data_sources["x_sentiment"].fetch_sentiment(symbol))
            independent_tasks.append(task)
            task_metadata[id(task)] = ("x_sentiment", "sentiment")

        if "sonar" in self.data_sources:
            task = asyncio.create_task(self.data_sources["sonar"].fetch_analysis(symbol))
            independent_tasks.append(task)
            task_metadata[id(task)] = ("sonar", "analysis")

        # Add Chinese models if available
        if "chinese_models" in self.data_sources:
            task = asyncio.create_task(
                self.data_sources["chinese_models"].get_signal(symbol, market_data)
            )
            independent_tasks.append(task)
            task_metadata[id(task)] = ("chinese_models", "ai_analysis")

        # Wait for all tasks and process results
        if independent_tasks:
            results = await asyncio.gather(*independent_tasks, return_exceptions=True)
            self._process_independent_results(
                symbol, independent_tasks, results, task_metadata, source_signals
            )

    def _process_independent_results(
        self, symbol: str, tasks: List, results: List, task_metadata: Dict, source_signals: Dict
    ):
        """Process results from independent data source tasks"""
        yfinance_attempted = False
        yfinance_exception = False

        for task, result in zip(tasks, results):
            source_name, data_type = task_metadata[id(task)]

            if isinstance(result, Exception):
                logger.debug(f"{source_name} error for {symbol}: {result}")
                if source_name == "yfinance":
                    yfinance_attempted = True
                    yfinance_exception = True
                continue

            if source_name == "yfinance":
                yfinance_attempted = True
                if result:
                    signal = self.data_sources["yfinance"].generate_signal(result, symbol)
                    if signal:
                        source_signals["yfinance"] = signal
                        logger.info(
                            f"✅ yfinance signal for {symbol}: {signal.get('direction')} @ {signal.get('confidence')}%"
                        )
                    else:
                        logger.debug(
                            f"⏭️  yfinance returned no signal for {symbol} (confidence < 60%)"
                        )
                else:
                    logger.debug(f"⏭️  yfinance returned no indicators for {symbol}")

            elif source_name == "alpha_vantage":
                if result:
                    signal = self.data_sources["alpha_vantage"].generate_signal(result, symbol)
                    if signal:
                        self._handle_alpha_vantage_signal(
                            symbol, signal, source_signals, yfinance_attempted, yfinance_exception
                        )

            elif source_name == "x_sentiment" and result:
                signal = self.data_sources["x_sentiment"].generate_signal(result, symbol)
                if signal:
                    source_signals["x_sentiment"] = signal

            elif source_name == "sonar" and result:
                signal = self.data_sources["sonar"].generate_signal(result, symbol)
                if signal:
                    source_signals["sonar"] = signal

            elif source_name == "chinese_models" and result:
                # Chinese models already return signal format
                if result:
                    source_signals["chinese_models"] = result
                    logger.info(
                        f"✅ Chinese Models signal for {symbol}: {result.get('direction')} @ {result.get('confidence')}%"
                    )

    def _handle_alpha_vantage_signal(
        self,
        symbol: str,
        signal: Dict,
        source_signals: Dict,
        yfinance_attempted: bool,
        yfinance_exception: bool,
    ):
        """Handle Alpha Vantage signal with yfinance fallback logic"""
        if not yfinance_attempted:
            source_signals["alpha_vantage"] = signal
            logger.info(
                f"✅ Alpha Vantage signal for {symbol}: {signal.get('direction')} @ {signal.get('confidence')}%"
            )
        elif yfinance_exception:
            source_signals["alpha_vantage"] = signal
            logger.info(
                f"✅ Alpha Vantage signal (yfinance exception fallback) for {symbol}: {signal.get('direction')} @ {signal.get('confidence')}%"
            )
        elif "yfinance" in source_signals:
            yf_signal = source_signals["yfinance"]
            if signal.get("confidence", 0) > yf_signal.get("confidence", 0):
                source_signals.pop("yfinance", None)
                source_signals["alpha_vantage"] = signal
                logger.info(
                    f"✅ Alpha Vantage signal (higher confidence) for {symbol}: {signal.get('direction')} @ {signal.get('confidence')}%"
                )

    def _calculate_consensus(
        self, source_signals: Dict, symbol: str, regime: Optional[str] = None
    ) -> Optional[Dict]:
        """Calculate weighted consensus from source signals (OPTIMIZED: with caching and regime-based weights)"""
        # OPTIMIZATION: Cache current time to avoid multiple datetime.now() calls
        current_time = datetime.now(timezone.utc)

        # OPTIMIZATION: Create cache key from source signals
        cache_key = self._create_consensus_cache_key(source_signals, symbol)

        # Check cache first (but only if regime hasn't changed)
        if cache_key in self._consensus_cache:
            cached_consensus, cache_time = self._consensus_cache[cache_key]
            age = (current_time - cache_time).total_seconds()
            if age < self._consensus_cache_ttl:
                logger.debug(f"✅ Using cached consensus for {symbol}")
                # OPTIMIZATION: Use shallow copy for dict (faster than deep copy)
                # Only copy if we need to modify, otherwise return reference
                import copy
                return copy.copy(cached_consensus)  # Shallow copy is sufficient for dict

        # OPTIMIZATION: Only create signal summary if logging is enabled (avoid unnecessary work)
        if logger.isEnabledFor(logging.INFO):
            signal_summary = [
                (s, sig.get("direction"), f"{sig.get('confidence')}%")
                for s, sig in source_signals.items()
            ]
            logger.info(f"📊 Source signals for {symbol}: {signal_summary}")

        consensus_input = {
            source: {
                "direction": signal.get("direction", "NEUTRAL"),
                "confidence": signal.get("confidence", 0) / 100.0,
            }
            for source, signal in source_signals.items()
        }

        # Use adaptive weights if enabled
        if self.adaptive_weight_manager:
            # Get current adaptive weights
            adaptive_weights = self.adaptive_weight_manager.adjust_weights()
            # Temporarily update consensus engine weights
            original_weights = self.consensus_engine.weights.copy()
            self.consensus_engine.weights.update(adaptive_weights)
            logger.debug(f"Using adaptive weights: {adaptive_weights}")

        # Pass regime to consensus engine for regime-based weights
        consensus = self.consensus_engine.calculate_consensus(consensus_input, regime=regime)

        # Restore original weights if we used adaptive weights
        if self.adaptive_weight_manager:
            self.consensus_engine.weights = original_weights

        if not consensus:
            logger.info(
                f"ℹ️  No consensus calculated for {symbol} - signals may conflict or be neutral"
            )
            return None

        # Store regime in consensus for later use
        if regime:
            consensus["regime"] = regime

        threshold = self.regime_thresholds.get(regime or "UNKNOWN", self.confidence_threshold)
        logger.info(
            f"📈 Consensus for {symbol}: {consensus.get('direction')} @ {consensus.get('confidence')}% (threshold: {threshold}%, regime: {regime or 'UNKNOWN'})"
        )

        # Cache the result (use cached current_time)
        # OPTIMIZATION: Use shallow copy for dict (faster than deep copy)
        import copy
        self._consensus_cache[cache_key] = (copy.copy(consensus), current_time)
        self._cleanup_consensus_cache()

        return consensus

    def _create_consensus_cache_key(self, source_signals: Dict, symbol: str) -> str:
        """Create cache key from source signals signature (OPTIMIZED: faster string building)"""
        # OPTIMIZATION: Use list comprehension and join for better performance
        if not source_signals:
            return f"{symbol}:"

        signal_summary = [
            f"{source}:{signal.get('direction', 'NEUTRAL')}:{int(signal.get('confidence', 0) // 5) * 5}"
            for source, signal in sorted(source_signals.items())
        ]
        return f"{symbol}:{':'.join(signal_summary)}"

    def _cleanup_regime_cache(self):
        """Remove old regime cache entries to prevent memory growth"""
        if len(self._regime_cache) < self._regime_cache_max_size:
            return
        
        now = datetime.now(timezone.utc)
        expired_keys = []
        for key, (regime, cache_time) in self._regime_cache.items():
            if (now - cache_time).total_seconds() >= self._regime_cache_ttl:
                expired_keys.append(key)
        
        # Remove expired entries
        for key in expired_keys:
            del self._regime_cache[key]
        
        # If still too large, remove oldest entries
        if len(self._regime_cache) >= self._regime_cache_max_size:
            entries_to_remove = len(self._regime_cache) - int(self._regime_cache_max_size * 0.8)  # Keep 80%
            sorted_entries = sorted(
                self._regime_cache.items(),
                key=lambda x: x[1][1]  # Sort by timestamp
            )
            for key, _ in sorted_entries[:int(entries_to_remove)]:
                del self._regime_cache[key]
        
        logger.debug(f"🧹 Cleaned regime cache: {len(expired_keys)} expired, {len(self._regime_cache)} remaining")

    def _cleanup_consensus_cache(self):
        """Remove old cache entries to prevent memory growth (OPTIMIZED: efficient cleanup)"""
        if len(self._consensus_cache) > 1000:  # Max 1000 entries
            # OPTIMIZATION: Use list of (timestamp, key) tuples and sort only what we need
            # This is more efficient than sorting all entries when we only need the oldest 20%
            entries_to_remove = len(self._consensus_cache) // 5
            timestamp_key_pairs = [
                (cache_time, key) for key, (_, cache_time) in self._consensus_cache.items()
            ]
            # Sort only to get the oldest entries
            timestamp_key_pairs.sort()
            for _, key in timestamp_key_pairs[:entries_to_remove]:
                del self._consensus_cache[key]

    def _calculate_partial_consensus(self, source_signals: Dict, symbol: str) -> Optional[Dict]:
        """Calculate partial consensus for early exit check"""
        if not source_signals:
            return None

        consensus_input = {
            source: {
                "direction": signal.get("direction", "NEUTRAL"),
                "confidence": signal.get("confidence", 0) / 100.0,
            }
            for source, signal in source_signals.items()
        }

        return self.consensus_engine.calculate_consensus(consensus_input)

    def _calculate_max_possible_confidence(
        self, source_signals: Dict, remaining_weight: float = 0.20
    ) -> float:
        """Calculate maximum possible confidence if all remaining sources are perfect"""
        if not source_signals:
            return 0.0

        # Calculate current confidence
        current_consensus = self._calculate_partial_consensus(source_signals, "")
        if not current_consensus:
            return 0.0

        current_confidence = current_consensus.get("confidence", 0)

        # Calculate max additional confidence from remaining sources (assuming 100% confidence)
        # Remaining weight represents sources not yet fetched
        max_additional = remaining_weight * 100.0  # If remaining sources are 100% confident

        # Get actual weights from consensus engine
        weights = getattr(self.consensus_engine, "weights", {})
        if not weights:
            # Fallback to default weights if not available
            weights = {
                "massive": 0.40,
                "alpaca_pro": 0.40,
                "alpha_vantage": 0.25,
                "yfinance": 0.25,
                "x_sentiment": 0.20,
                "sonar": 0.15,
            }

        # Calculate max possible with remaining sources (assuming 100% confidence)
        # OPTIMIZATION: Use dict() constructor for shallow copy (slightly faster than .copy())
        remaining_weights = dict(weights)

        # Remove weights for sources we already have
        for source in source_signals.keys():
            if source in remaining_weights:
                del remaining_weights[source]

        # Add max possible from remaining sources (assume 100% confidence, same direction)
        max_additional = sum(remaining_weights.values()) * 100.0

        return min(current_confidence + max_additional, 100.0)

    async def _get_cached_regime(self, market_data_df: Optional, symbol: str) -> str:
        """
        Get cached regime for market data (OPTIMIZATION 7)
        Returns cached regime if available, otherwise detects and caches it
        """
        if market_data_df is None or len(market_data_df) < 200:
            return "UNKNOWN"

        # Create hash of last 200 rows (regime detection window)
        try:
            import hashlib

            data_hash = hashlib.md5(market_data_df.tail(200).to_string().encode()).hexdigest()

            cache_key = f"regime:{data_hash}"

            # Check Redis cache first
            if self.redis_cache:
                cached = (
                    await self.redis_cache.aget(cache_key)
                    if hasattr(self.redis_cache, "aget")
                    else self.redis_cache.get(cache_key)
                )
                if cached:
                    logger.debug(f"✅ Using cached regime: {cached}")
                    return cached

            # Check in-memory cache
            if cache_key in self._regime_cache:
                cached_regime, cache_time = self._regime_cache[cache_key]
                cache_age = (datetime.now(timezone.utc) - cache_time).total_seconds()
                if cache_age < self._regime_cache_ttl:
                    logger.debug(f"✅ Using in-memory cached regime: {cached_regime}")
                    return cached_regime
                else:
                    # Remove expired entry
                    del self._regime_cache[cache_key]

            # Detect regime
            try:
                from argo.core.regime_detector import (
                    detect_regime,
                    detect_regime_enhanced,
                    map_legacy_regime_to_enhanced,
                )

                legacy_regime = detect_regime(market_data_df)
                regime = map_legacy_regime_to_enhanced(legacy_regime)

                # Cache result
                ttl = self._regime_cache_ttl  # 5 minute cache
                if self.redis_cache:
                    if hasattr(self.redis_cache, "aset"):
                        await self.redis_cache.aset(cache_key, regime, ttl=ttl)
                    else:
                        self.redis_cache.set(cache_key, regime, ttl=ttl)

                # Cleanup old entries if cache is too large
                if len(self._regime_cache) >= self._regime_cache_max_size:
                    self._cleanup_regime_cache()
                
                self._regime_cache[cache_key] = (regime, datetime.now(timezone.utc))

                return regime
            except Exception as e:
                logger.debug(f"Regime detection error: {e}")
                return "UNKNOWN"
        except Exception as e:
            logger.debug(f"Regime caching error: {e}")
            return "UNKNOWN"

    async def _apply_regime_adjustment(
        self, consensus: Dict, symbol: str, market_data_df: Optional
    ) -> Dict:
        """Apply market regime detection and adjust confidence (OPTIMIZATION 7: uses cached regime)"""
        regime = consensus.get("regime", "UNKNOWN")

        # If regime not already set, get it (with caching)
        if regime == "UNKNOWN" and market_data_df is not None and len(market_data_df) >= 200:
            regime = await self._get_cached_regime(market_data_df, symbol)
            try:
                from argo.core.regime_detector import detect_regime, adjust_confidence

                # Get legacy regime for adjustment
                legacy_regime = detect_regime(market_data_df)
                consensus["confidence"] = adjust_confidence(consensus["confidence"], legacy_regime)
            except Exception as e:
                logger.debug(f"Regime adjustment error: {e}")
        elif regime == "UNKNOWN" and "massive" in self.data_sources and market_data_df is None:
            try:
                from argo.core.regime_detector import (
                    detect_regime,
                    map_legacy_regime_to_enhanced,
                    adjust_confidence,
                )

                df = await self.data_sources["massive"].fetch_price_data(symbol, days=200)
                if df is not None:
                    regime = await self._get_cached_regime(df, symbol)
                    legacy_regime = detect_regime(df)
                    consensus["confidence"] = adjust_confidence(
                        consensus["confidence"], legacy_regime
                    )
            except Exception as e:
                logger.debug(f"Regime detection error: {e}")

        consensus["regime"] = regime
        return consensus

    def _build_signal(self, symbol: str, consensus: Dict, source_signals: Dict) -> Dict:
        """Build final signal dictionary with confidence calibration (v5.0)"""
        direction = consensus["direction"]
        action = "BUY" if direction == "LONG" else "SELL"

        entry_price = self._get_entry_price(source_signals, symbol)
        stop_loss, take_profit = self._calculate_stop_and_target(entry_price, action)

        # Apply confidence calibration (v5.0 optimization)
        raw_confidence = consensus["confidence"]
        if self._confidence_calibrator:
            calibrated_confidence = self._confidence_calibrator.calibrate(raw_confidence, symbol)
            logger.debug(
                f"📊 Confidence calibration for {symbol}: {raw_confidence}% → {calibrated_confidence}%"
            )
        else:
            calibrated_confidence = raw_confidence

        signal = {
            "symbol": symbol,
            "action": action,
            "entry_price": round(entry_price, 2),
            "target_price": round(take_profit, 2),
            "stop_price": round(stop_loss, 2),
            "confidence": round(calibrated_confidence, 2),
            "raw_confidence": round(raw_confidence, 2),  # Store raw for comparison
            "strategy": "weighted_consensus_v6",
            "asset_type": "crypto" if "-USD" in symbol else "stock",
            "data_source": "weighted_consensus",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "regime": consensus.get("regime", "UNKNOWN"),
            "consensus_agreement": consensus.get("agreement", 0),
            "sources_count": consensus.get("sources", 0),
        }

        # Calculate quality score if scorer is available
        if hasattr(self, "_quality_scorer") and self._quality_scorer:
            try:
                quality_result = self._quality_scorer.calculate_quality_score(signal)
                signal["quality_score"] = quality_result["quality_score"]
                signal["quality_tier"] = quality_result["quality_tier"]
                signal["quality_components"] = quality_result["components"]
            except Exception as e:
                logger.debug(f"Could not calculate quality score: {e}")

        return signal

    def _get_entry_price(self, source_signals: Dict, symbol: str) -> float:
        """Get entry price from primary source or fallback"""
        if "massive" in source_signals:
            return source_signals["massive"].get("entry_price")
        elif "alpha_vantage" in source_signals:
            return source_signals["alpha_vantage"].get("indicators", {}).get("current_price")

        # Fallback to defaults
        price_defaults = {
            "AAPL": 175.0,
            "NVDA": 460.0,
            "TSLA": 260.0,
            "MSFT": 161.0,
            "BTC-USD": 40000.0,
            "ETH-USD": 2500.0,
        }
        return price_defaults.get(symbol, 100.0)

    def _calculate_stop_and_target(self, entry_price: float, action: str) -> Tuple[float, float]:
        """Calculate stop loss and take profit prices"""
        stop_loss_pct = self.trading_config.get("stop_loss", 0.03)
        profit_target_pct = self.trading_config.get("profit_target", 0.05)

        if action == "BUY":
            stop_loss = entry_price * (1 - stop_loss_pct)
            take_profit = entry_price * (1 + profit_target_pct)
        else:  # SELL
            stop_loss = entry_price * (1 + stop_loss_pct)
            take_profit = entry_price * (1 - profit_target_pct)

        return stop_loss, take_profit

    def _create_reasoning_cache_key(self, signal: Dict, consensus: Dict) -> str:
        """Create cache key for AI reasoning (OPTIMIZATION 12)"""
        import hashlib
        import json

        # Create hash of signal key attributes (rounded to avoid minor differences)
        signal_data = {
            "symbol": signal.get("symbol"),
            "direction": signal.get("action"),
            "confidence": round(signal.get("confidence", 0), 1),  # Round to 1 decimal
            "entry_price": round(signal.get("entry_price", 0), 2),  # Round to 2 decimals
            "regime": signal.get("regime", "UNKNOWN"),
        }
        signal_hash = hashlib.md5(json.dumps(signal_data, sort_keys=True).encode()).hexdigest()
        return f"reasoning:{signal_hash}"

    def _get_cached_reasoning(self, signal: Dict, consensus: Dict, cache_key: Optional[str] = None) -> Optional[str]:
        """Get cached AI reasoning for signal (OPTIMIZATION 12)"""
        # OPTIMIZATION: Reuse cache key if provided to avoid duplicate creation
        if cache_key is None:
            cache_key = self._create_reasoning_cache_key(signal, consensus)

        # Check Redis cache first
        if self.redis_cache:
            cached = self.redis_cache.get(cache_key)
            if cached:
                logger.debug("✅ Using cached AI reasoning from Redis")
                return cached

        # Check in-memory cache
        if cache_key in self._reasoning_cache:
            cached_reasoning, cache_time = self._reasoning_cache[cache_key]
            # OPTIMIZATION: Cache current time to avoid multiple datetime.now() calls
            current_time = datetime.now(timezone.utc)
            age = (current_time - cache_time).total_seconds()
            if age < 3600:  # 1 hour cache
                logger.debug("✅ Using cached AI reasoning")
                return cached_reasoning

        return None

    def _cache_reasoning(self, signal: Dict, consensus: Dict, reasoning: str, current_time: Optional[datetime] = None):
        """Cache AI reasoning (OPTIMIZATION 12)"""
        cache_key = self._create_reasoning_cache_key(signal, consensus)
        ttl = 3600  # 1 hour cache (reasoning is expensive)
        
        # OPTIMIZATION: Use provided time or get current time
        if current_time is None:
            current_time = datetime.now(timezone.utc)

        # Cache in Redis
        if self.redis_cache:
            self.redis_cache.set(cache_key, reasoning, ttl=ttl)

        # Cache in-memory
        self._reasoning_cache[cache_key] = (reasoning, current_time)

    def _generate_reasoning(self, signal: Dict, consensus: Dict) -> str:
        """Generate AI reasoning for signal (OPTIMIZATION 12: with caching)"""
        # OPTIMIZATION: Create cache key once and reuse
        cache_key = self._create_reasoning_cache_key(signal, consensus)
        
        # OPTIMIZATION 12: Check cache first (pass cache_key to avoid recreating it)
        cached_reasoning = self._get_cached_reasoning(signal, consensus, cache_key)
        if cached_reasoning:
            return cached_reasoning

        # OPTIMIZATION: Cache current time for age calculation
        current_time = datetime.now(timezone.utc)

        # Check cache first (legacy check)
        if cache_key in self._reasoning_cache:
            cached_reasoning, cache_time = self._reasoning_cache[cache_key]
            age = (current_time - cache_time).total_seconds()
            if age < self._reasoning_cache_ttl:
                logger.debug(f"✅ Using cached reasoning for {signal['symbol']}")
                return cached_reasoning

        # Generate new reasoning
        try:
            reasoning = self.explainer.explain_signal(
                {
                    "symbol": signal["symbol"],
                    "action": signal["action"],
                    "entry": signal["entry_price"],
                    "stop_loss": signal["stop_price"],
                    "take_profit": signal["target_price"],
                    "confidence": consensus["confidence"],
                }
            )

            # OPTIMIZATION 12: Cache the result (reuse cached current_time)
            self._cache_reasoning(signal, consensus, reasoning, current_time)
            self._cleanup_reasoning_cache()

            return reasoning
        except Exception as e:
            logger.debug(f"Reasoning generation error: {e}")
            fallback = f"Weighted consensus ({consensus.get('sources', 0)} sources) indicates {signal['action']} opportunity with {consensus['confidence']:.1f}% confidence in {consensus.get('regime', 'UNKNOWN')} market regime."
            return fallback

    def _track_symbol_success(self, symbol: str, success: bool):
        """Track symbol success for adaptive processing (OPTIMIZATION 10)"""
        if symbol not in self._symbol_success_tracking:
            self._symbol_success_tracking[symbol] = []

        self._symbol_success_tracking[symbol].append(success)

        # Keep only last 20 results
        if len(self._symbol_success_tracking[symbol]) > 20:
            self._symbol_success_tracking[symbol] = self._symbol_success_tracking[symbol][-20:]

    def _optimize_dataframe_memory(self, df) -> Optional:
        """Optimize DataFrame memory usage (OPTIMIZATION 9)"""
        if df is None or df.empty:
            return df

        try:
            # OPTIMIZATION: Check if optimization is needed before copying
            needs_optimization = False
            for col in ["Open", "High", "Low", "Close"]:
                if col in df.columns and df[col].dtype != "float32":
                    needs_optimization = True
                    break
            if "Volume" in df.columns and df["Volume"].dtype not in ["int32", "int64", "int16", "int8"]:
                needs_optimization = True
            
            if not needs_optimization:
                return df  # Already optimized, no copy needed

            # OPTIMIZATION 9: Use appropriate dtypes to reduce memory
            df = df.copy()  # Only copy if we need to modify

            # Convert to float32 where precision allows (50% memory reduction)
            for col in ["Open", "High", "Low", "Close"]:
                if col in df.columns and df[col].dtype != "float32":
                    df[col] = df[col].astype("float32")

            # Convert Volume to int32 (if values allow)
            if "Volume" in df.columns:
                df["Volume"] = pd.to_numeric(df["Volume"], downcast="integer")

            return df
        except Exception as e:
            logger.debug(f"DataFrame memory optimization error: {e}")
            return df

    async def _validate_signals_batch(
        self, signals: List[Tuple[str, Dict]], market_data: Dict
    ) -> List[Tuple[str, Dict]]:
        """Validate multiple signals in parallel (OPTIMIZATION 15)"""
        if not hasattr(self, "data_quality_monitor") or not self.data_quality_monitor:
            return signals

        # Create validation tasks
        validation_tasks = [
            self.data_quality_monitor.validate_signal(signal, market_data) for _, signal in signals
        ]

        # Run validations in parallel
        results = await asyncio.gather(*validation_tasks, return_exceptions=True)

        # Filter valid signals
        valid_signals = []
        for (source_name, signal), (is_valid, issue) in zip(signals, results):
            if isinstance((is_valid, issue), Exception):
                logger.warning(f"Validation error for {source_name}: {is_valid}")
                continue

            if is_valid:
                valid_signals.append((source_name, signal))
            else:
                logger.warning(
                    f"⚠️  Signal from {source_name} rejected: {issue.description if issue else 'Unknown issue'}"
                )

        return valid_signals

    def _should_update_component(self, symbol: str, component: str, current_value: Any) -> bool:
        """Check if component needs update (OPTIMIZATION 13)"""
        cache_key = f"{symbol}:{component}"

        # Get last value
        if cache_key in self._component_cache:
            last_value = self._component_cache[cache_key]
            if last_value == current_value:
                return False  # No change, skip update

        # Cache new value
        self._component_cache[cache_key] = current_value

        # Cleanup cache if too large
        if len(self._component_cache) > 1000:
            # Remove oldest 20%
            keys_to_remove = list(self._component_cache.keys())[:200]
            for key in keys_to_remove:
                del self._component_cache[key]

        return True  # Changed, need update

    def _cleanup_reasoning_cache(self):
        """Remove old cache entries to prevent memory growth (OPTIMIZED: efficient cleanup)"""
        if len(self._reasoning_cache) > 500:  # Max 500 entries
            # OPTIMIZATION: Use list of (timestamp, key) tuples and sort only what we need
            entries_to_remove = len(self._reasoning_cache) // 5
            timestamp_key_pairs = [
                (cache_time, key) for key, (_, cache_time) in self._reasoning_cache.items()
            ]
            # Sort only to get the oldest entries
            timestamp_key_pairs.sort()
            for _, key in timestamp_key_pairs[:entries_to_remove]:
                del self._reasoning_cache[key]

    def _get_cached_positions(self):
        """Get positions with caching to reduce API calls"""
        import time

        current_time = time.time()

        if (
            self._positions_cache is None
            or self._positions_cache_time is None
            or (current_time - self._positions_cache_time) > self._positions_cache_ttl
        ):
            if self.trading_engine and self.trading_engine.alpaca_enabled:
                self._positions_cache = self.trading_engine.get_positions()
                self._positions_cache_time = current_time
            else:
                self._positions_cache = []

        return self._positions_cache or []

    def _check_correlation_groups(self, symbol: str, existing_positions: List[Dict]) -> bool:
        """Check if adding this symbol would exceed correlation limits"""
        # Correlation groups (ETFs and their components)
        correlation_groups = {
            "tech": ["AAPL", "MSFT", "GOOGL", "META", "NVDA", "AMD", "XLK", "QQQ"],
            "finance": ["JPM", "BAC", "WFC", "GS", "XLF"],
            "energy": ["XOM", "CVX", "XLE"],
            "consumer": ["AMZN", "TSLA", "DIS", "XLY"],
            "healthcare": ["JNJ", "PFE", "XLV"],
            "etf_broad": ["SPY", "QQQ", "DIA", "IWM"],
            "crypto": ["BTC-USD", "ETH-USD", "COIN"],
        }

        max_correlated = self.trading_config.get("max_correlated_positions", 3)

        # Asset class specific limits (if configured)
        asset_class_limits = self.trading_config.get("asset_class_limits", {})

        # Find which group(s) this symbol belongs to
        symbol_groups = [
            group for group, symbols in correlation_groups.items() if symbol in symbols
        ]

        if not symbol_groups:
            return True  # No correlation group, allow trade

        # OPTIMIZATION: Pre-compute existing position symbols set for O(1) lookups
        existing_symbols = {p.get("symbol", "") for p in existing_positions if p.get("symbol")}

        # Count existing positions in same correlation groups
        for group in symbol_groups:
            # OPTIMIZATION: Use set intersection (O(n)) instead of list comprehension with membership check (O(n*m))
            group_symbols = set(correlation_groups[group])
            positions_in_group = existing_symbols & group_symbols

            # Check if group has specific limit
            group_limit = asset_class_limits.get(group, max_correlated)

            if len(positions_in_group) >= group_limit:
                logger.info(
                    f"⏭️  Skipping {symbol} - max correlated positions ({group_limit}) reached in {group} group"
                )
                return False

        return True

    def _update_peak_equity(self, current_equity: float):
        """Track peak equity for accurate drawdown calculation"""
        if self._peak_equity is None:
            self._peak_equity = current_equity

        if current_equity > self._peak_equity:
            self._peak_equity = current_equity

        return self._peak_equity

    def _check_daily_loss_limit(self, account: Dict) -> Tuple[bool, str]:
        """Check if daily loss limit has been exceeded"""
        equity = account.get("equity", 0) or 0

        # Initialize daily start equity if not set (first check of the day)
        if self._daily_start_equity is None:
            self._daily_start_equity = equity
            return True, "OK"

        # Calculate daily P&L
        daily_pnl = equity - self._daily_start_equity
        daily_pnl_pct = (
            (daily_pnl / self._daily_start_equity * 100) if self._daily_start_equity > 0 else 0
        )

        # Check if daily loss limit exceeded
        if daily_pnl_pct < -self._daily_loss_limit_pct:
            self._trading_paused = True
            return (
                False,
                f"Daily loss limit exceeded: {daily_pnl_pct:.2f}% < -{self._daily_loss_limit_pct}%",
            )

        return True, "OK"

    def _validate_trade(self, signal: Dict, account: Dict) -> Tuple[bool, str]:
        """Validate trade against risk management rules"""
        # Check if trading is paused (daily loss limit)
        if self._trading_paused:
            return False, "Trading paused due to daily loss limit"

        # Check account status
        if account.get("trading_blocked", False):
            return False, "Trading is blocked on account"

        if account.get("account_blocked", False):
            return False, "Account is blocked"

        # PROP FIRM: Check risk monitor if enabled
        # OPTIMIZATION: risk_monitor and prop_firm_mode are initialized in __init__, no need for hasattr
        if self.risk_monitor and self.prop_firm_mode:
            can_trade, reason = self.risk_monitor.can_trade()
            if not can_trade:
                return False, f"Prop firm risk check failed: {reason}"

            # Get current stats
            stats = self.risk_monitor.get_monitoring_stats()

            # Check position count
            max_positions = self.prop_firm_config.get("risk_limits", {}).get("max_positions", 3)
            if stats.get("open_positions", 0) >= max_positions:
                return (
                    False,
                    f"Max positions reached: {stats.get('open_positions', 0)} >= {max_positions}",
                )

            # Check confidence threshold
            min_confidence = self.prop_firm_config.get("risk_limits", {}).get(
                "min_confidence", 82.0
            )
            signal_confidence = signal.get("confidence", 0)
            if signal_confidence < min_confidence:
                return False, f"Confidence too low: {signal_confidence:.2f}% < {min_confidence}%"

            # Check symbol restrictions
            symbol = signal.get("symbol", "")
            allowed_symbols = self.prop_firm_config.get("symbols", {}).get("allowed", [])
            restricted_symbols = self.prop_firm_config.get("symbols", {}).get("restricted", [])

            if allowed_symbols and symbol not in allowed_symbols:
                return False, f"Symbol {symbol} not in allowed list: {allowed_symbols}"

            if symbol in restricted_symbols:
                return False, f"Symbol {symbol} is restricted: {restricted_symbols}"

        # Check daily loss limit
        daily_check, daily_reason = self._check_daily_loss_limit(account)
        if not daily_check:
            return False, daily_reason

        # Check drawdown using peak equity (more accurate)
        max_drawdown_pct = self.trading_config.get("max_drawdown_pct", 10)
        if max_drawdown_pct:
            equity = account.get("equity", 0) or 0
            peak_equity = self._update_peak_equity(equity)

            if peak_equity > 0 and equity is not None:
                drawdown_pct = ((peak_equity - equity) / peak_equity) * 100
                if drawdown_pct > max_drawdown_pct:
                    return (
                        False,
                        f"Max drawdown exceeded: {drawdown_pct:.2f}% > {max_drawdown_pct}%",
                    )

        # FIX: Check buying power using actual calculated position size (not just base percentage)
        buying_power = account.get("buying_power", 0) or 0

        if buying_power <= 0:
            return False, "Invalid buying power"

        # Calculate actual position size that would be used (same logic as trading engine)
        entry_price = signal.get("entry_price", 0)
        if entry_price <= 0:
            return False, "Invalid entry price"

        # PROP FIRM: Use prop firm position size limit if enabled
        # OPTIMIZATION: prop_firm_mode is initialized in __init__, no need for hasattr
        if self.prop_firm_mode:
            position_size_pct = self.prop_firm_config.get("risk_limits", {}).get(
                "max_position_size_pct", 3.0
            )
        else:
            # Use max position size to be conservative in validation
            position_size_pct = self.trading_config.get("max_position_size_pct", 15)
            # Could also calculate actual position size here, but max is safer for validation

        # Calculate required capital using max position size (conservative check)
        required_capital = buying_power * (position_size_pct / 100)

        # Also check if we can afford at least 1 share
        min_required = entry_price * 1  # Minimum 1 share

        if required_capital > buying_power * 0.95:  # Leave 5% buffer
            return (
                False,
                f"Insufficient buying power: need ${required_capital:,.2f}, have ${buying_power:,.2f}",
            )

        if min_required > buying_power:
            return (
                False,
                f"Cannot afford minimum position: need ${min_required:,.2f} for 1 share, have ${buying_power:,.2f}",
            )

        return True, "OK"

    async def generate_signals_cycle(self, symbols: List[str] = None) -> List[Dict]:
        """
        Generate signals for all symbols with error recovery and performance tracking
        
        Returns:
            List of generated signals
        """
        if symbols is None:
            symbols = DEFAULT_SYMBOLS

        generated_signals = []
        account, existing_positions = self._get_trading_context()

        # Priority-based symbol processing (high volatility first)
        sorted_symbols = self._prioritize_symbols(symbols)

        # Process in adaptive batches with early exit
        batch_size = min(6, len(sorted_symbols))
        
        # Performance tracking
        import time
        cycle_start_time = time.time()

        for i in range(0, len(sorted_symbols), batch_size):
            batch = sorted_symbols[i : i + batch_size]

            # Process batch in parallel
            symbol_tasks = [self.generate_signal_for_symbol(symbol) for symbol in batch]
            results = await asyncio.gather(*symbol_tasks, return_exceptions=True)

            # Process results with early exit tracking
            batch_successes = 0
            for symbol, result in zip(batch, results):
                try:
                    if isinstance(result, Exception):
                        logger.error(f"Error processing {symbol}: {result}")
                        self._track_symbol_success(symbol, False)
                        # Track error in performance metrics
                        if self.performance_metrics:
                            self.performance_metrics.record_error("signal_generation", str(type(result).__name__))
                        continue

                    signal = result
                    if signal:
                        batch_successes += 1
                        self._track_symbol_success(symbol, True)

                        # Process and store signal
                        processed_signal = await self._process_and_store_signal(
                            signal, symbol, account, existing_positions
                        )
                        if processed_signal:
                            generated_signals.append(processed_signal)
                    else:
                        self._track_symbol_success(symbol, False)

                except Exception as e:
                    logger.error(f"❌ Error in signal cycle for {symbol}: {e}")
                    self._track_symbol_success(symbol, False)

            # Early exit if too many failures
            if self._should_exit_early(batch_successes, len(results)):
                break

        # Cleanup and finalize
        self._finalize_signal_cycle(symbols)
        
        # Track performance metrics
        if cycle_start_time and self.performance_metrics:
            import time
            cycle_duration = time.time() - cycle_start_time
            self.performance_metrics.record_signal_generation_time(cycle_duration)
            for _ in symbols:
                self.performance_metrics.record_symbol_processed()
            logger.debug(f"📊 Signal cycle completed in {cycle_duration:.2f}s for {len(symbols)} symbols")

        return generated_signals

    async def _process_and_store_signal(
        self, signal: Dict, symbol: str, account: Optional[Dict], existing_positions: List[Dict]
    ) -> Optional[Dict]:
        """Process, store, and execute signal if valid (OPTIMIZED: async non-blocking database insert)"""
        # OPTIMIZATION: Use async signal logging to avoid blocking the pipeline
        # Store signal in database (non-blocking async batch insert)
        signal_id = await self.tracker.log_signal_async(signal)
        signal["signal_id"] = signal_id

        logger.info(
            f"✅ Generated signal: {symbol} {signal['action']} @ ${signal['entry_price']} ({signal['confidence']}% confidence)"
        )

        # Sync to Alpine backend (async, non-blocking)
        self._sync_signal_to_alpine(signal)

        # Track signal generation
        self._track_signal_generated(signal, signal_id, symbol)

        # Execute trade if enabled
        if self.auto_execute and self.trading_engine and account and not self._paused:
            executed = await self._execute_trade_if_valid(
                signal, account, existing_positions, symbol
            )
            self._track_trade_execution(signal, signal_id, executed)
        else:
            self._track_signal_skipped(signal_id)

        return signal

    def _sync_signal_to_alpine(self, signal: Dict):
        """Sync signal to Alpine backend (async, non-blocking)"""
        if not self.alpine_sync:
            return

        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(self.alpine_sync.sync_signal(signal))
            else:
                logger.debug("No event loop for Alpine sync")
        except RuntimeError:
            # No event loop available - this is fine, sync will be skipped
            logger.debug("No event loop available for Alpine sync")
        except Exception as e:
            logger.warning(f"⚠️  Failed to queue Alpine sync: {e}")

    def _track_signal_generated(self, signal: Dict, signal_id: str, symbol: str):
        """Track signal generation in lifecycle tracker"""
        if not self._lifecycle_tracker:
            return

        try:
            self._lifecycle_tracker.record_signal_generated(
                signal_id=signal_id,
                symbol=symbol,
                action=signal["action"],
                entry_price=signal["entry_price"],
                confidence=signal["confidence"],
                regime=signal.get("regime", "UNKNOWN"),
            )
        except Exception as e:
            logger.debug(f"Could not track signal lifecycle: {e}")

    def _track_trade_execution(self, signal: Dict, signal_id: str, executed: bool):
        """Track trade execution or skip in lifecycle tracker"""
        if not self._lifecycle_tracker or not executed:
            return

        try:
            self._lifecycle_tracker.record_signal_executed(
                signal_id=signal_id, trade_id=signal.get("trade_id", "")
            )
        except Exception as e:
            logger.debug(f"Could not update signal lifecycle: {e}")

    def _track_signal_skipped(self, signal_id: str):
        """Track signal skip in lifecycle tracker"""
        if not self._lifecycle_tracker:
            return

        try:
            reason = "auto_execute_disabled" if not self.auto_execute else "no_trading_engine"
            self._lifecycle_tracker.record_signal_skipped(signal_id=signal_id, reason=reason)
        except Exception as e:
            logger.debug(f"Could not track signal skip: {e}")

    def _should_exit_early(self, batch_successes: int, total_results: int) -> bool:
        """Check if we should exit early due to low success rate"""
        if total_results == 0:
            return False

        success_rate = batch_successes / total_results
        if success_rate < 0.3:  # Less than 30% success
            logger.warning(f"Low success rate ({success_rate:.0%}), skipping remaining symbols")
            return True
        return False

    def _finalize_signal_cycle(self, symbols: List[str]):
        """Finalize signal cycle with cleanup and outcome tracking"""
        # OPTIMIZATION: Conditional memory cleanup (only if memory pressure detected)
        # Only run gc.collect() periodically to avoid overhead
        import gc
        import time
        import psutil
        import os

        current_time = time.time()
        if not hasattr(self, "_last_gc_time"):
            self._last_gc_time = 0.0
        if not hasattr(self, "_last_memory_check"):
            self._last_memory_check = 0.0

        # Check memory usage every minute
        if (current_time - self._last_memory_check) > 60:  # 1 minute
            try:
                process = psutil.Process(os.getpid())
                memory_info = process.memory_info()
                memory_mb = memory_info.rss / 1024 / 1024
                memory_percent = process.memory_percent()
                
                # Log memory usage
                if memory_percent > 80:
                    logger.warning(f"⚠️  High memory usage: {memory_mb:.1f}MB ({memory_percent:.1f}%)")
                
                # Force GC if memory usage is high
                if memory_percent > 85 or memory_mb > 1500:  # > 1.5GB or > 85%
                    logger.warning(f"🧹 Forcing GC due to high memory: {memory_mb:.1f}MB ({memory_percent:.1f}%)")
                    gc.collect()
                    self._last_gc_time = current_time
                    
                    # Cleanup caches
                    self._cleanup_consensus_cache()
                    self._cleanup_regime_cache()
                    self._cleanup_reasoning_cache()
                
                self._last_memory_check = current_time
            except ImportError:
                # psutil not available, skip memory monitoring
                pass
            except Exception as e:
                logger.debug(f"Memory check error: {e}")

        # Run GC every 5 minutes or if memory usage is high
        if (current_time - self._last_gc_time) > 300:  # 5 minutes
            gc.collect()
            self._last_gc_time = current_time

        # Flush any pending batch inserts
        try:
            self.tracker.flush_pending()
        except Exception as e:
            logger.debug(f"Error flushing pending signals: {e}")

        # Track outcomes for open signals (periodic check)
        self._update_outcome_tracking(symbols)

    def _update_outcome_tracking(self, symbols: List[str]):
        """Update outcome tracking for open signals"""
        if not self._outcome_tracker:
            return

        try:
            # OPTIMIZATION: Use timezone-aware datetime for consistency
            now = datetime.now(timezone.utc)

            # Check if it's time to update outcomes (every 5 minutes)
            if (
                self._last_outcome_check is None
                or (now - self._last_outcome_check).total_seconds() >= self._outcome_check_interval
            ):

                # OPTIMIZATION: Safe dictionary access - only get prices for symbols we have
                current_prices = {
                    symbol: self._last_prices[symbol]
                    for symbol in symbols
                    if symbol in self._last_prices and self._last_prices[symbol] is not None
                }

                # Update outcomes if we have prices
                if current_prices:
                    try:
                        updated = self._outcome_tracker.track_open_signals(current_prices)
                        if updated > 0:
                            logger.debug(f"📊 Updated {updated} signal outcomes")
                    except Exception as e:
                        logger.debug(f"Error tracking outcomes: {e}")

                self._last_outcome_check = now
        except Exception as e:
            logger.debug(f"Could not track outcomes: {e}")

    def _prioritize_symbols(self, symbols: List[str]) -> List[str]:
        """Prioritize symbols by volatility (high volatility first)"""

        # Sort by volatility (highest first), with unknown volatility at end
        def get_volatility(symbol):
            return self._symbol_volatility.get(symbol, 0.0)

        return sorted(symbols, key=get_volatility, reverse=True)

    def _get_trading_context(self) -> Tuple[Optional[Dict], List[Dict]]:
        """Get account and positions for trading context"""
        if not (self.auto_execute and self.trading_engine):
            return None, []

        account = self.trading_engine.get_account_details()
        existing_positions = self._get_cached_positions()

        # PROP FIRM: Update risk monitor with current equity
        # OPTIMIZATION: risk_monitor is initialized in __init__, no need for hasattr
        if self.risk_monitor and account:
            equity = account.get("equity", 0)
            if equity > 0:
                self.risk_monitor.update_equity(equity)

                # Sync position tracking in risk monitor
                # First, get current tracked positions
                current_tracked = set(self.risk_monitor.positions.keys())
                current_actual = {
                    p.get("symbol", "") for p in existing_positions if p.get("symbol")
                }

                # Remove positions that no longer exist
                for symbol in current_tracked - current_actual:
                    try:
                        self.risk_monitor.remove_position(symbol)
                        logger.debug(f"🗑️  Removed closed position {symbol} from risk monitor")
                    except Exception as e:
                        logger.warning(f"Failed to remove position {symbol} from risk monitor: {e}")

                # Update/add current positions
                for position in existing_positions:
                    symbol = position.get("symbol", "")
                    if not symbol:
                        continue
                    qty = position.get("qty", 0)
                    avg_price = position.get("avg_entry_price", 0)
                    current_price = position.get("current_price", avg_price)
                    position_value = qty * current_price
                    account_equity = account.get("equity", 1)
                    size_pct = (position_value / account_equity * 100) if account_equity > 0 else 0

                    self.risk_monitor.add_position(
                        symbol,
                        {
                            "qty": qty,
                            "avg_price": avg_price,
                            "current_price": current_price,
                            "size_pct": size_pct,
                        },
                    )

        return account, existing_positions

    async def _execute_trade_if_valid(
        self, signal: Dict, account: Dict, existing_positions: List[Dict], symbol: str
    ):
        """Execute trade if all validations pass"""
        try:
            # Risk validation
            can_trade, reason = self._validate_trade(signal, account)
            if not can_trade:
                logger.warning(f"⏭️  Skipping {symbol} - {reason}")
                return

            # OPTIMIZATION: Check existing position using set for O(1) lookup
            existing_symbols = {p.get("symbol") for p in existing_positions if p.get("symbol")}
            if symbol in existing_symbols:
                logger.info(f"⏭️  Skipping {symbol} - position already exists")
                return

            # Check correlation limits
            if not self._check_correlation_groups(symbol, existing_positions):
                return

            # FIX: Pass existing_positions to avoid race condition
            order_id = self.trading_engine.execute_signal(
                signal, existing_positions=existing_positions
            )
            if order_id:
                await self._handle_successful_trade(signal, order_id, existing_positions, symbol)
            else:
                logger.warning(f"⚠️  Trade execution returned no order ID for {symbol}")

        except Exception as e:
            logger.error(f"❌ Error executing trade for {symbol}: {e}")

    async def _handle_successful_trade(
        self, signal: Dict, order_id: str, existing_positions: List[Dict], symbol: str
    ):
        """Handle successful trade execution"""
        signal["order_id"] = str(order_id)

        # Get order status
        order_status = self.trading_engine.get_order_status(order_id)
        if order_status:
            signal["order_status"] = order_status.get("status")
            signal["filled_qty"] = order_status.get("filled_qty", 0)
            signal["filled_price"] = order_status.get("filled_avg_price")

        # Record in performance tracker
        self._record_trade_in_tracker(signal, order_id, symbol)

        # Journal trade
        self._journal_trade(signal, order_id, order_status)

        # Update position cache
        self._update_position_cache(signal, existing_positions)

        logger.info(f"✅ Trade executed: {symbol} {signal['action']} - Order ID: {order_id}")

    def _record_trade_in_tracker(self, signal: Dict, order_id: str, symbol: str):
        """Record trade in performance tracker with enhanced fields"""
        if not self._performance_tracker:
            return

        try:
            # Get order status to get actual fill price
            order_status = None
            actual_entry_price = None
            filled_qty = None
            if self.trading_engine:
                order_status = self.trading_engine.get_order_status(order_id)
                if order_status:
                    actual_entry_price = order_status.get("filled_avg_price")
                    filled_qty = order_status.get("filled_qty", 0)

            # Get regime from signal
            regime = signal.get("regime", "UNKNOWN")

            trade = self._performance_tracker.record_signal_entry(
                signal_id=str(signal.get("signal_id", "")),
                asset_class="stock" if not symbol.endswith("-USD") else "crypto",
                symbol=symbol,
                signal_type="long" if signal["action"] == "BUY" else "short",
                entry_price=signal["entry_price"],
                quantity=signal.get("filled_qty", 0) or signal.get("qty", 0),
                confidence=signal["confidence"],
                alpaca_order_id=str(order_id),
                regime=regime,
                signal_entry_price=signal["entry_price"],
                actual_entry_price=actual_entry_price,
                stop_price=signal.get("stop_price"),
                target_price=signal.get("target_price"),
                filled_qty=filled_qty,
            )
            signal["trade_id"] = trade.id

            # Sync entry to Tradervue
            self._sync_trade_entry_to_tradervue(trade)

            # Update lifecycle tracker
            if self._lifecycle_tracker:
                try:
                    self._lifecycle_tracker.record_signal_executed(
                        signal_id=str(signal.get("signal_id", "")), trade_id=trade.id
                    )
                except Exception as e:
                    logger.debug(f"Could not update lifecycle tracker: {e}")

            logger.debug(f"📊 Trade recorded: {trade.id} (regime: {regime})")
        except Exception as e:
            logger.warning(f"Could not record trade in tracker: {e}")

    def _update_position_cache(self, signal: Dict, existing_positions: List[Dict]):
        """Update position cache after successful trade"""
        # FIX: Invalidate cache immediately to force refresh on next call
        self._positions_cache = None
        self._positions_cache_time = None

        # Update local positions list for immediate use
        existing_positions.append(
            {
                "symbol": signal["symbol"],
                "side": signal["action"],
                "qty": signal.get("filled_qty", 0) or 0,
                "entry_price": signal.get("filled_price") or signal["entry_price"],
                "stop_price": signal.get("stop_price"),
                "target_price": signal.get("target_price"),
            }
        )

    def _journal_trade(self, signal: Dict, order_id: str, order_status: Dict = None):
        """Journal trade for analysis and audit"""
        try:
            journal_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "signal_id": signal.get("signal_id"),
                "order_id": order_id,
                "symbol": signal["symbol"],
                "action": signal["action"],
                "entry_price": signal["entry_price"],
                "confidence": signal["confidence"],
                "stop_price": signal.get("stop_price"),
                "target_price": signal.get("target_price"),
                "order_status": order_status.get("status") if order_status else None,
                "filled_qty": order_status.get("filled_qty", 0) if order_status else 0,
                "filled_price": order_status.get("filled_avg_price") if order_status else None,
                "strategy": signal.get("strategy", "weighted_consensus_v6"),
            }

            # Log to file or database (could be enhanced to write to file/db)
            logger.info(f"📝 Trade Journal: {journal_entry}")

        except Exception as e:
            logger.debug(f"Error journaling trade: {e}")

    async def monitor_positions(self):
        """Monitor positions and execute stop loss/take profit"""
        if not self.auto_execute or not self.trading_engine:
            return

        while self.running:
            try:
                positions = self._get_cached_positions()
                account = self.trading_engine.get_account_details()

                for pos in positions:
                    symbol = pos["symbol"]
                    current_price = pos["current_price"]
                    entry_price = pos.get("entry_price", current_price)
                    stop_price = pos.get("stop_price")
                    target_price = pos.get("target_price")
                    side = pos["side"]

                    # Check stop loss
                    if stop_price:
                        if side == "LONG" and current_price <= stop_price:
                            logger.warning(
                                f"🛑 Stop loss triggered: {symbol} @ ${current_price:.2f} (stop: ${stop_price:.2f})"
                            )
                            self._close_position(symbol, "stop_loss")
                        elif side == "SHORT" and current_price >= stop_price:
                            logger.warning(
                                f"🛑 Stop loss triggered: {symbol} @ ${current_price:.2f} (stop: ${stop_price:.2f})"
                            )
                            self._close_position(symbol, "stop_loss")

                    # Check take profit
                    if target_price:
                        if side == "LONG" and current_price >= target_price:
                            logger.info(
                                f"🎯 Take profit triggered: {symbol} @ ${current_price:.2f} (target: ${target_price:.2f})"
                            )
                            self._close_position(symbol, "take_profit")
                        elif side == "SHORT" and current_price <= target_price:
                            logger.info(
                                f"🎯 Take profit triggered: {symbol} @ ${current_price:.2f} (target: ${target_price:.2f})"
                            )
                            self._close_position(symbol, "take_profit")

                # FIX: Reset daily tracking at start of new trading day
                if account:
                    equity = account.get("equity", 0)
                    # Check if it's a new trading day by checking market status and time
                    # Reset if market just opened (first check after market open)
                    if self.trading_engine and self.trading_engine.is_market_open():
                        # Check if we haven't reset today (simple heuristic: if equity changed significantly or it's been > 12 hours)
                        from datetime import datetime

                        current_hour = datetime.now().hour
                        # If it's early morning (before 10 AM) and we have daily equity set, reset it
                        if current_hour < 10 and self._daily_start_equity is not None:
                            # Check if equity is close to last equity (within 2%) - likely new day
                            if equity > 0 and self._daily_start_equity > 0:
                                equity_change_pct = (
                                    abs(
                                        (equity - self._daily_start_equity)
                                        / self._daily_start_equity
                                    )
                                    * 100
                                )
                                if (
                                    equity_change_pct < 2.0
                                ):  # Equity reset to similar value (new day)
                                    self._daily_start_equity = equity
                                    self._trading_paused = False
                                    logger.info(
                                        f"🔄 Daily tracking reset - new trading day (equity: ${equity:,.2f})"
                                    )
                    # Fallback: if equity increased significantly, might be new day (deposit/transfer)
                    elif self._daily_start_equity and equity > self._daily_start_equity * 1.1:
                        self._daily_start_equity = equity
                        self._trading_paused = False
                        logger.info(
                            f"🔄 Daily tracking reset - equity increased significantly (${equity:,.2f})"
                        )

                await asyncio.sleep(5)  # Check every 5 seconds
            except Exception as e:
                logger.error(f"Error in position monitoring: {e}")
                await asyncio.sleep(10)

    def _close_position(self, symbol: str, reason: str):
        """Close a position"""
        try:
            # Get position details before closing
            positions = self._get_cached_positions()
            # OPTIMIZATION: Use dict lookup instead of linear search
            position = None
            for p in positions:
                if p.get("symbol") == symbol:
                    position = p
                    break

            if not position:
                logger.warning(f"Position not found for {symbol}")
                return

            # Get current price
            current_price = position.get("current_price")
            if not current_price:
                current_price = self.trading_engine.get_current_price(symbol)

            # Determine action based on position side
            action = "SELL" if position["side"] == "LONG" else "BUY"

            signal = {
                "symbol": symbol,
                "action": action,
                "entry_price": current_price or position.get("entry_price", 0),
                "confidence": 100.0,
                "strategy": "position_monitor",
                "asset_type": "stock" if not symbol.endswith("-USD") else "crypto",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "close_reason": reason,
                "trade_id": position.get("trade_id"),  # Preserve trade_id for exit tracking
            }

            # FIX: Pass existing positions to avoid race condition
            positions = self._get_cached_positions()
            order_id = self.trading_engine.execute_signal(signal, existing_positions=positions)
            if order_id:
                logger.info(
                    f"✅ Position closed: {symbol} - Reason: {reason} - Order ID: {order_id}"
                )

                # PROP FIRM: Remove position from risk monitor when closed
                if (
                    # OPTIMIZATION: risk_monitor and prop_firm_mode are initialized in __init__
                    self.risk_monitor
                    and self.prop_firm_mode
                ):
                    try:
                        self.risk_monitor.remove_position(symbol)
                        logger.debug(f"🗑️  Removed {symbol} from prop firm risk monitor")
                    except Exception as e:
                        logger.warning(f"Failed to remove position from risk monitor: {e}")

                # Record exit in performance tracker
                if self._performance_tracker and position.get("trade_id"):
                    try:
                        exit_price = current_price or position.get("entry_price", 0)

                        # Get actual exit price from order if available
                        actual_exit_price = None
                        if order_id and self.trading_engine:
                            exit_order_status = self.trading_engine.get_order_status(order_id)
                            if exit_order_status:
                                actual_exit_price = exit_order_status.get("filled_avg_price")

                        # Determine exit reason from close_reason
                        exit_reason = reason  # stop_loss, take_profit, etc.
                        exit_method = "automatic"  # All position monitor exits are automatic

                        # Get current regime if available
                        exit_regime = None
                        try:
                            # Try to get current regime from signal generation
                            # This would require access to market data, simplified for now
                            pass
                        except:
                            pass

                        trade = self._performance_tracker.record_signal_exit(
                            trade_id=position["trade_id"],
                            exit_price=exit_price,
                            actual_exit_price=actual_exit_price,
                            exit_reason=exit_reason,
                            exit_method=exit_method,
                            exit_regime=exit_regime,
                        )
                        logger.debug(
                            f"📊 Trade exit recorded for {position['trade_id']} (reason: {exit_reason})"
                        )

                        # Sync exit to Tradervue
                        if trade:
                            self._sync_trade_exit_to_tradervue(trade)
                    except Exception as e:
                        logger.warning(f"Could not record trade exit in tracker: {e}")

                # Invalidate cache
                self._positions_cache = None
                self._positions_cache_time = None
            else:
                logger.warning(f"⚠️  Failed to close position {symbol}")
        except Exception as e:
            logger.error(f"Error closing position {symbol}: {e}")

    def _sync_trade_entry_to_tradervue(self, trade):
        """Sync trade entry to Tradervue when trade is recorded"""
        if not TRADERVUE_INTEGRATION_AVAILABLE:
            return

        try:
            tradervue = get_tradervue_integration()
            if tradervue and tradervue.client.enabled:
                tradervue.sync_trade_entry(trade)
        except Exception as e:
            logger.warning(f"Could not sync trade entry to Tradervue: {e}")

    def _sync_trade_exit_to_tradervue(self, trade):
        """Sync trade exit to Tradervue when position closes"""
        if not TRADERVUE_INTEGRATION_AVAILABLE:
            return

        try:
            tradervue = get_tradervue_integration()
            if tradervue and tradervue.client.enabled:
                tradervue.sync_trade_exit(trade)
        except Exception as e:
            logger.warning(f"Could not sync trade exit to Tradervue: {e}")

    async def start_background_generation(self, interval_seconds: int = 5):
        """
        Start background signal generation task with position monitoring

        Args:
            interval_seconds: Time between signal generation cycles (default: 5 seconds)
        """
        self.running = True
        logger.info(f"🚀 Starting background signal generation (every {interval_seconds} seconds)")

        # Start risk monitoring if enabled
        # OPTIMIZATION: risk_monitor is initialized in __init__, no need for hasattr
        if self.risk_monitor:
            await self.risk_monitor.start_monitoring()
            logger.info("🚨 Risk monitoring started")

        self._start_position_monitoring()

        pause_checker = PauseStateChecker(self, interval_seconds=30)

        while self.running:
            try:
                # Check and update pause state
                pause_checker.check_and_update()

                # Skip if paused
                if self._paused:
                    await asyncio.sleep(interval_seconds)
                    continue

                # Generate signals
                await self._run_signal_generation_cycle(interval_seconds)

            except Exception as e:
                logger.error(f"❌ Error in background generation cycle: {e}")
                await asyncio.sleep(interval_seconds)

    def _start_position_monitoring(self):
        """Start position monitoring task if enabled"""
        if self.trading_config.get("enable_position_monitoring", True) and self.auto_execute:
            import asyncio

            asyncio.create_task(self.monitor_positions())
            logger.info("🔄 Position monitoring started")

    async def _run_signal_generation_cycle(self, interval_seconds: int):
        """Run one signal generation cycle"""
        start_time = datetime.now(timezone.utc)
        signals = await self.generate_signals_cycle()
        elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
        logger.info(f"📊 Generated {len(signals)} signals in {elapsed:.2f}s")

        # OPTIMIZATION: Record performance metrics
        if self.performance_metrics:
            self.performance_metrics.record_signal_generation_time(elapsed)

        await asyncio.sleep(interval_seconds)

    def _is_cursor_running(self) -> bool:
        """Check if Cursor application is currently running (dev only)"""
        if not self._cursor_aware:
            return True  # Production always runs

        try:
            # Check for Cursor process on macOS
            if platform.system() == "Darwin":
                result = subprocess.run(
                    ["pgrep", "-f", "Cursor"], capture_output=True, text=True, timeout=2
                )
                return result.returncode == 0 and len(result.stdout.strip()) > 0
            else:
                # For other platforms, try ps
                result = subprocess.run(["ps", "aux"], capture_output=True, text=True, timeout=2)
                return "Cursor" in result.stdout
        except Exception:
            # If we can't check, assume Cursor is running (fail open)
            return True

    def _is_computer_awake(self) -> bool:
        """Check if computer is awake (macOS only, dev only)"""
        if not self._cursor_aware:
            return True  # Production always runs

        # If Cursor is running, computer is definitely awake
        if self._is_cursor_running():
            return True

        try:
            if platform.system() == "Darwin":
                # Check system assertions - if anything is preventing sleep, likely awake
                result = subprocess.run(
                    ["pmset", "-g", "assertions"], capture_output=True, text=True, timeout=2
                )
                # If system has active assertions preventing sleep, it's likely awake
                if (
                    "PreventUserIdleSystemSleep" in result.stdout
                    or "PreventUserIdleDisplaySleep" in result.stdout
                ):
                    return True

                # Check system idle time (macOS)
                try:
                    idle_result = subprocess.run(
                        ["ioreg", "-c", "IOHIDSystem"], capture_output=True, text=True, timeout=2
                    )
                    # If we can query IORegistry, system is likely awake
                    # More sophisticated: parse HIDIdleTime from output
                    return True
                except Exception:
                    # If we can't check, assume awake (fail open)
                    return True
            else:
                # For other platforms, assume awake
                return True
        except Exception:
            # If we can't check, assume awake (fail open - better to trade than miss opportunities)
            return True

    def _should_pause_trading(self) -> bool:
        """Check if trading should be paused (dev only)"""
        if not self._cursor_aware:
            return False  # Production never pauses

        # Pause if Cursor is not running
        if not self._is_cursor_running():
            return True

        # Pause if computer appears to be asleep (macOS heuristic)
        if not self._is_computer_awake():
            return True

        return False

    def stop(self):
        """Stop signal generation service and cleanup"""
        self.running = False

        # Stop risk monitoring if enabled
        if (
            hasattr(self, "risk_monitor")
            and self.risk_monitor
            and hasattr(self.risk_monitor, "monitoring_active")
            and self.risk_monitor.monitoring_active
        ):
            import asyncio

            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # Schedule async cleanup if loop is running
                    asyncio.create_task(self.risk_monitor.stop_monitoring())
                else:
                    # Run synchronously if no loop is running
                    loop.run_until_complete(self.risk_monitor.stop_monitoring())
            except RuntimeError:
                # No event loop available, try to create one
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(self.risk_monitor.stop_monitoring())
                    loop.close()
                except Exception as e:
                    logger.warning(f"Error stopping risk monitor: {e}")
            except Exception as e:
                logger.warning(f"Error stopping risk monitor: {e}")

        # OPTIMIZATION: Flush any pending batch inserts before stopping
        try:
            self.tracker.flush_pending()
        except Exception as e:
            logger.warning(f"Error flushing pending signals: {e}")

        # Close Alpine sync service
        if hasattr(self, "alpine_sync") and self.alpine_sync:
            import asyncio

            try:
                # Try to close async
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # Schedule async cleanup if loop is running
                    asyncio.create_task(self.alpine_sync.close())
                else:
                    # Run synchronously if no loop is running
                    loop.run_until_complete(self.alpine_sync.close())
            except RuntimeError:
                # No event loop available, try to create one
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(self.alpine_sync.close())
                    loop.close()
                except Exception as e:
                    logger.debug(f"Error closing Alpine sync service: {e}")
            except Exception as e:
                logger.debug(f"Error closing Alpine sync service: {e}")

        logger.info("🛑 Signal Generation Service stopped")

    async def stop_async(self):
        """Async version of stop() for proper async cleanup"""
        self.running = False

        # Stop risk monitoring if enabled
        if (
            hasattr(self, "risk_monitor")
            and self.risk_monitor
            and hasattr(self.risk_monitor, "monitoring_active")
            and self.risk_monitor.monitoring_active
        ):
            try:
                await self.risk_monitor.stop_monitoring()
            except Exception as e:
                logger.warning(f"Error stopping risk monitor: {e}")

        # OPTIMIZATION: Flush any pending batch inserts before stopping
        try:
            self.tracker.flush_pending()
        except Exception as e:
            logger.warning(f"Error flushing pending signals: {e}")

        # Close Alpine sync service
        if hasattr(self, "alpine_sync") and self.alpine_sync:
            try:
                await self.alpine_sync.close()
            except Exception as e:
                logger.debug(f"Error closing Alpine sync service: {e}")

        logger.info("🛑 Signal Generation Service stopped (async)")


class PauseStateChecker:
    """Manages pause state checking for development mode"""

    def __init__(self, service, interval_seconds=30):
        self.service = service
        self.interval_seconds = interval_seconds
        self.last_check = datetime.now(timezone.utc)

    def check_and_update(self):
        """Check if pause state should be updated"""
        if not self.service._cursor_aware:
            return

        time_since_check = (datetime.now(timezone.utc) - self.last_check).total_seconds()
        if time_since_check < self.interval_seconds:
            return

        should_pause = self.service._should_pause_trading()
        self._update_pause_state(should_pause)
        self.last_check = datetime.now(timezone.utc)

    def _update_pause_state(self, should_pause: bool):
        """Update pause state and log appropriately"""
        if should_pause and not self.service._paused:
            self.service._paused = True
            reason = (
                "Cursor is not running"
                if not self.service._is_cursor_running()
                else "Computer appears to be asleep"
            )
            logger.info(f"💤 {reason} - pausing signal generation and trading")
            logger.info("   Trading will resume automatically when Cursor starts or computer wakes")
        elif not should_pause and self.service._paused:
            self.service._paused = False
            reason = "Cursor detected" if self.service._is_cursor_running() else "Computer awake"
            logger.info(f"✅ Resuming signal generation and trading ({reason})")


# Global instance
_signal_service: Optional[SignalGenerationService] = None


def get_signal_service() -> SignalGenerationService:
    """Get or create global signal generation service instance"""
    global _signal_service
    if _signal_service is None:
        _signal_service = SignalGenerationService()
    return _signal_service

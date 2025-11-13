#!/usr/bin/env python3
"""
Alpine Analytics - Automatic Signal Generation Service
Generates signals every 5 seconds using Weighted Consensus v6.0
"""
import asyncio
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import json

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
        
        # Initialize consensus engine (uses config.json)
        try:
            self.consensus_engine = WeightedConsensusEngine()
        except Exception as e:
            logger.warning(f"⚠️  Could not load consensus engine config: {e}")
            # Create minimal consensus engine
            self.consensus_engine = WeightedConsensusEngine.__new__(WeightedConsensusEngine)
            self.consensus_engine.weights = {
                'massive': 0.40,
                'alpha_vantage': 0.25,
                'x_sentiment': 0.20,
                'sonar': 0.15
            }
            self.consensus_engine.calculate_consensus = lambda signals: self._simple_consensus(signals)
        
        self.explainer = SignalExplainer()
        self.running = False
        
        # Initialize data sources
        self.data_sources = {}
        self._init_data_sources()
        
        logger.info("✅ Signal Generation Service initialized")
    
    def _simple_consensus(self, signals):
        """Fallback consensus calculation if config.json not available"""
        if not signals:
            return None
        
        long_votes = 0
        short_votes = 0
        total_weight = 0
        
        for source, signal in signals.items():
            weight = self.consensus_engine.weights.get(source, 0)
            direction = signal.get('direction', 'NEUTRAL')
            confidence = signal.get('confidence', 0)
            vote = confidence * weight
            
            if direction == 'LONG':
                long_votes += vote
            elif direction == 'SHORT':
                short_votes += vote
            
            total_weight += weight
        
        if long_votes > short_votes and long_votes > 0:
            return {
                'direction': 'LONG',
                'confidence': (long_votes / total_weight * 100) if total_weight > 0 else 0,
                'sources': len(signals),
                'agreement': (long_votes / total_weight * 100) if total_weight > 0 else 0
            }
        elif short_votes > long_votes and short_votes > 0:
            return {
                'direction': 'SHORT',
                'confidence': (short_votes / total_weight * 100) if total_weight > 0 else 0,
                'sources': len(signals),
                'agreement': (short_votes / total_weight * 100) if total_weight > 0 else 0
            }
        
        return None
    
    def _init_data_sources(self):
        """Initialize all data sources with API keys from AWS Secrets Manager or env"""
        try:
            import os
            import sys
            from pathlib import Path
            
            # Add shared package to path
            shared_path = Path(__file__).parent.parent.parent.parent.parent / "packages" / "shared"
            if shared_path.exists():
                sys.path.insert(0, str(shared_path))
            
            try:
                from utils.secrets_manager import get_secret
            except ImportError:
                get_secret = None
            
            service = "argo"
            
            # Massive (Polygon.io) - 40% weight
            try:
                polygon_key = None
                if get_secret:
                    polygon_key = get_secret("polygon-api-key", service=service)
                polygon_key = polygon_key or os.getenv('POLYGON_API_KEY')
                if polygon_key:
                    self.data_sources['massive'] = MassiveDataSource(polygon_key)
                    logger.info("✅ Massive data source initialized")
            except Exception as e:
                logger.debug(f"Massive init error: {e}")
            
            # Alpha Vantage - 25% weight
            try:
                alpha_key = None
                if get_secret:
                    alpha_key = get_secret("alpha-vantage-api-key", service=service)
                alpha_key = alpha_key or os.getenv('ALPHA_VANTAGE_API_KEY')
                if alpha_key:
                    self.data_sources['alpha_vantage'] = AlphaVantageDataSource(alpha_key)
                    logger.info("✅ Alpha Vantage data source initialized")
            except Exception as e:
                logger.debug(f"Alpha Vantage init error: {e}")
            
            # XAI Grok - 20% weight
            try:
                xai_key = None
                if get_secret:
                    xai_key = get_secret("xai-api-key", service=service)
                xai_key = xai_key or os.getenv('XAI_API_KEY')
                if xai_key:
                    self.data_sources['x_sentiment'] = XAIGrokDataSource(xai_key)
                    logger.info("✅ XAI Grok data source initialized")
            except Exception as e:
                logger.debug(f"XAI Grok init error: {e}")
            
            # Sonar AI (Perplexity) - 15% weight
            try:
                sonar_key = None
                if get_secret:
                    sonar_key = get_secret("perplexity-api-key", service=service)
                sonar_key = sonar_key or os.getenv('PERPLEXITY_API_KEY')
                if sonar_key:
                    self.data_sources['sonar'] = SonarDataSource(sonar_key)
                    logger.info("✅ Sonar AI data source initialized")
            except Exception as e:
                logger.debug(f"Sonar init error: {e}")
            
            if not self.data_sources:
                logger.warning("⚠️  No data sources initialized - using fallback mode")
        
        except Exception as e:
            logger.error(f"❌ Error initializing data sources: {e}")
    
    async def generate_signal_for_symbol(self, symbol: str) -> Optional[Dict]:
        """
        Generate a signal for a single symbol using weighted consensus
        
        Returns:
            Dict with signal data or None if no valid signal
        """
        try:
            # Step 1: Fetch data from all sources
            source_signals = {}
            
            # Massive (primary market data)
            if 'massive' in self.data_sources:
                try:
                    df = self.data_sources['massive'].fetch_price_data(symbol, days=90)
                    if df is not None:
                        signal = self.data_sources['massive'].generate_signal(df, symbol)
                        if signal:
                            source_signals['massive'] = signal
                except Exception as e:
                    logger.debug(f"Massive error for {symbol}: {e}")
            
            # Alpha Vantage (technical indicators)
            if 'alpha_vantage' in self.data_sources:
                try:
                    indicators = self.data_sources['alpha_vantage'].fetch_technical_indicators(symbol)
                    if indicators:
                        signal = self.data_sources['alpha_vantage'].generate_signal(indicators, symbol)
                        if signal:
                            source_signals['alpha_vantage'] = signal
                except Exception as e:
                    logger.debug(f"Alpha Vantage error for {symbol}: {e}")
            
            # XAI Grok (sentiment)
            if 'x_sentiment' in self.data_sources:
                try:
                    sentiment = await self.data_sources['x_sentiment'].fetch_sentiment(symbol)
                    if sentiment:
                        signal = self.data_sources['x_sentiment'].generate_signal(sentiment, symbol)
                        if signal:
                            source_signals['x_sentiment'] = signal
                except Exception as e:
                    logger.debug(f"XAI Grok error for {symbol}: {e}")
            
            # Sonar AI (AI analysis)
            if 'sonar' in self.data_sources:
                try:
                    analysis = await self.data_sources['sonar'].fetch_analysis(symbol)
                    if analysis:
                        signal = self.data_sources['sonar'].generate_signal(analysis, symbol)
                        if signal:
                            source_signals['sonar'] = signal
                except Exception as e:
                    logger.debug(f"Sonar error for {symbol}: {e}")
            
            # Step 2: Calculate weighted consensus
            if not source_signals:
                return None
            
            # Prepare signals for consensus engine
            consensus_input = {}
            for source, signal in source_signals.items():
                consensus_input[source] = {
                    'direction': signal.get('direction', 'NEUTRAL'),
                    'confidence': signal.get('confidence', 0) / 100.0  # Convert to 0-1 scale
                }
            
            consensus = self.consensus_engine.calculate_consensus(consensus_input)
            
            if not consensus:
                return None
            
            # Step 3: Apply 75% consensus threshold (as per investor docs)
            if consensus['confidence'] < 75.0:
                return None
            
            # Step 4: Detect market regime and adjust confidence
            regime = 'UNKNOWN'
            if 'massive' in source_signals and 'massive' in self.data_sources:
                try:
                    df = self.data_sources['massive'].fetch_price_data(symbol, days=200)
                    if df is not None:
                        regime = detect_regime(df)
                        consensus['confidence'] = adjust_confidence(consensus['confidence'], regime)
                except Exception as e:
                    logger.debug(f"Regime detection error: {e}")
            
            # Step 5: Build final signal
            direction = consensus['direction']  # LONG or SHORT
            action = "BUY" if direction == "LONG" else "SELL"
            
            # Get entry price from primary source
            entry_price = None
            if 'massive' in source_signals:
                entry_price = source_signals['massive'].get('entry_price')
            elif 'alpha_vantage' in source_signals:
                entry_price = source_signals['alpha_vantage'].get('indicators', {}).get('current_price')
            
            # Fallback to reasonable defaults if no price available
            if not entry_price:
                # Use symbol-based defaults (will be replaced with real data)
                price_defaults = {
                    "AAPL": 175.0, "NVDA": 460.0, "TSLA": 260.0, "MSFT": 161.0,
                    "BTC-USD": 40000.0, "ETH-USD": 2500.0
                }
                entry_price = price_defaults.get(symbol, 100.0)
            
            # Calculate stop loss and take profit (2-5% risk, 3-10% reward)
            if action == "BUY":
                stop_loss = entry_price * 0.97  # 3% stop loss
                take_profit = entry_price * 1.05  # 5% take profit
            else:  # SELL
                stop_loss = entry_price * 1.03  # 3% stop loss
                take_profit = entry_price * 0.95  # 5% take profit
            
            # Build signal dict
            signal = {
                'symbol': symbol,
                'action': action,
                'entry_price': round(entry_price, 2),
                'target_price': round(take_profit, 2),
                'stop_price': round(stop_loss, 2),
                'confidence': round(consensus['confidence'], 2),
                'strategy': 'weighted_consensus_v6',
                'asset_type': 'crypto' if '-USD' in symbol else 'stock',
                'data_source': 'weighted_consensus',
                'timestamp': datetime.utcnow().isoformat(),
                'regime': regime,
                'consensus_agreement': consensus.get('agreement', 0),
                'sources_count': consensus.get('sources', 0)
            }
            
            # Step 6: Generate AI reasoning
            try:
                reasoning = self.explainer.explain_signal({
                    'symbol': symbol,
                    'action': action,
                    'entry': entry_price,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'confidence': consensus['confidence']
                })
                signal['reasoning'] = reasoning
            except Exception as e:
                logger.debug(f"Reasoning generation error: {e}")
                signal['reasoning'] = f"Weighted consensus ({consensus.get('sources', 0)} sources) indicates {action} opportunity with {consensus['confidence']:.1f}% confidence in {regime} market regime."
            
            return signal
        
        except Exception as e:
            logger.error(f"❌ Error generating signal for {symbol}: {e}")
            return None
    
    async def generate_signals_cycle(self, symbols: List[str] = None) -> List[Dict]:
        """
        Generate signals for all symbols in one cycle
        
        Returns:
            List of generated signals
        """
        if symbols is None:
            symbols = DEFAULT_SYMBOLS
        
        generated_signals = []
        
        for symbol in symbols:
            try:
                signal = await self.generate_signal_for_symbol(symbol)
                if signal:
                    # Store signal in database
                    signal_id = self.tracker.log_signal(signal)
                    signal['signal_id'] = signal_id
                    generated_signals.append(signal)
                    logger.info(f"✅ Generated signal: {symbol} {signal['action']} @ ${signal['entry_price']} ({signal['confidence']}% confidence)")
            except Exception as e:
                logger.error(f"❌ Error in signal cycle for {symbol}: {e}")
        
        return generated_signals
    
    async def start_background_generation(self, interval_seconds: int = 5):
        """
        Start background signal generation task
        
        Args:
            interval_seconds: Time between signal generation cycles (default: 5 seconds)
        """
        self.running = True
        logger.info(f"🚀 Starting background signal generation (every {interval_seconds} seconds)")
        
        while self.running:
            try:
                start_time = datetime.utcnow()
                
                # Generate signals for all symbols
                signals = await self.generate_signals_cycle()
                
                elapsed = (datetime.utcnow() - start_time).total_seconds()
                logger.info(f"📊 Generated {len(signals)} signals in {elapsed:.2f}s")
                
                # Wait for next cycle
                await asyncio.sleep(interval_seconds)
            
            except Exception as e:
                logger.error(f"❌ Error in background generation cycle: {e}")
                await asyncio.sleep(interval_seconds)
    
    def stop(self):
        """Stop background signal generation"""
        self.running = False
        logger.info("🛑 Signal generation service stopped")

# Global instance
_signal_service: Optional[SignalGenerationService] = None

def get_signal_service() -> SignalGenerationService:
    """Get or create global signal generation service instance"""
    global _signal_service
    if _signal_service is None:
        _signal_service = SignalGenerationService()
    return _signal_service


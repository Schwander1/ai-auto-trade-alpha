#!/usr/bin/env python3
"""
TRADE SECRET - PROPRIETARY ALGORITHM
Argo Capital - Confidential

Market Regime Detector

This code contains proprietary algorithms and trade secrets.
Unauthorized disclosure, copying, or use is strictly prohibited.

PATENT-PENDING TECHNOLOGY
Patent Application: [Application Number]
Filing Date: [Date]

This code implements patent-pending technology.
Unauthorized use may infringe on pending patent rights.
"""
import pandas as pd
import logging
from typing import Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RegimeDetector")

def detect_regime(price_data):
    """
    Detect current market regime: BULL, BEAR, CHOP, or CRISIS
    
    Args:
        price_data (pd.DataFrame): DataFrame with 'Close' column
    
    Returns:
        str: Regime classification
    """
    try:
        if len(price_data) < 200:
            return 'UNKNOWN'
        
        # Calculate moving averages
        sma_20 = price_data['Close'].rolling(20).mean().iloc[-1]
        sma_50 = price_data['Close'].rolling(50).mean().iloc[-1]
        sma_200 = price_data['Close'].rolling(200).mean().iloc[-1]
        
        # Calculate volatility
        returns = price_data['Close'].pct_change()
        volatility_20 = returns.rolling(20).std().iloc[-1]
        volatility_50 = returns.rolling(50).std().iloc[-1]
        
        # CRISIS: High volatility spike
        if volatility_20 > volatility_50 * 1.5:
            return 'CRISIS'
        
        # BULL: Uptrend across all timeframes
        elif sma_20 > sma_50 > sma_200:
            return 'BULL'
        
        # BEAR: Downtrend across all timeframes
        elif sma_20 < sma_50 < sma_200:
            return 'BEAR'
        
        # CHOP: No clear trend
        else:
            return 'CHOP'
            
    except Exception as e:
        logger.error(f"❌ Error detecting regime: {e}")
        return 'UNKNOWN'

def detect_regime_enhanced(price_data):
    """
    Enhanced regime detection: TRENDING / CONSOLIDATION / VOLATILE
    
    Args:
        price_data (pd.DataFrame): DataFrame with 'Close', 'High', 'Low' columns
    
    Returns:
        str: 'TRENDING', 'CONSOLIDATION', 'VOLATILE', or 'UNKNOWN'
    """
    try:
        if len(price_data) < 200:
            return 'UNKNOWN'
        
        current_price = price_data['Close'].iloc[-1]
        
        # Calculate ATR (Average True Range) for volatility
        if 'High' in price_data.columns and 'Low' in price_data.columns:
            high_low = price_data['High'] - price_data['Low']
            high_close = abs(price_data['High'] - price_data['Close'].shift())
            low_close = abs(price_data['Low'] - price_data['Close'].shift())
            true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            atr = true_range.rolling(14).mean().iloc[-1]
            atr_pct = (atr / current_price) * 100
        else:
            # Fallback: use returns volatility
            returns = price_data['Close'].pct_change()
            atr_pct = returns.rolling(14).std().iloc[-1] * 100
        
        # Calculate trend strength
        sma_20 = price_data['Close'].rolling(20).mean().iloc[-1]
        sma_50 = price_data['Close'].rolling(50).mean().iloc[-1]
        sma_200 = price_data['Close'].rolling(200).mean().iloc[-1]
        
        # Trend strength (how far price is from moving averages)
        trend_strength = abs(current_price - sma_200) / sma_200 * 100
        
        # Classify regime
        if atr_pct > 3.0:  # High volatility
            return 'VOLATILE'
        elif trend_strength > 10.0 and (sma_20 > sma_50 > sma_200 or sma_20 < sma_50 < sma_200):
            return 'TRENDING'
        else:
            return 'CONSOLIDATION'
            
    except Exception as e:
        logger.error(f"❌ Error detecting enhanced regime: {e}")
        return 'UNKNOWN'

def get_regime_weights(regime: str) -> Dict[str, float]:
    """
    Get optimized weights for each regime
    
    Args:
        regime: Market regime ('TRENDING', 'CONSOLIDATION', 'VOLATILE', 'UNKNOWN')
    
    Returns:
        Dict mapping source -> weight
    """
    regime_weights = {
        'TRENDING': {
            'massive': 0.55,
            'alpha_vantage': 0.25,
            'xai_grok': 0.15,
            'sonar': 0.05
        },
        'CONSOLIDATION': {
            'massive': 0.40,
            'alpha_vantage': 0.30,
            'xai_grok': 0.20,
            'sonar': 0.10
        },
        'VOLATILE': {
            'massive': 0.45,
            'alpha_vantage': 0.30,
            'xai_grok': 0.15,
            'sonar': 0.10
        },
        'UNKNOWN': {
            'massive': 0.50,  # Default to optimized weights
            'alpha_vantage': 0.30,
            'xai_grok': 0.15,
            'sonar': 0.05
        }
    }
    return regime_weights.get(regime, regime_weights['UNKNOWN'])

def map_legacy_regime_to_enhanced(legacy_regime: str) -> str:
    """
    Map legacy regime types to enhanced regime types
    
    Args:
        legacy_regime: 'BULL', 'BEAR', 'CHOP', 'CRISIS', 'UNKNOWN'
    
    Returns:
        Enhanced regime: 'TRENDING', 'CONSOLIDATION', 'VOLATILE', 'UNKNOWN'
    """
    mapping = {
        'BULL': 'TRENDING',
        'BEAR': 'TRENDING',  # Bear trends are still trends
        'CHOP': 'CONSOLIDATION',
        'CRISIS': 'VOLATILE',
        'UNKNOWN': 'UNKNOWN'
    }
    return mapping.get(legacy_regime, 'UNKNOWN')

def adjust_confidence(base_confidence, regime):
    """
    Adjust signal confidence based on market regime
    IMPROVEMENT: Only apply negative adjustments, not positive boosts
    
    Args:
        base_confidence (float): Original confidence score
        regime (str): Market regime
    
    Returns:
        float: Adjusted confidence
    """
    adjustments = {
        'BULL': 1.00,    # No boost - keep as-is (prevent artificial inflation)
        'BEAR': 0.95,    # Slight reduction in downtrend
        'CHOP': 0.90,    # Reduce in sideways market
        'CRISIS': 0.85,  # Reduce most during high volatility
        'UNKNOWN': 1.00,
        # Enhanced regimes
        'TRENDING': 1.00,      # No boost for trending
        'CONSOLIDATION': 0.90, # Reduce in consolidation
        'VOLATILE': 0.90       # Reduce in volatile markets
    }
    
    return min(base_confidence * adjustments.get(regime, 1.0), 98.0)

if __name__ == "__main__":
    # Test
    print("Regime Detector ready")

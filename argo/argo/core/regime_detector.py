#!/usr/bin/env python3
"""Alpine Analytics - Market Regime Detector"""
import pandas as pd
import logging

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

def adjust_confidence(base_confidence, regime):
    """
    Adjust signal confidence based on market regime
    
    Args:
        base_confidence (float): Original confidence score
        regime (str): Market regime
    
    Returns:
        float: Adjusted confidence
    """
    adjustments = {
        'BULL': 1.05,    # Boost in clear uptrend
        'BEAR': 0.95,    # Slight reduction in downtrend
        'CHOP': 0.90,    # Reduce in sideways market
        'CRISIS': 0.85,  # Reduce most during high volatility
        'UNKNOWN': 1.00
    }
    
    return min(base_confidence * adjustments.get(regime, 1.0), 98.0)

if __name__ == "__main__":
    # Test
    print("Regime Detector ready")

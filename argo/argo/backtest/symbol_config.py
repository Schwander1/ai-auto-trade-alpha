#!/usr/bin/env python3
"""
Symbol Configuration
Symbol-specific trading configurations for adaptive stops, position sizing, etc.
"""
from typing import Dict, Optional, Tuple
from .symbol_classifier import SymbolClassifier
from .constants import TradingConstants


class SymbolConfig:
    """Configuration for symbol-specific trading parameters"""
    
    # Default configuration (v6: Push threshold symbols over 1.0)
    DEFAULT_CONFIG: Dict = {
        'stop_multiplier': 1.85,
        'profit_multiplier': 3.5,  # v6: Increased from 3.45
        'max_stop_pct': 0.07,  # 7%
        'max_profit_pct': 0.30,  # 30% (v6: Increased from 28%)
        'position_size_adjustment': 1.0,  # No adjustment
        'trailing_stop_pct': 0.065,  # 6.5%
        'time_based_exit_days': TradingConstants.DEFAULT_TIME_BASED_EXIT_DAYS,
    }
    
    # Crypto configuration
    CRYPTO_CONFIG: Dict = {
        'stop_multiplier': 1.7,
        'profit_multiplier': 3.0,
        'max_stop_pct': 0.06,  # 6%
        'max_profit_pct': 0.22,  # 22%
        'position_size_adjustment': 0.88,  # 12% reduction
        'trailing_stop_pct': 0.075,  # 7.5%
        'time_based_exit_days': 25,
    }
    
    # Symbol-specific configurations
    SYMBOL_CONFIGS: Dict[str, Dict] = {
        'SPY': {
            'stop_multiplier': 1.2,  # Even tighter (was 1.3) for drawdown reduction
            'profit_multiplier': 5.0,  # Keep wide profit targets
            'max_stop_pct': 0.025,  # 2.5% (tighter from 3%) for drawdown reduction
            'max_profit_pct': 0.35,  # 35%
            'position_size_adjustment': 0.95,  # 5% reduction for risk control
            'trailing_stop_pct': 0.05,  # 5% (tighter from 6%)
            'time_based_exit_days': 30,  # Shorter holding period
        },
        'AMZN': {
            'stop_multiplier': 1.4,  # Tighter stops (was 1.6) for drawdown reduction
            'profit_multiplier': 3.9,
            'max_stop_pct': 0.05,  # 5% (tighter from 6%) for drawdown reduction
            'max_profit_pct': 0.32,  # 32%
            'position_size_adjustment': 0.90,  # 10% reduction for risk control
            'trailing_stop_pct': 0.055,  # 5.5% (tighter from 6%)
            'time_based_exit_days': 25,  # Shorter holding period
        },
        'NVDA': {
            'stop_multiplier': 1.85,
            'profit_multiplier': 3.7,
            'max_stop_pct': 0.07,  # 7%
            'max_profit_pct': 0.32,  # 32%
            'position_size_adjustment': 1.0,
            'trailing_stop_pct': 0.065,
            'time_based_exit_days': 30,
        },
        'GOOGL': {
            'stop_multiplier': 2.0,
            'profit_multiplier': 3.7,  # v6: Increased from 3.6 to push over 1.0
            'max_stop_pct': 0.07,  # 7%
            'max_profit_pct': 0.35,  # 35% (v6: Increased from 32%)
            'position_size_adjustment': 1.0,
            'trailing_stop_pct': 0.06,  # 6%
            'time_based_exit_days': 30,
        },
        'META': {
            'stop_multiplier': 1.8,
            'profit_multiplier': 3.7,
            'max_stop_pct': 0.07,  # 7%
            'max_profit_pct': 0.32,  # 32%
            'position_size_adjustment': 0.95,  # 5% reduction
            'trailing_stop_pct': 0.07,  # 7%
            'time_based_exit_days': 28,
        },
        'MSFT': {
            'stop_multiplier': 1.75,
            'profit_multiplier': 3.8,  # v6: Increased from 3.7 to push over 1.0
            'max_stop_pct': 0.07,  # 7%
            'max_profit_pct': 0.35,  # 35% (v6: Increased from 30%)
            'position_size_adjustment': 1.0,
            'trailing_stop_pct': 0.06,  # 6%
            'time_based_exit_days': 30,
        },
        'AMD': {
            'stop_multiplier': 1.5,  # Tighter stops (was 1.75) for drawdown reduction
            'profit_multiplier': 3.7,
            'max_stop_pct': 0.05,  # 5% (tighter from 7%) for drawdown reduction
            'max_profit_pct': 0.30,  # 30%
            'position_size_adjustment': 0.90,  # 10% reduction (was 5%) for risk control
            'trailing_stop_pct': 0.06,  # 6% (tighter from 7%)
            'time_based_exit_days': 25,  # Shorter holding period
        },
        'QQQ': {
            'stop_multiplier': 1.75,
            'profit_multiplier': 3.7,
            'max_stop_pct': 0.07,  # 7%
            'max_profit_pct': 0.30,  # 30%
            'position_size_adjustment': 1.0,
            'trailing_stop_pct': 0.06,  # 6%
            'time_based_exit_days': 35,
        },
        'TSLA': {
            'stop_multiplier': 1.8,
            'profit_multiplier': 3.6,
            'max_stop_pct': 0.07,  # 7%
            'max_profit_pct': 0.30,  # 30%
            'position_size_adjustment': 0.95,  # 5% reduction
            'trailing_stop_pct': 0.07,  # 7%
            'time_based_exit_days': 28,
        },
        'AAPL': {
            'stop_multiplier': 1.85,
            'profit_multiplier': 3.5,
            'max_stop_pct': 0.07,  # 7%
            'max_profit_pct': 0.28,  # 28%
            'position_size_adjustment': 1.0,
            'trailing_stop_pct': 0.065,
            'time_based_exit_days': 30,
        },
    }
    
    @staticmethod
    def get_config(symbol: Optional[str]) -> Dict:
        """
        Get symbol-specific configuration
        
        Args:
            symbol: Trading symbol (e.g., 'AAPL', 'BTC-USD')
            
        Returns:
            Dictionary with configuration parameters
        """
        if not symbol:
            return SymbolConfig.DEFAULT_CONFIG.copy()
        
        # Check for crypto first
        if SymbolClassifier.is_crypto(symbol):
            return SymbolConfig.CRYPTO_CONFIG.copy()
        
        # Check for symbol-specific config
        if symbol in SymbolConfig.SYMBOL_CONFIGS:
            return SymbolConfig.SYMBOL_CONFIGS[symbol].copy()
        
        # Return default
        return SymbolConfig.DEFAULT_CONFIG.copy()
    
    @staticmethod
    def get_stop_multipliers(symbol: Optional[str]) -> tuple[float, float]:
        """
        Get stop and profit multipliers for a symbol
        
        Returns:
            Tuple of (stop_multiplier, profit_multiplier)
        """
        config = SymbolConfig.get_config(symbol)
        return config['stop_multiplier'], config['profit_multiplier']
    
    @staticmethod
    def get_stop_limits(symbol: Optional[str], action: str) -> Tuple[float, float]:
        """
        Get max stop loss and take profit percentages for a symbol
        
        Args:
            symbol: Trading symbol
            action: 'BUY' or 'SELL'
            
        Returns:
            Tuple of (max_stop_pct, max_profit_pct) for BUY
            For SELL, returns (max_stop_pct, min_profit_pct) where values are inverted
        """
        config = SymbolConfig.get_config(symbol)
        
        if action == 'BUY':
            return config['max_stop_pct'], config['max_profit_pct']
        else:  # SELL/SHORT
            # For SELL, stop is above entry, profit is below entry
            # So we need to invert the logic
            if SymbolClassifier.is_crypto(symbol):
                return 0.07, 0.82  # 7% stop above, 18% profit below
            else:
                return 0.08, 0.80  # 8% stop above, 20% profit below


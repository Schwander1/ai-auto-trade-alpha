#!/usr/bin/env python3
"""
Symbol Classifier
Utility for classifying and categorizing trading symbols
"""
from typing import Set, Optional


class SymbolClassifier:
    """Classifies symbols into categories for trading logic"""
    
    # Symbol categories
    CRYPTO_SUFFIX: str = '-USD'
    HIGH_VOLATILITY_STOCKS: Set[str] = {'META', 'TSLA', 'AMD'}
    STABLE_ETFS: Set[str] = {'SPY', 'QQQ'}
    STABLE_STOCKS: Set[str] = {'MSFT', 'GOOGL', 'AAPL'}
    
    @staticmethod
    def is_crypto(symbol: Optional[str]) -> bool:
        """Check if symbol is a cryptocurrency"""
        if not symbol:
            return False
        return symbol.endswith(SymbolClassifier.CRYPTO_SUFFIX)
    
    @staticmethod
    def is_high_volatility(symbol: Optional[str]) -> bool:
        """Check if symbol is a high volatility stock"""
        if not symbol:
            return False
        return symbol in SymbolClassifier.HIGH_VOLATILITY_STOCKS
    
    @staticmethod
    def is_stable_etf(symbol: Optional[str]) -> bool:
        """Check if symbol is a stable ETF"""
        if not symbol:
            return False
        return symbol in SymbolClassifier.STABLE_ETFS
    
    @staticmethod
    def is_stable_stock(symbol: Optional[str]) -> bool:
        """Check if symbol is a stable stock"""
        if not symbol:
            return False
        return symbol in SymbolClassifier.STABLE_STOCKS
    
    @staticmethod
    def get_symbol_type(symbol: Optional[str]) -> str:
        """
        Get the type/category of a symbol
        
        Returns:
            'crypto', 'high_volatility', 'stable_etf', 'stable_stock', or 'stock'
        """
        if not symbol:
            return 'stock'
        
        if SymbolClassifier.is_crypto(symbol):
            return 'crypto'
        elif SymbolClassifier.is_high_volatility(symbol):
            return 'high_volatility'
        elif SymbolClassifier.is_stable_etf(symbol):
            return 'stable_etf'
        elif SymbolClassifier.is_stable_stock(symbol):
            return 'stable_stock'
        else:
            return 'stock'


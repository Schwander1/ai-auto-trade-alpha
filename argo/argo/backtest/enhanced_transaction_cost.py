#!/usr/bin/env python3
"""
Enhanced Transaction Cost Model
Realistic cost modeling with square-root slippage (industry standard)
Compliance: Industry best practices for backtesting
"""
import numpy as np
from typing import Dict, Literal, Optional
import logging

logger = logging.getLogger(__name__)

class EnhancedTransactionCostModel:
    """Realistic cost modeling with square-root slippage"""
    
    def __init__(self):
        # Commission (Alpaca is zero, but model for realism)
        self.commission_per_share = 0.0
        
        # Bid-ask spread (varies by liquidity)
        self.spread_bps = {
            'high_liquidity': 1,    # SPY, QQQ: 0.01%
            'medium_liquidity': 5,   # Mid-caps: 0.05%
            'low_liquidity': 20      # Small-caps: 0.20%
        }
        
        # Slippage model
        self.slippage_model = 'sqrt'  # Square root model (industry standard)
    
    def calculate_slippage(
        self,
        trade_size: float,
        avg_volume: float,
        volatility: float
    ) -> float:
        """
        Square-root market impact model (industry standard)
        
        Slippage = sigma * sqrt(trade_size / avg_volume) * 0.1
        
        Args:
            trade_size: Size of trade (in shares or dollars)
            avg_volume: Average daily volume
            volatility: Daily volatility (standard deviation of returns)
        
        Returns:
            Slippage as decimal (e.g., 0.0005 = 0.05%)
        """
        if avg_volume == 0:
            return 0.0
        
        participation_rate = trade_size / avg_volume
        
        # Square root model (industry standard)
        # Prevents over-estimating slippage for large trades
        slippage_bps = volatility * np.sqrt(participation_rate) * 10
        
        return slippage_bps / 10000  # Convert to decimal
    
    def determine_liquidity_tier(
        self,
        symbol: str,
        avg_volume: float
    ) -> Literal['high_liquidity', 'medium_liquidity', 'low_liquidity']:
        """
        Determine liquidity tier based on symbol and volume
        
        Args:
            symbol: Trading symbol
            avg_volume: Average daily volume
        
        Returns:
            Liquidity tier
        """
        # High liquidity: Major indices and large caps
        high_liquidity_symbols = ['SPY', 'QQQ', 'DIA', 'IWM', 'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA']
        
        if symbol in high_liquidity_symbols or avg_volume > 10_000_000:
            return 'high_liquidity'
        elif avg_volume > 1_000_000:
            return 'medium_liquidity'
        else:
            return 'low_liquidity'
    
    def total_cost(
        self,
        trade_size: float,
        price: float,
        symbol: str,
        avg_volume: float,
        volatility: float,
        liquidity_tier: Optional[Literal['high_liquidity', 'medium_liquidity', 'low_liquidity']] = None
    ) -> float:
        """
        Calculate total transaction cost
        
        Args:
            trade_size: Size of trade (in shares)
            price: Current price
            liquidity_tier: Liquidity tier (auto-determined if None)
            avg_volume: Average daily volume
            volatility: Daily volatility
        
        Returns:
            Total cost in dollars
        """
        # Determine liquidity tier if not provided
        if liquidity_tier is None:
            liquidity_tier = self.determine_liquidity_tier(symbol, avg_volume)
        
        # Spread cost
        spread_bps = self.spread_bps[liquidity_tier]
        spread_cost = (spread_bps / 10000) * price
        
        # Slippage cost
        trade_value = trade_size * price
        slippage_cost = self.calculate_slippage(trade_value, avg_volume * price, volatility) * price
        
        # Commission
        commission = self.commission_per_share * trade_size
        
        total = spread_cost + slippage_cost + commission
        
        return total
    
    def apply_costs_to_price(
        self,
        price: float,
        side: Literal['LONG', 'SHORT'],
        symbol: str,
        trade_size: float,
        avg_volume: float,
        volatility: float,
        is_entry: bool = True
    ) -> float:
        """
        Apply transaction costs to price
        
        Args:
            price: Base price
            side: 'LONG' or 'SHORT'
            symbol: Trading symbol
            trade_size: Size of trade (in shares)
            avg_volume: Average daily volume
            volatility: Daily volatility
            is_entry: True for entry, False for exit
        
        Returns:
            Adjusted price with costs
        """
        # Calculate total cost
        total_cost = self.total_cost(trade_size, price, symbol, avg_volume, volatility)
        cost_per_share = total_cost / trade_size if trade_size > 0 else 0
        
        if side == 'LONG':
            if is_entry:
                # Buying: pay more
                return price + cost_per_share
            else:
                # Selling: receive less
                return price - cost_per_share
        else:
            # SHORT: selling first, then buying back
            if is_entry:
                # Selling: receive less
                return price - cost_per_share
            else:
                # Buying back: pay more
                return price + cost_per_share


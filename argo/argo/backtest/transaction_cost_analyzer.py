#!/usr/bin/env python3
"""
Transaction Cost Analyzer
Comprehensive transaction cost analysis for realistic P&L.
Essential for prop firm profitability assessment.
"""
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional
import numpy as np

logger = logging.getLogger(__name__)

class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"

@dataclass
class TransactionCosts:
    commission: float
    spread: float
    slippage: float
    market_impact: float
    total: float

@dataclass
class Order:
    """Order representation"""
    symbol: str
    shares: int
    price: float
    side: str  # "buy" or "sell"
    type: OrderType

class TransactionCostAnalyzer:
    """
    Comprehensive transaction cost analysis for realistic P&L.
    Essential for prop firm profitability assessment.
    """
    def __init__(self, config: Optional[Dict] = None):
        if config is None:
            config = {}
            
        self.base_commission = config.get("commission_per_share", 0.0035)
        self.min_commission = config.get("min_commission", 0.35)
        self.max_commission = config.get("max_commission", 1.0)
        
    def calculate_costs(self, order: Order, market_data: Dict) -> TransactionCosts:
        """Calculate all transaction costs for an order"""
        # 1. Commission
        commission = self._calculate_commission(order)
        
        # 2. Bid-ask spread
        spread = self._calculate_spread_cost(order, market_data)
        
        # 3. Slippage (market orders only)
        slippage = self._calculate_slippage(order, market_data)
        
        # 4. Market impact (large orders)
        market_impact = self._calculate_market_impact(order, market_data)
        
        total = commission + spread + slippage + market_impact
        
        return TransactionCosts(
            commission=commission,
            spread=spread,
            slippage=slippage,
            market_impact=market_impact,
            total=total
        )
        
    def _calculate_commission(self, order: Order) -> float:
        """Calculate commission based on shares and price"""
        commission = order.shares * self.base_commission
        return max(self.min_commission, min(commission, self.max_commission))
        
    def _calculate_spread_cost(self, order: Order, market_data: Dict) -> float:
        """Calculate effective cost from bid-ask spread"""
        bid = market_data.get("bid", order.price)
        ask = market_data.get("ask", order.price)
        spread = ask - bid
        
        # Buy orders pay the spread, sell orders receive it
        spread_cost = (spread / 2) * order.shares
        return spread_cost if order.side == "buy" else -spread_cost
        
    def _calculate_slippage(self, order: Order, market_data: Dict) -> float:
        """
        Calculate slippage for market orders.
        Based on volatility and order size relative to volume.
        """
        if order.type != OrderType.MARKET:
            return 0.0
            
        volatility = market_data.get("volatility", 0.02)
        avg_volume = market_data.get("avg_volume", 1000000)
        
        # Slippage increases with volatility and order size
        volume_ratio = order.shares / avg_volume if avg_volume > 0 else 0
        slippage_pct = volatility * (1 + volume_ratio * 10)  # Amplify for large orders
        
        return order.price * order.shares * slippage_pct
        
    def _calculate_market_impact(self, order: Order, market_data: Dict) -> float:
        """
        Calculate market impact for large orders.
        Uses square root model: impact ∝ √(order_size / avg_volume)
        """
        avg_volume = market_data.get("avg_volume", 1000000)
        volume_ratio = order.shares / avg_volume if avg_volume > 0 else 0
        
        if volume_ratio < 0.01:  # Less than 1% of volume, negligible impact
            return 0.0
            
        # Impact coefficient (calibrated to market)
        impact_coefficient = 0.1
        impact_pct = impact_coefficient * np.sqrt(volume_ratio)
        
        return order.price * order.shares * impact_pct
        
    def calculate_effective_price(self, order: Order, market_data: Dict) -> float:
        """
        Calculate effective execution price including all costs.
        """
        costs = self.calculate_costs(order, market_data)
        cost_per_share = costs.total / order.shares if order.shares > 0 else 0
        
        # Buy orders: add costs to price
        # Sell orders: subtract costs from price
        if order.side == "buy":
            return order.price + cost_per_share
        else:
            return order.price - cost_per_share


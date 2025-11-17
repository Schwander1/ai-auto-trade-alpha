"""
Unit tests for Transaction Cost Analysis
"""
import pytest
from argo.backtest.transaction_cost_analyzer import (
    TransactionCostAnalyzer,
    Order,
    OrderType,
    TransactionCosts
)

def test_commission_calculation():
    """Test commission calculation"""
    analyzer = TransactionCostAnalyzer()
    
    order = Order(
        symbol='AAPL',
        shares=100,
        price=175.0,
        side='buy',
        type=OrderType.MARKET
    )
    
    costs = analyzer.calculate_costs(order, {})
    assert costs.commission > 0
    assert costs.commission >= analyzer.min_commission

def test_spread_cost():
    """Test spread cost calculation"""
    analyzer = TransactionCostAnalyzer()
    
    order = Order(
        symbol='AAPL',
        shares=100,
        price=175.0,
        side='buy',
        type=OrderType.MARKET
    )
    
    market_data = {
        'bid': 174.95,
        'ask': 175.05
    }
    
    costs = analyzer.calculate_costs(order, market_data)
    # Buy orders pay spread, so spread cost should be positive
    assert costs.spread > 0

def test_slippage_calculation():
    """Test slippage calculation for market orders"""
    analyzer = TransactionCostAnalyzer()
    
    # Market order should have slippage
    market_order = Order(
        symbol='AAPL',
        shares=100,
        price=175.0,
        side='buy',
        type=OrderType.MARKET
    )
    
    market_data = {
        'volatility': 0.02,
        'avg_volume': 1000000
    }
    
    costs = analyzer.calculate_costs(market_order, market_data)
    assert costs.slippage > 0
    
    # Limit order should have no slippage
    limit_order = Order(
        symbol='AAPL',
        shares=100,
        price=175.0,
        side='buy',
        type=OrderType.LIMIT
    )
    
    costs_limit = analyzer.calculate_costs(limit_order, market_data)
    assert costs_limit.slippage == 0.0

def test_market_impact():
    """Test market impact calculation for large orders"""
    analyzer = TransactionCostAnalyzer()
    
    # Small order (no impact)
    small_order = Order(
        symbol='AAPL',
        shares=1000,  # 0.1% of volume
        price=175.0,
        side='buy',
        type=OrderType.MARKET
    )
    
    market_data = {
        'avg_volume': 1000000
    }
    
    costs_small = analyzer.calculate_costs(small_order, market_data)
    assert costs_small.market_impact == 0.0  # < 1% of volume
    
    # Large order (has impact)
    large_order = Order(
        symbol='AAPL',
        shares=50000,  # 5% of volume
        price=175.0,
        side='buy',
        type=OrderType.MARKET
    )
    
    costs_large = analyzer.calculate_costs(large_order, market_data)
    assert costs_large.market_impact > 0

def test_effective_price():
    """Test effective price calculation"""
    analyzer = TransactionCostAnalyzer()
    
    order = Order(
        symbol='AAPL',
        shares=100,
        price=175.0,
        side='buy',
        type=OrderType.MARKET
    )
    
    market_data = {
        'bid': 174.95,
        'ask': 175.05,
        'volatility': 0.02,
        'avg_volume': 1000000
    }
    
    effective_price = analyzer.calculate_effective_price(order, market_data)
    # Effective price should be higher than order price for buy orders
    assert effective_price > order.price


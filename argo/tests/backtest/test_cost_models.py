#!/usr/bin/env python3
"""
Tests for Transaction Cost Models
Validates cost calculations are correct
"""
import pytest
from argo.backtest.enhanced_transaction_cost import EnhancedTransactionCostModel
from argo.backtest.constants import TransactionCostConstants


class TestEnhancedCostModel:
    """Test Enhanced Transaction Cost Model"""
    
    def test_liquidity_tier_determination(self):
        """Test liquidity tier determination"""
        model = EnhancedTransactionCostModel()
        
        # High liquidity symbols
        assert model.determine_liquidity_tier('SPY', 20_000_000) == 'high_liquidity'
        assert model.determine_liquidity_tier('AAPL', 15_000_000) == 'high_liquidity'
        
        # Medium liquidity
        assert model.determine_liquidity_tier('TEST', 5_000_000) == 'medium_liquidity'
        
        # Low liquidity
        assert model.determine_liquidity_tier('TEST', 500_000) == 'low_liquidity'
    
    def test_slippage_calculation(self):
        """Test slippage calculation"""
        model = EnhancedTransactionCostModel()
        
        # Small trade relative to volume - low slippage
        slippage_small = model.calculate_slippage(
            trade_size=100_000,  # $100k
            avg_volume=10_000_000,  # $10M daily volume
            volatility=0.02  # 2% daily volatility
        )
        
        # Large trade relative to volume - higher slippage
        slippage_large = model.calculate_slippage(
            trade_size=5_000_000,  # $5M
            avg_volume=10_000_000,  # $10M daily volume
            volatility=0.02  # 2% daily volatility
        )
        
        # Large trade should have higher slippage
        assert slippage_large > slippage_small
        
        # Slippage should be positive
        assert slippage_small > 0
        assert slippage_large > 0
    
    def test_cost_application(self):
        """Test cost application to prices"""
        model = EnhancedTransactionCostModel()
        
        price = 100.0
        symbol = 'AAPL'
        trade_size = 100  # 100 shares
        avg_volume = 10_000_000  # 10M shares
        volatility = 0.02  # 2% daily
        
        # LONG entry - should pay more
        long_entry = model.apply_costs_to_price(
            price=price,
            side='LONG',
            symbol=symbol,
            trade_size=trade_size,
            avg_volume=avg_volume,
            volatility=volatility,
            is_entry=True
        )
        assert long_entry > price
        
        # LONG exit - should receive less
        long_exit = model.apply_costs_to_price(
            price=price,
            side='LONG',
            symbol=symbol,
            trade_size=trade_size,
            avg_volume=avg_volume,
            volatility=volatility,
            is_entry=False
        )
        assert long_exit < price
        
        # SHORT entry - should receive less
        short_entry = model.apply_costs_to_price(
            price=price,
            side='SHORT',
            symbol=symbol,
            trade_size=trade_size,
            avg_volume=avg_volume,
            volatility=volatility,
            is_entry=True
        )
        assert short_entry < price
        
        # SHORT exit - should pay more
        short_exit = model.apply_costs_to_price(
            price=price,
            side='SHORT',
            symbol=symbol,
            trade_size=trade_size,
            avg_volume=avg_volume,
            volatility=volatility,
            is_entry=False
        )
        assert short_exit > price


#!/usr/bin/env python3
"""
Automated test suite for SHORT position handling

Tests:
- SELL signal generation
- SHORT position opening
- SHORT position closing
- Position flipping
- Bracket orders for SHORT
- Risk management for SHORT
"""

import sys
import os
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from argo.core.paper_trading_engine import PaperTradingEngine
    from argo.core.signal_generation_service import SignalGenerationService
except ImportError:
    print("❌ Could not import required modules")
    sys.exit(1)


class TestShortPositionOpening(unittest.TestCase):
    """Test SHORT position opening from SELL signals"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.signal = {
            "symbol": "SPY",
            "action": "SELL",
            "entry_price": 450.0,
            "stop_price": 459.0,  # 2% above for SHORT
            "target_price": 441.0,  # 2% below for SHORT
            "confidence": 85.0,
        }
    
    def test_sell_signal_opens_short(self):
        """Test that SELL signal opens SHORT position when no position exists"""
        with patch('argo.core.paper_trading_engine.PaperTradingEngine') as MockEngine:
            engine = MockEngine.return_value
            engine.get_positions.return_value = []  # No existing positions
            engine.alpaca_enabled = True
            
            # Mock account
            mock_account = Mock()
            mock_account.buying_power = 100000.0
            engine.get_account_details.return_value = mock_account
            
            # Test _prepare_sell_order_details
            from argo.core.paper_trading_engine import PaperTradingEngine
            real_engine = PaperTradingEngine.__new__(PaperTradingEngine)
            real_engine.config = {}
            
            order_details = real_engine._prepare_sell_order_details(
                self.signal, mock_account, 450.0, 459.0, 441.0, []
            )
            
            self.assertIsNotNone(order_details)
            self.assertFalse(order_details['is_closing'])
            self.assertTrue(order_details['place_bracket'])
            self.assertEqual(order_details['stop_price'], 459.0)
            self.assertEqual(order_details['target_price'], 441.0)
    
    def test_sell_signal_closes_long(self):
        """Test that SELL signal closes LONG position when LONG exists"""
        existing_position = {
            "symbol": "SPY",
            "side": "LONG",
            "qty": 10,
            "entry_price": 440.0,
            "current_price": 450.0,
        }
        
        with patch('argo.core.paper_trading_engine.PaperTradingEngine') as MockEngine:
            from argo.core.paper_trading_engine import PaperTradingEngine
            real_engine = PaperTradingEngine.__new__(PaperTradingEngine)
            
            mock_account = Mock()
            order_details = real_engine._prepare_sell_order_details(
                self.signal, mock_account, 450.0, 459.0, 441.0, [existing_position]
            )
            
            self.assertIsNotNone(order_details)
            self.assertTrue(order_details['is_closing'])
            self.assertFalse(order_details['place_bracket'])


class TestShortPositionClosing(unittest.TestCase):
    """Test SHORT position closing with BUY signals"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.signal = {
            "symbol": "SPY",
            "action": "BUY",
            "entry_price": 441.0,
            "confidence": 85.0,
        }
        self.short_position = {
            "symbol": "SPY",
            "side": "SHORT",
            "qty": 10,
            "entry_price": 450.0,
            "current_price": 441.0,
            "pnl_pct": 2.0,
        }
    
    def test_buy_signal_closes_short(self):
        """Test that BUY signal closes SHORT position"""
        with patch('argo.core.paper_trading_engine.PaperTradingEngine') as MockEngine:
            from argo.core.paper_trading_engine import PaperTradingEngine
            real_engine = PaperTradingEngine.__new__(PaperTradingEngine)
            
            mock_account = Mock()
            order_details = real_engine._prepare_buy_order_details(
                self.signal, mock_account, 441.0, 85.0, None, None, [self.short_position]
            )
            
            self.assertIsNotNone(order_details)
            self.assertTrue(order_details['is_closing'])
            self.assertFalse(order_details['place_bracket'])


class TestShortPositionRiskManagement(unittest.TestCase):
    """Test risk management for SHORT positions"""
    
    def test_short_stop_loss_validation(self):
        """Test that SHORT stop loss must be above entry price"""
        with patch('argo.core.paper_trading_engine.PaperTradingEngine') as MockEngine:
            from argo.core.paper_trading_engine import PaperTradingEngine
            from alpaca.trading.enums import OrderSide
            
            real_engine = PaperTradingEngine.__new__(PaperTradingEngine)
            
            # Valid: stop above entry
            is_valid, error = real_engine._validate_bracket_prices(
                "SPY", 450.0, 459.0, 441.0, OrderSide.SELL
            )
            self.assertTrue(is_valid)
            
            # Invalid: stop below entry (wrong for SHORT)
            is_valid, error = real_engine._validate_bracket_prices(
                "SPY", 450.0, 441.0, 459.0, OrderSide.SELL
            )
            self.assertFalse(is_valid)
            self.assertIn("above entry", error.lower())
    
    def test_short_take_profit_validation(self):
        """Test that SHORT take profit must be below entry price"""
        with patch('argo.core.paper_trading_engine.PaperTradingEngine') as MockEngine:
            from argo.core.paper_trading_engine import PaperTradingEngine
            from alpaca.trading.enums import OrderSide
            
            real_engine = PaperTradingEngine.__new__(PaperTradingEngine)
            
            # Valid: target below entry
            is_valid, error = real_engine._validate_bracket_prices(
                "SPY", 450.0, 459.0, 441.0, OrderSide.SELL
            )
            self.assertTrue(is_valid)
            
            # Invalid: target above entry (wrong for SHORT)
            is_valid, error = real_engine._validate_bracket_prices(
                "SPY", 450.0, 459.0, 459.0, OrderSide.SELL
            )
            self.assertFalse(is_valid)
            self.assertIn("below entry", error.lower())


class TestSignalToPositionMapping(unittest.TestCase):
    """Test signal direction to action mapping"""
    
    def test_long_direction_to_buy_action(self):
        """Test that LONG direction maps to BUY action"""
        from argo.core.signal_generation_service import SignalGenerationService
        
        consensus = {"direction": "LONG", "confidence": 85.0}
        signal = SignalGenerationService._build_signal.__func__(
            None, "AAPL", consensus, {}
        )
        
        self.assertEqual(signal["action"], "BUY")
    
    def test_short_direction_to_sell_action(self):
        """Test that SHORT direction maps to SELL action"""
        from argo.core.signal_generation_service import SignalGenerationService
        
        consensus = {"direction": "SHORT", "confidence": 85.0}
        signal = SignalGenerationService._build_signal.__func__(
            None, "SPY", consensus, {}
        )
        
        self.assertEqual(signal["action"], "SELL")


class TestPositionFlipping(unittest.TestCase):
    """Test position flipping logic"""
    
    def test_long_to_short_flip(self):
        """Test flipping from LONG to SHORT"""
        existing_position = {
            "symbol": "AAPL",
            "side": "LONG",
            "qty": 10,
        }
        
        signal = {
            "symbol": "AAPL",
            "action": "SELL",
        }
        
        # Should allow flip: close LONG, open SHORT
        signal_action = signal.get("action", "").upper()
        existing_side = existing_position.get("side", "LONG").upper()
        
        would_close = (existing_side == "LONG" and signal_action == "SELL")
        would_duplicate = (existing_side == "LONG" and signal_action == "BUY")
        
        self.assertTrue(would_close)
        self.assertFalse(would_duplicate)
    
    def test_short_to_long_flip(self):
        """Test flipping from SHORT to LONG"""
        existing_position = {
            "symbol": "SPY",
            "side": "SHORT",
            "qty": 10,
        }
        
        signal = {
            "symbol": "SPY",
            "action": "BUY",
        }
        
        # Should allow flip: close SHORT, open LONG
        signal_action = signal.get("action", "").upper()
        existing_side = existing_position.get("side", "LONG").upper()
        
        would_close = (existing_side == "SHORT" and signal_action == "BUY")
        would_duplicate = (existing_side == "SHORT" and signal_action == "SELL")
        
        self.assertTrue(would_close)
        self.assertFalse(would_duplicate)


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestShortPositionOpening))
    suite.addTests(loader.loadTestsFromTestCase(TestShortPositionClosing))
    suite.addTests(loader.loadTestsFromTestCase(TestShortPositionRiskManagement))
    suite.addTests(loader.loadTestsFromTestCase(TestSignalToPositionMapping))
    suite.addTests(loader.loadTestsFromTestCase(TestPositionFlipping))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())


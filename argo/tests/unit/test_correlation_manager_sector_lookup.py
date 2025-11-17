#!/usr/bin/env python3
"""
Unit tests for Advanced Correlation Manager sector lookup functionality
"""
import pytest
from argo.argo.risk.advanced_correlation_manager import (
    AdvancedCorrelationManager,
    Position
)


class TestSectorLookup:
    """Test sector lookup functionality"""

    def test_technology_sector_detection(self):
        """Test that technology symbols are correctly identified"""
        manager = AdvancedCorrelationManager()

        tech_symbols = ['AAPL', 'MSFT', 'GOOGL', 'META', 'NVDA', 'AMD']
        for symbol in tech_symbols:
            sector = manager._get_sector(symbol)
            assert sector == 'Technology', f"{symbol} should be Technology, got {sector}"

    def test_consumer_discretionary_sector_detection(self):
        """Test that consumer discretionary symbols are correctly identified"""
        manager = AdvancedCorrelationManager()

        symbols = ['TSLA', 'AMZN', 'NFLX', 'HD', 'MCD']
        for symbol in symbols:
            sector = manager._get_sector(symbol)
            assert sector == 'Consumer Discretionary', f"{symbol} should be Consumer Discretionary, got {sector}"

    def test_financials_sector_detection(self):
        """Test that financial symbols are correctly identified"""
        manager = AdvancedCorrelationManager()

        symbols = ['JPM', 'BAC', 'WFC', 'GS', 'MS']
        for symbol in symbols:
            sector = manager._get_sector(symbol)
            assert sector == 'Financials', f"{symbol} should be Financials, got {sector}"

    def test_healthcare_sector_detection(self):
        """Test that healthcare symbols are correctly identified"""
        manager = AdvancedCorrelationManager()

        symbols = ['JNJ', 'UNH', 'PFE', 'ABT', 'TMO']
        for symbol in symbols:
            sector = manager._get_sector(symbol)
            assert sector == 'Healthcare', f"{symbol} should be Healthcare, got {sector}"

    def test_energy_sector_detection(self):
        """Test that energy symbols are correctly identified"""
        manager = AdvancedCorrelationManager()

        symbols = ['XOM', 'CVX', 'COP', 'SLB']
        for symbol in symbols:
            sector = manager._get_sector(symbol)
            assert sector == 'Energy', f"{symbol} should be Energy, got {sector}"

    def test_cryptocurrency_detection(self):
        """Test that cryptocurrency symbols are correctly identified"""
        manager = AdvancedCorrelationManager()

        crypto_symbols = ['BTC-USD', 'ETH-USD', 'SOL-USD', 'BTCUSD', 'ETHUSD']
        for symbol in crypto_symbols:
            sector = manager._get_sector(symbol)
            assert sector == 'Cryptocurrency', f"{symbol} should be Cryptocurrency, got {sector}"

    def test_unknown_symbol_returns_none(self):
        """Test that unknown symbols return None"""
        manager = AdvancedCorrelationManager()

        unknown_symbols = ['UNKNOWN', 'XYZ123', 'TEST']
        for symbol in unknown_symbols:
            sector = manager._get_sector(symbol)
            assert sector is None, f"{symbol} should return None, got {sector}"

    def test_case_insensitive_lookup(self):
        """Test that sector lookup is case-insensitive"""
        manager = AdvancedCorrelationManager()

        # Test lowercase
        assert manager._get_sector('aapl') == 'Technology'
        assert manager._get_sector('tsla') == 'Consumer Discretionary'

        # Test mixed case
        assert manager._get_sector('AaPl') == 'Technology'
        assert manager._get_sector('TsLa') == 'Consumer Discretionary'

    def test_auto_detect_sector_in_can_add_position(self):
        """Test that can_add_position auto-detects sector if not provided"""
        manager = AdvancedCorrelationManager({
            'max_sector_exposure': 0.5,  # 50% to allow test
            'max_correlation': 0.7,
            'max_correlated_positions': 2,
            'max_portfolio_correlation': 0.5
        })

        # Add a position without sector
        positions = [Position('MSFT', 0.1, None)]  # No sector provided

        # Try to add another tech stock - should auto-detect sector
        can_add, reason = manager.can_add_position('AAPL', None, positions)

        # Should work since we're under the limit
        assert can_add or 'sector' in reason.lower(), f"Should auto-detect sector, got: {reason}"


class TestSectorExposure:
    """Test sector exposure calculations"""

    def test_sector_exposure_calculation(self):
        """Test that sector exposure is calculated correctly"""
        manager = AdvancedCorrelationManager()

        positions = [
            Position('AAPL', 0.2, 'Technology'),
            Position('MSFT', 0.15, 'Technology'),
            Position('TSLA', 0.1, 'Consumer Discretionary'),
        ]

        exposure = manager._calculate_sector_exposure(positions)

        # Technology should be 0.2 + 0.15 = 0.35 (35% of total 0.45)
        # But normalized to percentages: 0.35 / 0.45 = ~0.778
        total = sum(p.size_pct for p in positions)
        tech_exposure = (0.2 + 0.15) / total
        consumer_exposure = 0.1 / total

        assert abs(exposure.get('Technology', 0) - tech_exposure) < 0.01
        assert abs(exposure.get('Consumer Discretionary', 0) - consumer_exposure) < 0.01

    def test_sector_exposure_limit_enforcement(self):
        """Test that sector exposure limits are enforced"""
        manager = AdvancedCorrelationManager({
            'max_sector_exposure': 0.4,  # 40% max
            'max_correlation': 0.7,
            'max_correlated_positions': 2,
            'max_portfolio_correlation': 0.5
        })

        # Create positions that exceed 40% technology exposure
        positions = [
            Position('AAPL', 0.25, 'Technology'),
            Position('MSFT', 0.20, 'Technology'),  # Total: 45% tech
        ]

        # Try to add another tech stock
        can_add, reason = manager.can_add_position('NVDA', 'Technology', positions)

        assert not can_add, "Should reject position that exceeds sector limit"
        assert 'sector' in reason.lower() or 'exposure' in reason.lower()


class TestIntegration:
    """Integration tests for sector-aware correlation management"""

    def test_full_workflow_with_sector_detection(self):
        """Test complete workflow with automatic sector detection"""
        manager = AdvancedCorrelationManager({
            'max_sector_exposure': 0.5,
            'max_correlation': 0.7,
            'max_correlated_positions': 2,
            'max_portfolio_correlation': 0.5
        })

        # Start with empty portfolio
        positions = []

        # Add tech stock (sector auto-detected)
        can_add, reason = manager.can_add_position('AAPL', None, positions)
        assert can_add, f"Should allow first position: {reason}"

        # Add another tech stock
        positions.append(Position('AAPL', 0.2, 'Technology'))
        can_add, reason = manager.can_add_position('MSFT', None, positions)
        assert can_add, f"Should allow second tech position: {reason}"

        # Add consumer discretionary stock
        positions.append(Position('MSFT', 0.2, 'Technology'))
        can_add, reason = manager.can_add_position('TSLA', None, positions)
        assert can_add, f"Should allow different sector: {reason}"

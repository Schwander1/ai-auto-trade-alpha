#!/usr/bin/env python3
"""
Advanced Correlation Manager
Dynamic correlation management with rolling windows and sector analysis.
Prevents overexposure to correlated movements.
"""
import logging
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import numpy as np

logger = logging.getLogger(__name__)

@dataclass
class Position:
    """Position representation"""
    symbol: str
    size_pct: float
    sector: Optional[str] = None

class AdvancedCorrelationManager:
    """
    Dynamic correlation management with rolling windows and sector analysis.
    Prevents overexposure to correlated movements.
    """
    def __init__(self, config: Optional[Dict] = None):
        if config is None:
            config = {}

        self.config = config
        self.correlation_matrix: Dict[Tuple[str, str], float] = {}
        self.sector_exposure: Dict[str, float] = {}
        self.lookback_period = config.get("lookback_period", 20)  # days
        self.max_sector_exposure = config.get("max_sector_exposure", 0.4)  # 40%
        self.max_correlation = config.get("max_correlation", 0.7)  # 70%
        self.max_correlated_positions = config.get("max_correlated_positions", 2)
        self.max_portfolio_correlation = config.get("max_portfolio_correlation", 0.5)  # 50%

    async def update_correlations(self, positions: List[Position], price_data: Dict[str, List[float]]):
        """Update correlation matrix using recent price data"""
        symbols = [p.symbol for p in positions]

        # Calculate pairwise correlations
        for i, sym1 in enumerate(symbols):
            if sym1 not in price_data:
                continue
            for sym2 in symbols[i+1:]:
                if sym2 not in price_data:
                    continue

                try:
                    # Calculate correlation
                    prices1 = np.array(price_data[sym1])
                    prices2 = np.array(price_data[sym2])

                    if len(prices1) == len(prices2) and len(prices1) > 1:
                        # Calculate returns
                        returns1 = np.diff(prices1) / prices1[:-1]
                        returns2 = np.diff(prices2) / prices2[:-1]

                        # Calculate correlation
                        if len(returns1) > 1 and np.std(returns1) > 0 and np.std(returns2) > 0:
                            correlation = np.corrcoef(returns1, returns2)[0, 1]
                            self.correlation_matrix[(sym1, sym2)] = correlation
                            self.correlation_matrix[(sym2, sym1)] = correlation  # Symmetric
                except Exception as e:
                    logger.warning(f"Error calculating correlation between {sym1} and {sym2}: {e}")

    def can_add_position(self, new_symbol: str, new_sector: Optional[str], current_positions: List[Position]) -> Tuple[bool, str]:
        """
        Determine if adding a new position would violate correlation limits.
        Returns (can_add, reason) tuple.
        """
        # Auto-detect sector if not provided
        if not new_sector:
            new_sector = self._get_sector(new_symbol)

        # Check sector exposure
        if new_sector:
            sector_exposure = self._calculate_sector_exposure(current_positions)
            current_sector_exposure = sector_exposure.get(new_sector, 0.0)

            if current_sector_exposure >= self.max_sector_exposure:
                return False, f"Sector exposure limit reached for {new_sector} ({current_sector_exposure:.1%} >= {self.max_sector_exposure:.1%})"

        # Check pairwise correlations
        for position in current_positions:
            correlation = self.correlation_matrix.get((new_symbol, position.symbol), 0)
            if abs(correlation) > self.max_correlation:
                current_correlated = self._count_correlated_positions(position.symbol, current_positions)
                if current_correlated >= self.max_correlated_positions:
                    return False, f"High correlation with {position.symbol} (r={correlation:.2f}), max correlated positions reached"

        # Check portfolio-wide correlation
        portfolio_correlation = self._calculate_portfolio_correlation(current_positions + [Position(new_symbol, 0.0, new_sector)])
        if portfolio_correlation > self.max_portfolio_correlation:
            return False, f"Portfolio correlation too high ({portfolio_correlation:.2f} > {self.max_portfolio_correlation:.2f})"

        return True, "OK"

    def get_risk_adjusted_size(self, symbol: str, base_size: float, positions: List[Position]) -> float:
        """
        Calculate risk-adjusted position size based on correlations.
        Reduce size for highly correlated positions.
        """
        max_correlation = 0.0
        for position in positions:
            correlation = abs(self.correlation_matrix.get((symbol, position.symbol), 0))
            max_correlation = max(max_correlation, correlation)

        # Reduce position size based on maximum correlation
        # High correlation (>0.7) = 50% size reduction
        # Moderate correlation (0.4-0.7) = 25% size reduction
        # Low correlation (<0.4) = no reduction
        if max_correlation > 0.7:
            adjustment_factor = 0.5
        elif max_correlation > 0.4:
            adjustment_factor = 0.75
        else:
            adjustment_factor = 1.0

        return base_size * adjustment_factor

    def _calculate_sector_exposure(self, positions: List[Position]) -> Dict[str, float]:
        """Calculate exposure by sector"""
        sector_exposure = {}
        total_size = sum(p.size_pct for p in positions)

        if total_size == 0:
            return sector_exposure

        for position in positions:
            if position.sector:
                sector_exposure[position.sector] = sector_exposure.get(position.sector, 0.0) + position.size_pct

        # Normalize to percentages
        return {sector: exposure / total_size for sector, exposure in sector_exposure.items()}

    def _count_correlated_positions(self, symbol: str, positions: List[Position]) -> int:
        """Count positions highly correlated with given symbol"""
        count = 0
        for position in positions:
            if position.symbol != symbol:
                correlation = abs(self.correlation_matrix.get((symbol, position.symbol), 0))
                if correlation > self.max_correlation:
                    count += 1
        return count

    def _calculate_portfolio_correlation(self, positions: List[Position]) -> float:
        """Calculate portfolio-wide average correlation"""
        if len(positions) < 2:
            return 0.0

        correlations = []
        for i, pos1 in enumerate(positions):
            for pos2 in positions[i+1:]:
                corr = abs(self.correlation_matrix.get((pos1.symbol, pos2.symbol), 0))
                correlations.append(corr)

        return np.mean(correlations) if correlations else 0.0

    def _get_sector(self, symbol: str) -> Optional[str]:
        """
        Get sector for a symbol.
        Uses a mapping of common symbols to their sectors.
        Can be extended to use external APIs or databases for comprehensive coverage.
        """
        # Sector mapping for common symbols
        # Technology
        tech_symbols = {
            'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'META', 'NVDA', 'AMD', 'INTC', 'QCOM',
            'AVGO', 'CRM', 'ORCL', 'ADBE', 'CSCO', 'TXN', 'AMAT', 'LRCX', 'KLAC'
        }
        # Consumer Discretionary
        consumer_discretionary = {
            'TSLA', 'AMZN', 'NFLX', 'HD', 'MCD', 'SBUX', 'NKE', 'LOW', 'TJX',
            'BKNG', 'CMG', 'YUM', 'TGT', 'BBY', 'DKS'
        }
        # Financials
        financials = {
            'JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'BLK', 'SCHW', 'AXP', 'COF',
            'USB', 'PNC', 'TFC', 'BK', 'STT'
        }
        # Healthcare
        healthcare = {
            'JNJ', 'UNH', 'PFE', 'ABT', 'TMO', 'ABBV', 'MRK', 'BMY', 'AMGN',
            'GILD', 'CVS', 'CI', 'HUM', 'ELV', 'DHR'
        }
        # Communication Services
        communication = {
            'VZ', 'T', 'CMCSA', 'DIS', 'NFLX', 'GOOGL', 'GOOG', 'META'
        }
        # Industrials
        industrials = {
            'BA', 'CAT', 'GE', 'HON', 'UPS', 'RTX', 'LMT', 'NOC', 'GD', 'DE',
            'EMR', 'ITW', 'ETN', 'PH', 'CMI'
        }
        # Consumer Staples
        consumer_staples = {
            'PG', 'KO', 'PEP', 'WMT', 'COST', 'CL', 'KMB', 'CHD', 'CLX', 'GIS'
        }
        # Energy
        energy = {
            'XOM', 'CVX', 'COP', 'SLB', 'EOG', 'MPC', 'PSX', 'VLO', 'HAL', 'OXY'
        }
        # Utilities
        utilities = {
            'NEE', 'DUK', 'SO', 'D', 'AEP', 'EXC', 'SRE', 'XEL', 'WEC', 'ES'
        }
        # Real Estate
        real_estate = {
            'AMT', 'PLD', 'EQIX', 'PSA', 'WELL', 'SPG', 'O', 'DLR', 'VICI', 'CBRE'
        }
        # Materials
        materials = {
            'LIN', 'APD', 'SHW', 'ECL', 'DD', 'PPG', 'NEM', 'FCX', 'VALE', 'NUE'
        }

        # Check symbol against sector mappings
        symbol_upper = symbol.upper()

        if symbol_upper in tech_symbols:
            return 'Technology'
        elif symbol_upper in consumer_discretionary:
            return 'Consumer Discretionary'
        elif symbol_upper in financials:
            return 'Financials'
        elif symbol_upper in healthcare:
            return 'Healthcare'
        elif symbol_upper in communication:
            return 'Communication Services'
        elif symbol_upper in industrials:
            return 'Industrials'
        elif symbol_upper in consumer_staples:
            return 'Consumer Staples'
        elif symbol_upper in energy:
            return 'Energy'
        elif symbol_upper in utilities:
            return 'Utilities'
        elif symbol_upper in real_estate:
            return 'Real Estate'
        elif symbol_upper in materials:
            return 'Materials'
        elif symbol_upper.endswith('-USD') or symbol_upper.startswith('BTC') or symbol_upper.startswith('ETH'):
            return 'Cryptocurrency'
        else:
            # Unknown symbol - return None
            logger.debug(f"Unknown sector for symbol: {symbol}")
            return None

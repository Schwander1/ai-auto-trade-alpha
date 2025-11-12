"""Mean Reversion Strategy - Buy Low, Sell High"""
import numpy as np
from argo.strategies.base_strategy import BaseStrategy, SignalOutput
from datetime import datetime

class MeanReversionStrategy(BaseStrategy):
    def __init__(self):
        super().__init__("MeanReversion")
        self.lookback_period = 20
        self.std_multiplier = 2.0  # Bollinger Bands std dev
    
    async def generate_signal(self, symbol: str, market_data: dict):
        """Generate mean reversion signal using Bollinger Bands"""
        try:
            prices = np.array(market_data.get('close_prices', []))
            
            if len(prices) < self.lookback_period:
                return None
            
            # Calculate Bollinger Bands
            sma = np.mean(prices[-self.lookback_period:])
            std = np.std(prices[-self.lookback_period:])
            upper_band = sma + (self.std_multiplier * std)
            lower_band = sma - (self.std_multiplier * std)
            
            current_price = prices[-1]
            
            # Calculate distance from mean (normalized)
            distance_from_mean = abs(current_price - sma) / sma
            
            # Oversold - Buy signal
            if current_price < lower_band:
                confidence = min(0.75 + (distance_from_mean * 10), 0.95)
                
                return SignalOutput(
                    symbol=symbol,
                    action='BUY',
                    confidence=confidence,
                    entry_price=current_price,
                    target_price=sma,  # Target is mean reversion
                    stop_loss=current_price * 0.96,
                    position_size=0.08,
                    reasoning=f"Price ${current_price:.2f} below lower BB ${lower_band:.2f}, expect reversion to mean ${sma:.2f}",
                    strategy_name=self.name,
                    timestamp=datetime.utcnow()
                )
            
            # Overbought - Sell signal
            elif current_price > upper_band:
                confidence = min(0.75 + (distance_from_mean * 10), 0.95)
                
                return SignalOutput(
                    symbol=symbol,
                    action='SELL',
                    confidence=confidence,
                    entry_price=current_price,
                    target_price=sma,
                    stop_loss=current_price * 1.04,
                    position_size=0.08,
                    reasoning=f"Price ${current_price:.2f} above upper BB ${upper_band:.2f}, expect reversion to mean ${sma:.2f}",
                    strategy_name=self.name,
                    timestamp=datetime.utcnow()
                )
            
            return None
            
        except Exception as e:
            print(f"Mean reversion error for {symbol}: {e}")
            return None
    
    def get_required_data(self) -> list[str]:
        return ['close_prices']

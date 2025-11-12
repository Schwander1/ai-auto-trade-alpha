import numpy as np
from argo.strategies.base_strategy import BaseStrategy, SignalOutput
from datetime import datetime

class MomentumStrategy(BaseStrategy):
    def __init__(self):
        super().__init__("Momentum")
        self.lookback = 20
        self.threshold = 0.015
    
    async def generate_signal(self, symbol: str, market_data: dict):
        try:
            prices = np.array(market_data.get('close_prices', []))
            if len(prices) < self.lookback:
                return None
            
            momentum = (prices[-1] - prices[-self.lookback]) / prices[-self.lookback]
            rsi = self._calc_rsi(prices)
            
            if momentum > self.threshold and rsi < 70:
                conf = min(abs(momentum) * 20 + 0.70, 0.98)
                return SignalOutput(symbol, 'BUY', conf, prices[-1], prices[-1]*1.05, prices[-1]*0.97, 0.10, f"Momentum {momentum:.2%}, RSI {rsi:.0f}", self.name, datetime.utcnow())
            elif momentum < -self.threshold and rsi > 30:
                conf = min(abs(momentum) * 20 + 0.70, 0.98)
                return SignalOutput(symbol, 'SELL', conf, prices[-1], prices[-1]*0.95, prices[-1]*1.03, 0.10, f"Momentum {momentum:.2%}, RSI {rsi:.0f}", self.name, datetime.utcnow())
            return None
        except:
            return None
    
    def get_required_data(self):
        return ['close_prices', 'volume']
    
    def _calc_rsi(self, prices, period=14):
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        if avg_loss == 0:
            return 100
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

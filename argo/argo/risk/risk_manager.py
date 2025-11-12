import numpy as np
from typing import Dict, Tuple
from dataclasses import dataclass

@dataclass
class RiskParameters:
    max_position_size: float = 0.15
    max_portfolio_risk: float = 0.20
    max_drawdown: float = 0.15
    win_rate_threshold: float = 0.60

class RiskManager:
    def __init__(self):
        self.params = RiskParameters()
        self.positions = {}
        self.history = []
        self.peak = 100000
        self.current = 100000
    
    def calc_position_size(self, conf: float, wr: float, aw: float, al: float) -> float:
        if al == 0:
            return self.params.max_position_size
        b = aw / al
        kelly = ((wr * b) - (1 - wr)) / b
        return min(kelly * 0.5 * conf, self.params.max_position_size)
    
    def validate(self, sig: Dict, port: Dict) -> Tuple[bool, str]:
        if sig['confidence'] < 65:
            return False, "Low confidence"
        dd = (self.peak - self.current) / self.peak
        if dd > self.params.max_drawdown:
            return False, "Max drawdown"
        return True, "OK"

risk_manager = RiskManager()

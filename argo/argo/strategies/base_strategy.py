from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import hashlib
import json

@dataclass
class SignalOutput:
    symbol: str
    action: str
    confidence: float
    entry_price: float
    target_price: Optional[float]
    stop_loss: Optional[float]
    position_size: float
    reasoning: str
    strategy_name: str
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        data = {
            'symbol': self.symbol,
            'action': self.action,
            'confidence': round(self.confidence, 4),
            'entry_price': self.entry_price,
            'target_price': self.target_price,
            'stop_loss': self.stop_loss,
            'position_size': self.position_size,
            'reasoning': self.reasoning,
            'strategy': self.strategy_name,
            'timestamp': self.timestamp.isoformat()
        }
        data_str = json.dumps(data, sort_keys=True)
        data['sha256'] = hashlib.sha256(data_str.encode()).hexdigest()
        return data

class BaseStrategy(ABC):
    def __init__(self, name: str):
        self.name = name
        self.signals_generated = 0
        self.win_rate = 0.0
    
    @abstractmethod
    async def generate_signal(self, symbol: str, market_data: Dict) -> Optional[SignalOutput]:
        pass
    
    @abstractmethod
    def get_required_data(self) -> list[str]:
        pass

import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class TradeLogger:
    def __init__(self, log_file='monitoring/trades.jsonl'):
        self.log_file = log_file

    def log_trade(self, symbol, action, quantity, price, confidence, reason):
        trade = {
            'timestamp': datetime.now().isoformat(),
            'symbol': symbol,
            'action': action,
            'quantity': quantity,
            'price': price,
            'confidence': confidence,
            'reason': reason,
        }
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(trade) + '\n')
        logger.info(f"TRADE: {symbol} {action} {quantity}x @ ${price}")
        return trade

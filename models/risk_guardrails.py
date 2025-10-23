import logging
logger = logging.getLogger(name)

class RiskGuardrails:
def init(self):
self.daily_pnl = 0
self.trades_today = 0
self.per_symbol_loss = {}

    # LIMITS
    self.MAX_DAILY_LOSS = -500
    self.MAX_PER_SYMBOL_LOSS = -100
    self.MAX_TRADES_PER_DAY = 50
    self.MIN_CONFIDENCE = 0.52

def check_can_trade(self, symbol, confidence):
    if confidence < self.MIN_CONFIDENCE:
        logger.warning(f"BLOCKED: {symbol} confidence {confidence:.2f} < {self.MIN_CONFIDENCE}")
        return False

    if self.trades_today >= self.MAX_TRADES_PER_DAY:
        logger.warning(f"BLOCKED: {self.trades_today} trades >= {self.MAX_TRADES_PER_DAY} limit")
        return False

    if self.daily_pnl < self.MAX_DAILY_LOSS:
        logger.error(f"🚨 CIRCUIT BREAKER: Daily loss {self.daily_pnl} < {self.MAX_DAILY_LOSS}. STOP TRADING")
        return False

    if symbol in self.per_symbol_loss and self.per_symbol_loss[symbol] < self.MAX_PER_SYMBOL_LOSS:
        logger.warning(f"BLOCKED: {symbol} loss {self.per_symbol_loss[symbol]} < {self.MAX_PER_SYMBOL_LOSS}")
        return False

    return True

def record_trade(self, symbol, pnl):
    self.daily_pnl += pnl
    self.trades_today += 1
    self.per_symbol_loss[symbol] = self.per_symbol_loss.get(symbol, 0) + pnl
    logger.info(f"Trade: {symbol} PnL={pnl:.2f} | Daily={self.daily_pnl:.2f} | Trades={self.trades_today}")

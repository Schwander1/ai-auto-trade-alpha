import logging
logger = logging.getLogger(__name__)

class AlertSystem:
    def alert_circuit_breaker(self, daily_loss):
        msg = f"🚨 CIRCUIT BREAKER: Daily loss ${daily_loss}"
        logger.error(msg)
        return msg

import json
from datetime import datetime

class MetricsTracker:
    def __init__(self):
        self.daily_stats = {
            'date': datetime.now().date().isoformat(),
            'trades': 0,
            'wins': 0,
            'losses': 0,
            'total_pnl': 0,
        }

    def record_metrics(self, trades, pnl):
        self.daily_stats['trades'] = len(trades)
        self.daily_stats['wins'] = len([t for t in trades if t.get('pnl', 0) > 0])
        self.daily_stats['losses'] = len([t for t in trades if t.get('pnl', 0) < 0])
        self.daily_stats['total_pnl'] = pnl
        return self.daily_stats

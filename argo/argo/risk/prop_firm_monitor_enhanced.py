#!/usr/bin/env python3
"""
Enhanced Prop Firm Monitoring with Real-Time Alerts
Provides enhanced monitoring, alerting, and dashboard capabilities for prop firm trading
"""
import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class Alert:
    """Alert data structure"""
    level: str  # 'info', 'warning', 'critical', 'breach'
    message: str
    timestamp: datetime
    metrics: Dict
    action_required: bool = False

class PropFirmMonitorEnhanced:
    """Enhanced prop firm monitoring with alerts and dashboard"""

    def __init__(self, risk_monitor):
        self.risk_monitor = risk_monitor
        self.alerts: List[Alert] = []
        self.alert_handlers: List[callable] = []
        self.monitoring_active = False

    async def start_monitoring(self):
        """Start enhanced monitoring"""
        self.monitoring_active = True
        logger.info("🚨 Enhanced prop firm monitoring started")

        # Start monitoring loop
        asyncio.create_task(self._monitoring_loop())

    async def _monitoring_loop(self):
        """Enhanced monitoring loop with alerting"""
        while self.monitoring_active:
            try:
                stats = self.risk_monitor.get_monitoring_stats()

                # Check for alerts
                alerts = self._check_alerts(stats)

                # Process alerts
                for alert in alerts:
                    await self._process_alert(alert)

                # Log status every minute
                await asyncio.sleep(60)

            except Exception as e:
                logger.error(f"Error in enhanced monitoring loop: {e}")
                await asyncio.sleep(60)

    def _check_alerts(self, stats: Dict) -> List[Alert]:
        """Check for conditions that require alerts"""
        alerts = []
        current_time = datetime.now()

        # Check drawdown
        drawdown = stats.get('current_drawdown', 0)
        max_drawdown = self.risk_monitor.max_drawdown

        if drawdown >= max_drawdown:
            alerts.append(Alert(
                level='breach',
                message=f'Drawdown breach: {drawdown:.2f}% >= {max_drawdown}%',
                timestamp=current_time,
                metrics={'drawdown': drawdown, 'limit': max_drawdown},
                action_required=True
            ))
        elif drawdown >= max_drawdown * 0.9:
            alerts.append(Alert(
                level='critical',
                message=f'Drawdown critical: {drawdown:.2f}% (90% of limit)',
                timestamp=current_time,
                metrics={'drawdown': drawdown, 'limit': max_drawdown},
                action_required=True
            ))
        elif drawdown >= max_drawdown * 0.7:
            alerts.append(Alert(
                level='warning',
                message=f'Drawdown warning: {drawdown:.2f}% (70% of limit)',
                timestamp=current_time,
                metrics={'drawdown': drawdown, 'limit': max_drawdown},
                action_required=False
            ))

        # Check daily P&L
        daily_pnl = stats.get('daily_pnl_pct', 0)
        daily_limit = -self.risk_monitor.daily_loss_limit

        if daily_pnl <= daily_limit:
            alerts.append(Alert(
                level='breach',
                message=f'Daily loss breach: {daily_pnl:.2f}% <= {daily_limit}%',
                timestamp=current_time,
                metrics={'daily_pnl': daily_pnl, 'limit': daily_limit},
                action_required=True
            ))
        elif daily_pnl <= daily_limit * 0.9:
            alerts.append(Alert(
                level='critical',
                message=f'Daily loss critical: {daily_pnl:.2f}% (90% of limit)',
                timestamp=current_time,
                metrics={'daily_pnl': daily_pnl, 'limit': daily_limit},
                action_required=True
            ))
        elif daily_pnl <= daily_limit * 0.7:
            alerts.append(Alert(
                level='warning',
                message=f'Daily loss warning: {daily_pnl:.2f}% (70% of limit)',
                timestamp=current_time,
                metrics={'daily_pnl': daily_pnl, 'limit': daily_limit},
                action_required=False
            ))

        # Check position count
        positions = stats.get('open_positions', 0)
        max_positions = 3  # Prop firm limit

        if positions >= max_positions:
            alerts.append(Alert(
                level='info',
                message=f'Maximum positions reached: {positions}/{max_positions}',
                timestamp=current_time,
                metrics={'positions': positions, 'max': max_positions},
                action_required=False
            ))

        # Check correlation
        correlation = stats.get('portfolio_correlation', 0)
        if correlation > 0.7:
            alerts.append(Alert(
                level='warning',
                message=f'High portfolio correlation: {correlation:.2f}',
                timestamp=current_time,
                metrics={'correlation': correlation},
                action_required=False
            ))

        return alerts

    async def _process_alert(self, alert: Alert):
        """Process an alert"""
        # Add to alerts list
        self.alerts.append(alert)

        # Keep only last 100 alerts
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]

        # Log alert
        log_level = {
            'info': logger.info,
            'warning': logger.warning,
            'critical': logger.error,
            'breach': logger.critical
        }.get(alert.level, logger.info)

        log_level(f"🚨 [{alert.level.upper()}] {alert.message}")

        # Call alert handlers
        for handler in self.alert_handlers:
            try:
                await handler(alert)
            except Exception as e:
                logger.error(f"Error in alert handler: {e}")

        # Save alert to file if critical or breach
        if alert.level in ['critical', 'breach']:
            self._save_alert(alert)

    def _save_alert(self, alert: Alert):
        """Save critical alert to file"""
        alerts_dir = Path(__file__).parent.parent.parent / "logs" / "alerts"
        alerts_dir.mkdir(parents=True, exist_ok=True)

        alert_file = alerts_dir / f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        alert_data = asdict(alert)
        alert_data['timestamp'] = alert.timestamp.isoformat()

        with open(alert_file, 'w') as f:
            json.dump(alert_data, f, indent=2)

    def register_alert_handler(self, handler: callable):
        """Register an alert handler function"""
        self.alert_handlers.append(handler)

    def get_dashboard_data(self) -> Dict:
        """Get dashboard data for display"""
        stats = self.risk_monitor.get_monitoring_stats()

        # Get recent alerts
        recent_alerts = [
            {
                'level': alert.level,
                'message': alert.message,
                'timestamp': alert.timestamp.isoformat(),
                'action_required': alert.action_required
            }
            for alert in self.alerts[-10:]  # Last 10 alerts
        ]

        return {
            'timestamp': datetime.now().isoformat(),
            'stats': stats,
            'recent_alerts': recent_alerts,
            'alert_counts': {
                'total': len(self.alerts),
                'breach': len([a for a in self.alerts if a.level == 'breach']),
                'critical': len([a for a in self.alerts if a.level == 'critical']),
                'warning': len([a for a in self.alerts if a.level == 'warning']),
                'info': len([a for a in self.alerts if a.level == 'info'])
            }
        }

    def get_status_summary(self) -> str:
        """Get human-readable status summary"""
        stats = self.risk_monitor.get_monitoring_stats()

        drawdown = stats.get('current_drawdown', 0)
        daily_pnl = stats.get('daily_pnl_pct', 0)
        positions = stats.get('open_positions', 0)
        risk_level = stats.get('current_risk_level', 'normal')

        summary = f"""
📊 PROP FIRM STATUS SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Risk Level: {risk_level.upper()}
Drawdown: {drawdown:.2f}% / {self.risk_monitor.max_drawdown}% limit
Daily P&L: {daily_pnl:+.2f}% / {self.risk_monitor.daily_loss_limit}% limit
Open Positions: {positions} / 3 max
Account Equity: ${stats.get('account_equity', 0):,.2f}
Peak Equity: ${stats.get('peak_equity', 0):,.2f}
Trading Halted: {'YES' if stats.get('trading_halted', False) else 'NO'}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        return summary

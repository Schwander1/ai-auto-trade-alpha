#!/usr/bin/env python3
"""
Real-Time Prop Firm Risk Monitor
Provides continuous monitoring, alerts, and emergency shutdown
"""
import asyncio
import logging
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from typing import List, Callable, Optional, Dict
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class RiskLevel(Enum):
    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"
    BREACH = "breach"

@dataclass
class RiskMetrics:
    """Current risk metrics snapshot"""
    timestamp: datetime
    current_drawdown: float
    daily_pnl_pct: float
    open_positions: int
    correlated_positions: int
    largest_position_size: float
    portfolio_correlation: float
    risk_level: RiskLevel
    account_equity: float = 0.0
    peak_equity: float = 0.0

class PropFirmRiskMonitor:
    """
    Real-time monitoring system for prop firm compliance.
    Provides alerts, auto-shutdown, and detailed risk reporting.
    Conservative limits: 2.0% max drawdown (vs 2.5% limit), 4.5% daily loss (vs 5.0% limit)
    """
    def __init__(self, config: dict):
        self.config = config
        self.alert_handlers: List[Callable] = []
        self.metrics_history: List[RiskMetrics] = []
        self.monitoring_active = False
        self.breach_count = 0
        self.warning_count = 0
        self.critical_count = 0
        self.monitoring_task: Optional[asyncio.Task] = None
        
        # Risk thresholds (conservative: 2.0% vs 2.5% limit)
        self.max_drawdown = config.get("max_drawdown_pct", 2.0)
        self.daily_loss_limit = config.get("daily_loss_limit_pct", 4.5)
        self.initial_capital = config.get("initial_capital", 25000.0)
        self.peak_equity = self.initial_capital
        self.current_equity = self.initial_capital
        self.daily_start_equity = self.initial_capital
        self.last_reset_date = datetime.now().date()
        
        # Position tracking
        self.positions: Dict[str, Dict] = {}
        
    async def start_monitoring(self):
        """Start continuous monitoring loop"""
        if self.monitoring_active:
            logger.warning("⚠️  Monitoring already active")
            return
            
        self.monitoring_active = True
        logger.info("🚨 Prop Firm Risk Monitor started")
        
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        
    async def stop_monitoring(self):
        """Stop monitoring loop"""
        self.monitoring_active = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        logger.info("🛑 Prop Firm Risk Monitor stopped")
        
    async def _monitoring_loop(self):
        """Continuous monitoring loop"""
        while self.monitoring_active:
            try:
                # Reset daily metrics at start of new trading day
                current_date = datetime.now().date()
                if current_date > self.last_reset_date:
                    self.daily_start_equity = self.current_equity
                    self.last_reset_date = current_date
                    logger.info(f"📅 Daily reset: Starting equity = ${self.daily_start_equity:.2f}")
                
                metrics = await self._collect_metrics()
                risk_level = self._assess_risk_level(metrics)
                
                if risk_level != RiskLevel.NORMAL:
                    await self._handle_risk_event(metrics, risk_level)
                    
                self.metrics_history.append(metrics)
                
                # Keep only last 1000 metrics
                if len(self.metrics_history) > 1000:
                    self.metrics_history = self.metrics_history[-1000:]
                    
                await asyncio.sleep(5)  # Monitor every 5 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Error in risk monitoring loop: {e}")
                await asyncio.sleep(5)
                
    def _assess_risk_level(self, metrics: RiskMetrics) -> RiskLevel:
        """Assess current risk level based on metrics"""
        # Breach level: Hard limits exceeded
        if metrics.current_drawdown >= self.max_drawdown or metrics.daily_pnl_pct <= -self.daily_loss_limit:
            return RiskLevel.BREACH
            
        # Critical level: Approaching limits (90% of max)
        critical_drawdown = self.max_drawdown * 0.9
        critical_daily_loss = -self.daily_loss_limit * 0.9
        
        if metrics.current_drawdown >= critical_drawdown or metrics.daily_pnl_pct <= critical_daily_loss:
            return RiskLevel.CRITICAL
            
        # Warning level: Significant exposure (70% of max)
        warning_drawdown = self.max_drawdown * 0.7
        warning_daily_loss = -self.daily_loss_limit * 0.7
        
        if metrics.current_drawdown >= warning_drawdown or metrics.daily_pnl_pct <= warning_daily_loss:
            return RiskLevel.WARNING
            
        return RiskLevel.NORMAL
        
    async def _handle_risk_event(self, metrics: RiskMetrics, level: RiskLevel):
        """Handle risk events with appropriate actions"""
        if level == RiskLevel.BREACH:
            self.breach_count += 1
            await self._emergency_shutdown(metrics)
            logger.critical(f"🚨 BREACH: Emergency shutdown triggered. Metrics: {metrics}")
            
        elif level == RiskLevel.CRITICAL:
            self.critical_count += 1
            await self._reduce_risk_exposure(metrics)
            logger.error(f"⚠️  CRITICAL: Risk reduction initiated. Metrics: {metrics}")
            
        elif level == RiskLevel.WARNING:
            self.warning_count += 1
            await self._send_alerts(metrics, level)
            logger.warning(f"⚠️  WARNING: Risk level elevated. Metrics: {metrics}")
            
    async def _emergency_shutdown(self, metrics: RiskMetrics):
        """Emergency shutdown procedure"""
        logger.critical("🛑 EMERGENCY SHUTDOWN INITIATED")
        
        # 1. Stop all new orders immediately
        self.trading_halted = True
        self.halt_reason = f"Emergency shutdown: Drawdown={metrics.current_drawdown:.2f}%, Daily P&L={metrics.daily_pnl_pct:.2f}%"
        
        # 2. Close all open positions at market (if position_manager available)
        if hasattr(self, 'position_manager') and self.position_manager:
            try:
                await self.position_manager.close_all_positions(urgency="immediate")
                logger.critical("🛑 All positions closed")
            except Exception as e:
                logger.error(f"Error closing positions: {e}")
        
        # 3. Send critical alerts
        await self._send_critical_alert(metrics)
        
        # 4. Log detailed state
        self._log_shutdown_state(metrics)
        
        # 5. Disable monitoring (system is shut down)
        await self.stop_monitoring()
    
    def set_position_manager(self, position_manager):
        """Set position manager for emergency shutdown"""
        self.position_manager = position_manager
    
    def set_order_manager(self, order_manager):
        """Set order manager for halting trading"""
        self.order_manager = order_manager
        
    async def _reduce_risk_exposure(self, metrics: RiskMetrics):
        """Reduce risk exposure by closing risky positions"""
        logger.warning("📉 Reducing risk exposure...")
        
        # Close positions with highest risk (largest size or highest correlation)
        if hasattr(self, 'position_manager') and self.position_manager:
            try:
                # Sort positions by risk (size * correlation)
                risky_positions = []
                for symbol, pos_data in self.positions.items():
                    size_pct = pos_data.get('size_pct', 0.0)
                    # Calculate risk score
                    risk_score = size_pct * (1.0 + metrics.portfolio_correlation)
                    risky_positions.append((symbol, risk_score, pos_data))
                
                # Sort by risk score (highest first)
                risky_positions.sort(key=lambda x: x[1], reverse=True)
                
                # Close top 50% of risky positions
                positions_to_close = len(risky_positions) // 2
                if positions_to_close > 0:
                    for symbol, risk_score, pos_data in risky_positions[:positions_to_close]:
                        logger.warning(f"📉 Closing risky position: {symbol} (risk score: {risk_score:.2f})")
                        try:
                            await self.position_manager.close_position(symbol, urgency="high")
                        except Exception as e:
                            logger.error(f"Error closing position {symbol}: {e}")
            except Exception as e:
                logger.error(f"Error reducing risk exposure: {e}")
        
    async def _send_alerts(self, metrics: RiskMetrics, level: RiskLevel):
        """Send alerts to all registered handlers"""
        for handler in self.alert_handlers:
            try:
                await handler(metrics, level)
            except Exception as e:
                logger.error(f"Error in alert handler: {e}")
                
    async def _send_critical_alert(self, metrics: RiskMetrics):
        """Send critical alert for breach"""
        alert_message = f"""
        🚨 PROP FIRM RISK BREACH 🚨
        
        Drawdown: {metrics.current_drawdown:.2f}% (limit: {self.max_drawdown}%)
        Daily P&L: {metrics.daily_pnl_pct:.2f}% (limit: -{self.daily_loss_limit}%)
        
        Emergency shutdown executed.
        """
        logger.critical(alert_message)
        # Send to alerting system (email, Slack, etc.)
        
    def _log_shutdown_state(self, metrics: RiskMetrics):
        """Log detailed state for post-incident analysis"""
        log_file = Path("argo/logs") / f"risk_shutdown_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        shutdown_data = {
            'timestamp': datetime.now().isoformat(),
            'metrics': {
                'current_drawdown': metrics.current_drawdown,
                'daily_pnl_pct': metrics.daily_pnl_pct,
                'account_equity': metrics.account_equity,
                'peak_equity': metrics.peak_equity,
                'open_positions': metrics.open_positions
            },
            'limits': {
                'max_drawdown': self.max_drawdown,
                'daily_loss_limit': self.daily_loss_limit
            }
        }
        
        with open(log_file, 'w') as f:
            json.dump(shutdown_data, f, indent=2)
            
        logger.critical(f"📝 Shutdown state logged to {log_file}")
        
    async def _collect_metrics(self) -> RiskMetrics:
        """Collect current risk metrics"""
        # Calculate drawdown
        if self.current_equity > self.peak_equity:
            self.peak_equity = self.current_equity
            
        drawdown_pct = ((self.peak_equity - self.current_equity) / self.peak_equity) * 100 if self.peak_equity > 0 else 0.0
        
        # Calculate daily P&L
        daily_pnl = self.current_equity - self.daily_start_equity
        daily_pnl_pct = (daily_pnl / self.daily_start_equity) * 100 if self.daily_start_equity > 0 else 0.0
        
        # Count positions
        open_positions = len(self.positions)
        
        # Calculate correlation (simplified)
        correlated_positions = self._count_correlated_positions()
        portfolio_correlation = self._calculate_portfolio_correlation()
        
        # Largest position size
        largest_position_size = max(
            (pos.get('size_pct', 0.0) for pos in self.positions.values()),
            default=0.0
        )
        
        return RiskMetrics(
            timestamp=datetime.now(),
            current_drawdown=drawdown_pct,
            daily_pnl_pct=daily_pnl_pct,
            open_positions=open_positions,
            correlated_positions=correlated_positions,
            largest_position_size=largest_position_size,
            portfolio_correlation=portfolio_correlation,
            risk_level=RiskLevel.NORMAL,  # Will be set by assess_risk_level
            account_equity=self.current_equity,
            peak_equity=self.peak_equity
        )
        
    def _count_correlated_positions(self) -> int:
        """Count positions that are highly correlated (>0.7 correlation)"""
        if len(self.positions) < 2:
            return 0
        
        # Define correlation groups (ETFs, tech stocks, etc.)
        correlation_groups = {
            'sp500_etfs': ['SPY', 'VOO', 'IVV'],
            'nasdaq_etfs': ['QQQ', 'ONEQ', 'QQQM'],
            'tech_stocks': ['AAPL', 'MSFT', 'GOOGL', 'META', 'NVDA', 'AMD'],
            'crypto': ['BTC-USD', 'ETH-USD', 'SOL-USD', 'AVAX-USD'],
            'semiconductors': ['NVDA', 'AMD', 'INTC', 'TSM'],
        }
        
        # Count positions in same correlation group
        position_symbols = list(self.positions.keys())
        correlated_count = 0
        
        for group_name, symbols in correlation_groups.items():
            group_positions = [s for s in position_symbols if s in symbols]
            if len(group_positions) > 1:
                # More than 1 position in same group = correlated
                correlated_count += len(group_positions) - 1  # Count excess positions
        
        return correlated_count
        
    def _calculate_portfolio_correlation(self) -> float:
        """Calculate portfolio-wide correlation (0.0 to 1.0)"""
        if len(self.positions) < 2:
            return 0.0
        
        # Define correlation groups
        correlation_groups = {
            'sp500_etfs': ['SPY', 'VOO', 'IVV'],
            'nasdaq_etfs': ['QQQ', 'ONEQ', 'QQQM'],
            'tech_stocks': ['AAPL', 'MSFT', 'GOOGL', 'META', 'NVDA', 'AMD'],
            'crypto': ['BTC-USD', 'ETH-USD', 'SOL-USD', 'AVAX-USD'],
            'semiconductors': ['NVDA', 'AMD', 'INTC', 'TSM'],
        }
        
        position_symbols = list(self.positions.keys())
        total_positions = len(position_symbols)
        correlated_pairs = 0
        total_pairs = total_positions * (total_positions - 1) / 2 if total_positions > 1 else 0
        
        if total_pairs == 0:
            return 0.0
        
        # Count correlated pairs (positions in same group)
        for group_name, symbols in correlation_groups.items():
            group_positions = [s for s in position_symbols if s in symbols]
            if len(group_positions) > 1:
                # Calculate pairs within this group
                group_pairs = len(group_positions) * (len(group_positions) - 1) / 2
                correlated_pairs += group_pairs
        
        # Return correlation ratio
        return min(correlated_pairs / total_pairs if total_pairs > 0 else 0.0, 1.0)
        
    def update_equity(self, equity: float):
        """Update current account equity"""
        self.current_equity = equity
        
    def add_position(self, symbol: str, position_data: Dict):
        """Add a position to tracking"""
        self.positions[symbol] = position_data
        
    def remove_position(self, symbol: str):
        """Remove a position from tracking"""
        if symbol in self.positions:
            del self.positions[symbol]
            
    def register_alert_handler(self, handler: Callable):
        """Register an alert handler function"""
        self.alert_handlers.append(handler)
        
    def get_monitoring_stats(self) -> dict:
        """Get monitoring statistics"""
        current_metrics = self.metrics_history[-1] if self.metrics_history else None
        return {
            "monitoring_active": self.monitoring_active,
            "breach_count": self.breach_count,
            "critical_count": self.critical_count,
            "warning_count": self.warning_count,
            "total_metrics_collected": len(self.metrics_history),
            "current_risk_level": current_metrics.risk_level.value if current_metrics else "normal",
            "current_drawdown": current_metrics.current_drawdown if current_metrics else 0.0,
            "daily_pnl_pct": current_metrics.daily_pnl_pct if current_metrics else 0.0,
            "account_equity": self.current_equity,
            "peak_equity": self.peak_equity,
            "trading_halted": getattr(self, 'trading_halted', False),
            "halt_reason": getattr(self, 'halt_reason', None),
            "open_positions": len(self.positions),
            "correlated_positions": current_metrics.correlated_positions if current_metrics else 0,
            "portfolio_correlation": current_metrics.portfolio_correlation if current_metrics else 0.0
        }
    
    def can_trade(self) -> tuple[bool, str]:
        """
        Check if trading is allowed
        
        Returns:
            (can_trade: bool, reason: str)
        """
        if not self.monitoring_active:
            return True, "Monitoring not active"
        
        if getattr(self, 'trading_halted', False):
            return False, getattr(self, 'halt_reason', 'Trading halted')
        
        stats = self.get_monitoring_stats()
        risk_level = stats.get('current_risk_level', 'normal')
        
        if risk_level == 'breach':
            return False, "Risk breach detected"
        elif risk_level == 'critical':
            return False, "Critical risk level - trading suspended"
        
        return True, "OK"


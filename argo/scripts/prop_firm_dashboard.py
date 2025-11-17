#!/usr/bin/env python3
"""
Prop Firm Monitoring Dashboard
Real-time dashboard for prop firm risk monitoring and alerts

Usage:
    python scripts/prop_firm_dashboard.py [--refresh 5] [--json]
"""
import sys
import argparse
import json
import time
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from argo.risk.prop_firm_risk_monitor import PropFirmRiskMonitor
    from argo.risk.prop_firm_monitor_enhanced import PropFirmMonitorEnhanced
    from argo.core.config_loader import ConfigLoader
except ImportError as e:
    print(f"⚠️  Import error: {e}")
    print("   Make sure you're running from the argo directory")
    sys.exit(1)

def load_prop_firm_config():
    """Load prop firm configuration"""
    try:
        config, _ = ConfigLoader.load_config()
        prop_firm_config = config.get('prop_firm', {})
        
        if not prop_firm_config.get('enabled', False):
            print("❌ Prop firm mode is not enabled in config.json")
            return None
        
        risk_limits = prop_firm_config.get('risk_limits', {})
        return {
            'max_drawdown_pct': risk_limits.get('max_drawdown_pct', 2.0),
            'daily_loss_limit_pct': risk_limits.get('daily_loss_limit_pct', 4.5),
            'max_position_size_pct': risk_limits.get('max_position_size_pct', 3.0),
            'min_confidence': risk_limits.get('min_confidence', 82.0),
            'max_positions': risk_limits.get('max_positions', 3),
            'max_stop_loss_pct': risk_limits.get('max_stop_loss_pct', 1.5)
        }
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return None

def print_dashboard(monitor: PropFirmMonitorEnhanced, json_output: bool = False):
    """Print dashboard"""
    dashboard_data = monitor.get_dashboard_data()
    
    if json_output:
        print(json.dumps(dashboard_data, indent=2))
        return
    
    # Clear screen (works on most terminals)
    print("\033[2J\033[H", end="")
    
    stats = dashboard_data['stats']
    alert_counts = dashboard_data['alert_counts']
    
    print("=" * 70)
    print("🏢 PROP FIRM MONITORING DASHBOARD")
    print("=" * 70)
    print(f"⏰ Last Updated: {dashboard_data['timestamp']}")
    print()
    
    # Risk Level
    risk_level = stats.get('current_risk_level', 'normal')
    risk_emoji = {
        'normal': '✅',
        'warning': '⚠️',
        'critical': '🔴',
        'breach': '🚨'
    }.get(risk_level, '❓')
    
    print(f"{risk_emoji} Risk Level: {risk_level.upper()}")
    print()
    
    # Drawdown
    drawdown = stats.get('current_drawdown', 0)
    max_drawdown = monitor.risk_monitor.max_drawdown
    drawdown_pct = (drawdown / max_drawdown * 100) if max_drawdown > 0 else 0
    
    drawdown_bar = "█" * int(drawdown_pct / 5) + "░" * (20 - int(drawdown_pct / 5))
    drawdown_color = "🟢" if drawdown_pct < 70 else "🟡" if drawdown_pct < 90 else "🔴"
    
    print(f"📉 Drawdown: {drawdown:.2f}% / {max_drawdown}% limit")
    print(f"   {drawdown_color} [{drawdown_bar}] {drawdown_pct:.1f}%")
    print()
    
    # Daily P&L
    daily_pnl = stats.get('daily_pnl_pct', 0)
    daily_limit = monitor.risk_monitor.daily_loss_limit
    daily_pct = abs(daily_pnl / daily_limit * 100) if daily_limit > 0 else 0
    
    daily_bar = "█" * int(daily_pct / 5) + "░" * (20 - int(daily_pct / 5))
    daily_color = "🟢" if daily_pnl > -daily_limit * 0.7 else "🟡" if daily_pnl > -daily_limit * 0.9 else "🔴"
    
    print(f"💰 Daily P&L: {daily_pnl:+.2f}% / {daily_limit}% limit")
    print(f"   {daily_color} [{daily_bar}] {daily_pct:.1f}%")
    print()
    
    # Account Info
    equity = stats.get('account_equity', 0)
    peak_equity = stats.get('peak_equity', 0)
    
    print(f"💵 Account Equity: ${equity:,.2f}")
    print(f"📈 Peak Equity: ${peak_equity:,.2f}")
    print()
    
    # Positions
    positions = stats.get('open_positions', 0)
    max_positions = 3
    correlation = stats.get('portfolio_correlation', 0)
    
    print(f"📊 Open Positions: {positions} / {max_positions} max")
    print(f"🔗 Portfolio Correlation: {correlation:.2f}")
    print()
    
    # Trading Status
    trading_halted = stats.get('trading_halted', False)
    halt_reason = stats.get('halt_reason', '')
    
    if trading_halted:
        print(f"🛑 Trading HALTED: {halt_reason}")
    else:
        print("✅ Trading ACTIVE")
    print()
    
    # Alerts
    print("🚨 RECENT ALERTS")
    print("-" * 70)
    
    if dashboard_data['recent_alerts']:
        for alert in dashboard_data['recent_alerts'][:5]:
            alert_emoji = {
                'info': 'ℹ️',
                'warning': '⚠️',
                'critical': '🔴',
                'breach': '🚨'
            }.get(alert['level'], '❓')
            
            timestamp = datetime.fromisoformat(alert['timestamp']).strftime('%H:%M:%S')
            print(f"{alert_emoji} [{timestamp}] {alert['message']}")
    else:
        print("✅ No recent alerts")
    print()
    
    # Alert Summary
    print("📊 ALERT SUMMARY")
    print("-" * 70)
    print(f"Total Alerts: {alert_counts['total']}")
    print(f"  🚨 Breach: {alert_counts['breach']}")
    print(f"  🔴 Critical: {alert_counts['critical']}")
    print(f"  ⚠️  Warning: {alert_counts['warning']}")
    print(f"  ℹ️  Info: {alert_counts['info']}")
    print()
    
    print("=" * 70)
    print("Press Ctrl+C to exit")
    print()

def main():
    parser = argparse.ArgumentParser(description='Prop Firm Monitoring Dashboard')
    parser.add_argument('--refresh', type=int, default=5, help='Refresh interval in seconds (default: 5)')
    parser.add_argument('--json', action='store_true', help='Output as JSON (single run)')
    args = parser.parse_args()
    
    # Load config
    config = load_prop_firm_config()
    if not config:
        sys.exit(1)
    
    # Initialize risk monitor
    risk_monitor = PropFirmRiskMonitor({
        'max_drawdown_pct': config['max_drawdown_pct'],
        'daily_loss_limit_pct': config['daily_loss_limit_pct'],
        'initial_capital': 25000.0
    })
    
    # Initialize enhanced monitor
    enhanced_monitor = PropFirmMonitorEnhanced(risk_monitor)
    
    # Try to get current equity from trading engine
    try:
        from argo.core.paper_trading_engine import PaperTradingEngine
        engine = PaperTradingEngine()
        if engine.alpaca_enabled:
            account = engine.get_account_details()
            if account:
                risk_monitor.update_equity(account['equity'])
                risk_monitor.peak_equity = account['equity']
    except Exception as e:
        print(f"⚠️  Could not get account info: {e}")
    
    if args.json:
        # Single JSON output
        print_dashboard(enhanced_monitor, json_output=True)
    else:
        # Continuous dashboard
        try:
            while True:
                print_dashboard(enhanced_monitor)
                time.sleep(args.refresh)
        except KeyboardInterrupt:
            print("\n\n👋 Dashboard stopped")

if __name__ == "__main__":
    main()


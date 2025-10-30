#!/usr/bin/env python3
"""
ARGO Capital Performance Analytics & P&L Tracking
Professional trading performance monitoring system
"""

import redis
import json
import pandas as pd
from datetime import datetime, timedelta
import logging

class ArgoPerformanceAnalytics:
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        self.logger = logging.getLogger('ArgoAnalytics')
        
    def get_portfolio_performance(self):
        """Get current portfolio performance metrics"""
        try:
            portfolio = self.redis_client.hgetall('portfolio:current')
            if not portfolio:
                return None
                
            # Parse position data
            positions = {}
            if portfolio.get('positions'):
                positions = json.loads(portfolio['positions'])
            
            # Calculate total position value
            total_position_value = 0
            for symbol, data in positions.items():
                if isinstance(data, dict):
                    shares = data.get('shares', 0)
                    avg_price = data.get('avg_price', 0)
                    total_position_value += shares * avg_price
            
            performance_data = {
                'timestamp': datetime.now().isoformat(),
                'balance': float(portfolio.get('balance', 0)),
                'buying_power': float(portfolio.get('buying_power', 0)),
                'total_positions': len(positions),
                'position_value': total_position_value,
                'daily_pnl': float(portfolio.get('daily_pnl', 0)),
                'positions': positions
            }
            
            return performance_data
            
        except Exception as e:
            self.logger.error(f"Performance calculation error: {e}")
            return None
    
    def get_trading_signals_performance(self):
        """Analyze recent trading signals performance"""
        try:
            signals = self.redis_client.lrange('signals:chronological', 0, 19)  # Last 20 signals
            
            if not signals:
                return {'total_signals': 0, 'avg_confidence': 0}
            
            parsed_signals = []
            total_confidence = 0
            
            for signal in signals:
                try:
                    signal_data = json.loads(signal)
                    parsed_signals.append(signal_data)
                    total_confidence += signal_data.get('confidence', 0)
                except json.JSONDecodeError:
                    continue
            
            if parsed_signals:
                avg_confidence = total_confidence / len(parsed_signals)
                
                # Count signal types
                buy_signals = sum(1 for s in parsed_signals if s.get('signal') == 'BUY')
                sell_signals = sum(1 for s in parsed_signals if s.get('signal') == 'SELL')
                
                return {
                    'total_signals': len(parsed_signals),
                    'avg_confidence': avg_confidence,
                    'buy_signals': buy_signals,
                    'sell_signals': sell_signals,
                    'latest_signals': parsed_signals[:5]  # Most recent 5
                }
            
            return {'total_signals': 0, 'avg_confidence': 0}
            
        except Exception as e:
            self.logger.error(f"Signal analysis error: {e}")
            return {'error': str(e)}
    
    def generate_performance_report(self):
        """Generate comprehensive performance report"""
        print("📊 ARGO CAPITAL PERFORMANCE ANALYTICS REPORT")
        print("=" * 50)
        print(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Portfolio Performance
        portfolio_perf = self.get_portfolio_performance()
        if portfolio_perf:
            print("💰 PORTFOLIO PERFORMANCE:")
            print(f"   Balance: ${portfolio_perf['balance']:,.2f}")
            print(f"   Buying Power: ${portfolio_perf['buying_power']:,.2f}")
            print(f"   Daily P&L: ${portfolio_perf['daily_pnl']:,.2f}")
            print(f"   Active Positions: {portfolio_perf['total_positions']}")
            print(f"   Position Value: ${portfolio_perf['position_value']:,.2f}")
            
            # Position breakdown
            if portfolio_perf['positions']:
                print(f"   Position Details:")
                for symbol, data in portfolio_perf['positions'].items():
                    if isinstance(data, dict):
                        shares = data.get('shares', 0)
                        avg_price = data.get('avg_price', 0)
                        value = shares * avg_price
                        print(f"     {symbol}: {shares} shares @ ${avg_price:.2f} = ${value:,.2f}")
        else:
            print("💰 PORTFOLIO PERFORMANCE: Data not available")
        
        print()
        
        # Trading Signals Performance
        signals_perf = self.get_trading_signals_performance()
        if 'error' not in signals_perf:
            print("📈 TRADING SIGNALS PERFORMANCE:")
            print(f"   Total Recent Signals: {signals_perf.get('total_signals', 0)}")
            print(f"   Average Confidence: {signals_perf.get('avg_confidence', 0):.1%}")
            print(f"   Buy Signals: {signals_perf.get('buy_signals', 0)}")
            print(f"   Sell Signals: {signals_perf.get('sell_signals', 0)}")
            
            # Latest signals
            latest = signals_perf.get('latest_signals', [])
            if latest:
                print("   Recent Signals:")
                for signal in latest[:3]:
                    symbol = signal.get('symbol', 'N/A')
                    action = signal.get('signal', 'N/A')
                    confidence = signal.get('confidence', 0)
                    timestamp = signal.get('timestamp', 'N/A')
                    print(f"     {symbol} {action} ({confidence:.1%}) - {timestamp}")
        else:
            print("📈 TRADING SIGNALS: Analysis error")
        
        print()
        
        # System Health
        print("💓 SYSTEM HEALTH STATUS:")
        try:
            redis_status = self.redis_client.ping()
            print(f"   Redis Connection: {'✅ HEALTHY' if redis_status else '❌ ERROR'}")
        except:
            print("   Redis Connection: ❌ ERROR")
        
        # Risk assessment
        print()
        print("🛡️ RISK ASSESSMENT:")
        if portfolio_perf:
            balance = portfolio_perf['balance']
            position_value = portfolio_perf['position_value']
            if balance > 0:
                exposure_pct = (position_value / balance) * 100
                risk_level = "LOW" if exposure_pct < 50 else "MODERATE" if exposure_pct < 75 else "HIGH"
                print(f"   Portfolio Exposure: {exposure_pct:.1f}% ({risk_level})")
            else:
                print("   Portfolio Exposure: Unable to calculate")
        
        print()
        print("✅ ARGO Performance Analytics: Report Complete")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    analytics = ArgoPerformanceAnalytics()
    analytics.generate_performance_report()

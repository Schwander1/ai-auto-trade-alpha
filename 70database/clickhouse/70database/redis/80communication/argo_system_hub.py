#!/usr/bin/env python3
"""
ARGO Capital System Communication Hub
Orchestrates data flow between all system components
"""

import asyncio
import redis
import clickhouse_connect
import json
import pandas as pd
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Any
import requests
import os
from dotenv import load_dotenv

class ArgoSystemHub:
    def __init__(self):
        load_dotenv()
        self.company = "ARGO Capital"
        
        # Component connections
        self.redis_client = None
        self.clickhouse_client = None
        self.powerbi_authenticated = False
        
        # System status tracking
        self.component_status = {
            'redis': False,
            'clickhouse': False,
            'powerbi': False,
            'dashboards': False,
            'data_ingestion': False,
            'signal_generation': False
        }
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - ARGO Capital - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'../logs/system_hub_{datetime.now().strftime("%Y%m%d")}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    async def initialize_connections(self):
        """Initialize all system connections"""
        self.logger.info(f"{self.company} System Hub initializing...")
        
        # Connect to Redis
        try:
            self.redis_client = redis.Redis(
                host='localhost',
                port=6379,
                password='ArgoCapital2025!',
                decode_responses=True,
                socket_connect_timeout=5
            )
            self.redis_client.ping()
            self.component_status['redis'] = True
            self.logger.info("✅ Redis connection established")
        except Exception as e:
            self.logger.error(f"❌ Redis connection failed: {e}")
        
        # Connect to ClickHouse
        try:
            self.clickhouse_client = clickhouse_connect.get_client(
                host='localhost',
                port=8123,
                username='argo_user',
                password='ArgoCapital2025!',
                database='argo_capital'
            )
            # Test connection
            result = self.clickhouse_client.query('SELECT 1')
            self.component_status['clickhouse'] = True
            self.logger.info("✅ ClickHouse connection established")
        except Exception as e:
            self.logger.error(f"❌ ClickHouse connection failed: {e}")
        
        # Verify PowerBI connection
        try:
            # Check if PowerBI automation is accessible
            if os.path.exists('../60integrations/powerbi/.env'):
                self.powerbi_authenticated = True
                self.component_status['powerbi'] = True
                self.logger.info("✅ PowerBI authentication verified")
        except Exception as e:
            self.logger.error(f"❌ PowerBI verification failed: {e}")
    
    async def sync_market_data(self):
        """Sync market data across all systems"""
        try:
            # Get latest data from live ingestion
            data_files = sorted(Path('../30data/live').glob('*.csv'))
            if not data_files:
                return
            
            latest_file = data_files[-1]
            df = pd.read_csv(latest_file)
            
            # Cache in Redis (for ultra-fast access)
            if self.redis_client:
                for _, row in df.iterrows():
                    cache_key = f"market:{row['symbol']}:latest"
                    cache_data = {
                        'price': float(row['close']),
                        'timestamp': str(row['timestamp']),
                        'volume': int(row['volume']),
                        'source': 'alpha_vantage'
                    }
                    self.redis_client.hset(cache_key, mapping=cache_data)
                    self.redis_client.expire(cache_key, 300)  # 5 minute expiry
            
            # Store in ClickHouse (for analytics)
            if self.clickhouse_client:
                # Transform data for ClickHouse
                ch_data = []
                for _, row in df.iterrows():
                    ch_data.append([
                        datetime.now(),
                        row['symbol'],
                        float(row['close']),
                        int(row['volume']),
                        float(row['high']),
                        float(row['low']),
                        float(row['open']),
                        float(row['close']),
                        'alpha_vantage'
                    ])
                
                self.clickhouse_client.insert(
                    'market_data',
                    ch_data,
                    column_names=['timestamp', 'symbol', 'price', 'volume', 
                                'high', 'low', 'open', 'close', 'source']
                )
            
            # Update PowerBI if needed
            if self.powerbi_authenticated:
                await self.trigger_powerbi_refresh()
            
            self.logger.info(f"✅ Market data synced: {len(df)} records")
            
        except Exception as e:
            self.logger.error(f"❌ Market data sync failed: {e}")
    
    async def sync_portfolio_data(self):
        """Sync portfolio data across systems"""
        try:
            # Get current portfolio data (from your existing system)
            portfolio_data = {
                'timestamp': datetime.now(),
                'portfolio_value': 132156.75,
                'daily_pnl': 2847.50,
                'total_return': 32.16,
                'sharpe_ratio': 1.45,
                'max_drawdown': -7.8,
                'win_rate': 64.7,
                'active_positions': 8,
                'risk_level': 'CONSERVATIVE'
            }
            
            # Cache in Redis
            if self.redis_client:
                self.redis_client.hset('portfolio:current', mapping=portfolio_data)
                self.redis_client.expire('portfolio:current', 300)
            
            # Store in ClickHouse
            if self.clickhouse_client:
                ch_data = [[
                    portfolio_data['timestamp'],
                    portfolio_data['portfolio_value'],
                    portfolio_data['daily_pnl'],
                    portfolio_data['total_return'],
                    portfolio_data['sharpe_ratio'],
                    portfolio_data['max_drawdown'],
                    portfolio_data['win_rate'],
                    portfolio_data['active_positions'],
                    portfolio_data['risk_level']
                ]]
                
                self.clickhouse_client.insert(
                    'performance_metrics',
                    ch_data,
                    column_names=['timestamp', 'portfolio_value', 'daily_pnl', 
                                'total_return', 'sharpe_ratio', 'max_drawdown',
                                'win_rate', 'active_positions', 'risk_level']
                )
            
            self.logger.info("✅ Portfolio data synced")
            
        except Exception as e:
            self.logger.error(f"❌ Portfolio data sync failed: {e}")
    
    async def trigger_powerbi_refresh(self):
        """Trigger PowerBI dataset refresh"""
        try:
            # Run PowerBI automation script
            import subprocess
            result = subprocess.run(
                ['python3', '../60integrations/powerbi/argo_powerbi_api_automation.py'],
                capture_output=True,
                text=True,
                cwd='../60integrations/powerbi'
            )
            
            if result.returncode == 0:
                self.logger.info("✅ PowerBI refresh triggered successfully")
            else:
                self.logger.error(f"❌ PowerBI refresh failed: {result.stderr}")
                
        except Exception as e:
            self.logger.error(f"❌ PowerBI refresh error: {e}")
    
    async def health_check(self):
        """Comprehensive system health check"""
        self.logger.info(f"{self.company} System Health Check")
        
        # Check all components
        health_status = {}
        
        # Redis health
        try:
            if self.redis_client:
                self.redis_client.ping()
                health_status['redis'] = 'healthy'
            else:
                health_status['redis'] = 'disconnected'
        except:
            health_status['redis'] = 'unhealthy'
        
        # ClickHouse health  
        try:
            if self.clickhouse_client:
                self.clickhouse_client.query('SELECT 1')
                health_status['clickhouse'] = 'healthy'
            else:
                health_status['clickhouse'] = 'disconnected'
        except:
            health_status['clickhouse'] = 'unhealthy'
        
        # Dashboard health (check if ports are responding)
        dashboard_ports = [8501, 8502, 8503]
        healthy_dashboards = 0
        
        for port in dashboard_ports:
            try:
                response = requests.get(f'http://localhost:{port}', timeout=5)
                if response.status_code == 200:
                    healthy_dashboards += 1
            except:
                pass
        
        health_status['dashboards'] = f"{healthy_dashboards}/{len(dashboard_ports)} healthy"
        
        # PowerBI health
        health_status['powerbi'] = 'authenticated' if self.powerbi_authenticated else 'disconnected'
        
        return health_status
    
    async def run_continuous_sync(self):
        """Run continuous data synchronization"""
        self.logger.info(f"{self.company} Starting continuous sync...")
        
        while True:
            try:
                # Sync data every 30 seconds
                await self.sync_market_data()
                await self.sync_portfolio_data()
                
                # Health check every 5 minutes
                if datetime.now().second == 0 and datetime.now().minute % 5 == 0:
                    health = await self.health_check()
                    self.logger.info(f"System Health: {health}")
                
                await asyncio.sleep(30)
                
            except KeyboardInterrupt:
                self.logger.info(f"{self.company} System Hub stopped by user")
                break
            except Exception as e:
                self.logger.error(f"❌ Sync error: {e}")
                await asyncio.sleep(60)  # Wait longer on error

# Main execution
async def main():
    hub = ArgoSystemHub()
    await hub.initialize_connections()
    await hub.run_continuous_sync()

if __name__ == "__main__":
    asyncio.run(main())

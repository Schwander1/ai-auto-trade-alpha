#!/usr/bin/env python3
"""
Alpine Analytics - Argo Metrics Exporter
Exports Argo trading metrics to Prometheus format
"""

import time
import requests
from prometheus_client import start_http_server, Gauge, Counter, Info
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# Argo API Configuration
ARGO_API_URL = "http://178.156.194.174:8000"
SCRAPE_INTERVAL = 30  # seconds
EXPORTER_PORT = 9200

# Prometheus Metrics
argo_win_rate = Gauge('argo_win_rate', 'Current win rate percentage')
argo_total_signals = Counter('argo_total_signals', 'Total signals generated')
argo_sharpe_ratio = Gauge('argo_sharpe_ratio', 'Sharpe ratio')
argo_max_drawdown = Gauge('argo_max_drawdown', 'Maximum drawdown percentage')
argo_premium_signals = Gauge('argo_premium_signals', 'Number of premium signals (>95%)')
argo_standard_signals = Gauge('argo_standard_signals', 'Number of standard signals (85-95%)')
argo_strategies_loaded = Gauge('argo_strategies_loaded', 'Number of active strategies')
argo_data_sources = Gauge('argo_data_sources', 'Number of connected data sources')
argo_uptime = Gauge('argo_uptime_seconds', 'Argo uptime in seconds')
argo_status = Gauge('argo_status', 'Argo health status (1=healthy, 0=unhealthy)')

# Info metrics
argo_info = Info('argo_info', 'Argo version and configuration')

def fetch_argo_metrics():
    """Fetch metrics from Argo API"""
    try:
        # Health endpoint
        health_response = requests.get(f"{ARGO_API_URL}/health", timeout=5)
        health_data = health_response.json()
        
        # Stats endpoint
        stats_response = requests.get(f"{ARGO_API_URL}/api/v1/stats", timeout=5)
        stats_data = stats_response.json()
        
        # Signals endpoint (if available)
        try:
            signals_response = requests.get(f"{ARGO_API_URL}/api/v1/signals/summary", timeout=5)
            signals_data = signals_response.json()
        except:
            signals_data = {}
        
        return health_data, stats_data, signals_data
    except Exception as e:
        logging.error(f"Failed to fetch Argo metrics: {e}")
        return None, None, None

def update_metrics():
    """Update Prometheus metrics with latest Argo data"""
    health, stats, signals = fetch_argo_metrics()
    
    if health is None:
        argo_status.set(0)
        logging.warning("Argo unreachable")
        return
    
    # Update status
    argo_status.set(1 if health.get('status') == 'healthy' else 0)
    
    # Update info
    argo_info.info({
        'version': str(health.get('version', 'unknown')),
        'ai_enabled': str(health.get('ai_enabled', False)),
        'performance_tracking': str(health.get('performance_tracking', False))
    })
    
    # Update metrics from health
    argo_strategies_loaded.set(health.get('strategies_loaded', 0))
    argo_data_sources.set(health.get('data_sources', 0))
    
    # Calculate uptime (if provided as percentage string like "100%")
    uptime_str = health.get('uptime', '0%')
    if isinstance(uptime_str, str):
        uptime_pct = float(uptime_str.strip('%'))
        # Assume 30 days max tracked
        argo_uptime.set(uptime_pct / 100 * 30 * 24 * 3600)
    
    # Update stats metrics
    if stats:
        argo_win_rate.set(stats.get('win_rate', 0))
        
        # Total signals as counter (need to track increases)
        total = stats.get('total_signals', 0)
        if total > 0:
            # Reset counter and increment to current value
            argo_total_signals._value.set(total)
        
        argo_sharpe_ratio.set(stats.get('sharpe_ratio', 0))
        argo_max_drawdown.set(stats.get('max_drawdown', 0))
    
    # Update signal breakdown
    if signals:
        argo_premium_signals.set(signals.get('premium_signals', 0))
        argo_standard_signals.set(signals.get('standard_signals', 0))
    
    logging.info(f"✓ Metrics updated - Win Rate: {stats.get('win_rate', 0)}%")

def main():
    """Main exporter loop"""
    logging.info(f"Starting Argo Metrics Exporter on port {EXPORTER_PORT}")
    logging.info(f"Polling {ARGO_API_URL} every {SCRAPE_INTERVAL}s")
    
    # Start Prometheus HTTP server
    start_http_server(EXPORTER_PORT)
    
    # Main loop
    while True:
        try:
            update_metrics()
        except Exception as e:
            logging.error(f"Error in metrics update: {e}")
        
        time.sleep(SCRAPE_INTERVAL)

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Enhanced Prometheus Metrics for Argo Trading Engine
Comprehensive metrics for observability
"""
from prometheus_client import Counter, Gauge, Histogram, Summary
from typing import Dict

# Signal Generation Metrics
signals_generated_total = Counter(
    'argo_signals_generated_total',
    'Total signals generated',
    ['symbol', 'direction', 'source']
)

signal_generation_duration = Histogram(
    'argo_signal_generation_duration_seconds',
    'Time to generate signal',
    ['symbol'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0]
)

signal_confidence = Gauge(
    'argo_signal_confidence',
    'Signal confidence level',
    ['symbol', 'direction']
)

# Data Source Metrics (already in data_source_health.py, but adding here for completeness)
data_source_requests_total = Counter(
    'argo_data_source_requests_total',
    'Total requests to data source',
    ['source_name', 'status']
)

# Trading Metrics
trades_executed_total = Counter(
    'argo_trades_executed_total',
    'Total trades executed',
    ['symbol', 'direction', 'status']
)

trade_pnl = Gauge(
    'argo_trade_pnl',
    'Profit/Loss for trade',
    ['symbol', 'trade_id']
)

active_positions = Gauge(
    'argo_active_positions',
    'Number of active positions',
    ['symbol']
)

# API Metrics
api_requests_total = Counter(
    'argo_api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status_code']
)

api_request_duration = Histogram(
    'argo_api_request_duration_seconds',
    'API request duration',
    ['method', 'endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0]
)

# System Metrics
system_cpu_usage = Gauge('argo_system_cpu_usage_percent', 'CPU usage percentage')
system_memory_usage = Gauge('argo_system_memory_usage_percent', 'Memory usage percentage')
system_disk_usage = Gauge('argo_system_disk_usage_percent', 'Disk usage percentage')

# Consensus Engine Metrics
consensus_calculations_total = Counter(
    'argo_consensus_calculations_total',
    'Total consensus calculations',
    ['result']  # 'signal_generated', 'no_consensus', 'below_threshold'
)

consensus_confidence = Gauge(
    'argo_consensus_confidence',
    'Consensus confidence level',
    ['symbol']
)

# Error Metrics
errors_total = Counter(
    'argo_errors_total',
    'Total errors',
    ['component', 'error_type']
)


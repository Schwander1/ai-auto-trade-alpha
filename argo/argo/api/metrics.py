"""Prometheus Metrics for Argo"""
from prometheus_client import Counter, Gauge, generate_latest
from fastapi import Response

signals_generated_total = Counter('signals_generated_total', 'Total signals generated', ['type'])
signals_premium_total = Counter('signals_premium_total', 'Total premium signals generated')
trading_win_rate = Gauge('trading_win_rate', 'Current win rate percentage')
signal_confidence = Gauge('signal_confidence', 'Average signal confidence', ['type'])

def get_metrics():
    return Response(content=generate_latest(), media_type="text/plain")

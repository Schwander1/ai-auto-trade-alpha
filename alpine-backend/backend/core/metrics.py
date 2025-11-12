"""Prometheus metrics for Alpine Backend"""
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
import time

# Request metrics
http_requests_total = Counter(
    'alpine_http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

http_request_duration_seconds = Histogram(
    'alpine_http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

# Business metrics
users_total = Gauge('alpine_users_total', 'Total number of users')
active_subscriptions = Gauge('alpine_active_subscriptions', 'Number of active subscriptions')
signals_delivered = Counter('alpine_signals_delivered_total', 'Total signals delivered')

# Error metrics
http_errors_total = Counter(
    'alpine_http_errors_total',
    'Total HTTP errors',
    ['status_code', 'endpoint']
)

# Database metrics
db_query_duration_seconds = Histogram(
    'alpine_db_query_duration_seconds',
    'Database query duration in seconds',
    ['operation']
)

# Cache metrics
cache_hits_total = Counter('alpine_cache_hits_total', 'Total cache hits', ['cache_type'])
cache_misses_total = Counter('alpine_cache_misses_total', 'Total cache misses', ['cache_type'])

# Rate limiting metrics
rate_limit_exceeded_total = Counter(
    'alpine_rate_limit_exceeded_total',
    'Total rate limit violations',
    ['endpoint', 'client_id']
)


def get_metrics() -> Response:
    """Get Prometheus metrics"""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


def record_request(method: str, endpoint: str, status_code: int, duration: float):
    """Record HTTP request metrics"""
    http_requests_total.labels(method=method, endpoint=endpoint, status_code=status_code).inc()
    http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(duration)
    
    if status_code >= 400:
        http_errors_total.labels(status_code=status_code, endpoint=endpoint).inc()


def record_db_query(operation: str, duration: float):
    """Record database query metrics"""
    db_query_duration_seconds.labels(operation=operation).observe(duration)


def record_cache_hit(cache_type: str):
    """Record cache hit"""
    cache_hits_total.labels(cache_type=cache_type).inc()


def record_cache_miss(cache_type: str):
    """Record cache miss"""
    cache_misses_total.labels(cache_type=cache_type).inc()


def record_rate_limit_exceeded(endpoint: str, client_id: str):
    """Record rate limit violation"""
    rate_limit_exceeded_total.labels(endpoint=endpoint, client_id=client_id).inc()

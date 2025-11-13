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

# Signal latency metrics (PATENT CLAIM: <500ms delivery)
signal_generation_latency = Histogram(
    'signal_generation_latency_seconds',
    'Time to generate signal (patent claim: real-time generation)',
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0]
)

signal_delivery_latency = Histogram(
    'signal_delivery_latency_seconds',
    'End-to-end signal delivery time (patent claim: <500ms)',
    buckets=[0.01, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0]
)

signal_verification_duration = Histogram(
    'signal_verification_duration_seconds',
    'SHA-256 verification time (patent claim: cryptographic verification)',
    buckets=[0.0001, 0.0005, 0.001, 0.005, 0.01]
)

# Latency percentile warnings
latency_p95_warning = Gauge(
    'signal_delivery_latency_p95_ms',
    'P95 signal delivery latency in milliseconds (alert if >500ms)'
)

latency_p99_warning = Gauge(
    'signal_delivery_latency_p99_ms',
    'P99 signal delivery latency in milliseconds (alert if >500ms)'
)

# Backup metrics
backup_duration_seconds = Histogram(
    'backup_duration_seconds',
    'Time to create backup',
    buckets=[1.0, 5.0, 10.0, 30.0, 60.0, 300.0]
)

last_backup_timestamp = Gauge(
    'last_backup_timestamp',
    'Unix timestamp of last successful backup'
)

# Integrity verification metrics
integrity_failed_verifications_total = Counter(
    'integrity_failed_verifications_total',
    'Total failed integrity verifications (should be 0)'
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

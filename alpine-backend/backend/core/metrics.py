"""Prometheus metrics for Redis and application monitoring"""
from prometheus_client import Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response

# Redis metrics
redis_cache_hits = Counter(
    'redis_cache_hits_total',
    'Total number of cache hits',
    ['cache_key']
)

redis_cache_misses = Counter(
    'redis_cache_misses_total',
    'Total number of cache misses',
    ['cache_key']
)

redis_cache_operations = Counter(
    'redis_cache_operations_total',
    'Total cache operations',
    ['operation', 'status']  # operation: get/set/delete, status: success/error
)

redis_memory_usage = Gauge(
    'redis_memory_usage_bytes',
    'Redis memory usage in bytes'
)

redis_connected = Gauge(
    'redis_connected',
    'Redis connection status (1=connected, 0=disconnected)'
)

# Rate limiting metrics
rate_limit_requests = Counter(
    'rate_limit_requests_total',
    'Total rate limit check requests',
    ['client_id', 'status']  # status: allowed/denied
)

rate_limit_exceeded = Counter(
    'rate_limit_exceeded_total',
    'Total rate limit violations',
    ['client_id']
)

# API performance metrics
api_request_duration = Histogram(
    'api_request_duration_seconds',
    'API request duration in seconds',
    ['method', 'endpoint', 'status_code'],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

api_requests_total = Counter(
    'api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status_code']
)

# Database metrics
db_query_duration = Histogram(
    'db_query_duration_seconds',
    'Database query duration in seconds',
    ['query_type'],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5]
)

db_connections_active = Gauge(
    'db_connections_active',
    'Number of active database connections'
)

db_connections_idle = Gauge(
    'db_connections_idle',
    'Number of idle database connections'
)


def get_metrics():
    """Get Prometheus metrics"""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


def update_redis_status(connected: bool):
    """Update Redis connection status"""
    redis_connected.set(1 if connected else 0)


def record_cache_hit(cache_key: str):
    """Record a cache hit"""
    redis_cache_hits.labels(cache_key=cache_key).inc()


def record_cache_miss(cache_key: str):
    """Record a cache miss"""
    redis_cache_misses.labels(cache_key=cache_key).inc()


def record_cache_operation(operation: str, success: bool):
    """Record a cache operation"""
    status = 'success' if success else 'error'
    redis_cache_operations.labels(operation=operation, status=status).inc()


def record_rate_limit_check(client_id: str, allowed: bool):
    """Record a rate limit check"""
    status = 'allowed' if allowed else 'denied'
    rate_limit_requests.labels(client_id=client_id, status=status).inc()
    if not allowed:
        rate_limit_exceeded.labels(client_id=client_id).inc()


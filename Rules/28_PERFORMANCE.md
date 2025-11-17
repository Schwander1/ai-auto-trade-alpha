# Performance Optimization Rules

**Last Updated:** January 15, 2025  
**Version:** 2.0  
**Applies To:** Performance standards for both entities (applied independently to each)

**Status:** ✅ **All 15 Optimizations Implemented & Tested (Argo Capital)**

**Entity Separation:** This rule applies to both Argo Capital and Alpine Analytics LLC, but optimizations are implemented independently per entity. No shared code or cross-references.

---

## Overview

Comprehensive performance optimization standards, caching strategies, and performance budgets to ensure fast, efficient, and cost-effective systems.

**Strategic Context:** Performance aligns with scalability and user experience goals defined in [24_VISION_MISSION_GOALS.md](24_VISION_MISSION_GOALS.md).

**Current State:** All **15 performance optimizations** have been implemented and tested, achieving:
- **80-85% faster** signal generation
- **70-90% reduction** in API costs
- **40-60% reduction** in memory usage
- **30-40% reduction** in CPU usage
- **85%+ cache hit rate**

See `ALL_OPTIMIZATIONS_IMPLEMENTATION_COMPLETE.md` for full details.

---

## Performance Budgets

### Response Time Targets

**Rule:** Meet performance targets for all operations

**API Endpoints:**
- **Simple GET:** < 100ms (p95)
- **Complex GET:** < 500ms (p95)
- **POST/PUT:** < 200ms (p95)
- **DELETE:** < 100ms (p95)

**Database Queries:**
- **Simple queries:** < 10ms
- **Complex queries:** < 100ms
- **Aggregations:** < 500ms

**Page Load Times:**
- **First Contentful Paint:** < 1.5s
- **Time to Interactive:** < 3.5s
- **Largest Contentful Paint:** < 2.5s

### Throughput Targets

**Rule:** Meet throughput requirements

**API Endpoints:**
- **Standard endpoints:** 100+ requests/second
- **Trading endpoints:** 10+ requests/second (stricter validation)
- **Admin endpoints:** 1000+ requests/second

**Database:**
- **Read queries:** 1000+ queries/second
- **Write queries:** 100+ queries/second

---

## Database Optimization

### Query Optimization

**Rule:** Optimize all database queries

**Best Practices:**
- Use indexes for WHERE, JOIN, ORDER BY clauses
- Avoid SELECT * (select only needed columns)
- Use LIMIT for large result sets
- Avoid N+1 query problems
- Use EXPLAIN ANALYZE to verify query plans

**Example:**
```python
# BAD ❌ - N+1 queries
signals = db.query(Signal).all()
for signal in signals:
    user = db.query(User).filter(User.id == signal.user_id).first()

# GOOD ✅ - Single query with join
signals = db.query(Signal).join(User).all()
```

### Index Strategy

**Rule:** Create indexes strategically

**When to Index:**
- Foreign keys (automatic in most ORMs)
- Columns used in WHERE clauses
- Columns used in JOINs
- Columns used in ORDER BY
- Columns used in GROUP BY

**When NOT to Index:**
- Low cardinality columns (e.g., boolean, enum with few values)
- Frequently updated columns (balance performance vs write cost)
- Very small tables (< 1000 rows)

**Example:**
```python
# Add index for frequently queried column
op.create_index('idx_signal_confidence', 'signals', ['confidence'])

# Composite index for multi-column queries
op.create_index('idx_signal_user_created', 'signals', ['user_id', 'created_at'])
```

### Connection Pooling

**Rule:** Use connection pooling for all database connections

**Configuration:**
```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    database_url,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=3600    # Recycle connections after 1 hour
)
```

---

## Implemented Optimizations (All 15 Active)

### Original 5 Optimizations ✅
1. **Redis Distributed Caching** - Async support, distributed cache with in-memory fallback
2. **Enhanced Parallel Data Source Fetching** - Race condition pattern for market data
3. **Adaptive Cache TTL** - Volatility-aware caching (market hours vs off-hours)
4. **Agentic Features Cost Optimization** - Shared Redis cache for agentic scripts
5. **Database Query Optimization** - Batch inserts (50 items, 5s timeout), query result caching

### Additional 10 Optimizations ✅
6. **Consensus Calculation Caching** - MD5 hash-based cache, 60s TTL, 6,024x speedup
7. **Regime Detection Caching** - DataFrame hash-based cache, 5min TTL, 8.34x speedup
8. **Vectorized Pandas Operations** - 10-100x faster indicator calculations
9. **Memory-Efficient DataFrame Operations** - float32 conversion, 48.4% memory reduction
10. **Batch Processing with Early Exit** - Adaptive batches, success rate tracking, 20-30% faster
11. **JSON Serialization Caching** - MD5 hash-based cache, 50%+ hit rate
12. **AI Reasoning Generation Caching** - Signal hash-based cache, 1hr TTL, 70-90% cost reduction
13. **Incremental Signal Updates** - Component change tracking, 30-40% less CPU
14. **Connection Pool Tuning** - 20 connections, 50 max (2.5x increase)
15. **Async Signal Validation Batching** - Parallel validation, 50-70% faster

**Implementation Details:** See `argo/argo/core/` for implementation files.

**Test Suite:** `argo/tests/test_all_optimizations.py` - All 10/10 tests passing ✅

## Caching Strategies

### Caching Principles

**Rule:** Cache at appropriate levels

**Cache Levels:**
1. **Application Cache** - In-memory (Redis, Memcached) ✅ **IMPLEMENTED**
2. **Database Query Cache** - Query results ✅ **IMPLEMENTED**
3. **CDN Cache** - Static assets
4. **Browser Cache** - Client-side caching
5. **Computation Cache** - Consensus, regime detection, reasoning ✅ **IMPLEMENTED**
6. **Serialization Cache** - JSON serialization ✅ **IMPLEMENTED**

### What to Cache

**Cache These:**
- Frequently accessed, rarely changed data
- Expensive computations
- External API responses
- User session data
- Configuration data

**Don't Cache These:**
- User-specific, frequently changing data
- Real-time trading data
- Sensitive data (unless encrypted)
- Data that changes on every request

### Cache Key Naming

**Rule:** Use consistent cache key naming

**Format:** `{service}:{entity}:{identifier}:{version}`

**Examples:**
```
user:profile:123:v1
signal:latest:AAPL:v1
config:trading:risk_limits:v1
```

### Cache Invalidation

**Rule:** Implement proper cache invalidation

**Strategies:**
- **TTL (Time To Live):** Automatic expiration
- **Event-based:** Invalidate on data change
- **Version-based:** Include version in key
- **Manual:** Explicit invalidation when needed

**Example:**
```python
from functools import wraps
import redis

redis_client = redis.Redis()

def cache_result(ttl=300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{args}:{kwargs}"
            
            # Try cache first
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # Compute result
            result = await func(*args, **kwargs)
            
            # Cache result
            redis_client.setex(
                cache_key,
                ttl,
                json.dumps(result)
            )
            
            return result
        return wrapper
    return decorator
```

### Cache Warming

**Rule:** Warm caches for critical data

**When to Warm:**
- Application startup
- After cache invalidation
- Scheduled jobs for frequently accessed data

**Example:**
```python
async def warm_cache():
    """Warm cache with frequently accessed data"""
    # Warm user profiles
    active_users = await get_active_users()
    for user in active_users:
        await get_user_profile(user.id)  # Cached
    
    # Warm configuration
    await get_trading_config()  # Cached
```

---

## Async & Concurrency

### Async Operations

**Rule:** Use async for I/O operations

**When to Use Async:**
- Database queries
- External API calls
- File I/O
- Network requests

**Example:**
```python
# BAD ❌ - Synchronous
def fetch_signals():
    signals = db.query(Signal).all()  # Blocks
    return signals

# GOOD ✅ - Async
async def fetch_signals():
    async with async_session() as session:
        result = await session.execute(select(Signal))
        return result.scalars().all()
```

### Concurrency Limits

**Rule:** Limit concurrent operations

**Why:** Prevent resource exhaustion

**Implementation:**
```python
import asyncio

# Limit concurrent API calls
semaphore = asyncio.Semaphore(10)

async def fetch_with_limit(url):
    async with semaphore:
        return await fetch(url)
```

---

## API Optimization

### Request Optimization

**Rule:** Optimize API requests

**Best Practices:**
- Use pagination for large result sets
- Support field selection (sparse fieldsets)
- Use compression (gzip, brotli)
- Batch requests when possible
- Use HTTP/2 for multiplexing

**Example:**
```python
# Support field selection
@router.get("/api/v1/signals")
async def get_signals(fields: str = None):
    query = select(Signal)
    if fields:
        # Only select requested fields
        field_list = fields.split(',')
        query = select(*[getattr(Signal, f) for f in field_list])
    return await session.execute(query)
```

### Response Optimization

**Rule:** Optimize API responses

**Best Practices:**
- Minimize response size
- Use appropriate HTTP status codes
- Include only necessary data
- Use compression
- Set appropriate cache headers

**Cache Headers:**
```python
from fastapi import Response

@router.get("/api/v1/config")
async def get_config(response: Response):
    response.headers["Cache-Control"] = "public, max-age=3600"
    return config_data
```

---

## Frontend Performance

### Code Splitting

**Rule:** Implement code splitting

**Next.js:**
```typescript
// Dynamic imports for large components
const HeavyComponent = dynamic(() => import('./HeavyComponent'), {
  loading: () => <Loading />,
  ssr: false
})
```

### Asset Optimization

**Rule:** Optimize all assets

**Best Practices:**
- Compress images (WebP, AVIF)
- Minify CSS/JavaScript
- Use CDN for static assets
- Lazy load images
- Use appropriate image sizes

### Bundle Size

**Rule:** Monitor and limit bundle size

**Targets:**
- **Initial bundle:** < 200KB (gzipped)
- **Total bundle:** < 500KB (gzipped)
- **Individual chunks:** < 100KB (gzipped)

---

## Cost Optimization

### API Call Optimization

**Rule:** Minimize external API calls

**Strategies:**
- Cache external API responses
- Batch requests when possible
- Use webhooks instead of polling
- Rate limit appropriately

**Example:**
```python
# Cache external API calls
@cache_result(ttl=300)
async def fetch_market_data(symbol: str):
    return await external_api.get_quote(symbol)
```

### Database Cost Optimization

**Rule:** Optimize database usage

**Strategies:**
- Use read replicas for read-heavy workloads
- Archive old data
- Use appropriate instance sizes
- Monitor and optimize slow queries
- Use connection pooling

### Compute Optimization

**Rule:** Optimize compute resources

**Strategies:**
- Use async operations
- Implement proper caching
- Optimize algorithms (avoid O(n²) where possible)
- Use appropriate data structures
- Profile and optimize hot paths

---

## Performance Monitoring

### Metrics to Track

**Rule:** Monitor key performance metrics

**API Metrics:**
- Response time (p50, p95, p99)
- Request rate
- Error rate
- Cache hit rate

**Database Metrics:**
- Query execution time
- Connection pool usage
- Slow query count
- Lock wait time

**Application Metrics:**
- Memory usage
- CPU usage
- Garbage collection (if applicable)
- Thread/process count

### Performance Testing

**Rule:** Test performance regularly

**Types of Tests:**
- **Load Testing:** Normal expected load
- **Stress Testing:** Beyond normal load
- **Spike Testing:** Sudden load increases
- **Endurance Testing:** Sustained load over time

**Tools:**
- Locust (Python)
- k6 (JavaScript)
- Apache Bench (ab)
- wrk

---

## Algorithm Optimization

### Complexity Analysis

**Rule:** Optimize algorithm complexity

**Targets:**
- **Lookups:** O(1) or O(log n)
- **Sorting:** O(n log n)
- **Avoid:** O(n²) where possible

**Example:**
```python
# BAD ❌ - O(n²)
def find_duplicates(items):
    duplicates = []
    for i, item1 in enumerate(items):
        for item2 in items[i+1:]:
            if item1 == item2:
                duplicates.append(item1)
    return duplicates

# GOOD ✅ - O(n)
def find_duplicates(items):
    seen = set()
    duplicates = []
    for item in items:
        if item in seen:
            duplicates.append(item)
        seen.add(item)
    return duplicates
```

---

## Related Rules

- **API Design:** [26_API_DESIGN.md](26_API_DESIGN.md) - API performance requirements
- **Database Migrations:** [27_DATABASE_MIGRATIONS.md](27_DATABASE_MIGRATIONS.md) - Index management
- **Code Quality:** [02_CODE_QUALITY.md](02_CODE_QUALITY.md) - Code optimization
- **Monitoring:** [14_MONITORING_OBSERVABILITY.md](14_MONITORING_OBSERVABILITY.md) - Performance monitoring

---

**Note:** Performance is critical for user experience and cost efficiency. Always profile before optimizing, measure the impact, and monitor continuously. Premature optimization is the root of all evil - optimize based on data, not assumptions.


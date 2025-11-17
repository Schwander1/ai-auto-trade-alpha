# Error Handling & Resilience Rules

**Last Updated:** January 15, 2025  
**Version:** 1.0  
**Applies To:** All projects (Argo Capital, Alpine Analytics LLC)

---

## Overview

Comprehensive error handling standards, resilience patterns, and recovery strategies to ensure reliable, fault-tolerant systems.

**Strategic Context:** Error handling aligns with reliability goals defined in [24_VISION_MISSION_GOALS.md](24_VISION_MISSION_GOALS.md).

**See Also:** [01_DEVELOPMENT.md](01_DEVELOPMENT.md) for basic error handling, [26_API_DESIGN.md](26_API_DESIGN.md) for API error responses.

---

## Error Classification

### Error Types

**Rule:** Classify errors by type and handle appropriately

**1. Transient Errors (Retryable)**
- Network timeouts
- Temporary service unavailability
- Rate limiting (with retry-after)
- Database connection errors

**2. Permanent Errors (Not Retryable)**
- Authentication failures
- Authorization failures
- Validation errors
- Not found errors

**3. User Errors (Client-Side)**
- Invalid input
- Missing required fields
- Out of range values
- Format errors

**4. System Errors (Server-Side)**
- Internal server errors
- Database errors
- External service failures
- Configuration errors

---

## Exception Hierarchy

### Custom Exceptions

**Rule:** Define custom exception hierarchy

**Base Exception:**
```python
class ApplicationError(Exception):
    """Base exception for all application errors"""
    def __init__(self, message: str, code: str = None, details: dict = None):
        self.message = message
        self.code = code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)
```

**Specific Exceptions:**
```python
class ValidationError(ApplicationError):
    """Raised when input validation fails"""
    pass

class NotFoundError(ApplicationError):
    """Raised when resource not found"""
    pass

class AuthenticationError(ApplicationError):
    """Raised when authentication fails"""
    pass

class AuthorizationError(ApplicationError):
    """Raised when authorization fails"""
    pass

class ExternalServiceError(ApplicationError):
    """Raised when external service fails"""
    pass

class DatabaseError(ApplicationError):
    """Raised when database operation fails"""
    pass
```

---

## Error Handling Patterns

### Try-Except Best Practices

**Rule:** Use specific exception types

**BAD ❌:**
```python
try:
    result = process_signal(signal)
except Exception:  # Too broad
    logger.error("Error occurred")
    return None
```

**GOOD ✅:**
```python
try:
    result = process_signal(signal)
except ValidationError as e:
    logger.warning(f"Validation failed: {e.message}", extra={"signal_id": signal.id})
    raise HTTPException(status_code=422, detail=str(e))
except DatabaseError as e:
    logger.error(f"Database error: {e.message}", exc_info=True)
    raise HTTPException(status_code=500, detail="Internal server error")
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
    raise HTTPException(status_code=500, detail="Internal server error")
```

### Never Fail Silently

**Rule:** Always handle errors explicitly

**BAD ❌:**
```python
try:
    execute_trade(signal)
except Exception:
    pass  # Silent failure - BAD!
```

**GOOD ✅:**
```python
try:
    execute_trade(signal)
except TradeExecutionError as e:
    logger.error(f"Trade execution failed: {e}", extra={"signal_id": signal.id})
    # Notify user, retry, or handle appropriately
    raise
```

---

## Retry Strategies

### Exponential Backoff

**Rule:** Use exponential backoff for transient errors

**Implementation:**
```python
import asyncio
from typing import Callable, TypeVar

T = TypeVar('T')

async def retry_with_backoff(
    func: Callable[[], T],
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0
) -> T:
    """Retry function with exponential backoff"""
    delay = initial_delay
    
    for attempt in range(max_retries):
        try:
            return await func()
        except TransientError as e:
            if attempt == max_retries - 1:
                raise
            
            logger.warning(
                f"Transient error (attempt {attempt + 1}/{max_retries}): {e}",
                extra={"delay": delay}
            )
            
            await asyncio.sleep(delay)
            delay = min(delay * backoff_factor, max_delay)
    
    raise Exception("Max retries exceeded")
```

### Retry Decorator

**Rule:** Use retry decorator for common patterns

**Example:**
```python
from functools import wraps
import asyncio

def retry_on_transient_error(max_retries=3, delay=1.0):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except TransientError as e:
                    if attempt == max_retries - 1:
                        raise
                    await asyncio.sleep(delay * (2 ** attempt))
            return None
        return wrapper
    return decorator

@retry_on_transient_error(max_retries=3)
async def fetch_external_data(url: str):
    # Will retry on transient errors
    pass
```

---

## Circuit Breaker Pattern

### Circuit Breaker Implementation

**Rule:** Use circuit breaker for external services

**Purpose:** Prevent cascading failures

**States:**
- **Closed:** Normal operation
- **Open:** Failing, reject requests immediately
- **Half-Open:** Testing if service recovered

**Implementation:**
```python
from enum import Enum
from datetime import datetime, timedelta

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: int = 60,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
    
    def call(self, func, *args, **kwargs):
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise CircuitBreakerOpenError("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise
    
    def _on_success(self):
        self.failure_count = 0
        self.state = CircuitState.CLOSED
    
    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
    
    def _should_attempt_reset(self):
        if self.last_failure_time is None:
            return True
        return datetime.now() - self.last_failure_time > timedelta(seconds=self.timeout)
```

---

## Graceful Degradation

### Degradation Strategies

**Rule:** Implement graceful degradation for non-critical features

**Strategies:**
1. **Return Cached Data:** Use stale cache if service unavailable
2. **Return Default Values:** Use sensible defaults
3. **Disable Feature:** Temporarily disable non-critical features
4. **Queue for Later:** Queue requests for processing later

**Example:**
```python
async def get_signal_with_fallback(signal_id: str):
    try:
        return await signal_service.get_signal(signal_id)
    except ExternalServiceError:
        # Fallback to cache
        cached = await cache.get(f"signal:{signal_id}")
        if cached:
            logger.warning(f"Using cached signal {signal_id}")
            return cached
        
        # Fallback to default
        logger.error(f"Signal {signal_id} unavailable, using default")
        return Signal.default()
```

---

## Error Logging

### Structured Error Logging

**Rule:** Log errors with full context

**Required Context:**
- Error message
- Error type/class
- Stack trace
- Request ID
- User ID (if applicable)
- Relevant data (signal_id, trade_id, etc.)
- Timestamp

**Example:**
```python
import logging
import traceback

logger = logging.getLogger(__name__)

try:
    execute_trade(signal)
except TradeExecutionError as e:
    logger.error(
        f"Trade execution failed: {e.message}",
        extra={
            "error_type": type(e).__name__,
            "error_code": e.code,
            "signal_id": signal.id,
            "symbol": signal.symbol,
            "user_id": signal.user_id,
            "request_id": request.state.request_id,
            "traceback": traceback.format_exc()
        },
        exc_info=True
    )
    raise
```

### Error Monitoring

**Rule:** Monitor and alert on errors

**Metrics to Track:**
- Error rate (errors per minute)
- Error types (by exception class)
- Error frequency (by endpoint/function)
- Error trends (increasing/decreasing)

**Alerting:**
- Critical errors: Immediate alert
- High error rate: Alert if > 1% of requests
- New error types: Alert on first occurrence
- Error spikes: Alert on sudden increases

---

## Error Recovery

### Recovery Procedures

**Rule:** Define recovery procedures for different error types

**Transient Errors:**
1. Retry with exponential backoff
2. If retries fail, queue for later processing
3. Notify monitoring system

**Permanent Errors:**
1. Log error with full context
2. Return appropriate error to user
3. Do not retry
4. Investigate root cause

**System Errors:**
1. Log error with full context
2. Return generic error to user (don't expose internals)
3. Alert operations team
4. Investigate immediately

---

## User-Facing Error Messages

### Error Message Guidelines

**Rule:** Provide clear, actionable error messages

**Requirements:**
- **Clear:** User understands what went wrong
- **Actionable:** User knows what to do
- **Non-Technical:** Avoid technical jargon
- **Helpful:** Include relevant information

**BAD ❌:**
```
Error: 500
Database connection failed
NullPointerException at line 42
```

**GOOD ✅:**
```
We're having trouble processing your request right now. 
Please try again in a few moments. If the problem persists, 
contact support with reference ID: ABC123.
```

### Error Message Examples

**Validation Error:**
```
The signal confidence must be between 0 and 100. 
You entered 150. Please correct this and try again.
```

**Not Found Error:**
```
The signal you're looking for doesn't exist. 
It may have been deleted or the ID is incorrect.
```

**Rate Limit Error:**
```
You've made too many requests. Please wait 60 seconds 
before trying again.
```

---

## Error Handling in APIs

### API Error Responses

**Rule:** Return consistent error responses

**See:** [26_API_DESIGN.md](26_API_DESIGN.md) for API error response format

**Example:**
```python
from fastapi import HTTPException

try:
    signal = await get_signal(signal_id)
except NotFoundError:
    raise HTTPException(
        status_code=404,
        detail={
            "type": "NotFoundError",
            "message": f"Signal {signal_id} not found",
            "code": "SIGNAL_NOT_FOUND"
        }
    )
except ValidationError as e:
    raise HTTPException(
        status_code=422,
        detail={
            "type": "ValidationError",
            "message": e.message,
            "code": e.code,
            "details": e.details
        }
    )
```

---

## Related Rules

- **Development:** [01_DEVELOPMENT.md](01_DEVELOPMENT.md) - Basic error handling
- **API Design:** [26_API_DESIGN.md](26_API_DESIGN.md) - API error responses
- **Security:** [07_SECURITY.md](07_SECURITY.md) - Security error handling
- **Monitoring:** [14_MONITORING_OBSERVABILITY.md](14_MONITORING_OBSERVABILITY.md) - Error monitoring

---

**Note:** Proper error handling is critical for system reliability and user experience. Always handle errors explicitly, log with context, and provide clear feedback to users. Never fail silently.


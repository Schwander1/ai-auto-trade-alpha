# Alpine Analytics LLC Backend Rules

**Last Updated:** January 15, 2025  
**Version:** 3.0  
**Applies To:** Alpine Analytics LLC Backend (Python/FastAPI)

---

## Overview

Backend-specific rules for **Alpine Analytics LLC** backend, focusing on Python, FastAPI, and analytics platform best practices.

**Note:** Alpine Analytics LLC is an **independent entity** with **no relationship** to Argo Capital. This rule applies ONLY to Alpine Analytics LLC.

---

## Code Style

### Python Standards
- **Style Guide:** PEP 8
- **Formatter:** Black (88-100 char line length)
- **Linter:** Ruff, mypy
- **Type Hints:** Required for all functions

### Naming Conventions
- **Functions:** `snake_case` with `verb_noun` pattern (see Rule 01)
- **Classes:** `PascalCase` with `Noun` or `NounVerb` pattern
- **Variables:** `snake_case` with descriptive names
- **Constants:** `UPPER_SNAKE_CASE`

---

## FastAPI Best Practices

**See:** [26_API_DESIGN.md](26_API_DESIGN.md) for comprehensive API design standards, versioning, and documentation requirements.

### Endpoint Structure

```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/signals", tags=["signals"])

class SignalCreate(BaseModel):
    symbol: str
    confidence: float
    entry_price: float

@router.post("/", response_model=SignalResponse)
async def create_signal(
    signal: SignalCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new signal.
    
    - **symbol**: Stock symbol (e.g., "AAPL")
    - **confidence**: Signal confidence (0-100)
    - **entry_price**: Entry price in USD
    """
    try:
        result = await signal_service.create_signal(signal, current_user)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating signal: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

### Response Models
- **Rule:** Always define response models
- **Use:** Pydantic models for validation

---

## Error Handling

**See:** [29_ERROR_HANDLING.md](29_ERROR_HANDLING.md) for comprehensive error handling patterns and resilience strategies.

### Exception Handling
```python
from fastapi import HTTPException

@router.get("/signals/{signal_id}")
async def get_signal(signal_id: str):
    try:
        signal = await signal_service.get_signal(signal_id)
        if not signal:
            raise HTTPException(status_code=404, detail="Signal not found")
        return signal
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error fetching signal {signal_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

---

## Database Operations

### SQLAlchemy Patterns

#### Session Management
```python
from sqlalchemy.orm import Session

def get_signal(db: Session, signal_id: str):
    return db.query(Signal).filter(Signal.id == signal_id).first()

def create_signal(db: Session, signal_data: dict):
    signal = Signal(**signal_data)
    db.add(signal)
    db.commit()
    db.refresh(signal)
    return signal
```

#### Query Optimization
- **Rule:** Avoid N+1 queries
- **Use:** Eager loading with `joinedload` or `selectinload`

### Parameterized Queries
- **Rule:** Always use parameterized queries
- **Never:** Concatenate SQL strings

---

## Async Operations

### Async/Await Pattern
```python
import asyncio
import aiohttp

async def fetch_data(url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()
```

### Database Async
```python
from sqlalchemy.ext.asyncio import AsyncSession

async def get_signal_async(db: AsyncSession, signal_id: str):
    result = await db.execute(
        select(Signal).where(Signal.id == signal_id)
    )
    return result.scalar_one_or_none()
```

---

## Logging

### Structured Logging
```python
import logging

logger = logging.getLogger(__name__)

def log_signal_creation(signal_id: str, user_id: str, symbol: str):
    logger.info(
        "Signal created",
        extra={
            "signal_id": signal_id,
            "user_id": user_id,
            "symbol": symbol,
            "event": "signal_created"
        }
    )
```

### Log Levels
- **DEBUG:** Detailed information for debugging
- **INFO:** General informational messages
- **WARNING:** Warning messages
- **ERROR:** Error messages
- **CRITICAL:** Critical errors

---

## API Security

### Authentication
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        return get_user(user_id)
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
```

### Rate Limiting
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/signals")
@limiter.limit("10/minute")
async def create_signal(request: Request, signal: SignalCreate):
    # Endpoint implementation
    pass
```

---

## Performance Optimization

### Caching
```python
from functools import lru_cache
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

@lru_cache(maxsize=100)
def get_cached_signal(signal_id: str):
    return fetch_signal_from_db(signal_id)

async def get_signal_with_redis(signal_id: str):
    # Try Redis first
    cached = redis_client.get(f"signal:{signal_id}")
    if cached:
        return json.loads(cached)
    
    # Fallback to database
    signal = await get_signal_from_db(signal_id)
    redis_client.setex(
        f"signal:{signal_id}",
        3600,  # 1 hour TTL
        json.dumps(signal)
    )
    return signal
```

### Connection Pooling
```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20
)
```

---

## Testing

### Unit Tests
```python
import pytest
from unittest.mock import Mock, patch

def test_calculate_confidence():
    # Test implementation
    pass
```

### Integration Tests
```python
@pytest.mark.asyncio
async def test_signal_creation_flow(client):
    response = await client.post(
        "/api/signals",
        json={
            "symbol": "AAPL",
            "confidence": 85.0,
            "entry_price": 150.25
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["symbol"] == "AAPL"
```

---

## Related Rules

- [01_DEVELOPMENT.md](01_DEVELOPMENT.md) - Development practices
- [03_TESTING.md](03_TESTING.md) - Testing requirements
- [07_SECURITY.md](07_SECURITY.md) - Security practices
- [14_MONITORING_OBSERVABILITY.md](14_MONITORING_OBSERVABILITY.md) - Monitoring and logging
- [10_MONOREPO.md](10_MONOREPO.md) - Entity separation (Alpine is independent)
- [22_TRADE_SECRET_IP_PROTECTION.md](22_TRADE_SECRET_IP_PROTECTION.md) - IP protection (Alpine has proprietary IP)

---

**Note:** This rule applies ONLY to Alpine Analytics LLC. Argo Capital has separate backend rules (see Rule 12A).


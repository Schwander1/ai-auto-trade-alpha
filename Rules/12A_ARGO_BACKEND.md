# Argo Capital Backend Rules

**Last Updated:** January 15, 2025  
**Version:** 3.0  
**Applies To:** Argo Capital Backend (Python/FastAPI)

---

## Overview

Backend-specific rules for **Argo Capital** trading engine, focusing on Python, FastAPI, and trading system best practices.

**Note:** Argo Capital is an **independent entity** with **no relationship** to Alpine Analytics LLC. This rule applies ONLY to Argo Capital.

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

### Basic Endpoint Structure

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
    Create a new trading signal.
    
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

### Basic Exception Handling
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

### Custom Exceptions
```python
class SignalNotFoundError(Exception):
    """Raised when signal is not found."""
    pass

class InvalidSignalError(Exception):
    """Raised when signal data is invalid."""
    pass
```

---

## Trading System Specifics

### Signal Generation
```python
class SignalGenerationService:
    def __init__(self, consensus_engine: WeightedConsensusEngine):
        self.consensus_engine = consensus_engine
        self.trading_engine = None  # Initialize if auto_execute enabled
    
    async def generate_signal_for_symbol(self, symbol: str) -> Signal:
        # Generate signal using consensus engine
        signal = await self.consensus_engine.generate_signal(symbol)
        
        # Validate signal
        if not self._validate_signal(signal):
            raise InvalidSignalError("Signal validation failed")
        
        # Execute if auto_execute enabled
        if self.trading_engine and signal.confidence >= MIN_CONFIDENCE:
            await self.trading_engine.execute_signal(signal)
        
        return signal
```

### Risk Management
```python
def validate_trade(signal: Signal, account: Account) -> bool:
    # Check confidence threshold
    if signal.confidence < MIN_CONFIDENCE:
        return False
    
    # Check buying power
    required_capital = calculate_position_size(signal, account)
    if required_capital > account.buying_power * 0.95:
        return False
    
    # Check daily loss limit
    if account.daily_loss >= account.equity * DAILY_LOSS_LIMIT_PCT:
        return False
    
    return True
```

---

## Async Operations

### Async/Await Pattern
```python
import asyncio
import aiohttp

async def fetch_market_data(symbol: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.example.com/{symbol}") as response:
            return await response.json()

async def process_multiple_symbols(symbols: list[str]):
    tasks = [fetch_market_data(symbol) for symbol in symbols]
    return await asyncio.gather(*tasks)
```

---

## Logging

### Structured Logging
```python
import logging

logger = logging.getLogger(__name__)

def log_signal_creation(signal_id: str, symbol: str):
    logger.info(
        "Signal created",
        extra={
            "signal_id": signal_id,
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

## Testing

### Unit Tests
```python
import pytest
from unittest.mock import Mock, patch

def test_calculate_position_size():
    balance = 10000.0
    confidence = 80.0
    risk_pct = 0.1
    
    result = calculate_position_size(balance, confidence, risk_pct)
    
    assert result == 800.0

@patch('alpaca.tradeapi.REST')
def test_execute_trade(mock_alpaca):
    mock_alpaca.return_value.submit_order.return_value = {"id": "123"}
    result = execute_trade(signal)
    assert result.order_id == "123"
```

---

## Related Rules

- [01_DEVELOPMENT.md](01_DEVELOPMENT.md) - Development practices
- [03_TESTING.md](03_TESTING.md) - Testing requirements
- [07_SECURITY.md](07_SECURITY.md) - Security practices
- [13_TRADING_OPERATIONS.md](13_TRADING_OPERATIONS.md) - Trading operations
- [14_MONITORING_OBSERVABILITY.md](14_MONITORING_OBSERVABILITY.md) - Monitoring and logging
- [10_MONOREPO.md](10_MONOREPO.md) - Entity separation (Argo is independent)

---

**Note:** This rule applies ONLY to Argo Capital. Alpine Analytics LLC has separate backend rules (see Rule 12B).


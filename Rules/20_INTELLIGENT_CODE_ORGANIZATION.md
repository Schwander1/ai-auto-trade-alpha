# Intelligent Code Organization Rules

**Last Updated:** January 15, 2025  
**Version:** 1.0  
**Applies To:** All code organization and refactoring

---

## Overview

This rule ensures code is organized **intelligently by feature/functionality** rather than by type, making it easy to find, understand, and modify specific capabilities. Code is organized into **feature-based modules** where related functionality lives together, while maintaining clear boundaries and integration points.

**Core Principle:** **Feature-Based Modular Organization** - Organize by what the code does, not by what type of file it is.

**Enforcement:** Code organization is **automatically enforced** - code that doesn't follow organization standards will be flagged and must be reorganized.

**Note:** This rule complements:
- **[09_WORKSPACE.md](09_WORKSPACE.md)** - Workspace organization (this rule focuses on code structure within projects)
- **[10_MONOREPO.md](10_MONOREPO.md)** - Monorepo structure (this rule focuses on internal project organization)
- **[21_DEPENDENCY_IMPACT_ANALYSIS.md](21_DEPENDENCY_IMPACT_ANALYSIS.md)** - Dependency tracking (this rule provides organization standards)

---

## Core Principle: Feature-Based Modular Organization

### Philosophy

**Organize by Feature, Not by Type:**
- ✅ **DO:** Group related functionality together (e.g., all risk management code in `risk_management/`)
- ❌ **DON'T:** Mix unrelated code just because it's the same type (e.g., all `*_manager.py` files together)

**Benefits:**
- **Easy to Find:** "Where's the risk management code?" → `argo/risk_management/`
- **Easy to Understand:** All related code is in one place
- **Easy to Modify:** Changes to a feature are localized
- **Easy to Test:** Tests mirror the code structure
- **Easy to Remove:** Delete a feature = delete a folder

### Automatic Enforcement

**Rule:** Code organization is automatically checked:
- New code MUST be placed in appropriate feature modules
- Code reviews MUST verify organization compliance
- Refactoring MUST follow organization standards
- Violations MUST be corrected before merge

---

## Proposed Directory Structures

### Argo Capital (`argo/`)

```
argo/
├── argo/
│   ├── __init__.py
│   │
│   ├── strategies/                    # All trading strategies
│   │   ├── __init__.py
│   │   ├── base_strategy.py
│   │   ├── momentum/
│   │   ├── mean_reversion/
│   │   ├── ml/
│   │   └── sentiment/
│   │
│   ├── risk_management/               # All risk management code
│   │   ├── __init__.py
│   │   ├── risk_manager.py
│   │   ├── position_sizing.py
│   │   ├── drawdown_monitor.py
│   │   ├── correlation_checker.py
│   │   └── daily_limits.py
│   │
│   ├── data_sources/                  # All data source integrations
│   │   ├── __init__.py
│   │   ├── base_source.py
│   │   ├── massive_source.py
│   │   ├── alpha_vantage_source.py
│   │   ├── xai_grok_source.py
│   │   └── sonar_source.py
│   │
│   ├── trading/                       # All trading execution code
│   │   ├── __init__.py
│   │   ├── paper_trading_engine.py
│   │   ├── order_manager.py
│   │   ├── position_manager.py
│   │   └── execution_handler.py
│   │
│   ├── signal_generation/             # Signal generation logic
│   │   ├── __init__.py
│   │   ├── signal_generation_service.py
│   │   ├── weighted_consensus_engine.py
│   │   ├── regime_detector.py
│   │   └── signal_tracker.py
│   │
│   ├── backtesting/                   # All backtesting code
│   │   ├── __init__.py
│   │   ├── base_backtester.py
│   │   ├── strategy_backtester.py
│   │   ├── profit_backtester.py
│   │   ├── data_manager.py
│   │   ├── optimizer.py
│   │   └── results_storage.py
│   │
│   ├── compliance/                    # Compliance and monitoring
│   │   ├── __init__.py
│   │   ├── signal_logger.py
│   │   ├── integrity_monitor.py
│   │   ├── health_check.py
│   │   └── backup_manager.py
│   │
│   ├── tracking/                      # Performance tracking
│   │   ├── __init__.py
│   │   └── unified_tracker.py
│   │
│   ├── integrations/                  # External integrations
│   │   ├── __init__.py
│   │   └── [external service integrations]
│   │
│   ├── api/                           # API endpoints
│   │   ├── __init__.py
│   │   ├── server.py
│   │   ├── signals.py
│   │   ├── backtest.py
│   │   ├── health.py
│   │   └── metrics.py
│   │
│   ├── core/                          # Core utilities (shared across features)
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── environment.py
│   │   └── exceptions.py
│   │
│   └── ai/                            # AI/ML utilities
│       ├── __init__.py
│       └── explainer.py
│
├── config.json
├── main.py
└── requirements.txt
```

### Alpine Analytics LLC (`alpine-backend/`)

```
alpine-backend/
├── backend/
│   ├── __init__.py
│   │
│   ├── caching/                       # All Redis/caching code
│   │   ├── __init__.py
│   │   ├── cache_manager.py
│   │   ├── redis_client.py
│   │   └── cache_decorators.py
│   │
│   ├── rate_limiting/                 # Rate limiting functionality
│   │   ├── __init__.py
│   │   ├── rate_limiter.py
│   │   └── rate_limit_middleware.py
│   │
│   ├── authentication/                # Authentication & authorization
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── password_validator.py
│   │   ├── totp.py
│   │   ├── token_blacklist.py
│   │   └── account_lockout.py
│   │
│   ├── security/                      # Security utilities
│   │   ├── __init__.py
│   │   ├── security_headers.py
│   │   ├── csrf.py
│   │   ├── input_sanitizer.py
│   │   └── security_logging.py
│   │
│   ├── api/                           # API endpoints
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── signals.py
│   │   ├── payments.py
│   │   └── routes/
│   │
│   ├── models/                        # Database models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── signal.py
│   │   └── notification.py
│   │
│   ├── core/                          # Core utilities (shared)
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── metrics.py
│   │   ├── request_logging.py
│   │   └── response_formatter.py
│   │
│   └── main.py
│
└── requirements.txt
```

---

## Organization Principles

### 1. Feature-Based Organization

**Rule:** Each feature gets its own module/directory.

**Examples:**
- **Risk Management:** All risk-related code in `argo/risk_management/`
- **Strategies:** All strategy code in `argo/strategies/`
- **Caching:** All Redis/cache code in `alpine-backend/backend/caching/`

**Enforcement:**
- New code MUST be placed in appropriate feature module
- Code reviews MUST verify feature-based organization
- Violations MUST be corrected before merge

**Benefits:**
- Easy to find: "Where's risk management?" → `risk_management/`
- Easy to modify: Changes are localized
- Easy to test: Tests mirror structure
- Easy to remove: Delete folder = delete feature

### 2. Clear Module Boundaries

**Rule:** Each module should have a single, clear purpose.

**Module Structure:**
```python
# argo/risk_management/__init__.py
"""
Risk Management Module

Provides risk assessment, position sizing, drawdown monitoring,
and correlation checking for trading operations.
"""

from argo.risk_management.risk_manager import RiskManager
from argo.risk_management.position_sizing import calculate_position_size
from argo.risk_management.drawdown_monitor import DrawdownMonitor

__all__ = [
    'RiskManager',
    'calculate_position_size',
    'DrawdownMonitor',
]
```

**Module Documentation:**
- **Purpose:** What this module does
- **Exports:** What other modules should import
- **Dependencies:** What this module depends on

**Enforcement:**
- Every module MUST have clear purpose
- Every module MUST document exports
- Every module MUST document dependencies

### 3. Proper Import Structure

**Rule:** Use absolute imports, organized by feature.

**Good:**
```python
# In argo/trading/order_manager.py
from argo.risk_management.risk_manager import RiskManager
from argo.strategies.base_strategy import BaseStrategy
from argo.core.config import get_config
```

**Bad:**
```python
# Mixing relative and absolute, unclear structure
from ..risk import RiskManager
from ...strategies import BaseStrategy
import config
```

**Enforcement:**
- All imports MUST use absolute paths
- All imports MUST be organized by feature
- Relative imports MUST be avoided

### 4. Integration Points

**Rule:** Features integrate through well-defined interfaces.

**Example:**
```python
# argo/trading/paper_trading_engine.py
from argo.risk_management import RiskManager
from argo.signal_generation import SignalGenerationService

class PaperTradingEngine:
    def __init__(self):
        self.risk_manager = RiskManager()
        self.signal_service = SignalGenerationService()
    
    def execute_trade(self, signal):
        # Risk check
        if not self.risk_manager.validate(signal, self.portfolio):
            return None
        # Execute trade
        ...
```

**Enforcement:**
- Features MUST integrate through interfaces
- Features MUST NOT directly access internal implementation
- Integration points MUST be documented

---

## Automatic Organization Enforcement

### Code Review Requirements

**Before Accepting Code:**
1. **Verify feature-based organization** - Code in correct feature module?
2. **Verify module boundaries** - Clear purpose and exports?
3. **Verify import structure** - Absolute imports, organized by feature?
4. **Verify integration points** - Well-defined interfaces?

**Rejection Criteria:**
- Code in wrong feature module
- Unclear module purpose
- Relative imports
- Direct access to internal implementation

### Automated Checks

**Rule:** Automated tools MUST verify:
- Code placement in correct feature modules
- Module structure compliance
- Import organization
- Integration point compliance

---

## Finding Code Rules

### Quick Reference

**"Where is X?"**

- **Strategies:** `argo/strategies/`
- **Risk Management:** `argo/risk_management/`
- **Trading Execution:** `argo/trading/`
- **Signal Generation:** `argo/signal_generation/`
- **Data Sources:** `argo/data_sources/`
- **Backtesting:** `argo/backtesting/`
- **Caching (Alpine):** `alpine-backend/backend/caching/`
- **Rate Limiting (Alpine):** `alpine-backend/backend/rate_limiting/`
- **Authentication (Alpine):** `alpine-backend/backend/authentication/`

---

## Import Rules

### Absolute Imports

**Rule:** Always use absolute imports from project root.

**Good:**
```python
from argo.risk_management.risk_manager import RiskManager
from argo.strategies.momentum.momentum_strategy import MomentumStrategy
```

**Bad:**
```python
from ..risk_management import RiskManager  # Relative imports
from risk_manager import RiskManager  # Implicit relative
```

**Enforcement:** Reject code with relative imports.

### Import Organization

**Rule:** Organize imports by:
1. Standard library
2. Third-party packages
3. Project modules (by feature)

**Example:**
```python
# Standard library
import asyncio
from datetime import datetime
from typing import Dict, Optional

# Third-party
import numpy as np
from alpaca.trading.client import TradingClient

# Project modules (by feature)
from argo.risk_management import RiskManager
from argo.strategies import MomentumStrategy
from argo.core.config import get_config
```

**Enforcement:** Imports MUST be organized as specified.

---

## Testing Organization

### Test Structure Mirrors Code Structure

**Rule:** Tests should mirror the code structure.

**Example:**
```
argo/
├── risk_management/
│   ├── risk_manager.py
│   └── position_sizing.py
└── tests/
    └── risk_management/
        ├── test_risk_manager.py
        └── test_position_sizing.py
```

**Enforcement:** Tests MUST mirror code structure.

### Integration Tests

**Rule:** Test feature integrations in `tests/integration/`.

**Example:**
```
tests/
├── unit/
│   ├── risk_management/
│   └── strategies/
└── integration/
    ├── test_trading_risk_integration.py
    └── test_signal_generation_strategies.py
```

**Enforcement:** Integration tests MUST be in `tests/integration/`.

---

## Documentation Rules

### Module Documentation

**Rule:** Each module must document:
- **Purpose:** What it does
- **Usage:** How to use it
- **API:** What to import
- **Examples:** Code examples

**Example:**
```python
"""
Risk Management Module

Provides comprehensive risk management for trading operations.

Usage:
    from argo.risk_management import RiskManager
    
    risk_manager = RiskManager()
    is_valid, reason = risk_manager.validate(signal, portfolio)
    
API:
    - RiskManager: Main risk management class
    - calculate_position_size: Position sizing utilities
    - DrawdownMonitor: Drawdown tracking
"""
```

**Enforcement:** Every module MUST have complete documentation.

---

## Migration Strategy

### Phase 1: Create New Structure (No Breaking Changes)

1. **Create new directories** alongside existing code
2. **Copy files** to new locations (don't move yet)
3. **Update imports** in new locations
4. **Test** that new structure works

### Phase 2: Update Imports (Backward Compatible)

1. **Add compatibility imports** in old locations:
   ```python
   # argo/core/risk_manager.py (old location)
   from argo.risk_management.risk_manager import RiskManager
   # Re-export for backward compatibility
   __all__ = ['RiskManager']
   ```

2. **Update all imports** to use new locations
3. **Test** that everything still works

### Phase 3: Remove Old Structure

1. **Remove old files** after all imports updated
2. **Remove compatibility imports**
3. **Update documentation**
4. **Final testing**

---

## Best Practices

### DO
- ✅ Organize by feature/functionality
- ✅ Keep related code together
- ✅ Use clear module boundaries
- ✅ Document module purpose
- ✅ Use absolute imports
- ✅ Test feature integrations
- ✅ Update documentation

### DON'T
- ❌ Mix unrelated code
- ❌ Create circular dependencies
- ❌ Use relative imports
- ❌ Skip module documentation
- ❌ Break existing functionality
- ❌ Ignore test structure

---

## Related Rules

- [09_WORKSPACE.md](09_WORKSPACE.md) - Workspace organization
- [10_MONOREPO.md](10_MONOREPO.md) - Monorepo structure
- [21_DEPENDENCY_IMPACT_ANALYSIS.md](21_DEPENDENCY_IMPACT_ANALYSIS.md) - Dependency tracking
- [01_DEVELOPMENT.md](01_DEVELOPMENT.md) - Naming conventions (affects organization)

---

**Note:** This rule ensures code is organized intelligently for maintainability, discoverability, and scalability. When in doubt, ask: "Where would I look for this functionality?" and organize accordingly. Code organization is **automatically enforced** - violations must be corrected before merge.


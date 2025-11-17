# Dependency Documentation

**Date:** January 15, 2025  
**Version:** 1.0  
**Status:** Complete

---

## Overview

This document provides comprehensive dependency tracking and impact analysis documentation for the workspace. It maps all module dependencies, integration points, and impact relationships to support safe code changes and refactoring.

**Reference:** `Rules/21_DEPENDENCY_IMPACT_ANALYSIS.md` - Mandatory impact analysis before changes

---

## Argo Capital Dependencies

### Core Module Dependencies

#### `argo/core/signal_generation_service.py`

**Dependencies:**
- `argo.core.signal_tracker` - Signal storage and tracking
- `argo.core.weighted_consensus_engine` - Consensus algorithm
- `argo.core.regime_detector` - Market regime detection
- `argo.ai.explainer` - AI signal explanations
- `argo.core.data_sources.massive_source` - Market data
- `argo.core.data_sources.alpha_vantage_source` - Technical indicators
- `argo.core.data_sources.xai_grok_source` - Sentiment data
- `argo.core.data_sources.sonar_source` - AI analysis
- `argo.core.paper_trading_engine` - Trade execution (optional)
- `argo.core.environment` - Environment detection

**Used By:**
- `argo/main.py` - API server startup
- `argo/scripts/execute_test_trade.py` - Test trades
- `argo/scripts/test_full_system_integration.py` - Integration tests
- `argo/scripts/test_complete_trade_lifecycle.py` - Trade lifecycle tests

**Impact Analysis:**
- **Changing this module affects:** All signal generation, trading execution, API endpoints
- **Breaking changes require:** Update all scripts, API endpoints, tests
- **Configuration dependencies:** `config.json` (strategy, trading sections)

---

#### `argo/core/weighted_consensus_engine.py`

**Dependencies:**
- `config.json` - Strategy weights, trading parameters
- Standard library only (no other code dependencies)

**Used By:**
- `argo.core.signal_generation_service` - Signal generation
- `argo.backtest.strategy_backtester` - Backtesting

**Impact Analysis:**
- **Changing this module affects:** Signal quality, consensus calculation, backtesting
- **Breaking changes require:** Update signal generation service, backtesters
- **Configuration dependencies:** `config.json` (strategy section)

**Trade Secret:** ✅ Marked as proprietary algorithm

---

#### `argo/core/paper_trading_engine.py`

**Dependencies:**
- `argo.core.environment` - Environment detection
- `argo.core.risk.risk_manager` - Risk validation (if imported)
- Alpaca API (external)

**Used By:**
- `argo.core.signal_generation_service` - Trade execution
- `argo/scripts/execute_test_trade.py` - Test trades
- `argo/scripts/verify_trading_system.py` - System verification
- `argo/scripts/test_full_system_integration.py` - Integration tests

**Impact Analysis:**
- **Changing this module affects:** All trade execution, position management
- **Breaking changes require:** Update signal generation service, all scripts
- **Configuration dependencies:** `config.json` (alpaca section), AWS Secrets Manager

---

#### `argo/core/regime_detector.py`

**Dependencies:**
- Standard library only

**Used By:**
- `argo.core.signal_generation_service` - Confidence adjustment

**Impact Analysis:**
- **Changing this module affects:** Signal confidence, signal quality
- **Breaking changes require:** Update signal generation service

---

#### `argo/core/data_sources/`

**Dependencies:**
- External APIs (Massive.com, Alpha Vantage, X API, Sonar AI)
- `config.json` - API keys and configuration

**Used By:**
- `argo.core.signal_generation_service` - Data collection

**Impact Analysis:**
- **Changing these modules affects:** Data availability, signal generation
- **Breaking changes require:** Update signal generation service
- **Configuration dependencies:** `config.json` (data source sections)

---

#### `argo/risk/risk_manager.py`

**Dependencies:**
- `argo.core.paper_trading_engine` - Account details
- `config.json` - Risk parameters

**Used By:**
- `argo.core.paper_trading_engine` - Risk validation (if integrated)
- `argo.core.signal_generation_service` - Risk checks (if integrated)

**Impact Analysis:**
- **Changing this module affects:** Risk validation, position sizing, trade execution
- **Breaking changes require:** Update trading engine, signal generation
- **Configuration dependencies:** `config.json` (trading section)

---

#### `argo/backtest/`

**Dependencies:**
- `argo.core.weighted_consensus_engine` - Consensus algorithm
- `argo.core.signal_generation_service` - Signal generation
- Historical data sources

**Used By:**
- Backtesting scripts
- Strategy optimization scripts

**Impact Analysis:**
- **Changing these modules affects:** Backtesting accuracy, strategy optimization
- **Breaking changes require:** Update all backtesting scripts
- **Configuration dependencies:** `config.json` (backtest section)

---

#### `argo/api/`

**Dependencies:**
- `argo.core.signal_generation_service` - Signal data
- `argo.core.paper_trading_engine` - Trading data
- FastAPI framework

**Used By:**
- `argo/main.py` - API server
- External clients (Alpine Analytics, etc.)

**Impact Analysis:**
- **Changing these modules affects:** API responses, external integrations
- **Breaking changes require:** Update external clients, API documentation
- **No configuration dependencies** (uses service layer)

---

### Configuration Dependencies

#### `config.json`

**Structure:**
```json
{
  "massive": { "api_key": "...", "enabled": true },
  "alpha_vantage": { "api_key": "...", "enabled": true },
  "x_api": { "bearer_token": "...", "enabled": true },
  "sonar": { "api_key": "...", "enabled": true },
  "alpaca": {
    "dev": { "api_key": "...", "secret_key": "..." },
    "production": { "api_key": "...", "secret_key": "..." }
  },
  "strategy": {
    "weight_massive": 0.4,
    "weight_alpha_vantage": 0.25,
    "weight_x_sentiment": 0.2,
    "weight_sonar": 0.15
  },
  "trading": {
    "min_confidence": 75.0,
    "auto_execute": true,
    "position_size_pct": 10,
    "max_drawdown_pct": 10
  },
  "backtest": { ... }
}
```

**Used By:**
- `argo.core.weighted_consensus_engine` - Strategy weights
- `argo.core.signal_generation_service` - Trading parameters
- `argo.core.paper_trading_engine` - Alpaca credentials
- `argo.core.data_sources.*` - API keys
- `argo.risk.risk_manager` - Risk parameters
- `argo.backtest.*` - Backtest parameters

**Impact Analysis:**
- **Changing config structure affects:** All modules that read config
- **Breaking changes require:** Update all config readers, migration script
- **Environment-specific:** Dev vs production configs

---

## Alpine Analytics LLC Dependencies

### Backend Module Dependencies

#### `backend/api/external_signal_sync.py`

**Dependencies:**
- `backend.core.database` - Database access
- `backend.core.config` - Configuration
- `backend.models.signal` - Signal model
- External signal provider API (business integration)

**Used By:**
- `backend/main.py` - API router registration

**Impact Analysis:**
- **Changing this module affects:** External signal provider integration
- **Breaking changes require:** Update external signal provider client
- **Configuration dependencies:** `EXTERNAL_SIGNAL_API_KEY` (AWS Secrets Manager)

---

#### `backend/core/cache.py`

**Dependencies:**
- Redis (external service)
- Standard library

**Used By:**
- API endpoints (caching)
- Signal distribution (caching)

**Impact Analysis:**
- **Changing this module affects:** Cache performance, API response times
- **Breaking changes require:** Update all cache users

---

#### `backend/core/rate_limit.py`

**Dependencies:**
- Redis (external service)
- FastAPI middleware

**Used By:**
- `backend/main.py` - Middleware registration

**Impact Analysis:**
- **Changing this module affects:** Rate limiting behavior, API security
- **Breaking changes require:** Update middleware registration

---

#### `backend/auth/`

**Dependencies:**
- `backend.core.database` - User data
- `backend.models.user` - User model
- JWT libraries

**Used By:**
- `backend/api/auth.py` - Authentication endpoints
- `backend/api/auth_2fa.py` - 2FA endpoints
- All protected API endpoints

**Impact Analysis:**
- **Changing these modules affects:** All authentication, authorization
- **Breaking changes require:** Update all API endpoints, frontend

---

### Frontend Dependencies

#### `alpine-frontend/lib/api.ts`

**Dependencies:**
- External signal provider API (business integration)
- TypeScript types

**Used By:**
- `alpine-frontend/hooks/useSignals.ts` - Signal fetching
- Frontend components

**Impact Analysis:**
- **Changing this module affects:** All frontend API calls
- **Breaking changes require:** Update all API callers, components

---

## Cross-Entity Dependencies

### Business Integration (API Only)

**Alpine Analytics → External Signal Provider:**
- **Type:** External API integration (business relationship)
- **Implementation:** `backend/api/external_signal_sync.py`
- **No code dependencies:** Pure API integration
- **Separation:** Complete - no shared code, no cross-references

**Impact Analysis:**
- **Changing integration affects:** Signal distribution to Alpine customers
- **Breaking changes require:** Update external signal provider client
- **No code dependencies:** Safe to change independently

---

## Dependency Graphs

### Argo Capital Signal Generation Flow

```
config.json
    ↓
weighted_consensus_engine.py
    ↓
data_sources/*.py
    ↓
signal_generation_service.py
    ↓
paper_trading_engine.py
    ↓
risk_manager.py (optional)
    ↓
signal_tracker.py
```

### Alpine Analytics Signal Distribution Flow

```
External Signal Provider API
    ↓
external_signal_sync.py
    ↓
database.py
    ↓
models/signal.py
    ↓
api/signals.py
    ↓
Frontend (api.ts)
```

---

## Impact Analysis Checklist

### Before Making Changes

- [ ] Identify all direct dependencies (imports)
- [ ] Identify all indirect dependencies (used by)
- [ ] Identify configuration dependencies
- [ ] Identify environment-specific impacts
- [ ] Review SystemDocs for context
- [ ] Document impact analysis

### During Changes

- [ ] Update all affected imports
- [ ] Update all affected function calls
- [ ] Update all affected configurations
- [ ] Update all affected tests
- [ ] Update all affected documentation

### After Changes

- [ ] Verify all dependencies still work
- [ ] Run tests for all affected components
- [ ] Update SystemDocs if architecture changed
- [ ] Update this dependency documentation
- [ ] Document what changed and why

---

## Quick Reference: Finding Dependencies

### Find All Imports of a Module

```bash
# Find all files importing a module
grep -r "from argo.core.signal_generation_service" argo/
grep -r "import.*SignalGenerationService" argo/
```

### Find All Usages of a Function

```bash
# Find all usages of a function
grep -r "calculate_consensus" argo/
grep -r "generate_signal" argo/
```

### Find Configuration Dependencies

```bash
# Find all config readers
grep -r "config.get\|config\['" argo/
grep -r "self.config" argo/
```

---

## Related Documentation

- `Rules/21_DEPENDENCY_IMPACT_ANALYSIS.md` - Impact analysis process
- `Rules/20_INTELLIGENT_CODE_ORGANIZATION.md` - Code organization (affects dependencies)
- `docs/SystemDocs/COMPLETE_SYSTEM_ARCHITECTURE.md` - System architecture

---

**Last Updated:** January 15, 2025  
**Version:** 1.0

**Note:** This documentation must be updated whenever dependencies change. Impact analysis is mandatory before making changes (Rule 21).


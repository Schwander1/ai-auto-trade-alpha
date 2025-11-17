# Code Organization Plan

**Date:** January 15, 2025  
**Version:** 1.0  
**Status:** Implementation Plan

---

## Overview

This document outlines the plan for implementing feature-based code organization according to `Rules/20_INTELLIGENT_CODE_ORGANIZATION.md`. The migration will be done in phases to ensure no breaking changes.

**Reference:** `Rules/20_INTELLIGENT_CODE_ORGANIZATION.md` - Intelligent code organization rules

---

## Current Structure

### Argo Capital

```
argo/argo/
├── core/                    # Mixed: signal generation, trading, data sources
├── risk/                    # Risk management (already organized)
├── backtest/                # Backtesting (already organized)
├── strategies/              # Strategies (already organized)
├── api/                     # API endpoints (already organized)
├── compliance/              # Compliance (already organized)
├── tracking/                # Tracking (already organized)
└── ai/                      # AI utilities (already organized)
```

### Alpine Analytics LLC

```
alpine-backend/backend/
├── core/                    # Mixed: config, database, caching, rate limiting, security
├── api/                     # API endpoints (already organized)
├── auth/                    # Authentication (already organized)
├── models/                  # Models (already organized)
└── migrations/              # Migrations (already organized)
```

---

## Target Structure (Feature-Based)

### Argo Capital

```
argo/argo/
├── strategies/              # ✅ Already organized
├── risk_management/         # ⚠️  Move from risk/
├── data_sources/            # ⚠️  Move from core/data_sources/
├── trading/                 # ⚠️  Move paper_trading_engine from core/
├── signal_generation/       # ⚠️  Move signal generation from core/
├── backtesting/             # ✅ Already organized
├── compliance/              # ✅ Already organized
├── tracking/                # ✅ Already organized
├── integrations/            # ✅ Already organized
├── api/                     # ✅ Already organized
├── core/                    # ⚠️  Keep only shared utilities (config, environment, exceptions)
└── ai/                      # ✅ Already organized
```

### Alpine Analytics LLC

```
alpine-backend/backend/
├── caching/                 # ⚠️  Move from core/cache.py, core/rate_limit.py
├── rate_limiting/           # ⚠️  Move from core/rate_limit.py
├── authentication/          # ✅ Already organized (auth/)
├── security/                # ⚠️  Move security utilities from core/
├── api/                     # ✅ Already organized
├── models/                  # ✅ Already organized
├── core/                    # ⚠️  Keep only shared utilities (config, database, metrics)
└── migrations/              # ✅ Already organized
```

---

## Migration Strategy

### Phase 1: Create New Structure (No Breaking Changes)

**Step 1:** Create new directories alongside existing code
**Step 2:** Copy files to new locations (don't move yet)
**Step 3:** Add compatibility imports in old locations
**Step 4:** Test that new structure works

### Phase 2: Update Imports (Backward Compatible)

**Step 1:** Update all imports to use new locations
**Step 2:** Keep compatibility imports in old locations
**Step 3:** Test that everything still works

### Phase 3: Remove Old Structure

**Step 1:** Remove old files after all imports updated
**Step 2:** Remove compatibility imports
**Step 3:** Update documentation
**Step 4:** Final testing

---

## Compatibility Import Pattern

### Example: Moving `paper_trading_engine.py`

**Old Location:** `argo/core/paper_trading_engine.py`
**New Location:** `argo/trading/paper_trading_engine.py`

**Compatibility Import (in old location):**
```python
# argo/core/paper_trading_engine.py (backward compatibility)
"""
DEPRECATED: This file is maintained for backward compatibility.
New code should import from argo.trading.paper_trading_engine
"""
from argo.trading.paper_trading_engine import PaperTradingEngine

# Re-export for backward compatibility
__all__ = ['PaperTradingEngine']
```

---

## Implementation Priority

### High Priority (Most Impact)

1. **Signal Generation** (`core/` → `signal_generation/`)
   - High usage, affects many components
   - Create compatibility layer

2. **Trading** (`core/paper_trading_engine.py` → `trading/`)
   - High usage, affects signal generation
   - Create compatibility layer

3. **Data Sources** (`core/data_sources/` → `data_sources/`)
   - High usage, affects signal generation
   - Create compatibility layer

### Medium Priority

4. **Risk Management** (`risk/` → `risk_management/`)
   - Already somewhat organized
   - Lower impact

5. **Alpine Caching** (`core/cache.py` → `caching/`)
   - Moderate usage
   - Create compatibility layer

6. **Alpine Security** (`core/security*.py` → `security/`)
   - Moderate usage
   - Create compatibility layer

### Low Priority (Already Organized)

- `backtest/` - Already organized
- `strategies/` - Already organized
- `api/` - Already organized
- `compliance/` - Already organized
- `tracking/` - Already organized

---

## Testing Strategy

### After Each Phase

1. **Import Tests:** Verify all imports work
2. **Integration Tests:** Run full system tests
3. **Health Checks:** Verify 100% health
4. **Backward Compatibility:** Verify old imports still work

### Test Commands

```bash
# Test imports
python -c "from argo.core.paper_trading_engine import PaperTradingEngine"
python -c "from argo.trading.paper_trading_engine import PaperTradingEngine"

# Run health checks
python argo/scripts/health_check_unified.py --level 3

# Run integration tests
python argo/scripts/test_full_system_integration.py
```

---

## Rollback Plan

### If Issues Occur

1. **Keep compatibility imports** - Old imports still work
2. **Revert new structure** - Remove new directories
3. **Restore old files** - From git history
4. **Test thoroughly** - Verify system works

---

## Benefits

### Before Migration

- Mixed organization (some organized, some not)
- Hard to find related code
- Unclear module boundaries

### After Migration

- **Feature-based organization** - Easy to find code
- **Clear module boundaries** - Each module has single purpose
- **Better maintainability** - Changes localized to features
- **Easier testing** - Tests mirror code structure
- **Backward compatible** - Old imports still work during migration

---

## Next Steps

1. **Start with High Priority:** Signal generation, trading, data sources
2. **Create compatibility layers:** Ensure no breaking changes
3. **Test thoroughly:** Verify everything works
4. **Update documentation:** Reflect new structure
5. **Gradually migrate:** Move to new structure over time

---

## Related Documentation

- `Rules/20_INTELLIGENT_CODE_ORGANIZATION.md` - Organization rules
- `Rules/21_DEPENDENCY_IMPACT_ANALYSIS.md` - Impact analysis
- `docs/SystemDocs/DEPENDENCY_DOCUMENTATION.md` - Dependency tracking

---

**Last Updated:** January 15, 2025  
**Version:** 1.0

**Note:** This is an implementation plan. Actual migration will be done gradually to ensure no breaking changes.


# Trading Environment UI Review & Troubleshooting

**Date:** 2025-01-27  
**Issue:** User not seeing Dev, Production, or Prop Firm trading environment indicators in UI

---

## Executive Summary

The system has comprehensive backend support for three trading environments:
1. **Development** - Uses `alpaca.dev` account
2. **Production** - Uses `alpaca.production` account  
3. **Prop Firm** - Uses `prop_firm_test` account (when enabled)

However, **there is NO frontend UI component** to display or select these trading environments. The backend logic exists but is not exposed to users through the Alpine frontend.

---

## Current System Architecture

### Backend (Argo) - ✅ Working

#### Environment Detection
- **Location:** `argo/argo/core/environment.py`
- **Function:** `detect_environment()` automatically detects dev/prod
- **Priority Order:**
  1. `ARGO_ENVIRONMENT` env var
  2. File path: `/root/argo-production/config.json`
  3. Working directory contains `/root/argo-production`
  4. Hostname contains "production" or "prod"
  5. Default: `development`

#### Account Selection
- **Location:** `argo/argo/core/paper_trading_engine.py`
- **Logic:** Automatically selects account based on:
  - `prop_firm.enabled = true` → Uses `prop_firm_test` account
  - Environment = `production` → Uses `alpaca.production` account
  - Environment = `development` → Uses `alpaca.dev` account

#### Prop Firm Mode
- **Location:** `argo/argo/core/signal_generation_service.py`
- **Configuration:** `config.json` → `prop_firm.enabled`
- **Behavior:** When enabled, uses separate account and risk limits

### Frontend (Alpine) - ❌ Missing

#### Current State
- **Dashboard:** `alpine-frontend/app/dashboard/page.tsx` - No environment indicator
- **Navigation:** `alpine-frontend/components/dashboard/Navigation.tsx` - No environment selector
- **User Menu:** `alpine-frontend/components/dashboard/UserMenu.tsx` - No environment info
- **No API Integration:** No frontend code fetches trading environment status

#### Missing Components
1. ❌ Trading environment status API endpoint (Alpine backend)
2. ❌ Trading environment status API endpoint (Argo backend)
3. ❌ Frontend component to display current environment
4. ❌ Frontend component to switch environments (if needed)
5. ❌ Integration with dashboard/navigation

---

## Root Cause Analysis

### Primary Issue: Missing API Endpoints

**Argo Backend:**
- ✅ Has environment detection logic
- ✅ Has account selection logic
- ❌ **NO API endpoint** to expose environment/account status
- ❌ Health endpoint doesn't include trading environment info

**Alpine Backend:**
- ✅ Has health check endpoint
- ❌ **NO endpoint** to query Argo for trading environment
- ❌ **NO endpoint** to expose trading environment to frontend

### Secondary Issue: Missing UI Components

**Frontend:**
- ❌ No component to fetch trading environment status
- ❌ No component to display current environment
- ❌ No visual indicator in dashboard/navigation
- ❌ No way for users to see which account is active

---

## Detailed Troubleshooting

### 1. Backend API Gaps

#### Argo API Missing Endpoint
**Current:** `/api/v1/health` doesn't include trading environment
**Needed:** `/api/v1/trading/status` or `/api/v1/account/status`

**Required Information:**
```json
{
  "environment": "development" | "production",
  "trading_mode": "dev" | "production" | "prop_firm",
  "account_name": "Dev Trading Account",
  "account_number": "...",
  "portfolio_value": 100000.00,
  "buying_power": 100000.00,
  "prop_firm_enabled": false,
  "alpaca_connected": true
}
```

#### Alpine Backend Missing Endpoint
**Current:** No proxy/endpoint to Argo trading status
**Needed:** `/api/v1/trading/status` that queries Argo

### 2. Frontend Integration Gaps

#### Missing Data Fetching
- No React hook to fetch trading environment
- No API client method for trading status
- No state management for environment info

#### Missing UI Components
- No `TradingEnvironmentBadge` component
- No `TradingEnvironmentSelector` component (if switching needed)
- No integration in Navigation or Dashboard

### 3. Configuration Visibility

**Current:** Users cannot see:
- Which environment is active (dev/prod)
- Which account is being used
- Whether prop firm mode is enabled
- Account balance/status

**Impact:** Users have no visibility into trading configuration

---

## Solution Implementation Plan

### Phase 1: Backend API Endpoints

#### Step 1.1: Create Argo Trading Status Endpoint
**File:** `argo/argo/api/trading.py` (new file)
**Endpoint:** `GET /api/v1/trading/status`
**Returns:** Environment, account, prop firm status

#### Step 1.2: Update Argo Health Endpoint
**File:** `argo/argo/api/health.py`
**Add:** Trading environment info to health response

#### Step 1.3: Create Alpine Trading Status Endpoint
**File:** `alpine-backend/backend/api/trading.py` (new file)
**Endpoint:** `GET /api/v1/trading/status`
**Behavior:** Queries Argo API and returns trading status

### Phase 2: Frontend Components

#### Step 2.1: Create Trading Environment Hook
**File:** `alpine-frontend/hooks/useTradingEnvironment.ts` (new file)
**Purpose:** Fetch and manage trading environment state

#### Step 2.2: Create Trading Environment Badge Component
**File:** `alpine-frontend/components/dashboard/TradingEnvironmentBadge.tsx` (new file)
**Purpose:** Display current environment with visual indicator

#### Step 2.3: Integrate into Navigation
**File:** `alpine-frontend/components/dashboard/Navigation.tsx`
**Add:** TradingEnvironmentBadge component

#### Step 2.4: Integrate into Dashboard
**File:** `alpine-frontend/app/dashboard/page.tsx`
**Add:** Trading environment status card/section

### Phase 3: Testing & Validation

#### Step 3.1: Test Backend Endpoints
- Verify Argo endpoint returns correct environment
- Verify Alpine endpoint proxies correctly
- Test with prop firm enabled/disabled

#### Step 3.2: Test Frontend Display
- Verify badge shows correct environment
- Verify updates when environment changes
- Test error handling

---

## Implementation Details

### Argo Trading Status Endpoint

```python
# argo/argo/api/trading.py
from fastapi import APIRouter
from argo.core.paper_trading_engine import PaperTradingEngine
from argo.core.environment import detect_environment
import json
from pathlib import Path

router = APIRouter(prefix="/api/v1/trading", tags=["trading"])

@router.get("/status")
async def get_trading_status():
    """Get current trading environment and account status"""
    environment = detect_environment()
    
    # Load config to check prop firm
    config_path = Path("/root/argo-production/config.json") if environment == "production" else Path("config.json")
    prop_firm_enabled = False
    if config_path.exists():
        with open(config_path) as f:
            config = json.load(f)
            prop_firm_config = config.get('prop_firm', {})
            prop_firm_enabled = prop_firm_config.get('enabled', False)
    
    # Get trading engine info
    engine = PaperTradingEngine()
    
    if engine.alpaca_enabled:
        account = engine.get_account_details()
        return {
            "environment": environment,
            "trading_mode": "prop_firm" if prop_firm_enabled else environment,
            "account_name": engine.account_name,
            "account_number": account.get("account_number"),
            "portfolio_value": account.get("portfolio_value", 0),
            "buying_power": account.get("buying_power", 0),
            "prop_firm_enabled": prop_firm_enabled,
            "alpaca_connected": True
        }
    else:
        return {
            "environment": environment,
            "trading_mode": "simulation",
            "account_name": None,
            "prop_firm_enabled": prop_firm_enabled,
            "alpaca_connected": False
        }
```

### Alpine Trading Status Endpoint

```python
# alpine-backend/backend/api/trading.py
from fastapi import APIRouter, HTTPException
from backend.core.config import settings
import httpx

router = APIRouter(prefix="/api/v1/trading", tags=["trading"])

@router.get("/status")
async def get_trading_status():
    """Get trading environment status from Argo"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"{settings.EXTERNAL_SIGNAL_API_URL}/api/v1/trading/status",
                headers={"X-API-Key": settings.EXTERNAL_SIGNAL_API_KEY}
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Failed to fetch trading status: {str(e)}")
```

### Frontend Hook

```typescript
// alpine-frontend/hooks/useTradingEnvironment.ts
import { useState, useEffect } from 'react'

interface TradingEnvironment {
  environment: 'development' | 'production'
  trading_mode: 'dev' | 'production' | 'prop_firm' | 'simulation'
  account_name: string | null
  account_number?: string
  portfolio_value?: number
  buying_power?: number
  prop_firm_enabled: boolean
  alpaca_connected: boolean
}

export function useTradingEnvironment() {
  const [status, setStatus] = useState<TradingEnvironment | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        setLoading(true)
        const response = await fetch('/api/v1/trading/status')
        if (!response.ok) throw new Error('Failed to fetch trading status')
        const data = await response.json()
        setStatus(data)
        setError(null)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error')
        setStatus(null)
      } finally {
        setLoading(false)
      }
    }

    fetchStatus()
    const interval = setInterval(fetchStatus, 30000) // Refresh every 30s
    return () => clearInterval(interval)
  }, [])

  return { status, loading, error }
}
```

### Frontend Badge Component

```typescript
// alpine-frontend/components/dashboard/TradingEnvironmentBadge.tsx
'use client'

import { useTradingEnvironment } from '@/hooks/useTradingEnvironment'
import { Loader2, Building2, Code, Factory, AlertCircle } from 'lucide-react'

export default function TradingEnvironmentBadge() {
  const { status, loading, error } = useTradingEnvironment()

  if (loading) {
    return (
      <div className="flex items-center gap-2 px-3 py-1.5 bg-alpine-black-secondary rounded-lg">
        <Loader2 className="w-4 h-4 animate-spin text-alpine-text-secondary" />
        <span className="text-sm text-alpine-text-secondary">Loading...</span>
      </div>
    )
  }

  if (error || !status) {
    return (
      <div className="flex items-center gap-2 px-3 py-1.5 bg-alpine-semantic-error/10 border border-alpine-semantic-error/30 rounded-lg">
        <AlertCircle className="w-4 h-4 text-alpine-semantic-error" />
        <span className="text-sm text-alpine-semantic-error">Status unavailable</span>
      </div>
    )
  }

  const getModeConfig = () => {
    if (status.trading_mode === 'prop_firm') {
      return {
        label: 'Prop Firm',
        icon: Building2,
        color: 'text-alpine-neon-purple',
        bg: 'bg-alpine-neon-purple/10',
        border: 'border-alpine-neon-purple/30'
      }
    } else if (status.trading_mode === 'production') {
      return {
        label: 'Production',
        icon: Factory,
        color: 'text-alpine-neon-cyan',
        bg: 'bg-alpine-neon-cyan/10',
        border: 'border-alpine-neon-cyan/30'
      }
    } else if (status.trading_mode === 'dev') {
      return {
        label: 'Dev',
        icon: Code,
        color: 'text-alpine-neon-pink',
        bg: 'bg-alpine-neon-pink/10',
        border: 'border-alpine-neon-pink/30'
      }
    } else {
      return {
        label: 'Simulation',
        icon: AlertCircle,
        color: 'text-alpine-text-secondary',
        bg: 'bg-alpine-black-secondary',
        border: 'border-alpine-black-border'
      }
    }
  }

  const config = getModeConfig()
  const Icon = config.icon

  return (
    <div className={`flex items-center gap-2 px-3 py-1.5 ${config.bg} border ${config.border} rounded-lg`}>
      <Icon className={`w-4 h-4 ${config.color}`} />
      <span className={`text-sm font-semibold ${config.color}`}>
        {config.label}
      </span>
      {status.account_name && (
        <span className="text-xs text-alpine-text-secondary">
          {status.account_name}
        </span>
      )}
    </div>
  )
}
```

---

## Testing Checklist

### Backend Testing
- [ ] Argo `/api/v1/trading/status` returns correct environment
- [ ] Argo endpoint works with prop firm enabled
- [ ] Argo endpoint works with prop firm disabled
- [ ] Alpine `/api/v1/trading/status` proxies correctly
- [ ] Error handling works when Argo is unavailable

### Frontend Testing
- [ ] Badge displays correct environment
- [ ] Badge updates on environment change
- [ ] Loading state displays correctly
- [ ] Error state displays correctly
- [ ] Badge integrates into Navigation
- [ ] Badge integrates into Dashboard

### Integration Testing
- [ ] Full flow: Argo → Alpine → Frontend
- [ ] Real-time updates work
- [ ] Multiple users see correct status
- [ ] Performance is acceptable

---

## Priority & Timeline

### High Priority (Immediate)
1. Create Argo trading status endpoint
2. Create Alpine trading status endpoint
3. Create frontend badge component
4. Integrate into Navigation

### Medium Priority (This Week)
5. Add to Dashboard page
6. Add error handling
7. Add loading states
8. Test all scenarios

### Low Priority (Future)
9. Add environment switching (if needed)
10. Add detailed account info modal
11. Add environment history/logging

---

## Related Files

### Backend
- `argo/argo/core/environment.py` - Environment detection
- `argo/argo/core/paper_trading_engine.py` - Account selection
- `argo/argo/core/signal_generation_service.py` - Prop firm mode
- `argo/argo/api/health.py` - Health endpoint (needs update)
- `alpine-backend/backend/main.py` - Alpine API

### Frontend
- `alpine-frontend/app/dashboard/page.tsx` - Dashboard page
- `alpine-frontend/components/dashboard/Navigation.tsx` - Navigation
- `alpine-frontend/components/dashboard/UserMenu.tsx` - User menu
- `alpine-frontend/hooks/useSignals.ts` - Example hook pattern

### Configuration
- `argo/config.json` - Prop firm configuration
- `Rules/16_DEV_PROD_DIFFERENCES.md` - Environment rules
- `Rules/13_TRADING_OPERATIONS.md` - Trading operations rules

---

## Conclusion

The trading environment system is fully functional on the backend but completely invisible to users. The solution requires:

1. **Backend:** 2 new API endpoints (Argo + Alpine)
2. **Frontend:** 1 hook + 1 component + 2 integrations
3. **Testing:** Comprehensive testing of all scenarios

**Estimated Implementation Time:** 4-6 hours

**Impact:** High - Users will finally see which trading environment is active, improving transparency and trust.


# Argo Production Signal Generation & Storage Audit

**Date:** 2025-01-27  
**Status:** ⚠️ **CRITICAL ISSUE FOUND**

## Executive Summary

Signal generation in Argo production is **working correctly**, but **signal sync to Alpine backend is MISSING**. Signals are being generated and stored locally in Argo's SQLite database, but they are not being sent to Alpine backend for storage in the production PostgreSQL database.

---

## ✅ What's Working

### 1. Signal Generation Service
- **Location:** `argo/argo/core/signal_generation_service.py`
- **Status:** ✅ **WORKING**
- **Details:**
  - Background service runs every 5 seconds
  - Uses Weighted Consensus v6.0 algorithm
  - Generates signals for multiple symbols (AAPL, NVDA, TSLA, MSFT, BTC-USD, ETH-USD)
  - Includes AI-generated reasoning
  - SHA-256 verification hash generation
  - Confidence threshold: 88% (with regime-based adaptation)

### 2. Signal Storage in Argo
- **Location:** `argo/argo/core/signal_tracker.py`
- **Status:** ✅ **WORKING**
- **Details:**
  - Signals stored in SQLite: `argo/data/signals.db`
  - Batch insert optimization (50 signals per batch)
  - Connection pooling enabled
  - WAL mode for better concurrency
  - Audit trail logging to `argo/logs/signals.log`
  - SHA-256 hash verification

### 3. Alpine Backend Endpoint
- **Location:** `alpine-backend/backend/api/argo_sync.py`
- **Status:** ✅ **READY**
- **Details:**
  - Endpoint: `POST /api/v1/external-signals/sync/signal`
  - Authentication: X-API-Key header
  - Hash verification
  - Duplicate detection
  - Stores signals in PostgreSQL database

---

## ❌ Critical Issue: Missing Signal Sync

### Problem
**Argo does not send generated signals to Alpine backend.** Signals are generated and stored locally in Argo's SQLite database, but there is no code that:
1. Reads signals from Argo's database
2. Sends HTTP POST requests to Alpine backend
3. Handles sync failures or retries

### Evidence
1. **No sync code found** in `signal_generation_service.py` or `signal_tracker.py`
2. **No HTTP client code** for sending signals to Alpine
3. **Documentation exists** (`ARGO_ALPINE_SYNC_ARCHITECTURE.md`) but implementation is missing
4. **Alpine endpoint is ready** but not being called

### Impact
- Signals are generated but not available in Alpine production database
- Frontend cannot display signals from Alpine backend
- Users cannot access signals through Alpine application
- Signal history is only in Argo's local SQLite database

---

## Configuration Analysis

### Production Configuration

**Alpine Backend (docker-compose.production.yml):**
```yaml
EXTERNAL_SIGNAL_API_URL=http://178.156.194.174:8000  # Argo server
```

**Expected Argo Configuration (MISSING):**
- `ALPINE_API_URL`: Should be `http://91.98.153.49:8001` (Alpine backend)
- `ARGO_API_KEY`: API key for Alpine authentication
- Endpoint: `/api/v1/external-signals/sync/signal`

### Current Signal Flow (Broken)

```
Argo Signal Generation
    ↓
SignalTracker.log_signal()
    ↓
SQLite Database (argo/data/signals.db) ✅
    ↓
[MISSING: Sync to Alpine] ❌
    ↓
Alpine Backend (Not receiving signals) ❌
```

### Expected Signal Flow

```
Argo Signal Generation
    ↓
SignalTracker.log_signal()
    ↓
SQLite Database (argo/data/signals.db) ✅
    ↓
Alpine Sync Service (NEW - NEEDS IMPLEMENTATION)
    ↓
HTTP POST to Alpine Backend ✅
    ↓
Alpine PostgreSQL Database ✅
```

---

## Recommendations

### Immediate Action Required

1. **Implement Signal Sync Service**
   - Create `argo/argo/core/alpine_sync.py`
   - Send signals to Alpine backend after generation
   - Handle retries and error recovery
   - Use async HTTP client (httpx or aiohttp)

2. **Add Configuration**
   - Add `ALPINE_API_URL` environment variable
   - Add `ARGO_API_KEY` for authentication
   - Configure sync interval (real-time or batch)

3. **Integration Points**
   - Hook into `SignalTracker.log_signal()` to trigger sync
   - Or add sync in `SignalGenerationService.generate_signals_cycle()`
   - Use background task for async sync

4. **Error Handling**
   - Retry logic for failed syncs
   - Queue failed signals for retry
   - Logging and monitoring

### Implementation Priority

**HIGH PRIORITY** - This is blocking signal availability in production.

---

## Code Locations

### Signal Generation
- **Service:** `argo/argo/core/signal_generation_service.py` (line 1688-1823)
- **Storage:** `argo/argo/core/signal_tracker.py` (line 189-245)

### Alpine Backend
- **Endpoint:** `alpine-backend/backend/api/argo_sync.py` (line 97-217)
- **Model:** `alpine-backend/backend/models/signal.py`

### Documentation
- **Architecture:** `archive/docs/SystemDocs/v3.0/ARGO_ALPINE_SYNC_ARCHITECTURE.md`

---

## Testing Checklist

Once sync is implemented, verify:

- [ ] Signals are generated in Argo
- [ ] Signals are stored in Argo SQLite
- [ ] Signals are sent to Alpine backend
- [ ] Signals are stored in Alpine PostgreSQL
- [ ] Duplicate signals are handled correctly
- [ ] Hash verification works
- [ ] API authentication works
- [ ] Error handling and retries work
- [ ] Monitoring and logging are in place

---

## Next Steps

1. **Create Alpine Sync Service** (see implementation plan below)
2. **Add configuration** for Alpine API URL and API key
3. **Integrate sync** into signal generation flow
4. **Test end-to-end** signal flow
5. **Monitor** sync success rate and errors

---

## Implementation Plan

### Step 1: Create Alpine Sync Service

Create `argo/argo/core/alpine_sync.py`:

```python
import httpx
import logging
import os
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class AlpineSyncService:
    """Sync signals from Argo to Alpine backend"""
    
    def __init__(self):
        self.alpine_url = os.getenv('ALPINE_API_URL', 'http://91.98.153.49:8001')
        self.api_key = os.getenv('ARGO_API_KEY', '')
        self.endpoint = f"{self.alpine_url}/api/v1/external-signals/sync/signal"
        self.client = httpx.AsyncClient(timeout=10.0)
    
    async def sync_signal(self, signal: Dict) -> bool:
        """Send signal to Alpine backend"""
        try:
            payload = {
                "signal_id": signal.get('signal_id'),
                "symbol": signal.get('symbol'),
                "action": signal.get('action'),
                "entry_price": signal.get('entry_price'),
                "target_price": signal.get('target_price'),
                "stop_price": signal.get('stop_price'),
                "confidence": signal.get('confidence'),
                "strategy": signal.get('strategy', 'weighted_consensus_v6'),
                "timestamp": signal.get('timestamp', datetime.utcnow().isoformat()),
                "sha256": signal.get('sha256'),
                "reasoning": signal.get('reasoning', '')
            }
            
            headers = {
                "X-API-Key": self.api_key,
                "Content-Type": "application/json"
            }
            
            response = await self.client.post(
                self.endpoint,
                json=payload,
                headers=headers
            )
            
            if response.status_code == 201:
                logger.info(f"✅ Signal synced to Alpine: {signal.get('signal_id')}")
                return True
            else:
                logger.error(f"❌ Failed to sync signal: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error syncing signal to Alpine: {e}")
            return False
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
```

### Step 2: Integrate into Signal Generation

Modify `signal_generation_service.py`:

```python
# In __init__:
from argo.core.alpine_sync import AlpineSyncService
self.alpine_sync = AlpineSyncService()

# In generate_signals_cycle(), after storing signal:
if signal:
    # Store signal in database
    signal_id = self.tracker.log_signal(signal)
    signal['signal_id'] = signal_id
    
    # Sync to Alpine backend
    await self.alpine_sync.sync_signal(signal)
```

### Step 3: Add Configuration

Add to production environment:
```bash
ALPINE_API_URL=http://91.98.153.49:8001
ARGO_API_KEY=<shared-secret-key>
```

---

## Conclusion

Signal generation and local storage are working correctly. However, **the critical missing piece is the sync service that sends signals from Argo to Alpine backend**. This must be implemented immediately to enable signal availability in production.


# Argo Capital → Alpine Analytics Signal Sync Architecture

**Date:** November 13, 2025  
**Version:** 1.0  
**Status:** Implementation Complete

---

## Executive Summary

This document describes the secure, API-based signal synchronization architecture between **Argo Capital** (signal producer) and **Alpine Analytics LLC** (signal consumer). The architecture maintains complete entity separation with no direct database access between the two companies.

---

## Entity Separation Requirements

### Argo Capital
- **Role:** Signal producer
- **Responsibility:** Generate trading signals using Weighted Consensus v6.0
- **Database:** Own SQLite database (internal use only)
- **Access:** No access to Alpine's database

### Alpine Analytics LLC
- **Role:** Signal consumer and distributor
- **Responsibility:** Receive, store, and distribute signals to subscribers
- **Database:** Own PostgreSQL database (customer-facing)
- **Access:** No access to Argo's database

### Separation Principle
- **No direct database connections** between entities
- **API-based communication only**
- **Secure authentication required**
- **Complete audit trail**

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    ARGO CAPITAL                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Signal Generation Service (every 5 seconds)         │  │
│  │  - Weighted Consensus v6.0                           │  │
│  │  - Real data sources (Massive, Alpha Vantage, etc.)  │  │
│  │  - SHA-256 verification                              │  │
│  └──────────────────────────────────────────────────────┘  │
│                          │                                   │
│                          │ Store in SQLite                   │
│                          ▼                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  SignalTracker                                       │  │
│  │  - SQLite database (argo/data/signals.db)            │  │
│  │  - Immutable log files                               │  │
│  └──────────────────────────────────────────────────────┘  │
│                          │                                   │
│                          │ Sync via API                      │
│                          ▼                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  AlpineBackendSync                                   │  │
│  │  - HTTP POST to Alpine API                           │  │
│  │  - X-API-Key authentication                          │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                          │
                          │ HTTPS + API Key
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                 ALPINE ANALYTICS LLC                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  /api/v1/argo/sync/signal                            │  │
│  │  - Verify API key (HMAC)                             │  │
│  │  - Verify SHA-256 hash                               │  │
│  │  - Prevent duplicates                                │  │
│  └──────────────────────────────────────────────────────┘  │
│                          │                                   │
│                          │ Store in PostgreSQL               │
│                          ▼                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  PostgreSQL Database                                 │  │
│  │  - signals table                                     │  │
│  │  - verification_hash (unique)                        │  │
│  │  - Complete audit trail                              │  │
│  └──────────────────────────────────────────────────────┘  │
│                          │                                   │
│                          │ Serve to subscribers              │
│                          ▼                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  User-Facing API                                     │  │
│  │  - /api/v1/signals/subscribed                        │  │
│  │  - Tier-based filtering                              │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## Security Architecture

### Authentication

**Method:** API Key (HMAC-verified)

**Flow:**
1. Argo generates signal and stores in SQLite
2. Argo sends signal to Alpine API with `X-API-Key` header
3. Alpine verifies API key using `hmac.compare_digest()` (constant-time)
4. Alpine verifies SHA-256 hash of signal data
5. Alpine stores signal in PostgreSQL

**API Key Storage:**
- **Argo:** `argo-alpine/argo/argo-api-key` (AWS Secrets Manager)
- **Alpine:** `argo-alpine/alpine-backend/argo-api-key` (AWS Secrets Manager)
- Same key used by both (shared secret)

### Data Integrity

**SHA-256 Verification:**
- Every signal includes SHA-256 hash
- Alpine verifies hash before storing
- Prevents tampering during transmission
- Immutable audit trail

**Duplicate Prevention:**
- Alpine checks `verification_hash` before storing
- Prevents duplicate signals
- Idempotent API design

---

## API Endpoints

### Alpine Backend: Receive Signal

**Endpoint:** `POST /api/v1/argo/sync/signal`

**Authentication:** `X-API-Key` header

**Request Body:**
```json
{
  "signal_id": "SIG-1234567890",
  "symbol": "AAPL",
  "action": "BUY",
  "entry_price": 175.50,
  "target_price": 184.25,
  "stop_price": 171.00,
  "confidence": 95.5,
  "strategy": "weighted_consensus_v6",
  "timestamp": "2025-11-13T15:00:00Z",
  "sha256": "abc123...",
  "reasoning": "AI-generated explanation..."
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Signal stored successfully",
  "signal_id": 42,
  "alpine_signal_id": 42,
  "argo_signal_id": "SIG-1234567890"
}
```

**Error Responses:**
- `401`: Invalid API key
- `400`: Hash verification failed
- `409`: Signal already exists (duplicate)
- `500`: Server error

### Alpine Backend: Health Check

**Endpoint:** `GET /api/v1/argo/sync/health`

**Response:**
```json
{
  "status": "healthy",
  "service": "Alpine Analytics - Argo Sync",
  "endpoint": "/api/v1/argo/sync/signal"
}
```

---

## Configuration

### Argo Configuration

**AWS Secrets Manager:**
- `argo-alpine/argo/argo-api-key`: API key for Alpine authentication
- `argo-alpine/argo/alpine-api-url`: Alpine Backend API URL

**Environment Variables (fallback):**
- `ARGO_API_KEY`: API key
- `ALPINE_API_URL`: Alpine API URL (default: `http://localhost:9001`)

### Alpine Configuration

**AWS Secrets Manager:**
- `argo-alpine/alpine-backend/argo-api-key`: API key to verify Argo requests

**Environment Variables (fallback):**
- `ARGO_API_KEY`: API key

---

## Signal Flow

### 1. Signal Generation (Argo)

```python
# Argo generates signal
signal = {
    'symbol': 'AAPL',
    'action': 'BUY',
    'entry_price': 175.50,
    'confidence': 95.5,
    # ... other fields
}

# Store in Argo SQLite
signal_id = tracker.log_signal(signal)
# → Stored in argo/data/signals.db
# → Logged to argo/logs/signals.log
```

### 2. Signal Sync (Argo → Alpine)

```python
# Argo syncs to Alpine via API
alpine_sync = get_alpine_sync()
alpine_sync.sync_signal(signal)
# → POST to Alpine API
# → X-API-Key header included
# → SHA-256 hash verified
```

### 3. Signal Storage (Alpine)

```python
# Alpine receives and stores
@app.post("/api/v1/argo/sync/signal")
async def receive_signal(signal_data, api_key):
    # Verify API key
    verify_argo_api_key(api_key)
    
    # Verify SHA-256 hash
    verify_hash(signal_data)
    
    # Store in PostgreSQL
    signal = Signal(...)
    db.add(signal)
    db.commit()
```

---

## Benefits of API-Based Architecture

### 1. Entity Separation
- ✅ No direct database access between entities
- ✅ Clear API contract
- ✅ Independent scaling
- ✅ Separate security perimeters

### 2. Security
- ✅ API key authentication
- ✅ SHA-256 verification
- ✅ HTTPS encryption
- ✅ Rate limiting (future)

### 3. Reliability
- ✅ Idempotent API (duplicate prevention)
- ✅ Error handling and retries
- ✅ Audit trail
- ✅ Health checks

### 4. Maintainability
- ✅ Clear separation of concerns
- ✅ Independent deployments
- ✅ Versioned API
- ✅ Monitoring and logging

---

## Setup Instructions

### 1. Generate API Key

```bash
# Generate secure 64-character API key
openssl rand -hex 32
```

### 2. Add to AWS Secrets Manager

**For Alpine Backend:**
```bash
aws secretsmanager create-secret \
    --name "argo-alpine/alpine-backend/argo-api-key" \
    --secret-string "YOUR_API_KEY"
```

**For Argo:**
```bash
aws secretsmanager create-secret \
    --name "argo-alpine/argo/argo-api-key" \
    --secret-string "YOUR_API_KEY"

aws secretsmanager create-secret \
    --name "argo-alpine/argo/alpine-api-url" \
    --secret-string "http://91.98.153.49:8001"
```

### 3. Or Use Setup Script

```bash
./scripts/setup-argo-alpine-sync.sh
```

### 4. Restart Services

**Alpine Backend:**
```bash
# Will automatically load ARGO_API_KEY from AWS Secrets Manager
systemctl restart alpine-backend
```

**Argo:**
```bash
# Will automatically load ARGO_API_KEY and ALPINE_API_URL
systemctl restart argo
```

---

## Monitoring

### Argo Logs

Look for:
- `✅ Signal synced to Alpine: AAPL BUY`
- `❌ Alpine API error: ...`

### Alpine Logs

Look for:
- `✅ Signal synced from Argo: AAPL BUY (42)`
- `❌ Error storing signal from Argo: ...`

### Health Checks

**Alpine Sync Health:**
```bash
curl http://localhost:9001/api/v1/argo/sync/health
```

**Argo Sync Status:**
Check Argo logs for sync initialization:
- `✅ Alpine Backend API sync initialized`

---

## Troubleshooting

### Signals Not Syncing

1. **Check API Key:**
   ```bash
   # Verify key exists in AWS Secrets Manager
   aws secretsmanager get-secret-value --secret-id "argo-alpine/argo/argo-api-key"
   ```

2. **Check Alpine API URL:**
   ```bash
   # Verify URL is correct
   aws secretsmanager get-secret-value --secret-id "argo-alpine/argo/alpine-api-url"
   ```

3. **Check Alpine Backend:**
   ```bash
   # Verify endpoint is accessible
   curl http://localhost:9001/api/v1/argo/sync/health
   ```

4. **Check Argo Logs:**
   ```bash
   # Look for sync errors
   tail -f /tmp/argo.log | grep -i "alpine\|sync"
   ```

### Authentication Errors

- Verify API key matches in both services
- Check `X-API-Key` header is being sent
- Verify `hmac.compare_digest()` is working

### Hash Verification Failures

- Verify signal data matches hash
- Check timestamp format
- Ensure all required fields are present

---

## Compliance & Audit

### Audit Trail

**Argo Side:**
- SQLite database with all signals
- Immutable log files
- SHA-256 hashes

**Alpine Side:**
- PostgreSQL database with all signals
- `verification_hash` for integrity
- Timestamps for all operations

### Data Retention

- **Argo:** 7+ years (SQLite + S3 backups)
- **Alpine:** 7+ years (PostgreSQL + backups)
- Both maintain independent audit trails

---

## Future Enhancements

1. **Rate Limiting:** Add rate limits to Alpine API
2. **Webhooks:** Real-time notifications for new signals
3. **Retry Logic:** Automatic retry on sync failures
4. **Metrics:** Prometheus metrics for sync operations
5. **Encryption:** End-to-end encryption for signal data

---

## Conclusion

The API-based sync architecture maintains complete separation between Argo Capital and Alpine Analytics LLC while providing secure, reliable signal synchronization. All signals are stored permanently in both databases with full audit trails and cryptographic verification.

---

**Document Version:** 1.0  
**Last Updated:** November 13, 2025  
**Status:** ✅ Implementation Complete


# Alpine Sync Configuration Guide

## Overview

The Alpine sync service sends signals from Argo to Alpine backend for storage in the production PostgreSQL database. This document describes how to configure the sync service.

## Configuration Sources

The sync service checks configuration in the following order:

1. **Environment Variables** (highest priority)
2. **AWS Secrets Manager**
3. **config.json** file
4. **Default values** (fallback)

## Required Configuration

### Environment Variables

Add these to your production environment (`.env` file or systemd service):

```bash
# Alpine Backend API URL
ALPINE_API_URL=http://91.98.153.49:8001

# API Key for Alpine authentication (shared secret)
ARGO_API_KEY=your-secure-api-key-here

# Enable/disable sync (optional, default: true)
ALPINE_SYNC_ENABLED=true
```

### AWS Secrets Manager

For production, store secrets in AWS Secrets Manager:

**Secret Path:** `argo-alpine/argo/argo-api-key`
- Contains the API key for Alpine authentication

**Secret Path:** `argo-alpine/argo/alpine-api-url` (optional)
- Contains the Alpine backend URL (if different from default)

### config.json

Add to `argo/config.json`:

```json
{
  "alpine": {
    "api_url": "http://91.98.153.49:8001",
    "api_key": "your-secure-api-key-here",
    "sync_enabled": true
  }
}
```

## Production Setup

### Step 1: Generate API Key

Generate a secure API key (shared between Argo and Alpine):

```bash
# Generate 32-byte hex key
openssl rand -hex 32
```

### Step 2: Configure Argo

**Option A: Environment Variables**

Create/update `/root/argo-production/.env`:

```bash
ALPINE_API_URL=http://91.98.153.49:8001
ARGO_API_KEY=<generated-key>
ALPINE_SYNC_ENABLED=true
```

**Option B: AWS Secrets Manager**

Store in AWS Secrets Manager:
- `argo-alpine/argo/argo-api-key`: `<generated-key>`
- `argo-alpine/argo/alpine-api-url`: `http://91.98.153.49:8001`

### Step 3: Configure Alpine Backend

The Alpine backend must have the same API key configured.

**Environment Variable:**
```bash
EXTERNAL_SIGNAL_API_KEY=<same-generated-key>
```

Or in AWS Secrets Manager:
- `argo-alpine/alpine-backend/argo-api-key`: `<same-generated-key>`

### Step 4: Verify Configuration

Check that sync is enabled:

```bash
# Check Argo logs
tail -f /root/argo-production/logs/*.log | grep -i alpine

# Should see:
# ✅ Alpine sync service initialized: http://91.98.153.49:8001
```

## Verification

### Health Check

The sync service automatically checks Alpine backend health on startup. Check logs for:

```
✅ Alpine backend health check passed
```

### Test Signal Sync

1. Generate a test signal in Argo
2. Check Argo logs for sync confirmation:
   ```
   ✅ Signal synced to Alpine: <signal_id> (AAPL BUY)
   ```
3. Check Alpine backend logs:
   ```
   ✅ Signal synced from external provider: AAPL BUY (<id>)
   ```
4. Verify in Alpine database:
   ```sql
   SELECT * FROM signals ORDER BY created_at DESC LIMIT 5;
   ```

## Troubleshooting

### Sync Not Working

**Check 1: Configuration**
```bash
# Verify environment variables are set
env | grep ALPINE
env | grep ARGO_API_KEY
```

**Check 2: Network Connectivity**
```bash
# Test Alpine backend reachability
curl http://91.98.153.49:8001/api/v1/external-signals/sync/health
```

**Check 3: Authentication**
```bash
# Test with API key
curl -H "X-API-Key: <your-key>" \
     http://91.98.153.49:8001/api/v1/external-signals/sync/health
```

**Check 4: Logs**
```bash
# Check for errors
tail -f /root/argo-production/logs/*.log | grep -i "alpine\|sync\|error"
```

### Common Issues

**Issue: "Alpine sync disabled (missing configuration)"**
- **Solution:** Set `ALPINE_API_URL` and `ARGO_API_KEY` environment variables

**Issue: "Authentication failed - check ARGO_API_KEY"**
- **Solution:** Verify API key matches between Argo and Alpine backend

**Issue: "Connection error - Alpine backend unreachable"**
- **Solution:** Check network connectivity and Alpine backend is running

**Issue: "Timeout syncing signal"**
- **Solution:** Check Alpine backend performance and network latency

## Disabling Sync

To disable sync (for testing or maintenance):

```bash
# Set environment variable
export ALPINE_SYNC_ENABLED=false

# Or in .env file
ALPINE_SYNC_ENABLED=false
```

When disabled, signals are still generated and stored in Argo's SQLite database, but not sent to Alpine backend.

## Monitoring

### Metrics

Monitor sync success rate in logs:
- Look for `✅ Signal synced to Alpine` (success)
- Look for `❌ Failed to sync signal` (failure)

### Log Patterns

**Success:**
```
✅ Signal synced to Alpine: <signal_id> (<symbol> <action>)
```

**Failure:**
```
❌ Failed to sync signal: HTTP <code> - <error>
❌ Error syncing signal to Alpine: <error>
```

**Retry:**
```
🔄 Retrying <n> failed signals
```

## Security Notes

1. **API Key Security:**
   - Use strong, randomly generated keys (32+ bytes)
   - Store in AWS Secrets Manager for production
   - Never commit keys to version control

2. **Network Security:**
   - Use HTTPS in production (when available)
   - Consider VPN or private network for Argo-Alpine communication
   - Firewall rules to restrict access

3. **Authentication:**
   - API key is validated on every request
   - Failed authentication attempts are logged
   - Consider rate limiting for security

## Production Checklist

- [ ] API key generated and stored securely
- [ ] `ALPINE_API_URL` configured in Argo
- [ ] `ARGO_API_KEY` configured in Argo
- [ ] Same API key configured in Alpine backend
- [ ] Network connectivity verified
- [ ] Health check passing
- [ ] Test signal sync successful
- [ ] Monitoring and logging configured
- [ ] Error handling verified


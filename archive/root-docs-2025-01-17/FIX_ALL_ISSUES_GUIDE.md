# 🔧 Fix All Production Issues - Complete Guide

**Date:** 2025-01-15  
**Status:** ✅ Fix Scripts Created  
**Purpose:** Comprehensive guide to fix all identified production issues

---

## Issues Identified

1. **API Key Problems:**
   - xAI Grok API key invalid
   - Massive API key invalid

2. **Alpine Backend Service:**
   - Service down or unhealthy
   - Sync endpoint returning 404

3. **Service Restart:**
   - Argo service may need restart after API key updates

---

## Quick Fix: Automated Script

### Option 1: Fix All Issues Automatically

Run the comprehensive fix script:

```bash
./scripts/fix_all_production_issues.sh
```

This script will:
1. ✅ Check all current issues
2. ✅ Prompt for API key updates (xAI Grok, Massive)
3. ✅ Check and restart Alpine backend
4. ✅ Restart Argo service if needed
5. ✅ Verify all fixes

### Option 2: Fix Issues Individually

#### Fix API Keys Only

```bash
./scripts/update_production_api_keys.sh
```

#### Check Alpine Backend Only

```bash
./scripts/check_alpine_backend.sh
```

---

## Manual Fix Instructions

### 1. Fix API Keys

#### Get API Keys

**xAI Grok API Key:**
- Source: https://console.x.ai
- Format: `xai-...`
- Required for: Sentiment analysis

**Massive API Key:**
- Source: https://massive.com
- Format: Alphanumeric string
- Required for: Market data

#### Update API Keys

**Method 1: Using Update Script**
```bash
./scripts/update_production_api_keys.sh
```

**Method 2: Manual Update**
```bash
# SSH to production server
ssh root@178.156.194.174

# Edit config file (find active environment)
nano /root/argo-production-blue/config.json
# or
nano /root/argo-production-green/config.json

# Add/update API keys:
{
  "xai": {
    "api_key": "your-xai-key-here",
    "enabled": true
  },
  "massive": {
    "api_key": "your-massive-key-here",
    "enabled": true
  }
}

# Restart service
systemctl restart argo-trading.service
```

### 2. Fix Alpine Backend

#### Check Status

```bash
# Check health
curl http://91.98.153.49:8001/api/v1/health

# Check sync endpoint
curl http://91.98.153.49:8001/api/v1/external-signals/sync/health
```

#### Restart Service

**Method 1: Using Check Script**
```bash
./scripts/check_alpine_backend.sh
```

**Method 2: Manual Restart**
```bash
# SSH to Alpine server
ssh root@91.98.153.49

# Find docker-compose file
find /root -name "docker-compose.production.yml"

# Navigate to directory
cd /root/alpine-production  # or wherever the file is

# Restart services
docker compose -f docker-compose.production.yml restart
# or
docker-compose -f docker-compose.production.yml restart

# Verify
curl http://localhost:8001/api/v1/health
curl http://localhost:8001/api/v1/external-signals/sync/health
```

### 3. Restart Argo Service

After updating API keys, restart the Argo service:

```bash
# SSH to production server
ssh root@178.156.194.174

# Restart service
systemctl restart argo-trading.service

# Check status
systemctl status argo-trading.service

# Monitor logs
tail -f /tmp/argo-blue.log
```

---

## Verification

### Verify API Keys

```bash
# Check for API key errors in logs
ssh root@178.156.194.174 "tail -n 100 /tmp/argo-blue.log | grep -E 'xAI API error|Massive API error'"

# Should see no errors (or reduced errors)
```

### Verify Alpine Backend

```bash
# Check health
curl http://91.98.153.49:8001/api/v1/health
# Expected: HTTP 200 with JSON response

# Check sync endpoint
curl http://91.98.153.49:8001/api/v1/external-signals/sync/health
# Expected: HTTP 200
```

### Verify Argo Service

```bash
# Check service status
ssh root@178.156.194.174 "systemctl status argo-trading.service"

# Check latest signals
curl http://178.156.194.174:8000/api/signals/latest?limit=5

# Monitor logs
ssh root@178.156.194.174 "tail -f /tmp/argo-blue.log | grep -E 'Generated signal|Order|ERROR'"
```

---

## Troubleshooting

### API Keys Still Not Working

1. **Verify keys are correct:**
   - Test xAI key: `curl -H "Authorization: Bearer YOUR_KEY" https://api.x.ai/v1/models`
   - Test Massive key: `curl "https://api.massive.com/v2/aggs/ticker/AAPL/range/1/day/2023-01-01/2023-01-02?apiKey=YOUR_KEY"`

2. **Check config file location:**
   - Find active environment: `ssh root@178.156.194.174 "ls -la /root/argo-production-*/config.json"`

3. **Verify service restarted:**
   - Check service logs: `ssh root@178.156.194.174 "journalctl -u argo-trading.service -n 50"`

### Alpine Backend Still Down

1. **Check containers:**
   ```bash
   ssh root@91.98.153.49 "docker ps -a | grep alpine"
   ```

2. **Check logs:**
   ```bash
   ssh root@91.98.153.49 "docker logs alpine-backend-1 --tail 50"
   ```

3. **Check docker-compose file:**
   ```bash
   ssh root@91.98.153.49 "find /root -name 'docker-compose.production.yml'"
   ```

4. **Try full restart:**
   ```bash
   ssh root@91.98.153.49 "cd /root/alpine-production && docker compose -f docker-compose.production.yml down && docker compose -f docker-compose.production.yml up -d"
   ```

### Argo Service Won't Start

1. **Check service logs:**
   ```bash
   ssh root@178.156.194.174 "journalctl -u argo-trading.service -n 100"
   ```

2. **Check application logs:**
   ```bash
   ssh root@178.156.194.174 "tail -n 100 /tmp/argo-blue.log"
   ```

3. **Verify config file:**
   ```bash
   ssh root@178.156.194.174 "python3 -m json.tool /root/argo-production-blue/config.json | head -50"
   ```

---

## Expected Results

After fixing all issues:

### ✅ API Keys
- No API key errors in logs
- xAI Grok sentiment analysis working
- Massive market data available

### ✅ Alpine Backend
- Health endpoint: HTTP 200
- Sync endpoint: HTTP 200
- Containers running

### ✅ Argo Service
- Service running
- Signals generating
- Trades executing (if enabled)

---

## Monitoring

### Continuous Monitoring

```bash
# Monitor production trading
./scripts/monitor_production_trading.sh

# View logs
./commands/lib/view-logs-production.sh follow argo

# Health check
./commands/lib/health-check-production.sh
```

### Check Status

```bash
# Quick status check
./scripts/fix_all_production_issues.sh
# (Will show current status without making changes if you skip prompts)
```

---

## Summary

### Automated Fix
```bash
./scripts/fix_all_production_issues.sh
```

### Manual Steps
1. Update API keys in config.json
2. Restart Argo service
3. Restart Alpine backend
4. Verify all services

### Verification
- Check logs for errors
- Test API endpoints
- Monitor signal generation

---

**Status:** ✅ All fix scripts created and ready to use

**Next Steps:**
1. Run `./scripts/fix_all_production_issues.sh`
2. Follow prompts to update API keys
3. Verify all services are working
4. Monitor logs for any remaining issues


# Tradervue Enhanced Integration - Setup Guide

**Date:** 2025-01-XX  
**Status:** Ready for Configuration

---

## Quick Start

### 1. Verify Installation

Run the setup verification script:

```bash
cd argo
bash scripts/verify_tradervue_setup.sh
```

### 2. Configure Credentials

Choose one of the following methods:

#### Option A: Environment Variables (Recommended for Development)

```bash
export TRADERVUE_USERNAME=your_username
export TRADERVUE_PASSWORD=your_password
```

#### Option B: AWS Secrets Manager (Recommended for Production)

```bash
# Using AWS CLI
aws secretsmanager create-secret \
  --name argo-capital/argo/tradervue-username \
  --secret-string "your_username" \
  --description "Tradervue Gold username"

aws secretsmanager create-secret \
  --name argo-capital/argo/tradervue-password \
  --secret-string "your_password" \
  --description "Tradervue Gold password"
```

### 3. Test Integration

Run the test script:

```bash
cd argo
python3 scripts/test_tradervue_integration.py
```

### 4. Start API Server

```bash
cd argo
python3 -m uvicorn argo.api.server:app --reload --host 0.0.0.0 --port 8000
```

### 5. Test API Endpoints

```bash
# Check status
curl http://localhost:8000/api/v1/tradervue/status

# Get widget URL
curl http://localhost:8000/api/v1/tradervue/widget-url

# Get profile URL
curl http://localhost:8000/api/v1/tradervue/profile-url

# Get metrics (requires trades in Tradervue)
curl http://localhost:8000/api/v1/tradervue/metrics?days=30

# Manual sync
curl -X POST http://localhost:8000/api/v1/tradervue/sync?days=30
```

---

## Getting Tradervue Account Credentials

1. **Log in to Tradervue:**
   - Go to https://www.tradervue.com
   - Log in to your account

2. **Get Account Credentials:**
   - Your **username** is your Tradervue login username
   - Your **password** is your Tradervue login password
   - Tradervue uses HTTP Basic Authentication with your account credentials

3. **Verify Gold Subscription:**
   - Ensure you have Tradervue Gold subscription
   - API access requires Gold subscription

---

## Configuration Methods

### Method 1: Environment Variables

**Pros:**
- Simple for development
- No AWS dependencies
- Easy to test

**Cons:**
- Not secure for production
- Must be set in each environment

**Usage:**
```bash
export TRADERVUE_USERNAME=your_username
export TRADERVUE_PASSWORD=your_password
```

### Method 2: AWS Secrets Manager

**Pros:**
- Secure for production
- Centralized configuration
- Automatic rotation support

**Cons:**
- Requires AWS access
- More complex setup

**Secret Names:**
- `argo-capital/argo/tradervue-username`
- `argo-capital/argo/tradervue-password`

**Backward Compatibility:**
- Also checks `argo-alpine/argo/tradervue-username`
- Also checks `argo-alpine/argo/tradervue-password`

---

## Verification Steps

### Step 1: Check Configuration

```bash
cd argo
python3 -c "
from argo.integrations.tradervue_client import get_tradervue_client
client = get_tradervue_client()
print(f'Enabled: {client.enabled}')
print(f'Username: {client.username if client.enabled else \"Not configured\"}')
"
```

Expected output:
```
Enabled: True
Username: your_username
```

### Step 2: Test Integration

```bash
python3 scripts/test_tradervue_integration.py
```

Expected output:
```
✅ All critical tests passed!
```

### Step 3: Test API Endpoints

Start the API server and test endpoints:

```bash
# Terminal 1: Start server
cd argo
python3 -m uvicorn argo.api.server:app --reload

# Terminal 2: Test endpoints
curl http://localhost:8000/api/v1/tradervue/status
```

---

## Troubleshooting

### Issue: "Tradervue not enabled"

**Solution:**
- Verify credentials are set correctly
- Check environment variables: `echo $TRADERVUE_USERNAME`
- Verify password is set: `echo $TRADERVUE_PASSWORD` (won't display for security)
- Verify AWS Secrets Manager secrets exist (if using AWS)

### Issue: "Module not found: requests"

**Solution:**
```bash
pip install requests
# Or
pip install -r requirements.txt
```

### Issue: "API endpoint returns 503"

**Solution:**
- Credentials not configured
- Check status endpoint: `curl http://localhost:8000/api/v1/tradervue/status`
- Verify credentials are correct

### Issue: "Trades not syncing"

**Solution:**
1. Check logs for error messages
2. Verify Tradervue account credentials are valid (username and password)
3. Test API connection manually:
   ```bash
   curl -u username:password https://www.tradervue.com/api/v1/trades
   ```
4. Check network connectivity
5. Verify Tradervue Gold subscription is active

### Issue: "Exit trades not linking to entries"

**Solution:**
- This is expected if entry wasn't synced first
- Use manual sync to backfill: `POST /api/v1/tradervue/sync?days=30`
- Verify trade_id_mapping is working

---

## Production Deployment

### 1. Configure Secrets in AWS

```bash
aws secretsmanager create-secret \
  --name argo-capital/argo/tradervue-username \
  --secret-string "production_username" \
  --description "Tradervue Gold username for production"

aws secretsmanager create-secret \
  --name argo-capital/argo/tradervue-password \
  --secret-string "production_password" \
  --description "Tradervue Gold password for production"
```

### 2. Verify IAM Permissions

Ensure your IAM role/user has permissions to read secrets:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue",
        "secretsmanager:DescribeSecret"
      ],
      "Resource": [
        "arn:aws:secretsmanager:*:*:secret:argo-capital/argo/*"
      ]
    }
  ]
}
```

### 3. Monitor Logs

Check integration logs for sync status:

```bash
# Check for sync messages
grep "Tradervue" logs/*.log

# Check for errors
grep "ERROR.*Tradervue" logs/*.log
```

---

## Next Steps

1. ✅ **Configure Credentials** - Set up Tradervue API credentials
2. ✅ **Test Integration** - Run test script to verify setup
3. ✅ **Start API Server** - Start server and test endpoints
4. ✅ **Monitor Sync** - Watch logs for automatic trade syncing
5. ✅ **Frontend Integration** - Use widget URLs in frontend (see below)

---

## Frontend Integration

### Get Widget URLs

```typescript
// Fetch widget URL from API
const response = await fetch('/api/v1/tradervue/widget-url?widget_type=equity');
const data = await response.json();

// Embed widget
<iframe 
  src={data.widget_url} 
  width={data.width} 
  height={data.height}
  frameBorder="0"
/>
```

### Display Profile Link

```typescript
// Fetch profile URL
const response = await fetch('/api/v1/tradervue/profile-url');
const data = await response.json();

// Display link
<a href={data.profile_url} target="_blank" rel="noopener noreferrer">
  View Verified Performance on Tradervue
</a>
```

---

## Support

For issues or questions:
1. Check logs in `argo/logs/`
2. Review API endpoint responses
3. Verify Tradervue API credentials
4. Test with manual sync endpoint
5. Review test script output

---

**Setup Complete!** ✅  
**Ready for production use**


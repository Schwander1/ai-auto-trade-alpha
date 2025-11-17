# Prop Firm Deployment Guide

Complete guide for deploying prop firm trading system with dual services.

## Overview

This guide covers deploying both regular Argo trading service and prop firm trading service to run simultaneously on production.

## Architecture

### Dual Service Setup

- **Regular Service** (Port 8000)
  - Standard trading with dev/production accounts
  - `prop_firm.enabled = false`
  - Service: `argo-trading.service`

- **Prop Firm Service** (Port 8001)
  - Prop firm trading with separate account
  - `prop_firm.enabled = true`
  - Service: `argo-trading-prop-firm.service`

## Pre-Deployment Checklist

### 1. Local Validation

```bash
# Run comprehensive validation
cd argo
python scripts/validate_prop_firm_setup.py

# Test account switching
python scripts/test_prop_firm_account.py

# Run pre-deployment validation
../scripts/pre_deployment_validation.sh
```

### 2. Configuration Verification

Ensure `config.json` has:
- ✅ Prop firm account configured with valid credentials
- ✅ Prop firm section with all required fields
- ✅ Risk limits properly set
- ✅ Symbol restrictions configured

### 3. Code Verification

- ✅ All imports working
- ✅ No syntax errors
- ✅ Position cleanup logic implemented
- ✅ Error handling in place

## Deployment Steps

### Step 1: Pre-Deployment Validation

```bash
./scripts/pre_deployment_validation.sh
```

This validates:
- Python syntax
- Config JSON validity
- Prop firm configuration
- Import paths
- Service files
- Port availability

### Step 2: Deploy Dual Services

```bash
./scripts/deploy_dual_services.sh
```

This script:
1. Validates configuration
2. Deploys regular service (port 8000)
3. Deploys prop firm service (port 8001)
4. Verifies both services are running
5. Checks health endpoints

### Step 3: Post-Deployment Verification

```bash
# Check service status
ssh root@178.156.194.174 "systemctl status argo-trading.service argo-trading-prop-firm.service"

# Check health endpoints
curl http://178.156.194.174:8000/api/v1/health
curl http://178.156.194.174:8001/api/v1/health

# Check logs
ssh root@178.156.194.174 "tail -f /tmp/argo-green.log"
ssh root@178.156.194.174 "tail -f /tmp/argo-prop-firm.log"
```

## Manual Deployment (Alternative)

If automated deployment fails, deploy manually:

### Regular Service

```bash
ssh root@178.156.194.174

# Navigate to service directory
cd /root/argo-production-green

# Ensure prop_firm.enabled = false
python3 << PYTHON
import json
with open('config.json', 'r') as f:
    config = json.load(f)
if 'prop_firm' not in config:
    config['prop_firm'] = {}
config['prop_firm']['enabled'] = False
with open('config.json', 'w') as f:
    json.dump(config, f, indent=2)
PYTHON

# Install service
cp infrastructure/systemd/argo-trading.service /etc/systemd/system/
systemctl daemon-reload
systemctl restart argo-trading.service
```

### Prop Firm Service

```bash
# Navigate to prop firm directory
cd /root/argo-production-prop-firm

# Ensure prop_firm.enabled = true
python3 << PYTHON
import json
with open('config.json', 'r') as f:
    config = json.load(f)
if 'prop_firm' not in config:
    config['prop_firm'] = {}
config['prop_firm']['enabled'] = True
with open('config.json', 'w') as f:
    json.dump(config, f, indent=2)
PYTHON

# Install service
cp infrastructure/systemd/argo-trading-prop-firm.service /etc/systemd/system/
systemctl daemon-reload
systemctl restart argo-trading-prop-firm.service
```

## Service Management

### Start Services

```bash
systemctl start argo-trading.service
systemctl start argo-trading-prop-firm.service
```

### Stop Services

```bash
systemctl stop argo-trading.service
systemctl stop argo-trading-prop-firm.service
```

### Restart Services

```bash
systemctl restart argo-trading.service
systemctl restart argo-trading-prop-firm.service
```

### Check Status

```bash
systemctl status argo-trading.service
systemctl status argo-trading-prop-firm.service
```

### View Logs

```bash
# Regular service
tail -f /tmp/argo-green.log

# Prop firm service
tail -f /tmp/argo-prop-firm.log

# Both services
tail -f /tmp/argo-green.log /tmp/argo-prop-firm.log
```

## Monitoring

### Health Checks

```bash
# Regular service
curl http://localhost:8000/api/v1/health

# Prop firm service
curl http://localhost:8001/api/v1/health
```

### Verify Account Usage

Check logs for account selection:
- Regular service should show: `📊 Using Production paper account`
- Prop firm service should show: `🏢 PROP FIRM MODE: Using Prop Firm Test Account`

### Verify Prop Firm Mode

Check logs for prop firm initialization:
- Should see: `✅ Prop Firm Risk Monitor initialized (PROP FIRM MODE)`
- Should see: `🏢 PROP FIRM MODE: Using Prop Firm Test Account`

## Troubleshooting

### Service Won't Start

1. Check logs: `journalctl -u argo-trading-prop-firm.service -n 50`
2. Verify config: `python3 -c "import json; json.load(open('config.json'))"`
3. Check port: `lsof -i :8001`
4. Verify credentials: Check `config.json` has valid API keys

### Wrong Account Being Used

1. Verify `prop_firm.enabled` in config
2. Check logs for account selection message
3. Restart service after config change

### Port Conflicts

If ports are in use:
```bash
# Find process using port
lsof -i :8000
lsof -i :8001

# Kill process if needed (be careful!)
kill -9 <PID>
```

### Import Errors

1. Verify virtual environment is activated
2. Check Python path: `python3 -c "import sys; print(sys.path)"`
3. Reinstall dependencies: `pip install -r requirements.txt`

## Rollback

If deployment fails:

```bash
# Stop new services
systemctl stop argo-trading-prop-firm.service

# Restart regular service
systemctl restart argo-trading.service

# Verify regular service is working
curl http://localhost:8000/api/v1/health
```

## Testing

### Local Testing

1. Enable prop firm mode locally:
   ```json
   {
     "prop_firm": {
       "enabled": true
     }
   }
   ```

2. Start service:
   ```bash
   cd argo && source venv/bin/activate
   uvicorn main:app --reload --port 8000
   ```

3. Verify prop firm mode is active (check logs)

### Production Testing

1. Deploy to production
2. Verify both services are running
3. Check health endpoints
4. Monitor logs for errors
5. Verify account selection in logs

## Best Practices

1. **Always validate before deploying**
   - Run pre-deployment validation script
   - Test locally first

2. **Monitor after deployment**
   - Check logs immediately
   - Verify health endpoints
   - Monitor for first 10 minutes

3. **Keep services separate**
   - Don't mix configs
   - Use separate directories
   - Independent logging

4. **Document changes**
   - Note any config changes
   - Track deployment times
   - Document any issues

## Support

For issues:
1. Check logs first
2. Run validation scripts
3. Verify configuration
4. Check service status
5. Review this guide

---

**Last Updated**: 2025-01-XX
**Status**: ✅ Ready for Deployment


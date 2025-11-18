# Complete Production Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying both Prop Firm and Argo trading services to production.

## Prerequisites

- Production server access (SSH)
- Root or sudo access
- Alpaca API credentials for both accounts
- Python 3.8+ installed
- uvicorn installed

## Deployment Methods

### Method 1: Automated Deployment (Recommended)

#### Step 1: Copy Files to Production Server

From your local machine:

```bash
# Copy deployment package
scp -r production_deployment/* root@your-production-server:/root/

# Or if using specific IP
scp -r production_deployment/* root@178.156.194.174:/root/
```

#### Step 2: SSH to Production Server

```bash
ssh root@your-production-server
# or
ssh root@178.156.194.174
```

#### Step 3: Run Automated Deployment

```bash
cd /root
chmod +x deploy_to_production.sh
./deploy_to_production.sh
```

This script will:
- ✅ Verify production environment
- ✅ Configure dual trading
- ✅ Check Alpaca credentials
- ✅ Create systemd services
- ✅ Start services
- ✅ Enable services on boot
- ✅ Verify deployment

### Method 2: Manual Deployment

#### Step 1: Copy Files

```bash
scp -r production_deployment/* root@your-production-server:/root/
```

#### Step 2: Configure Services

```bash
ssh root@your-production-server
cd /root

# Run configuration
chmod +x enable_dual_trading_production.sh
./enable_dual_trading_production.sh
```

#### Step 3: Add Alpaca Credentials

Edit Argo config:
```bash
nano /root/argo-production-green/config.json
```

Add credentials:
```json
{
  "alpaca": {
    "api_key": "YOUR_ARGO_API_KEY",
    "secret_key": "YOUR_ARGO_SECRET_KEY"
  }
}
```

Edit Prop Firm config:
```bash
nano /root/argo-production-prop-firm/config.json
```

Add credentials:
```json
{
  "alpaca": {
    "prop_firm_test": {
      "api_key": "YOUR_PROP_FIRM_API_KEY",
      "secret_key": "YOUR_PROP_FIRM_SECRET_KEY"
    }
  }
}
```

#### Step 4: Create Systemd Services

```bash
chmod +x create_systemd_services.sh
sudo ./create_systemd_services.sh
```

#### Step 5: Start Services

```bash
sudo systemctl daemon-reload
sudo systemctl start argo-trading.service
sudo systemctl start argo-trading-prop-firm.service
sudo systemctl enable argo-trading.service
sudo systemctl enable argo-trading-prop-firm.service
```

#### Step 6: Verify

```bash
# Check status
sudo systemctl status argo-trading.service
sudo systemctl status argo-trading-prop-firm.service

# Check health
curl http://localhost:8000/health
curl http://localhost:8001/health

# Run verification
python3 verify_dual_trading_setup.py
```

## Service Management

### Start Services
```bash
sudo systemctl start argo-trading.service
sudo systemctl start argo-trading-prop-firm.service
```

### Stop Services
```bash
sudo systemctl stop argo-trading.service
sudo systemctl stop argo-trading-prop-firm.service
```

### Restart Services
```bash
sudo systemctl restart argo-trading.service
sudo systemctl restart argo-trading-prop-firm.service
```

### Check Status
```bash
sudo systemctl status argo-trading.service
sudo systemctl status argo-trading-prop-firm.service
```

### View Logs
```bash
# Argo service logs
sudo journalctl -u argo-trading.service -f

# Prop Firm service logs
sudo journalctl -u argo-trading-prop-firm.service -f

# Last 100 lines
sudo journalctl -u argo-trading.service -n 100
sudo journalctl -u argo-trading-prop-firm.service -n 100
```

## Monitoring

### Health Checks

```bash
# Argo service
curl http://localhost:8000/health | python3 -m json.tool

# Prop Firm service
curl http://localhost:8001/health | python3 -m json.tool
```

### Trading Status

```bash
# Argo trading status
curl http://localhost:8000/api/v1/trading/status | python3 -m json.tool

# Prop Firm trading status
curl http://localhost:8001/api/v1/trading/status | python3 -m json.tool
```

### Latest Signals

```bash
# Argo signals
curl http://localhost:8000/api/signals/latest?limit=5 | python3 -m json.tool

# Prop Firm signals
curl http://localhost:8001/api/signals/latest?limit=5 | python3 -m json.tool
```

## Troubleshooting

### Service Won't Start

1. Check logs:
   ```bash
   sudo journalctl -u argo-trading.service -n 50
   ```

2. Check config files:
   ```bash
   python3 -m json.tool /root/argo-production-green/config.json
   ```

3. Check ports:
   ```bash
   netstat -tlnp | grep -E "8000|8001"
   ```

### Service Crashes

1. Check for errors in logs
2. Verify Alpaca credentials
3. Check disk space: `df -h`
4. Check memory: `free -h`

### Trades Not Executing

1. Verify `auto_execute: true` in config
2. Check Alpaca connection status
3. Review risk validation logs
4. Check signal confidence thresholds

## Configuration Files

### Argo Config
Location: `/root/argo-production-green/config.json`

Key settings:
- `trading.auto_execute: true`
- `trading.force_24_7_mode: true`
- `prop_firm.enabled: false`

### Prop Firm Config
Location: `/root/argo-production-prop-firm/config.json`

Key settings:
- `trading.auto_execute: true`
- `trading.force_24_7_mode: true`
- `prop_firm.enabled: true`
- `prop_firm.risk_limits.min_confidence: 82.0`

## Verification Checklist

After deployment, verify:

- [ ] Both services are running
- [ ] Health checks return 200 OK
- [ ] Trading status shows connected
- [ ] Alpaca accounts are connected
- [ ] Signals are being generated
- [ ] Auto-execute is enabled
- [ ] 24/7 mode is enabled
- [ ] Prop firm mode is correct for each service
- [ ] Systemd services are enabled on boot
- [ ] Logs show no errors

## Rollback

If deployment fails:

```bash
# Stop services
sudo systemctl stop argo-trading.service
sudo systemctl stop argo-trading-prop-firm.service

# Disable services
sudo systemctl disable argo-trading.service
sudo systemctl disable argo-trading-prop-firm.service

# Remove systemd files
sudo rm /etc/systemd/system/argo-trading.service
sudo rm /etc/systemd/system/argo-trading-prop-firm.service
sudo systemctl daemon-reload
```

## Support

For issues:
1. Check logs first
2. Verify configuration
3. Check service status
4. Review health endpoints

## Summary

✅ **Automated deployment script available**
✅ **Manual deployment steps documented**
✅ **Service management commands provided**
✅ **Monitoring and troubleshooting guides included**

**Ready for production deployment!**


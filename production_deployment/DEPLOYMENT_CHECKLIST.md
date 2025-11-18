# Production Deployment Checklist

Use this checklist to ensure complete deployment.

## Pre-Deployment

- [ ] Production server access confirmed
- [ ] Alpaca API credentials obtained for both accounts
- [ ] Deployment package copied to server
- [ ] SSH access tested

## Deployment Steps

### 1. Initial Setup
- [ ] SSH to production server
- [ ] Navigate to deployment directory
- [ ] Verify all files are present
- [ ] Make scripts executable

### 2. Configuration
- [ ] Run `enable_dual_trading_production.sh`
- [ ] Verify Argo config created/updated
- [ ] Verify Prop Firm config created/updated
- [ ] Add Argo Alpaca credentials
- [ ] Add Prop Firm Alpaca credentials
- [ ] Verify `auto_execute: true` in both configs
- [ ] Verify `force_24_7_mode: true` in both configs

### 3. Service Creation
- [ ] Run `create_systemd_services.sh`
- [ ] Verify systemd service files created
- [ ] Reload systemd daemon

### 4. Service Startup
- [ ] Start Argo service
- [ ] Start Prop Firm service
- [ ] Enable services on boot
- [ ] Wait for services to initialize (10-15 seconds)

### 5. Verification
- [ ] Argo service health check passes
- [ ] Prop Firm service health check passes
- [ ] Run `verify_dual_trading_setup.py`
- [ ] Check trading status for both services
- [ ] Verify Alpaca connections
- [ ] Check signal generation

### 6. Monitoring Setup
- [ ] Set up log monitoring
- [ ] Configure health check monitoring
- [ ] Set up alerts (if applicable)

## Post-Deployment

- [ ] Monitor logs for first 30 minutes
- [ ] Verify trades are executing (if applicable)
- [ ] Check for any errors
- [ ] Document deployment completion
- [ ] Update deployment records

## Verification Commands

```bash
# Service status
sudo systemctl status argo-trading.service
sudo systemctl status argo-trading-prop-firm.service

# Health checks
curl http://localhost:8000/health
curl http://localhost:8001/health

# Trading status
curl http://localhost:8000/api/v1/trading/status
curl http://localhost:8001/api/v1/trading/status

# Latest signals
curl http://localhost:8000/api/signals/latest?limit=3
curl http://localhost:8001/api/signals/latest?limit=3

# Logs
sudo journalctl -u argo-trading.service -n 50
sudo journalctl -u argo-trading-prop-firm.service -n 50
```

## Success Criteria

✅ Both services running
✅ Health checks returning 200 OK
✅ Trading status shows connected
✅ Signals being generated
✅ No critical errors in logs
✅ Services enabled on boot

## Notes

- Keep deployment package for reference
- Document any custom configurations
- Save deployment timestamp
- Note any issues encountered


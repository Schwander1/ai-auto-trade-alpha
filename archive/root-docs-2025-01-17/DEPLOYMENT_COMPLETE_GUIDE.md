# Complete Production Deployment Guide

**Date:** January 2025
**Status:** ✅ Ready for Deployment

---

## 🚀 Deployment Overview

This guide provides step-by-step instructions for deploying all optimizations and fixes to production.

---

## 📋 Pre-Deployment Checklist

### 1. Verify Local Files
```bash
# Check all new components exist
ls -la argo/argo/core/signal_quality_scorer.py
ls -la argo/argo/core/performance_monitor.py
ls -la argo/argo/core/error_recovery.py
ls -la argo/argo/core/config_validator.py
ls -la argo/argo/risk/prop_firm_monitor_enhanced.py
ls -la argo/argo/api/health.py

# Check all scripts exist
ls -la argo/scripts/verify_alpine_sync.py
ls -la argo/scripts/monitor_signal_quality.py
ls -la argo/scripts/prop_firm_dashboard.py
ls -la argo/scripts/validate_config.py
ls -la argo/scripts/performance_report.py
```

### 2. Validate Configuration
```bash
cd argo
python3 scripts/validate_config.py config.json
```

### 3. Review Deployment Script
```bash
cat scripts/deploy_optimizations_to_production.sh
```

---

## 🎯 Deployment Steps

### Step 1: Execute Deployment

```bash
# Make script executable (if not already)
chmod +x scripts/deploy_optimizations_to_production.sh

# Run deployment
./scripts/deploy_optimizations_to_production.sh
```

**What it does:**
- Creates backups of current production
- Syncs all new code to production
- Installs dependencies
- Validates configuration
- Restarts services
- Verifies deployment

**Expected time:** 5-10 minutes

---

### Step 2: Post-Deployment Verification

```bash
# Run comprehensive verification
chmod +x scripts/post_deployment_verification.sh
./scripts/post_deployment_verification.sh
```

**What it checks:**
- Service status
- Health endpoints
- Component presence
- Script executability
- Configuration validity
- Alpine sync status
- Signal quality
- Import tests
- Log errors

**Expected time:** 2-3 minutes

---

### Step 3: Setup Monitoring

```bash
# Configure automated monitoring
chmod +x scripts/setup_monitoring.sh
./scripts/setup_monitoring.sh
```

**What it sets up:**
- Monitoring directories
- Automated cron jobs
- Daily monitoring reports
- Log rotation
- Health check monitoring

**Expected time:** 1-2 minutes

---

### Step 4: Quick Verification

```bash
# Quick status check
chmod +x scripts/quick_deployment_check.sh
./scripts/quick_deployment_check.sh
```

**What it checks:**
- Services running
- Health endpoint
- Components present
- Scripts present

**Expected time:** 30 seconds

---

## 🔍 Manual Verification

### 1. Check Services
```bash
ssh root@178.156.194.174 'systemctl status argo-trading.service argo-trading-prop-firm.service'
```

### 2. Test Health Endpoint
```bash
curl http://178.156.194.174:8000/api/v1/health/
```

### 3. Verify Alpine Sync
```bash
ssh root@178.156.194.174 'cd /root/argo-production && python3 scripts/verify_alpine_sync.py --hours 24 --verbose'
```

### 4. Monitor Signal Quality
```bash
ssh root@178.156.194.174 'cd /root/argo-production && python3 scripts/monitor_signal_quality.py --hours 24'
```

### 5. Check Prop Firm Dashboard
```bash
ssh root@178.156.194.174 'cd /root/argo-production-prop-firm && python3 scripts/prop_firm_dashboard.py --json'
```

---

## 📊 Monitoring After Deployment

### Automated Monitoring

**Cron Jobs Configured:**
- Alpine sync verification: Every hour
- Signal quality monitoring: Every 6 hours
- Performance reporting: Daily at midnight
- Health checks: Every 15 minutes

**Log Locations:**
- Regular service: `/root/argo-production/logs/monitoring/`
- Prop firm service: `/root/argo-production-prop-firm/logs/monitoring/`

### Manual Monitoring

**Daily Report:**
```bash
ssh root@178.156.194.174 '/root/monitor_production.sh'
```

**View Logs:**
```bash
# Service logs
ssh root@178.156.194.174 'journalctl -u argo-trading.service -f'

# Monitoring logs
ssh root@178.156.194.174 'tail -f /root/argo-production/logs/monitoring/*.log'
```

---

## 🔄 Rollback Procedure

If issues occur after deployment:

### Option 1: Automated Rollback
```bash
chmod +x scripts/rollback_deployment.sh
./scripts/rollback_deployment.sh
```

### Option 2: Manual Rollback
```bash
# 1. Stop services
ssh root@178.156.194.174 'systemctl stop argo-trading.service argo-trading-prop-firm.service'

# 2. List backups
ssh root@178.156.194.174 'ls -dt /root/argo-production.backup.* | head -5'

# 3. Restore from backup
ssh root@178.156.194.174 'rm -rf /root/argo-production && cp -r /root/argo-production.backup.YYYYMMDD_HHMMSS /root/argo-production'

# 4. Restart services
ssh root@178.156.194.174 'systemctl start argo-trading.service argo-trading-prop-firm.service'
```

---

## ⚠️ Troubleshooting

### Services Won't Start

**Check logs:**
```bash
ssh root@178.156.194.174 'journalctl -u argo-trading.service -n 50'
```

**Common issues:**
- Missing dependencies: Check `requirements.txt`
- Configuration errors: Run `validate_config.py`
- Port conflicts: Check if port 8000 is in use

### Health Endpoint Not Responding

**Check service status:**
```bash
ssh root@178.156.194.174 'systemctl status argo-trading.service'
```

**Check if service is listening:**
```bash
ssh root@178.156.194.174 'netstat -tlnp | grep 8000'
```

### Import Errors

**Test imports:**
```bash
ssh root@178.156.194.174 'cd /root/argo-production && source venv/bin/activate && python3 -c "from argo.core.signal_quality_scorer import SignalQualityScorer; print(\"OK\")"'
```

**Reinstall dependencies:**
```bash
ssh root@178.156.194.174 'cd /root/argo-production && source venv/bin/activate && pip install -r requirements.txt'
```

### Alpine Sync Issues

**Check sync status:**
```bash
ssh root@178.156.194.174 'cd /root/argo-production && python3 scripts/verify_alpine_sync.py --hours 24 --verbose'
```

**Check Alpine backend:**
```bash
curl http://91.98.153.49:8001/api/v1/external-signals/sync/health
```

**Check API key:**
```bash
ssh root@178.156.194.174 'grep -r "ARGO_API_KEY\|argo-api-key" /root/argo-production/config.json'
```

---

## 📈 Post-Deployment Tasks

### Immediate (First Hour)
1. ✅ Verify all services are running
2. ✅ Check health endpoints
3. ✅ Verify Alpine sync
4. ✅ Monitor for errors

### Short-term (First Day)
1. Review monitoring reports
2. Check signal quality metrics
3. Verify performance metrics
4. Monitor error rates

### Long-term (First Week)
1. Review quality scores
2. Analyze performance trends
3. Optimize based on metrics
4. Set up additional alerts

---

## 📞 Support

### Log Locations
- Service logs: `journalctl -u argo-trading.service`
- Application logs: `/root/argo-production/logs/`
- Monitoring logs: `/root/argo-production/logs/monitoring/`

### Key Commands
```bash
# Service management
systemctl status argo-trading.service
systemctl restart argo-trading.service
systemctl stop argo-trading.service

# Monitoring
/root/monitor_production.sh
cd /root/argo-production && python3 scripts/verify_alpine_sync.py
cd /root/argo-production && python3 scripts/monitor_signal_quality.py

# Health checks
curl http://localhost:8000/api/v1/health/
```

---

## ✅ Deployment Checklist

- [ ] Pre-deployment checks completed
- [ ] Configuration validated
- [ ] Deployment script executed
- [ ] Post-deployment verification passed
- [ ] Monitoring setup completed
- [ ] Services running correctly
- [ ] Health endpoints responding
- [ ] Alpine sync verified
- [ ] Signal quality monitoring working
- [ ] No critical errors in logs

---

## 🎉 Success Criteria

Deployment is successful when:
- ✅ All services are running
- ✅ Health endpoints respond correctly
- ✅ All new components are present
- ✅ Monitoring scripts execute successfully
- ✅ No critical errors in logs
- ✅ Alpine sync is working
- ✅ Signal quality monitoring is active

---

**Last Updated:** January 2025

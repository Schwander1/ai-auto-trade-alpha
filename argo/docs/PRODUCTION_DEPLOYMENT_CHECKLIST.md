# Production Deployment Checklist - V11 Configuration

**Date:** 2025-11-16  
**Version:** V11 Optimal

---

## Pre-Deployment Checklist

### Configuration
- [x] V11 configuration file created (`config.v11.production.json`)
- [x] Configuration validated (JSON syntax)
- [x] All V11 settings verified
- [x] API keys and secrets preserved
- [x] Backup procedure tested

### Scripts
- [x] Deployment script created (`deploy_v11_configuration.py`)
- [x] Monitoring script created (`monitor_v11_performance.py`)
- [x] Production deployment script created (`deploy_v11_to_production.sh`)
- [x] All scripts tested locally
- [x] Scripts made executable

### Documentation
- [x] Deployment guide created
- [x] Monitoring procedures documented
- [x] Troubleshooting guide included
- [x] Rollback procedure documented

### Testing
- [x] Local deployment tested
- [x] Configuration validation tested
- [x] Service restart tested
- [x] Monitoring script tested

---

## Deployment Steps

### 1. Pre-Deployment
```bash
# Review configuration
cat argo/config.v11.production.json

# Test local deployment
cd argo
python3 scripts/deploy_v11_configuration.py

# Verify configuration
python3 -m json.tool config.json > /dev/null && echo "✅ Valid"
```

### 2. Production Deployment
```bash
# Run production deployment
./argo/scripts/deploy_v11_to_production.sh

# Or manually:
# 1. SSH to production
# 2. Backup current config
# 3. Deploy V11 config
# 4. Restart service
# 5. Verify status
```

### 3. Post-Deployment Verification
```bash
# Check service status
ssh root@178.156.194.174 'systemctl status argo-trading-prop-firm'

# Check logs
ssh root@178.156.194.174 'journalctl -u argo-trading-prop-firm -n 50'

# Run performance monitor
ssh root@178.156.194.174 'cd /root/argo-production-prop-firm/argo && python3 scripts/monitor_v11_performance.py'
```

---

## V11 Configuration Verification

### Required Settings
- [ ] `trading.min_confidence` = 60.0
- [ ] `trading.position_size_pct` = 9
- [ ] `trading.max_drawdown_pct` = 20
- [ ] `backtest.use_enhanced_cost_model` = true
- [ ] `backtest.volume_confirmation` = true
- [ ] `backtest.dynamic_stop_loss` = true
- [ ] `backtest.portfolio_risk_limits` = true

### Verify Command
```bash
python3 << 'EOF'
import json
with open('config.json') as f:
    config = json.load(f)
    print(f"Min Confidence: {config['trading']['min_confidence']}")
    print(f"Position Size: {config['trading']['position_size_pct']}%")
    print(f"Enhanced Cost Model: {config.get('backtest', {}).get('use_enhanced_cost_model', False)}")
EOF
```

---

## Monitoring Checklist

### Immediate (First Hour)
- [ ] Service is running
- [ ] No errors in logs
- [ ] Configuration loaded correctly
- [ ] Trading signals being generated

### Daily (First Week)
- [ ] Run performance monitor
- [ ] Check service logs
- [ ] Review trade execution
- [ ] Monitor risk limits
- [ ] Compare with backtest expectations

### Weekly (First Month)
- [ ] Comprehensive performance review
- [ ] Compare live vs backtest metrics
- [ ] Review symbol-specific performance
- [ ] Document any deviations
- [ ] Adjust if needed

---

## Rollback Procedure

If issues occur:

1. **Stop Service**
   ```bash
   ssh root@178.156.194.174 'systemctl stop argo-trading-prop-firm'
   ```

2. **Restore Backup**
   ```bash
   ssh root@178.156.194.174 'cd /root/argo-production-prop-firm/argo && ls -lt config.backup.*.json | head -1'
   # Copy backup filename and restore
   ssh root@178.156.194.174 'cd /root/argo-production-prop-firm/argo && cp config.backup.YYYYMMDD_HHMMSS.json config.json'
   ```

3. **Restart Service**
   ```bash
   ssh root@178.156.194.174 'systemctl start argo-trading-prop-firm'
   ```

4. **Verify**
   ```bash
   ssh root@178.156.194.174 'systemctl status argo-trading-prop-firm'
   ```

---

## Success Criteria

### Deployment Success
- ✅ Service restarts without errors
- ✅ Configuration loads correctly
- ✅ All V11 settings applied
- ✅ No configuration errors in logs

### Performance Success (After 1 Week)
- ✅ Win rate within 45-55% range
- ✅ Sharpe ratio > 0.60
- ✅ Drawdown < -25%
- ✅ Profit factor > 1.20
- ✅ Service stable (no crashes)

---

## Support

- **Deployment Guide:** `docs/V11_PRODUCTION_DEPLOYMENT.md`
- **Configuration:** `config.v11.production.json`
- **Deployment Script:** `scripts/deploy_v11_to_production.sh`
- **Monitor Script:** `scripts/monitor_v11_performance.py`

---

**Status:** Ready for Deployment  
**Last Updated:** 2025-11-16


# Deploy Performance Evaluation System to Production

## 🚀 Quick Deployment

### Option 1: Automated Deployment (Recommended)
```bash
# Deploy everything
./scripts/deploy_performance_evaluation_to_production.sh
```

### Option 2: Verify Deployment
```bash
# Check what's deployed
./scripts/verify_performance_evaluation_deployment.sh
```

---

## 📋 What Gets Deployed

### Scripts Deployed
1. ✅ `evaluate_performance.py`
2. ✅ `evaluate_performance_enhanced.py`
3. ✅ `performance_optimizer.py`
4. ✅ `performance_trend_analyzer.py`
5. ✅ `performance_comparator.py`
6. ✅ `performance_alert.py`
7. ✅ `auto_optimize.py`
8. ✅ `performance_summary.py`
9. ✅ `performance_exporter.py`
10. ✅ `setup_performance_monitoring.sh`

### Directories Created
- `/root/argo-production/reports`
- `/root/argo-production/logs/monitoring`
- `/root/argo-production-prop-firm/reports`
- `/root/argo-production-prop-firm/logs/monitoring`

### Cron Jobs Configured
- **Daily 9 AM**: Performance evaluation
- **Sunday 10 AM**: Weekly trend analysis
- **Daily 11 AM**: Optimization check
- **Every 6 hours**: Alert checks

---

## 🔍 Verification

### Check Scripts
```bash
ssh root@178.156.194.174 'ls -la /root/argo-production/scripts/performance*.py'
```

### Check Cron Jobs
```bash
ssh root@178.156.194.174 'crontab -l | grep performance'
```

### Test Scripts
```bash
# Test summary
ssh root@178.156.194.174 'cd /root/argo-production && python3 scripts/performance_summary.py'

# Test alert
ssh root@178.156.194.174 'cd /root/argo-production && python3 scripts/performance_alert.py --check'

# Run evaluation
ssh root@178.156.194.174 'cd /root/argo-production && python3 scripts/evaluate_performance_enhanced.py --days 1'
```

---

## 📊 Production Usage

### Manual Evaluation
```bash
ssh root@178.156.194.174
cd /root/argo-production
python3 scripts/evaluate_performance_enhanced.py --days 1
```

### View Reports
```bash
ssh root@178.156.194.174 'ls -lh /root/argo-production/reports/daily_*'
```

### View Alerts
```bash
ssh root@178.156.194.174 'tail -f /root/argo-production/logs/monitoring/alerts.log'
```

### Check Trends
```bash
ssh root@178.156.194.174 'cat /root/argo-production/reports/weekly_trends_*.txt'
```

---

## 🎯 Production Monitoring

### Daily Checks
- Reports generated at 9 AM
- Optimizations analyzed at 11 AM
- Alerts checked every 6 hours

### Weekly Reviews
- Trend analysis on Sundays
- Compare weekly performance
- Review optimization recommendations

---

## ✅ Deployment Checklist

- [ ] Run deployment script
- [ ] Verify scripts are deployed
- [ ] Check cron jobs are configured
- [ ] Test scripts manually
- [ ] Verify directories exist
- [ ] Check first scheduled run
- [ ] Review initial reports
- [ ] Configure alerting (optional)

---

*Ready to deploy!*


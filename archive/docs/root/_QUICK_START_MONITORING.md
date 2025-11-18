# Quick Start: Monitoring & Verification

**Date:** January 2025

---

## 🚀 Quick Commands

### 1. Verify Alpine Sync Status
```bash
cd argo
python scripts/verify_alpine_sync.py --hours 24 --verbose
```

**What it does:**
- Checks if signals are syncing from Argo to Alpine backend
- Verifies Alpine backend health
- Calculates sync rate
- Shows missing signals

---

### 2. Monitor Signal Quality
```bash
cd argo
python scripts/monitor_signal_quality.py --hours 24
```

**What it shows:**
- Total signals generated
- Confidence distribution
- Symbol performance
- Recent signals
- Quality alerts

**JSON output:**
```bash
python scripts/monitor_signal_quality.py --hours 24 --json
```

---

### 3. Prop Firm Dashboard
```bash
cd argo
python scripts/prop_firm_dashboard.py --refresh 5
```

**What it shows:**
- Real-time risk metrics
- Drawdown and daily P&L progress bars
- Account equity
- Open positions
- Recent alerts
- Alert summary

**Single JSON output:**
```bash
python scripts/prop_firm_dashboard.py --json
```

---

### 4. Health Check Endpoint
```bash
# Comprehensive health check
curl http://localhost:8000/api/v1/health/

# Simple health check (for load balancers)
curl http://localhost:8000/api/v1/health/simple
```

**What it checks:**
- Signal generation service
- Database connectivity
- Alpine sync service
- Trading engine
- Prop firm monitor

---

## 📊 Monitoring Schedule

### Daily Checks
1. **Morning:** Verify Alpine sync status
2. **Afternoon:** Check signal quality metrics
3. **Evening:** Review prop firm dashboard

### Weekly Reviews
1. Review signal quality trends
2. Check database size
3. Review prop firm performance
4. Analyze confidence distribution

---

## 🔍 Troubleshooting

### Alpine Sync Issues
```bash
# Check sync status
python scripts/verify_alpine_sync.py --hours 24 --verbose

# Check Alpine backend health
curl http://91.98.153.49:8001/api/v1/external-signals/sync/health

# Check logs
tail -f argo/logs/service_*.log | grep -i sync
```

### Signal Quality Issues
```bash
# Monitor quality metrics
python scripts/monitor_signal_quality.py --hours 24

# Check for low confidence signals
python scripts/monitor_signal_quality.py --hours 24 | grep "Low confidence"
```

### Prop Firm Issues
```bash
# Check prop firm dashboard
python scripts/prop_firm_dashboard.py

# Check risk monitor logs
tail -f argo/logs/alerts/*.json
```

---

## 📈 Key Metrics to Watch

### Signal Generation
- **Total signals:** Should be consistent (every 5 seconds)
- **Average confidence:** Should be ≥85%
- **High confidence rate:** Should be ≥30% (≥90% confidence)

### Alpine Sync
- **Sync rate:** Should be ≥90%
- **Missing signals:** Should be 0 or minimal

### Prop Firm
- **Drawdown:** Should be <70% of limit
- **Daily P&L:** Should be >-70% of limit
- **Risk level:** Should be "normal" or "warning"

---

## 🎯 Next Steps

1. **Set up automated monitoring:**
   - Schedule daily sync verification
   - Set up alerts for low sync rates
   - Monitor signal quality trends

2. **Create monitoring dashboard:**
   - Combine all metrics into one view
   - Add charts and graphs
   - Set up alerting

3. **Review and optimize:**
   - Review quality metrics weekly
   - Optimize based on performance data
   - Adjust thresholds as needed

---

## 📚 Documentation

- **Comprehensive Assessment:** `PRODUCTION_TRADING_COMPREHENSIVE_ASSESSMENT.md`
- **Fixes Applied:** `FIXES_AND_OPTIMIZATIONS_APPLIED.md`
- **Database Optimization:** `argo/docs/DATABASE_OPTIMIZATION_RECOMMENDATIONS.md`

---

**Last Updated:** January 2025

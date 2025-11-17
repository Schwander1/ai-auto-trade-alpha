# Performance Monitoring Automation Guide

## 🚀 Quick Start

### Setup Automation
```bash
cd argo
./scripts/setup_performance_monitoring.sh
```

This will:
- ✅ Create necessary directories
- ✅ Set up cron jobs for automated evaluation
- ✅ Create alert scripts
- ✅ Configure automated optimization workflow

---

## 📋 Automated Tasks

### Daily Tasks

**Performance Evaluation** (9 AM daily)
- Runs enhanced evaluation for last 24 hours
- Saves report to `reports/daily_evaluation_YYYYMMDD.json`

**Optimization Check** (11 AM daily)
- Analyzes latest evaluation report
- Generates optimization recommendations
- Saves to `reports/daily_optimizations_YYYYMMDD.txt`

**Alert Checks** (Every 6 hours)
- Checks for performance issues
- Logs alerts to `logs/monitoring/alerts.log`
- Sends notifications if critical issues found

### Weekly Tasks

**Trend Analysis** (Sundays 10 AM)
- Analyzes trends over last 7 days
- Generates trend report
- Saves to `reports/weekly_trends_YYYYMMDD.txt`

---

## 🛠️ Available Scripts

### 1. Performance Alert (`performance_alert.py`)

Checks for performance issues and generates alerts.

```bash
# Check for alerts
python3 scripts/performance_alert.py --check

# Check specific report
python3 scripts/performance_alert.py --report reports/daily_evaluation_20251117.json

# JSON output
python3 scripts/performance_alert.py --check --json

# Exit with code (for automation)
python3 scripts/performance_alert.py --check --exit-code
```

**Alert Levels:**
- 🔴 **Critical**: D grades, compliance breaches, profit factor < 1.0
- ⚠️ **Warning**: Metrics below targets, performance issues
- ❌ **Error**: System errors, missing data

---

### 2. Automated Optimization (`auto_optimize.py`)

Runs evaluation, analyzes optimizations, and suggests changes.

```bash
# Run full workflow
python3 scripts/auto_optimize.py

# Evaluate last 7 days
python3 scripts/auto_optimize.py --days 7

# JSON output
python3 scripts/auto_optimize.py --json
```

**Workflow:**
1. Runs performance evaluation
2. Analyzes with optimizer
3. Generates prioritized suggestions
4. Provides actionable steps

---

### 3. Performance Summary (`performance_summary.py`)

Quick overview of current performance status.

```bash
# Show summary
python3 scripts/performance_summary.py
```

**Shows:**
- Latest performance grades
- Key metrics for each component
- Quick status overview

---

### 4. Performance Exporter (`performance_exporter.py`)

Exports metrics to Prometheus format.

```bash
# Export once
python3 scripts/performance_exporter.py

# Run as HTTP server
python3 scripts/performance_exporter.py --server --port 9091

# Export specific report
python3 scripts/performance_exporter.py --report reports/daily_evaluation_20251117.json
```

**Prometheus Integration:**
```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'argo-performance'
    static_configs:
      - targets: ['localhost:9091']
```

---

## 📊 Monitoring Workflow

### Daily Monitoring
```bash
# 1. Check current status
python3 scripts/performance_summary.py

# 2. Check for alerts
python3 scripts/performance_alert.py --check

# 3. Review optimizations
cat reports/daily_optimizations_$(date +%Y%m%d).txt
```

### Weekly Review
```bash
# 1. Review trends
cat reports/weekly_trends_$(date +%Y%m%d).txt

# 2. Compare with previous week
python3 scripts/performance_comparator.py \
  reports/daily_evaluation_last_week.json \
  reports/daily_evaluation_this_week.json

# 3. Analyze trends
python3 scripts/performance_trend_analyzer.py --days 7
```

### Optimization Workflow
```bash
# 1. Run automated optimization
python3 scripts/auto_optimize.py

# 2. Review suggestions
# ... implement changes ...

# 3. Measure impact
python3 scripts/performance_comparator.py \
  reports/before_optimization.json \
  reports/after_optimization.json
```

---

## 🔔 Alert Configuration

### Email Alerts

Add to cron job:
```bash
# Alert check with email
0 */6 * * * cd /path/to/argo && python3 scripts/performance_alert.py --check --exit-code 2>&1 | mail -s "Performance Alert" admin@example.com
```

### Slack Integration

Create `scripts/slack_alert.py`:
```python
import requests
import subprocess
import json

result = subprocess.run(
    ["python3", "scripts/performance_alert.py", "--check", "--json"],
    capture_output=True,
    text=True
)

alerts = json.loads(result.stdout)
critical = [a for a in alerts if a['level'] == 'critical']

if critical:
    webhook_url = "YOUR_SLACK_WEBHOOK"
    message = f"🚨 {len(critical)} critical performance alerts!"
    requests.post(webhook_url, json={"text": message})
```

---

## 📈 Grafana Dashboard

### Add Performance Panels

1. **Performance Grades**
   ```
   Query: argo_signal_generator_grade
   Visualization: Gauge (0-4)
   ```

2. **Cache Hit Rate**
   ```
   Query: argo_cache_hit_rate_percent
   Visualization: Graph
   Alert: < 50%
   ```

3. **Win Rate**
   ```
   Query: argo_production_win_rate_percent
   Visualization: Graph
   Alert: < 40%
   ```

4. **Compliance Status**
   ```
   Query: argo_prop_firm_drawdown_breaches
   Visualization: Stat
   Alert: > 0
   ```

---

## 🔧 Customization

### Change Schedule

Edit crontab:
```bash
crontab -e
```

### Change Alert Thresholds

Edit `scripts/performance_alert.py`:
```python
# Modify thresholds
if gen_time > 1.0:  # Change threshold
    alerts.append(...)
```

### Add Custom Metrics

Edit `scripts/performance_exporter.py`:
```python
# Add new metric
lines.append(f"argo_custom_metric {value}")
```

---

## 📚 Related Documentation

- `PERFORMANCE_EVALUATION_README.md` - Evaluation guide
- `ADVANCED_FEATURES.md` - Advanced features
- `FIXES_AND_OPTIMIZATIONS.md` - Optimization guide

---

## ✅ Verification

### Test Setup
```bash
# 1. Check cron jobs
crontab -l | grep performance

# 2. Test alert script
python3 scripts/performance_alert.py --check

# 3. Test exporter
python3 scripts/performance_exporter.py

# 4. Test summary
python3 scripts/performance_summary.py
```

### Monitor Logs
```bash
# Watch alert logs
tail -f logs/monitoring/alerts.log

# Check cron logs
grep CRON /var/log/syslog | grep performance
```

---

## 🎯 Next Steps

1. ✅ Run setup script
2. ✅ Verify cron jobs are scheduled
3. ✅ Test all scripts manually
4. ✅ Configure alerting (email/Slack)
5. ✅ Add Grafana panels
6. ✅ Review daily reports
7. ✅ Implement optimizations

---

*Created: November 17, 2025*
*Status: ✅ Ready for Use*

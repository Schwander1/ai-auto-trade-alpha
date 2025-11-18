# ✅ Report Paths Configuration - Complete

**Date:** 2025-01-27
**Status:** ✅ **CONFIGURED - All Reports Go to Specific Folders**

---

## 📁 Report Directory Structure

### Production Reports
- **Location:** `/root/argo-production/reports/`
- **Purpose:** All performance evaluation reports
- **Contents:**
  - Daily evaluations: `daily_evaluation_YYYYMMDD.json`
  - Weekly trends: `weekly_trends_YYYYMMDD.txt`
  - Daily optimizations: `daily_optimizations_YYYYMMDD.txt`
  - Enhanced evaluations: `performance_evaluation_enhanced_*.json`

### Production Logs
- **Location:** `/root/argo-production/logs/monitoring/`
- **Purpose:** Monitoring and alert logs
- **Contents:**
  - Alert logs: `alerts.log`
  - Performance reports: `performance_report.json`
  - Health checks: `health_check.json`

### Prop Firm Reports
- **Location:** `/root/argo-production-prop-firm/reports/`
- **Purpose:** Prop firm specific reports
- **Contents:** Same structure as production reports

### Prop Firm Logs
- **Location:** `/root/argo-production-prop-firm/logs/monitoring/`
- **Purpose:** Prop firm monitoring logs
- **Contents:** Same structure as production logs

---

## ⏰ Automated Report Generation

### Daily Reports (9 AM)
- **Script:** `evaluate_performance_enhanced.py`
- **Output:** `/root/argo-production/reports/daily_evaluation_YYYYMMDD.json`
- **Command:** Uses `--reports-dir` flag to ensure correct directory

### Weekly Reports (Sunday 10 AM)
- **Script:** `performance_trend_analyzer.py`
- **Output:** `/root/argo-production/reports/weekly_trends_YYYYMMDD.txt`
- **Command:** Uses absolute path in `--output` flag

### Daily Optimizations (11 AM)
- **Script:** `performance_optimizer.py`
- **Output:** `/root/argo-production/reports/daily_optimizations_YYYYMMDD.txt`
- **Command:** Uses absolute paths for input and output

### Alert Logs (Every 6 Hours)
- **Script:** `performance_alert.py`
- **Output:** `/root/argo-production/logs/monitoring/alerts.log`
- **Command:** Uses `--reports-dir` flag and absolute path for log file

---

## 🔧 Configuration Details

### Cron Jobs Updated
All cron jobs now use **absolute paths** to ensure reports are saved to specific folders:

```bash
# Daily Evaluation - 9 AM
0 9 * * * cd /root/argo-production && python3 scripts/evaluate_performance_enhanced.py --days 1 --json --reports-dir /root/argo-production/reports > /root/argo-production/reports/daily_evaluation_$(date +\%Y\%m\%d).json 2>&1

# Weekly Trends - Sunday 10 AM
0 10 * * 0 cd /root/argo-production && python3 scripts/performance_trend_analyzer.py --days 7 --output /root/argo-production/reports/weekly_trends_$(date +\%Y\%m\%d).txt 2>&1

# Daily Optimizations - 11 AM
0 11 * * * cd /root/argo-production && python3 scripts/performance_optimizer.py /root/argo-production/reports/daily_evaluation_$(date +\%Y\%m\%d).json --output /root/argo-production/reports/daily_optimizations_$(date +\%Y\%m\%d).txt 2>&1

# Alert Checks - Every 6 Hours
0 */6 * * * cd /root/argo-production && python3 scripts/performance_alert.py --check --reports-dir /root/argo-production/reports 2>&1 | tee -a /root/argo-production/logs/monitoring/alerts.log
```

### Script Updates
- ✅ `evaluate_performance_enhanced.py` - Added `--reports-dir` argument
- ✅ All scripts use absolute paths in cron jobs
- ✅ Directories are created automatically if they don't exist

---

## ✅ Verification

### Directories
- ✅ `/root/argo-production/reports/` - Exists
- ✅ `/root/argo-production/logs/monitoring/` - Exists
- ✅ `/root/argo-production-prop-firm/reports/` - Exists
- ✅ `/root/argo-production-prop-firm/logs/monitoring/` - Exists

### Cron Jobs
- ✅ All cron jobs use absolute paths
- ✅ All reports go to `/root/argo-production/reports/`
- ✅ All logs go to `/root/argo-production/logs/monitoring/`
- ✅ Scripts use `--reports-dir` flag when available

---

## 📋 Report File Naming

### Daily Evaluation Reports
- **Format:** `daily_evaluation_YYYYMMDD.json`
- **Example:** `daily_evaluation_20251117.json`
- **Location:** `/root/argo-production/reports/`

### Weekly Trend Reports
- **Format:** `weekly_trends_YYYYMMDD.txt`
- **Example:** `weekly_trends_20251117.txt`
- **Location:** `/root/argo-production/reports/`

### Daily Optimization Reports
- **Format:** `daily_optimizations_YYYYMMDD.txt`
- **Example:** `daily_optimizations_20251117.txt`
- **Location:** `/root/argo-production/reports/`

### Alert Logs
- **Format:** `alerts.log` (appended)
- **Location:** `/root/argo-production/logs/monitoring/`

---

## 🚀 Quick Commands

### View Reports
```bash
# List all daily reports
ssh root@178.156.194.174 'ls -lh /root/argo-production/reports/daily_*'

# View latest daily evaluation
ssh root@178.156.194.174 'cat /root/argo-production/reports/daily_evaluation_$(date +%Y%m%d).json'

# View latest optimization report
ssh root@178.156.194.174 'cat /root/argo-production/reports/daily_optimizations_$(date +%Y%m%d).txt'
```

### View Logs
```bash
# View alert log
ssh root@178.156.194.174 'tail -f /root/argo-production/logs/monitoring/alerts.log'

# View all monitoring logs
ssh root@178.156.194.174 'ls -lh /root/argo-production/logs/monitoring/'
```

### Verify Configuration
```bash
# Check cron jobs
ssh root@178.156.194.174 'crontab -l | grep performance'

# Verify directories
ssh root@178.156.194.174 'ls -ld /root/argo-production/reports /root/argo-production/logs/monitoring'
```

---

## ✅ Summary

**All reports are now configured to generate to specific folders:**

- ✅ **Reports:** `/root/argo-production/reports/`
- ✅ **Logs:** `/root/argo-production/logs/monitoring/`
- ✅ **Absolute paths** used in all cron jobs
- ✅ **Scripts updated** to support `--reports-dir` flag
- ✅ **Directories created** automatically
- ✅ **Prop firm** has separate directories

**Everything is configured and ready!** 🎉

---

**Configuration Date:** 2025-01-27
**Status:** ✅ **COMPLETE**
**Next Report:** Will be generated at 9 AM daily

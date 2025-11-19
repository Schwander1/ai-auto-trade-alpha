# SHORT Position Scripts - Quick Reference

## Overview

This directory contains all scripts for monitoring, testing, and managing SHORT positions.

---

## 📊 Monitoring Scripts

### `monitor_short_positions.py`
**Purpose:** Continuous or one-time monitoring of SHORT positions

**Usage:**
```bash
# One-time check
python scripts/monitor_short_positions.py

# Continuous monitoring (every 5 min)
python scripts/monitor_short_positions.py --continuous --interval 300

# JSON output
python scripts/monitor_short_positions.py --json
```

**What it monitors:**
- SELL signal execution rates
- Current SHORT positions and P&L
- Rejected SELL orders
- Account restrictions

---

### `short_position_dashboard.py`
**Purpose:** Comprehensive dashboard showing all metrics

**Usage:**
```bash
# Display dashboard
python scripts/short_position_dashboard.py

# Save to file
python scripts/short_position_dashboard.py --output dashboard.json

# JSON output
python scripts/short_position_dashboard.py --json
```

**Shows:**
- Current positions
- Execution metrics
- Performance summary
- Recent statistics
- Alerts
- System health

---

### `health_check_short.py`
**Purpose:** Quick health check with exit codes

**Usage:**
```bash
python scripts/health_check_short.py
```

**Exit Codes:**
- `0` - All systems healthy
- `1` - Warnings detected
- `2` - Critical issues detected

**Use in scripts:**
```bash
if python scripts/health_check_short.py; then
    echo "System is healthy"
else
    echo "System has issues"
fi
```

---

## 🚨 Alerting Scripts

### `alert_short_position_issues.py`
**Purpose:** Check for critical issues and send alerts

**Usage:**
```bash
# Run alert checks
python scripts/alert_short_position_issues.py

# Save alerts to file
python scripts/alert_short_position_issues.py --output alerts.json

# Custom thresholds
python scripts/alert_short_position_issues.py \
  --execution-rate-threshold 60.0 \
  --loss-threshold -3.0 \
  --max-rejected 5
```

**Alert Types:**
- Low execution rate
- Large SHORT losses
- Rejected orders
- Account restrictions

---

## 📈 Performance Scripts

### `short_position_performance_tracker.py`
**Purpose:** Track and report SHORT position performance

**Usage:**
```bash
# Generate report
python scripts/short_position_performance_tracker.py

# Save to file
python scripts/short_position_performance_tracker.py --output performance.json

# JSON output
python scripts/short_position_performance_tracker.py --json
```

**Metrics:**
- SHORT vs LONG comparison
- P&L tracking
- Execution statistics
- Historical analysis

---

## 🔍 Verification Scripts

### `verify_short_positions.py`
**Purpose:** Comprehensive verification of SHORT position system

**Usage:**
```bash
python scripts/verify_short_positions.py
```

**Checks:**
- Database for SELL signals
- Alpaca positions
- Order history
- Execution errors

---

### `query_short_positions.py`
**Purpose:** Database queries for SHORT position analysis

**Usage:**
```bash
python scripts/query_short_positions.py
```

**Queries:**
- SELL signal execution rates
- SHORT vs LONG comparison
- Recent activity
- Symbol-specific analysis

---

## 🧪 Testing Scripts

### `test_short_position.py`
**Purpose:** Manual testing of SHORT position opening

**Usage:**
```bash
# Dry run (safe)
python scripts/test_short_position.py --symbol SPY --dry-run

# Live test
python scripts/test_short_position.py --symbol SPY
```

**What it does:**
- Generates test SELL signal
- Executes to open SHORT
- Verifies position opened
- Checks bracket orders

---

## ⚙️ Setup Scripts

### `setup_scheduled_monitoring.sh`
**Purpose:** Set up scheduled monitoring via cron

**Usage:**
```bash
bash scripts/setup_scheduled_monitoring.sh
crontab crontab_short_monitoring.txt
```

**Creates:**
- Crontab entries
- Log directory
- Configuration files

---

### `scheduled_monitor_short.sh`
**Purpose:** Scheduled monitoring script (called by cron)

**Usage:**
```bash
# Manual test
bash scripts/scheduled_monitor_short.sh
```

**Runs:**
- Monitoring check
- Alert check
- Logs to files

---

## 📋 Quick Command Reference

### Daily Checks
```bash
# Quick status
python scripts/short_position_dashboard.py

# Health check
python scripts/health_check_short.py

# Performance
python scripts/short_position_performance_tracker.py
```

### Troubleshooting
```bash
# Comprehensive check
python scripts/verify_short_positions.py

# Check for issues
python scripts/alert_short_position_issues.py

# Monitor continuously
python scripts/monitor_short_positions.py --continuous
```

### Testing
```bash
# Run tests
python tests/test_short_positions.py

# Manual test
python scripts/test_short_position.py --symbol SPY --dry-run
```

---

## 📁 Related Files

### Configuration
- `config/short_position_monitoring.json` - Main configuration
- `crontab_short_monitoring.txt` - Scheduled tasks

### Documentation
- `SHORT_POSITION_MONITORING_GUIDE.md` - Complete guide
- `COMPLETE_IMPLEMENTATION_SUMMARY.md` - Implementation details
- `SIGNAL_BUY_SELL_LONG_SHORT_INVESTIGATION.md` - Investigation report

### Logs
- `logs/short_position_monitor_*.log` - Monitoring logs
- `logs/alerts_*.json` - Alert snapshots
- `logs/performance_*.json` - Performance reports

---

## 🔧 Configuration

### Alert Thresholds
Edit `config/short_position_monitoring.json`:
```json
{
  "alerting": {
    "thresholds": {
      "execution_rate_min": 50.0,
      "short_loss_threshold": -5.0,
      "max_rejected_orders": 3
    }
  }
}
```

### Monitoring Intervals
```json
{
  "monitoring": {
    "check_interval_seconds": 300
  }
}
```

---

## 📊 Exit Codes

| Script | Exit Code | Meaning |
|--------|-----------|---------|
| `health_check_short.py` | 0 | Healthy |
| `health_check_short.py` | 1 | Warnings |
| `health_check_short.py` | 2 | Critical |
| `alert_short_position_issues.py` | 0 | No alerts |
| `alert_short_position_issues.py` | 1 | Alerts found |

---

## 🚀 Quick Start

1. **Initial Setup:**
   ```bash
   bash scripts/setup_scheduled_monitoring.sh
   crontab crontab_short_monitoring.txt
   ```

2. **Daily Check:**
   ```bash
   python scripts/short_position_dashboard.py
   ```

3. **Health Check:**
   ```bash
   python scripts/health_check_short.py
   ```

4. **View Logs:**
   ```bash
   tail -f logs/short_position_monitor_*.log
   ```

---

**For detailed documentation, see `SHORT_POSITION_MONITORING_GUIDE.md`**


# Compliance Features Deployment Guide

Complete step-by-step guide for deploying compliance, security, and auditability features.

---

## Overview

This guide covers deployment of:
- Database immutability and audit logging
- Integrity monitoring
- Automated backups
- Latency tracking
- Compliance monitoring

---

## Prerequisites

- Access to Alpine production server (91.98.153.49)
- Access to Argo production server (178.156.194.174)
- SSH access with root privileges
- Python 3.8+ installed
- PostgreSQL database access
- AWS credentials (for S3 backups)

---

## Quick Start (Automated)

### Option 1: Automated Deployment Script

```bash
# Run comprehensive deployment script
./scripts/deploy-compliance-features.sh
```

This script will:
1. Deploy database migration
2. Setup cron jobs
3. Configure S3 versioning
4. Verify services
5. Run initial integrity check
6. Test backup system
7. Verify immutability
8. Check Prometheus metrics

### Option 2: Step-by-Step Manual Deployment

Follow the sections below for manual deployment.

---

## Step 1: Database Migration

### 1.1 Copy Migration File

```bash
# From your local machine
scp alpine-backend/backend/migrations/immutability_and_audit.py \
    root@91.98.153.49:/root/alpine-production/backend/migrations/
```

### 1.2 Run Migration

```bash
# SSH to Alpine server
ssh root@91.98.153.49

# Navigate to project
cd /root/alpine-production

# Activate virtual environment
source venv/bin/activate

# Run migration
python -m backend.migrations.immutability_and_audit upgrade
```

### 1.3 Verify Migration

```bash
# Check if tables were created
python3 <<EOF
from backend.core.database import get_engine
from sqlalchemy import inspect, text

engine = get_engine()
inspector = inspect(engine)

# Check for audit log table
tables = inspector.get_table_names()
required = ['signal_audit_log']

for table in required:
    if table in tables:
        print(f"✅ {table} exists")
    else:
        print(f"❌ {table} missing")

# Check for triggers
with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT tgname FROM pg_trigger 
        WHERE tgname LIKE '%signal%immutable%'
    """))
    triggers = result.fetchall()
    print(f"✅ Found {len(triggers)} immutability triggers")
EOF
```

---

## Step 2: Setup Cron Jobs

### 2.1 Automated Setup

```bash
# On Argo server
ssh root@178.156.194.174
cd /root/argo-production/argo
./compliance/setup_cron.sh
```

### 2.2 Manual Setup

```bash
# SSH to Argo server
ssh root@178.156.194.174

# Edit crontab
crontab -e

# Add the following entries:
# Daily backup at 2 AM UTC
0 2 * * * cd /root/argo-production/argo && /usr/bin/python3 compliance/daily_backup.py >> logs/daily_backup.log 2>&1

# Hourly integrity check (sample 1000 signals)
0 * * * * cd /root/argo-production/argo && /usr/bin/python3 compliance/integrity_monitor.py 1000 >> logs/integrity_checks.log 2>&1

# Daily full integrity check at 3 AM UTC
0 3 * * * cd /root/argo-production/argo && /usr/bin/python3 compliance/integrity_monitor.py full >> logs/integrity_checks.log 2>&1

# Weekly report every Sunday at 6 AM UTC
0 6 * * 0 cd /root/argo-production/argo && /usr/bin/python3 compliance/weekly_report.py >> logs/weekly_report.log 2>&1
```

### 2.3 Verify Cron Jobs

```bash
# List cron jobs
crontab -l | grep -A 5 "argo-compliance"
```

---

## Step 3: Configure S3 Versioning

### 3.1 Run S3 Setup Script

```bash
# From local machine or server with AWS credentials
python3 scripts/enable-s3-versioning.py
```

### 3.2 Verify S3 Configuration

```bash
# Check S3 bucket versioning
aws s3api get-bucket-versioning --bucket your-bucket-name

# Check lifecycle policy
aws s3api get-bucket-lifecycle-configuration --bucket your-bucket-name
```

---

## Step 4: Configure Alerting

### 4.1 Set Environment Variables

On Argo server, set the following environment variables:

```bash
# PagerDuty (for critical alerts)
export PAGERDUTY_ENABLED=true
export PAGERDUTY_INTEGRATION_KEY=your-integration-key

# Slack (for all alerts)
export SLACK_ENABLED=true
export SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Email (for all alerts)
export EMAIL_ALERTS_ENABLED=true
export EMAIL_SMTP_HOST=smtp.gmail.com
export EMAIL_SMTP_PORT=587
export EMAIL_SMTP_USER=your-email@gmail.com
export EMAIL_SMTP_PASSWORD=your-app-password
export EMAIL_FROM=your-email@gmail.com
export EMAIL_TO=alerts@example.com,ops@example.com
```

### 4.2 Add to System Environment

```bash
# Add to /etc/environment or systemd service file
sudo nano /etc/environment
# Add all environment variables above
```

---

## Step 5: Import Grafana Dashboard

### 5.1 Access Grafana

```bash
# Open Grafana UI
http://91.98.153.49:3000
```

### 5.2 Import Dashboard

1. Go to **Dashboards** > **Import**
2. Click **Upload JSON file**
3. Select `infrastructure/monitoring/grafana-dashboards/compliance-dashboard.json`
4. Select **Prometheus** as data source
5. Click **Import**

### 5.3 Verify Dashboard

- Check that all panels are displaying data
- Verify latency graphs show <500ms
- Confirm integrity check results are visible

---

## Step 6: Configure Prometheus Alerts

### 6.1 Update Alert Rules

Edit `infrastructure/monitoring/alerts.yml`:

```yaml
groups:
  - name: compliance
    rules:
      - alert: SignalDeliveryLatencyHigh
        expr: histogram_quantile(0.95, rate(signal_delivery_latency_seconds_bucket[5m])) > 0.5
        for: 5m
        annotations:
          summary: "Signal delivery latency exceeds 500ms"
      
      - alert: IntegrityVerificationFailure
        expr: increase(integrity_failed_verifications_total[1h]) > 0
        annotations:
          summary: "Signal integrity verification failed"
      
      - alert: BackupOverdue
        expr: (time() - last_backup_timestamp) > 86400
        annotations:
          summary: "Backup is overdue (>24 hours)"
```

### 6.2 Reload Prometheus

```bash
# Reload Prometheus configuration
curl -X POST http://localhost:9090/-/reload
```

---

## Step 7: Verification

### 7.1 Run Verification Script

```bash
# Run comprehensive verification
./scripts/verify-compliance-deployment.sh
```

### 7.2 Manual Verification

#### Test Immutability

```bash
# Try to update a signal (should fail)
python3 <<EOF
from backend.core.database import get_db
from sqlalchemy import text

db = next(get_db())
try:
    db.execute(text("UPDATE signals SET entry_price = 999.99 WHERE signal_id = (SELECT signal_id FROM signals LIMIT 1)"))
    db.commit()
    print("❌ ERROR: Update succeeded (should have failed!)")
except Exception as e:
    if "immutable" in str(e).lower():
        print("✅ Immutability working correctly")
    else:
        print(f"⚠️  Unexpected error: {e}")
EOF
```

#### Test Integrity Monitor

```bash
# Run integrity check
cd /root/argo-production/argo
python3 compliance/integrity_monitor.py 100

# Should output JSON with success: true
```

#### Test Backup

```bash
# Run backup manually
cd /root/argo-production/argo
python3 compliance/daily_backup.py

# Check S3 for backup file
aws s3 ls s3://your-bucket/backups/ --recursive | tail -5
```

---

## Step 8: Post-Deployment Monitoring

### 8.1 Check Logs

```bash
# Integrity check logs
tail -f /root/argo-production/argo/logs/integrity_checks.log

# Backup logs
tail -f /root/argo-production/argo/logs/daily_backup.log

# Weekly report logs
tail -f /root/argo-production/argo/logs/weekly_report.log
```

### 8.2 Monitor Metrics

- **Grafana Dashboard:** http://91.98.153.49:3000
- **Prometheus:** http://91.98.153.49:9090
- **Key Metrics:**
  - Signal delivery latency (should be <500ms)
  - Integrity check results (should be 0 failures)
  - Backup status (should be <24 hours old)

### 8.3 Test Alerting

```bash
# Trigger a test alert (if possible)
# Or wait for next integrity check to verify alerts are sent
```

---

## Troubleshooting

### Migration Fails

**Problem:** Migration script fails with database errors

**Solution:**
```bash
# Check database connection
python3 -c "from backend.core.database import get_engine; print(get_engine())"

# Check if migration already applied
python3 -c "from sqlalchemy import inspect; from backend.core.database import get_engine; print(inspect(get_engine()).get_table_names())"
```

### Cron Jobs Not Running

**Problem:** Cron jobs are not executing

**Solution:**
```bash
# Check cron service
systemctl status cron

# Check cron logs
grep CRON /var/log/syslog | tail -20

# Test cron job manually
cd /root/argo-production/argo && python3 compliance/integrity_monitor.py 10
```

### Integrity Check Fails

**Problem:** Integrity monitor reports hash mismatches

**Solution:**
```bash
# Check integrity log
cat /root/argo-production/argo/logs/integrity_checks.log | tail -50

# Verify specific signal
python3 -c "from argo.compliance.integrity_monitor import IntegrityMonitor; m = IntegrityMonitor(); print(m._verify_signal_hash({...}))"
```

### Backup Fails

**Problem:** Daily backup fails

**Solution:**
```bash
# Check AWS credentials
aws sts get-caller-identity

# Check S3 bucket permissions
aws s3 ls s3://your-bucket/backups/

# Test backup manually
python3 /root/argo-production/argo/compliance/daily_backup.py
```

---

## Rollback Procedures

### Rollback Migration

```bash
# Run migration downgrade
cd /root/alpine-production
source venv/bin/activate
python -m backend.migrations.immutability_and_audit downgrade
```

### Remove Cron Jobs

```bash
# Remove compliance cron jobs
crontab -l | grep -v "argo-compliance" | crontab -
```

### Disable Alerting

```bash
# Unset environment variables
unset PAGERDUTY_ENABLED
unset SLACK_ENABLED
unset EMAIL_ALERTS_ENABLED
```

---

## Maintenance

### Regular Tasks

- **Daily:** Monitor backup logs
- **Weekly:** Review integrity check results
- **Monthly:** Review audit logs
- **Quarterly:** Test backup restore procedure

### Updates

When updating compliance features:

1. Test in staging first
2. Backup database before migration
3. Run verification script after deployment
4. Monitor logs for 24 hours

---

## Related Documentation

- `docs/COMPLIANCE_IMPLEMENTATION.md` - Implementation details
- `docs/INTEGRITY_VERIFICATION.md` - Integrity verification procedures
- `docs/INCIDENT_RESPONSE_PLAYBOOK.md` - Incident response
- `docs/PATENT_CLAIM_MAPPING.md` - Patent claim mapping

---

**Last Updated:** 2025-01-27  
**Version:** 1.0


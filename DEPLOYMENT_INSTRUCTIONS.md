# Deployment Instructions

**Date:** 2025-01-27  
**Status:** ✅ Code Committed and Pushed

---

## ✅ Completed Steps

1. ✅ All code committed to repository
2. ✅ Changes pushed to `origin/main`
3. ✅ Ready for deployment

---

## 🚀 Deployment Steps

### Option 1: Automated Deployment (Recommended)

#### On Alpine Server (91.98.153.49)

```bash
# SSH to server
ssh root@91.98.153.49

# Navigate to project
cd /root/alpine-production

# Pull latest changes
git pull origin main

# Run deployment script
./scripts/deploy-compliance-features.sh

# Verify deployment
./scripts/verify-compliance-deployment.sh
```

#### On Argo Server (178.156.194.174)

```bash
# SSH to server
ssh root@178.156.194.174

# Navigate to project
cd /root/argo-production

# Pull latest changes
git pull origin main

# Run deployment script
./scripts/deploy-compliance-features.sh

# Verify deployment
./scripts/verify-compliance-deployment.sh
```

### Option 2: Manual Deployment

Follow the step-by-step guide in `docs/DEPLOYMENT_GUIDE_COMPLIANCE.md`

---

## 📋 Post-Deployment Verification

### 1. Check Database Migration

```bash
# On Alpine server
cd /root/alpine-production
source venv/bin/activate
python3 <<EOF
from backend.core.database import get_engine
from sqlalchemy import inspect, text

engine = get_engine()
inspector = inspect(engine)
tables = inspector.get_table_names()

# Check for audit log table
if 'signal_audit_log' in tables:
    print("✅ Audit log table exists")
else:
    print("❌ Audit log table missing")

# Check for triggers
with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT COUNT(*) FROM information_schema.triggers 
        WHERE event_object_table IN ('signals', 'signal_audit_log')
    """))
    count = result.scalar()
    print(f"✅ Found {count} triggers")
EOF
```

### 2. Verify Cron Jobs

```bash
# On Argo server
crontab -l | grep -A 5 "argo-compliance"
```

Expected output:
```
# Argo Capital Compliance Automation
# Daily backup at 2 AM UTC
0 2 * * * cd /root/argo-production/argo && /usr/bin/python3 compliance/daily_backup.py >> logs/daily_backup.log 2>&1

# Hourly integrity check (sample 1000 signals)
0 * * * * cd /root/argo-production/argo && /usr/bin/python3 compliance/integrity_monitor.py 1000 >> logs/integrity_checks.log 2>&1

# Daily full integrity check at 3 AM UTC
0 3 * * * cd /root/argo-production/argo && /usr/bin/python3 compliance/integrity_monitor.py full >> logs/integrity_checks.log 2>&1
```

### 3. Test Integrity Monitor

```bash
# On Argo server
cd /root/argo-production/argo
python3 compliance/integrity_monitor.py 10
```

Should output JSON with `"success": true`

### 4. Check Prometheus Metrics

```bash
# Check if metrics are available
curl -s "http://localhost:9090/api/v1/query?query=signal_delivery_latency_seconds" | jq '.data.result | length'
```

### 5. Import Grafana Dashboard

1. Open Grafana: http://91.98.153.49:3000
2. Go to **Dashboards** > **Import**
3. Upload: `infrastructure/monitoring/grafana-dashboards/compliance-dashboard.json`
4. Select Prometheus data source
5. Click **Import**

### 6. Configure Alerting

Set environment variables on Argo server:

```bash
# PagerDuty
export PAGERDUTY_ENABLED=true
export PAGERDUTY_INTEGRATION_KEY=your-key

# Slack
export SLACK_ENABLED=true
export SLACK_WEBHOOK_URL=your-webhook-url

# Email
export EMAIL_ALERTS_ENABLED=true
export EMAIL_SMTP_HOST=smtp.gmail.com
export EMAIL_SMTP_PORT=587
export EMAIL_SMTP_USER=your-email@gmail.com
export EMAIL_SMTP_PASSWORD=your-app-password
export EMAIL_TO=alerts@example.com
```

---

## 🧪 Run Tests

### Compliance Tests

```bash
# On Alpine server
cd /root/alpine-production
source venv/bin/activate
pytest tests/compliance/ -v
```

### Trading Endpoint Tests

```bash
# On Alpine server
cd /root/alpine-production
source venv/bin/activate
pytest alpine-backend/tests/integration/test_trading_endpoint.py -v
```

### Frontend Tests

```bash
# On Alpine server or local
cd alpine-frontend
npm test
```

---

## 📊 Monitoring

### Check Logs

```bash
# Integrity check logs
tail -f /root/argo-production/argo/logs/integrity_checks.log

# Backup logs
tail -f /root/argo-production/argo/logs/daily_backup.log

# Weekly report logs
tail -f /root/argo-production/argo/logs/weekly_report.log
```

### Monitor Metrics

- **Grafana Dashboard:** http://91.98.153.49:3000
- **Prometheus:** http://91.98.153.49:9090
- **Key Metrics:**
  - Signal delivery latency (should be <500ms)
  - Integrity check results (should be 0 failures)
  - Backup status (should be <24 hours old)

---

## 🔧 Troubleshooting

### Migration Fails

```bash
# Check database connection
python3 -c "from backend.core.database import get_engine; print(get_engine())"

# Check if migration already applied
python3 -c "from sqlalchemy import inspect; from backend.core.database import get_engine; print(inspect(get_engine()).get_table_names())"
```

### Cron Jobs Not Running

```bash
# Check cron service
systemctl status cron

# Check cron logs
grep CRON /var/log/syslog | tail -20

# Test cron job manually
cd /root/argo-production/argo && python3 compliance/integrity_monitor.py 10
```

### Integrity Check Fails

```bash
# Check integrity log
cat /root/argo-production/argo/logs/integrity_checks.log | tail -50
```

### Backup Fails

```bash
# Check AWS credentials
aws sts get-caller-identity

# Check S3 bucket permissions
aws s3 ls s3://your-bucket/backups/

# Test backup manually
python3 /root/argo-production/argo/compliance/daily_backup.py
```

---

## 📝 Rollback (If Needed)

### Rollback Migration

```bash
cd /root/alpine-production
source venv/bin/activate
python -m backend.migrations.immutability_and_audit downgrade
```

### Remove Cron Jobs

```bash
crontab -l | grep -v "argo-compliance" | crontab -
```

---

## ✅ Success Criteria

After deployment, verify:

- [ ] Database migration completed
- [ ] Immutability triggers active
- [ ] Audit log table exists
- [ ] Cron jobs installed
- [ ] Integrity monitor working
- [ ] Backup system functional
- [ ] Prometheus metrics available
- [ ] Grafana dashboard imported
- [ ] Alerting configured
- [ ] All tests passing

---

## 📞 Support

If issues arise:
1. Check `docs/DEPLOYMENT_GUIDE_COMPLIANCE.md` for detailed troubleshooting
2. Review logs in `/root/argo-production/argo/logs/`
3. Run verification script: `./scripts/verify-compliance-deployment.sh`
4. Check Grafana dashboard for metrics

---

**Last Updated:** 2025-01-27  
**Status:** ✅ Ready for deployment


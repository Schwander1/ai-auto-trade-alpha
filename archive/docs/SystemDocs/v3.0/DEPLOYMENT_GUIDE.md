# Security & Compliance Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying the security, compliance, and auditability hardening to production servers.

## Prerequisites

- ✅ PostgreSQL database running and accessible
- ✅ AWS credentials configured (for S3 backups)
- ✅ Production servers accessible via SSH
- ✅ Database backup completed (before migration)

## Deployment Steps

### Step 1: Pre-Deployment Checklist

- [ ] Backup production database
- [ ] Verify AWS credentials are configured
- [ ] Ensure S3 bucket exists and is accessible
- [ ] Review migration script: `alpine-backend/backend/migrations/immutability_and_audit.py`
- [ ] Schedule maintenance window (if needed)

### Step 2: Deploy Code Changes

```bash
# On production server (Alpine Backend)
cd /path/to/alpine-backend
git pull origin main
source venv/bin/activate
pip install -r backend/requirements.txt  # Ensure all dependencies are installed
```

### Step 3: Run Database Migration

**⚠️ IMPORTANT: Run on staging first, then production**

```bash
# On production server (Alpine Backend)
cd /path/to/alpine-backend
source venv/bin/activate

# Run migration
python -m backend.migrations.immutability_and_audit

# Verify migration
python -c "
from backend.core.database import get_engine
from sqlalchemy import inspect, text

engine = get_engine()
inspector = inspect(engine)

# Check tables
tables = inspector.get_table_names()
print('Tables:', tables)

# Check triggers
with engine.connect() as conn:
    result = conn.execute(text(\"\"\"
        SELECT trigger_name, event_manipulation, event_object_table 
        FROM information_schema.triggers 
        WHERE event_object_table IN ('signals', 'signal_audit_log')
    \"\"\"))
    triggers = result.fetchall()
    print('Triggers:', triggers)
"
```

**Expected Output:**
- ✅ `signal_audit_log` table created
- ✅ `merkle_roots` table created
- ✅ `integrity_checksum_log` table created
- ✅ Triggers created: `prevent_signal_modification_trigger`, `log_signal_creation_trigger`

### Step 4: Verify Migration Results

```bash
# Check new columns in signals table
python -c "
from backend.core.database import get_engine
from sqlalchemy import inspect

engine = get_engine()
inspector = inspect(engine)

if 'signals' in inspector.get_table_names():
    columns = [col['name'] for col in inspector.get_columns('signals')]
    new_cols = ['retention_expires_at', 'previous_hash', 'chain_index', 
                'generation_latency_ms', 'delivery_latency_ms', 'server_timestamp']
    print('New columns present:', [col for col in new_cols if col in columns])
"
```

### Step 5: Test Immutability

```bash
# Test that UPDATE/DELETE are blocked
python -c "
from backend.core.database import get_engine
from sqlalchemy import text

engine = get_engine()

# Test UPDATE (should fail)
try:
    with engine.connect() as conn:
        trans = conn.begin()
        conn.execute(text('UPDATE signals SET confidence = 99.9 WHERE id = 1'))
        trans.commit()
    print('❌ UPDATE succeeded (should have failed!)')
except Exception as e:
    if 'immutable' in str(e).lower():
        print('✅ UPDATE correctly blocked')
    else:
        print(f'Error: {e}')

# Test DELETE (should fail)
try:
    with engine.connect() as conn:
        trans = conn.begin()
        conn.execute(text('DELETE FROM signals WHERE id = 1'))
        trans.commit()
    print('❌ DELETE succeeded (should have failed!)')
except Exception as e:
    if 'immutable' in str(e).lower():
        print('✅ DELETE correctly blocked')
    else:
        print(f'Error: {e}')
"
```

### Step 6: Verify Audit Logging

```bash
# Create a test signal and verify audit log entry
python -c "
from backend.core.database import get_engine
from sqlalchemy import text
from datetime import datetime
import hashlib
import json

engine = get_engine()

# Create test signal
test_data = {
    'signal_id': 'TEST-' + str(int(datetime.now().timestamp())),
    'symbol': 'TEST',
    'action': 'BUY',
    'entry_price': 100.0,
    'confidence': 95.5,
    'timestamp': datetime.utcnow().isoformat()
}

hash_string = json.dumps(test_data, sort_keys=True, default=str)
verification_hash = hashlib.sha256(hash_string.encode('utf-8')).hexdigest()

with engine.connect() as conn:
    trans = conn.begin()
    conn.execute(text(\"\"\"
        INSERT INTO signals (
            symbol, action, price, confidence, target_price, stop_loss,
            rationale, verification_hash, created_at, retention_expires_at
        ) VALUES (
            :symbol, :action, :price, :confidence, :target_price, :stop_loss,
            :rationale, :verification_hash, NOW(), NOW() + INTERVAL '7 years'
        )
    \"\"\"), {
        'symbol': test_data['symbol'],
        'action': test_data['action'],
        'price': test_data['entry_price'],
        'confidence': test_data['confidence'] / 100.0,
        'target_price': 110.0,
        'stop_loss': 95.0,
        'rationale': 'Test signal for audit verification',
        'verification_hash': verification_hash
    })
    trans.commit()

# Check audit log
with engine.connect() as conn:
    result = conn.execute(text(\"\"\"
        SELECT COUNT(*) 
        FROM signal_audit_log 
        WHERE action = 'INSERT' 
        AND timestamp > NOW() - INTERVAL '1 minute'
    \"\"\"))
    count = result.scalar()
    print(f'✅ Audit log entries created: {count}')
"
```

### Step 7: Set Up S3 Versioning

```bash
# On production server (Argo)
cd /path/to/argo-production
source venv/bin/activate

# Set environment variable
export BACKUP_BUCKET_NAME=your-backup-bucket-name

# Run S3 versioning setup
python scripts/enable-s3-versioning.py
```

**Expected Output:**
- ✅ Versioning enabled
- ✅ Lifecycle policy configured
- ✅ Verification passed

### Step 8: Configure Cron Jobs

```bash
# On production server (Argo)
crontab -e

# Add these lines:
# Daily backup at 2:00 AM UTC
0 2 * * * cd /root/argo-production && source venv/bin/activate && python argo/argo/compliance/daily_backup.py >> /root/argo-production/logs/backup.log 2>&1

# Hourly integrity check (sample 1000 signals)
0 * * * * cd /root/argo-production && source venv/bin/activate && python argo/argo/compliance/integrity_monitor.py >> /root/argo-production/logs/integrity.log 2>&1

# Daily full integrity check at 3:00 AM UTC
0 3 * * * cd /root/argo-production && source venv/bin/activate && python argo/argo/compliance/integrity_monitor.py full >> /root/argo-production/logs/integrity.log 2>&1
```

### Step 9: Restart Services

```bash
# Restart Alpine Backend
cd /path/to/alpine-backend
source venv/bin/activate
# Stop existing service
pkill -f "uvicorn.*backend.main:app"
# Start service
nohup uvicorn backend.main:app --host 0.0.0.0 --port 9001 > /tmp/alpine.log 2>&1 &

# Restart Argo (if needed)
cd /path/to/argo-production
source venv/bin/activate
# Stop existing service
pkill -f "uvicorn.*main:app"
# Start service
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > /tmp/argo.log 2>&1 &
```

### Step 10: Post-Deployment Verification

```bash
# 1. Verify services are running
curl http://localhost:9001/health
curl http://localhost:8000/health

# 2. Check audit logs are being created
python -c "
from backend.core.database import get_engine
from sqlalchemy import text

engine = get_engine()
with engine.connect() as conn:
    result = conn.execute(text('SELECT COUNT(*) FROM signal_audit_log'))
    print(f'Total audit log entries: {result.scalar()}')
"

# 3. Test backup (manual)
python argo/argo/compliance/daily_backup.py

# 4. Test integrity check (manual)
python argo/argo/compliance/integrity_monitor.py

# 5. Verify immutability still works
# (Run Step 5 again)
```

## Rollback Procedure

If issues occur, rollback the migration:

```bash
# On production server
cd /path/to/alpine-backend
source venv/bin/activate

# Rollback migration
python -m backend.migrations.immutability_and_audit downgrade

# Restore from backup if needed
# (Use your standard database restore procedure)
```

**⚠️ WARNING:** Rollback will lose audit log data. Only rollback if absolutely necessary.

## Monitoring

### Log Files

- **Backup logs**: `/root/argo-production/logs/backup.log`
- **Integrity logs**: `/root/argo-production/logs/integrity.log`
- **Application logs**: Check service-specific log locations

### Prometheus Metrics

Monitor these metrics:
- `signal_generation_latency_seconds`
- `signal_delivery_latency_seconds`
- `integrity_failed_verifications_total`
- `last_backup_timestamp`

### Alerts

Configure alerts for:
- Backup failures (no backup > 25 hours old)
- Integrity check failures (any hash mismatch)
- Latency violations (p95 > 500ms)

## Troubleshooting

### Migration Fails

**Issue**: Migration script fails with error

**Solution**:
1. Check database connection
2. Verify PostgreSQL version (9.5+ required)
3. Check for existing triggers/tables
4. Review error message and fix accordingly

### Immutability Not Working

**Issue**: UPDATE/DELETE operations succeed

**Solution**:
1. Verify triggers are created: `SELECT * FROM information_schema.triggers WHERE event_object_table = 'signals'`
2. Check trigger function exists: `SELECT * FROM pg_proc WHERE proname = 'prevent_signal_modification'`
3. Re-run migration if needed

### Audit Logs Not Created

**Issue**: No entries in `signal_audit_log` table

**Solution**:
1. Verify trigger exists: `SELECT * FROM information_schema.triggers WHERE trigger_name = 'log_signal_creation_trigger'`
2. Check trigger function: `SELECT * FROM pg_proc WHERE proname = 'log_signal_creation'`
3. Test with manual INSERT
4. Check PostgreSQL logs for errors

### S3 Backup Fails

**Issue**: Backup script fails

**Solution**:
1. Verify AWS credentials: `aws sts get-caller-identity`
2. Check S3 bucket exists and is accessible
3. Verify bucket name in environment variable
4. Check IAM permissions for S3 access

## Production Checklist

- [ ] Database migration completed successfully
- [ ] Immutability triggers verified (UPDATE/DELETE blocked)
- [ ] Audit logs being created automatically
- [ ] S3 versioning enabled
- [ ] Cron jobs configured
- [ ] Services restarted
- [ ] Health checks passing
- [ ] Backup tested successfully
- [ ] Integrity check tested successfully
- [ ] Monitoring configured
- [ ] Alerts configured

## Support

For deployment issues:
- Email: devops@alpineanalytics.com
- On-call: (configure PagerDuty)
- Documentation: This file


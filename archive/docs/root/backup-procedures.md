# Backup Procedures

## Overview

Alpine Analytics maintains automated daily backups of all trading signals with 7-year retention for compliance requirements. Backups are stored in S3 with versioning enabled for point-in-time recovery.

## Backup Schedule

- **Frequency**: Daily at 2:00 AM UTC
- **Retention**: 7 years (2555 days)
- **Storage**: AWS S3 with versioning
- **Format**: CSV (plain text, no encryption per configuration)

## Backup Process

### Automated Daily Backup

The backup process runs automatically via cron:

```bash
# Cron job (configured on Argo server)
0 2 * * * cd /root/argo-production && source venv/bin/activate && python argo/argo/compliance/daily_backup.py
```

### Manual Backup

To create a backup manually:

```bash
# Backup yesterday's signals (default)
python argo/argo/compliance/daily_backup.py

# Backup specific date
python argo/argo/compliance/daily_backup.py 2024-11-13
```

## Backup Contents

Each backup CSV file contains:

**Required Fields:**
- `signal_id`: Unique identifier
- `symbol`: Trading symbol
- `action`: BUY or SELL
- `entry_price`: Entry price
- `target_price`: Take profit price
- `stop_price`: Stop loss price
- `confidence`: Confidence score (0-100)
- `strategy`: Strategy name
- `timestamp`: ISO timestamp
- `verification_hash`: SHA-256 hash for integrity verification

**Optional Fields:**
- `generation_latency_ms`: Signal generation latency
- `server_timestamp`: Server timestamp for latency calculation

## S3 Storage Structure

```
s3://backup-bucket/
  signals/
    2024/
      11/
        signals_backup_20241113_020000.csv
        signals_backup_20241114_020000.csv
      ...
```

## S3 Versioning

- **Status**: Enabled
- **Purpose**: Point-in-time recovery
- **Previous Versions**: Retained for 90 days
- **Current Versions**: Retained for 7 years

## Lifecycle Policy

### Current Versions
- **0-90 days**: Standard storage
- **90-365 days**: Standard-IA (Infrequent Access)
- **365-2555 days**: Glacier
- **After 2555 days**: Expired (deleted)

### Previous Versions
- **0-30 days**: Standard storage
- **30-90 days**: Glacier
- **After 90 days**: Expired (deleted)

## Backup Verification

### Automatic Verification

Each backup is automatically verified immediately after upload:
- CSV structure validation
- Record count verification
- Hash verification (sample)

### Manual Verification

Verify a backup manually:

```bash
# Verify latest backup
python argo/argo/compliance/verify_backup.py

# Verify specific backup
python argo/argo/compliance/verify_backup.py signals/2024/11/signals_backup_20241113_020000.csv

# Continuous verification (last 7 days)
python argo/argo/compliance/verify_backup.py continuous 7
```

## Restore Procedures

### Restore from Backup

1. **Download Backup**:
   ```bash
   aws s3 cp s3://backup-bucket/signals/2024/11/signals_backup_20241113_020000.csv ./restore.csv
   ```

2. **Verify Backup**:
   ```bash
   python scripts/argo-verify-cli.py verify-backup --file restore.csv
   ```

3. **Import to Database** (if needed):
   ```python
   # Use database import script or manual import
   import csv
   import sqlite3
   
   conn = sqlite3.connect('signals.db')
   cursor = conn.cursor()
   
   with open('restore.csv', 'r') as f:
       reader = csv.DictReader(f)
       for row in reader:
           # Insert into database
           cursor.execute("INSERT INTO signals (...) VALUES (...)", ...)
   
   conn.commit()
   ```

### Point-in-Time Recovery

To restore from a previous version:

1. **List Versions**:
   ```bash
   aws s3api list-object-versions \
     --bucket backup-bucket \
     --prefix signals/2024/11/signals_backup_20241113_020000.csv
   ```

2. **Download Specific Version**:
   ```bash
   aws s3api get-object \
     --bucket backup-bucket \
     --key signals/2024/11/signals_backup_20241113_020000.csv \
     --version-id <VERSION_ID> \
     restore.csv
   ```

## RTO/RPO Values

- **RTO (Recovery Time Objective)**: < 1 hour
- **RPO (Recovery Point Objective)**: 24 hours (daily backups)

## Cost Analysis

### Storage Costs (Estimated)

**Standard Storage (0-90 days):**
- ~$0.023/GB/month
- Example: 1GB backup = $0.023/month

**Standard-IA (90-365 days):**
- ~$0.0125/GB/month
- Example: 1GB backup = $0.0125/month

**Glacier (1-7 years):**
- ~$0.004/GB/month
- Example: 1GB backup = $0.004/month

**Cost Optimization:**
- Old versions expire after 90 days
- Current versions transition to cheaper storage
- 7-year retention maintained for compliance

### Example Monthly Cost

For 100GB of signal data:
- Month 1-3: 100GB × $0.023 = $2.30/month
- Month 4-12: 100GB × $0.0125 = $1.25/month
- Year 2-7: 100GB × $0.004 = $0.40/month

## Testing Procedures

### Weekly Restore Test

Test backup restoration weekly:

```bash
# Automated weekly restore test (configure in cron)
0 3 * * 0 python argo/argo/compliance/verify_backup.py continuous 7
```

### Manual Testing

1. Download latest backup
2. Verify CSV structure
3. Verify all hashes
4. Test import to database
5. Verify data integrity

## Monitoring

### Backup Status

Monitor backup status via:
- **Prometheus Metrics**: `last_backup_timestamp`, `backup_duration_seconds`
- **Logs**: `/root/argo-production/logs/backup.log`
- **S3**: Check for daily backup files

### Alerts

Configure alerts for:
- Backup failure (no backup > 25 hours old)
- Backup verification failure
- S3 upload errors
- Storage quota warnings

## Troubleshooting

### Backup Failed

**Symptoms:**
- No backup file in S3
- Error in logs

**Actions:**
1. Check logs: `tail -f /root/argo-production/logs/backup.log`
2. Verify AWS credentials
3. Check S3 bucket permissions
4. Verify database connection
5. Run manual backup: `python argo/argo/compliance/daily_backup.py`

### Verification Failed

**Symptoms:**
- Hash mismatches
- Missing fields
- Record count mismatch

**Actions:**
1. Re-download backup
2. Verify CSV structure
3. Check for corruption
4. Compare with database
5. Report to support

### Restore Failed

**Symptoms:**
- Cannot download backup
- Import errors
- Data corruption

**Actions:**
1. Verify S3 access
2. Check backup file integrity
3. Try previous version
4. Contact support

## Compliance

### 7-Year Retention

- **Requirement**: Maintain backups for 7 years
- **Implementation**: S3 lifecycle policy (2555 days)
- **Verification**: Monthly audit of retention dates

### Audit Trail

- All backups logged in audit trail
- Backup metadata stored in S3
- Verification results logged

### Regulatory Compliance

- **SEC**: 7-year record retention
- **FINRA**: Data integrity requirements
- **GDPR**: Data protection (if applicable)

## Best Practices

1. **Regular Testing**: Test restore procedures monthly
2. **Monitoring**: Monitor backup status daily
3. **Documentation**: Document all restore procedures
4. **Access Control**: Limit S3 access to authorized personnel
5. **Versioning**: Keep versioning enabled at all times
6. **Verification**: Verify every backup immediately after creation

## Support

For backup issues:
- Email: support@alpineanalytics.com
- On-call: (configure PagerDuty)
- Documentation: This file


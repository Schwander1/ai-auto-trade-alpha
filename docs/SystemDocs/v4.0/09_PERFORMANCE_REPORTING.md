# Performance Reporting Guide

**Date:** January 15, 2025  
**Version:** 4.0  
**Status:** ✅ Complete

---

## Executive Summary

The Performance Reporting System provides automated, database-driven performance reports with comprehensive metrics including weekly statistics, premium signal performance, and all-time statistics.

---

## Overview

### Report Types

1. **Weekly Reports** - Generated every Sunday
2. **Premium Reports** - High-confidence signal performance
3. **All-Time Reports** - Historical performance statistics

### Report Contents

- Total signals generated
- Completed signals (with outcomes)
- Win/loss counts
- Win rates
- Average win/loss percentages
- Premium signal statistics

---

## Weekly Report Generation

### Automatic Generation

Reports are generated automatically every Sunday via cron job:

```bash
# Cron job (runs every Sunday at 11:59 PM)
59 23 * * 0 /usr/bin/python3 /path/to/weekly_report.py
```

### Manual Generation

```bash
cd argo/argo/compliance
python3 weekly_report.py
```

---

## Database Queries

### Weekly Metrics

```sql
-- Total signals this week
SELECT COUNT(*) as total
FROM signals
WHERE timestamp >= date('now', '-7 days')

-- Completed signals with outcomes
SELECT 
    COUNT(*) as total,
    SUM(CASE WHEN outcome = 'win' THEN 1 ELSE 0 END) as wins,
    SUM(CASE WHEN outcome = 'loss' THEN 1 ELSE 0 END) as losses,
    AVG(CASE WHEN outcome = 'win' THEN profit_loss_pct END) as avg_win_pct,
    AVG(CASE WHEN outcome = 'loss' THEN profit_loss_pct END) as avg_loss_pct
FROM signals
WHERE timestamp >= date('now', '-7 days') 
  AND outcome IS NOT NULL
```

### Premium Metrics

```sql
-- Premium signals (confidence >= 95)
SELECT 
    COUNT(*) as total,
    SUM(CASE WHEN outcome = 'win' THEN 1 ELSE 0 END) as wins,
    SUM(CASE WHEN outcome = 'loss' THEN 1 ELSE 0 END) as losses
FROM signals
WHERE timestamp >= date('now', '-7 days') 
  AND confidence >= 95 
  AND outcome IS NOT NULL
```

### All-Time Metrics

```sql
-- All-time statistics
SELECT 
    COUNT(*) as total,
    SUM(CASE WHEN outcome = 'win' THEN 1 ELSE 0 END) as wins,
    SUM(CASE WHEN outcome = 'loss' THEN 1 ELSE 0 END) as losses
FROM signals
WHERE outcome IS NOT NULL
```

---

## Report Format

### Text Report

```
Argo Capital Weekly Report
==================================================
Week ending: 2025-01-15
Generated: 2025-01-15 23:59:00 UTC

WEEKLY PERFORMANCE SUMMARY
--------------------------------------------------
Total Signals Generated: 247
Completed Signals: 198
  - Wins: 115
  - Losses: 83
Win Rate: 58.08%
Average Win: +4.23%
Average Loss: -2.15%

PREMIUM SIGNALS (95%+ Confidence)
--------------------------------------------------
Total: 89
Wins: 67
Premium Win Rate: 75.28%

ALL-TIME STATISTICS
--------------------------------------------------
Total Completed Signals: 4,374
Total Wins: 2,547
All-Time Win Rate: 58.23%
```

---

## S3 Integration

### Upload Configuration

Reports are automatically uploaded to S3:

```python
s3_key = f'reports/{datetime.now().year}/week_{datetime.now().strftime("%Y%m%d")}.txt'
s3.upload_file(report_filename, bucket, s3_key)
```

### S3 Structure

```
s3://bucket-name/
  reports/
    2025/
      week_20250115.txt
      week_20250108.txt
      ...
```

---

## Implementation

### Main Function

```python
def generate_report():
    """Generate weekly performance report"""
    print(f"📊 Generating weekly report for week ending {datetime.now().strftime('%Y-%m-%d')}")
    
    # Get performance metrics
    metrics = get_performance_metrics()
    
    # Create report
    report_filename = f'weekly_report_{datetime.now().strftime("%Y%m%d")}.txt'
    
    with open(report_filename, 'w') as f:
        # Write report content
        ...
    
    # Upload to S3
    if bucket:
        s3.upload_file(report_filename, bucket, s3_key)
    
    # Clean up
    os.remove(report_filename)
```

### Metrics Function

```python
def get_performance_metrics():
    """Get performance metrics from database"""
    conn = sqlite3.connect(str(DB_FILE))
    cursor = conn.cursor()
    
    # Query metrics
    ...
    
    return {
        'week': {...},
        'premium': {...},
        'all_time': {...}
    }
```

---

## Configuration

### Environment Variables

```bash
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_DEFAULT_REGION=us-east-1
AWS_BUCKET_NAME=your-bucket-name
```

### Database Path

The system automatically detects the database path:

```python
if os.path.exists("/root/argo-production"):
    BASE_DIR = Path("/root/argo-production")
else:
    BASE_DIR = Path(__file__).parent.parent.parent.parent

DB_FILE = BASE_DIR / "data" / "signals.db"
```

---

## Error Handling

### Database Connection

```python
if not DB_FILE.exists():
    print(f"⚠️  Database not found: {DB_FILE}")
    return None
```

### S3 Upload

```python
try:
    s3.upload_file(report_filename, bucket, s3_key)
    print(f"✅ Report uploaded to s3://{bucket}/{s3_key}")
except Exception as e:
    print(f"⚠️  S3 upload failed: {e}")
    # Continue without upload
```

---

## Best Practices

1. **Regular Generation**
   - Run reports weekly
   - Use cron for automation
   - Verify reports are generated

2. **Data Validation**
   - Check database connection
   - Verify data exists
   - Handle missing data gracefully

3. **Storage**
   - Upload to S3 for archival
   - Keep local copy temporarily
   - Clean up after upload

4. **Monitoring**
   - Monitor report generation
   - Alert on failures
   - Track report history

---

## Troubleshooting

### Database Not Found

1. Check database path
2. Verify database exists
3. Check file permissions

### S3 Upload Fails

1. Verify AWS credentials
2. Check bucket permissions
3. Verify network connectivity

### Missing Metrics

1. Check database has data
2. Verify date ranges
3. Check query logic

---

## Future Enhancements

- HTML report format
- Email delivery
- Dashboard integration
- Historical trend analysis
- Export to CSV/Excel

---

**Related Documentation:**
- `04_SYSTEM_MONITORING_COMPLETE_GUIDE.md` - Monitoring overview
- `02_SIGNAL_GENERATION_COMPLETE_GUIDE.md` - Signal generation


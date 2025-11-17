# Data Lifecycle & Retention Rules

**Last Updated:** January 15, 2025  
**Version:** 1.0  
**Applies To:** All data storage (Argo Capital, Alpine Analytics LLC)

---

## Overview

Comprehensive data retention policies, archiving strategies, and data purging procedures to ensure compliance, cost efficiency, and data management.

**Strategic Context:** Data lifecycle management aligns with compliance and cost optimization goals defined in [24_VISION_MISSION_GOALS.md](24_VISION_MISSION_GOALS.md).

---

## Data Classification

### Data Types

**Rule:** Classify data by type and sensitivity

**1. Trading Data**
- Signals
- Trades
- Positions
- Performance metrics
- Risk data

**2. User Data**
- User profiles
- Authentication data
- Subscription data
- Usage analytics

**3. System Data**
- Logs
- Metrics
- Audit trails
- Configuration snapshots

**4. Compliance Data**
- Financial records
- Audit logs
- Transaction history
- Regulatory reports

---

## Retention Policies

### Trading Data Retention

**Signals:**
- **Active Signals:** Keep indefinitely (for analysis)
- **Historical Signals:** 7 years (regulatory requirement)
- **Archived Signals:** Compress and archive after 1 year

**Trades:**
- **Active Trades:** Keep until closed + 30 days
- **Historical Trades:** 7 years (regulatory requirement)
- **Archived Trades:** Compress and archive after 1 year

**Performance Data:**
- **Daily Metrics:** 7 years
- **Hourly Metrics:** 2 years
- **Minute Metrics:** 90 days

### User Data Retention

**User Profiles:**
- **Active Users:** Keep while account active
- **Inactive Users:** 3 years after last activity
- **Deleted Users:** 90 days (soft delete), then purge

**Authentication Data:**
- **Sessions:** 30 days
- **Login History:** 1 year
- **Failed Login Attempts:** 90 days

**Subscription Data:**
- **Active Subscriptions:** Keep while active
- **Cancelled Subscriptions:** 7 years (financial records)
- **Payment History:** 7 years (regulatory requirement)

### System Data Retention

**Application Logs:**
- **Development:** 7 days
- **Production:** 30 days
- **Archived Logs:** 1 year (compressed)

**Metrics:**
- **Real-time Metrics:** 15 days
- **Aggregated Metrics:** 1 year
- **Historical Metrics:** 7 years (monthly aggregates)

**Audit Trails:**
- **Security Events:** 7 years
- **Access Logs:** 1 year
- **Change Logs:** 7 years

---

## Data Archiving

### Archive Strategy

**Rule:** Archive data before purging

**Archive Process:**
1. **Identify Data:** Data older than retention period
2. **Export Data:** Export to archive format (CSV, Parquet, etc.)
3. **Compress:** Compress archive files
4. **Store:** Move to archive storage (S3, Glacier, etc.)
5. **Verify:** Verify archive integrity
6. **Purge:** Delete from primary database

### Archive Format

**Rule:** Use standard archive formats

**Formats:**
- **CSV:** For simple tabular data
- **Parquet:** For large datasets (compressed, columnar)
- **JSON:** For complex nested data
- **Database Dump:** For complete database backups

**Naming Convention:**
```
{entity}_{data_type}_{start_date}_{end_date}.{format}.gz
```

**Example:**
```
argo_signals_2024-01-01_2024-12-31.parquet.gz
alpine_users_2023-01-01_2023-12-31.csv.gz
```

### Archive Storage

**Rule:** Store archives in cost-effective storage

**Storage Tiers:**
- **Hot Storage:** Frequently accessed archives (S3 Standard)
- **Cold Storage:** Rarely accessed archives (S3 Glacier)
- **Deep Archive:** Long-term storage (S3 Glacier Deep Archive)

**Selection Criteria:**
- **Access Frequency:** How often data is accessed
- **Retrieval Time:** How quickly data needs to be available
- **Cost:** Storage and retrieval costs

---

## Data Purging

### Purging Process

**Rule:** Follow structured purging process

**Steps:**
1. **Identify Data:** Data beyond retention period
2. **Archive Data:** Export and archive before purging
3. **Verify Archive:** Confirm archive integrity
4. **Purge Data:** Delete from primary database
5. **Verify Purge:** Confirm data removed
6. **Update Records:** Log purge operation

### Purging Implementation

**Rule:** Implement safe purging procedures

**Example:**
```python
async def purge_old_signals(retention_days: int = 365):
    """Purge signals older than retention period"""
    cutoff_date = datetime.now() - timedelta(days=retention_days)
    
    # 1. Archive before purging
    old_signals = await db.query(Signal).filter(
        Signal.created_at < cutoff_date
    ).all()
    
    if old_signals:
        # Archive
        archive_file = await archive_signals(old_signals, cutoff_date)
        
        # Verify archive
        if not verify_archive(archive_file):
            raise ArchiveVerificationError("Archive verification failed")
        
        # Purge
        await db.query(Signal).filter(
            Signal.created_at < cutoff_date
        ).delete()
        
        # Log purge
        logger.info(
            f"Purged {len(old_signals)} signals older than {cutoff_date}",
            extra={"archive_file": archive_file}
        )
```

### Soft Delete vs Hard Delete

**Rule:** Use soft delete before hard delete

**Soft Delete:**
- Mark as deleted (deleted_at timestamp)
- Keep data for recovery period (90 days)
- Exclude from normal queries
- Allow recovery if needed

**Hard Delete:**
- Permanently remove data
- Only after soft delete period
- After archiving
- Irreversible

**Example:**
```python
# Soft delete
user.deleted_at = datetime.now()
await db.commit()

# Hard delete (after 90 days)
cutoff = datetime.now() - timedelta(days=90)
await db.query(User).filter(
    User.deleted_at < cutoff
).delete()
```

---

## Compliance Requirements

### Financial Records

**Rule:** Retain financial records per regulations

**Requirements:**
- **Trading Records:** 7 years (SEC requirement)
- **Payment Records:** 7 years (tax requirement)
- **Audit Trails:** 7 years (compliance requirement)

### GDPR Compliance

**Rule:** Comply with GDPR data retention

**Requirements:**
- **User Data:** Delete upon request (right to be forgotten)
- **Consent Records:** Keep while processing data
- **Data Processing Records:** 3 years minimum

**Implementation:**
```python
async def delete_user_data(user_id: str):
    """Delete all user data per GDPR request"""
    # Archive before deletion
    await archive_user_data(user_id)
    
    # Delete user data
    await db.query(User).filter(User.id == user_id).delete()
    await db.query(Subscription).filter(Subscription.user_id == user_id).delete()
    # ... delete all related data
    
    # Log deletion
    logger.info(f"Deleted all data for user {user_id} per GDPR request")
```

---

## Backup & Restore

### Backup Strategy

**Rule:** Regular backups before purging

**Backup Frequency:**
- **Daily:** Full database backup
- **Hourly:** Incremental backup (production)
- **Before Purging:** Full backup

**Backup Retention:**
- **Daily Backups:** 30 days
- **Weekly Backups:** 12 weeks
- **Monthly Backups:** 12 months
- **Yearly Backups:** 7 years

### Restore Procedures

**Rule:** Test restore procedures regularly

**Restore Testing:**
- Test restore monthly
- Verify data integrity
- Document restore time
- Update procedures if needed

---

## Data Lifecycle Automation

### Automated Purging

**Rule:** Automate data lifecycle management

**Scheduled Jobs:**
```python
# Daily job to archive and purge old data
@schedule.daily(hour=2, minute=0)
async def daily_data_lifecycle():
    # Archive data older than 1 year
    await archive_old_data(cutoff_days=365)
    
    # Purge data older than retention period
    await purge_old_data(retention_days=2555)  # 7 years
```

### Monitoring

**Rule:** Monitor data lifecycle operations

**Metrics:**
- Data purged per day
- Archive size
- Purge failures
- Restore requests

---

## Related Rules

- **Disaster Recovery:** [33_DISASTER_RECOVERY.md](33_DISASTER_RECOVERY.md) - Backup procedures
- **Security:** [07_SECURITY.md](07_SECURITY.md) - Data security
- **Monitoring:** [14_MONITORING_OBSERVABILITY.md](14_MONITORING_OBSERVABILITY.md) - Log retention

---

**Note:** Data lifecycle management is critical for compliance, cost optimization, and data management. Always archive before purging, verify archives, and follow retention policies. When in doubt, retain data longer rather than shorter.


# Disaster Recovery & Backup Rules

**Last Updated:** January 15, 2025  
**Version:** 1.0  
**Applies To:** All systems (Argo Capital, Alpine Analytics LLC)

---

## Overview

Comprehensive disaster recovery procedures, backup strategies, and business continuity plans to ensure system resilience and data protection.

**Strategic Context:** Disaster recovery aligns with reliability and business continuity goals defined in [24_VISION_MISSION_GOALS.md](24_VISION_MISSION_GOALS.md).

**See Also:** [32_DATA_LIFECYCLE.md](32_DATA_LIFECYCLE.md) for data retention policies.

---

## Recovery Objectives

### RTO (Recovery Time Objective)

**Rule:** Define RTO for each system

**Targets:**
- **Critical Systems (Trading):** < 1 hour
- **User-Facing Systems (Alpine):** < 4 hours
- **Supporting Systems:** < 24 hours

**Definition:** Maximum acceptable downtime before system must be restored

### RPO (Recovery Point Objective)

**Rule:** Define RPO for each system

**Targets:**
- **Trading Data:** < 5 minutes (minimal data loss)
- **User Data:** < 1 hour
- **System Logs:** < 24 hours

**Definition:** Maximum acceptable data loss (time between last backup and failure)

---

## Backup Strategy

### Backup Types

**1. Full Backup**
- Complete system snapshot
- Includes all data and configuration
- Weekly or monthly
- Longest restore time, most complete

**2. Incremental Backup**
- Changes since last backup
- Daily or hourly
- Faster backup, requires full + incrementals to restore

**3. Differential Backup**
- Changes since last full backup
- Daily
- Faster restore than incremental

### Backup Frequency

**Rule:** Backup based on RPO requirements

**Production Systems:**
- **Full Backup:** Weekly (Sunday 2 AM)
- **Incremental Backup:** Daily (2 AM)
- **Transaction Logs:** Continuous (if supported)

**Development Systems:**
- **Full Backup:** Weekly
- **Incremental Backup:** Daily

### Backup Storage

**Rule:** Store backups in multiple locations

**Storage Locations:**
1. **Primary:** Same region (fast restore)
2. **Secondary:** Different region (disaster protection)
3. **Offline:** Air-gapped storage (ransomware protection)

**Storage Types:**
- **Hot Storage:** Frequently accessed (S3 Standard)
- **Cold Storage:** Rarely accessed (S3 Glacier)
- **Offline:** Physical media (tape, external drives)

---

## Database Backups

### PostgreSQL Backups

**Rule:** Use pg_dump for PostgreSQL backups

**Full Backup:**
```bash
# Full database backup
pg_dump -Fc -h localhost -U user database_name > backup_$(date +%Y%m%d_%H%M%S).dump

# Verify backup
pg_restore --list backup_file.dump
```

**Automated Backup:**
```bash
#!/bin/bash
# Daily backup script
BACKUP_DIR="/backups/postgresql"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_$DATE.dump"

# Create backup
pg_dump -Fc -h localhost -U user database_name > "$BACKUP_FILE"

# Compress
gzip "$BACKUP_FILE"

# Upload to S3
aws s3 cp "$BACKUP_FILE.gz" s3://backups/postgresql/

# Cleanup old backups (keep 30 days)
find "$BACKUP_DIR" -name "*.dump.gz" -mtime +30 -delete
```

### SQLite Backups

**Rule:** Copy database file for SQLite backups

**Backup Process:**
```bash
# Simple copy (ensure no writes during backup)
cp signals.db signals.db.backup.$(date +%Y%m%d_%H%M%S)

# Or use .backup command
sqlite3 signals.db ".backup 'signals.db.backup'"
```

---

## Application Backups

### Configuration Backups

**Rule:** Backup all configuration files

**What to Backup:**
- `config.json` (templates)
- Environment variables (documented)
- Docker compose files
- Infrastructure as Code (Terraform, CloudFormation)
- SSL certificates
- Secrets (encrypted, in secrets manager)

### Code Backups

**Rule:** Version control is primary backup

**Backup Strategy:**
- **Primary:** Git repository (GitHub, GitLab, etc.)
- **Secondary:** Local repository clones
- **Tertiary:** Regular repository exports

---

## Restore Procedures

### Database Restore

**Rule:** Test restore procedures regularly

**PostgreSQL Restore:**
```bash
# Restore from backup
pg_restore -Fc -h localhost -U user -d database_name backup_file.dump

# Verify restore
psql -h localhost -U user -d database_name -c "SELECT COUNT(*) FROM signals;"
```

**Restore Process:**
1. Stop application
2. Backup current database (if exists)
3. Restore from backup
4. Verify data integrity
5. Restart application
6. Verify application functionality

### Application Restore

**Rule:** Document restore procedures

**Steps:**
1. Restore code from version control
2. Restore configuration files
3. Restore database
4. Restore secrets (from secrets manager)
5. Verify environment
6. Start services
7. Run health checks

---

## Disaster Scenarios

### Scenario 1: Database Failure

**Recovery Steps:**
1. Identify failure (database down, corrupted, etc.)
2. Stop application
3. Restore from latest backup
4. Apply transaction logs (if available)
5. Verify data integrity
6. Restart application
7. Monitor for issues

**RTO:** < 1 hour  
**RPO:** < 5 minutes (if transaction logs available)

### Scenario 2: Server Failure

**Recovery Steps:**
1. Provision new server
2. Restore code from version control
3. Restore configuration
4. Restore database
5. Restore secrets
6. Start services
7. Verify functionality

**RTO:** < 4 hours  
**RPO:** < 1 hour

### Scenario 3: Data Corruption

**Recovery Steps:**
1. Identify corrupted data
2. Stop writes to affected tables
3. Restore from backup
4. Verify data integrity
5. Resume operations
6. Investigate root cause

**RTO:** < 2 hours  
**RPO:** < 1 hour

### Scenario 4: Ransomware Attack

**Recovery Steps:**
1. Isolate affected systems
2. Identify attack vector
3. Restore from offline backups
4. Verify backup integrity
5. Restore systems
6. Patch vulnerabilities
7. Enhance security

**RTO:** < 24 hours  
**RPO:** < 24 hours (from offline backup)

---

## Backup Verification

### Backup Testing

**Rule:** Test backups regularly

**Testing Schedule:**
- **Weekly:** Verify backup file exists and is valid
- **Monthly:** Test restore to test environment
- **Quarterly:** Full disaster recovery drill

**Verification Steps:**
1. Check backup file exists
2. Verify backup file size (not zero)
3. Test restore to test environment
4. Verify data integrity
5. Document results

### Backup Monitoring

**Rule:** Monitor backup operations

**Metrics:**
- Backup success/failure rate
- Backup duration
- Backup size
- Restore test results

**Alerting:**
- Backup failures: Immediate alert
- Backup size anomalies: Alert if > 20% change
- Restore test failures: Alert immediately

---

## Business Continuity

### Failover Procedures

**Rule:** Document failover procedures

**Active-Passive Failover:**
1. Detect primary failure
2. Promote secondary to primary
3. Update DNS/routing
4. Verify functionality
5. Monitor for issues

**Active-Active Failover:**
1. Load balancer detects failure
2. Route traffic to healthy instances
3. Remove failed instance from pool
4. Monitor for issues

### Communication Plan

**Rule:** Document communication procedures

**Stakeholders:**
- Development team
- Operations team
- Management
- Users (if applicable)

**Communication Channels:**
- Slack/Teams for team communication
- Email for formal notifications
- Status page for user communication

---

## Backup Retention

### Retention Policy

**Rule:** Retain backups per retention policy

**Retention:**
- **Daily Backups:** 30 days
- **Weekly Backups:** 12 weeks
- **Monthly Backups:** 12 months
- **Yearly Backups:** 7 years

**See:** [32_DATA_LIFECYCLE.md](32_DATA_LIFECYCLE.md) for detailed retention policies

---

## Related Rules

- **Data Lifecycle:** [32_DATA_LIFECYCLE.md](32_DATA_LIFECYCLE.md) - Data retention
- **Deployment:** [04_DEPLOYMENT.md](04_DEPLOYMENT.md) - Deployment procedures
- **Security:** [07_SECURITY.md](07_SECURITY.md) - Security practices

---

**Note:** Disaster recovery is critical for business continuity. Always test restore procedures, verify backups, and maintain offline backups. When disaster strikes, follow procedures, document everything, and learn from the experience.


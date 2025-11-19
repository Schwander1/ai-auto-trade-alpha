# Deployment Checklist - Compliance & Security

This document provides a comprehensive deployment checklist for compliance and security features.

---

## Pre-Deployment

### Database Migration

- [ ] **Run immutability migration on staging:**
  ```bash
  python -m backend.migrations.immutability_and_audit
  ```

- [ ] **Verify migration succeeds:**
  - Check migration logs for errors
  - Verify new columns exist: `retention_expires_at`, `previous_hash`, `chain_index`, etc.
  - Verify triggers are created: `prevent_signal_modification`, `log_signal_insert`

- [ ] **Test migration reversibility:**
  ```bash
  python -m backend.migrations.immutability_and_audit downgrade
  python -m backend.migrations.immutability_and_audit upgrade
  ```

### S3 Configuration

- [ ] **Execute S3 versioning setup:**
  ```bash
  python scripts/enable-s3-versioning.py
  ```

- [ ] **Verify S3 versioning is enabled:**
  - Check AWS Console: S3 → Bucket → Properties → Versioning
  - Verify lifecycle policy is active

- [ ] **Test backup/restore cycle:**
  ```bash
  # Create test backup
  python argo/argo/compliance/daily_backup.py

  # Verify backup exists in S3
  aws s3 ls s3://your-bucket/signals/ --recursive

  # Test restore
  python argo/argo/compliance/verify_backup.py
  ```

### Testing

- [ ] **Run all compliance tests:**
  ```bash
  pytest tests/compliance/ -v
  ```

- [ ] **Verify test coverage:**
  - `test_immutability.py` - Database immutability
  - `test_audit_log.py` - Audit logging
  - `test_latency_tracking.py` - Latency metrics
  - `test_backup_encryption.py` - S3 encryption
  - `test_backup_verification.py` - Backup verification
  - `test_reasoning_enforcement.py` - AI reasoning validation
  - `test_integrity_monitoring.py` - Integrity checks

- [ ] **Run signal execution investigation:**
  ```bash
  python scripts/investigate_execution_flow.py
  ```

---

## Deployment

### Code Deployment

- [ ] **Deploy backend code updates:**
  - Verify all files are updated
  - Check for breaking changes
  - Review migration scripts

- [ ] **Deploy frontend code updates:**
  - Verify WebSocket latency tracking is enabled
  - Check for client-side validation

- [ ] **Deploy infrastructure updates:**
  - Prometheus configuration
  - Grafana dashboards
  - Alert rules

### Cron Jobs Configuration

- [ ] **Configure daily backup (2 AM UTC):**
  ```bash
  0 2 * * * cd /root/argo-production && source venv/bin/activate && python argo/argo/compliance/daily_backup.py >> logs/backup.log 2>&1
  ```

- [ ] **Configure hourly integrity check:**
  ```bash
  0 * * * * cd /root/argo-production && source venv/bin/activate && python argo/argo/compliance/integrity_monitor.py >> logs/integrity.log 2>&1
  ```

- [ ] **Configure daily full integrity check (3 AM UTC):**
  ```bash
  0 3 * * * cd /root/argo-production && source venv/bin/activate && python argo/argo/compliance/integrity_monitor.py full >> logs/integrity.log 2>&1
  ```

- [ ] **Verify cron jobs are active:**
  ```bash
  crontab -l
  ```

### Monitoring Configuration

- [ ] **Configure Grafana dashboard:**
  - Import: `infrastructure/monitoring/grafana-dashboards/compliance-dashboard.json`
  - Verify data source connection
  - Check all panels are displaying data

- [ ] **Configure Prometheus alerts:**
  - Latency > 500ms alert
  - Integrity check failures
  - Backup failures
  - Audit log errors

- [ ] **Initialize integrity monitoring:**
  ```bash
  python argo/argo/compliance/integrity_monitor.py init
  ```

---

## Post-Deployment Verification

### Immutability Verification

- [ ] **Verify immutability (attempt UPDATE - should fail):**
  ```sql
  UPDATE signals SET entry_price = 200.0 WHERE signal_id = 'TEST-123';
  -- Should fail with error about immutability
  ```

- [ ] **Verify immutability (attempt DELETE - should fail):**
  ```sql
  DELETE FROM signals WHERE signal_id = 'TEST-123';
  -- Should fail with error about immutability
  ```

- [ ] **Verify audit log entries created:**
  ```sql
  SELECT COUNT(*) FROM signal_audit_log;
  -- Should show entries for modification attempts
  ```

### Latency Verification

- [ ] **Check latency metrics in Prometheus:**
  ```bash
  # Query P95 latency
  curl http://localhost:9090/api/v1/query?query=histogram_quantile(0.95,rate(signal_delivery_latency_seconds_bucket[5m]))

  # Should be < 500ms (patent requirement)
  ```

- [ ] **Verify latency tracking in Grafana:**
  - Check "Signal Delivery Latency (P95)" panel
  - Verify alert triggers if > 500ms

### Backup Verification

- [ ] **Test backup/restore cycle:**
  ```bash
  # Create backup
  python argo/argo/compliance/daily_backup.py

  # Verify backup
  python argo/argo/compliance/verify_backup.py

  # Check S3
  aws s3 ls s3://your-bucket/signals/ --recursive | tail -5
  ```

- [ ] **Verify backup encryption:**
  ```bash
  aws s3api head-object --bucket your-bucket --key signals/2024/11/signals_backup_20241115.csv
  # Check ServerSideEncryption: AES256
  ```

### Reasoning Validation

- [ ] **Verify reasoning validation works:**
  ```python
  # Attempt to create signal without rationale
  signal = Signal(
      symbol="AAPL",
      action="BUY",
      entry_price=150.0,
      rationale=""  # Empty - should fail
  )
  # Should raise validation error
  ```

- [ ] **Verify minimum length enforcement:**
  ```python
  signal = Signal(
      symbol="AAPL",
      action="BUY",
      entry_price=150.0,
      rationale="Short"  # < 20 chars - should fail
  )
  # Should raise validation error
  ```

### Integrity Monitoring

- [ ] **Run initial integrity check:**
  ```bash
  python argo/argo/compliance/integrity_monitor.py full
  ```

- [ ] **Verify integrity check results:**
  - Check logs for any failures
  - Verify all signals pass hash verification
  - Check metrics: `integrity_failed_verifications_total`

### Compliance Report

- [ ] **Generate compliance report:**
  ```bash
  python scripts/generate_compliance_report.py
  ```

- [ ] **Verify report includes:**
  - Immutability status
  - Audit log statistics
  - Latency metrics
  - Backup status
  - Integrity check results

---

## Ongoing Monitoring

### Daily Checks

- [ ] **Review backup logs:**
  ```bash
  tail -50 logs/backup.log
  ```

- [ ] **Check integrity check results:**
  ```bash
  tail -50 logs/integrity.log
  ```

- [ ] **Monitor Grafana dashboard:**
  - Latency metrics
  - Integrity failures
  - Backup status

### Weekly Checks

- [ ] **Review audit logs:**
  ```sql
  SELECT COUNT(*), DATE(timestamp) as date
  FROM signal_audit_log
  WHERE timestamp > NOW() - INTERVAL '7 days'
  GROUP BY DATE(timestamp);
  ```

- [ ] **Verify S3 backups:**
  ```bash
  aws s3 ls s3://your-bucket/signals/ --recursive | wc -l
  ```

- [ ] **Check compliance metrics:**
  - Execution rate
  - Latency P95/P99
  - Integrity check pass rate

### Monthly Checks

- [ ] **Review compliance documentation:**
  - Update any changes
  - Verify all procedures are current

- [ ] **Audit access logs:**
  - Review who accessed compliance features
  - Verify proper authorization

- [ ] **Test disaster recovery:**
  - Restore from backup
  - Verify data integrity

---

## Rollback Procedures

If issues are detected:

1. **Stop cron jobs:**
   ```bash
   crontab -e
   # Comment out compliance cron jobs
   ```

2. **Revert database migration:**
   ```bash
   python -m backend.migrations.immutability_and_audit downgrade
   ```

3. **Revert code deployment:**
   ```bash
   git checkout <previous-commit>
   # Redeploy previous version
   ```

4. **Restore from backup:**
   ```bash
   # Restore database from backup
   # Restore S3 files if needed
   ```

---

## Troubleshooting

### Common Issues

**Issue: Migration fails**
- Check database permissions
- Verify SQLite/PostgreSQL version
- Review migration logs

**Issue: Backup fails**
- Check AWS credentials
- Verify S3 bucket exists
- Check network connectivity

**Issue: Integrity check fails**
- Review hash calculation
- Check for data corruption
- Verify database integrity

**Issue: Latency > 500ms**
- Check network latency
- Review signal generation performance
- Optimize database queries

---

## Additional Resources

- [Compliance Implementation Guide](./COMPLIANCE_IMPLEMENTATION.md)
- [Backup Procedures](./backup-procedures.md)
- [Integrity Verification](./INTEGRITY_VERIFICATION.md)
- [Configuration Examples](./configuration-examples.md)

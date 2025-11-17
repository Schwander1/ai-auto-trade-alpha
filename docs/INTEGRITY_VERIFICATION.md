# Integrity Verification Procedures

This document describes procedures for verifying signal integrity and detecting tampering in the Argo-Alpine trading signal platform.

---

## Overview

Signal integrity is verified through:
1. **SHA-256 Hash Verification** - Cryptographic verification of signal data
2. **Hash Chain Verification** - Linking signals through previous_hash
3. **Automated Monitoring** - Hourly/daily integrity checks
4. **Manual Verification** - CLI tools for on-demand verification

---

## Automated Integrity Monitoring

### Hourly Checks (Sample)

**Frequency:** Every hour  
**Sample Size:** 1000 random signals  
**Purpose:** Quick detection of tampering

**Setup:**
```bash
# Cron job
0 * * * * cd /root/argo-production && python argo/argo/compliance/integrity_monitor.py 1000 >> logs/integrity_checks.log 2>&1
```

**Output:**
```json
{
  "success": true,
  "total_signals": 1000,
  "checked": 1000,
  "failed": 0,
  "status": "PASS",
  "duration_seconds": 2.34,
  "signals_per_second": 427.35,
  "timestamp": "2025-01-27T12:00:00Z"
}
```

### Daily Full Checks

**Frequency:** Once daily (3 AM UTC)  
**Scope:** All signals in database  
**Purpose:** Comprehensive integrity verification

**Setup:**
```bash
# Cron job
0 3 * * * cd /root/argo-production && python argo/argo/compliance/integrity_monitor.py full >> logs/integrity_checks.log 2>&1
```

**Output:**
```json
{
  "success": true,
  "total_signals": 125000,
  "checked": 125000,
  "failed": 0,
  "status": "PASS",
  "duration_seconds": 312.45,
  "signals_per_second": 400.13,
  "timestamp": "2025-01-27T03:00:00Z"
}
```

---

## Manual Verification

### Verify Single Signal

**Python:**
```python
from argo.compliance.integrity_monitor import IntegrityMonitor
import sqlite3

monitor = IntegrityMonitor()

# Get signal from database
conn = sqlite3.connect('data/signals.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM signals WHERE signal_id = ?", ('SIG-123',))
signal = dict(cursor.fetchone())

# Verify hash
is_valid = monitor._verify_signal_hash(signal)
print(f"Signal SIG-123 is {'VALID' if is_valid else 'INVALID'}")
```

**CLI (Future):**
```bash
argo verify-signal SIG-123
# Output:
# Signal: SIG-123
# Hash: VALID ✓
# Timestamp: 2025-01-27T12:00:00Z
# Previous Hash: VALID ✓
# Status: VERIFIED
```

### Verify Signal Range

**Python:**
```python
from argo.compliance.integrity_monitor import IntegrityMonitor

monitor = IntegrityMonitor()

# Verify signals from date range
results = monitor.run_integrity_check(sample_size=1000)
print(f"Checked: {results['checked']}")
print(f"Failed: {results['failed']}")
print(f"Status: {results['status']}")
```

---

## Hash Verification Process

### SHA-256 Hash Calculation

**Fields Included:**
- `signal_id`
- `symbol`
- `action`
- `entry_price`
- `target_price`
- `stop_price`
- `confidence`
- `strategy`
- `timestamp`

**Algorithm:**
```python
import hashlib
import json

def calculate_signal_hash(signal):
    hash_fields = {
        'signal_id': signal['signal_id'],
        'symbol': signal['symbol'],
        'action': signal['action'],
        'entry_price': signal['entry_price'],
        'target_price': signal['target_price'],
        'stop_price': signal['stop_price'],
        'confidence': signal['confidence'],
        'strategy': signal['strategy'],
        'timestamp': signal['timestamp']
    }
    
    hash_string = json.dumps(hash_fields, sort_keys=True, default=str)
    return hashlib.sha256(hash_string.encode('utf-8')).hexdigest()
```

### Verification Steps

1. **Extract Stored Hash:** Get `sha256` field from signal
2. **Recalculate Hash:** Calculate hash from current signal data
3. **Compare:** Verify stored hash matches calculated hash
4. **Report:** Log result (PASS/FAIL)

---

## Hash Chain Verification

### Previous Hash Linking

**Purpose:** Detect insertion/deletion of signals in sequence

**Field:** `previous_hash` - Hash of previous signal in sequence

**Verification:**
```python
def verify_hash_chain(signal_id):
    # Get signal
    signal = get_signal(signal_id)
    
    # Get previous signal
    previous_signal = get_previous_signal(signal)
    
    if previous_signal:
        # Calculate previous signal hash
        prev_hash = calculate_signal_hash(previous_signal)
        
        # Verify chain
        if signal['previous_hash'] == prev_hash:
            return True
        else:
            return False  # Chain broken
    else:
        return True  # First signal, no previous
```

---

## Alerting

### Integrity Failure Alerts

**Trigger:** Any hash mismatch detected

**Channels:**
- PagerDuty (critical)
- Slack
- Email
- Notion (optional)

**Alert Details:**
```json
{
  "title": "Signal Integrity Verification Failure",
  "message": "5 out of 1000 signals failed integrity verification",
  "severity": "critical",
  "details": {
    "total_checked": 1000,
    "failed_count": 5,
    "success_rate": "99.50%",
    "failed_signal_ids": [
      "SIG-123 (AAPL)",
      "SIG-456 (TSLA)",
      ...
    ]
  }
}
```

**Configuration:**
```bash
# Enable alerting
export PAGERDUTY_ENABLED=true
export PAGERDUTY_INTEGRATION_KEY=your-key
export SLACK_ENABLED=true
export SLACK_WEBHOOK_URL=your-webhook
```

---

## Monitoring

### Prometheus Metrics

**Metrics:**
- `integrity_failed_verifications_total` (Counter) - Total failures
- `signal_verification_duration_seconds` (Histogram) - Verification time

**Query:**
```promql
# Total integrity failures
integrity_failed_verifications_total

# Verification duration (P95)
histogram_quantile(0.95, signal_verification_duration_seconds_bucket)
```

### Grafana Dashboard

**Panels:**
- Integrity check results (PASS/FAIL)
- Failed verification count
- Verification duration
- Signals per second
- Failed signal IDs

---

## Troubleshooting

### Hash Mismatch

**Symptom:** Integrity check reports hash mismatches

**Investigation:**
1. Check audit log for modification attempts
2. Verify signal data hasn't been corrupted
3. Check database integrity
4. Review backup/restore history

**Resolution:**
```python
# Recalculate and update hash (if data is correct)
signal = get_signal('SIG-123')
new_hash = calculate_signal_hash(signal)
# Note: This requires special permissions and should be logged
```

### Performance Issues

**Symptom:** Integrity checks taking too long

**Optimization:**
- Reduce sample size for hourly checks
- Use database indexes on signal_id
- Parallelize verification
- Cache hash calculations

---

## Best Practices

1. **Regular Monitoring:** Run hourly checks continuously
2. **Full Verification:** Run daily full checks
3. **Alert Response:** Investigate failures immediately
4. **Documentation:** Document all integrity issues
5. **Backup Verification:** Verify backups regularly
6. **Access Control:** Limit who can modify signals
7. **Audit Logging:** Review audit logs regularly

---

## Related Documentation

- `docs/COMPLIANCE_IMPLEMENTATION.md` - Compliance guide
- `docs/PATENT_CLAIM_MAPPING.md` - Patent claim mapping
- `argo/argo/compliance/integrity_monitor.py` - Implementation
- `tests/compliance/test_integrity_monitoring.py` - Tests

---

**Last Updated:** 2025-01-27  
**Version:** 1.0

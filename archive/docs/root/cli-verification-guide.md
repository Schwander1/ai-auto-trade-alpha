# CLI Verification Tool Guide

## Overview

The Argo-Alpine Signal Verification CLI Tool (`argo-verify-cli.py`) is a standalone tool for customers, auditors, and regulators to independently verify signal integrity. It works completely offline and requires no backend connection.

## Installation

### Requirements
- Python 3.8+
- No additional dependencies (uses standard library only)
- Optional: `colorama` for colored terminal output (`pip install colorama`)

### Setup
```bash
# Make executable
chmod +x scripts/argo-verify-cli.py

# Or run directly with Python
python scripts/argo-verify-cli.py --help
```

## Commands

### 1. Verify Hash (`verify-hash`)

Verify the SHA-256 hash for a single signal.

**Usage:**
```bash
python scripts/argo-verify-cli.py verify-hash \
  --signal-id SIG-1234567890 \
  --file backup.csv
```

**Output:**
- ✅ Success: Hash verification PASSED
- ❌ Failure: Hash verification FAILED (shows stored vs calculated hash)

### 2. Verify Backup (`verify-backup`)

Verify all signals in a backup CSV file.

**Usage:**
```bash
python scripts/argo-verify-cli.py verify-backup \
  --file signals_backup_20241113.csv \
  --output results.json
```

**Output:**
- Summary statistics (total, valid, failed)
- List of failed signal IDs (first 10)
- Optional: JSON or CSV output file

**Example Output:**
```
ℹ️  Loading backup: signals_backup_20241113.csv
ℹ️  Loaded 1250 signals
ℹ️  Verifying SHA-256 hashes...

============================================================
ℹ️  Verification Summary:
  Total signals: 1250
✅  Valid: 1248
❌  Failed: 2
============================================================
```

### 3. Batch Verify (`batch-verify`)

Efficiently verify thousands of signals with progress tracking.

**Usage:**
```bash
python scripts/argo-verify-cli.py batch-verify \
  --file signals.csv \
  --output results.json
```

**Features:**
- Progress indicator (every 100 signals)
- Detailed results in JSON format
- Summary statistics

**Output Format (JSON):**
```json
{
  "summary": {
    "total": 10000,
    "valid": 9998,
    "failed": 2
  },
  "results": [
    {
      "signal_id": "SIG-123",
      "symbol": "AAPL",
      "timestamp": "2024-11-13T10:30:00Z",
      "valid": true,
      "stored_hash": "abc123def456...",
      "calculated_hash": null
    }
  ]
}
```

### 4. Generate Report (`generate-report`)

Generate a comprehensive verification report for a date range.

**Usage:**
```bash
python scripts/argo-verify-cli.py generate-report \
  --start 2024-01-01 \
  --end 2024-01-31 \
  --output report.json
```

**Note:** This command currently generates a JSON report template. Full PDF generation requires additional dependencies.

## CSV File Format

The CLI tool expects CSV files with the following columns:

**Required Columns:**
- `signal_id`: Unique signal identifier
- `symbol`: Trading symbol (e.g., AAPL, BTC-USD)
- `action`: BUY or SELL
- `entry_price`: Entry price
- `target_price`: Take profit price
- `stop_price`: Stop loss price
- `confidence`: Confidence score (0-100)
- `strategy`: Strategy name
- `timestamp`: ISO timestamp
- `verification_hash` or `sha256`: SHA-256 hash to verify

**Optional Columns:**
- `generation_latency_ms`: Generation latency
- `server_timestamp`: Server timestamp

## Examples

### Example 1: Verify Single Signal
```bash
# Download backup from S3 or use local file
python scripts/argo-verify-cli.py verify-hash \
  --signal-id SIG-abc123def456 \
  --file signals_backup_20241113.csv
```

### Example 2: Verify Entire Backup
```bash
# Verify all signals and save results
python scripts/argo-verify-cli.py verify-backup \
  --file signals_backup_20241113.csv \
  --output verification_results.json
```

### Example 3: Batch Verify Large Dataset
```bash
# Verify 10,000+ signals efficiently
python scripts/argo-verify-cli.py batch-verify \
  --file all_signals_2024.csv \
  --output batch_results.json
```

### Example 4: Generate Monthly Report
```bash
# Generate report for January 2024
python scripts/argo-verify-cli.py generate-report \
  --start 2024-01-01 \
  --end 2024-01-31 \
  --output january_2024_report.json
```

## Troubleshooting

### Issue: "File not found"
**Solution:** Ensure the CSV file path is correct and the file exists.

### Issue: "No signals found"
**Solution:** Check that the CSV file has the required columns and contains data.

### Issue: "Hash verification FAILED"
**Possible Causes:**
1. Signal data was modified after creation
2. CSV file corruption
3. Incorrect hash calculation

**Action:** Report to Alpine Analytics support with:
- Signal ID
- Stored hash
- Calculated hash
- CSV file name

### Issue: Missing colorama (colored output)
**Solution:** Install colorama or ignore (tool works without it):
```bash
pip install colorama
```

## Output Interpretation

### Success Indicators
- ✅ Green checkmark: Operation successful
- ✅ "PASSED": Hash verification successful
- ✅ "Valid: X": Number of valid signals

### Failure Indicators
- ❌ Red X: Operation failed
- ❌ "FAILED": Hash verification failed
- ❌ "Failed: X": Number of failed signals

### Warning Indicators
- ⚠️ Yellow warning: Non-critical issue
- ℹ️ Blue info: Informational message

## For Auditors/Regulators

### Independent Verification
The CLI tool allows complete independent verification:
1. Download backup CSV from S3 or request from Alpine Analytics
2. Run verification locally (no network required)
3. Review results and generate reports
4. Compare results with Alpine Analytics audit logs

### Verification Process
1. **Obtain Backup File**: Request CSV backup for date range
2. **Run Verification**: Use `verify-backup` or `batch-verify`
3. **Review Results**: Check for any failed verifications
4. **Generate Report**: Create report for documentation
5. **Compare**: Verify results match Alpine Analytics audit logs

### Expected Results
- **Integrity Score**: Should be 100% (all signals valid)
- **Failed Verifications**: Should be 0
- **Hash Mismatches**: Should not occur (indicates tampering)

## FAQ

**Q: Does this tool require internet connection?**  
A: No, the tool works completely offline once you have the CSV file.

**Q: Can I verify signals from multiple dates?**  
A: Yes, combine multiple CSV files or use `batch-verify` with a combined file.

**Q: What if I find a hash mismatch?**  
A: Report immediately to Alpine Analytics support. This indicates potential data integrity issue.

**Q: How do I verify the CLI tool itself?**  
A: The tool is open-source and can be audited. Hash verification logic matches the production system.

**Q: Can I automate verification?**  
A: Yes, the tool can be integrated into scripts and CI/CD pipelines.

## Support

For issues or questions:
- Email: support@alpineanalytics.com
- Documentation: https://docs.alpineanalytics.com
- GitHub: (if open-sourced)


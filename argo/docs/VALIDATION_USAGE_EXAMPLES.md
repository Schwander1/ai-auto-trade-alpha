# Win Rate Validation System - Usage Examples

**Date:** January 15, 2025  
**Version:** 1.0

---

## Quick Start Examples

### Example 1: Generate Basic Validation Report

```python
from argo.validation import WinRateValidator

validator = WinRateValidator()
report = validator.validate_win_rate(period_days=30)

print(f"Win Rate: {report.overall_win_rate}%")
print(f"Total Trades: {report.completed_trades}")
print(f"Wins: {report.wins}, Losses: {report.losses}")
```

### Example 2: Generate Investor Report

```python
from argo.validation import WinRateValidator

validator = WinRateValidator()

# Generate markdown report
report = validator.generate_investor_report(
    period_days=30,
    output_format="markdown"
)

# Save to file
with open("investor_report.md", "w") as f:
    f.write(report)
```

### Example 3: Check Statistical Significance

```python
from argo.validation import WinRateValidator, ValidationMethodology

validator = WinRateValidator()
report = validator.validate_win_rate(
    period_days=30,
    methodology=ValidationMethodology.COMPLETED_TRADES,
    include_statistics=True
)

if report.statistics:
    print(f"95% Confidence Interval: {report.statistics.confidence_interval_95}")
    print(f"Statistically Significant: {report.statistics.is_statistically_significant}")
    print(f"Z-Score: {report.statistics.z_score}")
```

### Example 4: Analyze by Regime

```python
from argo.validation import WinRateValidator, ValidationMethodology

validator = WinRateValidator()
report = validator.validate_win_rate(
    period_days=90,
    methodology=ValidationMethodology.REGIME_BASED
)

print("Win Rate by Regime:")
for regime, rate in report.breakdown.by_regime.items():
    print(f"  {regime}: {rate}%")
```

### Example 5: Run Reconciliation

```python
from argo.validation import ReconciliationSystem
from argo.tracking.unified_tracker import UnifiedPerformanceTracker

tracker = UnifiedPerformanceTracker()
reconciliation = ReconciliationSystem(tracker, trading_engine=None)

result = reconciliation.reconcile_trades(period_days=30, auto_fix=False)

print(f"Total Trades: {result.total_trades}")
print(f"Verified: {result.verified_trades}")
print(f"Success Rate: {result.success_rate}%")
print(f"Issues: {len(result.issues)}")

# Print critical issues
for issue in result.issues:
    if issue.severity == "critical":
        print(f"  CRITICAL: {issue.description}")
```

### Example 6: Validate Data Quality

```python
from argo.validation import DataQualityValidator
from argo.tracking.unified_tracker import UnifiedPerformanceTracker

tracker = UnifiedPerformanceTracker()
validator = DataQualityValidator(tracker)

result = validator.validate_data_quality(period_days=30, auto_fix=True)

print(f"Quality Score: {result.quality_score}%")
print(f"Valid Trades: {result.valid_trades}/{result.total_trades}")

# Print critical issues
for issue in result.issues:
    if issue.severity == "critical":
        print(f"  CRITICAL: {issue.description} ({issue.field})")
```

### Example 7: Get Signal Conversion Stats

```python
from argo.validation import SignalLifecycleTracker

tracker = SignalLifecycleTracker()
stats = tracker.get_conversion_stats(period_days=30)

print(f"Total Signals: {stats['total_signals']}")
print(f"Executed: {stats['executed']}")
print(f"Skipped: {stats['skipped']}")
print(f"Conversion Rate: {stats['conversion_rate']}%")

print("\nSkip Reasons:")
for reason, count in stats['skip_reasons'].items():
    print(f"  {reason}: {count}")
```

### Example 8: Complete Validation Workflow

```python
from argo.validation import (
    WinRateValidator,
    ReconciliationSystem,
    DataQualityValidator,
    SignalLifecycleTracker
)
from argo.tracking.unified_tracker import UnifiedPerformanceTracker

# Initialize
tracker = UnifiedPerformanceTracker()
validator = WinRateValidator()
reconciliation = ReconciliationSystem(tracker, trading_engine=None)
quality_validator = DataQualityValidator(tracker)
lifecycle_tracker = SignalLifecycleTracker()

# Step 1: Validate data quality
print("1. Validating data quality...")
quality_result = quality_validator.validate_data_quality(period_days=30, auto_fix=True)
print(f"   Quality Score: {quality_result.quality_score}%")

# Step 2: Reconcile with broker
print("2. Reconciling with broker...")
recon_result = reconciliation.reconcile_trades(period_days=30, auto_fix=True)
print(f"   Success Rate: {recon_result.success_rate}%")

# Step 3: Validate win rate
print("3. Validating win rate...")
win_rate_report = validator.validate_win_rate(period_days=30, include_statistics=True)
print(f"   Win Rate: {win_rate_report.overall_win_rate}%")
print(f"   95% CI: {win_rate_report.statistics.confidence_interval_95}")

# Step 4: Get conversion stats
print("4. Checking signal conversion...")
conversion_stats = lifecycle_tracker.get_conversion_stats(period_days=30)
print(f"   Conversion Rate: {conversion_stats['conversion_rate']}%")

# Step 5: Generate investor report
print("5. Generating investor report...")
investor_report = validator.generate_investor_report(period_days=30, output_format="markdown")
with open("validation_report.md", "w") as f:
    f.write(investor_report)
print("   Report saved to validation_report.md")
```

---

## API Usage Examples

### Example 1: Get Win Rate via API

```bash
# Get win rate for last 30 days
curl "http://localhost:8000/api/v1/validation/win-rate?period=30"

# Get win rate for high confidence signals only
curl "http://localhost:8000/api/v1/validation/win-rate?period=30&min_confidence=95"

# Get win rate for stocks only
curl "http://localhost:8000/api/v1/validation/win-rate?period=30&asset_class=stock"

# Get markdown report
curl "http://localhost:8000/api/v1/validation/win-rate?period=30&format=markdown"
```

### Example 2: Get Investor Report

```bash
# Get JSON report
curl "http://localhost:8000/api/v1/validation/investor-report?period=30"

# Get markdown report
curl "http://localhost:8000/api/v1/validation/investor-report?period=30&format=markdown" > report.md
```

### Example 3: Check Reconciliation

```bash
# Get reconciliation report
curl "http://localhost:8000/api/v1/validation/reconciliation?period=30"

# Run reconciliation with auto-fix
curl -X POST "http://localhost:8000/api/v1/validation/reconcile?period=30&auto_fix=true"
```

### Example 4: Check Data Quality

```bash
# Get data quality report
curl "http://localhost:8000/api/v1/validation/data-quality?period=30"

# Run validation with auto-fix
curl -X POST "http://localhost:8000/api/v1/validation/validate-quality?period=30&auto_fix=true"
```

### Example 5: Get Signal Conversion Stats

```bash
curl "http://localhost:8000/api/v1/validation/signal-conversion?period=30"
```

---

## Advanced Examples

### Example 1: Custom Breakdown Analysis

```python
from argo.validation import WinRateValidator

validator = WinRateValidator()
report = validator.validate_win_rate(period_days=90)

# Analyze by confidence
print("Win Rate by Confidence:")
for conf_range, rate in report.breakdown.by_confidence.items():
    print(f"  {conf_range}%: {rate}%")

# Analyze by exit reason
print("\nWin Rate by Exit Reason:")
for reason, rate in report.breakdown.by_exit_reason.items():
    print(f"  {reason}: {rate}%")

# Analyze by symbol
print("\nTop Performing Symbols:")
sorted_symbols = sorted(
    report.breakdown.by_symbol.items(),
    key=lambda x: x[1],
    reverse=True
)
for symbol, rate in sorted_symbols[:5]:
    print(f"  {symbol}: {rate}%")
```

### Example 2: Performance Trend Analysis

```python
from argo.validation import WinRateValidator
from datetime import datetime, timedelta

validator = WinRateValidator()

# Get win rate for multiple periods
periods = [7, 14, 30, 60, 90]
results = []

for period in periods:
    report = validator.validate_win_rate(period_days=period)
    results.append({
        'period': period,
        'win_rate': report.overall_win_rate,
        'trades': report.completed_trades
    })

print("Win Rate Trend:")
for result in results:
    print(f"  {result['period']} days: {result['win_rate']}% ({result['trades']} trades)")
```

### Example 3: Regime Performance Analysis

```python
from argo.validation import WinRateValidator

validator = WinRateValidator()
report = validator.validate_win_rate(period_days=90)

# Analyze regime performance
regime_performance = report.breakdown.by_regime

print("Performance by Market Regime:")
for regime in ["BULL", "BEAR", "CHOP", "CRISIS"]:
    if regime in regime_performance:
        rate = regime_performance[regime]
        print(f"  {regime}: {rate}%")
    else:
        print(f"  {regime}: No data")
```

### Example 4: Exit Reason Analysis

```python
from argo.validation import WinRateValidator

validator = WinRateValidator()
report = validator.validate_win_rate(period_days=90)

# Analyze exit reasons
exit_reasons = report.breakdown.by_exit_reason

print("Win Rate by Exit Reason:")
for reason, rate in exit_reasons.items():
    print(f"  {reason.replace('_', ' ').title()}: {rate}%")

# Calculate take-profit vs stop-loss performance
if 'take_profit' in exit_reasons and 'stop_loss' in exit_reasons:
    tp_rate = exit_reasons['take_profit']
    sl_rate = exit_reasons['stop_loss']
    print(f"\nTake Profit Win Rate: {tp_rate}%")
    print(f"Stop Loss Win Rate: {sl_rate}%")
    print(f"Difference: {tp_rate - sl_rate}%")
```

### Example 5: Comprehensive Report Generation

```python
from argo.validation import WinRateValidator
from datetime import datetime
import json

validator = WinRateValidator()

# Generate comprehensive report
report = validator.generate_investor_report(period_days=30, output_format="json")

# Save JSON
with open(f"validation_report_{datetime.now().strftime('%Y%m%d')}.json", "w") as f:
    json.dump(report, f, indent=2)

# Generate markdown
markdown = validator.generate_investor_report(period_days=30, output_format="markdown")
with open(f"validation_report_{datetime.now().strftime('%Y%m%d')}.md", "w") as f:
    f.write(markdown)

print("Reports generated:")
print(f"  - validation_report_{datetime.now().strftime('%Y%m%d')}.json")
print(f"  - validation_report_{datetime.now().strftime('%Y%m%d')}.md")
```

---

## Integration Examples

### Example 1: Add to Dashboard

```typescript
// Frontend dashboard component
async function fetchWinRateValidation() {
  const response = await fetch('/api/v1/validation/win-rate?period=30');
  const data = await response.json();
  
  return {
    winRate: data.overall_win_rate,
    confidenceInterval: data.statistics?.confidence_interval_95,
    totalTrades: data.total_trades,
    breakdown: data.breakdown
  };
}
```

### Example 2: Scheduled Reports

```python
# Scheduled task (cron job)
from argo.validation import WinRateValidator
from datetime import datetime
import schedule
import time

def generate_daily_report():
    validator = WinRateValidator()
    report = validator.generate_investor_report(
        period_days=30,
        output_format="markdown"
    )
    
    filename = f"reports/daily_validation_{datetime.now().strftime('%Y%m%d')}.md"
    with open(filename, "w") as f:
        f.write(report)
    
    print(f"Daily report generated: {filename}")

# Schedule daily at 9 AM
schedule.every().day.at("09:00").do(generate_daily_report)

while True:
    schedule.run_pending()
    time.sleep(60)
```

### Example 3: Alert on Issues

```python
from argo.validation import DataQualityValidator, ReconciliationSystem
from argo.tracking.unified_tracker import UnifiedPerformanceTracker

def check_system_health():
    tracker = UnifiedPerformanceTracker()
    
    # Check data quality
    quality_validator = DataQualityValidator(tracker)
    quality_result = quality_validator.validate_data_quality(period_days=7)
    
    if quality_result.quality_score < 95:
        print(f"⚠️  Data quality below threshold: {quality_result.quality_score}%")
        # Send alert
    
    # Check reconciliation
    reconciliation = ReconciliationSystem(tracker, trading_engine=None)
    recon_result = reconciliation.reconcile_trades(period_days=7)
    
    if recon_result.success_rate < 95:
        print(f"⚠️  Reconciliation success rate below threshold: {recon_result.success_rate}%")
        # Send alert
    
    critical_issues = [i for i in recon_result.issues if i.severity == "critical"]
    if critical_issues:
        print(f"🚨 {len(critical_issues)} critical reconciliation issues found")
        # Send alert
```

---

## Complete Workflow Example

```python
"""
Complete validation workflow for investor presentation
"""

from argo.validation import (
    WinRateValidator,
    ReconciliationSystem,
    DataQualityValidator,
    SignalLifecycleTracker
)
from argo.tracking.unified_tracker import UnifiedPerformanceTracker
from datetime import datetime
import json

def generate_complete_validation_package(period_days=30):
    """Generate complete validation package for investors"""
    
    # Initialize
    tracker = UnifiedPerformanceTracker()
    validator = WinRateValidator()
    reconciliation = ReconciliationSystem(tracker, trading_engine=None)
    quality_validator = DataQualityValidator(tracker)
    lifecycle_tracker = SignalLifecycleTracker()
    
    print("🔍 Running Complete Validation...")
    
    # 1. Data Quality Check
    print("\n1️⃣ Validating Data Quality...")
    quality_result = quality_validator.validate_data_quality(
        period_days=period_days,
        auto_fix=True
    )
    print(f"   ✅ Quality Score: {quality_result.quality_score}%")
    
    # 2. Reconciliation
    print("\n2️⃣ Reconciling with Broker...")
    recon_result = reconciliation.reconcile_trades(
        period_days=period_days,
        auto_fix=True
    )
    print(f"   ✅ Success Rate: {recon_result.success_rate}%")
    
    # 3. Win Rate Validation
    print("\n3️⃣ Validating Win Rate...")
    win_rate_report = validator.validate_win_rate(
        period_days=period_days,
        include_statistics=True
    )
    print(f"   ✅ Win Rate: {win_rate_report.overall_win_rate}%")
    if win_rate_report.statistics:
        print(f"   ✅ 95% CI: {win_rate_report.statistics.confidence_interval_95}")
        print(f"   ✅ Statistically Significant: {win_rate_report.statistics.is_statistically_significant}")
    
    # 4. Signal Conversion
    print("\n4️⃣ Checking Signal Conversion...")
    conversion_stats = lifecycle_tracker.get_conversion_stats(period_days=period_days)
    print(f"   ✅ Conversion Rate: {conversion_stats['conversion_rate']}%")
    
    # 5. Generate Reports
    print("\n5️⃣ Generating Reports...")
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Investor report
    investor_report = validator.generate_investor_report(
        period_days=period_days,
        output_format="markdown"
    )
    with open(f"reports/investor_report_{timestamp}.md", "w") as f:
        f.write(investor_report)
    print(f"   ✅ Investor report: reports/investor_report_{timestamp}.md")
    
    # JSON report
    json_report = validator.generate_investor_report(
        period_days=period_days,
        output_format="json"
    )
    with open(f"reports/validation_data_{timestamp}.json", "w") as f:
        json.dump(json_report, f, indent=2)
    print(f"   ✅ JSON data: reports/validation_data_{timestamp}.json")
    
    # Reconciliation report
    recon_report = reconciliation.get_reconciliation_report(period_days=period_days)
    with open(f"reports/reconciliation_{timestamp}.json", "w") as f:
        json.dump(recon_report, f, indent=2)
    print(f"   ✅ Reconciliation: reports/reconciliation_{timestamp}.json")
    
    # Quality report
    quality_report = quality_validator.get_quality_report(period_days=period_days)
    with open(f"reports/quality_{timestamp}.json", "w") as f:
        json.dump(quality_report, f, indent=2)
    print(f"   ✅ Quality report: reports/quality_{timestamp}.json")
    
    print("\n✅ Complete validation package generated!")
    
    return {
        'win_rate': win_rate_report,
        'reconciliation': recon_result,
        'quality': quality_result,
        'conversion': conversion_stats
    }

if __name__ == "__main__":
    generate_complete_validation_package(period_days=30)
```

---

## Best Practices

1. **Run validation regularly**: Weekly for reports, daily for quality checks
2. **Use auto-fix carefully**: Review issues before auto-fixing in production
3. **Monitor conversion rate**: Track signal-to-trade conversion over time
4. **Review breakdowns**: Analyze performance by regime, confidence, exit reason
5. **Include statistics**: Always include statistical validation in reports
6. **Reconcile regularly**: Weekly reconciliation with broker records
7. **Track trends**: Monitor win rate trends over time

---

**For more information, see:** `docs/VALIDATION_SYSTEM_GUIDE.md`


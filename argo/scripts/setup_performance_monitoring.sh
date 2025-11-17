#!/bin/bash
# Setup Performance Monitoring Automation
# Configures automated performance evaluation, trend analysis, and alerting

set -e

# Configuration
ARGO_DIR="${ARGO_DIR:-$(pwd)}"
REPORTS_DIR="${ARGO_DIR}/reports"
LOGS_DIR="${ARGO_DIR}/logs/monitoring"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_step() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Step 1: Create directories
print_step "STEP 1: CREATE DIRECTORIES"

mkdir -p "${REPORTS_DIR}"
mkdir -p "${LOGS_DIR}"
mkdir -p "${ARGO_DIR}/scripts"

print_success "Directories created"

# Step 2: Setup cron jobs
print_step "STEP 2: SETUP AUTOMATED SCHEDULING"

print_info "Setting up cron jobs for performance monitoring..."

# Check if running as root or user
if [ "$EUID" -eq 0 ]; then
    CRON_USER="root"
else
    CRON_USER="$USER"
fi

# Create temporary crontab
TEMP_CRON=$(mktemp)
crontab -l 2>/dev/null > "$TEMP_CRON" || true

# Remove existing performance monitoring jobs
sed -i.bak '/performance_evaluation/d' "$TEMP_CRON" 2>/dev/null || true
sed -i.bak '/performance_trend/d' "$TEMP_CRON" 2>/dev/null || true
sed -i.bak '/performance_optimizer/d' "$TEMP_CRON" 2>/dev/null || true
sed -i.bak '/performance_alert/d' "$TEMP_CRON" 2>/dev/null || true

# Add new cron jobs
cat >> "$TEMP_CRON" << EOF

# Performance Evaluation - Daily at 9 AM
0 9 * * * cd ${ARGO_DIR} && python3 scripts/evaluate_performance_enhanced.py --days 1 --json > ${REPORTS_DIR}/daily_evaluation_\$(date +\%Y\%m\%d).json 2>&1

# Performance Trend Analysis - Weekly on Sundays at 10 AM
0 10 * * 0 cd ${ARGO_DIR} && python3 scripts/performance_trend_analyzer.py --days 7 --output ${REPORTS_DIR}/weekly_trends_\$(date +\%Y\%m\%d).txt 2>&1

# Performance Optimization Check - Daily at 11 AM
0 11 * * * cd ${ARGO_DIR} && python3 scripts/performance_optimizer.py ${REPORTS_DIR}/daily_evaluation_\$(date +\%Y\%m\%d).json --output ${REPORTS_DIR}/daily_optimizations_\$(date +\%Y\%m\%d).txt 2>&1

# Performance Alert Check - Every 6 hours
0 */6 * * * cd ${ARGO_DIR} && python3 scripts/performance_alert.py --check 2>&1 | tee -a ${LOGS_DIR}/alerts.log
EOF

# Install new crontab
crontab "$TEMP_CRON"
rm "$TEMP_CRON"

print_success "Cron jobs configured"
print_info "Scheduled jobs:"
crontab -l | grep -E "(performance|evaluation|trend|optimizer|alert)" || true

# Step 3: Create performance alert script
print_step "STEP 3: CREATE PERFORMANCE ALERT SCRIPT"

cat > "${ARGO_DIR}/scripts/performance_alert.py" << 'PYTHON_SCRIPT'
#!/usr/bin/env python3
"""
Performance Alert System
Checks performance evaluation reports and sends alerts on issues
"""
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional

def find_latest_report(reports_dir: str) -> Optional[Path]:
    """Find latest performance evaluation report"""
    reports_path = Path(reports_dir)
    if not reports_path.exists():
        return None

    reports = list(reports_path.glob("daily_evaluation_*.json"))
    if not reports:
        # Try any evaluation report
        reports = list(reports_path.glob("performance_evaluation*.json"))

    if not reports:
        return None

    # Sort by modification time
    reports.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return reports[0]

def check_performance_alerts(report_path: Path) -> List[Dict]:
    """Check for performance issues and generate alerts"""
    alerts = []

    try:
        with open(report_path, 'r') as f:
            report = json.load(f)
    except Exception as e:
        alerts.append({
            'level': 'error',
            'component': 'system',
            'message': f"Could not read report: {e}",
            'action': 'Check report file'
        })
        return alerts

    # Check each component
    for component in ['signal_generator', 'production_trading', 'prop_firm_trading']:
        if component not in report:
            continue

        comp_data = report[component]
        grade = comp_data.get('performance_grade', 'N/A')
        metrics = comp_data.get('metrics', {})

        # Check for D grade
        if 'D' in grade or 'Needs Improvement' in grade:
            alerts.append({
                'level': 'critical',
                'component': component,
                'message': f"Performance grade is {grade}",
                'action': 'Review recommendations and take action',
                'grade': grade
            })

        # Component-specific checks
        if component == 'signal_generator':
            gen_time = metrics.get('avg_signal_generation_time_seconds', 0)
            cache_hit = metrics.get('cache_hit_rate_percent', 0)

            if gen_time > 1.0:
                alerts.append({
                    'level': 'warning',
                    'component': component,
                    'message': f"Signal generation time is {gen_time:.2f}s (target: <0.3s)",
                    'action': 'Optimize signal generation',
                    'metric': 'generation_time',
                    'value': gen_time,
                    'target': 0.3
                })

            if cache_hit < 30:
                alerts.append({
                    'level': 'warning',
                    'component': component,
                    'message': f"Cache hit rate is {cache_hit:.1f}% (target: >80%)",
                    'action': 'Improve cache strategy',
                    'metric': 'cache_hit_rate',
                    'value': cache_hit,
                    'target': 80
                })

        elif component == 'production_trading':
            win_rate = metrics.get('win_rate_percent', 0)
            profit_factor = metrics.get('profit_factor', 0)

            if win_rate > 0 and win_rate < 35:
                alerts.append({
                    'level': 'warning',
                    'component': component,
                    'message': f"Win rate is {win_rate:.1f}% (target: >45%)",
                    'action': 'Review signal quality and entry criteria',
                    'metric': 'win_rate',
                    'value': win_rate,
                    'target': 45
                })

            if profit_factor > 0 and profit_factor < 1.0:
                alerts.append({
                    'level': 'critical',
                    'component': component,
                    'message': f"Profit factor is {profit_factor:.2f} (target: >1.5)",
                    'action': 'Review risk/reward ratios and exit strategies',
                    'metric': 'profit_factor',
                    'value': profit_factor,
                    'target': 1.5
                })

        elif component == 'prop_firm_trading':
            compliance = metrics.get('compliance_metrics', {})

            # Check for compliance breaches
            drawdown_breaches = compliance.get('drawdown_breaches')
            if drawdown_breaches and drawdown_breaches > 0:
                alerts.append({
                    'level': 'critical',
                    'component': component,
                    'message': f"CRITICAL: {drawdown_breaches} drawdown breach(es) detected",
                    'action': 'IMMEDIATE ACTION REQUIRED - Review risk management',
                    'metric': 'drawdown_breaches',
                    'value': drawdown_breaches
                })

            daily_loss_breaches = compliance.get('daily_loss_breaches')
            if daily_loss_breaches and daily_loss_breaches > 0:
                alerts.append({
                    'level': 'critical',
                    'component': component,
                    'message': f"CRITICAL: {daily_loss_breaches} daily loss breach(es) detected",
                    'action': 'IMMEDIATE ACTION REQUIRED - Review position sizing',
                    'metric': 'daily_loss_breaches',
                    'value': daily_loss_breaches
                })

            trading_halted = compliance.get('trading_halted')
            if trading_halted:
                alerts.append({
                    'level': 'critical',
                    'component': component,
                    'message': "CRITICAL: Trading has been halted",
                    'action': 'Review compliance breaches and resolve before resuming',
                    'metric': 'trading_halted',
                    'value': True
                })

    return alerts

def print_alerts(alerts: List[Dict], json_output: bool = False):
    """Print alerts"""
    if json_output:
        print(json.dumps(alerts, indent=2))
        return

    if not alerts:
        print("✅ No performance alerts")
        return

    critical = [a for a in alerts if a['level'] == 'critical']
    warnings = [a for a in alerts if a['level'] == 'warning']
    errors = [a for a in alerts if a['level'] == 'error']

    print("\n" + "=" * 70)
    print("PERFORMANCE ALERTS")
    print("=" * 70)

    if critical:
        print(f"\n🔴 CRITICAL ALERTS ({len(critical)}):")
        for alert in critical:
            print(f"\n  Component: {alert['component']}")
            print(f"  Message: {alert['message']}")
            print(f"  Action: {alert['action']}")
            if 'metric' in alert:
                print(f"  Metric: {alert['metric']} = {alert.get('value', 'N/A')}")

    if warnings:
        print(f"\n⚠️  WARNINGS ({len(warnings)}):")
        for alert in warnings:
            print(f"\n  Component: {alert['component']}")
            print(f"  Message: {alert['message']}")
            print(f"  Action: {alert['action']}")
            if 'metric' in alert:
                print(f"  Metric: {alert['metric']} = {alert.get('value', 'N/A')}")

    if errors:
        print(f"\n❌ ERRORS ({len(errors)}):")
        for alert in errors:
            print(f"\n  Component: {alert['component']}")
            print(f"  Message: {alert['message']}")
            print(f"  Action: {alert['action']}")

    print("\n" + "=" * 70)

def main():
    parser = argparse.ArgumentParser(description='Performance Alert System')
    parser.add_argument('--check', action='store_true', help='Check for alerts')
    parser.add_argument('--report', help='Path to specific report file')
    parser.add_argument('--reports-dir', default='reports', help='Reports directory')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--exit-code', action='store_true', help='Exit with non-zero code if alerts found')

    args = parser.parse_args()

    # Find report
    if args.report:
        report_path = Path(args.report)
    else:
        report_path = find_latest_report(args.reports_dir)

    if not report_path or not report_path.exists():
        print("⚠️  No performance evaluation report found")
        if args.exit_code:
            sys.exit(1)
        return

    # Check for alerts
    alerts = check_performance_alerts(report_path)

    # Print alerts
    print_alerts(alerts, args.json)

    # Exit code
    if args.exit_code:
        critical_count = len([a for a in alerts if a['level'] == 'critical'])
        if critical_count > 0:
            sys.exit(2)  # Critical alerts
        elif len(alerts) > 0:
            sys.exit(1)  # Warnings/errors
        else:
            sys.exit(0)  # No alerts

if __name__ == '__main__':
    main()
PYTHON_SCRIPT

chmod +x "${ARGO_DIR}/scripts/performance_alert.py"
print_success "Performance alert script created"

# Step 4: Create automated optimization workflow
print_step "STEP 4: CREATE AUTOMATED OPTIMIZATION WORKFLOW"

cat > "${ARGO_DIR}/scripts/auto_optimize.py" << 'PYTHON_SCRIPT'
#!/usr/bin/env python3
"""
Automated Optimization Workflow
Runs evaluation, analyzes with optimizer, and suggests configuration changes
"""
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List

def run_evaluation(days: int = 1) -> Path:
    """Run performance evaluation"""
    print(f"📊 Running performance evaluation for last {days} days...")

    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)

    output_file = reports_dir / f"auto_evaluation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    result = subprocess.run(
        ["python3", "scripts/evaluate_performance_enhanced.py", "--days", str(days), "--json"],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"❌ Evaluation failed: {result.stderr}")
        sys.exit(1)

    # Save output
    with open(output_file, 'w') as f:
        f.write(result.stdout)

    print(f"✅ Evaluation complete: {output_file}")
    return output_file

def run_optimizer(report_path: Path) -> Dict:
    """Run performance optimizer"""
    print(f"🔍 Analyzing optimizations...")

    result = subprocess.run(
        ["python3", "scripts/performance_optimizer.py", str(report_path), "--json"],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"❌ Optimization analysis failed: {result.stderr}")
        return {}

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"⚠️  Could not parse optimizer output")
        return {}

def suggest_config_changes(optimizations: Dict) -> List[Dict]:
    """Suggest configuration changes based on optimizations"""
    suggestions = []

    if 'optimizations' not in optimizations:
        return suggestions

    for opt in optimizations['optimizations']:
        if opt.get('priority') in ['critical', 'high']:
            component = opt.get('component')
            metric = opt.get('metric')
            actions = opt.get('actions', [])

            # Map to config changes
            if component == 'signal_generator' and 'cache' in metric.lower():
                suggestions.append({
                    'type': 'config',
                    'component': 'signal_generator',
                    'change': 'Increase cache TTL',
                    'reason': opt.get('recommendation'),
                    'actions': actions
                })

            elif component == 'signal_generator' and 'generation_time' in metric.lower():
                suggestions.append({
                    'type': 'config',
                    'component': 'signal_generator',
                    'change': 'Optimize API calls',
                    'reason': opt.get('recommendation'),
                    'actions': actions
                })

            elif component == 'production_trading' and 'win_rate' in metric.lower():
                suggestions.append({
                    'type': 'config',
                    'component': 'trading',
                    'change': 'Increase minimum confidence threshold',
                    'reason': opt.get('recommendation'),
                    'actions': actions
                })

    return suggestions

def print_suggestions(suggestions: List[Dict]):
    """Print optimization suggestions"""
    if not suggestions:
        print("\n✅ No critical optimizations needed")
        return

    print("\n" + "=" * 70)
    print("OPTIMIZATION SUGGESTIONS")
    print("=" * 70)

    for i, suggestion in enumerate(suggestions, 1):
        print(f"\n{i}. {suggestion['component'].upper()}: {suggestion['change']}")
        print(f"   Reason: {suggestion['reason']}")
        print(f"   Actions:")
        for action in suggestion.get('actions', [])[:3]:  # Top 3 actions
            print(f"     • {action}")

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Automated Optimization Workflow')
    parser.add_argument('--days', type=int, default=1, help='Days to evaluate')
    parser.add_argument('--apply', action='store_true', help='Apply safe optimizations (not implemented yet)')
    parser.add_argument('--json', action='store_true', help='Output as JSON')

    args = parser.parse_args()

    # Step 1: Run evaluation
    report_path = run_evaluation(args.days)

    # Step 2: Run optimizer
    optimizations = run_optimizer(report_path)

    if not optimizations:
        print("⚠️  No optimization data available")
        return

    # Step 3: Generate suggestions
    suggestions = suggest_config_changes(optimizations)

    # Step 4: Print results
    if args.json:
        print(json.dumps({
            'report': str(report_path),
            'optimizations': optimizations,
            'suggestions': suggestions
        }, indent=2))
    else:
        print_suggestions(suggestions)

        if args.apply:
            print("\n⚠️  Auto-apply not yet implemented. Review suggestions manually.")

if __name__ == '__main__':
    main()
PYTHON_SCRIPT

chmod +x "${ARGO_DIR}/scripts/auto_optimize.py"
print_success "Automated optimization workflow created"

# Step 5: Create summary script
print_step "STEP 5: CREATE PERFORMANCE SUMMARY SCRIPT"

cat > "${ARGO_DIR}/scripts/performance_summary.py" << 'PYTHON_SCRIPT'
#!/usr/bin/env python3
"""
Performance Summary
Quick summary of current performance status
"""
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta

def get_latest_report(reports_dir: str = "reports") -> Path:
    """Get latest evaluation report"""
    reports_path = Path(reports_dir)
    if not reports_path.exists():
        return None

    reports = list(reports_path.glob("daily_evaluation_*.json"))
    if not reports:
        reports = list(reports_path.glob("performance_evaluation*.json"))

    if not reports:
        return None

    reports.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return reports[0]

def print_summary(report_path: Path):
    """Print performance summary"""
    try:
        with open(report_path, 'r') as f:
            report = json.load(f)
    except Exception:
        print("❌ Could not read report")
        return

    print("\n" + "=" * 70)
    print("PERFORMANCE SUMMARY")
    print("=" * 70)
    print(f"Report: {report_path.name}")
    print(f"Date: {datetime.fromtimestamp(report_path.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    for component in ['signal_generator', 'production_trading', 'prop_firm_trading']:
        if component not in report:
            continue

        comp_data = report[component]
        grade = comp_data.get('performance_grade', 'N/A')
        metrics = comp_data.get('metrics', {})

        print(f"{component.replace('_', ' ').title()}: {grade}")

        if component == 'signal_generator':
            print(f"  Generation Time: {metrics.get('avg_signal_generation_time_seconds', 0):.3f}s")
            print(f"  Cache Hit Rate: {metrics.get('cache_hit_rate_percent', 0):.1f}%")
        elif component == 'production_trading':
            print(f"  Win Rate: {metrics.get('win_rate_percent', 0):.1f}%")
            print(f"  Profit Factor: {metrics.get('profit_factor', 0):.2f}")
            print(f"  Total Trades: {metrics.get('completed_trades', 0)}")
        elif component == 'prop_firm_trading':
            compliance = metrics.get('compliance_metrics', {})
            print(f"  Win Rate: {metrics.get('win_rate_percent', 0):.1f}%")
            if compliance.get('drawdown_breaches'):
                print(f"  ⚠️  Drawdown Breaches: {compliance.get('drawdown_breaches')}")
            if compliance.get('daily_loss_breaches'):
                print(f"  ⚠️  Daily Loss Breaches: {compliance.get('daily_loss_breaches')}")
        print()

if __name__ == '__main__':
    report = get_latest_report()
    if report:
        print_summary(report)
    else:
        print("⚠️  No performance reports found. Run evaluation first.")
PYTHON_SCRIPT

chmod +x "${ARGO_DIR}/scripts/performance_summary.py"
print_success "Performance summary script created"

# Final summary
print_step "SETUP COMPLETE"

print_success "Performance monitoring automation configured!"
print_info "Scheduled tasks:"
print "  • Daily evaluation at 9 AM"
print "  • Weekly trend analysis on Sundays at 10 AM"
print "  • Daily optimization check at 11 AM"
print "  • Alert checks every 6 hours"
print ""
print_info "New scripts created:"
print "  • scripts/performance_alert.py - Alert checking"
print "  • scripts/auto_optimize.py - Automated optimization workflow"
print "  • scripts/performance_summary.py - Quick performance summary"
print ""
print_info "To test:"
print "  python3 scripts/performance_summary.py"
print "  python3 scripts/performance_alert.py --check"
print "  python3 scripts/auto_optimize.py"
print ""
print_success "Setup complete!"

#!/usr/bin/env python3
"""
Performance Comparator
Compares two performance evaluation reports to identify changes
"""
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

class PerformanceComparator:
    """Compare two performance evaluation reports"""

    def compare_reports(self, report1_path: str, report2_path: str) -> Dict:
        """Compare two reports"""
        try:
            with open(report1_path, 'r') as f:
                report1 = json.load(f)
            with open(report2_path, 'r') as f:
                report2 = json.load(f)
        except Exception as e:
            return {'error': f"Could not load reports: {e}"}

        comparison = {
            'report1': report1_path,
            'report2': report2_path,
            'report1_date': self._get_report_date(report1),
            'report2_date': self._get_report_date(report2),
            'components': {}
        }

        # Compare each component
        components = ['signal_generator', 'production_trading', 'prop_firm_trading']

        for component in components:
            if component in report1 or component in report2:
                comp_comparison = self._compare_component(
                    report1.get(component, {}),
                    report2.get(component, {})
                )
                if comp_comparison:
                    comparison['components'][component] = comp_comparison

        return comparison

    def _get_report_date(self, report: Dict) -> Optional[str]:
        """Extract report date"""
        for component in ['signal_generator', 'production_trading', 'prop_firm_trading']:
            if component in report:
                eval_date = report[component].get('evaluation_date')
                if eval_date:
                    return eval_date
        return None

    def _compare_component(self, comp1: Dict, comp2: Dict) -> Optional[Dict]:
        """Compare a component between two reports"""
        if not comp1 and not comp2:
            return None

        metrics1 = comp1.get('metrics', {}) if comp1 else {}
        metrics2 = comp2.get('metrics', {}) if comp2 else {}

        grade1 = comp1.get('performance_grade', 'N/A') if comp1 else 'N/A'
        grade2 = comp2.get('performance_grade', 'N/A') if comp2 else 'N/A'

        comparison = {
            'grade_change': {
                'before': grade1,
                'after': grade2,
                'improved': self._grade_improved(grade1, grade2)
            },
            'metrics_changes': {},
            'improvements': [],
            'degradations': [],
            'new_metrics': [],
            'removed_metrics': []
        }

        # Compare metrics
        all_metrics = set(list(metrics1.keys()) + list(metrics2.keys()))

        for metric in all_metrics:
            value1 = metrics1.get(metric)
            value2 = metrics2.get(metric)

            if value1 is None:
                comparison['new_metrics'].append({
                    'metric': metric,
                    'value': value2
                })
            elif value2 is None:
                comparison['removed_metrics'].append({
                    'metric': metric,
                    'value': value1
                })
            elif isinstance(value1, (int, float)) and isinstance(value2, (int, float)):
                change = value2 - value1
                change_pct = (change / value1 * 100) if value1 != 0 else 0

                comparison['metrics_changes'][metric] = {
                    'before': value1,
                    'after': value2,
                    'change': change,
                    'change_pct': change_pct
                }

                # Categorize as improvement or degradation
                if self._is_improvement(metric, change):
                    comparison['improvements'].append({
                        'metric': metric,
                        'change': change,
                        'change_pct': change_pct,
                        'before': value1,
                        'after': value2
                    })
                elif self._is_degradation(metric, change):
                    comparison['degradations'].append({
                        'metric': metric,
                        'change': change,
                        'change_pct': change_pct,
                        'before': value1,
                        'after': value2
                    })

        return comparison

    def _grade_improved(self, grade1: str, grade2: str) -> Optional[bool]:
        """Check if grade improved"""
        grade_order = {'A': 4, 'B': 3, 'C': 2, 'D': 1, 'N/A': 0}

        score1 = grade_order.get(grade1[0] if grade1 else 'N/A', 0)
        score2 = grade_order.get(grade2[0] if grade2 else 'N/A', 0)

        if score1 == 0 or score2 == 0:
            return None

        return score2 > score1

    def _is_improvement(self, metric: str, change: float) -> bool:
        """Check if change is an improvement"""
        # For most metrics, increase is good
        improvement_metrics = [
            'cache_hit_rate', 'win_rate', 'profit_factor', 'return',
            'total_pnl', 'avg_win', 'skip_rate'
        ]

        # For some metrics, decrease is good
        decrease_metrics = [
            'generation_time', 'api_latency', 'max_drawdown', 'daily_loss'
        ]

        for imp_metric in improvement_metrics:
            if imp_metric in metric.lower():
                return change > 0

        for dec_metric in decrease_metrics:
            if dec_metric in metric.lower():
                return change < 0

        return False

    def _is_degradation(self, metric: str, change: float) -> bool:
        """Check if change is a degradation"""
        return not self._is_improvement(metric, change) and change != 0

    def generate_comparison_report(self, comparison: Dict, output_path: Optional[str] = None) -> str:
        """Generate formatted comparison report"""
        if 'error' in comparison:
            return f"Error: {comparison['error']}"

        report_lines = [
            "=" * 70,
            "PERFORMANCE COMPARISON REPORT",
            "=" * 70,
            f"\nReport 1: {Path(comparison['report1']).name}",
            f"  Date: {comparison['report1_date']}",
            f"\nReport 2: {Path(comparison['report2']).name}",
            f"  Date: {comparison['report2_date']}",
            "\n" + "=" * 70
        ]

        for component, comp_comp in comparison['components'].items():
            report_lines.append(f"\n{component.replace('_', ' ').title().upper()}")
            report_lines.append("-" * 70)

            # Grade change
            grade_change = comp_comp['grade_change']
            report_lines.append(f"\n📊 Performance Grade:")
            report_lines.append(f"  Before: {grade_change['before']}")
            report_lines.append(f"  After: {grade_change['after']}")
            if grade_change['improved'] is True:
                report_lines.append(f"  Status: ✅ Improved")
            elif grade_change['improved'] is False:
                report_lines.append(f"  Status: ⚠️  Degraded")
            else:
                report_lines.append(f"  Status: ➡️  No change")

            # Improvements
            if comp_comp['improvements']:
                report_lines.append(f"\n✅ Improvements ({len(comp_comp['improvements'])}):")
                for imp in comp_comp['improvements']:
                    report_lines.append(f"  • {imp['metric']}:")
                    report_lines.append(f"    {imp['before']:.2f} → {imp['after']:.2f} ({imp['change_pct']:+.1f}%)")

            # Degradations
            if comp_comp['degradations']:
                report_lines.append(f"\n⚠️  Degradations ({len(comp_comp['degradations'])}):")
                for deg in comp_comp['degradations']:
                    report_lines.append(f"  • {deg['metric']}:")
                    report_lines.append(f"    {deg['before']:.2f} → {deg['after']:.2f} ({deg['change_pct']:+.1f}%)")

            # New metrics
            if comp_comp['new_metrics']:
                report_lines.append(f"\n➕ New Metrics ({len(comp_comp['new_metrics'])}):")
                for new in comp_comp['new_metrics']:
                    report_lines.append(f"  • {new['metric']}: {new['value']}")

            # Removed metrics
            if comp_comp['removed_metrics']:
                report_lines.append(f"\n➖ Removed Metrics ({len(comp_comp['removed_metrics'])}):")
                for rem in comp_comp['removed_metrics']:
                    report_lines.append(f"  • {rem['metric']}: {rem['value']}")

        report_text = "\n".join(report_lines)

        if output_path:
            with open(output_path, 'w') as f:
                f.write(report_text)

        return report_text

def main():
    parser = argparse.ArgumentParser(description='Performance Comparator')
    parser.add_argument('report1', help='First performance report (before)')
    parser.add_argument('report2', help='Second performance report (after)')
    parser.add_argument('--output', '-o', help='Output file for comparison report')
    parser.add_argument('--json', action='store_true', help='Output as JSON')

    args = parser.parse_args()

    comparator = PerformanceComparator()

    print(f"📊 Comparing reports...")
    comparison = comparator.compare_reports(args.report1, args.report2)

    if args.json:
        print(json.dumps(comparison, indent=2, default=str))
    else:
        report = comparator.generate_comparison_report(comparison, args.output)
        print(report)
        if args.output:
            print(f"\n💾 Comparison report saved to: {args.output}")

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Performance Trend Analyzer
Analyzes performance trends over time by comparing multiple evaluation reports
"""
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent))

class PerformanceTrendAnalyzer:
    """Analyze performance trends across multiple evaluation reports"""

    def __init__(self):
        self.reports = []

    def load_reports(self, reports_dir: str, days: int = 30) -> List[Dict]:
        """Load all reports from directory within time period"""
        reports_path = Path(reports_dir)
        if not reports_path.exists():
            return []

        cutoff_date = datetime.now() - timedelta(days=days)
        reports = []

        # Find all evaluation reports
        for report_file in reports_path.glob("performance_evaluation*.json"):
            try:
                # Try to parse date from filename
                with open(report_file, 'r') as f:
                    report = json.load(f)

                # Get evaluation date
                eval_date = None
                if 'signal_generator' in report:
                    eval_date_str = report['signal_generator'].get('evaluation_date')
                    if eval_date_str:
                        eval_date = datetime.fromisoformat(eval_date_str.replace('Z', '+00:00'))

                if eval_date and eval_date >= cutoff_date:
                    reports.append({
                        'file': str(report_file),
                        'date': eval_date,
                        'data': report
                    })
            except Exception as e:
                print(f"⚠️  Could not load {report_file}: {e}")

        # Sort by date
        reports.sort(key=lambda x: x['date'])
        return reports

    def analyze_trends(self, reports: List[Dict], component: str = 'all') -> Dict:
        """Analyze trends across reports"""
        if not reports:
            return {'error': 'No reports found'}

        trends = {
            'period_start': reports[0]['date'].isoformat(),
            'period_end': reports[-1]['date'].isoformat(),
            'total_reports': len(reports),
            'components': {}
        }

        components_to_analyze = ['signal_generator', 'production_trading', 'prop_firm_trading']
        if component != 'all':
            components_to_analyze = [component]

        for comp in components_to_analyze:
            comp_trends = self._analyze_component_trend(reports, comp)
            if comp_trends:
                trends['components'][comp] = comp_trends

        return trends

    def _analyze_component_trend(self, reports: List[Dict], component: str) -> Optional[Dict]:
        """Analyze trends for a specific component"""
        component_data = []

        for report in reports:
            if component in report['data']:
                comp_data = report['data'][component]
                metrics = comp_data.get('metrics', {})
                grade = comp_data.get('performance_grade', 'N/A')

                component_data.append({
                    'date': report['date'],
                    'metrics': metrics,
                    'grade': grade
                })

        if not component_data:
            return None

        # Extract key metrics over time
        trend_data = {
            'data_points': len(component_data),
            'metrics_trends': {},
            'grade_trend': [],
            'improvements': [],
            'degradations': []
        }

        # Track key metrics
        key_metrics = self._get_key_metrics(component)

        for metric_name in key_metrics:
            values = []
            dates = []

            for data_point in component_data:
                value = self._extract_metric_value(data_point['metrics'], metric_name)
                if value is not None:
                    values.append(value)
                    dates.append(data_point['date'])

            if values:
                trend_data['metrics_trends'][metric_name] = {
                    'values': values,
                    'dates': [d.isoformat() for d in dates],
                    'first': values[0],
                    'last': values[-1],
                    'change': values[-1] - values[0] if len(values) > 1 else 0,
                    'change_pct': ((values[-1] - values[0]) / values[0] * 100) if len(values) > 1 and values[0] != 0 else 0,
                    'trend': self._calculate_trend(values),
                    'avg': sum(values) / len(values),
                    'min': min(values),
                    'max': max(values)
                }

        # Grade trend
        for data_point in component_data:
            trend_data['grade_trend'].append({
                'date': data_point['date'].isoformat(),
                'grade': data_point['grade']
            })

        # Identify improvements and degradations
        if len(component_data) >= 2:
            first = component_data[0]
            last = component_data[-1]

            for metric_name, trend_info in trend_data['metrics_trends'].items():
                change = trend_info['change']
                target = self._get_metric_target(component, metric_name)

                if change > 0 and target and trend_info['last'] < target:
                    # Improving but not at target
                    trend_data['improvements'].append({
                        'metric': metric_name,
                        'change': change,
                        'change_pct': trend_info['change_pct'],
                        'current': trend_info['last'],
                        'target': target
                    })
                elif change < 0:
                    # Degrading
                    trend_data['degradations'].append({
                        'metric': metric_name,
                        'change': change,
                        'change_pct': trend_info['change_pct'],
                        'current': trend_info['last']
                    })

        return trend_data

    def _get_key_metrics(self, component: str) -> List[str]:
        """Get key metrics for a component"""
        if component == 'signal_generator':
            return [
                'avg_signal_generation_time_seconds',
                'cache_hit_rate_percent',
                'skip_rate_percent',
                'avg_api_latency_seconds'
            ]
        elif component == 'production_trading':
            return [
                'win_rate_percent',
                'profit_factor',
                'return_percent',
                'total_pnl_dollars'
            ]
        elif component == 'prop_firm_trading':
            return [
                'win_rate_percent',
                'profit_factor',
                'return_percent',
                'compliance_metrics.max_drawdown_pct'
            ]
        return []

    def _extract_metric_value(self, metrics: Dict, metric_path: str) -> Optional[float]:
        """Extract metric value, supporting nested paths"""
        if '.' in metric_path:
            parts = metric_path.split('.')
            value = metrics
            for part in parts:
                if isinstance(value, dict):
                    value = value.get(part)
                else:
                    return None
            return value if isinstance(value, (int, float)) else None
        else:
            value = metrics.get(metric_path)
            return value if isinstance(value, (int, float)) else None

    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction"""
        if len(values) < 2:
            return 'insufficient_data'

        # Simple linear trend
        first_half = values[:len(values)//2]
        second_half = values[len(values)//2:]

        first_avg = sum(first_half) / len(first_half)
        second_avg = sum(second_half) / len(second_half)

        change_pct = ((second_avg - first_avg) / first_avg * 100) if first_avg != 0 else 0

        if change_pct > 5:
            return 'improving'
        elif change_pct < -5:
            return 'degrading'
        else:
            return 'stable'

    def _get_metric_target(self, component: str, metric: str) -> Optional[float]:
        """Get target value for a metric"""
        targets = {
            'signal_generator': {
                'avg_signal_generation_time_seconds': 0.3,
                'cache_hit_rate_percent': 80.0,
                'skip_rate_percent': 40.0
            },
            'production_trading': {
                'win_rate_percent': 45.0,
                'profit_factor': 1.5,
                'return_percent': 10.0
            },
            'prop_firm_trading': {
                'win_rate_percent': 45.0,
                'profit_factor': 1.5,
                'compliance_metrics.max_drawdown_pct': 2.0
            }
        }

        return targets.get(component, {}).get(metric)

    def generate_trend_report(self, trends: Dict, output_path: Optional[str] = None) -> str:
        """Generate formatted trend report"""
        if 'error' in trends:
            return f"Error: {trends['error']}"

        report_lines = [
            "=" * 70,
            "PERFORMANCE TREND ANALYSIS",
            "=" * 70,
            f"\nPeriod: {trends['period_start']} to {trends['period_end']}",
            f"Total Reports Analyzed: {trends['total_reports']}",
            "\n" + "=" * 70
        ]

        for component, comp_trends in trends['components'].items():
            report_lines.append(f"\n{component.replace('_', ' ').title().upper()}")
            report_lines.append("-" * 70)
            report_lines.append(f"Data Points: {comp_trends['data_points']}")

            # Metrics trends
            if comp_trends['metrics_trends']:
                report_lines.append("\n📊 Metrics Trends:")
                for metric_name, trend_info in comp_trends['metrics_trends'].items():
                    report_lines.append(f"\n  {metric_name}:")
                    report_lines.append(f"    First: {trend_info['first']:.2f}")
                    report_lines.append(f"    Last: {trend_info['last']:.2f}")
                    report_lines.append(f"    Change: {trend_info['change']:+.2f} ({trend_info['change_pct']:+.1f}%)")
                    report_lines.append(f"    Trend: {trend_info['trend']}")
                    report_lines.append(f"    Average: {trend_info['avg']:.2f}")
                    report_lines.append(f"    Range: {trend_info['min']:.2f} - {trend_info['max']:.2f}")

            # Improvements
            if comp_trends['improvements']:
                report_lines.append("\n✅ Improvements:")
                for imp in comp_trends['improvements']:
                    report_lines.append(f"  • {imp['metric']}: {imp['change']:+.2f} ({imp['change_pct']:+.1f}%)")

            # Degradations
            if comp_trends['degradations']:
                report_lines.append("\n⚠️  Degradations:")
                for deg in comp_trends['degradations']:
                    report_lines.append(f"  • {deg['metric']}: {deg['change']:+.2f} ({deg['change_pct']:+.1f}%)")

        report_text = "\n".join(report_lines)

        if output_path:
            with open(output_path, 'w') as f:
                f.write(report_text)

        return report_text

def main():
    parser = argparse.ArgumentParser(description='Performance Trend Analyzer')
    parser.add_argument('--reports-dir', default='reports', help='Directory containing evaluation reports')
    parser.add_argument('--days', type=int, default=30, help='Number of days to analyze')
    parser.add_argument('--component', choices=['all', 'signal_generator', 'production_trading', 'prop_firm_trading'],
                       default='all', help='Component to analyze')
    parser.add_argument('--output', '-o', help='Output file for trend report')
    parser.add_argument('--json', action='store_true', help='Output as JSON')

    args = parser.parse_args()

    analyzer = PerformanceTrendAnalyzer()

    # Load reports
    print(f"📂 Loading reports from {args.reports_dir}...")
    reports = analyzer.load_reports(args.reports_dir, args.days)

    if not reports:
        print(f"❌ No reports found in {args.reports_dir}")
        return

    print(f"✅ Loaded {len(reports)} reports")

    # Analyze trends
    print(f"📊 Analyzing trends...")
    trends = analyzer.analyze_trends(reports, args.component)

    if args.json:
        print(json.dumps(trends, indent=2, default=str))
    else:
        report = analyzer.generate_trend_report(trends, args.output)
        print(report)
        if args.output:
            print(f"\n💾 Trend report saved to: {args.output}")

if __name__ == '__main__':
    main()

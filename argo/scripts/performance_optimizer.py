#!/usr/bin/env python3
"""
Performance Optimization Utilities
Provides optimization recommendations and automated fixes for performance issues
"""
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PerformanceOptimizer:
    """Provides performance optimization recommendations and fixes"""

    def __init__(self):
        self.optimizations = []

    def analyze_performance_report(self, report_path: str) -> Dict:
        """Analyze a performance evaluation report and provide optimizations with improved error handling"""
        try:
            report_file = Path(report_path)
            if not report_file.exists():
                error_msg = f"Report file does not exist: {report_path}"
                logger.error(error_msg)
                return {'error': error_msg}
            
            with open(report_file, 'r') as f:
                report = json.load(f)
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON in report: {e}"
            logger.error(f"{error_msg} - File: {report_path}")
            return {'error': error_msg}
        except PermissionError as e:
            error_msg = f"Permission denied reading report: {e}"
            logger.error(f"{error_msg} - File: {report_path}")
            return {'error': error_msg}
        except Exception as e:
            error_msg = f"Could not load report: {e}"
            logger.error(f"{error_msg} - File: {report_path}", exc_info=True)
            return {'error': error_msg}

        optimizations = []

        # Analyze signal generator
        if 'signal_generator' in report:
            sg_metrics = report['signal_generator'].get('metrics', {})
            optimizations.extend(self._optimize_signal_generator(sg_metrics))

        # Analyze production trading
        if 'production_trading' in report:
            pt_metrics = report['production_trading'].get('metrics', {})
            optimizations.extend(self._optimize_production_trading(pt_metrics))

        # Analyze prop firm trading
        if 'prop_firm_trading' in report:
            pf_metrics = report['prop_firm_trading'].get('metrics', {})
            optimizations.extend(self._optimize_prop_firm_trading(pf_metrics))

        return {
            'timestamp': datetime.now().isoformat(),
            'report_analyzed': report_path,
            'optimizations': optimizations,
            'priority': self._prioritize_optimizations(optimizations)
        }

    def _optimize_signal_generator(self, metrics: Dict) -> List[Dict]:
        """Generate optimizations for signal generator"""
        optimizations = []

        gen_time = metrics.get('avg_signal_generation_time_seconds', 0)
        cache_hit = metrics.get('cache_hit_rate_percent', 0)
        skip_rate = metrics.get('skip_rate_percent', 0)

        # Generation time optimization
        if gen_time > 0.7:
            optimizations.append({
                'component': 'signal_generator',
                'metric': 'generation_time',
                'current_value': gen_time,
                'target_value': 0.3,
                'priority': 'high',
                'recommendation': 'Optimize data source API calls',
                'actions': [
                    'Increase cache TTL for stable symbols',
                    'Implement parallel API calls where possible',
                    'Add request batching for multiple symbols',
                    'Consider using WebSocket connections for real-time data'
                ],
                'expected_improvement': f"Reduce generation time by {((gen_time - 0.3) / gen_time * 100):.1f}%"
            })

        # Cache optimization
        if cache_hit < 50:
            optimizations.append({
                'component': 'signal_generator',
                'metric': 'cache_hit_rate',
                'current_value': cache_hit,
                'target_value': 80,
                'priority': 'high',
                'recommendation': 'Improve cache strategy',
                'actions': [
                    'Increase cache TTL from current value',
                    'Implement adaptive cache TTL based on volatility',
                    'Cache intermediate calculations',
                    'Use Redis for distributed caching'
                ],
                'expected_improvement': f"Increase cache hit rate to 80%+ (current: {cache_hit:.1f}%)"
            })

        # Skip rate optimization
        if skip_rate < 20:
            optimizations.append({
                'component': 'signal_generator',
                'metric': 'skip_rate',
                'current_value': skip_rate,
                'target_value': 35,
                'priority': 'medium',
                'recommendation': 'Optimize skip logic',
                'actions': [
                    'Lower price change threshold for skipping',
                    'Implement volatility-based skipping',
                    'Skip symbols with low trading volume'
                ],
                'expected_improvement': f"Increase skip rate to 30-50% (current: {skip_rate:.1f}%)"
            })
        elif skip_rate > 60:
            optimizations.append({
                'component': 'signal_generator',
                'metric': 'skip_rate',
                'current_value': skip_rate,
                'target_value': 40,
                'priority': 'medium',
                'recommendation': 'Reduce skip rate (too aggressive)',
                'actions': [
                    'Increase price change threshold',
                    'Review skip logic for false positives',
                    'Ensure important signals are not skipped'
                ],
                'expected_improvement': f"Reduce skip rate to 30-50% (current: {skip_rate:.1f}%)"
            })

        return optimizations

    def _optimize_production_trading(self, metrics: Dict) -> List[Dict]:
        """Generate optimizations for production trading"""
        optimizations = []

        win_rate = metrics.get('win_rate_percent', 0)
        profit_factor = metrics.get('profit_factor', 0)
        return_pct = metrics.get('return_percent', 0)
        total_trades = metrics.get('completed_trades', 0)

        if total_trades == 0:
            return optimizations

        # Win rate optimization
        if win_rate < 40:
            optimizations.append({
                'component': 'production_trading',
                'metric': 'win_rate',
                'current_value': win_rate,
                'target_value': 45,
                'priority': 'high',
                'recommendation': 'Improve signal quality and entry criteria',
                'actions': [
                    'Increase minimum confidence threshold',
                    'Add additional filters (volume, volatility)',
                    'Review and improve signal generation logic',
                    'Implement regime-based filtering'
                ],
                'expected_improvement': f"Increase win rate to 45%+ (current: {win_rate:.1f}%)"
            })

        # Profit factor optimization
        if profit_factor < 1.2:
            optimizations.append({
                'component': 'production_trading',
                'metric': 'profit_factor',
                'current_value': profit_factor,
                'target_value': 1.5,
                'priority': 'high',
                'recommendation': 'Improve risk/reward ratios',
                'actions': [
                    'Adjust stop-loss and take-profit levels',
                    'Implement trailing stops',
                    'Review exit strategies',
                    'Consider partial profit taking'
                ],
                'expected_improvement': f"Increase profit factor to 1.5+ (current: {profit_factor:.2f})"
            })

        # Return optimization
        if return_pct < 5:
            optimizations.append({
                'component': 'production_trading',
                'metric': 'return',
                'current_value': return_pct,
                'target_value': 10,
                'priority': 'medium',
                'recommendation': 'Optimize position sizing and frequency',
                'actions': [
                    'Review position sizing algorithm',
                    'Increase trading frequency if signals are good',
                    'Optimize capital allocation',
                    'Consider portfolio diversification'
                ],
                'expected_improvement': f"Increase return to 10%+ (current: {return_pct:.1f}%)"
            })

        return optimizations

    def _optimize_prop_firm_trading(self, metrics: Dict) -> List[Dict]:
        """Generate optimizations for prop firm trading"""
        optimizations = []

        # Prop firm specific optimizations
        compliance = metrics.get('compliance_metrics', {})
        if not compliance:
            return optimizations

        drawdown_breaches = compliance.get('drawdown_breaches')
        if drawdown_breaches is not None and drawdown_breaches > 0:
            optimizations.append({
                'component': 'prop_firm_trading',
                'metric': 'drawdown_compliance',
                'current_value': compliance.get('max_drawdown_pct', 0),
                'target_value': 2.0,
                'priority': 'critical',
                'recommendation': 'CRITICAL: Reduce drawdown immediately',
                'actions': [
                    'Reduce position sizes by 50%',
                    'Increase stop-loss tightness',
                    'Pause trading if drawdown > 1.5%',
                    'Review all open positions'
                ],
                'expected_improvement': 'Prevent account termination'
            })

        daily_loss_breaches = compliance.get('daily_loss_breaches')
        if daily_loss_breaches is not None and daily_loss_breaches > 0:
            optimizations.append({
                'component': 'prop_firm_trading',
                'metric': 'daily_loss_compliance',
                'current_value': compliance.get('daily_loss_pct', 0),
                'target_value': 4.5,
                'priority': 'critical',
                'recommendation': 'CRITICAL: Implement daily loss limits',
                'actions': [
                    'Set hard daily loss limit at 3.5%',
                    'Stop trading for the day if limit reached',
                    'Review risk management rules',
                    'Implement position-level stop losses'
                ],
                'expected_improvement': 'Prevent daily loss limit breaches'
            })

        return optimizations

    def _prioritize_optimizations(self, optimizations: List[Dict]) -> Dict:
        """Prioritize optimizations by impact"""
        critical = [o for o in optimizations if o.get('priority') == 'critical']
        high = [o for o in optimizations if o.get('priority') == 'high']
        medium = [o for o in optimizations if o.get('priority') == 'medium']
        low = [o for o in optimizations if o.get('priority') == 'low']

        return {
            'critical': len(critical),
            'high': len(high),
            'medium': len(medium),
            'low': len(low),
            'total': len(optimizations)
        }

    def generate_optimization_report(self, report_path: str, output_path: Optional[str] = None) -> str:
        """Generate a formatted optimization report"""
        analysis = self.analyze_performance_report(report_path)

        if 'error' in analysis:
            return f"Error: {analysis['error']}"

        report_lines = [
            "=" * 70,
            "PERFORMANCE OPTIMIZATION REPORT",
            "=" * 70,
            f"\nGenerated: {analysis['timestamp']}",
            f"Report Analyzed: {analysis['report_analyzed']}",
            f"\nTotal Optimizations: {analysis['priority']['total']}",
            f"  Critical: {analysis['priority']['critical']}",
            f"  High: {analysis['priority']['high']}",
            f"  Medium: {analysis['priority']['medium']}",
            f"  Low: {analysis['priority']['low']}",
            "\n" + "=" * 70,
            "OPTIMIZATION RECOMMENDATIONS",
            "=" * 70
        ]

        # Group by priority
        for priority in ['critical', 'high', 'medium', 'low']:
            priority_ops = [o for o in analysis['optimizations'] if o.get('priority') == priority]
            if priority_ops:
                report_lines.append(f"\n{priority.upper()} PRIORITY:")
                report_lines.append("-" * 70)

                for i, opt in enumerate(priority_ops, 1):
                    report_lines.append(f"\n{i}. {opt['component'].replace('_', ' ').title()} - {opt['metric']}")
                    report_lines.append(f"   Current: {opt['current_value']} | Target: {opt['target_value']}")
                    report_lines.append(f"   Recommendation: {opt['recommendation']}")
                    report_lines.append(f"   Expected Improvement: {opt['expected_improvement']}")
                    report_lines.append(f"   Actions:")
                    for action in opt['actions']:
                        report_lines.append(f"     • {action}")

        report_text = "\n".join(report_lines)

        if output_path:
            with open(output_path, 'w') as f:
                f.write(report_text)

        return report_text

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Performance Optimization Analyzer')
    parser.add_argument('report', help='Path to performance evaluation report JSON')
    parser.add_argument('--output', '-o', help='Output file for optimization report')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        optimizer = PerformanceOptimizer()

        if args.json:
            analysis = optimizer.analyze_performance_report(args.report)
            if 'error' in analysis:
                print(f"❌ Error: {analysis['error']}", file=sys.stderr)
                sys.exit(1)
            print(json.dumps(analysis, indent=2))
        else:
            report = optimizer.generate_optimization_report(args.report, args.output)
            if report.startswith("Error:"):
                print(f"❌ {report}", file=sys.stderr)
                sys.exit(1)
            print(report)
            if args.output:
                print(f"\n💾 Optimization report saved to: {args.output}")
    except KeyboardInterrupt:
        print("\n⚠️  Operation interrupted by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()

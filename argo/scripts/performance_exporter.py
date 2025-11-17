#!/usr/bin/env python3
"""
Performance Metrics Exporter for Prometheus
Exports performance evaluation metrics to Prometheus format
"""
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

def load_latest_report(reports_dir: str = "reports") -> Optional[Dict]:
    """Load latest performance evaluation report"""
    reports_path = Path(reports_dir)
    if not reports_path.exists():
        return None

    reports = list(reports_path.glob("daily_evaluation_*.json"))
    if not reports:
        reports = list(reports_path.glob("performance_evaluation*.json"))

    if not reports:
        return None

    reports.sort(key=lambda p: p.stat().st_mtime, reverse=True)

    try:
        with open(reports[0], 'r') as f:
            return json.load(f)
    except Exception:
        return None

def grade_to_number(grade: str) -> float:
    """Convert grade to number for metrics"""
    if 'A' in grade or 'Excellent' in grade:
        return 4.0
    elif 'B' in grade or 'Good' in grade:
        return 3.0
    elif 'C' in grade or 'Fair' in grade:
        return 2.0
    elif 'D' in grade or 'Needs Improvement' in grade:
        return 1.0
    else:
        return 0.0

def export_metrics(report: Dict) -> str:
    """Export metrics in Prometheus format"""
    lines = []

    # Signal Generator Metrics
    if 'signal_generator' in report:
        sg = report['signal_generator']
        metrics = sg.get('metrics', {})
        grade = grade_to_number(sg.get('performance_grade', 'N/A'))

        lines.append(f"# Signal Generator Metrics")
        lines.append(f"argo_signal_generation_time_seconds {metrics.get('avg_signal_generation_time_seconds', 0)}")
        lines.append(f"argo_cache_hit_rate_percent {metrics.get('cache_hit_rate_percent', 0)}")
        lines.append(f"argo_skip_rate_percent {metrics.get('skip_rate_percent', 0)}")
        lines.append(f"argo_api_latency_seconds {metrics.get('avg_api_latency_seconds', 0)}")
        lines.append(f"argo_signal_generator_grade {grade}")
        lines.append(f"argo_cache_hits_total {metrics.get('total_cache_hits', 0)}")
        lines.append(f"argo_cache_misses_total {metrics.get('total_cache_misses', 0)}")
        lines.append("")

    # Production Trading Metrics
    if 'production_trading' in report:
        pt = report['production_trading']
        metrics = pt.get('metrics', {})
        grade = grade_to_number(pt.get('performance_grade', 'N/A'))

        lines.append(f"# Production Trading Metrics")
        lines.append(f"argo_production_win_rate_percent {metrics.get('win_rate_percent', 0)}")
        lines.append(f"argo_production_profit_factor {metrics.get('profit_factor', 0)}")
        lines.append(f"argo_production_return_percent {metrics.get('return_percent', 0)}")
        lines.append(f"argo_production_total_trades {metrics.get('total_trades', 0)}")
        lines.append(f"argo_production_completed_trades {metrics.get('completed_trades', 0)}")
        lines.append(f"argo_production_pnl_dollars {metrics.get('total_pnl_dollars', 0)}")
        lines.append(f"argo_production_grade {grade}")
        lines.append("")

    # Prop Firm Trading Metrics
    if 'prop_firm_trading' in report:
        pf = report['prop_firm_trading']
        metrics = pf.get('metrics', {})
        grade = grade_to_number(pf.get('performance_grade', 'N/A'))
        compliance = metrics.get('compliance_metrics', {})

        lines.append(f"# Prop Firm Trading Metrics")
        lines.append(f"argo_prop_firm_win_rate_percent {metrics.get('win_rate_percent', 0)}")
        lines.append(f"argo_prop_firm_profit_factor {metrics.get('profit_factor', 0)}")
        lines.append(f"argo_prop_firm_return_percent {metrics.get('return_percent', 0)}")
        lines.append(f"argo_prop_firm_grade {grade}")
        lines.append(f"argo_prop_firm_drawdown_breaches {compliance.get('drawdown_breaches', 0) or 0}")
        lines.append(f"argo_prop_firm_daily_loss_breaches {compliance.get('daily_loss_breaches', 0) or 0}")
        lines.append(f"argo_prop_firm_trading_halted {1 if compliance.get('trading_halted') else 0}")
        lines.append("")

    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description='Performance Metrics Exporter for Prometheus')
    parser.add_argument('--reports-dir', default='reports', help='Reports directory')
    parser.add_argument('--report', help='Specific report file to export')
    parser.add_argument('--port', type=int, default=9091, help='HTTP server port (if running as server)')
    parser.add_argument('--server', action='store_true', help='Run as HTTP server')

    args = parser.parse_args()

    if args.server:
        # Run as HTTP server
        from http.server import HTTPServer, BaseHTTPRequestHandler

        class MetricsHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/metrics':
                    report = load_latest_report(args.reports_dir)
                    if report:
                        metrics = export_metrics(report)
                        self.send_response(200)
                        self.send_header('Content-type', 'text/plain')
                        self.end_headers()
                        self.wfile.write(metrics.encode())
                    else:
                        self.send_response(404)
                        self.end_headers()
                        self.wfile.write(b"No metrics available")
                else:
                    self.send_response(404)
                    self.end_headers()

            def log_message(self, format, *args):
                pass  # Suppress logging

        server = HTTPServer(('', args.port), MetricsHandler)
        print(f"📊 Prometheus exporter running on port {args.port}")
        print(f"   Metrics available at: http://localhost:{args.port}/metrics")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Exporter stopped")
    else:
        # Export once
        if args.report:
            with open(args.report, 'r') as f:
                report = json.load(f)
        else:
            report = load_latest_report(args.reports_dir)

        if not report:
            print("❌ No report found")
            sys.exit(1)

        metrics = export_metrics(report)
        print(metrics)

if __name__ == '__main__':
    main()

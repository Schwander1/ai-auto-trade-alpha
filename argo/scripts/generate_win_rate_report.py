#!/usr/bin/env python3
"""
Generate Win Rate Validation Report
Usage: python scripts/generate_win_rate_report.py [--period 30] [--format json|markdown|pdf] [--output path]
"""

import argparse
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from argo.validation.win_rate_validator import WinRateValidator

def main():
    parser = argparse.ArgumentParser(description="Generate win rate validation report")
    parser.add_argument("--period", type=int, default=30, help="Period in days (default: 30)")
    parser.add_argument("--format", choices=["json", "markdown", "pdf"], default="json", help="Output format")
    parser.add_argument("--output", type=str, help="Output file path (default: stdout)")
    parser.add_argument("--methodology", choices=["completed_trades", "all_signals", "confidence_weighted", "time_weighted", "regime_based"], 
                       default="completed_trades", help="Validation methodology")
    
    args = parser.parse_args()
    
    validator = WinRateValidator()
    
    if args.format == "markdown":
        report = validator.generate_investor_report(period_days=args.period, output_format="markdown")
        output = report
    else:
        report = validator.generate_investor_report(period_days=args.period, output_format="json")
        output = json.dumps(report, indent=2)
    
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output)
        print(f"✅ Report saved to {args.output}")
    else:
        print(output)

if __name__ == "__main__":
    main()


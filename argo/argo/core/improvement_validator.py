#!/usr/bin/env python3
"""
Improvement Validator
Compares before/after metrics to validate improvements
"""
import json
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class ImprovementResult:
    """Result of improvement validation"""
    metric_name: str
    before_value: float
    after_value: float
    improvement_pct: float
    improvement_absolute: float
    target_met: bool
    target_value: float
    significance: str  # "high", "medium", "low", "none"

class ImprovementValidator:
    """Validate that enhancements actually improved the system"""
    
    def __init__(self, baseline_file: Path, after_file: Path):
        self.baseline_file = Path(baseline_file)
        self.after_file = Path(after_file)
        
    def validate_improvements(self) -> Dict[str, ImprovementResult]:
        """
        Compare before/after metrics and validate improvements.
        
        Returns:
            Dict mapping metric names to improvement results
        """
        with open(self.baseline_file) as f:
            baseline = json.load(f)
            
        with open(self.after_file) as f:
            after = json.load(f)
            
        results = {}
        
        # Performance improvements
        results['signal_generation_speed'] = self._compare_metric(
            'signal_generation_avg_ms',
            baseline, after,
            target_improvement_pct=40.0,  # Target 40% faster
            lower_is_better=True
        )
        
        results['cache_hit_rate'] = self._compare_metric(
            'cache_hit_rate',
            baseline, after,
            target_improvement_pct=50.0,  # Target 50% improvement
            lower_is_better=False
        )
        
        results['api_costs'] = self._compare_metric(
            'estimated_monthly_cost',
            baseline, after,
            target_improvement_pct=30.0,  # Target 30% cost reduction
            lower_is_better=True
        )
        
        results['error_rate'] = self._compare_metric(
            'error_rate',
            baseline, after,
            target_improvement_pct=50.0,  # Target 50% error reduction
            lower_is_better=True
        )
        
        # Generate report
        self._generate_report(results)
        
        return results
        
    def _compare_metric(
        self,
        metric_name: str,
        baseline: Dict,
        after: Dict,
        target_improvement_pct: float,
        lower_is_better: bool = True
    ) -> ImprovementResult:
        """Compare a single metric"""
        before_val = baseline.get(metric_name, 0)
        after_val = after.get(metric_name, 0)
        
        if before_val == 0:
            improvement_pct = 0.0
        else:
            if lower_is_better:
                improvement_pct = ((before_val - after_val) / before_val) * 100
            else:
                improvement_pct = ((after_val - before_val) / before_val) * 100
                
        improvement_absolute = abs(after_val - before_val)
        target_met = improvement_pct >= target_improvement_pct
        
        # Determine significance
        if improvement_pct >= target_improvement_pct * 1.2:
            significance = "high"
        elif improvement_pct >= target_improvement_pct:
            significance = "medium"
        elif improvement_pct >= target_improvement_pct * 0.5:
            significance = "low"
        else:
            significance = "none"
            
        return ImprovementResult(
            metric_name=metric_name,
            before_value=before_val,
            after_value=after_val,
            improvement_pct=improvement_pct,
            improvement_absolute=improvement_absolute,
            target_met=target_met,
            target_value=target_improvement_pct,
            significance=significance
        )
        
    def _generate_report(self, results: Dict[str, ImprovementResult]):
        """Generate improvement validation report"""
        report_lines = [
            "# Improvement Validation Report",
            f"Generated: {datetime.now().isoformat()}",
            "",
            "## Summary",
            ""
        ]
        
        total_metrics = len(results)
        targets_met = sum(1 for r in results.values() if r.target_met)
        
        report_lines.append(f"- **Total Metrics:** {total_metrics}")
        report_lines.append(f"- **Targets Met:** {targets_met} ({targets_met/total_metrics*100:.1f}%)")
        report_lines.append("")
        report_lines.append("## Detailed Results")
        report_lines.append("")
        
        for metric_name, result in results.items():
            status = "✅" if result.target_met else "❌"
            report_lines.append(f"### {status} {metric_name}")
            report_lines.append(f"- **Before:** {result.before_value:.4f}")
            report_lines.append(f"- **After:** {result.after_value:.4f}")
            report_lines.append(f"- **Improvement:** {result.improvement_pct:.2f}% (target: {result.target_value:.1f}%)")
            report_lines.append(f"- **Significance:** {result.significance}")
            report_lines.append("")
            
        # Save report
        report_file = Path("argo/reports") / f"improvement_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_file, 'w') as f:
            f.write("\n".join(report_lines))
            
        logger.info(f"📊 Improvement report saved to {report_file}")
        
        # Print summary
        print("\n" + "="*60)
        print("IMPROVEMENT VALIDATION SUMMARY")
        print("="*60)
        for metric_name, result in results.items():
            status = "✅ PASS" if result.target_met else "❌ FAIL"
            print(f"{status} {metric_name}: {result.improvement_pct:.2f}% improvement")
        print("="*60)

# CLI for validation
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate improvements")
    parser.add_argument("--baseline", required=True, help="Baseline metrics JSON file")
    parser.add_argument("--after", required=True, help="After metrics JSON file")
    args = parser.parse_args()
    
    validator = ImprovementValidator(args.baseline, args.after)
    validator.validate_improvements()


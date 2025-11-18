#!/usr/bin/env python3
"""
Automated Optimization Workflow
Runs evaluation, analyzes with optimizer, and suggests configuration changes
"""
import sys
import json
import subprocess
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_evaluation(days: int = 1, reports_dir: Optional[str] = None) -> Optional[Path]:
    """Run performance evaluation with improved error handling"""
    try:
        print(f"📊 Running performance evaluation for last {days} days...")
        
        if reports_dir:
            reports_path = Path(reports_dir)
        else:
            reports_path = Path("reports")
        reports_path.mkdir(parents=True, exist_ok=True)
        
        output_file = reports_path / f"auto_evaluation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        result = subprocess.run(
            ["python3", "scripts/evaluate_performance_enhanced.py", "--days", str(days), "--json", "--reports-dir", str(reports_path)],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode != 0:
            logger.error(f"Evaluation failed: {result.stderr}")
            print(f"❌ Evaluation failed: {result.stderr}")
            return None
        
        # Save output
        try:
            with open(output_file, 'w') as f:
                f.write(result.stdout)
            print(f"✅ Evaluation complete: {output_file}")
            return output_file
        except Exception as e:
            logger.error(f"Error saving evaluation output: {e}")
            print(f"❌ Error saving evaluation: {e}")
            return None
    except subprocess.TimeoutExpired:
        logger.error("Evaluation timed out after 5 minutes")
        print("❌ Evaluation timed out")
        return None
    except Exception as e:
        logger.error(f"Unexpected error running evaluation: {e}", exc_info=True)
        print(f"❌ Unexpected error: {e}")
        return None

def run_optimizer(report_path: Path) -> Dict:
    """Run performance optimizer with improved error handling"""
    try:
        print(f"🔍 Analyzing optimizations...")
        
        if not report_path.exists():
            logger.error(f"Report file does not exist: {report_path}")
            print(f"❌ Report file not found: {report_path}")
            return {}
        
        result = subprocess.run(
            ["python3", "scripts/performance_optimizer.py", str(report_path), "--json"],
            capture_output=True,
            text=True,
            timeout=60  # 1 minute timeout
        )
        
        if result.returncode != 0:
            logger.error(f"Optimization analysis failed: {result.stderr}")
            print(f"❌ Optimization analysis failed: {result.stderr}")
            return {}
        
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError as e:
            logger.error(f"Could not parse optimizer output: {e}")
            print(f"⚠️  Could not parse optimizer output: {e}")
            return {}
    except subprocess.TimeoutExpired:
        logger.error("Optimizer timed out")
        print("❌ Optimizer timed out")
        return {}
    except Exception as e:
        logger.error(f"Unexpected error running optimizer: {e}", exc_info=True)
        print(f"❌ Unexpected error: {e}")
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
    parser.add_argument('--reports-dir', help='Reports directory (default: reports)')
    parser.add_argument('--apply', action='store_true', help='Apply safe optimizations (not implemented yet)')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Step 1: Run evaluation
        report_path = run_evaluation(args.days, args.reports_dir)
        if not report_path:
            print("❌ Evaluation failed. Cannot continue.", file=sys.stderr)
            sys.exit(1)
        
        # Step 2: Run optimizer
        optimizations = run_optimizer(report_path)
        
        if not optimizations:
            print("⚠️  No optimization data available")
            if not args.json:
                sys.exit(1)
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
    except KeyboardInterrupt:
        print("\n⚠️  Operation interrupted by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()

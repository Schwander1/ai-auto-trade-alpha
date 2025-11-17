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

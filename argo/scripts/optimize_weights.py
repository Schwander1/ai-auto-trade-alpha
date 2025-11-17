#!/usr/bin/env python3
"""
Weight Optimizer
Uses scipy to optimize source weights based on actual accuracies
Compliance: Rule 01 (Naming), Rule 03 (Testing)
"""
import sys
from pathlib import Path
import numpy as np
from scipy.optimize import minimize
from typing import Dict, List
import json
import logging

sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def optimize_weights(source_accuracies: Dict[str, float]) -> Dict[str, float]:
    """
    Optimize source weights to maximize expected accuracy
    
    Args:
        source_accuracies: Dict mapping source_name -> accuracy_pct
    
    Returns:
        Optimized weights dict
    """
    # Convert to arrays in consistent order
    source_order = ['massive', 'alpha_vantage', 'xai_grok', 'sonar']
    sources = []
    accuracies = []
    
    for source in source_order:
        if source in source_accuracies:
            sources.append(source)
            accuracies.append(source_accuracies[source])
        else:
            # Use placeholder if missing
            placeholder_acc = {
                'massive': 88.5,
                'alpha_vantage': 83.2,
                'xai_grok': 78.9,
                'sonar': 72.1
            }
            sources.append(source)
            accuracies.append(placeholder_acc.get(source, 75.0))
    
    accuracies = np.array(accuracies)
    
    # Initial weights (current)
    x0 = np.array([0.40, 0.25, 0.20, 0.15])  # Massive, Alpha, xAI, Sonar
    
    # Constraints: weights must sum to 1.0
    constraints = {'type': 'eq', 'fun': lambda x: np.sum(x) - 1.0}
    
    # Bounds: each weight between 0 and 1
    bounds = [(0, 1) for _ in sources]
    
    # Objective: maximize weighted accuracy
    def objective(x):
        return -np.sum(x * accuracies)  # Negative because minimize
    
    # Optimize
    result = minimize(
        objective,
        x0,
        method='SLSQP',
        bounds=bounds,
        constraints=constraints
    )
    
    if not result.success:
        logger.warning(f"Optimization failed: {result.message}")
        logger.info("Using fallback optimized weights based on accuracy ranking")
        # Fallback: weight by accuracy ranking
        sorted_sources = sorted(zip(sources, accuracies), key=lambda x: x[1], reverse=True)
        weights = {}
        remaining_weight = 1.0
        for i, (source, acc) in enumerate(sorted_sources):
            if i == len(sorted_sources) - 1:
                weights[source] = remaining_weight
            else:
                # Higher accuracy gets more weight
                weight = 0.5 - (i * 0.1)
                weights[source] = weight
                remaining_weight -= weight
        return weights
    
    optimized = dict(zip(sources, result.x))
    
    # Calculate expected accuracy
    expected_accuracy = np.sum(result.x * accuracies)
    
    logger.info(f"Optimized weights:")
    for source, weight in optimized.items():
        logger.info(f"  {source:15s}: {weight:6.2%}")
    logger.info(f"Expected accuracy: {expected_accuracy:.2f}%")
    
    return optimized

if __name__ == "__main__":
    # Try to load actual accuracies
    accuracies_file = Path(__file__).parent.parent / "reports" / "source_accuracies.json"
    
    if accuracies_file.exists():
        with open(accuracies_file) as f:
            accuracy_data = json.load(f)
        # Extract accuracy percentages
        accuracies = {k: v['accuracy'] for k, v in accuracy_data.items()}
    else:
        # Use placeholder accuracies
        logger.warning("⚠️  No accuracy data found. Using placeholder accuracies.")
        accuracies = {
            'massive': 88.5,
            'alpha_vantage': 83.2,
            'xai_grok': 78.9,
            'sonar': 72.1
        }
    
    optimized = optimize_weights(accuracies)
    
    print("\n" + "=" * 60)
    print("OPTIMIZED WEIGHTS")
    print("=" * 60)
    for source, weight in optimized.items():
        print(f"{source:15s}: {weight:6.2%}")
    print("=" * 60)
    
    # Save to JSON
    output_file = Path(__file__).parent.parent / "reports" / "optimized_weights.json"
    output_file.parent.mkdir(exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(optimized, f, indent=2)
    print(f"\n✅ Optimized weights saved to: {output_file}")


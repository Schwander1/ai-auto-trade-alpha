#!/usr/bin/env python3
"""
Adaptive Weight Manager
Dynamically adjusts data source weights based on recent performance.
Uses exponential moving average and performance decay.
"""
import logging
from collections import deque
from typing import Dict
import numpy as np

logger = logging.getLogger(__name__)

class AdaptiveWeightManager:
    """
    Dynamically adjusts data source weights based on recent performance.
    Uses exponential moving average and performance decay.
    """
    def __init__(self, initial_weights: Dict[str, float]):
        self.base_weights = initial_weights.copy()
        self.current_weights = initial_weights.copy()
        self.performance_history = {source: deque(maxlen=100) for source in initial_weights}
        self.min_weight = 0.05  # Minimum 5% weight
        self.max_weight = 0.50  # Maximum 50% weight
        self.adjustment_factor = 0.1  # 10% adjustment per cycle
        
    def update_performance(self, source: str, was_correct: bool, confidence: float):
        """
        Record source performance for weight adjustment.
        Args:
            source: Data source name
            was_correct: Whether the signal was profitable
            confidence: Source's confidence in the signal (0-100)
        """
        if source not in self.performance_history:
            logger.warning(f"Unknown source: {source}")
            return
            
        # Weight by confidence (more confident signals count more)
        weighted_score = (1 if was_correct else 0) * (confidence / 100)
        self.performance_history[source].append(weighted_score)
        
    def adjust_weights(self) -> Dict[str, float]:
        """
        Adjust weights based on recent performance.
        Uses exponential moving average for responsiveness.
        """
        # Need minimum data to adjust
        if not any(len(history) > 10 for history in self.performance_history.values()):
            return self.current_weights
            
        # Calculate recent performance scores
        performance_scores = {}
        for source, history in self.performance_history.items():
            if len(history) > 0:
                # Exponential moving average favors recent performance
                weights_ema = np.exp(np.linspace(-1, 0, len(history)))
                weights_ema /= weights_ema.sum()
                performance_scores[source] = np.average(list(history), weights=weights_ema)
            else:
                performance_scores[source] = 0.5  # Neutral for no data
                
        # Adjust weights based on performance relative to average
        avg_performance = np.mean(list(performance_scores.values()))
        new_weights = {}
        
        for source, base_weight in self.base_weights.items():
            performance = performance_scores[source]
            performance_ratio = performance / avg_performance if avg_performance > 0 else 1.0
            
            # Adjust weight (outperformers get more weight, underperformers get less)
            adjustment = (performance_ratio - 1.0) * self.adjustment_factor
            new_weight = base_weight * (1 + adjustment)
            
            # Apply bounds
            new_weight = max(self.min_weight, min(self.max_weight, new_weight))
            new_weights[source] = new_weight
            
        # Normalize to sum to 1.0
        total_weight = sum(new_weights.values())
        if total_weight > 0:
            normalized_weights = {s: w/total_weight for s, w in new_weights.items()}
        else:
            normalized_weights = self.base_weights
            
        self.current_weights = normalized_weights
        return normalized_weights
        
    def get_weight(self, source: str) -> float:
        """Get current weight for a source"""
        return self.current_weights.get(source, 0.0)
        
    def get_performance_report(self) -> Dict:
        """Generate performance report for all sources"""
        report = {}
        for source, history in self.performance_history.items():
            if len(history) > 0:
                accuracy = np.mean(list(history)) * 100
                sample_size = len(history)
                current_weight = self.current_weights.get(source, 0.0)
                base_weight = self.base_weights.get(source, 0.0)
                weight_change = ((current_weight - base_weight) / base_weight) * 100 if base_weight > 0 else 0
                
                report[source] = {
                    "accuracy": accuracy,
                    "sample_size": sample_size,
                    "current_weight": current_weight,
                    "base_weight": base_weight,
                    "weight_change_pct": weight_change
                }
        return report


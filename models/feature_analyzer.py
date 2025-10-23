
"""
LAYER 4: Feature Importance & Pruning
Identifies which features actually drive model predictions
Removes noise, improves generalization to live trading
"""

import xgboost as xgb
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

def analyze_feature_importance(model, feature_names):
    """
    Identify which features actually drive model predictions

    XGBoost's feature importance shows how many times each feature
    is used in tree splits. Top features drive 80% of prediction power.

    Args:
        model: Trained XGBoost model
        feature_names: list of feature column names

    Returns:
        dict: Importance ranking and recommendations
    """

    try:
        importance_dict = model.get_booster().get_score(importance_type='weight')
    except:
        logger.warning("⚠️ Could not extract feature importance")
        return {
            'top_features': feature_names[:5],
            'drop_features': feature_names[5:],
            'error': 'Feature importance extraction failed'
        }

    sorted_features = sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)

    logger.info("\n=== FEATURE IMPORTANCE RANKING ===")
    total_importance = sum([score for _, score in sorted_features]) if sorted_features else 1
    cumulative = 0

    for i, (feat_name, score) in enumerate(sorted_features, 1):
        cumulative += score
        pct_cumulative = (cumulative / total_importance) * 100 if total_importance > 0 else 0
        logger.info(f"  {i:2d}. {feat_name:20s} importance={score:5.0f} cumulative={pct_cumulative:5.1f}%")

    top_features = []
    cumulative = 0
    for feat_name, score in sorted_features:
        top_features.append(feat_name)
        cumulative += score
        if (cumulative / total_importance) >= 0.80:
            break

    drop_features = [f for f, _ in sorted_features if f not in top_features]

    logger.info(f"\n✓ TOP FEATURES (80% of importance): {top_features}")
    logger.info(f"✗ DROP FEATURES (noise/redundancy): {drop_features}")

    compression_ratio = len(top_features) / len(sorted_features) if len(sorted_features) > 0 else 0
    logger.info(f"  Feature compression: {len(sorted_features)} → {len(top_features)} ({compression_ratio*100:.0f}%)")

    return {
        'top_features': top_features,
        'drop_features': drop_features,
        'importance_dict': importance_dict,
        'num_features_before': len(sorted_features),
        'num_features_after': len(top_features),
        'compression_ratio': compression_ratio
    }

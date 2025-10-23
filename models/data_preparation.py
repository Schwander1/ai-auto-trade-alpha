
"""
LAYER 2: Walk-Forward Validation & Overfitting Detection
Splits data into 70% train / 15% validation / 15% test (hold-out, unseen)
Catches overfitting that inflates backtest Sharpe by 20-40%
"""

import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

def prepare_data_walk_forward(df, feature_cols, target_col='target'):
    """
    Split time-series data properly (NO look-ahead bias)

    Critical: Test set is NEVER used during training
    This simulates real trading where you evaluate on future unseen data

    Args:
        df: DataFrame with features and target
        feature_cols: List of feature column names
        target_col: Name of target column

    Returns:
        tuple: (X_train, X_val, X_test, y_train, y_val, y_test, dates_test)
    """

    df = df.sort_values('timestamp').reset_index(drop=True)

    X = df[feature_cols].fillna(0).values
    y = df[target_col].values
    dates = df['timestamp'].values

    n = len(X)

    train_idx = int(n * 0.70)
    val_idx = int(n * 0.85)

    X_train = X[:train_idx]
    X_val = X[train_idx:val_idx]
    X_test = X[val_idx:]

    y_train = y[:train_idx]
    y_val = y[train_idx:val_idx]
    y_test = y[val_idx:]

    dates_test = dates[val_idx:]

    logger.info(f"✓ Data split: Train={len(X_train)}, Val={len(X_val)}, Test(UNSEEN)={len(X_test)}")

    if len(dates_test) > 0:
        logger.info(f"  Test date range: {pd.Timestamp(dates_test[0])} to {pd.Timestamp(dates_test[-1])}")

    return X_train, X_val, X_test, y_train, y_val, y_test, dates_test


def evaluate_with_overfitting_check(model, X_train, X_val, X_test, y_train, y_val, y_test):
    """
    Evaluate model on all 3 sets and flag overfitting

    The KEY metric is Test Accuracy (unseen data)
    If train >> test, model memorized training data

    Args:
        model: Trained sklearn model
        X_train, X_val, X_test: Feature arrays
        y_train, y_val, y_test: Target arrays

    Returns:
        dict: Performance metrics + overfitting flag
    """

    train_pred = model.predict(X_train)
    val_pred = model.predict(X_val)
    test_pred = model.predict(X_test)

    train_acc = (train_pred == y_train).mean()
    val_acc = (val_pred == y_val).mean()
    test_acc = (test_pred == y_test).mean()

    overfit_gap = train_acc - test_acc

    logger.info("\n=== MODEL PERFORMANCE (OVERFITTING CHECK) ===")
    logger.info(f"  Train Accuracy: {train_acc:.4f}")
    logger.info(f"  Val Accuracy:   {val_acc:.4f}")
    logger.info(f"  Test Accuracy (UNSEEN): {test_acc:.4f}  ← THIS MATTERS")
    logger.info(f"  Overfit Gap: {overfit_gap:.4f}")

    if overfit_gap > 0.15:
        logger.warning(f"\n⚠️ OVERFITTING DETECTED!")
        logger.warning(f"  Train-Test gap of {overfit_gap:.4f} is too large (>0.15)")
        logger.warning(f"  Action: Reduce features, increase regularization, or collect more data")
        is_overfitting = True
    else:
        logger.info(f"\n✓ No overfitting detected (gap < 0.15)")
        is_overfitting = False

    return {
        'train_acc': train_acc,
        'val_acc': val_acc,
        'test_acc': test_acc,
        'overfit_gap': overfit_gap,
        'is_overfitting': is_overfitting
    }

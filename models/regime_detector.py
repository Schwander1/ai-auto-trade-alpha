"""
LAYER 1: Market Regime Detection
Detects if model breaks in specific market conditions before paper trading
"""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
import logging

logger = logging.getLogger(__name__)

class MarketRegimeDetector:
    """Classify market into regimes: Trending, Choppy, Mean-Reversion"""

    def __init__(self, window=20):
        self.window = window

    def classify_regimes(self, returns_series):
        """
        Classify each timestep into one of 3 market regimes

        Args:
            returns_series: Series of daily returns

        Returns:
            array: regime labels (0, 1, or 2)
        """
        returns = returns_series.values

        vol = pd.Series(returns).rolling(self.window).std().values
        trend = pd.Series(returns).rolling(self.window).sum().values
        trend_strength = np.divide(trend, vol + 1e-8)

        features = np.column_stack([vol, trend_strength])
        features = np.nan_to_num(features, 0)

        kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
        regimes = kmeans.fit_predict(features)

        return regimes

    def backtest_by_regime(self, df, model, feature_cols, target_col='target'):
        """
        Backtest separately on each regime
        Shows if model is fragile in specific market conditions

        Args:
            df: DataFrame with OHLCV + features + target
            model: Trained sklearn model
            feature_cols: List of feature column names
            target_col: Name of target column

        Returns:
            dict with per-regime metrics
        """
        df = df.copy()

        df['regime'] = self.classify_regimes(df['close'].pct_change())

        results = {}
        regime_names = {0: 'Choppy (Low Vol)', 1: 'Trending', 2: 'Mean-Reversion'}

        logger.info("\n=== REGIME ANALYSIS ===")

        for regime_id in [0, 1, 2]:
            regime_mask = df['regime'] == regime_id
            regime_data = df[regime_mask]

            if len(regime_data) < 10:
                logger.warning(f"  ⚠️ Regime {regime_id}: Only {len(regime_data)} samples, skipping")
                continue

            X_regime = regime_data[feature_cols].fillna(0).values
            y_regime = regime_data[target_col].values
            preds = model.predict(X_regime)

            accuracy = (preds == y_regime).mean()

            returns = regime_data['close'].pct_change().values
            signal_returns = preds * returns
            sharpe = (signal_returns.mean() / signal_returns.std() * np.sqrt(252)) if signal_returns.std() > 0 else 0

            logger.info(f"  {regime_names[regime_id]:20s}: Accuracy={accuracy:.4f}, Sharpe={sharpe:.2f}, N={len(regime_data)}")

            results[f'regime_{regime_id}'] = {
                'name': regime_names[regime_id],
                'accuracy': accuracy,
                'sharpe': sharpe,
                'samples': len(regime_data)
            }

        return results

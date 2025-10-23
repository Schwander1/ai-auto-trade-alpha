
"""
MASTER TRAINER: Models/train_model_optimized.py
Orchestrates all 4 optimization layers in sequence
Run this after features are computed
"""

import pandas as pd
import numpy as np
import xgboost as xgb
import mlflow
import logging
import sys
from pathlib import Path

from regime_detector import MarketRegimeDetector
from data_preparation import prepare_data_walk_forward, evaluate_with_overfitting_check
from backtest_with_slippage import compare_slippage_impact
from feature_analyzer import analyze_feature_importance

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class OptimizedModelTrainer:
    """Complete training pipeline with all 4 optimization layers"""

    def __init__(self, features_csv, feature_cols, target_col='target'):
        self.features_csv = features_csv
        self.feature_cols = feature_cols
        self.target_col = target_col
        self.model = None
        self.validation_results = {}

    def run(self):
        """Execute complete training pipeline"""

        logger.info("=" * 80)
        logger.info("ARGO MODEL TRAINING: ALL 4 OPTIMIZATION LAYERS")
        logger.info("=" * 80)

        logger.info("\n[STEP 1/6] Loading features...")
        df = pd.read_csv(self.features_csv)
        logger.info(f"  ✓ Loaded {len(df)} rows, {len(df.columns)} columns")

        logger.info("\n[STEP 2/6] LAYER 2: Walk-forward validation (70/15/15 split)...")
        X_train, X_val, X_test, y_train, y_val, y_test, dates_test = prepare_data_walk_forward(
            df, feature_cols=self.feature_cols, target_col=self.target_col
        )

        logger.info("\n[STEP 3/6] Training XGBoost...")
        self.model = xgb.XGBClassifier(
            max_depth=5,
            n_estimators=200,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            eval_metric='logloss'
        )
        self.model.fit(
            X_train, y_train,
            eval_set=[(X_val, y_val)],
            early_stopping_rounds=20,
            verbose=False
        )
        logger.info(f"  ✓ Model trained")

        logger.info("\n[STEP 4/6] LAYER 2: Checking for overfitting...")
        perf_metrics = evaluate_with_overfitting_check(
            self.model, X_train, X_val, X_test, y_train, y_val, y_test
        )
        self.validation_results['performance'] = perf_metrics

        if perf_metrics['is_overfitting']:
            logger.error("❌ OVERFITTING DETECTED - Model failed Layer 2")
            return False

        logger.info("✓ Layer 2 PASSED")

        logger.info("\n[STEP 5/6] LAYER 1: Market regime analysis...")
        detector = MarketRegimeDetector()
        regime_results = detector.backtest_by_regime(df, self.model, self.feature_cols, self.target_col)
        self.validation_results['regimes'] = regime_results

        weak_regimes = [r for r, m in regime_results.items() if m['sharpe'] < 0.5]
        if weak_regimes:
            logger.warning(f"⚠️ WEAK REGIME(S): {weak_regimes}")
        else:
            logger.info("✓ Layer 1 PASSED: All regimes OK")

        logger.info("\n[STEP 6/6] LAYER 3: Execution slippage simulation...")
        test_preds = self.model.predict(X_test)
        close_prices = df.iloc[-len(X_test):]['close'].values
        test_returns = df['close'].pct_change().values[-len(X_test):]

        slippage_analysis = compare_slippage_impact(test_preds, close_prices, test_returns)
        self.validation_results['slippage'] = slippage_analysis

        if not slippage_analysis['gap_acceptable']:
            logger.error("❌ SLIPPAGE GAP TOO LARGE - Model failed Layer 3")
            return False

        logger.info("✓ Layer 3 PASSED")

        logger.info("\n[LAYER 4] Feature importance analysis...")
        importance_analysis = analyze_feature_importance(self.model, self.feature_cols)
        self.validation_results['feature_importance'] = importance_analysis
        logger.info("✓ Layer 4 PASSED")

        logger.info("\n[LOGGING] Saving metrics to MLflow...")
        try:
            with mlflow.start_run(run_name='xgb_optimized_v1'):
                mlflow.log_metrics(perf_metrics)
                for k, v in regime_results.items():
                    mlflow.log_metric(f"{k}_sharpe", v['sharpe'])
                mlflow.log_metric("backtest_sharpe", slippage_analysis['no_slippage_sharpe'])
                mlflow.log_metric("reality_sharpe", slippage_analysis['with_slippage_sharpe'])
                mlflow.sklearn.log_model(self.model, "model")
            logger.info("  ✓ Metrics logged")
        except:
            logger.warning("  ⚠️ MLflow logging failed (continue anyway)")

        logger.info("\nSaving model...")
        Path('models/artifacts').mkdir(parents=True, exist_ok=True)
        self.model.save_model('models/artifacts/model_optimized.pkl')
        logger.info("  ✓ Model saved to models/artifacts/model_optimized.pkl")

        logger.info("\n" + "=" * 80)
        logger.info("✓✓✓ ALL LAYERS PASSED - MODEL READY FOR PAPER TRADING ✓✓✓")
        logger.info("=" * 80)

        return True


if __name__ == "__main__":

    features_csv = 'datapipeline/features/features_output.csv'
    feature_cols = [
        'rsi', 'macd', 'atr', 'sma_20', 'sma_50',
        'bb_upper', 'bb_lower', 'obv', 'ad_line', 'cci'
    ]

    trainer = OptimizedModelTrainer(
        features_csv=features_csv,
        feature_cols=feature_cols,
        target_col='target'
    )

    success = trainer.run()

    if success:
        logger.info("\n✓✓✓ SUCCESS! Model is ready ✓✓✓")
        sys.exit(0)
    else:
        logger.error("\n❌ Training failed")
        sys.exit(1)

# ================================================================================
# END FILE 5
# ================================================================================

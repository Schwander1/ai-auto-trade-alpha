#!/usr/bin/env python3
import sys
import os
sys.path.append('40models/mlflow')

try:
    from argo_ml_manager_optimized import argo_ml_optimized
    
    print("🤖 TRAINED ML MODELS STATUS:")
    print("=" * 50)
    
    # Get model status
    models = argo_ml_optimized.get_model_status()
    
    if models:
        for symbol, status in models.items():
            acc = status.get('accuracy', 'N/A')
            f1 = status.get('f1_score', 'N/A')
            trained = status.get('last_trained', 'N/A')
            print(f"🎯 {symbol}:")
            print(f"   📊 Accuracy: {acc}")
            print(f"   📊 F1-Score: {f1}")
            print(f"   🕒 Last Trained: {trained}")
            print(f"   ✅ Status: {status.get('status', 'UNKNOWN')}")
            print()
    else:
        print("⚠️ No models found in Redis cache")
        
        # Check filesystem
        models_dir = "40models/xgboost/production"
        if os.path.exists(models_dir):
            model_files = [f for f in os.listdir(models_dir) if 'model' in f and f.endswith('.joblib')]
            print(f"💾 Found {len(model_files)} model files on disk:")
            for file in model_files:
                print(f"   📁 {file}")
        else:
            print("❌ No models directory found")

except Exception as e:
    print(f"❌ Error checking models: {e}")
    import traceback
    traceback.print_exc()

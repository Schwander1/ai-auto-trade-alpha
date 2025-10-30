#!/usr/bin/env python3
"""
Test ensemble trainer with fixed f-string syntax
"""
import sys
sys.path.append('40models')

try:
    from ensemble_models_fixed import ensemble_trainer_fixed
    
    print("🎯 TESTING FIXED ENSEMBLE TRAINER...")
    
    # Train ensemble for SPY (our best performer)
    result = ensemble_trainer_fixed.train_ensemble('SPY')
    
    if result:
        # Fix f-string syntax by extracting values first
        accuracy = result['ensemble_accuracy']
        f1_score = result['ensemble_f1']
        ensemble_type = result['ensemble_type']
        models_count = len(result['models_used'])
        
        print("🏆 ENSEMBLE SUCCESS:")
        print(f"   📊 Accuracy: {accuracy:.4f}")
        print(f"   📊 F1-Score: {f1_score:.4f}")
        print(f"   🔧 Type: {ensemble_type}")
        print(f"   🤖 Models: {models_count}")
        
        # Show improvement comparison
        original_accuracy = 0.6591
        improvement = ((accuracy - original_accuracy) / original_accuracy) * 100
        print(f"   📈 Improvement: +{improvement:.1f}% from original")
        
    else:
        print("❌ Ensemble training failed")

except Exception as e:
    print(f"❌ Ensemble error: {e}")
    import traceback
    traceback.print_exc()

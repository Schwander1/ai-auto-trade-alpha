#!/usr/bin/env python3
"""
Performance Optimization Script
Identifies and suggests optimizations for signal generation performance
"""
import json
import sys
from pathlib import Path

config_path = Path(__file__).parent.parent / "argo" / "config.json"

def analyze_performance():
    """Analyze current configuration and suggest optimizations"""
    if not config_path.exists():
        print("❌ Config file not found")
        return
    
    with open(config_path) as f:
        config = json.load(f)
    
    print("=" * 70)
    print("⚡ PERFORMANCE OPTIMIZATION ANALYSIS")
    print("=" * 70)
    print()
    
    # Check cache settings
    chinese_models = config.get('chinese_models', {})
    cache_market = chinese_models.get('cache_ttl_market_hours', 120)
    cache_off = chinese_models.get('cache_ttl_off_hours', 60)
    
    print("📊 CURRENT CACHE SETTINGS:")
    print(f"   Market Hours: {cache_market}s ({cache_market/60:.1f} min)")
    print(f"   Off Hours: {cache_off}s ({cache_off/60:.1f} min)")
    print()
    
    if cache_market < 300:
        print("💡 OPTIMIZATION: Increase market hours cache to 600s (10 min)")
        print("   This will reduce API calls by 5x")
    else:
        print("✅ Cache settings are optimized")
    print()
    
    # Check performance budgets
    perf_budgets = config.get('enhancements', {}).get('performance_budgets', {})
    signal_gen_budget = perf_budgets.get('signal_generation_max_ms', 500)
    
    print("📊 PERFORMANCE BUDGETS:")
    print(f"   Signal Generation: {signal_gen_budget}ms")
    print()
    
    if signal_gen_budget < 1000:
        print("💡 OPTIMIZATION: Consider increasing signal generation budget to 1000-2000ms")
        print("   Current budget may be too aggressive for multi-source consensus")
    print()
    
    # Check data source priorities
    strategy = config.get('strategy', {})
    print("📊 DATA SOURCE WEIGHTS:")
    print(f"   Massive: {strategy.get('weight_massive', 0.4)*100:.0f}%")
    print(f"   Alpha Vantage: {strategy.get('weight_alpha_vantage', 0.25)*100:.0f}%")
    print(f"   X Sentiment: {strategy.get('weight_x_sentiment', 0.2)*100:.0f}%")
    print(f"   Sonar: {strategy.get('weight_sonar', 0.15)*100:.0f}%")
    print(f"   Chinese Models: {strategy.get('weight_chinese_models', 0.1)*100:.0f}%")
    print()
    
    # Check Chinese models configuration
    print("📊 CHINESE MODELS CONFIGURATION:")
    glm = chinese_models.get('glm', {})
    deepseek = chinese_models.get('baichuan', {})
    
    print(f"   GLM:")
    print(f"     Enabled: {glm.get('enabled', False)}")
    print(f"     RPM: {glm.get('requests_per_minute', 30)}")
    print(f"     Budget: ${glm.get('daily_budget', 0.0)}/day")
    
    print(f"   DeepSeek:")
    print(f"     Enabled: {deepseek.get('enabled', False)}")
    print(f"     RPM: {deepseek.get('requests_per_minute', 5)}")
    print(f"     Budget: ${deepseek.get('daily_budget', 0.5)}/day")
    print()
    
    # Recommendations
    print("💡 RECOMMENDATIONS:")
    print()
    
    recommendations = []
    
    # Cache optimization
    if cache_market < 300:
        recommendations.append("Increase cache_ttl_market_hours to 600s (10 min)")
    
    # Performance budget
    if signal_gen_budget < 1000:
        recommendations.append("Increase signal_generation_max_ms to 1000-2000ms")
    
    # Parallel processing
    recommendations.append("Ensure parallel data source fetching is enabled")
    
    # Chinese models
    if glm.get('enabled') and glm.get('daily_budget', 0) == 0:
        recommendations.append("GLM is FREE - maximize usage (already optimized)")
    
    if deepseek.get('enabled') and deepseek.get('requests_per_minute', 25) > 5:
        recommendations.append("DeepSeek RPM is high - consider reducing to 5 for fallback only")
    
    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")
    else:
        print("   ✅ Configuration is already optimized!")
    
    print()
    print("=" * 70)

if __name__ == '__main__':
    try:
        analyze_performance()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


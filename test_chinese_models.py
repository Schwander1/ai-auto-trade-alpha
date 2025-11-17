#!/usr/bin/env python3
"""Quick test of Chinese Models integration"""
import asyncio
import sys
import os
import json
sys.path.insert(0, 'argo')

# Import directly to avoid dependency issues
import importlib.util
spec = importlib.util.spec_from_file_location('chinese_models_source', 'argo/argo/core/data_sources/chinese_models_source.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
ChineseModelsDataSource = module.ChineseModelsDataSource

async def test_chinese_models():
    """Test Chinese models with actual API calls"""
    print("🧪 Testing Chinese Models Integration\n")
    
    # Load config
    with open('argo/config.json') as f:
        config_data = json.load(f)
    
    chinese_config = config_data.get('chinese_models', {})
    qwen_config = chinese_config.get('qwen', {})
    glm_config = chinese_config.get('glm', {})
    baichuan_config = chinese_config.get('baichuan', {})
    
    # Prepare config
    config = {
        'qwen_api_key': qwen_config.get('api_key', ''),
        'qwen_access_key_id': qwen_config.get('access_key_id', ''),
        'qwen_access_key_secret': qwen_config.get('access_key_secret', ''),
        'qwen_enabled': qwen_config.get('enabled', False),
        'qwen_model': qwen_config.get('model', 'qwen-turbo'),
        'glm_api_key': glm_config.get('api_key', ''),
        'glm_enabled': glm_config.get('enabled', False),
        'glm_model': glm_config.get('model', 'glm-4.5-air'),
        'baichuan_api_key': baichuan_config.get('api_key', ''),
        'baichuan_enabled': baichuan_config.get('enabled', False),
        'baichuan_model': baichuan_config.get('model', 'deepseek-chat'),
    }
    
    # Initialize
    print("📦 Initializing Chinese Models DataSource...")
    ds = ChineseModelsDataSource(config)
    print(f"✅ Initialized! Enabled models: {[name for name, _, _ in ds.models]}\n")
    
    # Test with sample market data
    test_symbol = "AAPL"
    market_data = {
        'price': 175.50,
        'close': 175.50,
        'volume': 50000000
    }
    
    print(f"🔍 Testing signal generation for {test_symbol}...")
    print(f"   Market data: ${market_data['price']:.2f}, Volume: {market_data['volume']:,}\n")
    
    try:
        signal = await ds.get_signal(test_symbol, market_data)
        if signal:
            print("✅ Signal received!")
            print(f"   Source: {signal.get('source')}")
            print(f"   Direction: {signal.get('direction')}")
            print(f"   Confidence: {signal.get('confidence')}%")
            print(f"   Analysis: {signal.get('analysis', 'N/A')[:100]}...")
            print(f"   Timestamp: {signal.get('timestamp')}")
        else:
            print("⚠️  No signal returned (all models may have failed or rate limited)")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Show cost report
    print("\n💰 Cost Report:")
    cost_report = ds.get_cost_report()
    for model, stats in cost_report.items():
        if isinstance(stats, dict) and 'total_requests' in stats:
            print(f"   {model}: {stats.get('total_requests', 0)} requests, ${stats.get('daily_cost', 0):.4f} today")

if __name__ == "__main__":
    asyncio.run(test_chinese_models())


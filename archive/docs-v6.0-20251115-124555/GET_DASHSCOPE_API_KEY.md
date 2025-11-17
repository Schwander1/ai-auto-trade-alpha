# Get DashScope API Key - Quick Guide

## ✅ Network Policies Updated!

Now you need to get the DashScope API key to enable Qwen.

## Steps to Get DashScope API Key

### Step 1: Access DashScope Console
1. Go to: **https://dashscope.console.aliyun.com/**
2. Sign in with your Alibaba Cloud account (same account with the AccessKey)

### Step 2: Navigate to API Keys
1. In the DashScope console, look for:
   - **API Keys** in the left sidebar, OR
   - **Model Studio** → **API Keys**, OR
   - **Settings** → **API Keys**

### Step 3: Create API Key
1. Click **Create API Key** or **New API Key**
2. Give it a name (e.g., "Argo Trading System")
3. Set permissions (allow access to Qwen models)
4. Click **Create** or **Confirm**

### Step 4: Copy the API Key
1. **Important**: Copy the API key immediately - it won't be shown again!
2. The API key will look something like: `sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### Step 5: Add to Config
Once you have the API key, I can help you add it to `config.json`:

```json
"qwen": {
  "api_key": "YOUR_DASHSCOPE_API_KEY_HERE",
  "enabled": true,
  "model": "qwen-turbo",
  ...
}
```

## After Adding API Key

Run this to test:
```bash
python3 test_chinese_models.py
```

Or test Qwen specifically:
```bash
python3 -c "
import asyncio
import sys
import json
sys.path.insert(0, 'argo')
from argo.core.data_sources.chinese_models_source import ChineseModelsDataSource

async def test():
    with open('argo/config.json') as f:
        config = json.load(f)
    chinese = config.get('chinese_models', {})
    qwen_config = chinese.get('qwen', {})
    
    config_dict = {
        'qwen_api_key': qwen_config.get('api_key', ''),
        'qwen_enabled': True,
        'qwen_model': 'qwen-turbo',
    }
    
    ds = ChineseModelsDataSource(config_dict)
    signal = await ds._query_qwen('AAPL', {'price': 175.50, 'close': 175.50, 'volume': 50000000})
    if signal:
        print(f'✅ Qwen working! Direction: {signal.get(\"direction\")}, Confidence: {signal.get(\"confidence\")}%')
    else:
        print('⚠️  Qwen returned None')

asyncio.run(test())
"
```

## Troubleshooting

### "API Key Not Found"
- Verify you copied the entire API key
- Check for extra spaces before/after
- Ensure API key is in `qwen.api_key` field

### "Access Denied"
- Verify network policies are configured correctly
- Check IP whitelist includes your IP (or 0.0.0.0/0 for testing)
- Ensure API key has proper permissions

### "Rate Limit Exceeded"
- Check rate limit settings in DashScope console
- Adjust rate limits if needed

---

**Ready?** Once you have the DashScope API key, share it and I'll add it to the config!


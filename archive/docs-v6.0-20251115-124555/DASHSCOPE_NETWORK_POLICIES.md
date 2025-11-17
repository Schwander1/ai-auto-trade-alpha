# DashScope Network Policies Configuration Guide

## Network Policies for DashScope API

When using DashScope (Qwen) API, you may need to configure network policies in the Alibaba Cloud console to allow API access.

## Common Network Policy Settings

### 1. IP Whitelist
- **Location**: DashScope Console → Security Settings → IP Whitelist
- **Action**: Add your server's IP address(es) to the whitelist
- **Note**: If left empty, all IPs are allowed (less secure)

### 2. API Key Permissions
- **Location**: DashScope Console → API Keys → [Your API Key] → Permissions
- **Settings**:
  - Model access permissions
  - Rate limits
  - Usage quotas

### 3. Security Policies
- **Location**: Alibaba Cloud Console → Security → Access Control
- **Settings**:
  - VPC access rules
  - Security group rules
  - Network ACLs

### 4. CORS Settings (if using from browser)
- **Location**: DashScope Console → Settings → CORS
- **Action**: Configure allowed origins if accessing from web

## Steps to Configure

### Step 1: Access DashScope Console
1. Go to: https://dashscope.console.aliyun.com/
2. Sign in with your Alibaba Cloud account

### Step 2: Configure Network Policies
1. Navigate to: **Security Settings** or **API Management**
2. Find **IP Whitelist** or **Network Access Control**
3. Add your IP addresses:
   - For local development: Your current public IP
   - For production: Your server's IP address(es)
   - Or leave empty to allow all IPs (not recommended for production)

### Step 3: Create/Configure API Key
1. Go to: **API Keys** section
2. Click **Create API Key** or select existing key
3. Configure:
   - **Name**: Give it a descriptive name
   - **Permissions**: Select which models to allow
   - **Rate Limits**: Set request limits
   - **Network Access**: Configure IP whitelist if needed

### Step 4: Test API Access
After configuring, test the API key:
```bash
python3 test_chinese_models.py
```

## Common Issues

### Issue: "Access Denied" or "Network Policy Violation"
**Solution**: 
- Check IP whitelist settings
- Ensure your IP is in the allowed list
- Or temporarily allow all IPs for testing

### Issue: "API Key Not Found"
**Solution**:
- Verify API key is created in DashScope console
- Check API key is copied correctly (no extra spaces)
- Ensure API key has proper permissions

### Issue: "Rate Limit Exceeded"
**Solution**:
- Check rate limit settings in API key configuration
- Adjust rate limits in DashScope console
- Or wait for rate limit window to reset

## Security Best Practices

1. **Use IP Whitelist**: Restrict API access to known IPs
2. **Rotate API Keys**: Regularly rotate API keys
3. **Monitor Usage**: Check API usage logs regularly
4. **Set Rate Limits**: Configure appropriate rate limits
5. **Use Least Privilege**: Only grant necessary permissions

## Configuration in Code

Once you have the DashScope API key, update `config.json`:

```json
"qwen": {
  "api_key": "YOUR_DASHSCOPE_API_KEY_HERE",
  "enabled": true,
  "model": "qwen-turbo",
  "requests_per_minute": 20,
  "cost_per_request": 0.002,
  "daily_budget": 50.0
}
```

## Testing After Configuration

After configuring network policies and API key:

```bash
# Test Qwen specifically
python3 -c "
import asyncio
import sys
sys.path.insert(0, 'argo')
from argo.core.data_sources.chinese_models_source import ChineseModelsDataSource
import json

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
        print('⚠️  Qwen returned None - check network policies and API key')

asyncio.run(test())
"
```

## Next Steps

1. ✅ Configure network policies in DashScope console
2. ✅ Create DashScope API key
3. ✅ Add API key to `config.json`
4. ✅ Test API access
5. ✅ Enable Qwen in config

---

**Note**: Network policies are important for security but can block legitimate access if not configured correctly. Start with allowing all IPs for testing, then restrict once everything works.


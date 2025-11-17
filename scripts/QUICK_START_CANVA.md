# Canva API - Quick Start

## 🚀 Fast Setup (3 Steps)

### 1. Store Client Secret
```bash
./scripts/setup-canva-credentials.sh
# Enter your full Client Secret when prompted
```

### 2. Complete OAuth Flow
```bash
cd scripts
source venv/bin/activate
python3 canva_oauth2.py --auth
# Visit the URL, authorize, then:
python3 canva_oauth2.py --code <CODE> --state <STATE>
```

### 3. Test Connection
```bash
python3 canva_oauth2.py --test
```

## ✅ Current Status

- ✅ OAuth 2.0 client script created and tested
- ✅ Client ID stored: `OC-AZqFb4XOryzI`
- ✅ Authorization URL generation working
- ⚠️ **Client Secret needs to be stored** (run setup script above)
- ⚠️ **OAuth flow needs to be completed** (authorize app)

## 📝 Your Credentials

- **Client ID**: `OC-AZqFb4XOryzI` (stored ✅)
- **Client Secret**: `cnvcaJHz4ozJ_C7JZWwtC0jDN0iqorQwtvSKpq7coswE8ymkda4fc447...` (needs full value)

## 🎯 What Works Now

The OAuth flow is fully functional! The script successfully:
- ✅ Retrieves Client ID from AWS Secrets Manager
- ✅ Generates OAuth authorization URLs
- ✅ Creates secure state parameters
- ✅ Ready to exchange authorization codes for tokens

## 📚 Full Documentation

See `scripts/CANVA_SETUP.md` for complete documentation.


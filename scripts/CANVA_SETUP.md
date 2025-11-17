# Canva API Integration Setup Guide

Complete setup guide for Alpine Analytics Canva brand automation.

## ✅ What's Been Set Up

1. **OAuth 2.0 Client Script** (`canva_oauth2.py`) - Complete OAuth flow implementation
2. **Brand Automation Script** (`canva_brand_automation.py`) - High-level brand asset generation
3. **Setup Script** (`setup-canva-credentials.sh`) - Credential storage helper
4. **Client ID Stored** - `OC-AZqFb4XOryzI` stored in AWS Secrets Manager

## 🔑 Credentials Status

- ✅ **Client ID**: Stored in AWS Secrets Manager (`alpine-analytics/canva-client-id`)
- ⚠️ **Client Secret**: **NEEDS TO BE STORED** (see Step 2 below)

## 📋 Setup Steps

### Step 1: Store Client Secret

You need to store your full Client Secret. Run:

```bash
./scripts/setup-canva-credentials.sh
```

Or manually:

```bash
aws secretsmanager create-secret \
    --name alpine-analytics/canva-client-secret \
    --secret-string "YOUR_FULL_CLIENT_SECRET_HERE" \
    --description "Canva OAuth Client Secret for Alpine Analytics brand automation"
```

### Step 2: Complete OAuth Flow

1. **Get Authorization URL:**
   ```bash
   cd scripts
   source venv/bin/activate
   python3 canva_oauth2.py --auth
   ```

2. **Visit the URL** in your browser and authorize the app

3. **Copy the authorization code** from the redirect URL (the `code` parameter)

4. **Exchange code for token:**
   ```bash
   python3 canva_oauth2.py --code <AUTHORIZATION_CODE> --state <STATE_FROM_STEP_1>
   ```

### Step 3: Test API Connection

```bash
python3 canva_oauth2.py --test
```

### Step 4: List Your Designs

```bash
python3 canva_oauth2.py --list-designs
```

## 🎨 Using Brand Automation

### Generate Social Media Post

```bash
python3 canva_brand_automation.py \
    --generate-social <TEMPLATE_ID> \
    --title "Alpine Analytics - New Signal Release" \
    --description "Check out our latest trading signals with 95%+ win rate" \
    --cta "Learn More"
```

## 📁 File Structure

```
scripts/
├── canva_oauth2.py              # OAuth 2.0 client
├── canva_brand_automation.py    # Brand automation
├── setup-canva-credentials.sh   # Credential setup
├── requirements.txt             # Python dependencies
├── venv/                        # Virtual environment
└── CANVA_SETUP.md              # This file
```

## 🔧 Configuration

### Environment Variables (Optional)

If you prefer environment variables over AWS Secrets Manager:

```bash
export CANVA_CLIENT_ID="OC-AZqFb4XOryzI"
export CANVA_CLIENT_SECRET="your_secret_here"
export CANVA_REDIRECT_URI="http://localhost:3000/auth/canva/callback"
```

### Redirect URI

Make sure your Canva integration has this redirect URI configured:
- `https://www.canva.com/apps/oauth/authorized` (for integrations - this is the default)

**Note:** The script now supports PKCE (Proof Key for Code Exchange) which is required by Canva integrations.

## 🚀 Next Steps

1. **Store Client Secret** (if not done yet)
2. **Complete OAuth flow** to get access token
3. **Create branded templates** in Canva
4. **Use automation scripts** to generate assets

## 📚 API Reference

### CanvaOAuth2Client Methods

- `get_authorization_url()` - Get OAuth authorization URL
- `exchange_authorization_code(code, state)` - Exchange code for token
- `list_designs(limit=50)` - List user's designs
- `get_design(design_id)` - Get design details
- `create_design_from_template(template_id, autofill_data)` - Create from template
- `export_design(design_id, format="PNG", quality="high")` - Export design

### AlpineBrandAutomation Methods

- `generate_social_post(template_id, title, description, cta)` - Generate social post
- `generate_pdf_report(template_id, title, content)` - Generate PDF report
- `list_templates()` - List available templates

## 🐛 Troubleshooting

### "Client ID not configured"
- Check AWS Secrets Manager: `aws secretsmanager get-secret-value --secret-id alpine-analytics/canva-client-id`
- Or set environment variable: `export CANVA_CLIENT_ID="OC-AZqFb4XOryzI"`

### "ModuleNotFoundError: No module named 'requests'"
- Activate virtual environment: `source scripts/venv/bin/activate`
- Or install: `pip install -r scripts/requirements.txt`

### "Invalid state parameter"
- Make sure to use the state from `--auth` command when exchanging code

### OAuth token expired
- Tokens are automatically refreshed
- If refresh fails, re-run OAuth flow

## 📝 Notes

- Tokens are stored in `~/.alpine/canva_oauth_tokens.json`
- Tokens are automatically refreshed when expired
- All API calls use OAuth 2.0 Bearer token authentication


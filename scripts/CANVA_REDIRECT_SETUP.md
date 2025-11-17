# Canva Redirect URI Setup Guide

## Important: Local Development Requirements

According to Canva documentation:
- ✅ **Allowed**: `http://127.0.0.1:<port>`
- ❌ **NOT Allowed**: `http://localhost:<port>`

## Setup Steps

### 1. Configure Redirect URI in Canva

1. Go to: https://www.canva.com/developers/
2. Open your **integration** (not app)
3. Navigate to: **Authentication** → **Authorized redirects**
4. Click **Add redirect URL**
5. Enter: `http://127.0.0.1:3000/auth/canva/callback`
6. Save changes

### 2. Set Environment Variable (Optional)

```bash
export CANVA_REDIRECT_URI="http://127.0.0.1:3000/auth/canva/callback"
```

### 3. Generate Authorization URL

```bash
cd scripts
source venv/bin/activate
python3 canva_oauth2.py --auth
```

## Common Issues

### "Bad Request" Error

This usually means:
1. **Redirect URI not registered** - Make sure it's added in Canva settings
2. **Wrong format** - Must be `http://127.0.0.1:3000/...` not `localhost`
3. **Scopes mismatch** - Check scopes in Canva match what's in the request

### 404 Error

This means:
1. **Redirect URI doesn't match** - Must be exactly the same in Canva and script
2. **Integration not activated** - Make sure OAuth is enabled
3. **Wrong integration type** - Make sure you're using an "integration" not "app"

## Verification Checklist

- [ ] Redirect URI added in Canva: `http://127.0.0.1:3000/auth/canva/callback`
- [ ] Using `127.0.0.1` not `localhost`
- [ ] No trailing slash
- [ ] Scopes match in Canva settings
- [ ] Integration is saved and active

## Production Redirect URI

For production, use your actual domain:
```
https://alpineanalytics.com/auth/canva/callback
```

Make sure to add this in Canva settings as well.


# Fixing "Bad Request" Error

## Problem

You're getting:
```json
{"error":"ERROR_BAD_REQUEST","details":{"title":"Bad request.","detail":"Bad Request"}}
```

## Solution

The "Bad Request" error is usually caused by:

### 1. Redirect URI Not Registered

**Fix:** Add the redirect URI in Canva Developer Portal

1. Go to: https://www.canva.com/developers/
2. Open your **integration**
3. Navigate to: **Authentication** → **Authorized redirects**
4. Click **Add redirect URL**
5. Enter: `http://127.0.0.1:3000/auth/canva/callback`
6. **Save changes**

**Important:** 
- ✅ Use `127.0.0.1` (NOT `localhost`)
- ✅ No trailing slash
- ✅ Must match exactly what's in the authorization URL

### 2. Scopes Mismatch

**Fix:** Check scopes in Canva match the request

1. In Canva Developer Portal → **Scopes**
2. Make sure you have selected:
   - `design:read`
   - `design:write`
3. The scopes in the authorization URL must match exactly

### 3. Client ID/Secret Issues

**Verify credentials:**
```bash
aws secretsmanager get-secret-value --secret-id alpine-analytics/canva-client-id --query SecretString --output text
aws secretsmanager get-secret-value --secret-id alpine-analytics/canva-client-secret --query SecretString --output text | head -c 20
```

## Quick Fix Steps

1. **Add Redirect URI in Canva:**
   - Authentication → Authorized redirects
   - Add: `http://127.0.0.1:3000/auth/canva/callback`
   - Save

2. **Verify Scopes:**
   - Scopes → Reading and writing
   - Enable: `design:read`, `design:write`
   - Save

3. **Regenerate Authorization URL:**
   ```bash
   cd scripts
   source venv/bin/activate
   python3 canva_oauth2.py --auth
   ```

4. **Try Again:**
   - Visit the new authorization URL
   - Should work now!

## Verification

After adding the redirect URI, the authorization URL should work. The redirect URI in the URL must **exactly match** what's in Canva settings.

## Still Not Working?

If you still get "Bad Request":
1. Double-check redirect URI matches exactly (case-sensitive)
2. Verify scopes are enabled in Canva
3. Make sure integration is saved and active
4. Try clearing browser cache
5. Check Canva status page for outages


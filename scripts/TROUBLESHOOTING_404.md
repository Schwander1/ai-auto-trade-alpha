# Troubleshooting 404 Error

## Common Causes

The 404 error when visiting the OAuth authorization URL is usually caused by:

### 1. Redirect URI Mismatch (Most Common)

The redirect URI in your Canva integration settings **must exactly match** the one in the authorization URL.

**Check in Canva Developer Portal:**
1. Go to https://www.canva.com/developers/
2. Open your **integration** (not app)
3. Navigate to OAuth/Settings
4. Find the "Redirect URL" or "Redirect URI" field
5. It must be exactly: `https://www.canva.com/apps/oauth/authorized`

**Common mistakes:**
- ❌ `http://` instead of `https://`
- ❌ Trailing slash: `https://www.canva.com/apps/oauth/authorized/`
- ❌ Different path
- ❌ Case sensitivity issues

### 2. Integration Not Activated

Make sure your integration is:
- ✅ Created and saved
- ✅ OAuth is enabled
- ✅ Not in draft mode (if applicable)

### 3. Client ID Mismatch

Verify the Client ID in the URL matches your integration:
- Your Client ID: `OC-AZqFb4XOryzI`
- Check it matches in Canva Developer Portal

## Verification Steps

1. **Check Redirect URI in Canva:**
   ```
   Must be: https://www.canva.com/apps/oauth/authorized
   ```

2. **Verify Client ID:**
   ```bash
   aws secretsmanager get-secret-value --secret-id alpine-analytics/canva-client-id --query SecretString --output text
   ```
   Should return: `OC-AZqFb4XOryzI`

3. **Test URL Format:**
   The authorization URL should look like:
   ```
   https://www.canva.com/api/oauth/authorize?
     response_type=code&
     client_id=OC-AZqFb4XOryzI&
     redirect_uri=https%3A%2F%2Fwww.canva.com%2Fapps%2Foauth%2Fauthorized&
     scope=design%3Aread+design%3Awrite+user%3Aread&
     state=...&
     code_challenge_method=S256&
     code_challenge=...
   ```

## Quick Fix

1. **Update Redirect URI in Canva:**
   - Go to your integration settings
   - Set Redirect URI to: `https://www.canva.com/apps/oauth/authorized`
   - Save changes

2. **Regenerate Authorization URL:**
   ```bash
   cd scripts
   source venv/bin/activate
   python3 canva_oauth2.py --auth
   ```

3. **Try Again:**
   - Visit the new authorization URL
   - Should work now!

## Alternative: Check Integration Type

If you created an "integration" vs an "app", make sure you're using the correct OAuth flow:
- **Integration**: Uses `https://www.canva.com/apps/oauth/authorized`
- **App**: Might use different redirect URI

## Still Not Working?

If the redirect URI is correct and you still get 404:
1. Check Canva's status page
2. Verify your integration is not suspended
3. Try creating a new integration
4. Contact Canva support with your Client ID


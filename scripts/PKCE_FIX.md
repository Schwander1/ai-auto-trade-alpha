# PKCE Support Added ✅

## What Was Fixed

The OAuth script now supports **PKCE (Proof Key for Code Exchange)** which is required by Canva integrations.

## Changes Made

1. ✅ Added PKCE code generation (`_generate_pkce()` method)
2. ✅ Updated authorization URL to include `code_challenge` and `code_challenge_method=S256`
3. ✅ Updated token exchange to include `code_verifier`
4. ✅ Updated default redirect URI to `https://www.canva.com/apps/oauth/authorized`

## How It Works

1. **Authorization URL Generation:**
   - Generates a random `code_verifier`
   - Creates `code_challenge` (SHA256 hash of verifier)
   - Includes both in the authorization URL

2. **Token Exchange:**
   - Uses the `code_verifier` when exchanging authorization code for token
   - Canva verifies the challenge matches the verifier

## Testing

The script now generates URLs like:
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

## Next Steps

1. Visit the authorization URL from `python3 canva_oauth2.py --auth`
2. Authorize the app
3. Copy the authorization code from the redirect URL
4. Exchange code: `python3 canva_oauth2.py --code <CODE> --state <STATE>`

## Status

✅ PKCE support implemented
✅ Redirect URI updated
✅ Ready to test OAuth flow


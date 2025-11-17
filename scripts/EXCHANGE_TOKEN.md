# Exchange Authorization Code for Token

## After Authorization

After clicking "Allow" in Canva, you'll be redirected to:
```
http://127.0.0.1:3000/auth/canva/callback?code=AUTHORIZATION_CODE&state=STATE_VALUE
```

## Extract the Code

1. **Copy the entire redirect URL** from your browser's address bar
2. **Find the `code` parameter** - it's the value after `code=`
3. **Find the `state` parameter** - it's the value after `state=`

Example:
```
http://127.0.0.1:3000/auth/canva/callback?code=abc123xyz&state=KIZYeMo1SYXHiDpxoSrCcty8KAA1hAM2TFiUgcJI3NM
```
- Code: `abc123xyz`
- State: `KIZYeMo1SYXHiDpxoSrCcty8KAA1hAM2TFiUgcJI3NM`

## Exchange Code for Token

Run this command (replace with your actual values):

```bash
cd scripts
source venv/bin/activate
python3 canva_oauth2.py --code <AUTHORIZATION_CODE> --state <STATE>
```

Example:
```bash
python3 canva_oauth2.py --code abc123xyz --state KIZYeMo1SYXHiDpxoSrCcty8KAA1hAM2TFiUgcJI3NM
```

## Success!

If successful, you'll see:
```
✅ OAuth 2.0 Authentication Successful!
   Access token expires in: 3600 seconds
   Token type: Bearer
   ✅ Refresh token received
```

## Test API Connection

After getting the token, test the connection:

```bash
python3 canva_oauth2.py --test
```

Or list your designs:

```bash
python3 canva_oauth2.py --list-designs
```

## Troubleshooting

### "Invalid state parameter"
- Make sure you're using the state from the `--auth` command
- The state must match exactly

### "Code verifier not found"
- Make sure you ran `--auth` first to generate PKCE values
- The code verifier is stored in memory during the session

### Token exchange fails
- Check that the authorization code hasn't expired (usually expires quickly)
- Make sure you're using the code from the most recent authorization


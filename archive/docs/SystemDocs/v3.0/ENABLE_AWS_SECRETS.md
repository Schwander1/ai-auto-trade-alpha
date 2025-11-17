# Enabling AWS Secrets Manager

## Quick Setup

To enable AWS Secrets Manager for your services, set the environment variable:

```bash
export USE_AWS_SECRETS=true
```

## Making It Persistent

### Option 1: Add to .env Files (Recommended)

Add this line to your `.env` files:

**For Argo** (`argo/.env`):
```env
USE_AWS_SECRETS=true
```

**For Alpine Backend** (`alpine-backend/.env`):
```env
USE_AWS_SECRETS=true
```

### Option 2: Add to Shell Profile

Add to your `~/.zshrc` or `~/.bashrc`:

```bash
export USE_AWS_SECRETS=true
```

Then reload:
```bash
source ~/.zshrc  # or source ~/.bashrc
```

### Option 3: Set in Docker Compose

If using Docker, add to `docker-compose.yml`:

```yaml
environment:
  - USE_AWS_SECRETS=true
```

### Option 4: Set in Systemd Service Files

If running as systemd services, add to service files:

```ini
[Service]
Environment="USE_AWS_SECRETS=true"
```

## Verification

After setting the variable, verify it's working:

```bash
# Check environment variable
echo $USE_AWS_SECRETS

# Should output: true
```

## Behavior

When `USE_AWS_SECRETS=true`:
- ✅ Services will use AWS Secrets Manager as primary source
- ✅ Falls back to environment variables if AWS is unavailable
- ✅ Caches secrets for 5 minutes

When `USE_AWS_SECRETS=false` or unset:
- ✅ Services will use environment variables only
- ✅ Useful for local development without AWS access

## Testing

After enabling, restart your services and check health:

```bash
# Restart services
# Argo
cd argo && source venv/bin/activate && uvicorn main:app --reload

# Alpine Backend
cd alpine-backend && source venv/bin/activate && uvicorn backend.main:app --reload

# Verify
python scripts/verify-secrets-health.py
```

The health check should show `secrets: healthy` when AWS Secrets Manager is working correctly.


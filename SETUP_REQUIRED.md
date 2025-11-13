# ⚠️ Action Required: IAM Permissions Setup

## Quick Summary

Your IAM user needs permissions to create secrets. **Choose one option below:**

---

## ✅ Option 1: AWS Console (5 minutes)

1. **Go to**: https://console.aws.amazon.com/iam/
2. **Create Policy**:
   - Policies → Create Policy → JSON tab
   - Copy from: `scripts/iam-policy-secrets-manager.json`
   - Name: `ArgoAlpineSecretsManagerAccess`
3. **Attach to User**:
   - Users → `argo-compliance-backup` → Add permissions
   - Attach the policy you just created
4. **Run**: `python scripts/add-additional-secrets.py`

**Full instructions**: See `docs/SystemDocs/IAM_SETUP_INSTRUCTIONS.md`

---

## ✅ Option 2: Ask AWS Admin

Ask your AWS administrator to:
1. Create policy from: `scripts/iam-policy-secrets-manager.json`
2. Attach it to user: `argo-compliance-backup`

---

## ✅ Option 3: Use Admin AWS Profile

If you have admin credentials:

```bash
# Configure admin profile
aws configure --profile admin

# Setup permissions
AWS_PROFILE=admin ./scripts/setup-secrets-permissions.sh

# Add secrets (with your regular profile)
python scripts/add-additional-secrets.py
```

---

## After Setup

Once permissions are configured:

```bash
# Add all secrets
python scripts/add-additional-secrets.py

# Verify
python scripts/verify-secrets-health.py
```

---

**Need help?** See `docs/SystemDocs/IAM_SETUP_INSTRUCTIONS.md` for detailed steps.


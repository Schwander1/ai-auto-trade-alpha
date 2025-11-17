# IAM Permissions Setup - Action Required

## Current Situation

Your IAM user (`argo-compliance-backup`) doesn't have permission to:
- Create IAM policies
- Create secrets in AWS Secrets Manager

## What You Need To Do

You have **3 options** to proceed:

---

## Option 1: AWS Console (Easiest - Recommended)

### Step 1: Create IAM Policy

1. **Go to AWS IAM Console**: https://console.aws.amazon.com/iam/
2. **Click "Policies"** in the left sidebar
3. **Click "Create Policy"**
4. **Click the "JSON" tab**
5. **Copy and paste this policy**:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "SecretsManagerFullAccess",
      "Effect": "Allow",
      "Action": [
        "secretsmanager:CreateSecret",
        "secretsmanager:PutSecretValue",
        "secretsmanager:GetSecretValue",
        "secretsmanager:DescribeSecret",
        "secretsmanager:ListSecrets",
        "secretsmanager:UpdateSecret",
        "secretsmanager:TagResource"
      ],
      "Resource": "arn:aws:secretsmanager:*:*:secret:argo-alpine/*"
    },
    {
      "Sid": "SecretsManagerList",
      "Effect": "Allow",
      "Action": [
        "secretsmanager:ListSecrets"
      ],
      "Resource": "*"
    }
  ]
}
```

6. **Click "Next"**
7. **Name**: `ArgoAlpineSecretsManagerAccess`
8. **Description**: `Allows access to Argo-Alpine secrets in AWS Secrets Manager`
9. **Click "Create Policy"**

### Step 2: Attach Policy to User

1. **Go to "Users"** in the left sidebar
2. **Click on**: `argo-compliance-backup`
3. **Click "Add permissions"** button
4. **Select "Attach policies directly"**
5. **Search for**: `ArgoAlpineSecretsManagerAccess`
6. **Check the box** next to the policy
7. **Click "Add permissions"**

### Step 3: Add Secrets

After permissions are set up (wait 10-30 seconds), run:

```bash
python scripts/add-additional-secrets.py
```

---

## Option 2: Ask AWS Admin

If you don't have admin access, ask your AWS administrator to:

1. **Create the IAM policy** using the JSON above
2. **Attach it to user**: `argo-compliance-backup`

The policy file is also saved at: `scripts/iam-policy-secrets-manager.json`

---

## Option 3: Use Different AWS Credentials

If you have another AWS user/role with admin permissions:

1. **Switch AWS credentials**:
   ```bash
   aws configure --profile admin
   # Enter admin credentials
   ```

2. **Run the setup script**:
   ```bash
   AWS_PROFILE=admin ./scripts/setup-secrets-permissions.sh
   ```

3. **Switch back and add secrets**:
   ```bash
   python scripts/add-additional-secrets.py
   ```

---

## After Permissions Are Set Up

Once the policy is attached, you can:

### 1. Add All Secrets

```bash
python scripts/add-additional-secrets.py
```

This will add:
- ✅ Anthropic API key
- ✅ Perplexity Sonar API key
- ✅ X.AI (Grok) API key
- ✅ Sonar Administration key
- ✅ Figma API key
- ✅ NextAuth secret

### 2. Add Tradervue Credentials (Optional)

If you have Tradervue Gold credentials:

```bash
python scripts/add-additional-secrets.py \
  --tradervue-username YOUR_USERNAME \
  --tradervue-token YOUR_TOKEN
```

### 3. Verify Everything Works

```bash
# Verify secrets are accessible
python scripts/verify-secrets-health.py

# Or manually check
aws secretsmanager list-secrets --filters Key=name,Values=argo-alpine
```

---

## Quick Reference

**Policy Name**: `ArgoAlpineSecretsManagerAccess`  
**User**: `argo-compliance-backup`  
**Policy File**: `scripts/iam-policy-secrets-manager.json`

**Secrets to Add**:
- `argo-alpine/argo/anthropic-api-key`
- `argo-alpine/argo/perplexity-api-key`
- `argo-alpine/argo/xai-api-key`
- `argo-alpine/argo/sonar-admin-key`
- `argo-alpine/argo/figma-api-key`
- `argo-alpine/alpine-frontend/nextauth-secret`

---

## Need Help?

If you encounter issues:

1. **Check current AWS identity**:
   ```bash
   aws sts get-caller-identity
   ```

2. **Verify policy is attached**:
   ```bash
   aws iam list-attached-user-policies --user-name argo-compliance-backup
   ```

3. **Test permissions**:
   ```bash
   aws secretsmanager list-secrets --filters Key=name,Values=argo-alpine
   ```

If you see "Access Denied", the policy isn't attached yet or hasn't propagated (wait 30-60 seconds).


# 🔐 AWS IAM Policy Update Guide

## Current Situation

The IAM user `argo-compliance-backup` currently has access to secrets with the `argo-alpine/*` prefix, but needs access to the new prefixes:
- `argo-capital/*` (new Argo prefix)
- `alpine-analytics/*` (new Alpine prefix)

## ✅ Policy File Updated

The policy file has been updated: `scripts/iam-policy-secrets-manager.json`

It now includes all three prefixes for backward compatibility.

---

## 📋 How to Update the Policy in AWS

### Step 1: Open AWS IAM Console

1. Go to: https://console.aws.amazon.com/iam/
2. Make sure you're logged in with an account that has IAM admin permissions

### Step 2: Find the Policy

1. Click **"Policies"** in the left sidebar
2. In the search box, type: `ArgoAlpineSecretsManagerAccess`
3. If not found, search for policies attached to user: `argo-compliance-backup`
4. Click on the policy name

### Step 3: Edit the Policy

1. Click the **"Edit"** button (top right)
2. Click the **"JSON"** tab
3. **Delete all existing JSON**
4. **Copy and paste** the entire contents from: `scripts/iam-policy-secrets-manager.json`

The updated policy JSON:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "SecretsManagerFullAccessArgoCapital",
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
      "Resource": "arn:aws:secretsmanager:*:*:secret:argo-capital/*"
    },
    {
      "Sid": "SecretsManagerFullAccessAlpineAnalytics",
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
      "Resource": "arn:aws:secretsmanager:*:*:secret:alpine-analytics/*"
    },
    {
      "Sid": "SecretsManagerFullAccessArgoAlpine",
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

5. Click **"Next"** button
6. Review the changes
7. Click **"Save changes"**

### Step 4: Wait for Propagation

Wait **10-30 seconds** for permissions to propagate.

### Step 5: Verify (Optional)

Test that the permissions work:

```bash
# Test access to new prefix (should not show AccessDenied)
aws secretsmanager list-secrets --filters Key=name,Values=argo-capital --max-results 1
```

---

## ✅ What This Updates

The updated policy now grants access to:

1. ✅ **argo-capital/*** - New Argo Capital secrets
2. ✅ **alpine-analytics/*** - New Alpine Analytics secrets
3. ✅ **argo-alpine/*** - Legacy secrets (backward compatibility)

---

## 🎯 Result

After updating:
- ✅ System can access secrets with new prefixes
- ✅ Backward compatibility maintained (old prefix still works)
- ✅ No breaking changes
- ✅ System will automatically use new prefixes when available

---

## 📝 Quick Reference

**Policy File Location:** `scripts/iam-policy-secrets-manager.json`

**IAM User:** `argo-compliance-backup`

**AWS Account:** `132141656458`

**Policy Name:** `ArgoAlpineSecretsManagerAccess` (or similar)

---

## ⚠️  Note

If you don't have IAM admin access, ask your AWS administrator to:
1. Open the policy in IAM Console
2. Edit the JSON with the updated policy
3. Save changes

The policy file is ready at: `scripts/iam-policy-secrets-manager.json`


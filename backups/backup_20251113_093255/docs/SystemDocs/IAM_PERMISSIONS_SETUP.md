# IAM Permissions Setup for AWS Secrets Manager

## Quick Setup

Run the automated setup script:

```bash
./scripts/setup-secrets-permissions.sh
```

This will:
1. Create an IAM policy with the necessary permissions
2. Attach it to your IAM user (`argo-compliance-backup`)

## Manual Setup (Alternative)

If the script doesn't work, follow these steps:

### Step 1: Create IAM Policy

1. Go to [AWS IAM Console](https://console.aws.amazon.com/iam/)
2. Click **Policies** → **Create Policy**
3. Click **JSON** tab
4. Paste the following policy:

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

5. Click **Next**
6. Name it: `ArgoAlpineSecretsManagerAccess`
7. Description: `Allows access to Argo-Alpine secrets in AWS Secrets Manager`
8. Click **Create Policy**

### Step 2: Attach Policy to User

1. Go to **Users** → Find `argo-compliance-backup`
2. Click on the user
3. Click **Add permissions** → **Attach policies directly**
4. Search for: `ArgoAlpineSecretsManagerAccess`
5. Select the policy
6. Click **Add permissions**

### Step 3: Verify Permissions

Wait a few seconds for permissions to propagate, then test:

```bash
# Test if you can list secrets
aws secretsmanager list-secrets --filters Key=name,Values=argo-alpine

# If that works, you're ready to add secrets
python scripts/add-additional-secrets.py
```

## Using AWS CLI (Alternative Method)

If you prefer to use AWS CLI directly:

```bash
# Create the policy
aws iam create-policy \
  --policy-name ArgoAlpineSecretsManagerAccess \
  --policy-document file://scripts/iam-policy-secrets-manager.json \
  --description "Allows access to Argo-Alpine secrets in AWS Secrets Manager"

# Note the Policy ARN from the output, then attach it:
aws iam attach-user-policy \
  --user-name argo-compliance-backup \
  --policy-arn arn:aws:iam::YOUR_ACCOUNT_ID:policy/ArgoAlpineSecretsManagerAccess
```

Replace `YOUR_ACCOUNT_ID` with your AWS account ID (you can find it in the policy ARN from the create-policy command).

## Permissions Explained

The policy grants:

1. **CreateSecret** - Create new secrets
2. **PutSecretValue** - Update existing secrets
3. **GetSecretValue** - Read secret values
4. **DescribeSecret** - Get secret metadata
5. **ListSecrets** - List all secrets (for discovery)
6. **UpdateSecret** - Update secret metadata
7. **TagResource** - Add tags to secrets

**Scope:** Only secrets matching `argo-alpine/*` pattern (for security)

## Troubleshooting

### "Access Denied" Error

1. **Wait for propagation**: IAM changes can take 5-60 seconds to propagate
2. **Check policy attachment**: Verify the policy is attached to your user
3. **Verify resource ARN**: Make sure the secret name matches the pattern

### "Policy Already Exists"

If you get this error, the policy already exists. Just attach it:

```bash
# Get the policy ARN
POLICY_ARN=$(aws iam list-policies --query "Policies[?PolicyName=='ArgoAlpineSecretsManagerAccess'].Arn" --output text)

# Attach it
aws iam attach-user-policy \
  --user-name argo-compliance-backup \
  --policy-arn "$POLICY_ARN"
```

### "User Not Found"

If the user doesn't exist, you might need to:
1. Use a different IAM user
2. Create a new IAM user
3. Use an IAM role instead

To check your current AWS identity:

```bash
aws sts get-caller-identity
```

## Security Best Practices

1. **Least Privilege**: The policy only grants access to `argo-alpine/*` secrets
2. **No Delete Permission**: Intentionally excluded to prevent accidental deletion
3. **Audit Trail**: All actions are logged in CloudTrail
4. **Resource-Based**: Permissions are scoped to specific secret names

## Next Steps

After setting up permissions:

1. **Add secrets**: `python scripts/add-additional-secrets.py`
2. **Verify**: `python scripts/verify-secrets-health.py`
3. **Test services**: Restart services and verify they can access secrets


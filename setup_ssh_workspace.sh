#!/bin/bash
# Setup SSH keys via workspace/jump host to production

echo "🔑 SSH Setup via Workspace/Jump Host"
echo "===================================="
echo ""

# Get workspace hostname
if [ -z "$1" ]; then
    echo "Usage: $0 <workspace-hostname-or-ip> [workspace-user]"
    echo ""
    echo "Example: $0 workspace.example.com dylan"
    echo "Example: $0 192.168.1.100 root"
    echo ""
    echo "Or if workspace is in SSH config:"
    echo "  $0 workspace"
    exit 1
fi

WORKSPACE_HOST="$1"
WORKSPACE_USER="${2:-$USER}"

echo "Workspace: $WORKSPACE_USER@$WORKSPACE_HOST"
echo ""

# Get public key
PUBLIC_KEY=$(cat ~/.ssh/id_ed25519.pub 2>/dev/null || cat ~/.ssh/id_rsa.pub 2>/dev/null)

if [ -z "$PUBLIC_KEY" ]; then
    echo "❌ No SSH public key found!"
    exit 1
fi

echo "✅ Your SSH public key:"
echo "$PUBLIC_KEY"
echo ""

echo "📋 Setup Steps:"
echo "==============="
echo ""
echo "Step 1: Add key to workspace (if not already added)"
echo "  ssh $WORKSPACE_USER@$WORKSPACE_HOST"
echo "  mkdir -p ~/.ssh && chmod 700 ~/.ssh"
echo "  echo '$PUBLIC_KEY' >> ~/.ssh/authorized_keys"
echo "  chmod 600 ~/.ssh/authorized_keys"
echo "  exit"
echo ""
echo "Step 2: Test workspace SSH"
echo "  ssh $WORKSPACE_USER@$WORKSPACE_HOST 'echo \"Workspace SSH working!\"'"
echo ""
echo "Step 3: From workspace, add key to production servers"
echo "  ssh $WORKSPACE_USER@$WORKSPACE_HOST"
echo "  # Then on workspace:"
echo "  ssh root@178.156.194.174 'mkdir -p ~/.ssh && chmod 700 ~/.ssh && echo \"$PUBLIC_KEY\" >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys'"
echo "  ssh root@91.98.153.49 'mkdir -p ~/.ssh && chmod 700 ~/.ssh && echo \"$PUBLIC_KEY\" >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys'"
echo "  exit"
echo ""
echo "Step 4: Test production SSH (with agent forwarding)"
echo "  ssh -A $WORKSPACE_USER@$WORKSPACE_HOST"
echo "  # Then on workspace:"
echo "  ssh root@178.156.194.174 'echo \"Argo SSH working!\"'"
echo "  ssh root@91.98.153.49 'echo \"Alpine SSH working!\"'"
echo ""


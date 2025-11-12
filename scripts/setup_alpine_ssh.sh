#!/bin/bash
# Quick setup instructions for SSH key to Alpine server

PUBLIC_KEY=$(cat ~/.ssh/id_ed25519.pub 2>/dev/null || cat ~/.ssh/id_rsa.pub 2>/dev/null)

echo "🔑 SSH Key Setup for Alpine Server"
echo "==================================="
echo ""
echo "Your SSH public key:"
echo "$PUBLIC_KEY"
echo ""
echo "📋 Steps to add key (run in Warp Terminal):"
echo ""
echo "1. SSH to alpine:"
echo "   ssh alpine"
echo ""
echo "2. Once connected, run these commands:"
echo "   mkdir -p ~/.ssh && chmod 700 ~/.ssh"
echo "   echo '$PUBLIC_KEY' >> ~/.ssh/authorized_keys"
echo "   chmod 600 ~/.ssh/authorized_keys"
echo "   exit"
echo ""
echo "3. Test passwordless SSH:"
echo "   ssh alpine 'echo \"✅ SSH key working!\"'"
echo ""
echo "Once that works, we can deploy Alpine!"


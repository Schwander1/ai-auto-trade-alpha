#!/bin/bash
# Script to add SSH key to Alpine server
# Run this when you have SSH access to the server

PUBLIC_KEY="ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIP4zGDkJYclt6xo6t8HadFrWZC1sYyb+O2rVct89YmFO dylanwn95@gmail.com"

echo "🔑 Adding SSH key to Alpine server..."
echo ""
echo "This script will add your SSH key to the server."
echo "You'll need to enter the root password when prompted."
echo ""

# Try to add the key
ssh root@91.98.153.49 "mkdir -p ~/.ssh && chmod 700 ~/.ssh && echo '$PUBLIC_KEY' >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys && echo '✅ SSH key added successfully!'" 2>&1

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ SSH key setup complete!"
    echo ""
    echo "Testing passwordless connection..."
    ssh -o BatchMode=yes root@91.98.153.49 'echo "✅ Passwordless SSH working!"' 2>&1
else
    echo ""
    echo "⚠️  If connection timed out, you may need to:"
    echo "   1. Connect via VPN first"
    echo "   2. Use a different SSH port: ssh -p <PORT> root@91.98.153.49"
    echo "   3. Access via web console and run the commands manually"
    echo ""
    echo "Manual steps:"
    echo "  1. SSH into the server: ssh root@91.98.153.49"
    echo "  2. Run these commands:"
    echo "     mkdir -p ~/.ssh && chmod 700 ~/.ssh"
    echo "     echo '$PUBLIC_KEY' >> ~/.ssh/authorized_keys"
    echo "     chmod 600 ~/.ssh/authorized_keys"
fi


#!/bin/bash

# Script to disable all notifications on macOS

echo "Disabling all notifications on macOS..."

# Method 1: Enable Do Not Disturb via defaults (legacy method)
defaults write com.apple.notificationcenterui doNotDisturb -bool true
defaults write com.apple.notificationcenterui doNotDisturbDate -date "`date -u +%Y-%m-%d\ %H:%M:%S\ +0000`"

# Method 2: Set for current host
defaults -currentHost write ~/Library/Preferences/ByHost/com.apple.notificationcenterui doNotDisturb -bool true
defaults -currentHost write ~/Library/Preferences/ByHost/com.apple.notificationcenterui doNotDisturbDate -date "`date -u +%Y-%m-%d\ %H:%M:%S\ +0000`"

# Method 3: Restart Notification Center to apply changes
killall NotificationCenter 2>/dev/null || true

echo ""
echo "Notifications have been disabled using command-line methods."
echo ""
echo "For complete control on macOS 13+, you may also want to:"
echo "1. Open System Settings > Focus"
echo "2. Enable 'Do Not Disturb' or create a custom Focus mode"
echo "3. Set it to block all notifications"
echo ""
echo "To re-enable notifications later, run:"
echo "  defaults write com.apple.notificationcenterui doNotDisturb -bool false"
echo "  defaults -currentHost write ~/Library/Preferences/ByHost/com.apple.notificationcenterui doNotDisturb -bool false"
echo "  killall NotificationCenter"

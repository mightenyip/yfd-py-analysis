#!/bin/bash
# Setup launchd agents (better than cron for Mac)
# launchd can optionally wake the computer (though may require plugged in + specific settings)

PROJECT_DIR="/Users/mightenyip/Documents/GitHub/yfd-py-test"
LAUNCHD_DIR="$HOME/Library/LaunchAgents"

echo "=========================================="
echo "LAUNCHD SETUP FOR FANTASY AUTOMATION"
echo "=========================================="
echo ""
echo "launchd is macOS's native task scheduler"
echo "Advantages over cron:"
echo "  - Better integration with macOS"
echo "  - More reliable logging"
echo "  - Can trigger on system events"
echo ""
echo "⚠️  Note: Computer must be awake OR plugged in"
echo "    for tasks to run on time"
echo ""

# Create LaunchAgents directory if it doesn't exist
mkdir -p "$LAUNCHD_DIR"

# Copy plist files
echo "Step 1: Copying plist files..."
cp "$PROJECT_DIR/automation/com.fantasy.friday.plist" "$LAUNCHD_DIR/"
cp "$PROJECT_DIR/automation/com.fantasy.monday.plist" "$LAUNCHD_DIR/"
cp "$PROJECT_DIR/automation/com.fantasy.tuesday.plist" "$LAUNCHD_DIR/"
echo "✅ Plist files copied to $LAUNCHD_DIR"
echo ""

# Load the agents
echo "Step 2: Loading launchd agents..."
launchctl load "$LAUNCHD_DIR/com.fantasy.friday.plist"
launchctl load "$LAUNCHD_DIR/com.fantasy.monday.plist"
launchctl load "$LAUNCHD_DIR/com.fantasy.tuesday.plist"
echo "✅ Agents loaded"
echo ""

# Check status
echo "Step 3: Checking agent status..."
launchctl list | grep fantasy
echo ""

echo "=========================================="
echo "SETUP COMPLETE!"
echo "=========================================="
echo ""
echo "Your scrapers will now run:"
echo "  - Friday 8:00 AM"
echo "  - Monday 8:00 AM"
echo "  - Tuesday 8:00 AM"
echo ""
echo "To ensure they run when computer is asleep:"
echo "  1. Keep laptop plugged in"
echo "  2. Set Power settings to not sleep"
echo "  3. OR use a cloud server (see documentation)"
echo ""
echo "To check logs:"
echo "  tail -f ~/Documents/GitHub/yfd-py-test/logs/launchd_*.log"
echo ""
echo "To unload (disable):"
echo "  launchctl unload ~/Library/LaunchAgents/com.fantasy.*.plist"
echo ""


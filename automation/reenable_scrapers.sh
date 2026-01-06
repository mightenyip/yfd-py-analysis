#!/bin/bash
# Re-enable script for weekly fantasy scrapers
# Run this when the next season starts

PROJECT_DIR="/Users/mightenyip/Documents/GitHub/yfd-py-test"
LAUNCHD_DIR="$HOME/Library/LaunchAgents"

echo "=========================================="
echo "RE-ENABLING FANTASY SCRAPERS"
echo "=========================================="
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
launchctl load "$LAUNCHD_DIR/com.fantasy.friday.plist" 2>/dev/null || \
launchctl bootstrap gui/$(id -u) "$LAUNCHD_DIR/com.fantasy.friday.plist" 2>/dev/null || \
echo "  ⚠️  Could not load com.fantasy.friday (may need to use newer launchctl syntax)"

launchctl load "$LAUNCHD_DIR/com.fantasy.monday.plist" 2>/dev/null || \
launchctl bootstrap gui/$(id -u) "$LAUNCHD_DIR/com.fantasy.monday.plist" 2>/dev/null || \
echo "  ⚠️  Could not load com.fantasy.monday (may need to use newer launchctl syntax)"

launchctl load "$LAUNCHD_DIR/com.fantasy.tuesday.plist" 2>/dev/null || \
launchctl bootstrap gui/$(id -u) "$LAUNCHD_DIR/com.fantasy.tuesday.plist" 2>/dev/null || \
echo "  ⚠️  Could not load com.fantasy.tuesday (may need to use newer launchctl syntax)"

echo "✅ Agents loaded"
echo ""

# Check status
echo "Step 3: Checking agent status..."
launchctl list | grep fantasy || echo "  ℹ️  Services may be loaded but not showing in list"
echo ""

echo "=========================================="
echo "RE-ENABLE COMPLETE!"
echo "=========================================="
echo ""
echo "Your scrapers will now run:"
echo "  - Friday 8:00 AM (Thursday Night Football)"
echo "  - Monday 8:00 AM (Sunday games)"
echo "  - Tuesday 8:00 AM (Monday Night Football + weekly report)"
echo ""
echo "To check logs:"
echo "  tail -f $PROJECT_DIR/logs/launchd_*.log"
echo ""


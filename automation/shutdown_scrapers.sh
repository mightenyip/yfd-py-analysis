#!/bin/bash
# Shutdown script for weekly fantasy scrapers
# This disables all automated scrapers until next season

PROJECT_DIR="/Users/mightenyip/Documents/GitHub/yfd-py-test"
LAUNCHD_DIR="$HOME/Library/LaunchAgents"

echo "=========================================="
echo "SHUTTING DOWN FANTASY SCRAPERS"
echo "=========================================="
echo ""

# Step 1: Unload launchd services (if loaded)
echo "Step 1: Unloading launchd services..."
SERVICES=("com.fantasy.friday" "com.fantasy.monday" "com.fantasy.tuesday")

for service in "${SERVICES[@]}"; do
    if launchctl list "$service" &>/dev/null; then
        echo "  - Unloading $service..."
        launchctl unload "$LAUNCHD_DIR/$service.plist" 2>/dev/null || \
        launchctl bootout gui/$(id -u)/"$service" 2>/dev/null || \
        launchctl remove "$service" 2>/dev/null
        echo "    ✅ $service unloaded"
    else
        echo "    ℹ️  $service is not currently loaded"
    fi
done
echo ""

# Step 2: Remove plist files from LaunchAgents (if they exist)
echo "Step 2: Removing plist files from LaunchAgents..."
for service in "${SERVICES[@]}"; do
    PLIST_FILE="$LAUNCHD_DIR/$service.plist"
    if [ -f "$PLIST_FILE" ]; then
        echo "  - Removing $PLIST_FILE..."
        rm -f "$PLIST_FILE"
        echo "    ✅ Removed"
    else
        echo "    ℹ️  $PLIST_FILE not found"
    fi
done
echo ""

# Step 3: Check and remove cron jobs
echo "Step 3: Checking for cron jobs..."
CRON_JOBS=$(crontab -l 2>/dev/null | grep -i "fantasy\|friday_morning_scraper\|monday_morning_scraper\|tuesday_morning_scraper" || true)

if [ -n "$CRON_JOBS" ]; then
    echo "  Found cron jobs. Removing..."
    crontab -l 2>/dev/null | grep -v -i "fantasy\|friday_morning_scraper\|monday_morning_scraper\|tuesday_morning_scraper" | crontab -
    echo "    ✅ Cron jobs removed"
else
    echo "    ℹ️  No fantasy-related cron jobs found"
fi
echo ""

# Step 4: Verify shutdown
echo "Step 4: Verifying shutdown..."
REMAINING=$(launchctl list 2>/dev/null | grep -i fantasy || true)
if [ -z "$REMAINING" ]; then
    echo "  ✅ No fantasy services are running"
else
    echo "  ⚠️  Warning: Some services may still be active:"
    echo "$REMAINING"
fi
echo ""

echo "=========================================="
echo "SHUTDOWN COMPLETE!"
echo "=========================================="
echo ""
echo "All weekly scrapers have been disabled."
echo ""
echo "To re-enable for next season, run:"
echo "  ./automation/setup_launchd.sh"
echo ""


#!/bin/bash
# Force kill any running scraper processes

echo "=========================================="
echo "KILLING ALL SCRAPER PROCESSES"
echo "=========================================="
echo ""

PROJECT_DIR="/Users/mightenyip/Documents/GitHub/yfd-py-test"

# Find and kill Python processes running scraper scripts
echo "Step 1: Killing Python scraper processes..."
SCRAPER_PIDS=$(ps aux | grep -E "python.*scrapers/|python.*automated_yahoo|python.*cbs_defense" | grep -v grep | awk '{print $2}')

if [ -n "$SCRAPER_PIDS" ]; then
    echo "  Found scraper PIDs: $SCRAPER_PIDS"
    for pid in $SCRAPER_PIDS; do
        echo "    Killing PID $pid..."
        kill -9 $pid 2>/dev/null && echo "      ✅ Killed" || echo "      ⚠️  Could not kill"
    done
else
    echo "  ℹ️  No Python scraper processes found"
fi
echo ""

# Kill Chrome/ChromeDriver processes that might be from Selenium
echo "Step 2: Checking for orphaned Chrome processes..."
CHROME_PIDS=$(ps aux | grep -i "chrome.*--headless\|chrome.*--remote-debugging\|chromedriver" | grep -v grep | awk '{print $2}')

if [ -n "$CHROME_PIDS" ]; then
    echo "  Found Chrome/ChromeDriver PIDs: $CHROME_PIDS"
    for pid in $CHROME_PIDS; do
        # Check if it's actually a scraper-related Chrome (be careful not to kill user's Chrome)
        CMD=$(ps -p $pid -o command= 2>/dev/null)
        if echo "$CMD" | grep -qE "headless|remote-debugging|chromedriver|--disable-gpu.*--no-sandbox"; then
            echo "    Killing scraper Chrome PID $pid..."
            kill -9 $pid 2>/dev/null && echo "      ✅ Killed" || echo "      ⚠️  Could not kill"
        fi
    done
else
    echo "  ℹ️  No scraper-related Chrome processes found"
fi
echo ""

# Kill any processes related to the automation scripts
echo "Step 3: Checking for automation script processes..."
AUTOMATION_PIDS=$(ps aux | grep -E "friday_morning_scraper|monday_morning_scraper|tuesday_morning_scraper" | grep -v grep | awk '{print $2}')

if [ -n "$AUTOMATION_PIDS" ]; then
    echo "  Found automation script PIDs: $AUTOMATION_PIDS"
    for pid in $AUTOMATION_PIDS; do
        echo "    Killing PID $pid..."
        kill -9 $pid 2>/dev/null && echo "      ✅ Killed" || echo "      ⚠️  Could not kill"
    done
else
    echo "  ℹ️  No automation script processes found"
fi
echo ""

# Final check
echo "Step 4: Final verification..."
REMAINING=$(ps aux | grep -E "python.*scrapers/|python.*automated_yahoo|python.*cbs_defense|friday_morning_scraper|monday_morning_scraper|tuesday_morning_scraper" | grep -v grep)

if [ -z "$REMAINING" ]; then
    echo "  ✅ No scraper processes are running"
else
    echo "  ⚠️  Warning: Some processes may still be running:"
    echo "$REMAINING"
fi
echo ""

echo "=========================================="
echo "COMPLETE!"
echo "=========================================="
echo ""
echo "If you see a browser window that's still open, you may need to:"
echo "  1. Close it manually"
echo "  2. Or check Activity Monitor for stuck processes"
echo ""


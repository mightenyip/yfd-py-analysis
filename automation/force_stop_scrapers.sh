#!/bin/bash
# Force stop all scraper processes - more aggressive approach

echo "=========================================="
echo "FORCE STOPPING ALL SCRAPER PROCESSES"
echo "=========================================="
echo ""

PROJECT_DIR="/Users/mightenyip/Documents/GitHub/yfd-py-test"

# Method 1: Kill by process name patterns
echo "Step 1: Killing processes by name pattern..."
pkill -9 -f "automated_yahoo_scraper" 2>/dev/null && echo "  ✅ Killed automated_yahoo_scraper processes" || echo "  ℹ️  No automated_yahoo_scraper processes"
pkill -9 -f "cbs_defense_scraper" 2>/dev/null && echo "  ✅ Killed cbs_defense_scraper processes" || echo "  ℹ️  No cbs_defense_scraper processes"
pkill -9 -f "friday_morning_scraper" 2>/dev/null && echo "  ✅ Killed friday_morning_scraper processes" || echo "  ℹ️  No friday_morning_scraper processes"
pkill -9 -f "monday_morning_scraper" 2>/dev/null && echo "  ✅ Killed monday_morning_scraper processes" || echo "  ℹ️  No monday_morning_scraper processes"
pkill -9 -f "tuesday_morning_scraper" 2>/dev/null && echo "  ✅ Killed tuesday_morning_scraper processes" || echo "  ℹ️  No tuesday_morning_scraper processes"
echo ""

# Method 2: Kill all Python processes in scrapers directory (BE CAREFUL)
echo "Step 2: Checking for Python processes running scraper scripts..."
SCRAPER_PYTHON_PIDS=$(ps aux | awk '/python.*\/scrapers\// && !/grep/ {print $2}')

if [ -n "$SCRAPER_PYTHON_PIDS" ]; then
    echo "  Found Python scraper PIDs: $SCRAPER_PYTHON_PIDS"
    for pid in $SCRAPER_PYTHON_PIDS; do
        CMD=$(ps -p $pid -o command= 2>/dev/null)
        echo "    Killing PID $pid: $CMD"
        kill -9 $pid 2>/dev/null && echo "      ✅ Killed" || echo "      ⚠️  Could not kill"
    done
else
    echo "  ℹ️  No Python processes running scraper scripts"
fi
echo ""

# Method 3: Kill orphaned Chrome/ChromeDriver processes (be selective)
echo "Step 3: Checking for headless Chrome processes..."
HEADLESS_CHROME=$(ps aux | grep -i "chrome.*--headless\|chrome.*--remote-debugging\|chromedriver" | grep -v grep)

if [ -n "$HEADLESS_CHROME" ]; then
    echo "  ⚠️  Found potentially scraper-related Chrome processes:"
    echo "$HEADLESS_CHROME" | while read line; do
        PID=$(echo "$line" | awk '{print $2}')
        CMD=$(echo "$line" | awk '{for(i=11;i<=NF;i++) printf "%s ", $i; print ""}')
        echo "    PID $PID: $CMD"
        # Only kill if it's clearly a scraper process
        if echo "$CMD" | grep -qE "headless|remote-debugging|chromedriver|--disable-gpu.*--no-sandbox"; then
            echo "      Killing..."
            kill -9 $PID 2>/dev/null && echo "        ✅ Killed" || echo "        ⚠️  Could not kill"
        else
            echo "      ⚠️  Skipping (might be user's Chrome)"
        fi
    done
else
    echo "  ℹ️  No headless Chrome processes found"
fi
echo ""

# Method 4: Check for any processes with PROJECT_DIR in their command
echo "Step 4: Checking for processes in project directory..."
PROJECT_PIDS=$(ps aux | grep "$PROJECT_DIR" | grep -v grep | awk '{print $2}')

if [ -n "$PROJECT_PIDS" ]; then
    echo "  Found processes in project directory:"
    for pid in $PROJECT_PIDS; do
        CMD=$(ps -p $pid -o command= 2>/dev/null | head -c 100)
        echo "    PID $pid: $CMD..."
        # Ask user if they want to kill these
        echo "      ℹ️  Review this process - if it's a scraper, kill it manually"
    done
else
    echo "  ℹ️  No processes found in project directory"
fi
echo ""

# Final status check
echo "Step 5: Final status check..."
echo ""
echo "Checking for any remaining scraper-related processes:"
ps aux | grep -E "scrapers/|automated_yahoo|cbs_defense|friday_morning|monday_morning|tuesday_morning" | grep -v grep || echo "  ✅ No scraper processes found!"

echo ""
echo "=========================================="
echo "COMPLETE!"
echo "=========================================="
echo ""
echo "If you're still seeing activity:"
echo "  1. Check Activity Monitor for Python or Chrome processes"
echo "  2. Close any open Chrome browser windows manually"
echo "  3. Run: ps aux | grep python | grep -i scraper"
echo "  4. If you see a specific PID, kill it with: kill -9 <PID>"
echo ""


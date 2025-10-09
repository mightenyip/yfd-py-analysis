#!/bin/bash
# Monday Morning Scraper - Runs after Sunday games
# Schedule: Every Monday at 8:00 AM
# Cron: 0 8 * * 1 /Users/mightenyip/Documents/GitHub/yfd-py-test/automation/monday_morning_scraper.sh

PROJECT_DIR="/Users/mightenyip/Documents/GitHub/yfd-py-test"
LOG_DIR="$PROJECT_DIR/logs"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Create log directory if it doesn't exist
mkdir -p "$LOG_DIR"

LOG_FILE="$LOG_DIR/monday_scraper_$TIMESTAMP.log"

echo "========================================" | tee -a "$LOG_FILE"
echo "MONDAY MORNING SCRAPER" | tee -a "$LOG_FILE"
echo "Started: $(date)" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"

# Navigate to project directory
cd "$PROJECT_DIR" || exit 1

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Determine current week
CURRENT_WEEK=$(python3 -c "from datetime import datetime, timedelta; start = datetime(2025, 9, 4); print((datetime.now() - start).days // 7 + 1)")

echo "Current Week: $CURRENT_WEEK" | tee -a "$LOG_FILE"

# 1. Scrape Yahoo Sunday game data
echo "" | tee -a "$LOG_FILE"
echo "Step 1: Scraping Yahoo Sunday data..." | tee -a "$LOG_FILE"
python3 scrapers/automated_yahoo_scraper.py --week "$CURRENT_WEEK" --day Sunday --headless 2>&1 | tee -a "$LOG_FILE"

if [ $? -eq 0 ]; then
    echo "✅ Yahoo scraping successful" | tee -a "$LOG_FILE"
else
    echo "❌ Yahoo scraping failed" | tee -a "$LOG_FILE"
fi

# 2. Generate report for Sunday games
echo "" | tee -a "$LOG_FILE"
echo "Step 2: Generating Sunday report..." | tee -a "$LOG_FILE"
python3 reports/weekly_report_generator.py --week "$CURRENT_WEEK" --mode completed --day Sunday 2>&1 | tee -a "$LOG_FILE"

if [ $? -eq 0 ]; then
    echo "✅ Report generation successful" | tee -a "$LOG_FILE"
else
    echo "❌ Report generation failed" | tee -a "$LOG_FILE"
fi

# 3. Commit and push to git (optional)
echo "" | tee -a "$LOG_FILE"
echo "Step 3: Committing to git..." | tee -a "$LOG_FILE"
git add -A
git commit -m "Automated Monday scrape: Week $CURRENT_WEEK Sunday data - $(date +%Y-%m-%d)" 2>&1 | tee -a "$LOG_FILE"
git push origin main 2>&1 | tee -a "$LOG_FILE"

echo "" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
echo "MONDAY SCRAPER COMPLETED" | tee -a "$LOG_FILE"
echo "Finished: $(date)" | tee -a "$LOG_FILE"
echo "Log saved to: $LOG_FILE" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"

# Send notification
osascript -e 'display notification "Monday scraping complete!" with title "Fantasy Football Automation"' 2>/dev/null


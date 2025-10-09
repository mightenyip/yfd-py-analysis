#!/bin/bash
# Quick Setup Script for Fantasy Football Automation

PROJECT_DIR="/Users/mightenyip/Documents/GitHub/yfd-py-test"

echo "=========================================="
echo "FANTASY FOOTBALL AUTOMATION SETUP"
echo "=========================================="
echo ""

# Navigate to project directory
cd "$PROJECT_DIR" || exit 1

# 1. Make scripts executable
echo "Step 1: Making scripts executable..."
chmod +x automation/friday_morning_scraper.sh
chmod +x automation/monday_morning_scraper.sh
chmod +x automation/tuesday_morning_scraper.sh
echo "✅ Scripts are now executable"
echo ""

# 2. Create logs directory
echo "Step 2: Creating logs directory..."
mkdir -p logs
echo "✅ Logs directory created"
echo ""

# 3. Create reports directory
echo "Step 3: Creating reports directory..."
mkdir -p reports
echo "✅ Reports directory created"
echo ""

# 4. Test Python dependencies
echo "Step 4: Checking Python dependencies..."
python3 -c "import selenium, pandas, beautifulsoup4, requests" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Python dependencies installed"
else
    echo "⚠️  Missing Python dependencies. Installing..."
    pip3 install selenium pandas beautifulsoup4 requests matplotlib seaborn numpy
fi
echo ""

# 5. Test ChromeDriver
echo "Step 5: Checking ChromeDriver..."
which chromedriver >/dev/null
if [ $? -eq 0 ]; then
    echo "✅ ChromeDriver found: $(which chromedriver)"
else
    echo "⚠️  ChromeDriver not found. Installing via Homebrew..."
    brew install chromedriver
fi
echo ""

# 6. Run test scrape
echo "Step 6: Running test scrape..."
echo "This will scrape CBS defensive rankings as a test..."
python3 scrapers/cbs_defense_scraper_fixed.py >/dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Test scrape successful"
else
    echo "⚠️  Test scrape failed. Check manually."
fi
echo ""

# 7. Display cron setup instructions
echo "=========================================="
echo "CRON SETUP INSTRUCTIONS"
echo "=========================================="
echo ""
echo "To enable automatic scraping, run:"
echo ""
echo "  crontab -e"
echo ""
echo "Then add these lines:"
echo ""
echo "# Fantasy Football Automation"
echo "0 8 * * 5 $PROJECT_DIR/automation/friday_morning_scraper.sh"
echo "0 8 * * 1 $PROJECT_DIR/automation/monday_morning_scraper.sh"
echo "0 8 * * 2 $PROJECT_DIR/automation/tuesday_morning_scraper.sh"
echo ""
echo "This will run:"
echo "  - Friday 8:00 AM: Thursday game scraping"
echo "  - Monday 8:00 AM: Sunday games scraping"
echo "  - Tuesday 8:00 AM: Monday game scraping + full report"
echo ""
echo "=========================================="
echo "MANUAL TESTING"
echo "=========================================="
echo ""
echo "Test the automation scripts manually:"
echo ""
echo "  ./automation/friday_morning_scraper.sh"
echo "  ./automation/monday_morning_scraper.sh"
echo "  ./automation/tuesday_morning_scraper.sh"
echo ""
echo "Check logs in: $PROJECT_DIR/logs/"
echo ""
echo "=========================================="
echo "SETUP COMPLETE!"
echo "=========================================="
echo ""
echo "📖 Read the full documentation:"
echo "   $PROJECT_DIR/automation/AUTOMATION_SETUP.md"
echo ""


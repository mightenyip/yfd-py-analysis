# Fantasy Football Automation Setup

## Overview

This automation system automatically scrapes Yahoo Daily Fantasy data and CBS Sports defensive rankings on a weekly schedule:

- **Friday 8:00 AM**: Scrape Thursday Night Football data
- **Monday 8:00 AM**: Scrape Sunday games data
- **Tuesday 8:00 AM**: Scrape Monday Night Football data + generate full weekly report

## Components

### 1. Automated Yahoo Scraper (`scrapers/automated_yahoo_scraper.py`)
- Generic scraper for any game day (Thursday/Sunday/Monday)
- Auto-detects current week based on season start date
- Can be run manually or via cron

### 2. CBS Defense Scraper (`scrapers/cbs_defense_scraper_fixed.py`)
- Scrapes defensive rankings vs QB, RB, WR, TE
- Provides matchup analysis capabilities
- Updates weekly with latest data

### 3. Weekly Report Generator (`reports/weekly_report_generator.py`)
- Combines Yahoo data with CBS defensive rankings
- Analyzes completed games
- Generates matchup recommendations for upcoming games

### 4. Automation Scripts
- `friday_morning_scraper.sh` - Thursday games
- `monday_morning_scraper.sh` - Sunday games
- `tuesday_morning_scraper.sh` - Monday games + full report

## Installation

### 1. Make Scripts Executable

```bash
cd /Users/mightenyip/Documents/GitHub/yfd-py-test/automation
chmod +x friday_morning_scraper.sh
chmod +x monday_morning_scraper.sh
chmod +x tuesday_morning_scraper.sh
```

### 2. Test Scripts Manually

```bash
# Test Friday scraper
./friday_morning_scraper.sh

# Test Monday scraper
./monday_morning_scraper.sh

# Test Tuesday scraper
./tuesday_morning_scraper.sh
```

### 3. Set Up Cron Jobs

Open crontab:
```bash
crontab -e
```

Add these lines:

```cron
# Fantasy Football Automation
# Runs every Friday at 8:00 AM (after Thursday Night Football)
0 8 * * 5 /Users/mightenyip/Documents/GitHub/yfd-py-test/automation/friday_morning_scraper.sh

# Runs every Monday at 8:00 AM (after Sunday games)
0 8 * * 1 /Users/mightenyip/Documents/GitHub/yfd-py-test/automation/monday_morning_scraper.sh

# Runs every Tuesday at 8:00 AM (after Monday Night Football)
0 8 * * 2 /Users/mightenyip/Documents/GitHub/yfd-py-test/automation/tuesday_morning_scraper.sh
```

Save and exit (`:wq` in vim).

### 4. Verify Cron Jobs

```bash
crontab -l
```

## Manual Usage

### Run Scrapers Manually

```bash
# Scrape Yahoo data for specific week/day
python3 scrapers/automated_yahoo_scraper.py --week 6 --day Thursday

# Scrape CBS defensive rankings
python3 scrapers/cbs_defense_scraper_fixed.py

# Analyze specific matchup
python3 scrapers/cbs_defense_scraper_fixed.py --matchup Eagles Giants
```

### Generate Reports Manually

```bash
# Analyze completed games
python3 reports/weekly_report_generator.py --week 6 --mode completed --day Thursday

# Generate upcoming week recommendations
python3 reports/weekly_report_generator.py --week 7 --mode upcoming --matchups Eagles-Giants Cowboys-49ers

# Full weekly report
python3 reports/weekly_report_generator.py --week 6 --mode full
```

## Output Files

### Data Files (in `data_csv/`)
- `week{N}_Thur.csv` - Thursday game data
- `week{N}_Sun.csv` - Sunday games data
- `week{N}_Mon.csv` - Monday game data
- `cbs_defense_vs_{position}.csv` - Defensive rankings for each position
- `week{N}_matchup_recommendations.csv` - Matchup analysis
- `matchup_{TEAM1}_vs_{TEAM2}.csv` - Specific matchup details

### Log Files (in `logs/`)
- `friday_scraper_YYYYMMDD_HHMMSS.log`
- `monday_scraper_YYYYMMDD_HHMMSS.log`
- `tuesday_scraper_YYYYMMDD_HHMMSS.log`

## Troubleshooting

### Cron Jobs Not Running

1. Check cron is enabled:
```bash
# On macOS
sudo launchctl list | grep cron
```

2. Grant Full Disk Access to `cron` (macOS):
   - System Preferences → Security & Privacy → Privacy
   - Full Disk Access → Add `/usr/sbin/cron`

3. Check logs:
```bash
tail -f /var/log/system.log | grep cron
```

### ChromeDriver Issues

If scraping fails due to ChromeDriver:
```bash
# Install/update ChromeDriver
brew install chromedriver

# Or update if already installed
brew upgrade chromedriver

# Allow ChromeDriver to run (macOS)
xattr -d com.apple.quarantine $(which chromedriver)
```

### Python Dependencies

Ensure all dependencies are installed:
```bash
pip3 install selenium beautifulsoup4 pandas numpy matplotlib seaborn requests
```

## Customization

### Change Schedule Times

Edit cron times:
- `0 8 * * 5` = Friday 8:00 AM
- `0 10 * * 1` = Monday 10:00 AM (example change)
- Format: `minute hour day month weekday`

### Change Season Start Date

Edit `automated_yahoo_scraper.py`:
```python
season_start = datetime(2025, 9, 4)  # Adjust year/date
```

### Disable Auto-Commit to Git

Comment out git commands in automation scripts:
```bash
# git add -A
# git commit -m "..."
# git push origin main
```

## Notifications

macOS notifications are enabled by default. To disable, remove this line from scripts:
```bash
osascript -e 'display notification "..." with title "..."' 2>/dev/null
```

To add email notifications, add to scripts:
```bash
echo "Subject: Fantasy Scraping Complete" | sendmail your@email.com
```

## Advanced Features

### Add Custom Matchup Analysis

```python
# In your own script
from reports.weekly_report_generator import WeeklyReportGenerator

gen = WeeklyReportGenerator()
gen.load_defensive_rankings()
gen.analyze_upcoming_week(7, [('Eagles', 'Giants'), ('Cowboys', '49ers')])
```

### Filter Data by Criteria

```python
import pandas as pd

# Load data
df = pd.read_csv('data_csv/week6_Sun.csv')

# Filter active players with high value
high_value = df[(df['points'] > 15) & (df['salary'] < 20)]
```

## Shutting Down for Off-Season

To disable all automated scrapers until the next season:

```bash
cd /Users/mightenyip/Documents/GitHub/yfd-py-test/automation
./shutdown_scrapers.sh
```

This will:
- Unload all launchd services
- Remove plist files from LaunchAgents
- Remove any cron jobs
- Verify everything is shut down

## Re-Enabling for Next Season

When the next season starts, re-enable the scrapers:

```bash
cd /Users/mightenyip/Documents/GitHub/yfd-py-test/automation
./reenable_scrapers.sh
```

Or use the original setup script:

```bash
./setup_launchd.sh
```

## Support

For issues or questions:
1. Check logs in `logs/` directory
2. Run scripts manually with `--visible` flag to see browser
3. Verify data is being saved to `data_csv/`

## Future Enhancements

Potential additions:
- Email/SMS alerts for scraping completion
- Slack/Discord integration for reports
- Machine learning predictions based on historical data
- Real-time odds integration
- Player injury status tracking


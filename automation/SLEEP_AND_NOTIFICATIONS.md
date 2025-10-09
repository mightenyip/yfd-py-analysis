# 💤 Laptop Sleep & Notifications Guide

## ⚠️ The Sleep Problem

**Critical Issue:** If your laptop is asleep, cron jobs and automation **WILL NOT RUN**. ❌

macOS suspends all background processes when sleeping. This means:
- Friday 8 AM scraper won't run if laptop is asleep
- Monday 8 AM scraper won't run if laptop is asleep  
- Tuesday 8 AM scraper won't run if laptop is asleep

---

## ✅ Solutions (Choose One)

### **Option 1: Keep Laptop Awake (Easiest)**

#### Method A: Change System Settings

**System Settings → Battery → Power Adapter**
1. Set "Turn display off after" to your preference (10-15 min)
2. Uncheck "Put hard disks to sleep when possible"
3. Set "Prevent automatic sleeping when the display is off"

**Or use Terminal:**
```bash
# Disable sleep while plugged in
sudo pmset -c sleep 0

# Check current settings
pmset -g

# Restore default sleep (90 min)
sudo pmset -c sleep 90
```

**Pros:**
- ✅ Simple, one-time setup
- ✅ Works perfectly for automation
- ✅ No additional software needed

**Cons:**
- ❌ Uses more power
- ❌ Laptop must stay plugged in
- ❌ Not portable-friendly

---

### **Option 2: Use launchd Instead of Cron (Better for Mac)**

launchd is macOS's native scheduler and integrates better with the system.

**Setup:**
```bash
cd /Users/mightenyip/Documents/GitHub/yfd-py-test
./automation/setup_launchd.sh
```

This installs launchd agents that:
- ✅ Are more reliable than cron
- ✅ Better logging
- ✅ System-integrated
- ⚠️ Still requires computer to be awake (or use with Option 1)

**Check if running:**
```bash
launchctl list | grep fantasy
```

**Disable if needed:**
```bash
launchctl unload ~/Library/LaunchAgents/com.fantasy.*.plist
```

---

### **Option 3: Use `caffeinate` to Prevent Sleep During Scraping**

Modify your scraper scripts to prevent sleep during execution:

**Edit each automation script** (`friday_morning_scraper.sh`, etc.):

```bash
#!/bin/bash

# Add this near the top (after LOG_FILE setup)
echo "Preventing sleep during scraping..." | tee -a "$LOG_FILE"
caffeinate -s &
CAFFEINATE_PID=$!

# ... rest of your script ...

# Add this at the very end (before final echo)
kill $CAFFEINATE_PID 2>/dev/null
echo "Sleep prevention ended" | tee -a "$LOG_FILE"
```

**Pros:**
- ✅ Only prevents sleep during scraping (~5-10 min)
- ✅ Laptop can sleep rest of the time
- ✅ Good compromise

**Cons:**
- ❌ Requires computer to be awake when script starts
- ❌ Won't wake computer from sleep

---

### **Option 4: Run on Schedule While You're Awake**

Change the schedule to times when you're at your computer:

**Edit crontab:**
```bash
crontab -e
```

Change times:
```cron
# Friday 6:00 PM (when you're home)
0 18 * * 5 /path/to/friday_morning_scraper.sh

# Monday 6:00 PM  
0 18 * * 1 /path/to/monday_morning_scraper.sh

# Tuesday 6:00 PM
0 18 * * 2 /path/to/tuesday_morning_scraper.sh
```

**Pros:**
- ✅ No sleep issues
- ✅ Can watch it run
- ✅ Easier to debug

**Cons:**
- ❌ Must remember to be at computer
- ❌ Less "set it and forget it"

---

### **Option 5: Cloud Server (Most Reliable)**

Run automation on a cloud server that never sleeps.

#### A. **AWS EC2 Free Tier**

```bash
# On AWS EC2 instance
sudo apt update
sudo apt install python3-pip chromium-browser chromium-chromedriver
pip3 install selenium pandas beautifulsoup4 requests

# Clone your repo
git clone https://github.com/mightenyip/yfd-py-analysis.git
cd yfd-py-analysis

# Set up cron
crontab -e
# Add your cron jobs
```

#### B. **Raspberry Pi at Home**

Buy a $35 Raspberry Pi, keep it plugged in 24/7, runs your automation.

#### C. **GitHub Actions (Free!)**

Create `.github/workflows/scraper.yml`:

```yaml
name: Fantasy Scraper

on:
  schedule:
    - cron: '0 15 * * 5'  # Friday 8 AM PST = 15:00 UTC
    - cron: '0 15 * * 1'  # Monday 8 AM PST
    - cron: '0 15 * * 2'  # Tuesday 8 AM PST

jobs:
  scrape:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install selenium pandas beautifulsoup4 requests
      - run: sudo apt-get install chromium-chromedriver
      - run: python3 scrapers/automated_yahoo_scraper.py --headless
      - run: |
          git config user.name github-actions
          git config user.email github-actions@github.com
          git add .
          git commit -m "Automated scrape"
          git push
```

**Pros:**
- ✅ Runs 24/7 regardless of your laptop
- ✅ Most reliable
- ✅ Can run from anywhere
- ✅ GitHub Actions is FREE

**Cons:**
- ❌ More setup complexity
- ❌ Costs money (except GitHub Actions)

---

## 🔔 How You'll Know When Scraping Completes

### **1. Desktop Notifications (Built-in)**

Your scripts already include macOS notifications:

```bash
osascript -e 'display notification "Friday scraping complete!" with title "Fantasy Football Automation"'
```

**Appears as:**
```
┌────────────────────────────────────┐
│ Fantasy Football Automation        │
│ Friday scraping complete!          │
└────────────────────────────────────┘
```

⚠️ **Only shows if you're logged in and awake!**

---

### **2. Check Log Files**

Every run creates a log:

```bash
# View latest logs
ls -lt logs/ | head -5

# Check Friday log
tail logs/friday_scraper_*.log

# Look for completion message
grep "COMPLETED" logs/friday_scraper_*.log
```

**Log shows:**
```
========================================
FRIDAY SCRAPER COMPLETED
Finished: 2025-10-10 08:05:23
========================================
```

---

### **3. Git Commits**

Check GitHub for new commits:

```bash
# Check last commit
git log -1 --oneline

# Check remote
git fetch
git log origin/main -1
```

Each successful run commits:
```
"Automated Friday scrape: Week 6 Thursday data - 2025-10-10"
```

---

### **4. Check Data Files**

New CSV appears:

```bash
# List recent CSV files
ls -lt data_csv/week*.csv | head -5

# Check if today's file exists
ls data_csv/week6_Thurs.csv

# See when it was created
stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" data_csv/week6_Thurs.csv
```

---

### **5. Email Notifications (Optional)**

Add to your automation scripts:

```bash
# At the end of each scraper script
if [ $? -eq 0 ]; then
    echo "Subject: ✅ Fantasy Scraping Complete - Week $CURRENT_WEEK
    
Scraping completed successfully!
Check: https://github.com/mightenyip/yfd-py-analysis

Log: $LOG_FILE" | sendmail your@email.com
fi
```

Requires `sendmail` to be configured on your Mac.

---

### **6. SMS Notifications (Optional)**

Use Twilio or similar service:

```bash
# Install twilio
pip3 install twilio

# Add to Python script
from twilio.rest import Client
client = Client('your_account_sid', 'your_auth_token')
message = client.messages.create(
    body='Fantasy scraping complete!',
    from_='+1234567890',
    to='+0987654321'
)
```

---

### **7. Slack/Discord Webhook (Optional)**

```bash
# At end of script
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"✅ Fantasy scraping complete!"}' \
  YOUR_WEBHOOK_URL
```

---

## 🎯 Recommended Setup

### **For Most Users:**

1. **Keep laptop plugged in** on Friday/Monday/Tuesday mornings
2. **Disable sleep while plugged in:**
   ```bash
   sudo pmset -c sleep 0
   ```
3. **Use launchd** instead of cron:
   ```bash
   ./automation/setup_launchd.sh
   ```
4. **Check logs** later to verify:
   ```bash
   tail logs/friday_scraper_*.log
   ```

### **For "Set and Forget" Users:**

1. **Use GitHub Actions** (see Option 5)
2. Runs in cloud, never depends on your laptop
3. Completely automated
4. Free!

---

## 🧪 Test Your Setup

### Test if scraping works while laptop is awake:

```bash
# Run manually
./automation/friday_morning_scraper.sh

# Watch it complete
# Should see:
# - Desktop notification
# - New log file
# - New CSV file
# - Git commit
```

### Test sleep behavior:

```bash
# Schedule a test for 2 minutes from now
# If it's 3:45 PM, set for 3:47 PM
crontab -e

# Add temporary test
47 15 * * * /path/to/friday_morning_scraper.sh

# Put laptop to sleep immediately
# Wait 2 minutes
# Wake up laptop
# Check if script ran (it won't have)
```

---

## 📋 Quick Checklist

Before relying on automation:

- [ ] Scripts are executable (`chmod +x`)
- [ ] Cron or launchd is configured
- [ ] Sleep settings adjusted (if using laptop)
- [ ] Tested manually to verify it works
- [ ] Logs directory exists
- [ ] Git is configured (for auto-commits)
- [ ] ChromeDriver is installed
- [ ] Python dependencies installed
- [ ] Know how to check logs
- [ ] Tested notification system

---

## 🔍 Troubleshooting

### **Script didn't run?**

1. Check if laptop was asleep:
   ```bash
   pmset -g log | grep -i sleep
   ```

2. Check if cron/launchd triggered:
   ```bash
   # For cron
   grep CRON /var/log/system.log
   
   # For launchd
   launchctl list | grep fantasy
   ```

3. Check logs:
   ```bash
   ls -lt logs/ | head -5
   ```

### **No notification appeared?**

- Notifications only show if you're logged in
- Check System Settings → Notifications
- Enable "Script Editor" or "osascript" notifications

### **Data wasn't scraped?**

- Check if Yahoo site changed
- Run manually with `--visible` to debug
- Check error logs

---

## 💡 Pro Tips

1. **Set a reminder** on your phone for 8:10 AM Friday to check if scraping completed
2. **Enable GitHub mobile notifications** to see when commits happen
3. **Use a second old laptop** if you have one, keep it plugged in for automation
4. **Raspberry Pi** is $35 and perfect for this
5. **GitHub Actions** is free and reliable

---

## 🎯 Bottom Line

### The Reality:

**Cron + Sleeping Laptop = Won't Work** ❌

### The Solutions:

1. **Easy:** Keep laptop awake & plugged in on scraping days
2. **Better:** Use launchd + keep laptop awake  
3. **Best:** Use GitHub Actions or cloud server

Choose what works for your lifestyle!

---

## 📞 Need Help?

- Check logs: `logs/`
- Test manually first
- Use visible mode to debug
- See full guide: `AUTOMATION_SETUP.md`


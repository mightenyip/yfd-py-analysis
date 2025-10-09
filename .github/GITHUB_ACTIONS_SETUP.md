# 🚀 GitHub Actions Setup Guide

## ✅ What I Just Created

Three automated workflows that run in GitHub's cloud:

- **Friday 8:00 AM PST** → Scrape Thursday games
- **Monday 8:00 AM PST** → Scrape Sunday games  
- **Tuesday 8:00 AM PST** → Scrape Monday games + full report

## 🎯 Why This is Perfect

✅ **Runs in the cloud** - No dependency on your laptop  
✅ **FREE** - 2,000 minutes/month free (you'll use ~30 min/month)  
✅ **Never sleeps** - Always runs on schedule  
✅ **Zero maintenance** - Set it and forget it  
✅ **Works anywhere** - Laptop can be off, dead, anywhere  

---

## 📋 Setup Steps (5 Minutes)

### Step 1: Commit and Push the Workflows

```bash
cd /Users/mightenyip/Documents/GitHub/yfd-py-test

# Add the workflow files
git add .github/

# Commit
git commit -m "Add GitHub Actions automation workflows"

# Push to GitHub
git push origin main
```

### Step 2: Enable GitHub Actions (if not already enabled)

1. Go to your GitHub repo: `https://github.com/mightenyip/yfd-py-analysis`
2. Click **"Actions"** tab at the top
3. If prompted, click **"I understand my workflows, go ahead and enable them"**

### Step 3: Verify Workflows are There

On the **Actions** tab, you should see:

```
All workflows
├── Friday Morning Scraper (Thursday Games)
├── Monday Morning Scraper (Sunday Games)  
└── Tuesday Morning Scraper (Monday Games + Full Report)
```

### Step 4: Test Manually (Optional but Recommended)

Don't wait until Friday! Test now:

1. Go to **Actions** tab
2. Click **"Friday Morning Scraper"** on the left
3. Click **"Run workflow"** dropdown (top right)
4. Click green **"Run workflow"** button
5. Watch it run in real-time! 🎉

---

## 🎮 How to Use

### Automatic Mode (Set and Forget)

**Do nothing!** The workflows run automatically:

- Every Friday at 8:00 AM PST
- Every Monday at 8:00 AM PST
- Every Tuesday at 8:00 AM PST

### Manual Mode (Run Anytime)

1. Go to GitHub repo → **Actions** tab
2. Select the workflow (Friday/Monday/Tuesday)
3. Click **"Run workflow"**
4. Click the green button

---

## 🔍 How to Check Results

### Method 1: Check Commits

New commits appear automatically:

```
🤖 Automated Friday scrape: Week 6 Thursday data - 2025-10-10
🤖 Automated Monday scrape: Week 6 Sunday data - 2025-10-13
🤖 Automated Tuesday scrape: Week 6 Monday data + full report - 2025-10-14
```

### Method 2: Check Actions Tab

1. Go to **Actions** tab
2. See all runs with ✅ (success) or ❌ (failed)
3. Click any run to see detailed logs
4. Download logs if needed

### Method 3: Check Data Files

Pull latest changes:

```bash
git pull origin main
ls -lt data_csv/week*.csv
```

### Method 4: GitHub Mobile App

Install GitHub mobile app → Get notifications when actions complete!

---

## 📅 Schedule Details

### Current Schedule (All Times in PST)

| Day | Time | UTC Time | What It Does |
|-----|------|----------|--------------|
| Friday | 8:00 AM | 16:00 | Scrape Thursday games + update CBS rankings |
| Monday | 8:00 AM | 16:00 | Scrape Sunday games |
| Tuesday | 8:00 AM | 16:00 | Scrape Monday games + generate weekly report |

### Want to Change the Schedule?

Edit the cron expression in the workflow files:

```yaml
on:
  schedule:
    - cron: '0 16 * * 5'  # Friday 8 AM PST = 16:00 UTC
    #        │  │  │ │ │
    #        │  │  │ │ └─── Day of week (0-6, Sunday=0)
    #        │  │  │ └───── Month (1-12)
    #        │  │  └─────── Day of month (1-31)
    #        │  └────────── Hour (0-23, UTC time)
    #        └───────────── Minute (0-59)
```

**Examples:**
- `0 17 * * 5` = Friday 9:00 AM PST (5 PM UTC)
- `0 20 * * 1` = Monday 12:00 PM PST (8 PM UTC)
- `30 16 * * 2` = Tuesday 8:30 AM PST (4:30 PM UTC)

**Time Zone Conversion:**
- PST (UTC-8): Add 8 hours to get UTC
- PDT (UTC-7): Add 7 hours to get UTC
- 8 AM PST = 16:00 UTC
- 8 AM PDT = 15:00 UTC

---

## 🎯 What Happens During Each Run

### Example: Friday Workflow

```
1. GitHub Actions server starts Ubuntu VM
2. Checks out your code
3. Installs Python 3.11
4. Installs dependencies (selenium, pandas, etc.)
5. Installs ChromeDriver
6. Runs Yahoo scraper in headless mode
7. Scrapes CBS defensive rankings
8. Commits new data files
9. Pushes to GitHub
10. Uploads logs as downloadable artifact
11. Shuts down VM
```

**Duration:** ~5-8 minutes per run

---

## 💰 Cost Analysis

### GitHub Actions Free Tier:

- **Public repos:** Unlimited minutes ✅
- **Private repos:** 2,000 minutes/month free

### Your Usage:

- ~7 minutes per run
- 3 runs per week = ~21 minutes/week
- ~84 minutes/month
- **Cost: $0** (well within free tier) 💰

Even if private repo, you'd use less than 5% of free quota!

---

## 🔧 Troubleshooting

### Workflow Didn't Run?

**Check GitHub Actions tab:**

1. Go to **Actions**
2. Look for runs with ❌
3. Click the run to see error logs

**Common issues:**

- **No runs showing:** Workflows not enabled (see Step 2)
- **Permission denied:** Check repo settings → Actions → Workflow permissions
- **Scraping failed:** Yahoo might have changed site structure

### How to Debug:

1. **Run workflow manually** (don't wait for schedule)
2. **Click into the failed step** to see exact error
3. **Download logs** (artifact at bottom of run page)
4. **Check if Yahoo site is accessible**

### Permission Issues:

If you see "permission denied" errors:

1. Go to repo **Settings** → **Actions** → **General**
2. Scroll to **Workflow permissions**
3. Select **"Read and write permissions"**
4. Check **"Allow GitHub Actions to create and approve pull requests"**
5. Click **Save**

---

## 🎨 Customization

### Add Email Notifications

Add this step to any workflow:

```yaml
- name: Send email notification
  uses: dawidd6/action-send-mail@v3
  with:
    server_address: smtp.gmail.com
    server_port: 465
    username: ${{secrets.MAIL_USERNAME}}
    password: ${{secrets.MAIL_PASSWORD}}
    subject: Fantasy Scraping Complete
    to: your@email.com
    from: GitHub Actions
    body: Scraping completed successfully!
```

(Requires setting up secrets in repo settings)

### Add Slack Notifications

```yaml
- name: Slack notification
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### Run More Frequently

Add additional schedule entries:

```yaml
on:
  schedule:
    - cron: '0 16 * * 5'  # Friday 8 AM
    - cron: '0 20 * * 5'  # Friday 12 PM (backup run)
```

---

## 📊 Monitoring

### View Run History

**Actions tab shows:**
- ✅ Successful runs (green checkmark)
- ❌ Failed runs (red X)
- ⏳ In-progress runs (yellow spinner)
- ⏱️ Duration of each run
- 📅 Timestamp of each run

### Download Logs

Each run uploads logs as artifacts:

1. Go to completed run
2. Scroll to bottom → **Artifacts** section
3. Download `friday-logs-XXX.zip`
4. Unzip and view logs

Logs retained for 30 days.

---

## 🚀 Advanced Features

### Conditional Runs

Only run if it's regular season:

```yaml
- name: Check if regular season
  run: |
    WEEK=$(python3 -c "from datetime import datetime; start = datetime(2025, 9, 4); print((datetime.now() - start).days // 7 + 1)")
    if [ $WEEK -lt 1 ] || [ $WEEK -gt 18 ]; then
      echo "Not regular season, skipping"
      exit 0
    fi
```

### Matrix Strategy

Run multiple weeks in parallel:

```yaml
strategy:
  matrix:
    week: [6, 7, 8]
steps:
  - name: Scrape week ${{ matrix.week }}
    run: python3 scraper.py --week ${{ matrix.week }}
```

### Retry on Failure

```yaml
- name: Scrape with retry
  uses: nick-invision/retry@v2
  with:
    timeout_minutes: 10
    max_attempts: 3
    command: python3 scrapers/automated_yahoo_scraper.py
```

---

## ✅ Verification Checklist

After setup, verify:

- [ ] Workflows appear in Actions tab
- [ ] Manual test run succeeds
- [ ] New commit appears after manual run
- [ ] Data files are updated
- [ ] Logs are downloadable
- [ ] Schedule is set correctly (PST vs UTC)
- [ ] Email notifications work (if configured)

---

## 🎯 Next Steps

1. **Commit and push** the workflow files (see Step 1)
2. **Test manually** (don't wait for Friday!)
3. **Check the results**
4. **Forget about it** - it runs automatically now! 🎉

---

## 🆚 GitHub Actions vs Cron

| Feature | GitHub Actions | Cron (Local) |
|---------|---------------|--------------|
| Runs when laptop off | ✅ Yes | ❌ No |
| Runs when laptop asleep | ✅ Yes | ❌ No |
| Free | ✅ Yes | ✅ Yes |
| Setup complexity | Easy | Medium |
| Logs | Beautiful UI | Text files |
| Notifications | Built-in | Manual |
| Reliability | 99.9%+ | Depends on laptop |
| Maintenance | None | Keep laptop on |

**Winner:** GitHub Actions 🏆

---

## 💡 Pro Tips

1. **Test workflows manually first** before relying on schedule
2. **Star your repo** to get notifications about actions
3. **Check Actions tab** every Friday to confirm it ran
4. **Download logs** if something seems wrong
5. **Use GitHub mobile app** for on-the-go monitoring

---

## 📞 Questions?

- **Workflow not running?** Check Actions tab for errors
- **Data not updating?** Pull latest changes: `git pull`
- **Want to change schedule?** Edit the cron expression
- **Need help?** Check the logs in Actions tab

---

## 🎉 You're All Set!

Once you push these workflows, you have a **production-grade, cloud-based, automated fantasy football analysis system**.

Your laptop can be off, in another state, doesn't matter. The scraping happens in the cloud every week. 

**This is the professional way to do it.** 🚀


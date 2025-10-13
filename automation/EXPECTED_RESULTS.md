# Expected Results for Automated Scrapers

## 📊 Monday Workflow (Sunday Games) - Expected Results

Based on successful Week 6 manual scraper results:

### Expected Output:
- **File**: `weekX_Sunday_all_games.csv`
- **Raw scraped data**: ~700-800 players (with duplicates)
- **After deduplication**: ~400 unique players

### Position Breakdown (Expected):
- **QB**: ~55-60 players
- **RB**: ~90-95 players  
- **WR**: ~135-140 players
- **TE**: ~80-85 players
- **DEF**: ~25-30 players

### Why Duplicates Occur:
- Same players appear in multiple game time slates
- Example: Patrick Mahomes appears in both:
  - "1:00 PM (10 NFL Games)"
  - "1:00 PM (7 NFL Games)"
- The comprehensive scraper captures ALL instances, then deduplication removes extras

### Success Criteria:
- ✅ **SUCCESS**: ≥600 players scraped (comprehensive data)
- ⚠️ **PARTIAL**: 300-599 players (some data, may need verification)
- ❌ **ISSUE**: <300 players (low count, may need manual scraping)

### Game Time Coverage Expected:
- 9:30 AM (London games): ~300-350 players
- 1:00 PM (Early slate): ~300-350 players
- 1:00 PM (Early slate 2): ~25-30 players
- 4:05 PM (Afternoon): ~25-30 players
- 8:20 PM (Sunday Night): ~25-30 players

## 📊 Friday Workflow (Thursday Games) - Expected Results

### Expected Output:
- **File**: `weekX_Thur.csv`
- **Players**: ~25-35 players (single game)
- **No duplicates expected** (single game time)

## 📊 Tuesday Workflow (Monday Games) - Expected Results

### Expected Output:
- **File**: `weekX_Mon.csv`
- **Players**: ~25-35 players (single game)
- **No duplicates expected** (single game time)

## 🔍 Verification Steps

### Check Monday Workflow Results:
1. Look for `weekX_Sunday_all_games.csv` file
2. Count total rows (subtract 1 for header)
3. Verify position breakdown matches expected ranges
4. Check for reasonable point distribution

### If Results Are Low:
1. Check GitHub Actions logs for errors
2. Verify ChromeDriver installation
3. Consider manual scraping as backup
4. Check if Yahoo page structure changed

## 📝 Notes

- Week 6 manual scraper captured 768 players → 407 unique after deduplication
- Enhanced scrolling is critical for comprehensive data capture
- Dropdown detection must work for multiple game times
- Manual backup scraper available in `scrapers/manual_week6_sunday_all_games.py`


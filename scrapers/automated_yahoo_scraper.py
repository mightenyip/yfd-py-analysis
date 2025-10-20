#!/usr/bin/env python3
"""
Automated Yahoo Daily Fantasy Scraper
Scrapes completed game data from Yahoo Daily Fantasy
Can be run for Thursday, Sunday, or Monday games
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd
import time
import os
import sys
from datetime import datetime, timedelta
import argparse

def get_current_week_and_day():
    """
    Determine current NFL week and day based on date.
    Returns (week_number, day_name)
    """
    now = datetime.now()
    
    # NFL Week 1 started Sept 5, 2024 (Thursday)
    # Adjust this date for your season
    season_start = datetime(2025, 9, 4)  # Adjust for 2025 season
    
    days_since_start = (now - season_start).days
    week_number = (days_since_start // 7) + 1
    
    # Determine day based on today's weekday
    weekday = now.strftime('%A')
    
    if weekday == 'Friday':
        return week_number, 'Thursday'
    elif weekday == 'Monday':
        return week_number, 'Sunday'
    elif weekday == 'Tuesday':
        return week_number, 'Monday'
    else:
        # Default to current weekday
        return week_number, weekday
    
def setup_driver(headless=True):
    """Set up Chrome driver with options."""
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    # Detect OS and set Chrome binary path for Linux/Ubuntu (GitHub Actions)
    import platform
    if platform.system() == 'Linux':
        # On Ubuntu/Linux, chromium-browser is typically installed
        chrome_options.binary_location = "/usr/bin/chromium-browser"
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        print(f"❌ Error setting up Chrome driver: {e}")
        print("Make sure you have ChromeDriver installed:")
        print("  brew install chromedriver  # On macOS")
        print("  sudo apt-get install chromium-browser chromium-chromedriver  # On Linux")
        return None

def extract_player_data(driver, week, day):
    """Extract player data with correct column mapping."""
    player_data = []
    
    try:
        # Wait for table to load
        wait = WebDriverWait(driver, 15)
        table = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table")))
        
        # Get all rows
        rows = table.find_elements(By.CSS_SELECTOR, "tr")
        print(f"✅ Found {len(rows)} total rows")
        
        # Process all rows (skip header row)
        print(f"🔄 Processing {len(rows)-1} player rows...")
        
        for i in range(1, len(rows)):
            try:
                row = rows[i]
                cells = row.find_elements(By.CSS_SELECTOR, "td, th")
                
                if len(cells) >= 6:  # Need at least 6 columns
                    # Column 0: Position
                    position = cells[0].text.strip() if len(cells) > 0 else ""
                    
                    # Column 2: Player name + game info + stats
                    player_info = cells[2].text.strip() if len(cells) > 2 else ""
                    
                    # Column 3: Salary
                    salary = cells[3].text.strip() if len(cells) > 3 else ""
                    
                    # Column 4: FPPG (season average)
                    fppg = cells[4].text.strip() if len(cells) > 4 else ""
                    
                    # Column 5: Points (actual points from game)
                    points = cells[5].text.strip() if len(cells) > 5 else ""
                    
                    # Parse player name from player_info
                    if player_info:
                        lines = player_info.split('\n')
                        player_name = lines[0].strip() if lines else "Unknown"
                        game_info = lines[1] if len(lines) > 1 else ""
                        stats = lines[2] if len(lines) > 2 else ""
                    else:
                        player_name = "Unknown"
                        game_info = ""
                        stats = ""
                    
                    # Only include if we have a valid player name
                    if player_name and player_name != "Unknown" and len(player_name) > 2:
                        row_data = {
                            'player_name': player_name,
                            'position': position,
                            'game_info': game_info,
                            'stats': stats,
                            'salary': salary,
                            'fppg': fppg,
                            'points': points,
                            'row_number': i,
                            'scrape_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'week': f'Week {week}',
                            'day': day
                        }
                        player_data.append(row_data)
                
                # Progress indicator
                if i % 100 == 0:
                    print(f"   Processed {i}/{len(rows)-1} rows...")
                    
            except Exception as e:
                print(f"⚠️  Error processing row {i}: {e}")
                continue
        
        print(f"✅ Successfully extracted {len(player_data)} players")
        return player_data
        
    except Exception as e:
        print(f"❌ Error extracting player data: {e}")
        return []

def scroll_to_load_more_data(driver):
    """Scroll down to load more data if needed."""
    try:
        print("🔄 Scrolling to load more data...")
        
        initial_rows = len(driver.find_elements(By.CSS_SELECTOR, "tr"))
        print(f"   Initial rows: {initial_rows}")
        
        # Scroll down multiple times
        for i in range(5):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            current_rows = len(driver.find_elements(By.CSS_SELECTOR, "tr"))
            if current_rows > initial_rows:
                print(f"   Found {current_rows - initial_rows} more rows after scroll {i+1}")
                initial_rows = current_rows
        
        # Scroll back to top
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
        
        final_rows = len(driver.find_elements(By.CSS_SELECTOR, "tr"))
        print(f"   Final row count: {final_rows}")
        
    except Exception as e:
        print(f"⚠️  Error during scrolling: {e}")

def scroll_to_load_all_data(driver):
    """Scroll aggressively to load ALL data on the page."""
    print("   📜 Scrolling to load ALL data...")
    
    try:
        # Get initial count
        initial_rows = len(driver.find_elements(By.CSS_SELECTOR, "tr"))
        print(f"   Initial rows: {initial_rows}")
        
        # Scroll down multiple times to load more data
        for i in range(10):  # Increased from 5 to 10
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            current_rows = len(driver.find_elements(By.CSS_SELECTOR, "tr"))
            print(f"   Scroll {i+1}: {current_rows} rows")
            
            # If no new rows loaded, try scrolling by smaller increments
            if current_rows == initial_rows:
                # Try scrolling by smaller amounts
                for j in range(5):
                    driver.execute_script("window.scrollBy(0, 500);")
                    time.sleep(1)
                    current_rows = len(driver.find_elements(By.CSS_SELECTOR, "tr"))
                    if current_rows > initial_rows:
                        print(f"   Found {current_rows - initial_rows} more rows after incremental scroll")
                        initial_rows = current_rows
                        break
                else:
                    # No more data to load
                    break
            else:
                initial_rows = current_rows
        
        # Scroll back to top
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)
        
        final_rows = len(driver.find_elements(By.CSS_SELECTOR, "tr"))
        print(f"   Final row count: {final_rows}")
        
    except Exception as e:
        print(f"   ⚠️  Error during scrolling: {e}")

def find_dropdown_options(driver):
    """Find and return all dropdown options for different game times/slates."""
    try:
        print("🔍 Looking for dropdown options for different game times...")
        
        # Common selectors for dropdowns
        dropdown_selectors = [
            "select",
            "select[name*='time']",
            "select[name*='game']", 
            "select[name*='slate']",
            ".dropdown select",
            "[data-testid*='select']",
            "[data-testid*='dropdown']",
            "select[class*='dropdown']"
        ]
        
        dropdown = None
        for selector in dropdown_selectors:
            try:
                dropdown = driver.find_element(By.CSS_SELECTOR, selector)
                if dropdown:
                    print(f"✅ Found dropdown with selector: {selector}")
                    break
            except NoSuchElementException:
                continue
        
        if not dropdown:
            print("❌ No dropdown found - will scrape current view only")
            return []
        
        # Get all options
        select = Select(dropdown)
        options = [option.text.strip() for option in select.options if option.text.strip()]
        
        print(f"📋 Found {len(options)} dropdown options:")
        for i, option in enumerate(options):
            print(f"   {i}: {option}")
        
        return options
        
    except Exception as e:
        print(f"❌ Error finding dropdown options: {e}")
        return []

def scrape_all_sunday_games(driver, week, day):
    """Scrape data from all Sunday game times/slates."""
    print(f"🏈 Scraping ALL {day} games for Week {week}...")
    
    all_player_data = []
    
    try:
        # First, try to find dropdown options
        dropdown_options = find_dropdown_options(driver)
        
        if dropdown_options:
            print(f"🎯 Found {len(dropdown_options)} different game times/slates")
            
            # Try each dropdown option
            for i, option_text in enumerate(dropdown_options):
                try:
                    print(f"\n🔄 Scraping option {i+1}/{len(dropdown_options)}: {option_text}")
                    
                    # Find dropdown again (it might have changed)
                    dropdown_selectors = [
                        "select",
                        "select[name*='time']",
                        "select[name*='game']", 
                        "select[name*='slate']",
                        ".dropdown select"
                    ]
                    
                    dropdown = None
                    for selector in dropdown_selectors:
                        try:
                            dropdown = driver.find_element(By.CSS_SELECTOR, selector)
                            if dropdown:
                                break
                        except NoSuchElementException:
                            continue
                    
                    if dropdown:
                        select = Select(dropdown)
                        select.select_by_visible_text(option_text)
                        time.sleep(5)  # Wait for page to update
                        
                        # Scroll to load ALL data for this option
                        scroll_to_load_all_data(driver)
                        
                        # Extract data for this option
                        option_data = extract_player_data(driver, week, day)
                        
                        if option_data:
                            print(f"✅ Found {len(option_data)} players for {option_text}")
                            all_player_data.extend(option_data)
                        else:
                            print(f"⚠️  No players found for {option_text}")
                    
                except Exception as e:
                    print(f"❌ Error scraping option '{option_text}': {e}")
                    continue
        else:
            print("⚠️  No dropdown found - scraping current view only")
            # Just scrape current view with enhanced scrolling
            scroll_to_load_all_data(driver)
            all_player_data = extract_player_data(driver, week, day)
        
        print(f"\n🎉 Total players found across all games: {len(all_player_data)}")
        return all_player_data
        
    except Exception as e:
        print(f"❌ Error in scrape_all_sunday_games: {e}")
        # Fallback to single scrape with enhanced scrolling
        scroll_to_load_all_data(driver)
        return extract_player_data(driver, week, day)

def scrape_yahoo_data(week, day, headless=True):
    """Main scraping function."""
    driver = setup_driver(headless=headless)
    if not driver:
        return []
    
    try:
        url = "https://sports.yahoo.com/dailyfantasy/research/completed"
        print(f"🌐 Loading {url}...")
        driver.get(url)
        
        # Wait for page to load
        time.sleep(10)
        
        # For Sunday games, try to scrape all game times/slates
        if day.lower() == "sunday":
            player_data = scrape_all_sunday_games(driver, week, day)
        else:
            # For Thursday/Monday, just scrape current view
            scroll_to_load_more_data(driver)
            player_data = extract_player_data(driver, week, day)
        
        return player_data
        
    except Exception as e:
        print(f"❌ Error during scraping: {e}")
        return []
    finally:
        driver.quit()

def save_data(player_data, week, day, data_dir="data_csv"):
    """Save scraped data to CSV."""
    if not player_data:
        print("❌ No data to save")
        return None
    
    # Create DataFrame
    df = pd.DataFrame(player_data)
    
    # Ensure directory exists
    os.makedirs(data_dir, exist_ok=True)
    
    # Generate filename
    day_short = day[:4] if day in ['Thursday', 'Sunday', 'Monday'] else day[:3]
    if day.lower() == "sunday":
        filename = f"week{week}_{day_short}_all_games.csv"
    else:
        filename = f"week{week}_{day_short}.csv"
    filepath = os.path.join(data_dir, filename)
    
    # Save to CSV
    df.to_csv(filepath, index=False)
    
    print(f"\n✅ Data saved to {filepath}")
    print(f"📊 Found {len(player_data)} valid players")
    
    # Display summary
    print(f"\n📋 Sample of data:")
    for i, (_, row) in enumerate(df.head(10).iterrows(), 1):
        points = row['points'] if pd.notna(row['points']) else 'N/A'
        salary = row['salary'] if pd.notna(row['salary']) else 'N/A'
        print(f"  {i:2d}. {row['player_name']:<25} | {row['position']:<3} | {salary:<6} | Points: {points:<6}")
    
    # Position breakdown
    position_counts = df['position'].value_counts()
    print(f"\n📊 Position breakdown:")
    for pos, count in position_counts.items():
        print(f"   {pos}: {count} players")
    
    # Active vs inactive players
    active = df[df['points'] != '0.0']
    inactive = df[df['points'] == '0.0']
    print(f"\n📊 Player Activity:")
    print(f"   Active (scored points): {len(active)}")
    print(f"   Inactive (0 points): {len(inactive)}")
    
    return df

def main():
    parser = argparse.ArgumentParser(description='Automated Yahoo Daily Fantasy Scraper')
    parser.add_argument('--week', type=int, help='NFL week number (default: auto-detect)')
    parser.add_argument('--day', type=str, choices=['Thursday', 'Sunday', 'Monday'], 
                        help='Day of games (default: auto-detect)')
    parser.add_argument('--headless', action='store_true', default=True,
                        help='Run browser in headless mode (default: True)')
    parser.add_argument('--visible', action='store_true',
                        help='Run browser in visible mode for debugging')
    
    args = parser.parse_args()
    
    # Auto-detect week and day if not provided
    if args.week is None or args.day is None:
        auto_week, auto_day = get_current_week_and_day()
        week = args.week if args.week else auto_week
        day = args.day if args.day else auto_day
    else:
        week = args.week
        day = args.day
    
    headless = not args.visible if args.visible else args.headless
    
    print("="*80)
    print("AUTOMATED YAHOO DAILY FANTASY SCRAPER")
    print("="*80)
    print(f"📅 Week: {week}")
    print(f"📆 Day: {day}")
    print(f"🖥️  Mode: {'Headless' if headless else 'Visible'}")
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # Scrape data
    player_data = scrape_yahoo_data(week, day, headless=headless)
    
    if player_data:
        # Save data
        df = save_data(player_data, week, day)
        
        if df is not None:
            print(f"\n🎉 SUCCESS! Scraped {len(df)} players for Week {week} {day}")
        else:
            print("\n❌ Failed to save data")
    else:
        print("\n❌ No data found")
    
    print(f"\n⏰ Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()


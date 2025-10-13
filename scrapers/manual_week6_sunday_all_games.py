#!/usr/bin/env python3
"""
Manual scraper for Yahoo Daily Fantasy Week 6 Sunday data from ALL game times.
This scraper detects and iterates through dropdown options to capture data from all available games.
Based on the working Week 5 scraper approach.
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
from datetime import datetime

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
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        print(f"Error setting up Chrome driver: {e}")
        print("Make sure you have ChromeDriver installed:")
        print("  brew install chromedriver  # On macOS")
        print("  Or download from: https://chromedriver.chromium.org/")
        return None

def find_dropdown_options(driver):
    """
    Find and return all dropdown options for game times.
    """
    try:
        print("🔍 Looking for dropdown options...")
        
        # Common selectors for dropdowns
        dropdown_selectors = [
            "select",
            "select[name*='time']",
            "select[name*='game']", 
            "select[name*='slate']",
            ".dropdown select",
            "[data-testid*='select']",
            "[data-testid*='dropdown']"
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
            print("❌ No dropdown found - will scrape current view")
            return []
        
        # Get all options
        select = Select(dropdown)
        options = []
        for option in select.options:
            if option.text.strip() and option.text.strip() != "Select a game time":
                options.append({
                    'text': option.text.strip(),
                    'value': option.get_attribute('value')
                })
        
        print(f"📋 Found {len(options)} dropdown options:")
        for i, option in enumerate(options):
            print(f"   {i}: {option['text']}")
        
        return options
        
    except Exception as e:
        print(f"❌ Error finding dropdown options: {e}")
        return []

def extract_player_data(driver, game_time=""):
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
                    
                    # Parse player name from player_info (first line)
                    lines = player_info.split('\n')
                    player_name = lines[0].strip() if lines else ""
                    
                    # Parse game info from player_info (second line)
                    game_info = lines[1].strip() if len(lines) > 1 else ""
                    
                    # Parse stats from player_info (third line)
                    stats = lines[2].strip() if len(lines) > 2 else ""
                    
                    # Include ALL players (including those with 0 points)
                    # This matches the Week 5 approach for comprehensive data
                    player_data.append({
                        'Player': player_name,
                        'Position': position,
                        'Game': game_info,
                        'Stats': stats,
                        'Salary': salary,
                        'FPPG': fppg,
                        'Points': points,
                        'GameTime': game_time,
                        'ScrapedAt': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'Week': '6',
                        'Day': 'Sunday'
                    })
                
            except Exception as e:
                print(f"⚠️  Error processing row {i}: {e}")
                continue
        
        print(f"✅ Extracted {len(player_data)} valid players for {game_time}")
        return player_data
        
    except Exception as e:
        print(f"❌ Error extracting player data: {e}")
        return []

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

def scrape_all_week6_sunday_games():
    """
    Main function to scrape Week 6 Sunday data from ALL game times.
    """
    driver = setup_driver(headless=False)  # Run with GUI to see dropdown interactions
    if not driver:
        return []
    
    all_player_data = []
    
    try:
        url = "https://sports.yahoo.com/dailyfantasy/research/completed"
        print(f"🌐 Loading {url}...")
        driver.get(url)
        
        # Wait for page to load
        time.sleep(5)
        
        # Find dropdown options
        dropdown_options = find_dropdown_options(driver)
        
        if dropdown_options:
            print(f"\n🎯 Found {len(dropdown_options)} game time options. Scraping each one...")
            
            for i, option in enumerate(dropdown_options):
                try:
                    print(f"\n{'='*60}")
                    print(f"🎮 Scraping Game Time {i+1}/{len(dropdown_options)}: {option['text']}")
                    print(f"{'='*60}")
                    
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
                        select.select_by_visible_text(option['text'])
                        time.sleep(5)  # Wait for page to update
                        
                        # Scroll to load ALL data for this game time
                        print(f"   📜 Scrolling to load ALL players for {option['text']}...")
                        scroll_to_load_all_data(driver)
                        
                        # Extract data for this option
                        option_data = extract_player_data(driver, option['text'])
                        
                        if option_data:
                            print(f"✅ Found {len(option_data)} players for {option['text']}")
                            all_player_data.extend(option_data)
                        else:
                            print(f"⚠️  No players found for {option['text']}")
                    
                except Exception as e:
                    print(f"❌ Error scraping option '{option['text']}': {e}")
                    continue
        else:
            print("⚠️  No dropdown found - scraping current view only")
            # Just scrape current view
            current_data = extract_player_data(driver, "Current View")
            if current_data:
                all_player_data.extend(current_data)
        
        print(f"\n🎉 Total players found across all games: {len(all_player_data)}")
        return all_player_data
        
    except Exception as e:
        print(f"❌ Error during scraping: {e}")
        return []
    finally:
        driver.quit()

def save_all_week6_sunday_data(player_data, filename="week6_Sunday_all_games.csv"):
    """Save the Week 6 Sunday data from all games with correct Points column."""
    if not player_data:
        print("❌ No data to save")
        return None
    
    print(f"🧹 Processing {len(player_data)} player records from all games...")
    
    # Create DataFrame
    df = pd.DataFrame(player_data)
    
    # Ensure directory exists
    os.makedirs("data_csv", exist_ok=True)
    
    # Save to CSV
    filepath = os.path.join("data_csv", filename)
    df.to_csv(filepath, index=False)
    
    print(f"\n✅ Data saved to {filepath}")
    print(f"📊 Total players: {len(player_data)}")
    
    # Show summary by game time
    if 'GameTime' in df.columns:
        print(f"\n📈 Summary by Game Time:")
        game_summary = df.groupby('GameTime').size().sort_values(ascending=False)
        for game_time, count in game_summary.items():
            print(f"   {game_time}: {count} players")
    
    return filepath

def main():
    """Main execution function."""
    print("="*80)
    print("MANUAL WEEK 6 SUNDAY ALL GAMES SCRAPER")
    print("="*80)
    print("📅 Week: 6")
    print("📆 Day: Sunday (ALL GAMES)")
    print("🖥️  Mode: GUI (to see dropdown interactions)")
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # Scrape all Sunday games
    player_data = scrape_all_week6_sunday_games()
    
    if player_data:
        # Save data
        filepath = save_all_week6_sunday_data(player_data)
        
        if filepath:
            print(f"\n🎉 SUCCESS! Week 6 Sunday data saved to {filepath}")
        else:
            print("\n❌ Failed to save data")
    else:
        print("\n❌ No data found")
    
    print(f"⏰ Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

if __name__ == "__main__":
    main()

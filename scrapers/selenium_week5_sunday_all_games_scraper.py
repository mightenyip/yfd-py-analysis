#!/usr/bin/env python3
"""
Selenium scraper for Yahoo Daily Fantasy Week 5 Sunday data - ALL GAMES.
This will look for dropdowns, filters, or other ways to access all Sunday games.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd
import time
import os
from datetime import datetime

def setup_driver(headless=False):  # Set to False to see what's happening
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

def explore_page_for_filters(driver):
    """Explore the page to find filters, dropdowns, or other ways to access all games."""
    print("🔍 Exploring page for filters and dropdowns...")
    
    try:
        # Look for common filter elements
        selectors_to_check = [
            "select",  # Dropdown selects
            "[role='button']",  # Buttons
            ".dropdown",  # Dropdown classes
            ".filter",  # Filter classes
            "[data-testid*='filter']",  # Test IDs with filter
            "[data-testid*='dropdown']",  # Test IDs with dropdown
            "[aria-label*='filter']",  # Aria labels with filter
            "[aria-label*='game']",  # Aria labels with game
            ".game-selector",  # Game selector classes
            ".week-selector",  # Week selector classes
        ]
        
        found_elements = []
        for selector in selectors_to_check:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"✅ Found {len(elements)} elements with selector: {selector}")
                    for i, elem in enumerate(elements[:5]):  # Show first 5
                        try:
                            text = elem.text.strip()
                            if text:
                                print(f"   {i+1}. {text[:50]}...")
                                found_elements.append((selector, elem, text))
                        except:
                            pass
            except Exception as e:
                print(f"   Error with selector {selector}: {e}")
        
        # Look for specific game-related elements
        print("\n🎮 Looking for game-specific elements...")
        game_elements = driver.find_elements(By.CSS_SELECTOR, "[class*='game'], [id*='game'], [data*='game']")
        print(f"Found {len(game_elements)} game-related elements")
        
        # Look for date/time filters
        print("\n📅 Looking for date/time filters...")
        date_elements = driver.find_elements(By.CSS_SELECTOR, "[class*='date'], [id*='date'], [data*='date']")
        print(f"Found {len(date_elements)} date-related elements")
        
        return found_elements
        
    except Exception as e:
        print(f"Error exploring page: {e}")
        return []

def check_for_dropdowns_and_buttons(driver):
    """Check for dropdowns and buttons that might control game selection."""
    print("🔍 Checking for dropdowns and buttons...")
    
    try:
        # Look for select elements (dropdowns)
        selects = driver.find_elements(By.TAG_NAME, "select")
        print(f"Found {len(selects)} select dropdowns")
        
        for i, select in enumerate(selects):
            try:
                select_obj = Select(select)
                options = select_obj.options
                print(f"  Select {i+1}: {len(options)} options")
                for j, option in enumerate(options[:10]):  # Show first 10 options
                    print(f"    {j+1}. {option.text.strip()}")
            except Exception as e:
                print(f"    Error with select {i+1}: {e}")
        
        # Look for buttons that might be filters
        buttons = driver.find_elements(By.TAG_NAME, "button")
        print(f"Found {len(buttons)} buttons")
        
        for i, button in enumerate(buttons[:20]):  # Check first 20 buttons
            try:
                text = button.text.strip()
                if text and len(text) < 50:  # Reasonable button text length
                    print(f"  Button {i+1}: '{text}'")
            except:
                pass
        
        # Look for clickable elements with game-related text
        clickable_elements = driver.find_elements(By.CSS_SELECTOR, "a, button, [role='button'], [onclick]")
        game_related = []
        for elem in clickable_elements:
            try:
                text = elem.text.strip().lower()
                if any(keyword in text for keyword in ['game', 'week', 'sunday', 'all', 'more', 'show']):
                    game_related.append((elem, text))
            except:
                pass
        
        print(f"Found {len(game_related)} potentially game-related clickable elements")
        for elem, text in game_related[:10]:
            print(f"  '{text}'")
        
        return selects, buttons, game_related
        
    except Exception as e:
        print(f"Error checking dropdowns: {e}")
        return [], [], []

def try_clicking_elements(driver, elements):
    """Try clicking on elements to see if they reveal more games."""
    print("🖱️ Trying to click on potential filter elements...")
    
    for i, (elem, text) in enumerate(elements[:5]):  # Try first 5 elements
        try:
            print(f"Trying to click element {i+1}: '{text[:30]}...'")
            driver.execute_script("arguments[0].click();", elem)
            time.sleep(2)
            
            # Check if more rows appeared
            current_rows = len(driver.find_elements(By.CSS_SELECTOR, "tr"))
            print(f"  Rows after click: {current_rows}")
            
        except Exception as e:
            print(f"  Error clicking element {i+1}: {e}")

def extract_all_available_players(driver):
    """Extract all available player data from the current view."""
    player_data = []
    
    try:
        # Wait for table to load
        wait = WebDriverWait(driver, 10)
        table = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table")))
        
        # Get all rows
        rows = table.find_elements(By.CSS_SELECTOR, "tr")
        print(f"✅ Found {len(rows)} total rows")
        
        # Process all rows (skip header row)
        for i in range(1, len(rows)):
            try:
                row = rows[i]
                cells = row.find_elements(By.CSS_SELECTOR, "td, th")
                
                if len(cells) >= 6:
                    # Extract data from specific columns
                    position = cells[0].text.strip() if len(cells) > 0 else ""
                    player_info = cells[2].text.strip() if len(cells) > 2 else ""
                    salary = cells[3].text.strip() if len(cells) > 3 else ""
                    fppg = cells[4].text.strip() if len(cells) > 4 else ""
                    points = cells[5].text.strip() if len(cells) > 5 else ""
                    
                    # Parse player name from the player_info
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
                            'week': 'Week 5',
                            'day': 'Sunday'
                        }
                        player_data.append(row_data)
                    
            except Exception as e:
                print(f"Error processing row {i}: {e}")
                continue
        
        print(f"✅ Successfully extracted {len(player_data)} players")
        return player_data
        
    except Exception as e:
        print(f"Error extracting player data: {e}")
        return []

def scrape_week5_sunday_all_games():
    """Main function to scrape Week 5 Sunday data from all games."""
    driver = setup_driver(headless=False)  # Keep visible to see what's happening
    if not driver:
        return []
    
    try:
        url = "https://sports.yahoo.com/dailyfantasy/research/completed"
        print(f"🌐 Loading {url}...")
        driver.get(url)
        
        # Wait for page to load
        time.sleep(5)
        
        # Explore the page for filters
        found_elements = explore_page_for_filters(driver)
        
        # Check for dropdowns and buttons
        selects, buttons, game_related = check_for_dropdowns_and_buttons(driver)
        
        # Try clicking on potential filter elements
        if game_related:
            try_clicking_elements(driver, game_related)
        
        # Try scrolling to load more data
        print("\n🔄 Scrolling to load more data...")
        for i in range(10):  # More aggressive scrolling
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            
            # Check if more rows appeared
            current_rows = len(driver.find_elements(By.CSS_SELECTOR, "tr"))
            print(f"   Scroll {i+1}: {current_rows} rows")
        
        # Scroll back to top
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)
        
        # Extract all available player data
        player_data = extract_all_available_players(driver)
        
        return player_data
        
    except Exception as e:
        print(f"Error during scraping: {e}")
        return []
    finally:
        input("Press Enter to close the browser...")  # Keep browser open to inspect
        driver.quit()

def save_week5_sunday_all_games_data(player_data, filename="week5_Sunday_all_games.csv"):
    """Save the Week 5 Sunday data from all games."""
    if not player_data:
        print("❌ No data to save")
        return None
    
    print(f"🧹 Processing {len(player_data)} player records...")
    
    # Create DataFrame
    df = pd.DataFrame(player_data)
    
    # Ensure the data_csv directory exists
    data_dir = "/Users/mightenyip/Documents/GitHub/yfd-py-test/data_csv"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    # Save to data_csv directory
    filepath = os.path.join(data_dir, filename)
    df.to_csv(filepath, index=False)
    
    print(f"✅ Week 5 Sunday all games data saved to {filepath}")
    print(f"📊 Found {len(player_data)} valid players")
    
    # Display summary
    if len(player_data) > 0:
        print(f"\n📋 Sample of Week 5 Sunday all games data:")
        for i, (_, row) in enumerate(df.head(10).iterrows(), 1):
            points = row['points'] if pd.notna(row['points']) else 'N/A'
            salary = row['salary'] if pd.notna(row['salary']) else 'N/A'
            game_info = row['game_info'] if pd.notna(row['game_info']) else 'N/A'
            print(f"  {i:2d}. {row['player_name']:<20} | {row['position']:<3} | {salary:<6} | Points: {points:<6} | Game: {game_info[:30]}")
        
        # Show unique games
        unique_games = df['game_info'].value_counts()
        print(f"\n🎮 Games found ({len(unique_games)} unique games):")
        for game, count in unique_games.items():
            print(f"   {game}: {count} players")
        
        # Show position breakdown
        position_counts = df['position'].value_counts()
        print(f"\n📊 Position breakdown:")
        for pos, count in position_counts.items():
            print(f"   {pos}: {count} players")
    
    return df

def main():
    print("Yahoo Daily Fantasy Week 5 Sunday ALL GAMES Data Scraper")
    print("=" * 70)
    print("This will explore the page for filters and try to access all Sunday games.")
    print("The browser will stay open so you can inspect the page manually.")
    print("=" * 70)
    
    # Scrape Week 5 Sunday data from all games
    player_data = scrape_week5_sunday_all_games()
    
    if player_data:
        # Save Week 5 Sunday all games data
        df = save_week5_sunday_all_games_data(player_data)
        
        if df is not None:
            print(f"\n🎉 SUCCESS! Scraped {len(df)} players for Week 5 Sunday (all games)")
            print("📁 Data saved to: data_csv/week5_Sunday_all_games.csv")
        else:
            print("\n❌ Failed to save data")
    else:
        print("\n❌ No data found")

if __name__ == "__main__":
    main()

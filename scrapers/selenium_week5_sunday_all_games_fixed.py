#!/usr/bin/env python3
"""
Advanced Selenium scraper for Yahoo Daily Fantasy Week 5 Sunday data from ALL game times.
This scraper detects and iterates through dropdown options to capture data from all available games.
Based on the correct points scraper that captures the correct Points column (Column 5) instead of FPPG (Column 4).
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
        options = select.options
        
        print(f"📋 Found {len(options)} dropdown options:")
        option_data = []
        for i, option in enumerate(options):
            option_text = option.text.strip()
            option_value = option.get_attribute('value')
            print(f"  {i+1}. '{option_text}' (value: {option_value})")
            option_data.append({
                'index': i,
                'text': option_text,
                'value': option_value,
                'element': option
            })
        
        return option_data
        
    except Exception as e:
        print(f"Error finding dropdown options: {e}")
        return []

def extract_players_with_correct_points(driver, game_time="Unknown"):
    """
    Extract player data using the correct column mapping.
    """
    player_data = []
    
    try:
        # Wait for table to load
        wait = WebDriverWait(driver, 15)
        table = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table")))
        
        # Get all rows
        rows = table.find_elements(By.CSS_SELECTOR, "tr")
        print(f"✅ Found {len(rows)} total rows for {game_time}")
        
        # Process all rows (skip header row)
        print(f"🔄 Processing {len(rows)-1} player rows for {game_time}...")
        
        for i in range(1, len(rows)):
            try:
                row = rows[i]
                cells = row.find_elements(By.CSS_SELECTOR, "td, th")
                
                if len(cells) >= 6:  # Need at least 6 columns
                    row_data = {}
                    
                    # Extract data from specific columns based on our analysis
                    # Column 0: Position
                    position = cells[0].text.strip() if len(cells) > 0 else ""
                    
                    # Column 2: Player name + game info + stats
                    player_info = cells[2].text.strip() if len(cells) > 2 else ""
                    
                    # Column 3: Salary
                    salary = cells[3].text.strip() if len(cells) > 3 else ""
                    
                    # Column 4: FPPG (season average) - we'll capture this for comparison
                    fppg = cells[4].text.strip() if len(cells) > 4 else ""
                    
                    # Column 5: Points (actual points from yesterday) - THIS IS WHAT WE WANT
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
                            'fppg': fppg,  # Season average
                            'points': points,  # Actual points from yesterday
                            'row_number': i,
                            'scrape_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'week': 'Week 5',
                            'day': 'Sunday',
                            'game_time': game_time  # Track which game time this data is from
                        }
                        player_data.append(row_data)
                    
                # Progress indicator
                if i % 50 == 0:
                    print(f"   Processed {i}/{len(rows)-1} rows for {game_time}...")
                    
            except Exception as e:
                print(f"Error processing row {i} for {game_time}: {e}")
                continue
        
        print(f"✅ Successfully extracted {len(player_data)} players for {game_time}")
        return player_data
        
    except Exception as e:
        print(f"Error extracting player data for {game_time}: {e}")
        return []

def scroll_to_load_more_data(driver):
    """
    Scroll down to load more data if needed.
    """
    try:
        print("🔄 Scrolling to load more data...")
        
        # Get initial row count
        initial_rows = len(driver.find_elements(By.CSS_SELECTOR, "tr"))
        print(f"   Initial rows: {initial_rows}")
        
        # Scroll down multiple times
        for i in range(5):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Check if more rows appeared
            current_rows = len(driver.find_elements(By.CSS_SELECTOR, "tr"))
            if current_rows > initial_rows:
                print(f"   Found {current_rows - initial_rows} more rows after scroll {i+1}")
                initial_rows = current_rows
            else:
                print(f"   No new rows after scroll {i+1}")
        
        # Scroll back to top
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
        
        final_rows = len(driver.find_elements(By.CSS_SELECTOR, "tr"))
        print(f"   Final row count: {final_rows}")
        
    except Exception as e:
        print(f"Error during scrolling: {e}")

def scrape_all_week5_sunday_games():
    """
    Main function to scrape Week 5 Sunday data from ALL game times.
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
                    
                    # Select the dropdown option
                    select = Select(driver.find_element(By.CSS_SELECTOR, "select"))
                    select.select_by_index(option['index'])
                    
                    # Wait for page to update
                    time.sleep(3)
                    
                    # Try scrolling to load more data
                    scroll_to_load_more_data(driver)
                    
                    # Extract player data for this game time
                    game_player_data = extract_players_with_correct_points(driver, option['text'])
                    all_player_data.extend(game_player_data)
                    
                    print(f"✅ Collected {len(game_player_data)} players from {option['text']}")
                    
                except Exception as e:
                    print(f"❌ Error scraping {option['text']}: {e}")
                    continue
        else:
            print("\n📋 No dropdown found - scraping current view only")
            scroll_to_load_more_data(driver)
            all_player_data = extract_players_with_correct_points(driver, "Default View")
        
        return all_player_data
        
    except Exception as e:
        print(f"Error during scraping: {e}")
        return []
    finally:
        driver.quit()

def save_all_week5_sunday_data(player_data, filename="week5_Sunday_all_games.csv"):
    """Save the Week 5 Sunday data from all games with correct Points column."""
    if not player_data:
        print("❌ No data to save")
        return None
    
    print(f"🧹 Processing {len(player_data)} player records from all games...")
    
    # Create DataFrame
    df = pd.DataFrame(player_data)
    
    # Ensure the data_csv directory exists
    data_dir = "/Users/mightenyip/Documents/GitHub/yfd-py-test/data_csv"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    # Save to data_csv directory
    filepath = os.path.join(data_dir, filename)
    df.to_csv(filepath, index=False)
    
    print(f"✅ Week 5 Sunday data from all games saved to {filepath}")
    print(f"📊 Found {len(player_data)} valid players from all games")
    
    # Display summary
    if len(player_data) > 0:
        print(f"\n📋 Sample of Week 5 Sunday data from all games:")
        for i, (_, row) in enumerate(df.head(10).iterrows(), 1):
            points = row['points'] if pd.notna(row['points']) else 'N/A'
            fppg = row['fppg'] if pd.notna(row['fppg']) else 'N/A'
            salary = row['salary'] if pd.notna(row['salary']) else 'N/A'
            game_time = row['game_time'] if pd.notna(row['game_time']) else 'Unknown'
            print(f"  {i:2d}. {row['player_name']:<20} | {row['position']:<3} | {salary:<6} | Points: {points:<6} | FPPG: {fppg:<6} | {game_time}")
        
        # Show players with 0 points (didn't play)
        zero_points = df[df['points'] == '0.0']
        if len(zero_points) > 0:
            print(f"\n📊 Players with 0 points (didn't play): {len(zero_points)}")
            for _, row in zero_points.head(5).iterrows():
                print(f"   {row['player_name']} | {row['position']} | FPPG: {row['fppg']} | {row['game_time']}")
        
        # Show position breakdown
        position_counts = df['position'].value_counts()
        print(f"\n📊 Position breakdown:")
        for pos, count in position_counts.items():
            print(f"   {pos}: {count} players")
        
        # Show game time breakdown
        if 'game_time' in df.columns:
            game_time_counts = df['game_time'].value_counts()
            print(f"\n📊 Game time breakdown:")
            for game_time, count in game_time_counts.items():
                print(f"   {game_time}: {count} players")
    
    return df

def main():
    print("Yahoo Daily Fantasy Week 5 Sunday Data Scraper - ALL GAMES")
    print("=" * 70)
    print("This will capture data from ALL available game times via dropdown.")
    print("Data will be saved as 'week5_Sunday_all_games.csv' in the data_csv directory.")
    print("=" * 70)
    
    # Scrape Week 5 Sunday data from all game times
    all_player_data = scrape_all_week5_sunday_games()
    
    if all_player_data:
        # Save Week 5 Sunday data from all games
        df = save_all_week5_sunday_data(all_player_data)
        
        if df is not None:
            print(f"\n🎉 SUCCESS! Scraped {len(df)} players from all Week 5 Sunday games")
            print("📁 Data saved to: data_csv/week5_Sunday_all_games.csv")
        else:
            print("\n❌ Failed to save data")
    else:
        print("\n❌ No data found")

if __name__ == "__main__":
    main()

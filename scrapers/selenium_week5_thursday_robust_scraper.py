#!/usr/bin/env python3
"""
Robust scraper for Yahoo Daily Fantasy Week 5 Thursday data (49ers vs Rams 10/2/25).
This version includes better error handling and multiple approaches to access the data.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import pandas as pd
import time
import os
from datetime import datetime
import requests
import json

def setup_driver(headless=False):
    """Set up Chrome driver with options."""
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver
    except Exception as e:
        print(f"Error setting up Chrome driver: {e}")
        return None

def try_api_approach():
    """Try to access data via API endpoints."""
    print("🔄 Trying API approach...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://sports.yahoo.com/dailyfantasy/research/completed'
    }
    
    # Try different API endpoints
    endpoints = [
        "https://sports.yahoo.com/dailyfantasy/api/research/completed",
        "https://sports.yahoo.com/dailyfantasy/api/players",
        "https://sports.yahoo.com/dailyfantasy/api/contests"
    ]
    
    for endpoint in endpoints:
        try:
            print(f"   Trying: {endpoint}")
            response = requests.get(endpoint, headers=headers, timeout=10)
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   ✅ Got data from {endpoint}")
                    return data
                except json.JSONDecodeError:
                    print(f"   Response not JSON: {response.text[:100]}...")
            else:
                print(f"   Status: {response.status_code}")
        except Exception as e:
            print(f"   Error: {e}")
    
    return None

def extract_players_robust(driver):
    """Extract player data with multiple fallback approaches."""
    player_data = []
    
    try:
        # Wait for any table to load
        wait = WebDriverWait(driver, 20)
        
        # Try multiple selectors
        selectors = [
            "table",
            "table[data-testid='player-table']",
            ".player-table",
            "[data-testid='research-table']",
            "table tbody tr",
            ".fantasy-table"
        ]
        
        table = None
        for selector in selectors:
            try:
                table = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                print(f"✅ Found table with selector: {selector}")
                break
            except TimeoutException:
                continue
        
        if not table:
            print("❌ No table found with any selector")
            return []
        
        # Get all rows
        rows = table.find_elements(By.CSS_SELECTOR, "tr")
        print(f"✅ Found {len(rows)} total rows")
        
        if len(rows) == 0:
            print("❌ No rows found in table")
            return []
        
        # Process all rows (skip header row)
        print(f"🔄 Processing {len(rows)-1} player rows...")
        
        for i in range(1, len(rows)):
            try:
                row = rows[i]
                cells = row.find_elements(By.CSS_SELECTOR, "td, th")
                
                if len(cells) >= 4:  # Need at least 4 columns
                    row_data = {}
                    
                    # Extract data from columns
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
                            'day': 'Thursday'
                        }
                        player_data.append(row_data)
                    
                # Progress indicator
                if i % 50 == 0:
                    print(f"   Processed {i}/{len(rows)-1} rows...")
                    
            except Exception as e:
                print(f"Error processing row {i}: {e}")
                continue
        
        print(f"✅ Successfully extracted {len(player_data)} players")
        return player_data
        
    except Exception as e:
        print(f"Error extracting player data: {e}")
        return []

def scroll_and_wait(driver):
    """Scroll and wait for data to load."""
    try:
        print("🔄 Scrolling and waiting for data...")
        
        # Get initial row count
        initial_rows = len(driver.find_elements(By.CSS_SELECTOR, "tr"))
        print(f"   Initial rows: {initial_rows}")
        
        # Scroll down multiple times
        for i in range(10):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            
            # Check if more rows appeared
            current_rows = len(driver.find_elements(By.CSS_SELECTOR, "tr"))
            if current_rows > initial_rows:
                print(f"   Found {current_rows - initial_rows} more rows after scroll {i+1}")
                initial_rows = current_rows
            else:
                print(f"   No new rows after scroll {i+1}")
        
        # Scroll back to top
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)
        
        final_rows = len(driver.find_elements(By.CSS_SELECTOR, "tr"))
        print(f"   Final row count: {final_rows}")
        
    except Exception as e:
        print(f"Error during scrolling: {e}")

def scrape_week5_thursday_robust():
    """Main function to scrape Week 5 Thursday data with multiple approaches."""
    
    # First try API approach
    api_data = try_api_approach()
    if api_data:
        print("✅ Got data via API")
        return api_data
    
    # If API fails, try Selenium approach
    print("🔄 API failed, trying Selenium approach...")
    driver = setup_driver(headless=False)
    if not driver:
        return []
    
    try:
        url = "https://sports.yahoo.com/dailyfantasy/research/completed"
        print(f"🌐 Loading {url}...")
        driver.get(url)
        
        # Wait for page to load
        time.sleep(15)
        
        # Try scrolling to load more data
        scroll_and_wait(driver)
        
        # Extract player data
        player_data = extract_players_robust(driver)
        
        return player_data
        
    except Exception as e:
        print(f"Error during scraping: {e}")
        return []
    finally:
        driver.quit()

def save_week5_thursday_data(player_data, filename="week5_Thurs.csv"):
    """Save the Week 5 Thursday data."""
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
    
    print(f"✅ Week 5 Thursday data saved to {filepath}")
    print(f"📊 Found {len(player_data)} valid players")
    
    # Display summary
    if len(player_data) > 0:
        print(f"\n📋 Sample of Week 5 Thursday data:")
        for i, (_, row) in enumerate(df.head(10).iterrows(), 1):
            points = row['points'] if pd.notna(row['points']) else 'N/A'
            fppg = row['fppg'] if pd.notna(row['fppg']) else 'N/A'
            salary = row['salary'] if pd.notna(row['salary']) else 'N/A'
            print(f"  {i:2d}. {row['player_name']:<20} | {row['position']:<3} | {salary:<6} | Points: {points:<6} | FPPG: {fppg}")
        
        # Show position breakdown
        position_counts = df['position'].value_counts()
        print(f"\n📊 Position breakdown:")
        for pos, count in position_counts.items():
            print(f"   {pos}: {count} players")
    
    return df

def main():
    print("Yahoo Daily Fantasy Week 5 Thursday Data Scraper (Robust)")
    print("=" * 70)
    print("Targeting: 49ers vs Rams on 10/2/25")
    print("This will try multiple approaches to get the data.")
    print("=" * 70)
    
    # Scrape Week 5 Thursday data
    player_data = scrape_week5_thursday_robust()
    
    if player_data:
        # Save Week 5 Thursday data
        df = save_week5_thursday_data(player_data)
        
        if df is not None:
            print(f"\n🎉 SUCCESS! Scraped {len(df)} players for Week 5 Thursday")
            print("📁 Data saved to: data_csv/week5_Thurs.csv")
        else:
            print("\n❌ Failed to save data")
    else:
        print("\n❌ No data found")
        print("The data might not be available yet or there might be access issues.")

if __name__ == "__main__":
    main()

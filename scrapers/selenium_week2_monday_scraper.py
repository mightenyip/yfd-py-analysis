#!/usr/bin/env python3
"""
Selenium scraper for Week 2 Monday Yahoo DFS data.
Based on selenium_correct_points_scraper.py but modified for Week 2 Monday.
Captures the correct Points column (Column 5) instead of FPPG (Column 4).
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
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

def extract_players_with_correct_points(driver):
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
        print(f"✅ Found {len(rows)} total rows")
        
        # Process all rows (skip header row)
        print(f"🔄 Processing {len(rows)-1} player rows...")
        
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
                            'scrape_date': datetime.now().strftime('%Y-%m-%d'),
                            'week': 'Week 2',
                            'day': 'Monday'
                        }
                        player_data.append(row_data)
                    
                # Progress indicator
                if i % 100 == 0:
                    print(f"   Processed {i}/{len(rows)-1} rows...")
                    
            except Exception as e:
                print(f"Error processing row {i}: {e}")
                continue
        
        print(f"✅ Successfully extracted {len(player_data)} players")
        return player_data
        
    except Exception as e:
        print(f"Error extracting player data: {e}")
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

def scrape_week2_monday_data():
    """
    Main function to scrape Week 2 Monday data with correct Points column.
    """
    driver = setup_driver(headless=True)  # Run in background for speed
    if not driver:
        return []
    
    try:
        url = "https://sports.yahoo.com/dailyfantasy/research/completed"
        print(f"🌐 Loading {url}...")
        driver.get(url)
        
        # Wait for page to load
        time.sleep(5)
        
        # Try scrolling to load more data
        scroll_to_load_more_data(driver)
        
        # Extract player data with correct column mapping
        player_data = extract_players_with_correct_points(driver)
        
        return player_data
        
    except Exception as e:
        print(f"Error during scraping: {e}")
        return []
    finally:
        driver.quit()

def save_week2_monday_data(player_data, filename="week2_Mon.csv"):
    """Save the Week 2 Monday data with correct Points column."""
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
    
    print(f"✅ Week 2 Monday data saved to {filepath}")
    print(f"📊 Found {len(player_data)} valid players")
    
    # Display summary
    if len(player_data) > 0:
        print(f"\n📋 Sample of Week 2 Monday data (Points vs FPPG):")
        for i, (_, row) in enumerate(df.head(10).iterrows(), 1):
            points = row['points'] if pd.notna(row['points']) else 'N/A'
            fppg = row['fppg'] if pd.notna(row['fppg']) else 'N/A'
            salary = row['salary'] if pd.notna(row['salary']) else 'N/A'
            print(f"  {i:2d}. {row['player_name']:<20} | {row['position']:<3} | {salary:<6} | Points: {points:<6} | FPPG: {fppg}")
        
        # Show players with 0 points (didn't play)
        zero_points = df[df['points'] == '0.0']
        if len(zero_points) > 0:
            print(f"\n📊 Players with 0 points (didn't play Monday): {len(zero_points)}")
            for _, row in zero_points.head(5).iterrows():
                print(f"   {row['player_name']} | {row['position']} | FPPG: {row['fppg']}")
        
        # Show position breakdown
        position_counts = df['position'].value_counts()
        print(f"\n📊 Position breakdown:")
        for pos, count in position_counts.items():
            print(f"   {pos}: {count} players")
        
        # Show top performers
        try:
            # Convert points to numeric for sorting
            df['points_numeric'] = pd.to_numeric(df['points'], errors='coerce')
            top_performers = df.nlargest(5, 'points_numeric')
            print(f"\n🏆 Top 5 performers (by points):")
            for _, row in top_performers.iterrows():
                print(f"   {row['player_name']} | {row['position']} | {row['salary']} | Points: {row['points']}")
        except Exception as e:
            print(f"Could not determine top performers: {e}")
    
    return df

def main():
    print("Yahoo Daily Fantasy Week 2 Monday Data Scraper")
    print("=" * 60)
    print("This will capture the correct Points column (Column 5) instead of FPPG (Column 4).")
    print("Data will be saved as 'week2_Mon.csv' in the data_csv directory.")
    print("=" * 60)
    
    # Scrape Week 2 Monday data with correct column mapping
    player_data = scrape_week2_monday_data()
    
    if player_data:
        # Save Week 2 Monday data
        df = save_week2_monday_data(player_data)
        
        if df is not None:
            print(f"\n🎉 SUCCESS! Scraped {len(df)} players for Week 2 Monday")
            print("📁 Data saved to: data_csv/week2_Mon.csv")
        else:
            print("\n❌ Failed to save data")
    else:
        print("\n❌ No data found")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Script to scrape Yahoo Daily Fantasy data using Selenium for dynamic content.
Requires: pip install selenium beautifulsoup4 pandas
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time
import json

def setup_driver():
    """Set up Chrome driver with options."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in background
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        print(f"Error setting up Chrome driver: {e}")
        print("Make sure you have ChromeDriver installed and in your PATH")
        return None

def scrape_daily_fantasy_with_selenium():
    """
    Scrape Yahoo Daily Fantasy data using Selenium.
    """
    driver = setup_driver()
    if not driver:
        return []
    
    try:
        url = "https://sports.yahoo.com/dailyfantasy/research/completed"
        print(f"Loading {url}...")
        driver.get(url)
        
        # Wait for page to load
        wait = WebDriverWait(driver, 10)
        
        # Wait for player data to load (adjust selector as needed)
        try:
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "player")))
        except:
            print("Player data not found with expected selector")
        
        # Give extra time for dynamic content
        time.sleep(3)
        
        # Look for player data in various possible locations
        player_data = []
        
        # Method 1: Look for table rows
        try:
            rows = driver.find_elements(By.CSS_SELECTOR, "tr[data-player-id], .player-row, .player")
            print(f"Found {len(rows)} potential player rows")
            
            for row in rows[:10]:  # Limit to first 10 for testing
                try:
                    player_info = {}
                    
                    # Try to extract player name
                    name_elem = row.find_element(By.CSS_SELECTOR, ".player-name, .name, [data-player-name]")
                    player_info['name'] = name_elem.text if name_elem else "Unknown"
                    
                    # Try to extract position
                    pos_elem = row.find_element(By.CSS_SELECTOR, ".position, .pos, [data-position]")
                    player_info['position'] = pos_elem.text if pos_elem else "Unknown"
                    
                    # Try to extract salary
                    salary_elem = row.find_element(By.CSS_SELECTOR, ".salary, .price, [data-salary]")
                    player_info['salary'] = salary_elem.text if salary_elem else "Unknown"
                    
                    # Try to extract points
                    points_elem = row.find_element(By.CSS_SELECTOR, ".points, .fppg, [data-points]")
                    player_info['points'] = points_elem.text if points_elem else "Unknown"
                    
                    player_data.append(player_info)
                    
                except Exception as e:
                    print(f"Error extracting data from row: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error finding player rows: {e}")
        
        # Method 2: Look for JSON data in page source
        try:
            page_source = driver.page_source
            if 'window.__INITIAL_STATE__' in page_source:
                print("Found initial state data in page source")
                # Extract and parse JSON data here
        except Exception as e:
            print(f"Error checking page source: {e}")
        
        return player_data
        
    except Exception as e:
        print(f"Error during scraping: {e}")
        return []
    finally:
        driver.quit()

def save_data_to_csv(data, filename="yahoo_daily_fantasy_selenium.csv"):
    """Save scraped data to CSV file."""
    if data:
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        print(f"Data saved to {filename}")
        print(f"Found {len(data)} players")
        
        # Display sample data
        if len(data) > 0:
            print("\nSample data:")
            print(df.head())
    else:
        print("No data to save")

if __name__ == "__main__":
    print("Yahoo Daily Fantasy Data Scraper (Selenium)")
    print("=" * 50)
    
    data = scrape_daily_fantasy_with_selenium()
    save_data_to_csv(data)

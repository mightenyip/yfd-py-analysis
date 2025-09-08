#!/usr/bin/env python3
"""
Full Selenium scraper for Yahoo Daily Fantasy player data - gets ALL players.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd
import time
import json

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

def extract_all_player_data(driver):
    """
    Extract ALL player data from the table, not just the first 20.
    """
    player_data = []
    
    try:
        # Wait for the page to load
        wait = WebDriverWait(driver, 15)
        
        # Look for the main data table
        table_selectors = [
            "table",
            "[data-testid*='table']",
            "[data-testid*='player']",
            ".player-table",
            ".data-table",
            "[role='table']",
            ".table",
            "div[class*='table']",
            "div[class*='player']"
        ]
        
        table = None
        for selector in table_selectors:
            try:
                table = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                print(f"✅ Found table with selector: {selector}")
                break
            except TimeoutException:
                continue
        
        if not table:
            print("❌ No table found with any selector")
            return player_data
        
        # Try to find rows in the table
        row_selectors = [
            "tr",
            "[role='row']",
            "div[class*='row']",
            "div[class*='player']"
        ]
        
        rows = []
        for selector in row_selectors:
            rows = table.find_elements(By.CSS_SELECTOR, selector)
            if rows:
                print(f"✅ Found {len(rows)} total rows with selector: {selector}")
                break
        
        if not rows:
            print("❌ No rows found in table")
            return player_data
        
        # Extract data from ALL rows (not just first 20)
        print(f"🔄 Processing all {len(rows)} rows...")
        
        for i, row in enumerate(rows):
            try:
                # Get all cells in the row
                cells = row.find_elements(By.CSS_SELECTOR, "td, th, div[class*='cell'], span")
                
                if len(cells) >= 3:  # Need at least 3 columns of data
                    row_data = {}
                    
                    # Extract text from each cell
                    cell_texts = [cell.text.strip() for cell in cells if cell.text.strip()]
                    
                    if cell_texts:
                        # Try to identify what each column contains
                        row_data['raw_data'] = cell_texts
                        row_data['row_number'] = i + 1
                        
                        # Look for common patterns
                        for j, text in enumerate(cell_texts):
                            if any(pos in text.upper() for pos in ['QB', 'RB', 'WR', 'TE', 'K', 'DEF']):
                                row_data['position'] = text
                            elif '$' in text:
                                row_data['salary'] = text
                            elif text.replace('.', '').isdigit():
                                row_data['points'] = text
                            elif len(text) > 3 and not text.isdigit():
                                row_data['player_name'] = text
                        
                        player_data.append(row_data)
                        
                # Progress indicator for large datasets
                if (i + 1) % 50 == 0:
                    print(f"   Processed {i + 1}/{len(rows)} rows...")
                        
            except Exception as e:
                print(f"Error processing row {i}: {e}")
                continue
        
        print(f"✅ Successfully processed {len(rows)} rows")
        return player_data
        
    except Exception as e:
        print(f"Error extracting table data: {e}")
        return player_data

def scroll_to_load_more_data(driver):
    """
    Scroll down to potentially load more data if the table is paginated or lazy-loaded.
    """
    try:
        print("🔄 Scrolling to load more data...")
        
        # Get initial row count
        initial_rows = len(driver.find_elements(By.CSS_SELECTOR, "tr"))
        print(f"   Initial rows: {initial_rows}")
        
        # Scroll down multiple times
        for i in range(5):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Wait for potential lazy loading
            
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

def scrape_all_yahoo_daily_fantasy_data():
    """
    Main function to scrape ALL Yahoo Daily Fantasy data.
    """
    driver = setup_driver(headless=False)  # Set to False to see the browser
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
        
        print("📊 Extracting ALL player data from table...")
        player_data = extract_all_player_data(driver)
        
        return player_data
        
    except Exception as e:
        print(f"Error during scraping: {e}")
        return []
    finally:
        input("Press Enter to close the browser...")  # Keep browser open for inspection
        driver.quit()

def save_all_data_to_csv(data, filename="yahoo_daily_fantasy_all_players.csv"):
    """Save all scraped data to CSV file."""
    if data:
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        print(f"💾 Data saved to {filename}")
        print(f"📊 Found {len(data)} total records")
        
        # Display sample data
        if len(data) > 0:
            print(f"\n📋 First 5 records:")
            for i, record in enumerate(data[:5]):
                print(f"  {i+1}. {record}")
            
            print(f"\n📋 Last 5 records:")
            for i, record in enumerate(data[-5:], len(data)-4):
                print(f"  {i}. {record}")
    else:
        print("❌ No data to save")

def main():
    print("Yahoo Daily Fantasy Player Data Scraper - FULL VERSION")
    print("=" * 60)
    print("This will scrape ALL players from the table, not just the first 20.")
    print("The browser window will stay open so you can inspect the page.")
    print("=" * 60)
    
    data = scrape_all_yahoo_daily_fantasy_data()
    save_all_data_to_csv(data)
    
    if data:
        print(f"\n🎉 SUCCESS! Scraped {len(data)} total players!")
        print("📁 Data saved to: yahoo_daily_fantasy_all_players.csv")
    else:
        print("\n❌ No data found. Check the browser window for any errors.")

if __name__ == "__main__":
    main()

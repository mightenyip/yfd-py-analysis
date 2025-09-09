#!/usr/bin/env python3
"""
Selenium-based scraper for Yahoo Daily Fantasy player data.
This script will actually load the page and extract the table data.
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

def extract_player_data_from_table(driver):
    """
    Extract player data from the main table on the page.
    """
    player_data = []
    
    try:
        # Wait for the page to load
        wait = WebDriverWait(driver, 15)
        
        # Look for the main data table - try multiple selectors
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
                print(f"✅ Found {len(rows)} rows with selector: {selector}")
                break
        
        if not rows:
            print("❌ No rows found in table")
            return player_data
        
        # Extract data from each row
        for i, row in enumerate(rows[:20]):  # Limit to first 20 rows for testing
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
                        
            except Exception as e:
                print(f"Error processing row {i}: {e}")
                continue
        
        return player_data
        
    except Exception as e:
        print(f"Error extracting table data: {e}")
        return player_data

def extract_data_from_page_source(driver):
    """
    Try to extract data from the page source after it's fully loaded.
    """
    try:
        page_source = driver.page_source
        
        # Look for any JSON-like data in the page source
        import re
        
        # Look for patterns that might contain player data
        patterns = [
            r'"players":\s*\[(.*?)\]',
            r'"playerData":\s*\[(.*?)\]',
            r'"fantasyData":\s*\[(.*?)\]',
            r'"dailyFantasy":\s*\[(.*?)\]',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, page_source, re.DOTALL)
            if matches:
                print(f"✅ Found potential data with pattern: {pattern}")
                for match in matches[:3]:  # Show first 3 matches
                    print(f"   Sample: {match[:200]}...")
        
        return page_source
        
    except Exception as e:
        print(f"Error extracting from page source: {e}")
        return None

def scrape_yahoo_daily_fantasy():
    """
    Main function to scrape Yahoo Daily Fantasy data.
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
        
        print("📊 Extracting player data from table...")
        player_data = extract_player_data_from_table(driver)
        
        if not player_data:
            print("🔍 No table data found, checking page source...")
            page_source = extract_data_from_page_source(driver)
            
            if page_source:
                print("📄 Page source extracted, but no structured data found")
                print("💡 The page might use a different data structure")
        
        return player_data
        
    except Exception as e:
        print(f"Error during scraping: {e}")
        return []
    finally:
        input("Press Enter to close the browser...")  # Keep browser open for inspection
        driver.quit()

def save_data_to_csv(data, filename="yahoo_daily_fantasy_players.csv"):
    """Save scraped data to CSV file."""
    if data:
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        print(f"💾 Data saved to {filename}")
        print(f"📊 Found {len(data)} records")
        
        # Display sample data
        if len(data) > 0:
            print("\n📋 Sample data:")
            for i, record in enumerate(data[:5]):
                print(f"  {i+1}. {record}")
    else:
        print("❌ No data to save")

def main():
    print("Yahoo Daily Fantasy Player Data Scraper")
    print("=" * 50)
    print("This will open a browser window to load the page.")
    print("You can watch the process and inspect the page manually.")
    print("=" * 50)
    
    data = scrape_yahoo_daily_fantasy()
    save_data_to_csv(data)
    
    if not data:
        print("\n💡 TROUBLESHOOTING TIPS:")
        print("1. Check if the page loaded correctly in the browser")
        print("2. Look for any error messages or blocked content")
        print("3. Try running without headless mode to see what's happening")
        print("4. Check if Yahoo requires login for this data")
        print("5. The page structure might have changed")

if __name__ == "__main__":
    main()

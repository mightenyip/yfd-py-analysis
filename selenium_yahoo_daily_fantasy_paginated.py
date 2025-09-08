#!/usr/bin/env python3
"""
Selenium scraper for Yahoo Daily Fantasy that handles pagination and loads more data.
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
        return None

def try_to_load_more_data(driver):
    """
    Try various methods to load more data.
    """
    print("🔄 Attempting to load more data...")
    
    # Method 1: Scroll down multiple times
    print("   Method 1: Scrolling down...")
    for i in range(10):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        
        # Check if more rows appeared
        current_rows = len(driver.find_elements(By.CSS_SELECTOR, "tr"))
        print(f"     Scroll {i+1}: {current_rows} rows")
    
    # Method 2: Look for "Load More" or "Show More" buttons
    print("   Method 2: Looking for load more buttons...")
    load_more_selectors = [
        "button[class*='load']",
        "button[class*='more']",
        "button[class*='show']",
        "a[class*='load']",
        "a[class*='more']",
        "a[class*='show']",
        "[data-testid*='load']",
        "[data-testid*='more']",
        "[data-testid*='show']"
    ]
    
    for selector in load_more_selectors:
        try:
            buttons = driver.find_elements(By.CSS_SELECTOR, selector)
            for button in buttons:
                if button.is_displayed() and button.is_enabled():
                    print(f"     Found load more button: {button.text}")
                    try:
                        button.click()
                        time.sleep(2)
                        print(f"     Clicked button, now have {len(driver.find_elements(By.CSS_SELECTOR, 'tr'))} rows")
                    except:
                        pass
        except:
            continue
    
    # Method 3: Look for pagination
    print("   Method 3: Looking for pagination...")
    pagination_selectors = [
        "[class*='pagination']",
        "[class*='page']",
        "nav[aria-label*='page']",
        ".pagination",
        ".pager"
    ]
    
    for selector in pagination_selectors:
        try:
            pagination = driver.find_elements(By.CSS_SELECTOR, selector)
            if pagination:
                print(f"     Found pagination element")
                # Try clicking next page
                next_buttons = driver.find_elements(By.CSS_SELECTOR, f"{selector} a[class*='next'], {selector} button[class*='next']")
                for button in next_buttons:
                    if button.is_displayed() and button.is_enabled():
                        print(f"     Found next page button: {button.text}")
                        try:
                            button.click()
                            time.sleep(3)
                            print(f"     Clicked next page, now have {len(driver.find_elements(By.CSS_SELECTOR, 'tr'))} rows")
                        except:
                            pass
        except:
            continue
    
    # Method 4: Look for filters or dropdowns that might show more players
    print("   Method 4: Looking for filters...")
    filter_selectors = [
        "select",
        "[class*='filter']",
        "[class*='dropdown']",
        "[data-testid*='filter']"
    ]
    
    for selector in filter_selectors:
        try:
            filters = driver.find_elements(By.CSS_SELECTOR, selector)
            for filter_elem in filters:
                if filter_elem.is_displayed():
                    print(f"     Found filter element: {filter_elem.tag_name}")
        except:
            continue

def extract_all_available_players(driver):
    """
    Extract all available players from the current page state.
    """
    player_data = []
    
    try:
        # Wait for the page to load
        wait = WebDriverWait(driver, 15)
        
        # Look for the main data table
        table = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table")))
        print(f"✅ Found table")
        
        # Get all rows
        rows = table.find_elements(By.CSS_SELECTOR, "tr")
        print(f"✅ Found {len(rows)} total rows")
        
        # Process all rows (skip header row)
        print(f"🔄 Processing all {len(rows)-1} player rows...")
        
        for i in range(1, len(rows)):  # Skip header row (index 0)
            try:
                row = rows[i]
                
                # Get all cells in the row
                cells = row.find_elements(By.CSS_SELECTOR, "td, th, div[class*='cell'], span")
                
                if len(cells) >= 3:  # Need at least 3 columns of data
                    row_data = {}
                    
                    # Extract text from each cell
                    cell_texts = [cell.text.strip() for cell in cells if cell.text.strip()]
                    
                    if cell_texts:
                        # Try to identify what each column contains
                        row_data['raw_data'] = cell_texts
                        row_data['row_number'] = i
                        
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
                        
                # Progress indicator
                if i % 50 == 0:
                    print(f"   Processed {i-1}/{len(rows)-1} players...")
                        
            except Exception as e:
                print(f"Error processing row {i}: {e}")
                continue
        
        print(f"✅ Successfully processed {len(player_data)} players")
        return player_data
        
    except Exception as e:
        print(f"Error extracting table data: {e}")
        return player_data

def scrape_with_pagination():
    """
    Main function to scrape Yahoo Daily Fantasy data with pagination handling.
    """
    driver = setup_driver(headless=False)  # Keep visible to see what's happening
    if not driver:
        return []
    
    try:
        url = "https://sports.yahoo.com/dailyfantasy/research/completed"
        print(f"🌐 Loading {url}...")
        driver.get(url)
        
        # Wait for page to load
        time.sleep(5)
        
        # Try to load more data
        try_to_load_more_data(driver)
        
        print("📊 Extracting all available players...")
        player_data = extract_all_available_players(driver)
        
        return player_data
        
    except Exception as e:
        print(f"Error during scraping: {e}")
        return []
    finally:
        input("Press Enter to close the browser...")  # Keep browser open for inspection
        driver.quit()

def clean_and_save_data(data, filename="yahoo_daily_fantasy_paginated.csv"):
    """Clean and save the scraped data."""
    if not data:
        print("❌ No data to save")
        return None
    
    print(f"🧹 Cleaning {len(data)} player records...")
    
    cleaned_data = []
    
    for record in data:
        raw_data = record['raw_data']
        
        # Extract player name (usually in the 3rd element with newlines)
        player_info = raw_data[2] if len(raw_data) > 2 else ""
        
        # Split by newlines to get player name and game info
        lines = player_info.split('\n')
        player_name = lines[0].strip() if lines else "Unknown"
        
        # Extract game info
        game_info = lines[1] if len(lines) > 1 else ""
        
        # Extract stats
        stats = lines[2] if len(lines) > 2 else ""
        
        # Find salary (look for $ pattern)
        salary = None
        for item in raw_data:
            if '$' in str(item) and str(item).replace('$', '').replace(',', '').isdigit():
                salary = str(item)
                break
        
        # Find points (look for decimal numbers)
        points = None
        for item in raw_data:
            if isinstance(item, str) and '.' in item:
                try:
                    float(item)
                    if len(item) <= 6:  # Reasonable points range
                        points = item
                        break
                except ValueError:
                    continue
        
        # Extract position
        position = record.get('position', 'Unknown')
        
        # Only include if we have a valid player name
        if player_name and player_name != "Unknown" and len(player_name) > 2:
            cleaned_record = {
                'player_name': player_name,
                'position': position,
                'game_info': game_info,
                'stats': stats,
                'salary': salary,
                'points': points
            }
            cleaned_data.append(cleaned_record)
    
    # Create and save DataFrame
    df = pd.DataFrame(cleaned_data)
    df.to_csv(filename, index=False)
    
    print(f"✅ Cleaned data saved to {filename}")
    print(f"📊 Found {len(cleaned_data)} valid players")
    
    # Display summary
    if len(cleaned_data) > 0:
        print(f"\n📋 Sample of cleaned data:")
        for i, row in df.head(10).iterrows():
            points = row['points'] if pd.notna(row['points']) else "N/A"
            salary = row['salary'] if pd.notna(row['salary']) else "N/A"
            print(f"  {i+1:2d}. {row['player_name']:<20} | {row['position']:<3} | {salary:<6} | {points}")
        
        # Position breakdown
        print(f"\n🏈 Players by Position:")
        position_counts = df['position'].value_counts()
        for pos, count in position_counts.items():
            print(f"   {pos}: {count} players")
    
    return df

def main():
    print("Yahoo Daily Fantasy Player Data Scraper - With Pagination")
    print("=" * 60)
    print("This will try to load more data and handle pagination.")
    print("The browser will stay open so you can see what's happening.")
    print("=" * 60)
    
    # Scrape the data
    data = scrape_with_pagination()
    
    if data:
        # Clean and save
        df = clean_and_save_data(data)
        
        if df is not None:
            print(f"\n🎉 SUCCESS! Scraped {len(df)} players!")
            print("📁 Data saved to: yahoo_daily_fantasy_paginated.csv")
        else:
            print("\n❌ Failed to clean data")
    else:
        print("\n❌ No data found")

if __name__ == "__main__":
    main()

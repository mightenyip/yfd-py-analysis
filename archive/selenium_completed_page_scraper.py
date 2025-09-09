#!/usr/bin/env python3
"""
Selenium scraper for Yahoo's Daily Fantasy completed games page.
This targets the correct URL: https://sports.yahoo.com/dailyfantasy/research/completed
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
import re

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
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        print(f"Error setting up Chrome driver: {e}")
        return None

def get_week_info():
    """Get current week information for file naming."""
    now = datetime.now()
    year = now.year
    week = 1  # Default to week 1 for now
    return f"{year}_week{week}"

def scroll_to_load_more_data(driver):
    """Scroll down to load more data if needed."""
    print("📜 Scrolling to load more data...")
    
    # Get initial page height
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    # Scroll down multiple times
    for i in range(5):  # Scroll 5 times
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        
        # Check if new content loaded
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    
    print("✅ Finished scrolling")

def extract_players_from_completed_page(driver):
    """Extract player data from the completed games page."""
    player_data = []
    
    try:
        # Wait for table to load
        wait = WebDriverWait(driver, 15)
        table = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table")))
        
        # Get all rows
        rows = table.find_elements(By.CSS_SELECTOR, "tr")
        print(f"✅ Found {len(rows)} total rows")
        
        # Process all rows (skip header row)
        for i in range(1, len(rows)):
            try:
                row = rows[i]
                cells = row.find_elements(By.CSS_SELECTOR, "td, th")
                
                if len(cells) >= 6:  # Need at least 6 columns
                    row_data = {}
                    
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
                            'row_number': i
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

def check_for_date_navigation(driver):
    """Check if there are date navigation elements on the completed page."""
    print("🔍 Checking for date navigation elements...")
    
    # Look for date-related elements
    date_selectors = [
        "button[aria-label*='previous']",
        "button[aria-label*='next']",
        "button[aria-label*='arrow']",
        "button[class*='arrow']",
        "button[class*='nav']",
        "[data-testid*='arrow']",
        "[data-testid*='nav']",
        "[data-testid*='date']",
        "[class*='date']",
        "button:contains('<')",
        "button:contains('>')"
    ]
    
    found_elements = []
    for selector in date_selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                for element in elements:
                    try:
                        text = element.text.strip()
                        aria_label = element.get_attribute('aria-label') or ""
                        class_name = element.get_attribute('class') or ""
                        
                        if text or aria_label or 'date' in class_name.lower() or 'nav' in class_name.lower() or 'arrow' in class_name.lower():
                            found_elements.append({
                                'selector': selector,
                                'text': text,
                                'aria_label': aria_label,
                                'class': class_name[:50]
                            })
                    except:
                        pass
        except:
            continue
    
    if found_elements:
        print(f"✅ Found {len(found_elements)} potential date navigation elements:")
        for i, elem in enumerate(found_elements[:10]):  # Show first 10
            print(f"   {i+1}. {elem['selector']} | Text: '{elem['text']}' | Aria: '{elem['aria_label']}'")
        return found_elements
    else:
        print("❌ No date navigation elements found")
        return []

def scrape_completed_page():
    """Main function to scrape the completed games page."""
    driver = setup_driver(headless=False)  # Keep visible to see what's happening
    if not driver:
        return []
    
    all_player_data = []
    
    try:
        # Navigate to Yahoo Daily Fantasy completed page
        url = "https://sports.yahoo.com/dailyfantasy/research/completed"
        print(f"🌐 Loading {url}...")
        driver.get(url)
        
        # Wait for page to load
        time.sleep(5)
        
        # Check for date navigation elements
        date_elements = check_for_date_navigation(driver)
        
        # Scroll to load more data
        scroll_to_load_more_data(driver)
        
        # Extract players
        player_data = extract_players_from_completed_page(driver)
        all_player_data.extend(player_data)
        
        return all_player_data
        
    except Exception as e:
        print(f"Error during completed page scraping: {e}")
        return []
    finally:
        input("Press Enter to close the browser...")
        driver.quit()

def save_completed_data(player_data, week_info):
    """Save the completed page data."""
    if not player_data:
        print("❌ No data to save")
        return None
    
    print(f"🧹 Processing {len(player_data)} player records for {week_info}...")
    
    # Create DataFrame
    df = pd.DataFrame(player_data)
    
    # Main weekly file
    main_filename = f"yahoo_daily_fantasy_{week_info}_completed_page.csv"
    df.to_csv(main_filename, index=False)
    
    print(f"✅ Completed page data saved to {main_filename}")
    print(f"📊 Found {len(player_data)} valid players")
    
    # Display top performers
    if len(player_data) > 0:
        print(f"\n📋 Top 10 Overall Performers:")
        df['points_numeric'] = pd.to_numeric(df['points'], errors='coerce')
        df_sorted = df.sort_values('points_numeric', ascending=False)
        for i, (_, row) in enumerate(df_sorted.head(10).iterrows(), 1):
            points = row['points'] if pd.notna(row['points']) else 'N/A'
            salary = row['salary'] if pd.notna(row['salary']) else 'N/A'
            print(f"  {i:2d}. {row['player_name']:<20} | {row['position']:<3} | {salary:<6} | {points:<6} pts")
    
    return df

def main():
    print("Yahoo Daily Fantasy Completed Page Scraper")
    print("=" * 60)
    print("This will scrape data from the completed games page:")
    print("https://sports.yahoo.com/dailyfantasy/research/completed")
    print("=" * 60)
    
    # Get week information
    week_info = get_week_info()
    print(f"📅 Scraping data for: {week_info}")
    
    # Scrape completed page data
    player_data = scrape_completed_page()
    
    if player_data:
        # Save completed data
        df = save_completed_data(player_data, week_info)
        
        if df is not None:
            print(f"\n🎉 SUCCESS! Scraped {len(df)} players for {week_info}")
            print(f"📁 Data saved to: yahoo_daily_fantasy_{week_info}_completed_page.csv")
            print(f"\n💡 Next step: Run the position parser on this file:")
            print(f"   python3 parse_players_by_position.py yahoo_daily_fantasy_{week_info}_completed_page.csv")
        else:
            print("\n❌ Failed to save data")
    else:
        print("\n❌ No data found")

if __name__ == "__main__":
    main()

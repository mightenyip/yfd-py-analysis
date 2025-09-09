#!/usr/bin/env python3
"""
Selenium scraper for Yahoo Daily Fantasy that interacts with position filter tabs.
This script clicks on different position filters and scrapes data for each position.
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

def find_position_filters(driver):
    """
    Find position filter buttons/tabs on the page.
    """
    print("🔍 Looking for position filter elements...")
    
    # Common selectors for position filters
    filter_selectors = [
        # Button-based filters
        "button[data-position]",
        "button[class*='position']",
        "button[class*='filter']",
        "a[data-position]",
        "a[class*='position']",
        "a[class*='filter']",
        
        # Tab-based filters
        "[role='tab']",
        ".tab",
        "[class*='tab']",
        
        # Dropdown filters
        "select[class*='position']",
        "select[class*='filter']",
        
        # Generic filter elements
        "[data-testid*='position']",
        "[data-testid*='filter']",
        "[aria-label*='position']",
        "[aria-label*='filter']",
        
        # Look for specific position text
        "button:contains('QB')",
        "button:contains('RB')",
        "button:contains('WR')",
        "button:contains('TE')",
        "a:contains('QB')",
        "a:contains('RB')",
        "a:contains('WR')",
        "a:contains('TE')",
    ]
    
    found_filters = []
    
    for selector in filter_selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            for element in elements:
                if element.is_displayed():
                    text = element.text.strip()
                    if text and any(pos in text.upper() for pos in ['QB', 'RB', 'WR', 'TE', 'K', 'DEF', 'ALL']):
                        found_filters.append({
                            'element': element,
                            'text': text,
                            'selector': selector
                        })
                        print(f"   Found filter: '{text}' with selector: {selector}")
        except Exception as e:
            continue
    
    # Also look for elements containing position text
    try:
        all_buttons = driver.find_elements(By.TAG_NAME, "button")
        all_links = driver.find_elements(By.TAG_NAME, "a")
        
        for element in all_buttons + all_links:
            if element.is_displayed():
                text = element.text.strip()
                if text in ['QB', 'RB', 'WR', 'TE', 'K', 'DEF', 'ALL', 'All']:
                    found_filters.append({
                        'element': element,
                        'text': text,
                        'selector': 'text_match'
                    })
                    print(f"   Found filter by text: '{text}'")
    except Exception as e:
        pass
    
    return found_filters

def extract_players_from_current_view(driver, position_name="ALL"):
    """
    Extract player data from the current view.
    """
    player_data = []
    
    try:
        # Wait for table to load
        wait = WebDriverWait(driver, 10)
        table = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table")))
        
        # Get all rows
        rows = table.find_elements(By.CSS_SELECTOR, "tr")
        print(f"   Found {len(rows)} rows for {position_name}")
        
        # Process rows (skip header)
        for i in range(1, len(rows)):
            try:
                row = rows[i]
                cells = row.find_elements(By.CSS_SELECTOR, "td, th, div[class*='cell'], span")
                
                if len(cells) >= 3:
                    row_data = {}
                    cell_texts = [cell.text.strip() for cell in cells if cell.text.strip()]
                    
                    if cell_texts:
                        row_data['raw_data'] = cell_texts
                        row_data['row_number'] = i
                        row_data['position_filter'] = position_name
                        
                        # Extract data
                        for text in cell_texts:
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
                continue
        
        print(f"   Extracted {len(player_data)} players for {position_name}")
        return player_data
        
    except Exception as e:
        print(f"   Error extracting data for {position_name}: {e}")
        return []

def scrape_by_position_filters():
    """
    Main function to scrape data by clicking position filters.
    """
    driver = setup_driver(headless=False)  # Keep visible to see what's happening
    if not driver:
        return {}
    
    all_position_data = {}
    
    try:
        url = "https://sports.yahoo.com/dailyfantasy/research/completed"
        print(f"🌐 Loading {url}...")
        driver.get(url)
        
        # Wait for page to load
        time.sleep(5)
        
        # Find position filters
        filters = find_position_filters(driver)
        
        if not filters:
            print("❌ No position filters found. Trying to extract all data...")
            all_data = extract_players_from_current_view(driver, "ALL")
            all_position_data["ALL"] = all_data
        else:
            print(f"✅ Found {len(filters)} position filters")
            
            # Extract data for each position filter
            for filter_info in filters:
                try:
                    element = filter_info['element']
                    position_name = filter_info['text']
                    
                    print(f"\n🔄 Clicking on {position_name} filter...")
                    
                    # Click the filter
                    driver.execute_script("arguments[0].click();", element)
                    time.sleep(3)  # Wait for data to load
                    
                    # Extract data
                    position_data = extract_players_from_current_view(driver, position_name)
                    all_position_data[position_name] = position_data
                    
                except Exception as e:
                    print(f"   Error with {position_name} filter: {e}")
                    continue
        
        return all_position_data
        
    except Exception as e:
        print(f"Error during scraping: {e}")
        return {}
    finally:
        input("Press Enter to close the browser...")
        driver.quit()

def save_position_data(all_position_data, output_dir='position_filtered_data'):
    """
    Save position-specific data to separate CSV files.
    """
    if not all_position_data:
        print("❌ No data to save")
        return []
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    created_files = []
    
    for position, data in all_position_data.items():
        if not data:
            continue
            
        # Clean the data
        cleaned_data = []
        for record in data:
            raw_data = record['raw_data']
            
            # Extract player name
            player_info = raw_data[2] if len(raw_data) > 2 else ""
            lines = player_info.split('\n')
            player_name = lines[0].strip() if lines else "Unknown"
            
            # Extract other data
            game_info = lines[1] if len(lines) > 1 else ""
            stats = lines[2] if len(lines) > 2 else ""
            
            # Find salary and points
            salary = None
            points = None
            for item in raw_data:
                if '$' in str(item) and str(item).replace('$', '').replace(',', '').isdigit():
                    salary = str(item)
                elif isinstance(item, str) and '.' in item:
                    try:
                        float(item)
                        if len(item) <= 6:
                            points = item
                    except ValueError:
                        continue
            
            if player_name and player_name != "Unknown" and len(player_name) > 2:
                cleaned_record = {
                    'player_name': player_name,
                    'position': record.get('position', position),
                    'game_info': game_info,
                    'stats': stats,
                    'salary': salary,
                    'points': points,
                    'filter_used': position
                }
                cleaned_data.append(cleaned_record)
        
        if cleaned_data:
            # Create DataFrame and save
            df = pd.DataFrame(cleaned_data)
            
            # Sort by points if available
            if 'points' in df.columns:
                df['points_numeric'] = pd.to_numeric(df['points'], errors='coerce')
                df = df.sort_values('points_numeric', ascending=False)
                df = df.drop('points_numeric', axis=1)
            
            # Save to CSV
            filename = f"{position.lower().replace(' ', '_')}_filtered.csv"
            output_file = os.path.join(output_dir, filename)
            df.to_csv(output_file, index=False)
            created_files.append(output_file)
            
            print(f"✅ Saved {len(cleaned_data)} {position} players to {output_file}")
            
            # Show top 5 players
            if len(cleaned_data) > 0:
                print(f"   Top 5 {position} players:")
                for i, (_, row) in enumerate(df.head(5).iterrows(), 1):
                    points = row['points'] if pd.notna(row['points']) else 'N/A'
                    salary = row['salary'] if pd.notna(row['salary']) else 'N/A'
                    print(f"     {i}. {row['player_name']:<20} | {salary:<6} | {points}")
    
    return created_files

def main():
    print("Yahoo Daily Fantasy Position Filter Scraper")
    print("=" * 50)
    print("This will interact with position filter tabs on the Yahoo page.")
    print("The browser will stay open so you can see what's happening.")
    print("=" * 50)
    
    # Scrape data by position filters
    all_position_data = scrape_by_position_filters()
    
    if all_position_data:
        # Save position-specific data
        created_files = save_position_data(all_position_data)
        
        if created_files:
            print(f"\n🎉 SUCCESS! Created {len(created_files)} position-specific files")
            print(f"📁 All files saved in: position_filtered_data/")
        else:
            print("\n❌ No files created")
    else:
        print("\n❌ No data found")

if __name__ == "__main__":
    main()

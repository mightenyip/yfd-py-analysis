#!/usr/bin/env python3
"""
Selenium scraper that specifically targets the correct columns on Yahoo Daily Fantasy.
This version focuses on getting the actual "Points" column, not "FPPG".
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

def analyze_table_structure(driver):
    """
    Analyze the table structure to identify the correct columns.
    """
    print("🔍 Analyzing table structure to find correct columns...")
    
    try:
        # Wait for table to load
        wait = WebDriverWait(driver, 15)
        table = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table")))
        
        # Get header row
        header_row = table.find_element(By.CSS_SELECTOR, "tr")
        header_cells = header_row.find_elements(By.CSS_SELECTOR, "th, td")
        
        print(f"Found {len(header_cells)} columns in header:")
        column_info = []
        
        for i, cell in enumerate(header_cells):
            text = cell.text.strip()
            column_info.append({
                'index': i,
                'text': text,
                'element': cell
            })
            print(f"   Column {i}: '{text}'")
        
        # Look for specific column patterns
        points_column = None
        fppg_column = None
        salary_column = None
        position_column = None
        player_column = None
        
        for col in column_info:
            text = col['text'].upper()
            if 'POINTS' in text and 'FPPG' not in text:
                points_column = col
                print(f"✅ Found Points column at index {col['index']}: '{col['text']}'")
            elif 'FPPG' in text:
                fppg_column = col
                print(f"📊 Found FPPG column at index {col['index']}: '{col['text']}'")
            elif 'SALARY' in text or '$' in text:
                salary_column = col
                print(f"💰 Found Salary column at index {col['index']}: '{col['text']}'")
            elif 'POS' in text or 'POSITION' in text:
                position_column = col
                print(f"🏈 Found Position column at index {col['index']}: '{col['text']}'")
            elif 'PLAYER' in text or 'NAME' in text:
                player_column = col
                print(f"👤 Found Player column at index {col['index']}: '{col['text']}'")
        
        return {
            'points_column': points_column,
            'fppg_column': fppg_column,
            'salary_column': salary_column,
            'position_column': position_column,
            'player_column': player_column,
            'total_columns': len(header_cells)
        }
        
    except Exception as e:
        print(f"Error analyzing table structure: {e}")
        return None

def extract_players_with_correct_columns(driver, column_info):
    """
    Extract player data using the identified correct columns.
    """
    player_data = []
    
    try:
        table = driver.find_element(By.CSS_SELECTOR, "table")
        rows = table.find_elements(By.CSS_SELECTOR, "tr")
        
        print(f"🔄 Processing {len(rows)-1} player rows...")
        
        # Process each row (skip header)
        for i in range(1, len(rows)):
            try:
                row = rows[i]
                cells = row.find_elements(By.CSS_SELECTOR, "td, th")
                
                if len(cells) >= column_info['total_columns']:
                    row_data = {}
                    
                    # Extract data from specific columns
                    if column_info['player_column']:
                        player_cell = cells[column_info['player_column']['index']]
                        row_data['player_name'] = player_cell.text.strip()
                    
                    if column_info['position_column']:
                        position_cell = cells[column_info['position_column']['index']]
                        row_data['position'] = position_cell.text.strip()
                    
                    if column_info['salary_column']:
                        salary_cell = cells[column_info['salary_column']['index']]
                        row_data['salary'] = salary_cell.text.strip()
                    
                    if column_info['points_column']:
                        points_cell = cells[column_info['points_column']['index']]
                        row_data['points'] = points_cell.text.strip()
                    
                    if column_info['fppg_column']:
                        fppg_cell = cells[column_info['fppg_column']['index']]
                        row_data['fppg'] = fppg_cell.text.strip()
                    
                    # Get all cell data for debugging
                    row_data['all_cells'] = [cell.text.strip() for cell in cells]
                    row_data['row_number'] = i
                    
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

def scrape_with_correct_columns():
    """
    Main function to scrape data with correct column identification.
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
        
        # Analyze table structure
        column_info = analyze_table_structure(driver)
        
        if not column_info:
            print("❌ Could not analyze table structure")
            return []
        
        # Extract player data
        player_data = extract_players_with_correct_columns(driver, column_info)
        
        return player_data
        
    except Exception as e:
        print(f"Error during scraping: {e}")
        return []
    finally:
        input("Press Enter to close the browser...")
        driver.quit()

def save_corrected_data(player_data, filename="yahoo_daily_fantasy_corrected_columns.csv"):
    """Save the data with correct column mapping."""
    if not player_data:
        print("❌ No data to save")
        return None
    
    print(f"🧹 Processing {len(player_data)} player records...")
    
    cleaned_data = []
    
    for record in player_data:
        # Clean player name (remove game info if present)
        player_name = record.get('player_name', 'Unknown')
        if '\n' in player_name:
            player_name = player_name.split('\n')[0].strip()
        
        # Clean position
        position = record.get('position', 'Unknown')
        
        # Clean salary
        salary = record.get('salary', '')
        
        # Clean points (this should be the actual points, not FPPG)
        points = record.get('points', '')
        
        # Clean FPPG (season average)
        fppg = record.get('fppg', '')
        
        # Only include if we have a valid player name
        if player_name and player_name != "Unknown" and len(player_name) > 2:
            cleaned_record = {
                'player_name': player_name,
                'position': position,
                'salary': salary,
                'points': points,
                'fppg': fppg,
                'all_cells': record.get('all_cells', [])
            }
            cleaned_data.append(cleaned_record)
    
    # Create and save DataFrame
    df = pd.DataFrame(cleaned_data)
    df.to_csv(filename, index=False)
    
    print(f"✅ Corrected data saved to {filename}")
    print(f"📊 Found {len(cleaned_data)} valid players")
    
    # Display summary
    if len(cleaned_data) > 0:
        print(f"\n📋 Sample of corrected data:")
        for i, (_, row) in enumerate(df.head(10).iterrows(), 1):
            points = row['points'] if pd.notna(row['points']) else 'N/A'
            fppg = row['fppg'] if pd.notna(row['fppg']) else 'N/A'
            salary = row['salary'] if pd.notna(row['salary']) else 'N/A'
            print(f"  {i:2d}. {row['player_name']:<20} | {row['position']:<3} | {salary:<6} | Points: {points:<6} | FPPG: {fppg}")
        
        # Check for Anthony Richardson specifically
        anthony = df[df['player_name'].str.contains('Anthony Richardson', case=False, na=False)]
        if len(anthony) > 0:
            print(f"\n🔍 Anthony Richardson data:")
            for _, row in anthony.iterrows():
                print(f"   {row['player_name']} | Points: {row['points']} | FPPG: {row['fppg']}")
    
    return df

def main():
    print("Yahoo Daily Fantasy Correct Columns Scraper")
    print("=" * 50)
    print("This will identify and extract the correct Points column (not FPPG).")
    print("The browser will stay open so you can see the column analysis.")
    print("=" * 50)
    
    # Scrape data with correct column identification
    player_data = scrape_with_correct_columns()
    
    if player_data:
        # Save corrected data
        df = save_corrected_data(player_data)
        
        if df is not None:
            print(f"\n🎉 SUCCESS! Scraped {len(df)} players with correct columns")
            print("📁 Data saved to: yahoo_daily_fantasy_corrected_columns.csv")
        else:
            print("\n❌ Failed to save data")
    else:
        print("\n❌ No data found")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Script to scrape Yahoo Daily Fantasy player data from the research page.
Note: This is for educational purposes. Always check Yahoo's terms of service.
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import time

def scrape_yahoo_daily_fantasy_data():
    """
    Scrape player data from Yahoo Daily Fantasy research page.
    """
    url = "https://sports.yahoo.com/dailyfantasy/research/completed"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        print("Fetching Yahoo Daily Fantasy data...")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for data tables or JSON data in the page
        # Yahoo often loads data dynamically via JavaScript, so we might need to look for script tags
        scripts = soup.find_all('script')
        
        player_data = []
        
        for script in scripts:
            if script.string and 'player' in script.string.lower():
                try:
                    # Try to extract JSON data from script tags
                    script_content = script.string
                    if 'window.__INITIAL_STATE__' in script_content or 'window.__PRELOADED_STATE__' in script_content:
                        print("Found potential data in script tag")
                        # You would need to parse this JSON data here
                        break
                except:
                    continue
        
        # Alternative: Look for table elements
        tables = soup.find_all('table')
        if tables:
            print(f"Found {len(tables)} table(s) on the page")
            for i, table in enumerate(tables):
                print(f"Table {i+1}:")
                rows = table.find_all('tr')
                for row in rows[:5]:  # Show first 5 rows
                    cells = row.find_all(['td', 'th'])
                    row_data = [cell.get_text(strip=True) for cell in cells]
                    print(f"  {row_data}")
        
        # Look for div elements that might contain player data
        player_divs = soup.find_all('div', class_=lambda x: x and 'player' in x.lower())
        if player_divs:
            print(f"Found {len(player_divs)} player-related divs")
        
        return player_data
        
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return []
    except Exception as e:
        print(f"Error parsing data: {e}")
        return []

def save_data_to_csv(data, filename="yahoo_daily_fantasy_data.csv"):
    """Save scraped data to CSV file."""
    if data:
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        print(f"Data saved to {filename}")
    else:
        print("No data to save")

if __name__ == "__main__":
    print("Yahoo Daily Fantasy Data Scraper")
    print("=" * 40)
    
    # Note: This is a basic example. Yahoo's site likely uses dynamic loading
    # You might need Selenium or similar tools for full functionality
    data = scrape_yahoo_daily_fantasy_data()
    
    if data:
        save_data_to_csv(data)
    else:
        print("No data found. The page might use dynamic loading.")
        print("Consider using Selenium WebDriver for JavaScript-heavy sites.")

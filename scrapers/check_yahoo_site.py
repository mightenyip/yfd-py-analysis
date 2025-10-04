#!/usr/bin/env python3
"""
Simple script to check what's available on Yahoo's daily fantasy site.
"""

import requests
from bs4 import BeautifulSoup
import time

def check_yahoo_site():
    """Check what's available on Yahoo's daily fantasy site."""
    
    url = "https://sports.yahoo.com/dailyfantasy/research/completed"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    try:
        print(f"🌐 Checking: {url}")
        response = requests.get(url, headers=headers, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Content Length: {len(response.content)}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Check for any tables
            tables = soup.find_all('table')
            print(f"📊 Found {len(tables)} table(s)")
            
            # Check for any divs with player-related classes
            player_divs = soup.find_all('div', class_=lambda x: x and any(word in x.lower() for word in ['player', 'fantasy', 'research']))
            print(f"👥 Found {len(player_divs)} player-related divs")
            
            # Check for any script tags that might contain data
            scripts = soup.find_all('script')
            print(f"📜 Found {len(scripts)} script tags")
            
            # Look for any text that might indicate data availability
            page_text = soup.get_text().lower()
            if 'week 5' in page_text:
                print("✅ Found 'Week 5' in page text")
            if 'thursday' in page_text:
                print("✅ Found 'Thursday' in page text")
            if '49ers' in page_text or 'rams' in page_text:
                print("✅ Found team names in page text")
            
            # Check for any error messages
            if 'error' in page_text or 'not found' in page_text:
                print("❌ Found error messages in page text")
            
            # Show first few lines of the page
            print("\n📄 First 500 characters of page:")
            print(response.text[:500])
            
        else:
            print(f"❌ Failed to access site: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("Yahoo Daily Fantasy Site Checker")
    print("=" * 40)
    check_yahoo_site()

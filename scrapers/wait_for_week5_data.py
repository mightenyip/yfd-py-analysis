#!/usr/bin/env python3
"""
Script to wait for Week 5 Thursday data to become available.
"""

import time
import requests
from datetime import datetime

def check_for_week5_data():
    """Check if Week 5 Thursday data is available."""
    
    url = "https://sports.yahoo.com/dailyfantasy/research/completed"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            page_text = response.text.lower()
            
            # Check for Week 5 indicators
            week5_indicators = ['week 5', 'week5', 'thursday', '49ers', 'rams', 'san francisco', 'los angeles']
            found_indicators = [indicator for indicator in week5_indicators if indicator in page_text]
            
            if found_indicators:
                print(f"✅ Found indicators: {found_indicators}")
                return True
            else:
                print("❌ No Week 5 indicators found")
                return False
        else:
            print(f"❌ Failed to access site: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("Waiting for Week 5 Thursday data to become available...")
    print("Targeting: 49ers vs Rams on 10/2/25")
    print("=" * 50)
    
    max_attempts = 10
    attempt = 0
    
    while attempt < max_attempts:
        attempt += 1
        print(f"\n🔄 Attempt {attempt}/{max_attempts} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if check_for_week5_data():
            print("🎉 Week 5 Thursday data appears to be available!")
            print("You can now try running the scraper again.")
            break
        else:
            if attempt < max_attempts:
                print("⏳ Data not available yet, waiting 5 minutes...")
                time.sleep(300)  # Wait 5 minutes
            else:
                print("❌ Data still not available after maximum attempts")
                print("The data might not be processed yet or there might be access issues.")
                print("You may need to wait longer or check if there are authentication requirements.")

if __name__ == "__main__":
    main()

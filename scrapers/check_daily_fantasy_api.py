#!/usr/bin/env python3
"""
Script to check for potential Yahoo Daily Fantasy API endpoints.
"""

import requests
import json
import time

def check_api_endpoints():
    """
    Check for potential API endpoints that might provide Daily Fantasy data.
    """
    
    # Common API endpoint patterns for Yahoo
    potential_endpoints = [
        "https://sports.yahoo.com/dailyfantasy/api/research/completed",
        "https://sports.yahoo.com/dailyfantasy/api/players",
        "https://sports.yahoo.com/dailyfantasy/api/contests",
        "https://sports.yahoo.com/dailyfantasy/api/lineups",
        "https://sports.yahoo.com/dailyfantasy/api/games",
        "https://sports.yahoo.com/dailyfantasy/api/player-stats",
        "https://sports.yahoo.com/dailyfantasy/api/research/players",
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://sports.yahoo.com/dailyfantasy/research/completed'
    }
    
    working_endpoints = []
    
    for endpoint in potential_endpoints:
        try:
            print(f"Checking: {endpoint}")
            response = requests.get(endpoint, headers=headers, timeout=5)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"✅ Found working endpoint: {endpoint}")
                    print(f"   Response type: {type(data)}")
                    if isinstance(data, dict):
                        print(f"   Keys: {list(data.keys())[:5]}")  # Show first 5 keys
                    elif isinstance(data, list):
                        print(f"   List length: {len(data)}")
                    working_endpoints.append(endpoint)
                except json.JSONDecodeError:
                    print(f"   Response is not JSON: {response.text[:100]}...")
            else:
                print(f"   Status: {response.status_code}")
                
        except requests.RequestException as e:
            print(f"   Error: {e}")
        
        time.sleep(0.5)  # Be respectful with requests
    
    return working_endpoints

def check_network_requests():
    """
    Instructions for checking network requests in browser dev tools.
    """
    print("\n" + "="*60)
    print("MANUAL METHOD: Check Browser Network Tab")
    print("="*60)
    print("1. Open https://sports.yahoo.com/dailyfantasy/research/completed")
    print("2. Open browser Developer Tools (F12)")
    print("3. Go to Network tab")
    print("4. Refresh the page")
    print("5. Look for XHR/Fetch requests that return JSON data")
    print("6. Common patterns to look for:")
    print("   - Requests to /api/ endpoints")
    print("   - Requests with 'player', 'research', 'dailyfantasy' in URL")
    print("   - JSON responses with player data")
    print("7. Copy the request URL and headers for use in your script")

if __name__ == "__main__":
    print("Yahoo Daily Fantasy API Endpoint Checker")
    print("=" * 50)
    
    endpoints = check_api_endpoints()
    
    if endpoints:
        print(f"\n✅ Found {len(endpoints)} working endpoints:")
        for endpoint in endpoints:
            print(f"   - {endpoint}")
    else:
        print("\n❌ No obvious API endpoints found")
        print("The data is likely loaded dynamically via JavaScript")
    
    check_network_requests()

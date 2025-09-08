#!/usr/bin/env python3
"""
Comprehensive investigation of Yahoo Daily Fantasy data loading methods.
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import time

def investigate_page_source():
    """
    Look for embedded JSON data in the page source.
    """
    url = "https://sports.yahoo.com/dailyfantasy/research/completed"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        print("🔍 Investigating page source for embedded data...")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for script tags with potential data
        scripts = soup.find_all('script')
        print(f"Found {len(scripts)} script tags")
        
        data_found = False
        
        for i, script in enumerate(scripts):
            if script.string:
                script_content = script.string
                
                # Look for common patterns
                patterns = [
                    r'window\.__INITIAL_STATE__\s*=\s*({.*?});',
                    r'window\.__PRELOADED_STATE__\s*=\s*({.*?});',
                    r'window\.__APOLLO_STATE__\s*=\s*({.*?});',
                    r'window\.__NEXT_DATA__\s*=\s*({.*?});',
                    r'window\.__NUXT__\s*=\s*({.*?});',
                    r'window\.__DATA__\s*=\s*({.*?});',
                    r'window\.fantasyData\s*=\s*({.*?});',
                    r'window\.playerData\s*=\s*({.*?});',
                    r'window\.dailyFantasyData\s*=\s*({.*?});',
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, script_content, re.DOTALL)
                    if matches:
                        print(f"✅ Found data in script {i+1} with pattern: {pattern}")
                        try:
                            data = json.loads(matches[0])
                            print(f"   Data type: {type(data)}")
                            if isinstance(data, dict):
                                print(f"   Keys: {list(data.keys())[:10]}")
                            data_found = True
                        except json.JSONDecodeError:
                            print(f"   JSON decode error for pattern: {pattern}")
                
                # Look for any JSON-like structures
                json_pattern = r'\{[^{}]*"[^"]*player[^"]*"[^{}]*\}'
                json_matches = re.findall(json_pattern, script_content, re.IGNORECASE)
                if json_matches:
                    print(f"   Found {len(json_matches)} potential JSON objects with 'player'")
                    for match in json_matches[:3]:  # Show first 3
                        print(f"   Sample: {match[:100]}...")
        
        if not data_found:
            print("❌ No embedded JSON data found in script tags")
        
        return data_found
        
    except Exception as e:
        print(f"Error investigating page source: {e}")
        return False

def check_graphql_endpoints():
    """
    Check for GraphQL endpoints that might be used.
    """
    print("\n🔍 Checking for GraphQL endpoints...")
    
    potential_graphql_urls = [
        "https://sports.yahoo.com/graphql",
        "https://sports.yahoo.com/api/graphql",
        "https://sports.yahoo.com/dailyfantasy/graphql",
        "https://sports.yahoo.com/dailyfantasy/api/graphql",
        "https://query.sports.yahoo.com/v1/graphql",
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Content-Type': 'application/json',
    }
    
    # Sample GraphQL query for player data
    sample_query = {
        "query": """
        query {
            players {
                id
                name
                position
                salary
                points
            }
        }
        """
    }
    
    for url in potential_graphql_urls:
        try:
            print(f"Testing: {url}")
            response = requests.post(url, json=sample_query, headers=headers, timeout=5)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"✅ GraphQL endpoint found: {url}")
                    print(f"   Response: {data}")
                    return url
                except json.JSONDecodeError:
                    print(f"   Response not JSON: {response.text[:100]}")
            else:
                print(f"   Status: {response.status_code}")
                
        except requests.RequestException as e:
            print(f"   Error: {e}")
    
    print("❌ No GraphQL endpoints found")
    return None

def check_websocket_connections():
    """
    Instructions for checking WebSocket connections.
    """
    print("\n🔍 WebSocket Connection Check")
    print("=" * 40)
    print("1. Open https://sports.yahoo.com/dailyfantasy/research/completed")
    print("2. Open Developer Tools (F12)")
    print("3. Go to Network tab")
    print("4. Filter by 'WS' (WebSocket)")
    print("5. Refresh the page")
    print("6. Look for WebSocket connections")
    print("7. Click on any WebSocket connection to see messages")
    print("8. Look for messages containing player data")

def check_alternative_urls():
    """
    Check alternative URL patterns that might contain the data.
    """
    print("\n🔍 Checking alternative URL patterns...")
    
    base_urls = [
        "https://sports.yahoo.com/dailyfantasy/research/",
        "https://sports.yahoo.com/dailyfantasy/api/",
        "https://sports.yahoo.com/dailyfantasy/data/",
        "https://sports.yahoo.com/dailyfantasy/players/",
    ]
    
    endpoints = [
        "players",
        "research",
        "completed",
        "live",
        "upcoming",
        "stats",
        "lineups",
        "contests",
        "games",
        "data",
        "api/players",
        "api/research",
        "api/stats",
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'application/json, text/plain, */*',
    }
    
    working_urls = []
    
    for base_url in base_urls:
        for endpoint in endpoints:
            url = base_url + endpoint
            try:
                response = requests.get(url, headers=headers, timeout=3)
                
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '')
                    if 'json' in content_type:
                        try:
                            data = response.json()
                            print(f"✅ Found JSON endpoint: {url}")
                            print(f"   Content-Type: {content_type}")
                            if isinstance(data, dict):
                                print(f"   Keys: {list(data.keys())[:5]}")
                            elif isinstance(data, list):
                                print(f"   List length: {len(data)}")
                            working_urls.append(url)
                        except json.JSONDecodeError:
                            pass
                    elif 'html' not in content_type:
                        print(f"   Non-HTML response: {url} ({content_type})")
                        
            except requests.RequestException:
                pass
            
            time.sleep(0.1)  # Be respectful
    
    return working_urls

def main():
    print("Yahoo Daily Fantasy Data Investigation")
    print("=" * 50)
    
    # Check page source for embedded data
    found_embedded = investigate_page_source()
    
    # Check GraphQL endpoints
    graphql_url = check_graphql_endpoints()
    
    # Check alternative URLs
    working_urls = check_alternative_urls()
    
    # WebSocket instructions
    check_websocket_connections()
    
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    
    if found_embedded:
        print("✅ Found embedded data in page source")
    else:
        print("❌ No embedded data found")
    
    if graphql_url:
        print(f"✅ Found GraphQL endpoint: {graphql_url}")
    else:
        print("❌ No GraphQL endpoints found")
    
    if working_urls:
        print(f"✅ Found {len(working_urls)} working API endpoints")
        for url in working_urls:
            print(f"   - {url}")
    else:
        print("❌ No working API endpoints found")
    
    print("\n💡 RECOMMENDATIONS:")
    print("1. Check WebSocket connections in browser dev tools")
    print("2. Look for any requests to 'sports.yahoo.com' in Network tab")
    print("3. Check if data is loaded via iframe or embedded widget")
    print("4. Consider using Selenium to interact with the page")

if __name__ == "__main__":
    main()

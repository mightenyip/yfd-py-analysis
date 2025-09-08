#!/usr/bin/env python3
"""
Clean and parse the Yahoo Daily Fantasy data that was scraped.
"""

import pandas as pd
import re
import json

def clean_player_data():
    """
    Clean the scraped Yahoo Daily Fantasy data.
    """
    try:
        # Read the raw data
        df = pd.read_csv('yahoo_daily_fantasy_players.csv')
        print(f"📊 Loaded {len(df)} raw records")
        
        cleaned_data = []
        
        for index, row in df.iterrows():
            raw_data = eval(row['raw_data'])  # Convert string back to list
            
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
            position = row['position'] if pd.notna(row['position']) else "Unknown"
            
            # Only include if we have a valid player name
            if player_name and player_name != "Unknown" and len(player_name) > 2:
                cleaned_record = {
                    'player_name': player_name,
                    'position': position,
                    'game_info': game_info,
                    'stats': stats,
                    'salary': salary,
                    'points': points,
                    'raw_data': raw_data
                }
                cleaned_data.append(cleaned_record)
        
        # Create cleaned DataFrame
        cleaned_df = pd.DataFrame(cleaned_data)
        
        # Save cleaned data
        cleaned_df.to_csv('yahoo_daily_fantasy_cleaned.csv', index=False)
        
        print(f"✅ Cleaned data saved to yahoo_daily_fantasy_cleaned.csv")
        print(f"📊 Found {len(cleaned_df)} valid players")
        
        # Display sample of cleaned data
        print("\n📋 Sample of cleaned data:")
        for i, row in cleaned_df.head(10).iterrows():
            print(f"{i+1:2d}. {row['player_name']:<20} | {row['position']:<3} | {row['salary']:<6} | {row['points']}")
        
        return cleaned_df
        
    except Exception as e:
        print(f"Error cleaning data: {e}")
        return None

def create_summary_report(df):
    """
    Create a summary report of the data.
    """
    if df is None or len(df) == 0:
        print("❌ No data to summarize")
        return
    
    print("\n" + "="*60)
    print("📊 YAHOO DAILY FANTASY DATA SUMMARY")
    print("="*60)
    
    # Position breakdown
    print(f"\n🏈 Players by Position:")
    position_counts = df['position'].value_counts()
    for pos, count in position_counts.items():
        print(f"   {pos}: {count} players")
    
    # Top players by points
    print(f"\n⭐ Top 10 Players by Points:")
    top_players = df.sort_values('points', ascending=False, na_position='last').head(10)
    for i, (_, row) in enumerate(top_players.iterrows(), 1):
        points = row['points'] if pd.notna(row['points']) else "N/A"
        salary = row['salary'] if pd.notna(row['salary']) else "N/A"
        print(f"   {i:2d}. {row['player_name']:<20} | {points:<6} | {salary}")
    
    # Salary analysis
    print(f"\n💰 Salary Analysis:")
    salaries = df['salary'].dropna()
    if len(salaries) > 0:
        # Extract numeric values from salary strings
        numeric_salaries = []
        for salary in salaries:
            try:
                numeric = float(salary.replace('$', '').replace(',', ''))
                numeric_salaries.append(numeric)
            except:
                continue
        
        if numeric_salaries:
            print(f"   Average Salary: ${sum(numeric_salaries)/len(numeric_salaries):.2f}")
            print(f"   Highest Salary: ${max(numeric_salaries):.2f}")
            print(f"   Lowest Salary: ${min(numeric_salaries):.2f}")
    
    # Points analysis
    print(f"\n📈 Points Analysis:")
    points = df['points'].dropna()
    if len(points) > 0:
        numeric_points = []
        for point in points:
            try:
                numeric_points.append(float(point))
            except:
                continue
        
        if numeric_points:
            print(f"   Average Points: {sum(numeric_points)/len(numeric_points):.2f}")
            print(f"   Highest Points: {max(numeric_points):.2f}")
            print(f"   Lowest Points: {min(numeric_points):.2f}")

def main():
    print("🧹 Yahoo Daily Fantasy Data Cleaner")
    print("="*50)
    
    # Clean the data
    cleaned_df = clean_player_data()
    
    if cleaned_df is not None:
        # Create summary report
        create_summary_report(cleaned_df)
        
        print(f"\n✅ SUCCESS!")
        print(f"📁 Raw data: yahoo_daily_fantasy_players.csv")
        print(f"📁 Cleaned data: yahoo_daily_fantasy_cleaned.csv")
        print(f"📊 Total players found: {len(cleaned_df)}")
    else:
        print("❌ Failed to clean data")

if __name__ == "__main__":
    main()

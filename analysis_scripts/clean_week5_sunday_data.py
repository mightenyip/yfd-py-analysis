#!/usr/bin/env python3
"""
Clean Week 5 Sunday data to remove duplicates and sort by points.
"""

import pandas as pd
import numpy as np
from pathlib import Path

def clean_week5_sunday_data():
    """Clean the Week 5 Sunday all games data"""
    
    # Load the data
    data_dir = Path('/Users/mightenyip/Documents/GitHub/yfd-py-test/data_csv')
    input_file = data_dir / 'week5_Sunday_all_games.csv'
    
    if not input_file.exists():
        print(f"❌ File not found: {input_file}")
        return None
    
    print(f"📂 Loading data from {input_file}")
    df = pd.read_csv(input_file)
    print(f"📊 Original data: {len(df)} records")
    
    # Convert points to numeric for proper sorting
    df['points_clean'] = pd.to_numeric(df['points'], errors='coerce')
    df['salary_clean'] = df['salary'].astype(str).str.replace('$', '').str.replace(',', '')
    df['salary_clean'] = pd.to_numeric(df['salary_clean'], errors='coerce')
    
    # Remove rows with missing points
    df_clean = df.dropna(subset=['points_clean'])
    print(f"🧹 After removing missing points: {len(df_clean)} records")
    
    # Check for duplicates by player name
    print(f"\n🔍 Checking for duplicates...")
    duplicates = df_clean.duplicated(subset=['player_name'], keep=False)
    if duplicates.any():
        print(f"Found {duplicates.sum()} duplicate player records")
        
        # Show examples of duplicates
        duplicate_examples = df_clean[duplicates].groupby('player_name').size().head(10)
        print("Example duplicates:")
        for player, count in duplicate_examples.items():
            print(f"  {player}: {count} records")
        
        # For duplicates, keep the record with the highest points
        print(f"\n🎯 Keeping highest scoring record for each duplicate player...")
        df_unique = df_clean.sort_values('points_clean', ascending=False).drop_duplicates(subset=['player_name'], keep='first')
        print(f"After removing duplicates: {len(df_unique)} records")
    else:
        print("✅ No duplicates found")
        df_unique = df_clean
    
    # Sort by points from highest to lowest
    print(f"\n📊 Sorting by points (highest to lowest)...")
    df_sorted = df_unique.sort_values('points_clean', ascending=False).reset_index(drop=True)
    
    # Add ranking
    df_sorted['rank'] = range(1, len(df_sorted) + 1)
    
    # Save the cleaned data
    output_file = data_dir / 'week5_Sunday_clean.csv'
    df_sorted.to_csv(output_file, index=False)
    
    print(f"✅ Cleaned data saved to {output_file}")
    print(f"📊 Final data: {len(df_sorted)} unique players")
    
    # Display summary
    print(f"\n📋 Top 20 Players by Points:")
    print("-" * 80)
    for i, (_, row) in enumerate(df_sorted.head(20).iterrows(), 1):
        points = row['points_clean'] if pd.notna(row['points_clean']) else 0
        salary = row['salary_clean'] if pd.notna(row['salary_clean']) else 0
        points_per_dollar = points / salary if salary > 0 else 0
        game_time = row['game_time'] if pd.notna(row['game_time']) else 'Unknown'
        print(f"{i:2d}. {row['player_name']:<25} ({row['position']:>2}) "
              f"${salary:>3} → {points:>6.1f} pts ({points_per_dollar:.3f} pts/$) - {game_time}")
    
    # Show position breakdown
    print(f"\n📊 Position Breakdown:")
    position_counts = df_sorted['position'].value_counts()
    for pos, count in position_counts.items():
        print(f"   {pos}: {count} players")
    
    # Show game time breakdown
    print(f"\n📊 Game Time Breakdown:")
    game_time_counts = df_sorted['game_time'].value_counts()
    for game_time, count in game_time_counts.items():
        print(f"   {game_time}: {count} players")
    
    # Show players with 0 points
    zero_points = df_sorted[df_sorted['points_clean'] == 0]
    if len(zero_points) > 0:
        print(f"\n📊 Players with 0 points: {len(zero_points)}")
        for _, row in zero_points.head(10).iterrows():
            print(f"   {row['player_name']} ({row['position']}) - {row['game_time']}")
    
    return df_sorted

def main():
    print("Week 5 Sunday Data Cleaner")
    print("=" * 50)
    print("This will remove duplicates and sort by points (highest to lowest)")
    print("=" * 50)
    
    df_clean = clean_week5_sunday_data()
    
    if df_clean is not None:
        print(f"\n🎉 SUCCESS! Cleaned Week 5 Sunday data")
        print("📁 Clean data saved to: data_csv/week5_Sunday_clean.csv")
    else:
        print("\n❌ Failed to clean data")

if __name__ == "__main__":
    main()

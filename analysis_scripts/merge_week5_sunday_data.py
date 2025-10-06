#!/usr/bin/env python3
"""
Merge Week 5 Sunday data - combine week5_Sunday.csv with week5_Sunday_clean.csv
Keep the early Sunday players from week5_Sunday.csv and add the cleaned data from week5_Sunday_clean.csv
"""

import pandas as pd
import numpy as np
from pathlib import Path

def merge_week5_sunday_data():
    """Merge the Week 5 Sunday data files"""
    
    data_dir = Path('/Users/mightenyip/Documents/GitHub/yfd-py-test/data_csv')
    
    # Load the original early Sunday data
    early_file = data_dir / 'week5_Sunday.csv'
    if not early_file.exists():
        print(f"❌ File not found: {early_file}")
        return None
    
    print(f"📂 Loading early Sunday data from {early_file}")
    df_early = pd.read_csv(early_file)
    print(f"📊 Early Sunday data: {len(df_early)} records")
    
    # Load the cleaned all games data
    clean_file = data_dir / 'week5_Sunday_clean.csv'
    if not clean_file.exists():
        print(f"❌ File not found: {clean_file}")
        return None
    
    print(f"📂 Loading cleaned all games data from {clean_file}")
    df_clean = pd.read_csv(clean_file)
    print(f"📊 Cleaned all games data: {len(df_clean)} records")
    
    # Convert points to numeric for both datasets
    df_early['points_clean'] = pd.to_numeric(df_early['points'], errors='coerce')
    df_clean['points_clean'] = pd.to_numeric(df_clean['points'], errors='coerce')
    
    # Convert salary to numeric for both datasets
    df_early['salary_clean'] = df_early['salary'].astype(str).str.replace('$', '').str.replace(',', '')
    df_early['salary_clean'] = pd.to_numeric(df_early['salary_clean'], errors='coerce')
    
    df_clean['salary_clean'] = df_clean['salary'].astype(str).str.replace('$', '').str.replace(',', '')
    df_clean['salary_clean'] = pd.to_numeric(df_clean['salary_clean'], errors='coerce')
    
    # Add game_time column to early data if it doesn't exist
    if 'game_time' not in df_early.columns:
        df_early['game_time'] = 'Early Sunday Game'
    
    # Check for overlapping players
    early_players = set(df_early['player_name'].unique())
    clean_players = set(df_clean['player_name'].unique())
    overlap = early_players.intersection(clean_players)
    
    print(f"\n🔍 Checking for overlapping players...")
    print(f"Early Sunday players: {len(early_players)}")
    print(f"Cleaned all games players: {len(clean_players)}")
    print(f"Overlapping players: {len(overlap)}")
    
    if overlap:
        print(f"Overlapping players: {sorted(list(overlap))}")
        
        # For overlapping players, keep the one with higher points
        print(f"\n🎯 Resolving overlaps by keeping higher scoring records...")
        
        # Create a combined dataset for overlap resolution
        df_combined = pd.concat([df_early, df_clean], ignore_index=True)
        
        # For each overlapping player, keep the record with higher points
        df_resolved = df_combined.sort_values('points_clean', ascending=False).drop_duplicates(subset=['player_name'], keep='first')
        
        print(f"After resolving overlaps: {len(df_resolved)} records")
    else:
        print("✅ No overlapping players found - can merge directly")
        df_resolved = pd.concat([df_early, df_clean], ignore_index=True)
    
    # Sort by points from highest to lowest
    print(f"\n📊 Sorting by points (highest to lowest)...")
    df_final = df_resolved.sort_values('points_clean', ascending=False).reset_index(drop=True)
    
    # Add ranking
    df_final['rank'] = range(1, len(df_final) + 1)
    
    # Save the merged data
    output_file = data_dir / 'week5_Sunday_merged.csv'
    df_final.to_csv(output_file, index=False)
    
    print(f"✅ Merged data saved to {output_file}")
    print(f"📊 Final merged data: {len(df_final)} unique players")
    
    # Display summary
    print(f"\n📋 Top 20 Players by Points:")
    print("-" * 80)
    for i, (_, row) in enumerate(df_final.head(20).iterrows(), 1):
        points = row['points_clean'] if pd.notna(row['points_clean']) else 0
        salary = row['salary_clean'] if pd.notna(row['salary_clean']) else 0
        points_per_dollar = points / salary if salary > 0 else 0
        game_time = row['game_time'] if pd.notna(row['game_time']) else 'Unknown'
        print(f"{i:2d}. {row['player_name']:<25} ({row['position']:>2}) "
              f"${salary:>3} → {points:>6.1f} pts ({points_per_dollar:.3f} pts/$) - {game_time}")
    
    # Show position breakdown
    print(f"\n📊 Position Breakdown:")
    position_counts = df_final['position'].value_counts()
    for pos, count in position_counts.items():
        print(f"   {pos}: {count} players")
    
    # Show game time breakdown
    print(f"\n📊 Game Time Breakdown:")
    game_time_counts = df_final['game_time'].value_counts()
    for game_time, count in game_time_counts.items():
        print(f"   {game_time}: {count} players")
    
    # Show data source breakdown
    print(f"\n📊 Data Source Breakdown:")
    early_count = len(df_final[df_final['game_time'] == 'Early Sunday Game'])
    clean_count = len(df_final[df_final['game_time'] != 'Early Sunday Game'])
    print(f"   Early Sunday Game: {early_count} players")
    print(f"   All Games (cleaned): {clean_count} players")
    
    return df_final

def main():
    print("Week 5 Sunday Data Merger")
    print("=" * 50)
    print("This will merge week5_Sunday.csv with week5_Sunday_clean.csv")
    print("Keeping early Sunday players and adding cleaned all games data")
    print("=" * 50)
    
    df_merged = merge_week5_sunday_data()
    
    if df_merged is not None:
        print(f"\n🎉 SUCCESS! Merged Week 5 Sunday data")
        print("📁 Merged data saved to: data_csv/week5_Sunday_merged.csv")
    else:
        print("\n❌ Failed to merge data")

if __name__ == "__main__":
    main()

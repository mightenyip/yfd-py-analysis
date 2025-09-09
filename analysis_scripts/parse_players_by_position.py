#!/usr/bin/env python3
"""
Parse Yahoo Daily Fantasy cleaned data into position-specific files.
This script will read the cleaned CSV and create separate files for each position.
"""

import pandas as pd
import os
import re
from pathlib import Path

def parse_players_by_position(input_file="yahoo_daily_fantasy_cleaned.csv", output_dir="position_data"):
    """
    Parse the cleaned fantasy data into position-specific CSV files.
    
    Args:
        input_file (str): Path to the input CSV file
        output_dir (str): Directory to save position-specific files
    """
    
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(exist_ok=True)
    
    print("🏈 Yahoo Daily Fantasy Position Parser")
    print("=" * 50)
    
    # Read the cleaned data with proper handling of multiline entries
    try:
        # Try reading with different parameters to handle multiline entries
        df = pd.read_csv(input_file, quoting=1, escapechar='\\', on_bad_lines='skip')
        print(f"✅ Loaded {len(df)} players from {input_file}")
    except Exception as e:
        print(f"⚠️  First attempt failed: {e}")
        try:
            # Try with different quoting
            df = pd.read_csv(input_file, quoting=3, on_bad_lines='skip')
            print(f"✅ Loaded {len(df)} players from {input_file} (second attempt)")
        except Exception as e2:
            print(f"❌ Error reading file: {e2}")
            return
    
    # Display basic info about the data
    print(f"📊 Data columns: {list(df.columns)}")
    print(f"📊 Total players: {len(df)}")
    
    # Check for position column
    if 'position' not in df.columns:
        print("❌ Error: No 'position' column found in the data")
        return
    
    # Clean the data - handle any parsing issues
    df = df.dropna(subset=['position'])  # Remove rows with missing positions
    df = df[df['position'].str.len() <= 10]  # Remove rows where position seems to be corrupted (too long)
    
    # Clean position names - extract just the position abbreviation
    def clean_position(pos):
        if pd.isna(pos):
            return None
        pos_str = str(pos).strip()
        # Look for standard position abbreviations
        for standard_pos in ['QB', 'RB', 'WR', 'TE', 'K', 'DEF']:
            if standard_pos in pos_str:
                return standard_pos
        return pos_str[:3] if len(pos_str) <= 3 else None
    
    df['position_clean'] = df['position'].apply(clean_position)
    df = df.dropna(subset=['position_clean'])  # Remove rows where we couldn't clean the position
    
    # Get unique positions
    positions = df['position_clean'].value_counts()
    print(f"\n🏈 Players by Position:")
    for pos, count in positions.items():
        print(f"   {pos}: {count} players")
    
    # Create position-specific files
    position_files = {}
    
    for position in df['position_clean'].unique():
        if pd.isna(position) or position == '':
            continue
            
        # Filter players for this position
        position_df = df[df['position_clean'] == position].copy()
        
        # Sort by points (descending) for better organization
        # Convert points to numeric, handling any non-numeric values
        position_df['points_numeric'] = pd.to_numeric(position_df['points'], errors='coerce')
        position_df = position_df.sort_values('points_numeric', ascending=False)
        
        # Clean position name for filename
        clean_position = position.lower().replace(' ', '_')
        
        # Extract week info from input filename if present
        week_info = ""
        if "week" in input_file.lower():
            # Extract week pattern like "2025_week1" from filename
            week_match = re.search(r'(\d{4}_week\d+)', input_file)
            if week_match:
                week_info = f"_{week_match.group(1)}"
        
        filename = f"{clean_position}_players{week_info}.csv"
        filepath = os.path.join(output_dir, filename)
        
        # Save to CSV
        position_df.to_csv(filepath, index=False)
        position_files[position] = {
            'filename': filename,
            'count': len(position_df),
            'filepath': filepath
        }
        
        print(f"✅ Saved {len(position_df)} {position} players to {filename}")
    
    # Create a summary file
    create_position_summary(position_files, output_dir, input_file)
    
    # Display top performers by position
    display_top_performers(df)
    
    print(f"\n🎉 Successfully parsed {len(df)} players into position-specific files!")
    print(f"📁 Files saved in: {output_dir}/")
    
    return position_files

def create_position_summary(position_files, output_dir, input_file):
    """Create a summary file with position statistics."""
    
    summary_data = []
    
    for position, info in position_files.items():
        # Read the position file to get stats
        df = pd.read_csv(info['filepath'])
        
        # Calculate statistics
        points_stats = df['points'].describe()
        
        summary_data.append({
            'position': position,
            'player_count': info['count'],
            'filename': info['filename'],
            'avg_points': round(points_stats['mean'], 2) if not pd.isna(points_stats['mean']) else 0,
            'max_points': round(points_stats['max'], 2) if not pd.isna(points_stats['max']) else 0,
            'min_points': round(points_stats['min'], 2) if not pd.isna(points_stats['min']) else 0,
            'median_points': round(points_stats['50%'], 2) if not pd.isna(points_stats['50%']) else 0
        })
    
    # Create summary DataFrame
    summary_df = pd.DataFrame(summary_data)
    summary_df = summary_df.sort_values('avg_points', ascending=False)
    
    # Save summary with week info
    week_info = ""
    if "week" in input_file.lower():
        week_match = re.search(r'(\d{4}_week\d+)', input_file)
        if week_match:
            week_info = f"_{week_match.group(1)}"
    
    summary_path = os.path.join(output_dir, f"position_summary{week_info}.csv")
    summary_df.to_csv(summary_path, index=False)
    
    print(f"✅ Created position summary: position_summary{week_info}.csv")
    
    # Display summary
    print(f"\n📊 Position Summary:")
    print("-" * 80)
    print(f"{'Position':<8} {'Players':<8} {'Avg Pts':<8} {'Max Pts':<8} {'Min Pts':<8} {'Median':<8}")
    print("-" * 80)
    
    for _, row in summary_df.iterrows():
        print(f"{row['position']:<8} {row['player_count']:<8} {row['avg_points']:<8} {row['max_points']:<8} {row['min_points']:<8} {row['median_points']:<8}")

def display_top_performers(df):
    """Display top performers by position."""
    
    print(f"\n🏆 Top Performers by Position:")
    print("=" * 60)
    
    for position in df['position_clean'].unique():
        if pd.isna(position) or position == '':
            continue
            
        position_df = df[df['position_clean'] == position].copy()
        
        # Convert points to numeric for sorting
        position_df['points_numeric'] = pd.to_numeric(position_df['points'], errors='coerce')
        
        # Get top 3 performers
        top_players = position_df.nlargest(3, 'points_numeric')
        
        print(f"\n{position} (Top 3):")
        for i, (_, player) in enumerate(top_players.iterrows(), 1):
            points = player['points'] if pd.notna(player['points']) else 0
            salary = player['salary'] if pd.notna(player['salary']) else 'N/A'
            print(f"  {i}. {player['player_name']:<20} | {points:>6} pts | {salary}")

def main():
    """Main function to run the position parser."""
    
    import sys
    
    # Check for command line argument
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = "yahoo_daily_fantasy_cleaned.csv"
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"❌ Error: {input_file} not found!")
        print("Make sure you have run the selenium scraper first to generate the cleaned data.")
        print("Usage: python3 parse_players_by_position.py [filename.csv]")
        return
    
    # Parse players by position
    position_files = parse_players_by_position(input_file)
    
    if position_files:
        print(f"\n📁 Generated Files:")
        for position, info in position_files.items():
            print(f"   {info['filename']} - {info['count']} {position} players")
        print(f"   position_summary.csv - Summary statistics")

if __name__ == "__main__":
    main()
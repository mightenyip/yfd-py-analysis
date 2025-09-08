#!/usr/bin/env python3
"""
Improved parser for Yahoo Daily Fantasy players by position.
This version has better position detection logic.
"""

import pandas as pd
import argparse
import os
import re

def clean_position_name(position, player_name=""):
    """
    Clean and standardize position names with improved logic.
    """
    if pd.isna(position) or position == 'Unknown':
        return 'UNKNOWN'
    
    # Convert to string and clean
    pos = str(position).strip().upper()
    player = str(player_name).strip().upper()
    
    # Skip if position contains player name or game info (indicates parsing error)
    if '\n' in pos or '@' in pos or 'Final' in pos or 'PASS' in pos or 'RUSH' in pos:
        return 'UNKNOWN'
    
    # Skip if position is actually a player name
    if len(pos) > 10 and any(word in pos for word in ['JACKSON', 'HENRY', 'MAYFIELD', 'ALLEN', 'FIELDS']):
        return 'UNKNOWN'
    
    # Handle common position variations with more specific matching
    if pos == 'QB' or pos == 'QUARTERBACK':
        return 'QB'
    elif pos == 'RB' or pos == 'RUNNING BACK':
        return 'RB'
    elif pos == 'WR' or pos == 'WIDE RECEIVER':
        return 'WR'
    elif pos == 'TE' or pos == 'TIGHT END':
        return 'TE'
    elif pos == 'K' or pos == 'KICKER':
        return 'K'
    elif pos == 'DEF' or pos == 'DEFENSE' or pos == 'D/ST':
        return 'DEF'
    elif 'SACK' in pos:
        return 'DEF'  # Sacks are defensive stats
    elif 'BLK' in pos:
        return 'DEF'  # Blocked kicks are defensive stats
    elif pos in ['TEN 12', 'TEN', '12']:
        return 'TE'  # This seems to be a TE designation
    else:
        return 'UNKNOWN'

def extract_position_from_stats(stats):
    """
    Try to extract position from stats if position field is unclear.
    """
    if pd.isna(stats):
        return 'UNKNOWN'
    
    stats_str = str(stats).upper()
    
    # Look for position indicators in stats
    if 'PASS YD' in stats_str or 'PASS TD' in stats_str:
        return 'QB'
    elif 'RUSH ATT' in stats_str or 'RUSH YD' in stats_str or 'RUSH TD' in stats_str:
        if 'PASS' in stats_str:
            return 'QB'  # QB with rushing stats
        else:
            return 'RB'  # Pure RB
    elif 'TGT' in stats_str or 'REC' in stats_str or 'REC YD' in stats_str or 'REC TD' in stats_str:
        if 'RUSH' in stats_str:
            return 'RB'  # RB with receiving stats
        else:
            return 'WR'  # Likely WR
    elif 'SACK' in stats_str:
        return 'DEF'
    else:
        return 'UNKNOWN'

def parse_players_by_position_improved(input_file, output_dir='position_data_improved'):
    """
    Parse players by position with improved detection logic.
    """
    try:
        # Load the dataset
        print(f"📊 Loading dataset from {input_file}...")
        df = pd.read_csv(input_file)
        print(f"Total players in dataset: {len(df)}")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Clean position data with improved logic
        print("🧹 Cleaning position data with improved logic...")
        
        # First pass: clean position field
        df['clean_position'] = df.apply(lambda row: clean_position_name(row['position'], row['player_name']), axis=1)
        
        # Second pass: for unknown positions, try to extract from stats
        unknown_mask = df['clean_position'] == 'UNKNOWN'
        if unknown_mask.any():
            print(f"   Found {unknown_mask.sum()} players with unknown positions, trying to extract from stats...")
            df.loc[unknown_mask, 'clean_position'] = df.loc[unknown_mask, 'stats'].apply(extract_position_from_stats)
        
        # Get position counts
        position_counts = df['clean_position'].value_counts()
        print(f"\n📊 Position breakdown:")
        for pos, count in position_counts.items():
            print(f"   {pos}: {count} players")
        
        # Create separate CSV files for each position
        created_files = []
        
        for position in position_counts.index:
            if position == 'UNKNOWN':
                continue  # Skip unknown positions for now
                
            # Filter players for this position
            position_df = df[df['clean_position'] == position].copy()
            
            # Remove the clean_position column
            position_df = position_df.drop('clean_position', axis=1)
            
            # Sort by points (descending) if available
            if 'points' in position_df.columns:
                # Convert points to numeric, handling non-numeric values
                position_df['points_numeric'] = pd.to_numeric(position_df['points'], errors='coerce')
                position_df = position_df.sort_values('points_numeric', ascending=False)
                position_df = position_df.drop('points_numeric', axis=1)
            
            # Save to CSV
            output_file = os.path.join(output_dir, f'{position.lower()}_players.csv')
            position_df.to_csv(output_file, index=False)
            created_files.append(output_file)
            
            print(f"✅ Saved {len(position_df)} {position} players to {output_file}")
            
            # Show top 5 players for this position
            if len(position_df) > 0:
                print(f"   Top {min(5, len(position_df))} {position} players:")
                for i, (_, row) in enumerate(position_df.head(5).iterrows(), 1):
                    points = row['points'] if pd.notna(row['points']) else 'N/A'
                    salary = row['salary'] if pd.notna(row['salary']) else 'N/A'
                    print(f"     {i}. {row['player_name']:<20} | {salary:<6} | {points}")
        
        # Handle unknown positions
        unknown_df = df[df['clean_position'] == 'UNKNOWN'].copy()
        if len(unknown_df) > 0:
            unknown_df = unknown_df.drop('clean_position', axis=1)
            output_file = os.path.join(output_dir, 'unknown_players.csv')
            unknown_df.to_csv(output_file, index=False)
            created_files.append(output_file)
            print(f"✅ Saved {len(unknown_df)} unknown position players to {output_file}")
        
        # Create a summary file
        summary_file = os.path.join(output_dir, 'position_summary.csv')
        summary_df = pd.DataFrame({
            'position': position_counts.index,
            'count': position_counts.values
        })
        summary_df.to_csv(summary_file, index=False)
        created_files.append(summary_file)
        
        print(f"\n📁 Created {len(created_files)} files in {output_dir}/")
        print(f"📊 Summary saved to {summary_file}")
        
        return created_files
        
    except FileNotFoundError:
        print(f"❌ Error: File {input_file} not found")
        return []
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def main():
    parser = argparse.ArgumentParser(description='Parse Yahoo Daily Fantasy players by position (improved)')
    parser.add_argument('--input', '-i', 
                       default='yahoo_daily_fantasy_paginated.csv',
                       help='Input CSV file with full dataset (default: yahoo_daily_fantasy_paginated.csv)')
    parser.add_argument('--output-dir', '-o',
                       default='position_data_improved',
                       help='Output directory for position-specific CSV files (default: position_data_improved)')
    
    args = parser.parse_args()
    
    print("Yahoo Daily Fantasy Position Parser (Improved)")
    print("=" * 50)
    print(f"Input file: {args.input}")
    print(f"Output directory: {args.output_dir}")
    print("=" * 50)
    
    created_files = parse_players_by_position_improved(args.input, args.output_dir)
    
    if created_files:
        print(f"\n🎉 SUCCESS! Created {len(created_files)} position-specific files")
        print(f"📁 All files saved in: {args.output_dir}/")
    else:
        print(f"\n❌ FAILED! Check the error messages above")

if __name__ == "__main__":
    main()

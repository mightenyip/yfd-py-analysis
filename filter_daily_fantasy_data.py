#!/usr/bin/env python3
"""
Filter Yahoo Daily Fantasy data to get top N players.
This script filters the full dataset to get the top N players by ranking.
"""

import pandas as pd
import argparse
import sys

def filter_daily_fantasy_data(input_file, output_file, num_players):
    """
    Filter the daily fantasy data to get the top N players.
    
    Args:
        input_file (str): Path to the full dataset CSV file
        output_file (str): Path to save the filtered dataset
        num_players (int): Number of top players to extract
    """
    try:
        # Load the full dataset
        print(f"📊 Loading dataset from {input_file}...")
        df = pd.read_csv(input_file)
        print(f"Total players in dataset: {len(df)}")
        
        if len(df) < num_players:
            print(f"⚠️  Warning: Dataset only has {len(df)} players, but you requested {num_players}")
            num_players = len(df)
        
        # Get top N players
        print(f"🔍 Filtering to top {num_players} players...")
        top_players = df.head(num_players)
        
        # Save filtered data
        top_players.to_csv(output_file, index=False)
        print(f"✅ Saved top {num_players} players to {output_file}")
        
        # Display summary
        print(f"\n📋 Top {num_players} Players Summary:")
        print(f"Players: {len(top_players)}")
        
        # Position breakdown
        print(f"\n🏈 Players by Position:")
        position_counts = top_players['position'].value_counts()
        for pos, count in position_counts.items():
            print(f"   {pos}: {count} players")
        
        # Top 10 players
        print(f"\n⭐ Top 10 Players:")
        for i, (_, row) in enumerate(top_players.head(10).iterrows(), 1):
            points = row['points'] if pd.notna(row['points']) else 'N/A'
            salary = row['salary'] if pd.notna(row['salary']) else 'N/A'
            print(f"   {i:2d}. {row['player_name']:<20} | {row['position']:<3} | {salary:<6} | {points}")
        
        # Show some players from the middle if we have enough data
        if num_players > 20:
            middle_start = max(1, num_players // 2 - 5)
            middle_end = min(num_players, num_players // 2 + 5)
            print(f"\n📊 Sample from middle ({middle_start}-{middle_end}):")
            for i, (_, row) in enumerate(top_players.iloc[middle_start-1:middle_end].iterrows(), middle_start):
                points = row['points'] if pd.notna(row['points']) else 'N/A'
                salary = row['salary'] if pd.notna(row['salary']) else 'N/A'
                print(f"   {i:2d}. {row['player_name']:<20} | {row['position']:<3} | {salary:<6} | {points}")
        
        # Show some players from the end if we have enough data
        if num_players > 10:
            end_start = max(1, num_players - 9)
            end_end = num_players
            print(f"\n📊 Sample from end ({end_start}-{end_end}):")
            for i, (_, row) in enumerate(top_players.iloc[end_start-1:end_end].iterrows(), end_start):
                points = row['points'] if pd.notna(row['points']) else 'N/A'
                salary = row['salary'] if pd.notna(row['salary']) else 'N/A'
                print(f"   {i:2d}. {row['player_name']:<20} | {row['position']:<3} | {salary:<6} | {points}")
        
        return True
        
    except FileNotFoundError:
        print(f"❌ Error: File {input_file} not found")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Filter Yahoo Daily Fantasy data to get top N players')
    parser.add_argument('--input', '-i', 
                       default='yahoo_daily_fantasy_paginated.csv',
                       help='Input CSV file with full dataset (default: yahoo_daily_fantasy_paginated.csv)')
    parser.add_argument('--output', '-o',
                       help='Output CSV file (default: yahoo_daily_fantasy_top_N.csv)')
    parser.add_argument('--players', '-n', type=int, default=300,
                       help='Number of top players to extract (default: 300)')
    
    args = parser.parse_args()
    
    # Set default output filename if not provided
    if not args.output:
        args.output = f'yahoo_daily_fantasy_top_{args.players}.csv'
    
    print("Yahoo Daily Fantasy Data Filter")
    print("=" * 40)
    print(f"Input file: {args.input}")
    print(f"Output file: {args.output}")
    print(f"Number of players: {args.players}")
    print("=" * 40)
    
    success = filter_daily_fantasy_data(args.input, args.output, args.players)
    
    if success:
        print(f"\n🎉 SUCCESS! Filtered data saved to {args.output}")
    else:
        print(f"\n❌ FAILED! Check the error messages above")
        sys.exit(1)

if __name__ == "__main__":
    main()

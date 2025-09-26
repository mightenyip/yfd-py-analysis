#!/usr/bin/env python3
"""
Generate raw stats for position-salary heatmap
"""

import pandas as pd
import numpy as np

def load_all_thursday_data():
    """Load and combine all Thursday data from Week 2-4."""
    
    # Load Week 2 Thursday data
    week2_file = "/Users/mightenyip/Documents/GitHub/yfd-py-test/data_csv/week2_Thurs.csv"
    week2_df = pd.read_csv(week2_file)
    
    # Load Week 3 Thursday data
    week3_file = "/Users/mightenyip/Documents/GitHub/yfd-py-test/data_csv/week3_Thurs.csv"
    week3_df = pd.read_csv(week3_file)
    
    # Load Week 4 Thursday data
    week4_file = "/Users/mightenyip/Documents/GitHub/yfd-py-test/data_csv/week4_Thurs.csv"
    week4_df = pd.read_csv(week4_file)
    
    # Combine all data
    all_thursday_data = pd.concat([week2_df, week3_df, week4_df], ignore_index=True)
    
    return all_thursday_data

def clean_and_filter_data(df):
    """Clean and filter for active players only."""
    # Clean salary data (remove $ and convert to numeric)
    df['salary_numeric'] = df['salary'].str.replace('$', '').astype(float)
    
    # Clean points data (convert to numeric)
    df['points_numeric'] = pd.to_numeric(df['points'], errors='coerce')
    
    # Remove any rows where points or salary couldn't be converted
    df_clean = df.dropna(subset=['salary_numeric', 'points_numeric']).copy()
    
    # Filter for active players (non-zero points)
    df_active = df_clean[df_clean['points_numeric'] > 0].copy()
    
    return df_active

def create_salary_bins(df_active):
    """Create salary bins for analysis."""
    # Create bins: $10-15, $16-20, $21-25, $26-30, $31-35, $36-40, $41+
    bins = [9, 15, 20, 25, 30, 35, 40, 50]
    bin_labels = ['$10-15', '$16-20', '$21-25', '$26-30', '$31-35', '$36-40', '$41+']
    
    df_active['salary_bin'] = pd.cut(df_active['salary_numeric'], bins=bins, labels=bin_labels, include_lowest=True)
    
    # Calculate points per dollar
    df_active['points_per_dollar'] = df_active['points_numeric'] / df_active['salary_numeric']
    
    return df_active

def generate_heatmap_stats(df_active):
    """Generate raw stats for the position-salary heatmap."""
    
    print("📊 POSITION-SALARY HEATMAP RAW STATS")
    print("=" * 60)
    print("Player counts in each position-salary bin combination")
    print("=" * 60)
    
    # Create pivot table for player counts
    count_pivot = df_active.groupby(['position', 'salary_bin']).size().unstack(fill_value=0)
    
    print("\nPlayer Counts by Position and Salary Bin:")
    print(count_pivot)
    
    # Create pivot table for points per dollar
    ppd_pivot = df_active.groupby(['position', 'salary_bin'])['points_per_dollar'].mean().unstack(fill_value=0)
    
    print("\nPoints per Dollar by Position and Salary Bin:")
    print(ppd_pivot.round(3))
    
    # Create pivot table for average points
    points_pivot = df_active.groupby(['position', 'salary_bin'])['points_numeric'].mean().unstack(fill_value=0)
    
    print("\nAverage Points by Position and Salary Bin:")
    print(points_pivot.round(1))
    
    # Create detailed breakdown
    print("\nDetailed Breakdown by Position and Salary Bin:")
    print("-" * 60)
    
    for position in sorted(df_active['position'].unique()):
        pos_data = df_active[df_active['position'] == position]
        print(f"\n{position} Position:")
        
        for bin_label in pos_data['salary_bin'].cat.categories:
            bin_data = pos_data[pos_data['salary_bin'] == bin_label]
            
            if len(bin_data) > 0:
                avg_points = bin_data['points_numeric'].mean()
                avg_ppd = bin_data['points_per_dollar'].mean()
                count = len(bin_data)
                avg_salary = bin_data['salary_numeric'].mean()
                
                print(f"  {bin_label}: {count:2d} players | ${avg_salary:4.1f} avg salary | {avg_points:4.1f} avg pts | {avg_ppd:5.3f} pts/$")
    
    return count_pivot, ppd_pivot, points_pivot

def main():
    # Load data
    all_thursday_data = load_all_thursday_data()
    
    # Clean and filter
    df_active = clean_and_filter_data(all_thursday_data)
    
    # Create salary bins
    df_active = create_salary_bins(df_active)
    
    # Generate heatmap stats
    count_pivot, ppd_pivot, points_pivot = generate_heatmap_stats(df_active)
    
    print(f"\n📈 SUMMARY:")
    print(f"Total active players: {len(df_active)}")
    print(f"Positions: {sorted(df_active['position'].unique())}")
    print(f"Salary bins: {sorted(df_active['salary_bin'].cat.categories)}")

if __name__ == "__main__":
    main()

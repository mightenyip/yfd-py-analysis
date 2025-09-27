#!/usr/bin/env python3
"""
Sunday Games Salary Binning Analysis (Week 2-3)
Analyzing performance trends across different salary bins for Sunday games
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import os

def load_all_sunday_data():
    """Load and combine all Sunday data from Week 2-3."""
    
    print("📊 Loading all Sunday games data...")
    
    # Load Week 2 Sunday data
    week2_file = "/Users/mightenyip/Documents/GitHub/yfd-py-test/data_csv/week2_Sunday.csv"
    week2_df = pd.read_csv(week2_file)
    
    # Load Week 3 Sunday data
    week3_file = "/Users/mightenyip/Documents/GitHub/yfd-py-test/data_csv/week3_Sunday.csv"
    week3_df = pd.read_csv(week3_file)
    
    print(f"   Week 2 Sunday: {len(week2_df)} players")
    print(f"   Week 3 Sunday: {len(week3_df)} players")
    
    # Combine all data
    all_sunday_data = pd.concat([week2_df, week3_df], ignore_index=True)
    
    print(f"✅ Combined Sunday data: {len(all_sunday_data)} total players")
    
    return all_sunday_data

def clean_salary_and_points_data(df):
    """Clean and convert salary and points data to numeric."""
    # Clean salary data (remove $ and convert to numeric)
    df['salary_numeric'] = df['salary'].str.replace('$', '').astype(float)
    
    # Clean points data (convert to numeric)
    df['points_numeric'] = pd.to_numeric(df['points'], errors='coerce')
    
    # Remove any rows where points or salary couldn't be converted
    df_clean = df.dropna(subset=['salary_numeric', 'points_numeric']).copy()
    
    print(f"🧹 Cleaned data: {len(df_clean)} players with valid salary/points")
    
    return df_clean

def filter_active_players(df_clean):
    """Filter for active players only (exclude 0 points)."""
    # Filter for active players (non-zero points)
    df_active = df_clean[df_clean['points_numeric'] > 0].copy()
    
    excluded_count = len(df_clean) - len(df_active)
    print(f"✅ Active players: {len(df_active)} (excluded {excluded_count} inactive players)")
    
    return df_active

def create_salary_bins(df_active):
    """Create salary bins for analysis."""
    
    # Define salary bins based on the data distribution
    salary_min = df_active['salary_numeric'].min()
    salary_max = df_active['salary_numeric'].max()
    
    print(f"\n💰 Salary range: ${salary_min:.0f} - ${salary_max:.0f}")
    
    # Create bins: $10-15, $16-20, $21-25, $26-30, $31-35, $36-40, $41+
    bins = [9, 15, 20, 25, 30, 35, 40, 50]
    bin_labels = ['$10-15', '$16-20', '$21-25', '$26-30', '$31-35', '$36-40', '$41+']
    
    df_active['salary_bin'] = pd.cut(df_active['salary_numeric'], bins=bins, labels=bin_labels, include_lowest=True)
    
    # Calculate points per dollar
    df_active['points_per_dollar'] = df_active['points_numeric'] / df_active['salary_numeric']
    
    print(f"📊 Created salary bins: {bin_labels}")
    
    return df_active

def analyze_salary_bins(df_active):
    """Analyze performance by salary bin."""
    
    print(f"\n📊 SALARY BIN ANALYSIS:")
    
    bin_stats = []
    
    for bin_label in df_active['salary_bin'].cat.categories:
        bin_data = df_active[df_active['salary_bin'] == bin_label]
        
        if len(bin_data) > 0:
            avg_points = bin_data['points_numeric'].mean()
            avg_salary = bin_data['salary_numeric'].mean()
            avg_ppd = bin_data['points_per_dollar'].mean()
            std_points = bin_data['points_numeric'].std()
            count = len(bin_data)
            
            bin_stats.append({
                'salary_bin': bin_label,
                'count': count,
                'avg_salary': avg_salary,
                'avg_points': avg_points,
                'std_points': std_points,
                'avg_ppd': avg_ppd,
                'cv': std_points / avg_points if avg_points > 0 else 0
            })
            
            print(f"   {bin_label}: {count:2d} players | ${avg_salary:4.1f} avg salary | {avg_points:4.1f} ± {std_points:4.1f} pts | {avg_ppd:5.3f} pts/$")
    
    return pd.DataFrame(bin_stats)

def find_best_value_bins(df_active):
    """Find the best value salary bins."""
    
    print(f"\n💎 BEST VALUE SALARY BINS:")
    
    # Calculate average points per dollar by bin
    bin_ppd = df_active.groupby('salary_bin')['points_per_dollar'].mean().sort_values(ascending=False)
    
    for i, (bin_label, avg_ppd) in enumerate(bin_ppd.items(), 1):
        bin_data = df_active[df_active['salary_bin'] == bin_label]
        count = len(bin_data)
        avg_points = bin_data['points_numeric'].mean()
        avg_salary = bin_data['salary_numeric'].mean()
        
        print(f"   {i}. {bin_label}: {avg_ppd:.3f} pts/$ | {count} players | {avg_points:.1f} avg pts | ${avg_salary:.1f} avg salary")
    
    print(f"\n🏆 TOP PERFORMERS BY SALARY BIN:")
    
    for bin_label in df_active['salary_bin'].cat.categories:
        bin_data = df_active[df_active['salary_bin'] == bin_label]
        
        if len(bin_data) > 0:
            top_performer = bin_data.loc[bin_data['points_numeric'].idxmax()]
            print(f"   {bin_label}: {top_performer['player_name']} ({top_performer['week']}) - {top_performer['points_numeric']:.1f} pts | ${top_performer['salary_numeric']:.0f}")

def create_position_binning_heatmap(df_active):
    """Create a heatmap showing points per dollar by position and salary bin."""
    
    # Create pivot table for heatmap
    pivot_data = df_active.groupby(['position', 'salary_bin'])['points_per_dollar'].mean().unstack(fill_value=0)
    
    plt.figure(figsize=(12, 8))
    sns.heatmap(pivot_data, annot=True, fmt='.3f', cmap='YlOrRd', cbar_kws={'label': 'Points per Dollar'})
    plt.title('Sunday Games: Points per Dollar by Position and Salary Bin (Week 2-3)', fontsize=14, fontweight='bold')
    plt.xlabel('Salary Bin')
    plt.ylabel('Position')
    
    # Save plot
    plots_dir = "/Users/mightenyip/Documents/GitHub/yfd-py-test/plots_images"
    plt.tight_layout()
    plt.savefig(f"{plots_dir}/sunday_position_salary_heatmap.png", dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"📊 Position-salary heatmap saved to: {plots_dir}/sunday_position_salary_heatmap.png")
    
    return pivot_data

def generate_heatmap_stats(df_active):
    """Generate raw stats for the position-salary heatmap."""
    
    print("\n📊 POSITION-SALARY HEATMAP RAW STATS")
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
    
    return count_pivot, ppd_pivot, points_pivot

def analyze_sunday_patterns(df_active):
    """Analyze specific Sunday game patterns."""
    print(f"\n🔍 SUNDAY GAMES PATTERNS:")
    
    # Analyze by position efficiency
    position_efficiency = df_active.groupby('position').agg({
        'points_numeric': ['mean', 'std'],
        'salary_numeric': 'mean',
        'points_per_dollar': 'mean'
    }).round(3)
    
    print(f"\n📊 Position Efficiency (Average Performance):")
    for position in position_efficiency.index:
        avg_points = position_efficiency.loc[position, ('points_numeric', 'mean')]
        avg_salary = position_efficiency.loc[position, ('salary_numeric', 'mean')]
        avg_ppd = position_efficiency.loc[position, ('points_per_dollar', 'mean')]
        print(f"   {position}: {avg_points:.1f} pts avg, ${avg_salary:.0f} salary avg, {avg_ppd:.3f} pts/$")
    
    # Analyze week-to-week consistency
    print(f"\n📈 Week-to-Week Consistency:")
    for week in sorted(df_active['week'].unique()):
        week_data = df_active[df_active['week'] == week]
        avg_points = week_data['points_numeric'].mean()
        std_points = week_data['points_numeric'].std()
        cv = std_points / avg_points if avg_points > 0 else 0  # Coefficient of variation
        print(f"   {week}: {avg_points:.1f} ± {std_points:.1f} pts (CV: {cv:.3f})")

def main():
    print("Sunday Games Salary Binning Analysis (Week 2-3)")
    print("=" * 70)
    print("Analyzing performance trends across different salary bins for Sunday games")
    print("=" * 70)
    
    # Load and combine all Sunday data
    all_sunday_data = load_all_sunday_data()
    
    # Clean the data
    df_clean = clean_salary_and_points_data(all_sunday_data)
    
    # Filter for active players only
    df_active = filter_active_players(df_clean)
    
    # Create salary bins
    df_active = create_salary_bins(df_active)
    
    # Analyze salary bins
    bin_stats = analyze_salary_bins(df_active)
    
    # Find best value bins
    find_best_value_bins(df_active)
    
    # Create position-salary heatmap
    pivot_data = create_position_binning_heatmap(df_active)
    
    # Generate heatmap stats
    count_pivot, ppd_pivot, points_pivot = generate_heatmap_stats(df_active)
    
    # Analyze Sunday patterns
    analyze_sunday_patterns(df_active)
    
    # Final conclusions
    print(f"\n🎯 SUNDAY GAMES CONCLUSIONS:")
    print(f"   • Total active players analyzed: {len(df_active)}")
    print(f"   • Salary bins created: {len(bin_stats)}")
    print(f"   • Best value bin: {bin_stats.loc[bin_stats['avg_ppd'].idxmax(), 'salary_bin']}")
    print(f"   • Most consistent bin: {bin_stats.loc[bin_stats['cv'].idxmin(), 'salary_bin']}")
    print(f"   • Most volatile bin: {bin_stats.loc[bin_stats['cv'].idxmax(), 'salary_bin']}")
    
    # Strategic insights
    print(f"\n💡 STRATEGIC INSIGHTS:")
    best_bin = bin_stats.loc[bin_stats['avg_ppd'].idxmax()]
    worst_bin = bin_stats.loc[bin_stats['avg_ppd'].idxmin()]
    
    print(f"   • Target {best_bin['salary_bin']} players for best value ({best_bin['avg_ppd']:.3f} pts/$)")
    print(f"   • Avoid {worst_bin['salary_bin']} players for worst value ({worst_bin['avg_ppd']:.3f} pts/$)")
    
    if bin_stats['avg_ppd'].iloc[0] > bin_stats['avg_ppd'].iloc[-1]:
        print(f"   • Lower salary bins offer better value than higher salary bins")
    else:
        print(f"   • Higher salary bins offer better value than lower salary bins")

if __name__ == "__main__":
    main()

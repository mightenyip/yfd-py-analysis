#!/usr/bin/env python3
"""
Thursday Night Football Salary Binning Analysis (Week 2-4)
Analyzing performance trends across different salary bins
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import os

def load_all_thursday_data():
    """Load and combine all Thursday data from Week 2-4."""
    
    print("📊 Loading all Thursday Night Football data...")
    
    # Load Week 2 Thursday data
    week2_file = "/Users/mightenyip/Documents/GitHub/yfd-py-test/data_csv/week2_Thurs.csv"
    week2_df = pd.read_csv(week2_file)
    
    # Load Week 3 Thursday data
    week3_file = "/Users/mightenyip/Documents/GitHub/yfd-py-test/data_csv/week3_Thurs.csv"
    week3_df = pd.read_csv(week3_file)
    
    # Load Week 4 Thursday data
    week4_file = "/Users/mightenyip/Documents/GitHub/yfd-py-test/data_csv/week4_Thurs.csv"
    week4_df = pd.read_csv(week4_file)
    
    print(f"   Week 2 Thursday: {len(week2_df)} players")
    print(f"   Week 3 Thursday: {len(week3_df)} players")
    print(f"   Week 4 Thursday: {len(week4_df)} players")
    
    # Combine all data
    all_thursday_data = pd.concat([week2_df, week3_df, week4_df], ignore_index=True)
    
    print(f"✅ Combined Thursday data: {len(all_thursday_data)} total players")
    
    return all_thursday_data

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

def analyze_bins_by_position(df_active):
    """Analyze salary bins by position."""
    
    print(f"\n📊 SALARY BINS BY POSITION:")
    
    for position in df_active['position'].unique():
        pos_data = df_active[df_active['position'] == position]
        
        if len(pos_data) >= 5:  # Only analyze positions with at least 5 players
            print(f"\n   {position} Position:")
            
            for bin_label in pos_data['salary_bin'].cat.categories:
                bin_data = pos_data[pos_data['salary_bin'] == bin_label]
                
                if len(bin_data) > 0:
                    avg_points = bin_data['points_numeric'].mean()
                    avg_ppd = bin_data['points_per_dollar'].mean()
                    count = len(bin_data)
                    
                    print(f"     {bin_label}: {count:2d} players | {avg_points:4.1f} avg pts | {avg_ppd:5.3f} pts/$")

def analyze_bins_by_week(df_active):
    """Analyze salary bins by week."""
    
    print(f"\n📊 SALARY BINS BY WEEK:")
    
    for week in sorted(df_active['week'].unique()):
        week_data = df_active[df_active['week'] == week]
        
        print(f"\n   {week}:")
        
        for bin_label in week_data['salary_bin'].cat.categories:
            bin_data = week_data[week_data['salary_bin'] == bin_label]
            
            if len(bin_data) > 0:
                avg_points = bin_data['points_numeric'].mean()
                avg_ppd = bin_data['points_per_dollar'].mean()
                count = len(bin_data)
                
                print(f"     {bin_label}: {count:2d} players | {avg_points:4.1f} avg pts | {avg_ppd:5.3f} pts/$")

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

def create_salary_binning_visualizations(df_active, bin_stats):
    """Create visualizations for salary binning analysis."""
    
    # Set up the plotting style
    plt.style.use('default')
    
    # Create a figure with multiple subplots
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Thursday Night Football: Salary Binning Analysis (Week 2-4)', fontsize=16, fontweight='bold')
    
    # 1. Average points by salary bin
    ax1 = axes[0, 0]
    bin_stats_sorted = bin_stats.sort_values('avg_salary')
    ax1.bar(bin_stats_sorted['salary_bin'], bin_stats_sorted['avg_points'], color='skyblue', alpha=0.7)
    ax1.set_title('Average Points by Salary Bin')
    ax1.set_ylabel('Average Fantasy Points')
    ax1.tick_params(axis='x', rotation=45)
    ax1.grid(True, alpha=0.3)
    
    # Add error bars
    ax1.errorbar(bin_stats_sorted['salary_bin'], bin_stats_sorted['avg_points'], 
                yerr=bin_stats_sorted['std_points'], fmt='none', color='black', capsize=5)
    
    # 2. Points per dollar by salary bin
    ax2 = axes[0, 1]
    ax2.bar(bin_stats_sorted['salary_bin'], bin_stats_sorted['avg_ppd'], color='lightgreen', alpha=0.7)
    ax2.set_title('Average Points per Dollar by Salary Bin')
    ax2.set_ylabel('Points per Dollar')
    ax2.tick_params(axis='x', rotation=45)
    ax2.grid(True, alpha=0.3)
    
    # 3. Player count by salary bin
    ax3 = axes[1, 0]
    ax3.bar(bin_stats_sorted['salary_bin'], bin_stats_sorted['count'], color='lightcoral', alpha=0.7)
    ax3.set_title('Player Count by Salary Bin')
    ax3.set_ylabel('Number of Players')
    ax3.tick_params(axis='x', rotation=45)
    ax3.grid(True, alpha=0.3)
    
    # 4. Coefficient of variation by salary bin
    ax4 = axes[1, 1]
    ax4.bar(bin_stats_sorted['salary_bin'], bin_stats_sorted['cv'], color='gold', alpha=0.7)
    ax4.set_title('Coefficient of Variation by Salary Bin')
    ax4.set_ylabel('Coefficient of Variation')
    ax4.tick_params(axis='x', rotation=45)
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save plot
    plots_dir = "/Users/mightenyip/Documents/GitHub/yfd-py-test/plots_images"
    if not os.path.exists(plots_dir):
        os.makedirs(plots_dir)
    
    plt.savefig(f"{plots_dir}/thursday_salary_binning_analysis.png", dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"📊 Salary binning plot saved to: {plots_dir}/thursday_salary_binning_analysis.png")

def create_position_binning_heatmap(df_active):
    """Create a heatmap showing points per dollar by position and salary bin."""
    
    # Create pivot table for heatmap
    pivot_data = df_active.groupby(['position', 'salary_bin'])['points_per_dollar'].mean().unstack(fill_value=0)
    
    plt.figure(figsize=(12, 8))
    sns.heatmap(pivot_data, annot=True, fmt='.3f', cmap='YlOrRd', cbar_kws={'label': 'Points per Dollar'})
    plt.title('Thursday Night Football: Points per Dollar by Position and Salary Bin', fontsize=14, fontweight='bold')
    plt.xlabel('Salary Bin')
    plt.ylabel('Position')
    
    # Save plot
    plots_dir = "/Users/mightenyip/Documents/GitHub/yfd-py-test/plots_images"
    plt.tight_layout()
    plt.savefig(f"{plots_dir}/thursday_position_salary_heatmap.png", dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"📊 Position-salary heatmap saved to: {plots_dir}/thursday_position_salary_heatmap.png")

def analyze_salary_bin_trends(bin_stats):
    """Analyze trends across salary bins."""
    
    print(f"\n📈 SALARY BIN TRENDS:")
    
    # Calculate correlation between average salary and average points
    salary_corr = stats.pearsonr(bin_stats['avg_salary'], bin_stats['avg_points'])
    print(f"   Salary vs Points correlation: r = {salary_corr[0]:.3f}")
    
    # Calculate correlation between average salary and points per dollar
    ppd_corr = stats.pearsonr(bin_stats['avg_salary'], bin_stats['avg_ppd'])
    print(f"   Salary vs Points per Dollar correlation: r = {ppd_corr[0]:.3f}")
    
    # Find the most consistent bin (lowest CV)
    most_consistent = bin_stats.loc[bin_stats['cv'].idxmin()]
    print(f"   Most consistent bin: {most_consistent['salary_bin']} (CV: {most_consistent['cv']:.3f})")
    
    # Find the most volatile bin (highest CV)
    most_volatile = bin_stats.loc[bin_stats['cv'].idxmax()]
    print(f"   Most volatile bin: {most_volatile['salary_bin']} (CV: {most_volatile['cv']:.3f})")
    
    # Find the best value bin
    best_value = bin_stats.loc[bin_stats['avg_ppd'].idxmax()]
    print(f"   Best value bin: {best_value['salary_bin']} ({best_value['avg_ppd']:.3f} pts/$)")
    
    # Find the worst value bin
    worst_value = bin_stats.loc[bin_stats['avg_ppd'].idxmin()]
    print(f"   Worst value bin: {worst_value['salary_bin']} ({worst_value['avg_ppd']:.3f} pts/$)")

def main():
    print("Thursday Night Football Salary Binning Analysis (Week 2-4)")
    print("=" * 70)
    print("Analyzing performance trends across different salary bins")
    print("=" * 70)
    
    # Load and combine all Thursday data
    all_thursday_data = load_all_thursday_data()
    
    # Clean the data
    df_clean = clean_salary_and_points_data(all_thursday_data)
    
    # Filter for active players only
    df_active = filter_active_players(df_clean)
    
    # Create salary bins
    df_active = create_salary_bins(df_active)
    
    # Analyze salary bins
    bin_stats = analyze_salary_bins(df_active)
    
    # Analyze bins by position
    analyze_bins_by_position(df_active)
    
    # Analyze bins by week
    analyze_bins_by_week(df_active)
    
    # Find best value bins
    find_best_value_bins(df_active)
    
    # Create visualizations
    create_salary_binning_visualizations(df_active, bin_stats)
    create_position_binning_heatmap(df_active)
    
    # Analyze trends
    analyze_salary_bin_trends(bin_stats)
    
    # Final conclusions
    print(f"\n🎯 SALARY BINNING CONCLUSIONS:")
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

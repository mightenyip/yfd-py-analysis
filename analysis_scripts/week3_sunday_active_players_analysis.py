#!/usr/bin/env python3
"""
Analysis of Week 3 Sunday salary vs points correlation - ACTIVE PLAYERS ONLY
This script filters out inactive players but allows manual inclusion of specific players
who were active but scored 0 points (e.g., injured during game)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import os

def load_week3_sunday_data():
    """Load the Week 3 Sunday data."""
    filepath = "/Users/mightenyip/Documents/GitHub/yfd-py-test/data_csv/week3_Sunday.csv"
    df = pd.read_csv(filepath)
    
    print(f"📊 Loaded Week 3 Sunday data: {len(df)} players")
    print(f"Columns: {list(df.columns)}")
    
    return df

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

def identify_active_players(df_clean):
    """
    Identify active players by filtering out those with 0 points and empty stats.
    Also includes a manual list of players who should be included even with 0 points.
    """
    
    # Manual list of players who were active but scored 0 points (e.g., injured during game)
    # Add players here that you want to include even though they have 0 points
    MANUAL_INCLUDE_PLAYERS = [
        # Example: "CeeDee Lamb",  # Add injured active players here
        # Add more players as needed
    ]
    
    print(f"🔍 Identifying active players...")
    
    # Count players by points
    points_distribution = df_clean['points_numeric'].value_counts().sort_index()
    zero_points_count = df_clean[df_clean['points_numeric'] == 0.0].shape[0]
    
    print(f"📊 Points distribution:")
    print(f"   Players with 0 points: {zero_points_count}")
    print(f"   Players with positive points: {len(df_clean) - zero_points_count}")
    
    # Filter for active players (non-zero points OR manually included players)
    active_condition = (
        (df_clean['points_numeric'] > 0) |  # Players with positive points
        (df_clean['player_name'].isin(MANUAL_INCLUDE_PLAYERS))  # Manually included players
    )
    
    df_active = df_clean[active_condition].copy()
    
    print(f"✅ Active players identified: {len(df_active)}")
    print(f"   Excluded {len(df_clean) - len(df_active)} inactive players")
    
    # Show some examples of excluded players
    excluded_players = df_clean[~active_condition]
    if len(excluded_players) > 0:
        print(f"\n📋 Sample of excluded players (0 points, not manually included):")
        for i, (_, row) in enumerate(excluded_players.head(10).iterrows(), 1):
            print(f"   {i:2d}. {row['player_name']:<20} | {row['position']:<3} | ${row['salary_numeric']:>4.0f} | {row['points_numeric']:>5.1f} pts")
        if len(excluded_players) > 10:
            print(f"   ... and {len(excluded_players) - 10} more")
    
    # Show manually included players (if any)
    if MANUAL_INCLUDE_PLAYERS:
        manual_players = df_active[df_active['player_name'].isin(MANUAL_INCLUDE_PLAYERS)]
        if len(manual_players) > 0:
            print(f"\n📋 Manually included players (0 points but active):")
            for i, (_, row) in enumerate(manual_players.iterrows(), 1):
                print(f"   {i:2d}. {row['player_name']:<20} | {row['position']:<3} | ${row['salary_numeric']:>4.0f} | {row['points_numeric']:>5.1f} pts")
    
    return df_active, MANUAL_INCLUDE_PLAYERS

def calculate_correlation_stats(df_active):
    """Calculate correlation statistics for active players only."""
    salary = df_active['salary_numeric']
    points = df_active['points_numeric']
    
    # Calculate correlation coefficient
    correlation = stats.pearsonr(salary, points)
    
    # Calculate R-squared
    r_squared = correlation[0] ** 2
    
    # Calculate slope and intercept for regression line
    slope, intercept, r_value, p_value, std_err = stats.linregress(salary, points)
    
    print(f"\n📈 CORRELATION ANALYSIS (ACTIVE PLAYERS ONLY):")
    print(f"   Pearson Correlation Coefficient: {correlation[0]:.4f}")
    print(f"   R-squared: {r_squared:.4f}")
    print(f"   P-value: {correlation[1]:.6f}")
    print(f"   Regression line: Points = {slope:.4f} * Salary + {intercept:.4f}")
    
    return correlation, slope, intercept, r_squared

def analyze_by_position(df_active):
    """Analyze correlation by position for active players."""
    print(f"\n📊 CORRELATION BY POSITION (ACTIVE PLAYERS ONLY):")
    
    position_stats = []
    for position in df_active['position'].unique():
        pos_data = df_active[df_active['position'] == position]
        if len(pos_data) >= 5:  # Only analyze positions with at least 5 players
            corr = stats.pearsonr(pos_data['salary_numeric'], pos_data['points_numeric'])
            r_squared = corr[0] ** 2
            position_stats.append({
                'position': position,
                'count': len(pos_data),
                'correlation': corr[0],
                'r_squared': r_squared,
                'p_value': corr[1]
            })
            print(f"   {position}: r={corr[0]:.3f}, R²={r_squared:.3f}, n={len(pos_data)}")
    
    return pd.DataFrame(position_stats)

def find_value_players_and_busts(df_active):
    """Find high-value players and busts among active players."""
    # Calculate points per dollar
    df_active['points_per_dollar'] = df_active['points_numeric'] / df_active['salary_numeric']
    
    # Sort by points per dollar
    df_active_sorted = df_active.sort_values('points_per_dollar', ascending=False)
    
    print(f"\n💎 TOP 10 VALUE PLAYS (Highest Points per Dollar - ACTIVE PLAYERS):")
    for i, (_, row) in enumerate(df_active_sorted.head(10).iterrows(), 1):
        print(f"   {i:2d}. {row['player_name']:<20} | {row['position']:<3} | ${row['salary_numeric']:>4.0f} | {row['points_numeric']:>5.1f} pts | {row['points_per_dollar']:>5.3f} pts/$")
    
    print(f"\n💸 TOP 10 BUSTS (Lowest Points per Dollar, Min $20 salary - ACTIVE PLAYERS):")
    min_salary = 20
    busts = df_active_sorted[df_active_sorted['salary_numeric'] >= min_salary].tail(10)
    for i, (_, row) in enumerate(busts.iterrows(), 1):
        print(f"   {i:2d}. {row['player_name']:<20} | {row['position']:<3} | ${row['salary_numeric']:>4.0f} | {row['points_numeric']:>5.1f} pts | {row['points_per_dollar']:>5.3f} pts/$")
    
    return df_active_sorted

def create_salary_vs_points_plot(df_active, slope, intercept):
    """Create scatter plot of salary vs points for active players only."""
    plt.figure(figsize=(12, 8))
    
    # Create scatter plot with position-based colors
    positions = df_active['position'].unique()
    colors = ['red', 'blue', 'green', 'orange', 'purple']
    position_colors = {pos: colors[i % len(colors)] for i, pos in enumerate(positions)}
    
    for position in positions:
        pos_data = df_active[df_active['position'] == position]
        plt.scatter(pos_data['salary_numeric'], pos_data['points_numeric'], 
                   label=position, alpha=0.7, s=60, color=position_colors[position])
    
    # Add regression line
    x_range = np.linspace(df_active['salary_numeric'].min(), df_active['salary_numeric'].max(), 100)
    y_pred = slope * x_range + intercept
    plt.plot(x_range, y_pred, 'k--', linewidth=2, label=f'Regression Line (R² = {slope**2:.3f})')
    
    plt.xlabel('Salary ($)', fontsize=12)
    plt.ylabel('Fantasy Points', fontsize=12)
    plt.title('Week 3 Sunday: Salary vs Fantasy Points (ACTIVE PLAYERS ONLY)', fontsize=14, fontweight='bold')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Add correlation info as text
    correlation = stats.pearsonr(df_active['salary_numeric'], df_active['points_numeric'])[0]
    plt.text(0.05, 0.95, f'Correlation: r = {correlation:.3f}\nR² = {correlation**2:.3f}\nActive Players: {len(df_active)}', 
             transform=plt.gca().transAxes, fontsize=10, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # Save plot
    plots_dir = "/Users/mightenyip/Documents/GitHub/yfd-py-test/plots_images"
    if not os.path.exists(plots_dir):
        os.makedirs(plots_dir)
    
    plt.tight_layout()
    plt.savefig(f"{plots_dir}/week3_sunday_active_players_salary_vs_points.png", dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"📊 Plot saved to: {plots_dir}/week3_sunday_active_players_salary_vs_points.png")

def create_points_per_dollar_analysis(df_active):
    """Create analysis of points per dollar by position for active players."""
    # Calculate points per dollar
    df_active['points_per_dollar'] = df_active['points_numeric'] / df_active['salary_numeric']
    
    plt.figure(figsize=(12, 8))
    
    # Create box plot by position
    positions = df_active['position'].unique()
    box_data = [df_active[df_active['position'] == pos]['points_per_dollar'].values for pos in positions]
    
    plt.boxplot(box_data, labels=positions)
    plt.ylabel('Points per Dollar', fontsize=12)
    plt.title('Week 3 Sunday: Points per Dollar by Position (ACTIVE PLAYERS ONLY)', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    
    # Add mean points per dollar by position
    print(f"\n📊 MEAN POINTS PER DOLLAR BY POSITION (ACTIVE PLAYERS):")
    for position in positions:
        pos_data = df_active[df_active['position'] == position]
        mean_ppd = pos_data['points_per_dollar'].mean()
        print(f"   {position}: {mean_ppd:.4f} points per dollar")
    
    # Save plot
    plots_dir = "/Users/mightenyip/Documents/GitHub/yfd-py-test/plots_images"
    plt.tight_layout()
    plt.savefig(f"{plots_dir}/week3_sunday_active_players_points_per_dollar.png", dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"📊 Plot saved to: {plots_dir}/week3_sunday_active_players_points_per_dollar.png")

def compare_all_vs_active(df_clean, df_active):
    """Compare correlation between all players vs active players only."""
    all_corr = stats.pearsonr(df_clean['salary_numeric'], df_clean['points_numeric'])[0]
    active_corr = stats.pearsonr(df_active['salary_numeric'], df_active['points_numeric'])[0]
    
    print(f"\n🔄 COMPARISON: All Players vs Active Players Only")
    print(f"   All players ({len(df_clean)}):     r = {all_corr:.4f}, R² = {all_corr**2:.4f}")
    print(f"   Active players ({len(df_active)}):   r = {active_corr:.4f}, R² = {active_corr**2:.4f}")
    print(f"   Difference: {active_corr - all_corr:+.4f} correlation points")
    
    if abs(active_corr - all_corr) > 0.05:
        print(f"   📊 Significant difference - filtering active players {'increased' if active_corr > all_corr else 'decreased'} correlation")
    else:
        print(f"   📊 Minimal difference - filtering didn't significantly change correlation")

def main():
    print("Week 3 Sunday Salary vs Points Correlation Analysis - ACTIVE PLAYERS ONLY")
    print("=" * 80)
    print("This analysis filters out inactive players (0 points) but allows manual inclusion")
    print("of specific players who were active but scored 0 points (e.g., injured during game).")
    print("=" * 80)
    
    # Load data
    df = load_week3_sunday_data()
    
    # Clean data
    df_clean = clean_salary_and_points_data(df)
    
    # Identify active players
    df_active, manual_include_list = identify_active_players(df_clean)
    
    # Calculate correlation statistics for active players
    correlation, slope, intercept, r_squared = calculate_correlation_stats(df_active)
    
    # Analyze by position for active players
    position_stats = analyze_by_position(df_active)
    
    # Find value players and busts among active players
    df_sorted = find_value_players_and_busts(df_active)
    
    # Create visualizations for active players
    create_salary_vs_points_plot(df_active, slope, intercept)
    create_points_per_dollar_analysis(df_active)
    
    # Compare all vs active players
    compare_all_vs_active(df_clean, df_active)
    
    # Summary
    print(f"\n🎯 SUMMARY (ACTIVE PLAYERS ONLY):")
    print(f"   • Active players analyzed: {len(df_active)}")
    print(f"   • Correlation between salary and points: {correlation[0]:.3f}")
    print(f"   • This explains {r_squared:.1%} of the variance in fantasy points")
    print(f"   • Higher salary players tend to score {'more' if correlation[0] > 0 else 'fewer'} points")
    
    if abs(correlation[0]) < 0.3:
        print(f"   • Weak correlation - salary is not a strong predictor of performance")
    elif abs(correlation[0]) < 0.6:
        print(f"   • Moderate correlation - salary has some predictive value")
    else:
        print(f"   • Strong correlation - salary is a good predictor of performance")
    
    # Instructions for manual inclusion
    print(f"\n💡 TO INCLUDE SPECIFIC PLAYERS WITH 0 POINTS:")
    print(f"   Edit the MANUAL_INCLUDE_PLAYERS list in this script")
    print(f"   Add player names like: 'CeeDee Lamb', 'Player Name', etc.")
    print(f"   Current manual inclusion list: {manual_include_list if manual_include_list else 'Empty'}")

if __name__ == "__main__":
    main()

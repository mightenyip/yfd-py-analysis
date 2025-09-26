#!/usr/bin/env python3
"""
Week 4 Thursday Active Players Analysis
Analyzing salary vs points correlation excluding inactive 0-point players
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import os

def load_week4_thursday_data():
    """Load the Week 4 Thursday data."""
    filepath = "/Users/mightenyip/Documents/GitHub/yfd-py-test/data_csv/week4_Thurs.csv"
    df = pd.read_csv(filepath)
    
    print(f"📊 Loaded Week 4 Thursday data: {len(df)} players")
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

def filter_active_players(df_clean):
    """Filter for active players only (exclude 0 points)."""
    # Filter for active players (non-zero points)
    df_active = df_clean[df_clean['points_numeric'] > 0].copy()
    
    excluded_count = len(df_clean) - len(df_active)
    print(f"✅ Active players: {len(df_active)} (excluded {excluded_count} inactive players)")
    
    # Show excluded players
    excluded_players = df_clean[df_clean['points_numeric'] == 0]
    if len(excluded_players) > 0:
        print(f"\n📋 Excluded inactive players (0 points):")
        for i, (_, row) in enumerate(excluded_players.iterrows(), 1):
            print(f"   {i:2d}. {row['player_name']:<20} | {row['position']:<3} | ${row['salary_numeric']:>4.0f} | FPPG: {row['fppg']}")
    
    return df_active

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
    print(f"   Total active players: {len(df_active)}")
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
        if len(pos_data) >= 3:  # Only analyze positions with at least 3 players
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
    
    print(f"\n🏆 TOP 10 HIGHEST SCORING GAMES (ACTIVE PLAYERS):")
    top_scores = df_active.nlargest(10, 'points_numeric')
    for i, (_, row) in enumerate(top_scores.iterrows(), 1):
        print(f"   {i:2d}. {row['player_name']:<20} | {row['position']:<3} | ${row['salary_numeric']:>4.0f} | {row['points_numeric']:>5.1f} pts")
    
    print(f"\n💸 TOP 10 BUSTS (Lowest Points per Dollar, Min $15 salary - ACTIVE PLAYERS):")
    min_salary = 15
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
                   label=position, alpha=0.7, s=80, color=position_colors[position])
    
    # Add regression line
    x_range = np.linspace(df_active['salary_numeric'].min(), df_active['salary_numeric'].max(), 100)
    y_pred = slope * x_range + intercept
    plt.plot(x_range, y_pred, 'k--', linewidth=2, label=f'Regression Line (R² = {slope**2:.3f})')
    
    plt.xlabel('Salary ($)', fontsize=12)
    plt.ylabel('Fantasy Points', fontsize=12)
    plt.title('Week 4 Thursday: Salary vs Fantasy Points (ACTIVE PLAYERS ONLY)', fontsize=14, fontweight='bold')
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
    plt.savefig(f"{plots_dir}/week4_thursday_active_players_salary_vs_points.png", dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"📊 Plot saved to: {plots_dir}/week4_thursday_active_players_salary_vs_points.png")

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
    plt.title('Week 4 Thursday: Points per Dollar by Position (ACTIVE PLAYERS ONLY)', fontsize=14, fontweight='bold')
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
    plt.savefig(f"{plots_dir}/week4_thursday_active_players_points_per_dollar.png", dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"📊 Plot saved to: {plots_dir}/week4_thursday_active_players_points_per_dollar.png")

def analyze_game_context(df_active):
    """Analyze the game context and performance patterns."""
    print(f"\n🎮 GAME CONTEXT ANALYSIS:")
    print(f"   Game: Seattle Seahawks 23 @ Arizona Cardinals 20 (Final)")
    print(f"   Total active players: {len(df_active)}")
    
    # Analyze by team (based on game info)
    seattle_players = df_active[df_active['game_info'].str.contains('SEA', na=False)]
    arizona_players = df_active[df_active['game_info'].str.contains('ARI', na=False)]
    
    if len(seattle_players) > 0:
        seattle_avg = seattle_players['points_numeric'].mean()
        print(f"   Seattle players average: {seattle_avg:.1f} points ({len(seattle_players)} players)")
    
    if len(arizona_players) > 0:
        arizona_avg = arizona_players['points_numeric'].mean()
        print(f"   Arizona players average: {arizona_avg:.1f} points ({len(arizona_players)} players)")
    
    # Analyze salary distribution
    print(f"\n💰 SALARY DISTRIBUTION (ACTIVE PLAYERS):")
    print(f"   Average salary: ${df_active['salary_numeric'].mean():.1f}")
    print(f"   Median salary: ${df_active['salary_numeric'].median():.1f}")
    print(f"   Salary range: ${df_active['salary_numeric'].min():.0f} - ${df_active['salary_numeric'].max():.0f}")
    
    # Analyze points distribution
    print(f"\n📊 POINTS DISTRIBUTION (ACTIVE PLAYERS):")
    print(f"   Average points: {df_active['points_numeric'].mean():.1f}")
    print(f"   Median points: {df_active['points_numeric'].median():.1f}")
    print(f"   Points range: {df_active['points_numeric'].min():.1f} - {df_active['points_numeric'].max():.1f}")

def main():
    print("Week 4 Thursday Active Players Analysis")
    print("=" * 60)
    print("Analyzing salary vs points correlation excluding inactive 0-point players")
    print("=" * 60)
    
    # Load data
    df = load_week4_thursday_data()
    
    # Clean data
    df_clean = clean_salary_and_points_data(df)
    
    # Filter for active players only
    df_active = filter_active_players(df_clean)
    
    # Calculate correlation statistics for active players
    correlation, slope, intercept, r_squared = calculate_correlation_stats(df_active)
    
    # Analyze by position for active players
    position_stats = analyze_by_position(df_active)
    
    # Find value players and busts among active players
    df_sorted = find_value_players_and_busts(df_active)
    
    # Create visualizations for active players
    create_salary_vs_points_plot(df_active, slope, intercept)
    create_points_per_dollar_analysis(df_active)
    
    # Analyze game context
    analyze_game_context(df_active)
    
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
    
    # Best and worst positions for correlation
    if len(position_stats) > 0:
        best_pos = position_stats.loc[position_stats['correlation'].idxmax(), 'position']
        worst_pos = position_stats.loc[position_stats['correlation'].idxmin(), 'position']
        print(f"   • Most predictable position: {best_pos}")
        print(f"   • Least predictable position: {worst_pos}")

if __name__ == "__main__":
    main()

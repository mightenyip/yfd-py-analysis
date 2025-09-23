#!/usr/bin/env python3
"""
Analysis of Week 3 Sunday salary vs points correlation
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

def calculate_correlation_stats(df_clean):
    """Calculate correlation statistics."""
    salary = df_clean['salary_numeric']
    points = df_clean['points_numeric']
    
    # Calculate correlation coefficient
    correlation = stats.pearsonr(salary, points)
    
    # Calculate R-squared
    r_squared = correlation[0] ** 2
    
    # Calculate slope and intercept for regression line
    slope, intercept, r_value, p_value, std_err = stats.linregress(salary, points)
    
    print(f"\n📈 CORRELATION ANALYSIS:")
    print(f"   Pearson Correlation Coefficient: {correlation[0]:.4f}")
    print(f"   R-squared: {r_squared:.4f}")
    print(f"   P-value: {correlation[1]:.6f}")
    print(f"   Regression line: Points = {slope:.4f} * Salary + {intercept:.4f}")
    
    return correlation, slope, intercept, r_squared

def analyze_by_position(df_clean):
    """Analyze correlation by position."""
    print(f"\n📊 CORRELATION BY POSITION:")
    
    position_stats = []
    for position in df_clean['position'].unique():
        pos_data = df_clean[df_clean['position'] == position]
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

def find_value_players_and_busts(df_clean):
    """Find high-value players and busts."""
    # Calculate points per dollar
    df_clean['points_per_dollar'] = df_clean['points_numeric'] / df_clean['salary_numeric']
    
    # Sort by points per dollar
    df_clean_sorted = df_clean.sort_values('points_per_dollar', ascending=False)
    
    print(f"\n💎 TOP 10 VALUE PLAYS (Highest Points per Dollar):")
    for i, (_, row) in enumerate(df_clean_sorted.head(10).iterrows(), 1):
        print(f"   {i:2d}. {row['player_name']:<20} | {row['position']:<3} | ${row['salary_numeric']:>4.0f} | {row['points_numeric']:>5.1f} pts | {row['points_per_dollar']:>5.3f} pts/$")
    
    print(f"\n💸 TOP 10 BUSTS (Lowest Points per Dollar, Min $20 salary):")
    min_salary = 20
    busts = df_clean_sorted[df_clean_sorted['salary_numeric'] >= min_salary].tail(10)
    for i, (_, row) in enumerate(busts.iterrows(), 1):
        print(f"   {i:2d}. {row['player_name']:<20} | {row['position']:<3} | ${row['salary_numeric']:>4.0f} | {row['points_numeric']:>5.1f} pts | {row['points_per_dollar']:>5.3f} pts/$")
    
    return df_clean_sorted

def create_salary_vs_points_plot(df_clean, slope, intercept):
    """Create scatter plot of salary vs points."""
    plt.figure(figsize=(12, 8))
    
    # Create scatter plot with position-based colors
    positions = df_clean['position'].unique()
    colors = ['red', 'blue', 'green', 'orange', 'purple']
    position_colors = {pos: colors[i % len(colors)] for i, pos in enumerate(positions)}
    
    for position in positions:
        pos_data = df_clean[df_clean['position'] == position]
        plt.scatter(pos_data['salary_numeric'], pos_data['points_numeric'], 
                   label=position, alpha=0.7, s=60, color=position_colors[position])
    
    # Add regression line
    x_range = np.linspace(df_clean['salary_numeric'].min(), df_clean['salary_numeric'].max(), 100)
    y_pred = slope * x_range + intercept
    plt.plot(x_range, y_pred, 'k--', linewidth=2, label=f'Regression Line (R² = {slope**2:.3f})')
    
    plt.xlabel('Salary ($)', fontsize=12)
    plt.ylabel('Fantasy Points', fontsize=12)
    plt.title('Week 3 Sunday: Salary vs Fantasy Points Correlation', fontsize=14, fontweight='bold')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Add correlation info as text
    correlation = stats.pearsonr(df_clean['salary_numeric'], df_clean['points_numeric'])[0]
    plt.text(0.05, 0.95, f'Correlation: r = {correlation:.3f}\nR² = {correlation**2:.3f}', 
             transform=plt.gca().transAxes, fontsize=10, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # Save plot
    plots_dir = "/Users/mightenyip/Documents/GitHub/yfd-py-test/plots_images"
    if not os.path.exists(plots_dir):
        os.makedirs(plots_dir)
    
    plt.tight_layout()
    plt.savefig(f"{plots_dir}/week3_sunday_salary_vs_points.png", dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"📊 Plot saved to: {plots_dir}/week3_sunday_salary_vs_points.png")

def create_points_per_dollar_analysis(df_clean):
    """Create analysis of points per dollar by position."""
    # Calculate points per dollar
    df_clean['points_per_dollar'] = df_clean['points_numeric'] / df_clean['salary_numeric']
    
    plt.figure(figsize=(12, 8))
    
    # Create box plot by position
    positions = df_clean['position'].unique()
    box_data = [df_clean[df_clean['position'] == pos]['points_per_dollar'].values for pos in positions]
    
    plt.boxplot(box_data, labels=positions)
    plt.ylabel('Points per Dollar', fontsize=12)
    plt.title('Week 3 Sunday: Points per Dollar by Position', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    
    # Add mean points per dollar by position
    print(f"\n📊 MEAN POINTS PER DOLLAR BY POSITION:")
    for position in positions:
        pos_data = df_clean[df_clean['position'] == position]
        mean_ppd = pos_data['points_per_dollar'].mean()
        print(f"   {position}: {mean_ppd:.4f} points per dollar")
    
    # Save plot
    plots_dir = "/Users/mightenyip/Documents/GitHub/yfd-py-test/plots_images"
    plt.tight_layout()
    plt.savefig(f"{plots_dir}/week3_sunday_points_per_dollar_by_position.png", dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"📊 Plot saved to: {plots_dir}/week3_sunday_points_per_dollar_by_position.png")

def main():
    print("Week 3 Sunday Salary vs Points Correlation Analysis")
    print("=" * 60)
    
    # Load data
    df = load_week3_sunday_data()
    
    # Clean data
    df_clean = clean_salary_and_points_data(df)
    
    # Calculate correlation statistics
    correlation, slope, intercept, r_squared = calculate_correlation_stats(df_clean)
    
    # Analyze by position
    position_stats = analyze_by_position(df_clean)
    
    # Find value players and busts
    df_sorted = find_value_players_and_busts(df_clean)
    
    # Create visualizations
    create_salary_vs_points_plot(df_clean, slope, intercept)
    create_points_per_dollar_analysis(df_clean)
    
    # Summary
    print(f"\n🎯 SUMMARY:")
    print(f"   • Overall correlation between salary and points: {correlation[0]:.3f}")
    print(f"   • This explains {r_squared:.1%} of the variance in fantasy points")
    print(f"   • Higher salary players tend to score {'more' if correlation[0] > 0 else 'fewer'} points")
    
    if abs(correlation[0]) < 0.3:
        print(f"   • Weak correlation - salary is not a strong predictor of performance")
    elif abs(correlation[0]) < 0.6:
        print(f"   • Moderate correlation - salary has some predictive value")
    else:
        print(f"   • Strong correlation - salary is a good predictor of performance")

if __name__ == "__main__":
    main()

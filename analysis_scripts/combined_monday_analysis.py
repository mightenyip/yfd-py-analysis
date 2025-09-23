#!/usr/bin/env python3
"""
Combined Analysis of All Monday Night Football Data (Week 1-3)
Analyzing salary vs points correlation across all Monday games
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import os

def load_all_monday_data():
    """Load and combine all Monday data from Week 1-3."""
    
    print("📊 Loading all Monday Night Football data...")
    
    # Load Week 1 Monday data
    week1_file = "/Users/mightenyip/Documents/GitHub/yfd-py-test/data_csv/week1_monday_correct.csv"
    week1_df = pd.read_csv(week1_file)
    week1_df['week'] = 'Week 1'
    week1_df['day'] = 'Monday'
    week1_df['scrape_date'] = '2025-09-09'  # Approximate date
    
    # Load Week 2 Monday data
    week2_file = "/Users/mightenyip/Documents/GitHub/yfd-py-test/data_csv/week2_Mon.csv"
    week2_df = pd.read_csv(week2_file)
    
    # Load Week 3 Monday data
    week3_file = "/Users/mightenyip/Documents/GitHub/yfd-py-test/data_csv/week3_Mon.csv"
    week3_df = pd.read_csv(week3_file)
    
    print(f"   Week 1 Monday: {len(week1_df)} players")
    print(f"   Week 2 Monday: {len(week2_df)} players")
    print(f"   Week 3 Monday: {len(week3_df)} players")
    
    # Combine all data
    all_monday_data = pd.concat([week1_df, week2_df, week3_df], ignore_index=True)
    
    print(f"✅ Combined Monday data: {len(all_monday_data)} total players")
    
    return all_monday_data

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

def calculate_overall_correlation(df_active):
    """Calculate overall correlation statistics."""
    salary = df_active['salary_numeric']
    points = df_active['points_numeric']
    
    # Calculate correlation coefficient
    correlation = stats.pearsonr(salary, points)
    
    # Calculate R-squared
    r_squared = correlation[0] ** 2
    
    # Calculate slope and intercept for regression line
    slope, intercept, r_value, p_value, std_err = stats.linregress(salary, points)
    
    print(f"\n📈 OVERALL MONDAY CORRELATION ANALYSIS:")
    print(f"   Total active players: {len(df_active)}")
    print(f"   Pearson Correlation Coefficient: {correlation[0]:.4f}")
    print(f"   R-squared: {r_squared:.4f}")
    print(f"   P-value: {correlation[1]:.6f}")
    print(f"   Regression line: Points = {slope:.4f} * Salary + {intercept:.4f}")
    
    return correlation, slope, intercept, r_squared

def analyze_by_week(df_active):
    """Analyze correlation by individual week."""
    print(f"\n📊 CORRELATION BY WEEK:")
    
    week_stats = []
    for week in sorted(df_active['week'].unique()):
        week_data = df_active[df_active['week'] == week]
        if len(week_data) >= 5:  # Only analyze weeks with at least 5 players
            corr = stats.pearsonr(week_data['salary_numeric'], week_data['points_numeric'])
            r_squared = corr[0] ** 2
            week_stats.append({
                'week': week,
                'count': len(week_data),
                'correlation': corr[0],
                'r_squared': r_squared,
                'p_value': corr[1]
            })
            print(f"   {week}: r={corr[0]:.3f}, R²={r_squared:.3f}, n={len(week_data)}")
    
    return pd.DataFrame(week_stats)

def analyze_by_position(df_active):
    """Analyze correlation by position."""
    print(f"\n📊 CORRELATION BY POSITION:")
    
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

def find_top_performers(df_active):
    """Find top performers and value plays across all Mondays."""
    # Calculate points per dollar
    df_active['points_per_dollar'] = df_active['points_numeric'] / df_active['salary_numeric']
    
    print(f"\n💎 TOP 10 VALUE PLAYS (All Mondays - Highest Points per Dollar):")
    top_value = df_active.nlargest(10, 'points_per_dollar')
    for i, (_, row) in enumerate(top_value.iterrows(), 1):
        print(f"   {i:2d}. {row['player_name']:<20} | {row['week']:<6} | {row['position']:<3} | ${row['salary_numeric']:>4.0f} | {row['points_numeric']:>5.1f} pts | {row['points_per_dollar']:>5.3f} pts/$")
    
    print(f"\n🏆 TOP 10 HIGHEST SCORING GAMES (All Mondays):")
    top_scores = df_active.nlargest(10, 'points_numeric')
    for i, (_, row) in enumerate(top_scores.iterrows(), 1):
        print(f"   {i:2d}. {row['player_name']:<20} | {row['week']:<6} | {row['position']:<3} | ${row['salary_numeric']:>4.0f} | {row['points_numeric']:>5.1f} pts")
    
    print(f"\n💸 TOP 10 BUSTS (Min $20 salary - All Mondays):")
    min_salary = 20
    busts = df_active[df_active['salary_numeric'] >= min_salary].nsmallest(10, 'points_per_dollar')
    for i, (_, row) in enumerate(busts.iterrows(), 1):
        print(f"   {i:2d}. {row['player_name']:<20} | {row['week']:<6} | {row['position']:<3} | ${row['salary_numeric']:>4.0f} | {row['points_numeric']:>5.1f} pts | {row['points_per_dollar']:>5.3f} pts/$")
    
    return df_active

def create_comprehensive_visualizations(df_active, slope, intercept):
    """Create comprehensive visualizations for all Monday data."""
    
    # Set up the plotting style
    plt.style.use('default')
    
    # Create a figure with multiple subplots
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Monday Night Football: Salary vs Points Analysis (Week 1-3)', fontsize=16, fontweight='bold')
    
    # 1. Overall scatter plot with regression line
    ax1 = axes[0, 0]
    positions = df_active['position'].unique()
    colors = ['red', 'blue', 'green', 'orange', 'purple']
    position_colors = {pos: colors[i % len(colors)] for i, pos in enumerate(positions)}
    
    for position in positions:
        pos_data = df_active[df_active['position'] == position]
        ax1.scatter(pos_data['salary_numeric'], pos_data['points_numeric'], 
                   label=position, alpha=0.7, s=60, color=position_colors[position])
    
    # Add regression line
    x_range = np.linspace(df_active['salary_numeric'].min(), df_active['salary_numeric'].max(), 100)
    y_pred = slope * x_range + intercept
    correlation = stats.pearsonr(df_active['salary_numeric'], df_active['points_numeric'])[0]
    ax1.plot(x_range, y_pred, 'k--', linewidth=2, label=f'Regression (R² = {correlation**2:.3f})')
    
    ax1.set_xlabel('Salary ($)')
    ax1.set_ylabel('Fantasy Points')
    ax1.set_title('Overall Salary vs Points Correlation')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Points per dollar by position
    ax2 = axes[0, 1]
    df_active['points_per_dollar'] = df_active['points_numeric'] / df_active['salary_numeric']
    position_ppd = df_active.groupby('position')['points_per_dollar'].mean().sort_values(ascending=False)
    position_ppd.plot(kind='bar', ax=ax2, color='skyblue')
    ax2.set_title('Average Points per Dollar by Position')
    ax2.set_ylabel('Points per Dollar')
    ax2.tick_params(axis='x', rotation=45)
    
    # 3. Correlation by week
    ax3 = axes[1, 0]
    week_correlations = []
    week_labels = []
    for week in sorted(df_active['week'].unique()):
        week_data = df_active[df_active['week'] == week]
        if len(week_data) >= 5:
            corr = stats.pearsonr(week_data['salary_numeric'], week_data['points_numeric'])[0]
            week_correlations.append(corr)
            week_labels.append(week)
    
    ax3.bar(week_labels, week_correlations, color=['lightcoral', 'lightblue', 'lightgreen'])
    ax3.set_title('Correlation by Week')
    ax3.set_ylabel('Correlation Coefficient')
    ax3.set_ylim(0, 1)
    
    # 4. Distribution of points by position
    ax4 = axes[1, 1]
    df_active.boxplot(column='points_numeric', by='position', ax=ax4)
    ax4.set_title('Points Distribution by Position')
    ax4.set_xlabel('Position')
    ax4.set_ylabel('Fantasy Points')
    ax4.set_title('')
    
    plt.tight_layout()
    
    # Save plot
    plots_dir = "/Users/mightenyip/Documents/GitHub/yfd-py-test/plots_images"
    if not os.path.exists(plots_dir):
        os.makedirs(plots_dir)
    
    plt.savefig(f"{plots_dir}/combined_monday_analysis.png", dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"📊 Comprehensive plot saved to: {plots_dir}/combined_monday_analysis.png")

def analyze_monday_patterns(df_active):
    """Analyze specific Monday Night Football patterns."""
    print(f"\n🔍 MONDAY NIGHT FOOTBALL PATTERNS:")
    
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
    print("Monday Night Football Combined Analysis (Week 1-3)")
    print("=" * 70)
    print("Analyzing salary vs points correlation across all Monday games")
    print("=" * 70)
    
    # Load and combine all Monday data
    all_monday_data = load_all_monday_data()
    
    # Clean the data
    df_clean = clean_salary_and_points_data(all_monday_data)
    
    # Filter for active players only
    df_active = filter_active_players(df_clean)
    
    # Calculate overall correlation
    correlation, slope, intercept, r_squared = calculate_overall_correlation(df_active)
    
    # Analyze by week
    week_stats = analyze_by_week(df_active)
    
    # Analyze by position
    position_stats = analyze_by_position(df_active)
    
    # Find top performers
    df_with_ppd = find_top_performers(df_active)
    
    # Create visualizations
    create_comprehensive_visualizations(df_active, slope, intercept)
    
    # Analyze Monday patterns
    analyze_monday_patterns(df_active)
    
    # Final conclusions
    print(f"\n🎯 MONDAY NIGHT FOOTBALL CONCLUSIONS:")
    print(f"   • Total games analyzed: 3 Monday Night Football games")
    print(f"   • Total active players: {len(df_active)}")
    print(f"   • Overall correlation: {correlation[0]:.3f} (salary explains {r_squared:.1%} of variance)")
    
    if correlation[0] > 0.5:
        print(f"   • STRONG correlation - Monday Night Football shows clear salary/performance relationship")
    elif correlation[0] > 0.3:
        print(f"   • MODERATE correlation - Salary has some predictive value on Monday nights")
    else:
        print(f"   • WEAK correlation - Monday Night Football is more unpredictable")
    
    # Best position for value
    best_position = position_stats.loc[position_stats['correlation'].idxmin(), 'position']
    print(f"   • Best value position: {best_position} (lowest correlation = more unpredictable)")
    
    # Most consistent position
    position_cvs = df_active.groupby('position')['points_numeric'].apply(lambda x: x.std() / x.mean())
    most_consistent = position_cvs.idxmin()
    print(f"   • Most consistent position: {most_consistent}")

if __name__ == "__main__":
    main()

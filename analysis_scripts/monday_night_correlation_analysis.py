#!/usr/bin/env python3
"""
Monday Night Football Correlation Analysis
Analyzes the relationship between points and salary for Week 2 Monday data.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.stats import pearsonr, spearmanr
import warnings
warnings.filterwarnings('ignore')

def load_and_clean_data():
    """Load and clean the Monday Night Football data."""
    print("📊 Loading Monday Night Football data...")
    
    # Load the data
    df = pd.read_csv('/Users/mightenyip/Documents/GitHub/yfd-py-test/data_csv/week2_Mon.csv')
    
    print(f"✅ Loaded {len(df)} players from Monday Night Football")
    
    # Clean salary data - remove $ and convert to numeric
    df['salary_clean'] = df['salary'].str.replace('$', '').astype(float)
    
    # Clean points data - convert to numeric
    df['points_clean'] = pd.to_numeric(df['points'], errors='coerce')
    
    # Clean FPPG data - convert to numeric
    df['fppg_clean'] = pd.to_numeric(df['fppg'], errors='coerce')
    
    # Remove players with missing data
    df_clean = df.dropna(subset=['salary_clean', 'points_clean']).copy()
    
    # Remove inactive players (0 points)
    df_active = df_clean[df_clean['points_clean'] > 0].copy()
    
    print(f"🧹 After cleaning: {len(df_clean)} players with complete data")
    print(f"🏃 After removing inactive players: {len(df_active)} active players")
    
    return df_active

def calculate_correlations(df):
    """Calculate various correlation metrics."""
    print("\n🔍 CORRELATION ANALYSIS")
    print("=" * 50)
    
    # Overall correlations
    pearson_corr, pearson_p = pearsonr(df['salary_clean'], df['points_clean'])
    spearman_corr, spearman_p = spearmanr(df['salary_clean'], df['points_clean'])
    
    print(f"📈 Overall Correlations (n={len(df)}):")
    print(f"   Pearson Correlation:  {pearson_corr:.4f} (p-value: {pearson_p:.4f})")
    print(f"   Spearman Correlation: {spearman_corr:.4f} (p-value: {spearman_p:.4f})")
    
    # Interpret correlation strength
    def interpret_correlation(corr):
        abs_corr = abs(corr)
        if abs_corr >= 0.7:
            return "Strong"
        elif abs_corr >= 0.5:
            return "Moderate"
        elif abs_corr >= 0.3:
            return "Weak"
        else:
            return "Very Weak"
    
    print(f"\n📊 Correlation Interpretation:")
    print(f"   Pearson:  {interpret_correlation(pearson_corr)} correlation")
    print(f"   Spearman: {interpret_correlation(spearman_corr)} correlation")
    
    return pearson_corr, spearman_corr

def analyze_by_position(df):
    """Analyze correlations by position."""
    print(f"\n🏈 POSITION-SPECIFIC ANALYSIS")
    print("=" * 50)
    
    position_correlations = {}
    
    for position in df['position'].unique():
        pos_data = df[df['position'] == position]
        if len(pos_data) >= 3:  # Need at least 3 players for meaningful correlation
            pearson_corr, pearson_p = pearsonr(pos_data['salary_clean'], pos_data['points_clean'])
            spearman_corr, spearman_p = spearmanr(pos_data['salary_clean'], pos_data['points_clean'])
            
            position_correlations[position] = {
                'pearson': pearson_corr,
                'spearman': spearman_corr,
                'count': len(pos_data),
                'avg_salary': pos_data['salary_clean'].mean(),
                'avg_points': pos_data['points_clean'].mean()
            }
            
            print(f"📊 {position} ({len(pos_data)} players):")
            print(f"   Pearson:  {pearson_corr:.4f} (p: {pearson_p:.4f})")
            print(f"   Spearman: {spearman_corr:.4f} (p: {spearman_p:.4f})")
            print(f"   Avg Salary: ${pos_data['salary_clean'].mean():.1f}")
            print(f"   Avg Points: {pos_data['points_clean'].mean():.2f}")
            print()
    
    return position_correlations

def analyze_value_players(df):
    """Identify value players (high points per dollar)."""
    print(f"\n💰 VALUE ANALYSIS")
    print("=" * 50)
    
    # Calculate points per dollar
    df['points_per_dollar'] = df['points_clean'] / df['salary_clean']
    
    # Top value players
    top_value = df.nlargest(10, 'points_per_dollar')
    print("🏆 Top 10 Value Players (Points per Dollar):")
    for i, (_, player) in enumerate(top_value.iterrows(), 1):
        print(f"   {i:2d}. {player['player_name']:<20} | {player['position']:<3} | "
              f"${player['salary_clean']:>5.0f} | {player['points_clean']:>5.2f} pts | "
              f"{player['points_per_dollar']:>5.3f} pts/$")
    
    # Worst value players (among those who scored points)
    active_players = df[df['points_clean'] > 0]
    if len(active_players) > 0:
        worst_value = active_players.nsmallest(5, 'points_per_dollar')
        print(f"\n📉 Worst Value Players (among active players):")
        for i, (_, player) in enumerate(worst_value.iterrows(), 1):
            print(f"   {i:2d}. {player['player_name']:<20} | {player['position']:<3} | "
                  f"${player['salary_clean']:>5.0f} | {player['points_clean']:>5.2f} pts | "
                  f"{player['points_per_dollar']:>5.3f} pts/$")
    
    return df

def create_visualizations(df):
    """Create correlation visualizations."""
    print(f"\n📊 Creating visualizations...")
    
    # Set up the plotting style
    plt.style.use('default')
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Monday Night Football: Points vs Salary Analysis (Active Players Only)', fontsize=16, fontweight='bold')
    
    # 1. Overall scatter plot
    ax1 = axes[0, 0]
    scatter = ax1.scatter(df['salary_clean'], df['points_clean'], 
                         c=df['points_clean'], cmap='viridis', alpha=0.7, s=60)
    ax1.set_xlabel('Salary ($)')
    ax1.set_ylabel('Points')
    ax1.set_title('Points vs Salary (All Players)')
    ax1.grid(True, alpha=0.3)
    
    # Add correlation coefficient
    corr_coef = df['salary_clean'].corr(df['points_clean'])
    ax1.text(0.05, 0.95, f'r = {corr_coef:.3f}', transform=ax1.transAxes, 
             bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8),
             fontsize=12, fontweight='bold')
    
    # Add colorbar
    plt.colorbar(scatter, ax=ax1, label='Points')
    
    # 2. Position-specific scatter plot
    ax2 = axes[0, 1]
    colors = {'QB': 'red', 'RB': 'blue', 'WR': 'green', 'TE': 'orange', 'DEF': 'purple'}
    # Order positions: QB first, DEF last
    position_order = ['QB', 'RB', 'WR', 'TE', 'DEF']
    for position in position_order:
        if position in df['position'].unique():
            pos_data = df[df['position'] == position]
            ax2.scatter(pos_data['salary_clean'], pos_data['points_clean'], 
                       label=position, color=colors.get(position, 'gray'), alpha=0.7, s=60)
    
    ax2.set_xlabel('Salary ($)')
    ax2.set_ylabel('Points')
    ax2.set_title('Points vs Salary by Position')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. Points per dollar by position
    ax3 = axes[1, 0]
    df['points_per_dollar'] = df['points_clean'] / df['salary_clean']
    # Order positions: QB first, DEF last
    position_order = ['QB', 'RB', 'WR', 'TE', 'DEF']
    position_ppd = df.groupby('position')['points_per_dollar'].mean()
    position_ppd = position_ppd.reindex([pos for pos in position_order if pos in position_ppd.index])
    
    bars = ax3.bar(position_ppd.index, position_ppd.values, 
                   color=[colors.get(pos, 'gray') for pos in position_ppd.index])
    ax3.set_xlabel('Position')
    ax3.set_ylabel('Average Points per Dollar')
    ax3.set_title('Average Value by Position')
    ax3.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for bar, value in zip(bars, position_ppd.values):
        ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.001,
                f'{value:.3f}', ha='center', va='bottom', fontweight='bold')
    
    # 4. Salary distribution by position
    ax4 = axes[1, 1]
    position_salaries = [df[df['position'] == pos]['salary_clean'].values for pos in position_ppd.index]
    
    bp = ax4.boxplot(position_salaries, labels=position_ppd.index, patch_artist=True)
    for patch, pos in zip(bp['boxes'], position_ppd.index):
        patch.set_facecolor(colors.get(pos, 'gray'))
        patch.set_alpha(0.7)
    
    ax4.set_xlabel('Position')
    ax4.set_ylabel('Salary ($)')
    ax4.set_title('Salary Distribution by Position')
    ax4.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    
    # Save the plot
    output_path = '/Users/mightenyip/Documents/GitHub/yfd-py-test/plots_images/monday_night_correlation_analysis.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ Visualization saved to: {output_path}")
    
    plt.show()

def generate_summary_statistics(df):
    """Generate comprehensive summary statistics."""
    print(f"\n📈 SUMMARY STATISTICS")
    print("=" * 50)
    
    # Basic stats
    print(f"📊 Dataset Overview (Active Players Only):")
    print(f"   Active Players Analyzed: {len(df)}")
    print(f"   Salary Range: ${df['salary_clean'].min():.0f} - ${df['salary_clean'].max():.0f}")
    print(f"   Points Range: {df['points_clean'].min():.2f} - {df['points_clean'].max():.2f}")
    
    # Position breakdown
    print(f"\n🏈 Position Breakdown:")
    pos_counts = df['position'].value_counts()
    for pos, count in pos_counts.items():
        avg_salary = df[df['position'] == pos]['salary_clean'].mean()
        avg_points = df[df['position'] == pos]['points_clean'].mean()
        print(f"   {pos}: {count} players | Avg Salary: ${avg_salary:.1f} | Avg Points: {avg_points:.2f}")
    
    # Correlation summary
    overall_corr = df['salary_clean'].corr(df['points_clean'])
    print(f"\n🔗 Correlation Summary:")
    print(f"   Overall Points-Salary Correlation: {overall_corr:.4f}")
    
    if overall_corr > 0.3:
        print(f"   ✅ Positive correlation: Higher salary generally predicts higher points")
    elif overall_corr < -0.3:
        print(f"   ❌ Negative correlation: Higher salary generally predicts lower points")
    else:
        print(f"   ⚖️  Weak correlation: Salary is not a strong predictor of points")
    
    # Value insights
    df['points_per_dollar'] = df['points_clean'] / df['salary_clean']
    avg_value = df['points_per_dollar'].mean()
    print(f"\n💰 Value Insights:")
    print(f"   Average Points per Dollar: {avg_value:.4f}")
    print(f"   Best Value Position: {df.groupby('position')['points_per_dollar'].mean().idxmax()}")
    print(f"   Worst Value Position: {df.groupby('position')['points_per_dollar'].mean().idxmin()}")

def main():
    """Main analysis function."""
    print("🏈 MONDAY NIGHT FOOTBALL CORRELATION ANALYSIS")
    print("=" * 60)
    print("Analyzing the relationship between points and salary for Week 2 Monday data (Active Players Only)")
    print("=" * 60)
    
    # Load and clean data
    df = load_and_clean_data()
    
    # Calculate correlations
    pearson_corr, spearman_corr = calculate_correlations(df)
    
    # Analyze by position
    position_correlations = analyze_by_position(df)
    
    # Analyze value players
    df = analyze_value_players(df)
    
    # Create visualizations
    create_visualizations(df)
    
    # Generate summary statistics
    generate_summary_statistics(df)
    
    print(f"\n🎉 Analysis Complete!")
    print(f"📁 Results saved to plots_images/monday_night_correlation_analysis.png")

if __name__ == "__main__":
    main()

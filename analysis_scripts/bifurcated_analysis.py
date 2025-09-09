#!/usr/bin/env python3
"""
Bifurcated analysis of salary vs points correlation:
1) Top half performers analysis
2) Highest salaried players analysis
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy import stats

def create_updated_plots(csv_file="modeling_dataset_2025_week1.csv"):
    """
    Create plots with updated x-axis scaling for DEF (max $20) and TE (max $30)
    """
    print(f"📊 Creating updated plots with correct x-axis scaling")
    
    # Read the data
    df = pd.read_csv(csv_file)
    
    # Set up the plotting style
    plt.style.use('default')
    sns.set_palette("husl")
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('Fantasy Points vs Salary by Position (Updated X-Axis Scaling)', fontsize=16, fontweight='bold')
    
    positions = ['QB', 'RB', 'WR', 'TE', 'DEF']
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    
    # Plot each position
    for i, position in enumerate(positions):
        row = i // 3
        col = i % 3
        ax = axes[row, col]
        
        # Filter data for this position
        pos_data = df[df['position'] == position].copy()
        
        if len(pos_data) > 0:
            # Create scatter plot
            scatter = ax.scatter(pos_data['salary'], pos_data['points'], 
                               alpha=0.7, s=60, c=colors[i], edgecolors='black', linewidth=0.5)
            
            # Add trend line
            if len(pos_data) > 1:
                z = np.polyfit(pos_data['salary'], pos_data['points'], 1)
                p = np.poly1d(z)
                ax.plot(pos_data['salary'], p(pos_data['salary']), 
                       color='red', linestyle='--', alpha=0.8, linewidth=2)
                
                # Calculate correlation
                corr, p_value = stats.pearsonr(pos_data['salary'], pos_data['points'])
                ax.text(0.05, 0.95, f'Correlation: {corr:.3f}\nP-value: {p_value:.3f}', 
                       transform=ax.transAxes, fontsize=10, 
                       bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
            
            # Customize the plot
            ax.set_xlabel('Salary ($)', fontsize=12)
            ax.set_ylabel('Fantasy Points', fontsize=12)
            ax.set_title(f'{position} (n={len(pos_data)})', fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3)
            
            # Set position-specific axis limits
            if position == 'DEF':
                ax.set_xlim(9, 21)  # DEF max $20
            elif position == 'TE':
                ax.set_xlim(9, 31)  # TE max $30
            else:
                ax.set_xlim(9, 41)  # Others max $40
            
            ax.set_ylim(-4, 40)
            
            # Add some statistics
            avg_salary = pos_data['salary'].mean()
            avg_points = pos_data['points'].mean()
            ax.axhline(y=avg_points, color='gray', linestyle=':', alpha=0.5)
            ax.axvline(x=avg_salary, color='gray', linestyle=':', alpha=0.5)
    
    # Remove the empty subplot
    axes[1, 2].remove()
    
    # Add overall correlation plot in the bottom right
    ax_overall = fig.add_subplot(2, 3, 6)
    
    # Color code by position
    for i, position in enumerate(positions):
        pos_data = df[df['position'] == position]
        ax_overall.scatter(pos_data['salary'], pos_data['points'], 
                          alpha=0.6, s=50, c=colors[i], label=position, edgecolors='black', linewidth=0.3)
    
    # Overall trend line
    z = np.polyfit(df['salary'], df['points'], 1)
    p = np.poly1d(z)
    ax_overall.plot(df['salary'], p(df['salary']), 
                   color='red', linestyle='--', alpha=0.8, linewidth=3)
    
    # Overall correlation
    corr, p_value = stats.pearsonr(df['salary'], df['points'])
    ax_overall.text(0.05, 0.95, f'Overall Correlation: {corr:.3f}\nP-value: {p_value:.3f}', 
                   transform=ax_overall.transAxes, fontsize=10, 
                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    ax_overall.set_xlabel('Salary ($)', fontsize=12)
    ax_overall.set_ylabel('Fantasy Points', fontsize=12)
    ax_overall.set_title('All Positions Combined', fontsize=14, fontweight='bold')
    ax_overall.legend(loc='upper left', fontsize=10)
    ax_overall.grid(True, alpha=0.3)
    ax_overall.set_xlim(9, 41)
    ax_overall.set_ylim(-4, 40)
    
    plt.tight_layout()
    
    # Save the plot
    output_file = "updated_salary_vs_points_analysis.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ Updated plot saved as: {output_file}")
    
    plt.show()

def analysis_1_top_half_performers(csv_file="modeling_dataset_2025_week1.csv"):
    """
    Analysis 1: Top half performers - does correlation change?
    """
    print(f"\n🔍 ANALYSIS 1: Top Half Performers")
    print(f"=" * 50)
    
    # Read the data
    df = pd.read_csv(csv_file)
    
    # Define top half counts
    top_half_counts = {
        'QB': 13,   # Top 13 of 25
        'RB': 33,   # Top 33 of 65
        'WR': 45,   # Top 45 of 90
        'TE': 23,   # Top 23 of 45
        'DEF': 13   # Top 13 of 26
    }
    
    top_half_data = []
    
    print(f"Original vs Top Half Comparison:")
    print(f"{'Position':<6} {'Original':<10} {'Top Half':<10} {'Original Corr':<15} {'Top Half Corr':<15} {'Change':<10}")
    print(f"{'-'*70}")
    
    for position in ['QB', 'RB', 'WR', 'TE', 'DEF']:
        # Get original data
        original_data = df[df['position'] == position]
        original_corr, _ = stats.pearsonr(original_data['salary'], original_data['points'])
        
        # Get top half data
        top_half_count = top_half_counts[position]
        top_half_pos = original_data.nlargest(top_half_count, 'points')
        top_half_corr, _ = stats.pearsonr(top_half_pos['salary'], top_half_pos['points'])
        
        # Calculate change
        change = top_half_corr - original_corr
        
        print(f"{position:<6} {len(original_data):<10} {len(top_half_pos):<10} {original_corr:<15.4f} {top_half_corr:<15.4f} {change:>+8.4f}")
        
        top_half_data.append(top_half_pos)
    
    # Combine top half data
    top_half_df = pd.concat(top_half_data, ignore_index=True)
    
    # Overall correlation comparison
    original_overall_corr, _ = stats.pearsonr(df['salary'], df['points'])
    top_half_overall_corr, _ = stats.pearsonr(top_half_df['salary'], top_half_df['points'])
    
    print(f"\nOverall Correlation:")
    print(f"Original (all players): {original_overall_corr:.4f}")
    print(f"Top Half Only:          {top_half_overall_corr:.4f}")
    print(f"Change:                 {top_half_overall_corr - original_overall_corr:+.4f}")
    
    # Save top half dataset
    top_half_df.to_csv("top_half_performers_2025_week1.csv", index=False)
    print(f"\n✅ Top half performers dataset saved as: top_half_performers_2025_week1.csv")
    
    return top_half_df

def analysis_2_highest_salaried(original_file="yahoo_daily_fantasy_2025_week1_completed_page.csv"):
    """
    Analysis 2: Highest salaried players from original 764 players
    """
    print(f"\n💰 ANALYSIS 2: Highest Salaried Players")
    print(f"=" * 50)
    
    # Read the original full dataset
    try:
        df = pd.read_csv(original_file)
        print(f"✅ Loaded {len(df)} players from original dataset")
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return
    
    # Clean the data
    def clean_salary(salary_str):
        if pd.isna(salary_str) or salary_str == '':
            return 0
        return int(str(salary_str).replace('$', '').replace(',', ''))
    
    def clean_points(points_str):
        if pd.isna(points_str) or points_str == '':
            return 0
        try:
            return float(str(points_str))
        except:
            return 0
    
    df['salary_numeric'] = df['salary'].apply(clean_salary)
    df['points_numeric'] = df['points'].apply(clean_points)
    
    # Define highest salaried counts
    highest_salaried_counts = {
        'QB': 25,
        'RB': 65,
        'WR': 90,
        'TE': 45,
        'DEF': 26  # All defenses
    }
    
    highest_salaried_data = []
    
    print(f"Highest Salaried Players Analysis:")
    print(f"{'Position':<6} {'Count':<6} {'Avg Salary':<12} {'Avg Points':<12} {'Points/$':<10} {'Correlation':<12}")
    print(f"{'-'*70}")
    
    for position in ['QB', 'RB', 'WR', 'TE', 'DEF']:
        # Get position data
        pos_data = df[df['position'] == position].copy()
        
        # Get highest salaried players
        count = highest_salaried_counts[position]
        if position == 'DEF':
            # All defenses
            highest_salaried_pos = pos_data.copy()
        else:
            # Top N by salary
            highest_salaried_pos = pos_data.nlargest(count, 'salary_numeric')
        
        # Calculate statistics
        avg_salary = highest_salaried_pos['salary_numeric'].mean()
        avg_points = highest_salaried_pos['points_numeric'].mean()
        points_per_dollar = avg_points / avg_salary if avg_salary > 0 else 0
        
        # Calculate correlation
        if len(highest_salaried_pos) > 1:
            corr, _ = stats.pearsonr(highest_salaried_pos['salary_numeric'], highest_salaried_pos['points_numeric'])
        else:
            corr = 0
        
        print(f"{position:<6} {len(highest_salaried_pos):<6} ${avg_salary:<11.2f} {avg_points:<11.2f} {points_per_dollar:<9.3f} {corr:<11.4f}")
        
        highest_salaried_data.append(highest_salaried_pos)
    
    # Combine highest salaried data
    highest_salaried_df = pd.concat(highest_salaried_data, ignore_index=True)
    
    # Overall statistics
    overall_avg_salary = highest_salaried_df['salary_numeric'].mean()
    overall_avg_points = highest_salaried_df['points_numeric'].mean()
    overall_points_per_dollar = overall_avg_points / overall_avg_salary
    overall_corr, _ = stats.pearsonr(highest_salaried_df['salary_numeric'], highest_salaried_df['points_numeric'])
    
    print(f"\nOverall Statistics (Highest Salaried):")
    print(f"Total players: {len(highest_salaried_df)}")
    print(f"Average salary: ${overall_avg_salary:.2f}")
    print(f"Average points: {overall_avg_points:.2f}")
    print(f"Points per dollar: {overall_points_per_dollar:.3f}")
    print(f"Correlation: {overall_corr:.4f}")
    
    # Create clean dataset for analysis
    highest_salaried_clean = highest_salaried_df[['player_name', 'position', 'salary_numeric', 'points_numeric', 'fppg']].copy()
    highest_salaried_clean = highest_salaried_clean.rename(columns={
        'salary_numeric': 'salary',
        'points_numeric': 'points'
    })
    
    # Save highest salaried dataset
    highest_salaried_clean.to_csv("highest_salaried_players_2025_week1.csv", index=False)
    print(f"\n✅ Highest salaried players dataset saved as: highest_salaried_players_2025_week1.csv")
    
    return highest_salaried_clean

def compare_analyses():
    """
    Compare the three approaches: original, top half, highest salaried
    """
    print(f"\n📊 COMPARISON OF ALL THREE APPROACHES")
    print(f"=" * 60)
    
    # Read all three datasets
    original = pd.read_csv("modeling_dataset_2025_week1.csv")
    top_half = pd.read_csv("top_half_performers_2025_week1.csv")
    highest_salaried = pd.read_csv("highest_salaried_players_2025_week1.csv")
    
    print(f"{'Approach':<20} {'Players':<8} {'Avg Salary':<12} {'Avg Points':<12} {'Points/$':<10} {'Correlation':<12}")
    print(f"{'-'*80}")
    
    datasets = [
        ("Original (Top Points)", original),
        ("Top Half Performers", top_half),
        ("Highest Salaried", highest_salaried)
    ]
    
    for name, df in datasets:
        avg_salary = df['salary'].mean()
        avg_points = df['points'].mean()
        points_per_dollar = avg_points / avg_salary
        corr, _ = stats.pearsonr(df['salary'], df['points'])
        
        print(f"{name:<20} {len(df):<8} ${avg_salary:<11.2f} {avg_points:<11.2f} {points_per_dollar:<9.3f} {corr:<11.4f}")

if __name__ == "__main__":
    # Create updated plots with correct x-axis scaling
    create_updated_plots()
    
    # Analysis 1: Top half performers
    top_half_df = analysis_1_top_half_performers()
    
    # Analysis 2: Highest salaried players
    highest_salaried_df = analysis_2_highest_salaried()
    
    # Compare all approaches
    compare_analyses()

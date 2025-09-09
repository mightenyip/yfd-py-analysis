#!/usr/bin/env python3
"""
Analyze QB correlation and value metrics with and without the top 2 highest salaried QBs
"""

import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns

def analyze_qb_without_top2(csv_file="modeling_dataset_2025_week1.csv"):
    """
    Analyze QB data with and without Josh Allen and Lamar Jackson
    """
    print("🏈 QB Analysis: With and Without Top 2 Highest Salaried QBs")
    print("=" * 70)
    
    # Read the data
    df = pd.read_csv(csv_file)
    
    # Filter for QBs only
    qb_data = df[df['position'] == 'QB'].copy()
    print(f"Total QBs in dataset: {len(qb_data)}")
    
    # Calculate value (points per dollar)
    qb_data['value'] = qb_data['points'] / qb_data['salary']
    
    # Sort by salary to identify top 2 highest salaried
    qb_sorted = qb_data.sort_values('salary', ascending=False)
    print(f"\nTop 5 highest salaried QBs:")
    for i, (_, qb) in enumerate(qb_sorted.head().iterrows()):
        print(f"  {i+1}. {qb['player_name']:<20} | ${qb['salary']:<3} | {qb['points']:>6.2f} pts | {qb['value']:>6.3f} pts/$")
    
    # Identify the top 2 highest salaried QBs
    top2_salaried = qb_sorted.head(2)
    top2_names = top2_salaried['player_name'].tolist()
    print(f"\nTop 2 highest salaried QBs to remove: {top2_names}")
    
    # Create dataset without top 2
    qb_without_top2 = qb_data[~qb_data['player_name'].isin(top2_names)].copy()
    print(f"QBs remaining after removing top 2: {len(qb_without_top2)}")
    
    # Calculate metrics for both datasets
    print(f"\n📊 COMPARISON OF QB METRICS:")
    print(f"{'Metric':<25} {'With Top 2':<15} {'Without Top 2':<15} {'Change':<15}")
    print(f"{'-'*70}")
    
    # Sample size
    print(f"{'Sample Size':<25} {len(qb_data):<15} {len(qb_without_top2):<15} {len(qb_without_top2)-len(qb_data):>+13}")
    
    # Average salary
    avg_salary_with = qb_data['salary'].mean()
    avg_salary_without = qb_without_top2['salary'].mean()
    salary_change = avg_salary_without - avg_salary_with
    print(f"{'Average Salary':<25} ${avg_salary_with:<14.2f} ${avg_salary_without:<14.2f} ${salary_change:>+12.2f}")
    
    # Average points
    avg_points_with = qb_data['points'].mean()
    avg_points_without = qb_without_top2['points'].mean()
    points_change = avg_points_without - avg_points_with
    print(f"{'Average Points':<25} {avg_points_with:<14.2f} {avg_points_without:<14.2f} {points_change:>+12.2f}")
    
    # Average value (points per dollar)
    avg_value_with = qb_data['value'].mean()
    avg_value_without = qb_without_top2['value'].mean()
    value_change = avg_value_without - avg_value_with
    print(f"{'Average Value (pts/$)':<25} {avg_value_with:<14.3f} {avg_value_without:<14.3f} {value_change:>+12.3f}")
    
    # Correlation with salary
    corr_with, p_value_with = stats.pearsonr(qb_data['salary'], qb_data['points'])
    corr_without, p_value_without = stats.pearsonr(qb_without_top2['salary'], qb_without_top2['points'])
    corr_change = corr_without - corr_with
    print(f"{'Salary-Points Correlation':<25} {corr_with:<14.4f} {corr_without:<14.4f} {corr_change:>+12.4f}")
    
    # P-values
    print(f"{'P-value':<25} {p_value_with:<14.4f} {p_value_without:<14.4f} {p_value_without-p_value_with:>+12.4f}")
    
    # Best value players in each dataset
    print(f"\n💎 TOP 5 VALUE PLAYERS (Points per Dollar):")
    print(f"\nWith Top 2 Highest Salaried:")
    top_value_with = qb_data.nlargest(5, 'value')
    for i, (_, qb) in enumerate(top_value_with.iterrows()):
        print(f"  {i+1}. {qb['player_name']:<20} | ${qb['salary']:<3} | {qb['points']:>6.2f} pts | {qb['value']:>6.3f} pts/$")
    
    print(f"\nWithout Top 2 Highest Salaried:")
    top_value_without = qb_without_top2.nlargest(5, 'value')
    for i, (_, qb) in enumerate(top_value_without.iterrows()):
        print(f"  {i+1}. {qb['player_name']:<20} | ${qb['salary']:<3} | {qb['points']:>6.2f} pts | {qb['value']:>6.3f} pts/$")
    
    # Create visualization
    create_comparison_plot(qb_data, qb_without_top2, top2_names)
    
    return qb_data, qb_without_top2

def create_comparison_plot(qb_with, qb_without, removed_players):
    """
    Create a comparison plot showing the difference
    """
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle('QB Analysis: With vs Without Top 2 Highest Salaried QBs', fontsize=16, fontweight='bold')
    
    # Plot 1: With top 2
    ax1 = axes[0]
    scatter1 = ax1.scatter(qb_with['salary'], qb_with['points'], 
                          alpha=0.7, s=60, c='blue', edgecolors='black', linewidth=0.5)
    
    # Highlight the removed players
    removed_data = qb_with[qb_with['player_name'].isin(removed_players)]
    ax1.scatter(removed_data['salary'], removed_data['points'], 
               alpha=1.0, s=100, c='red', edgecolors='black', linewidth=2, 
               label=f'Removed: {", ".join(removed_players)}')
    
    # Add trend line
    z1 = np.polyfit(qb_with['salary'], qb_with['points'], 1)
    p1 = np.poly1d(z1)
    ax1.plot(qb_with['salary'], p1(qb_with['salary']), 
             color='red', linestyle='--', alpha=0.8, linewidth=2)
    
    # Calculate correlation
    corr1, p_val1 = stats.pearsonr(qb_with['salary'], qb_with['points'])
    ax1.text(0.05, 0.95, f'Correlation: {corr1:.3f}\nP-value: {p_val1:.3f}\nAvg Value: {qb_with["value"].mean():.3f}', 
             transform=ax1.transAxes, fontsize=10, 
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    ax1.set_xlabel('Salary ($)', fontsize=12)
    ax1.set_ylabel('Fantasy Points', fontsize=12)
    ax1.set_title(f'With Top 2 (n={len(qb_with)})', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # Plot 2: Without top 2
    ax2 = axes[1]
    scatter2 = ax2.scatter(qb_without['salary'], qb_without['points'], 
                          alpha=0.7, s=60, c='green', edgecolors='black', linewidth=0.5)
    
    # Add trend line
    z2 = np.polyfit(qb_without['salary'], qb_without['points'], 1)
    p2 = np.poly1d(z2)
    ax2.plot(qb_without['salary'], p2(qb_without['salary']), 
             color='red', linestyle='--', alpha=0.8, linewidth=2)
    
    # Calculate correlation
    corr2, p_val2 = stats.pearsonr(qb_without['salary'], qb_without['points'])
    ax2.text(0.05, 0.95, f'Correlation: {corr2:.3f}\nP-value: {p_val2:.3f}\nAvg Value: {qb_without["value"].mean():.3f}', 
             transform=ax2.transAxes, fontsize=10, 
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    ax2.set_xlabel('Salary ($)', fontsize=12)
    ax2.set_ylabel('Fantasy Points', fontsize=12)
    ax2.set_title(f'Without Top 2 (n={len(qb_without)})', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    # Set consistent axis limits
    for ax in axes:
        ax.set_xlim(19, 41)
        ax.set_ylim(8, 40)
    
    plt.tight_layout()
    
    # Save the plot
    output_file = "qb_analysis_with_without_top2.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\n✅ Comparison plot saved as: {output_file}")
    
    plt.show()

if __name__ == "__main__":
    qb_with, qb_without = analyze_qb_without_top2()

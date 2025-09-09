#!/usr/bin/env python3
"""
Create final plots with updated x-axis scaling and formatting
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy import stats

def create_final_plots(csv_file="modeling_dataset_2025_week1.csv"):
    """
    Create final plots with specific x-axis ranges and formatting
    """
    print(f"📊 Creating final plots with updated x-axis formatting")
    
    # Read the data
    df = pd.read_csv(csv_file)
    
    # Set up the plotting style
    plt.style.use('default')
    sns.set_palette("husl")
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('Fantasy Points vs Salary by Position (Final Analysis)', fontsize=16, fontweight='bold')
    
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
            
            # Set position-specific axis limits and ticks
            if position == 'QB':
                ax.set_xlim(19, 41)
                ax.set_xticks(range(20, 41, 5))  # 20, 25, 30, 35, 40
            elif position == 'TE':
                ax.set_xlim(9, 31)
                ax.set_xticks(range(10, 31, 5))  # 10, 15, 20, 25, 30
            elif position == 'DEF':
                ax.set_xlim(9, 21)
                ax.set_xticks(range(10, 21, 5))  # 10, 15, 20
            else:
                ax.set_xlim(9, 41)
                ax.set_xticks(range(10, 41, 5))  # 10, 15, 20, 25, 30, 35, 40
            
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
    ax_overall.set_xticks(range(10, 41, 5))
    ax_overall.set_ylim(-4, 40)
    
    plt.tight_layout()
    
    # Save the plot
    output_file = "final_salary_vs_points_analysis.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ Final plot saved as: {output_file}")
    
    plt.show()

def create_value_plot_for_readme(csv_file="modeling_dataset_2025_week1.csv"):
    """
    Create the value analysis plot for the README
    """
    print(f"\n💎 Creating value analysis plot for README")
    
    # Read the data
    df = pd.read_csv(csv_file)
    
    # Calculate value (points per dollar)
    df['value'] = df['points'] / df['salary']
    df['value'] = df['value'].replace([float('inf'), -float('inf')], 0)
    
    # Create the plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle('Value Analysis: Points per Dollar by Position', fontsize=16, fontweight='bold')
    
    # Box plot of value by position
    positions = ['QB', 'RB', 'WR', 'TE', 'DEF']
    value_data = [df[df['position'] == pos]['value'].values for pos in positions]
    
    bp = ax1.boxplot(value_data, tick_labels=positions, patch_artist=True)
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    
    ax1.set_ylabel('Points per Dollar', fontsize=12)
    ax1.set_title('Value Distribution by Position', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    
    # Scatter plot: Value vs Salary
    for i, position in enumerate(positions):
        pos_data = df[df['position'] == position]
        ax2.scatter(pos_data['salary'], pos_data['value'], 
                   alpha=0.7, s=60, c=colors[i], label=position, edgecolors='black', linewidth=0.5)
    
    ax2.set_xlabel('Salary ($)', fontsize=12)
    ax2.set_ylabel('Points per Dollar', fontsize=12)
    ax2.set_title('Value vs Salary', fontsize=14, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save the plot
    output_file = "value_analysis_for_readme.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ Value analysis plot saved as: {output_file}")
    
    plt.show()
    
    return output_file

if __name__ == "__main__":
    # Create final plots with updated formatting
    create_final_plots()
    
    # Create value plot for README
    value_plot_file = create_value_plot_for_readme()

#!/usr/bin/env python3
"""
Create plots showing fantasy points as a function of salary for all positions
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy import stats

def create_salary_vs_points_plots(csv_file="modeling_dataset_2025_week1.csv"):
    """
    Create comprehensive plots showing fantasy points vs salary by position
    """
    print(f"📊 Creating salary vs points plots from {csv_file}")
    
    # Read the data
    try:
        df = pd.read_csv(csv_file)
        print(f"✅ Loaded {len(df)} players from {csv_file}")
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return
    
    # Set up the plotting style
    plt.style.use('default')
    sns.set_palette("husl")
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('Fantasy Points vs Salary by Position (2025 Week 1)', fontsize=16, fontweight='bold')
    
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
            
            # Set consistent axis limits
            ax.set_xlim(9, 41)
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
    output_file = "salary_vs_points_analysis.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ Plot saved as: {output_file}")
    
    # Show the plot
    plt.show()
    
    return df

def create_value_analysis_plot(csv_file="modeling_dataset_2025_week1.csv"):
    """
    Create a plot showing value (points per dollar) by position
    """
    print(f"\n💎 Creating value analysis plot")
    
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
    
    bp = ax1.boxplot(value_data, labels=positions, patch_artist=True)
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
    output_file = "value_analysis.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ Value analysis plot saved as: {output_file}")
    
    plt.show()

def print_correlation_summary(csv_file="modeling_dataset_2025_week1.csv"):
    """
    Print detailed correlation analysis
    """
    print(f"\n📈 Detailed Correlation Analysis:")
    
    df = pd.read_csv(csv_file)
    
    print(f"\nOverall Dataset:")
    print(f"Total players: {len(df)}")
    print(f"Salary range: ${df['salary'].min()} - ${df['salary'].max()}")
    print(f"Points range: {df['points'].min():.2f} - {df['points'].max():.2f}")
    
    # Overall correlation
    corr, p_value = stats.pearsonr(df['salary'], df['points'])
    print(f"Overall correlation: {corr:.4f} (p-value: {p_value:.4f})")
    
    print(f"\nBy Position:")
    for position in ['QB', 'RB', 'WR', 'TE', 'DEF']:
        pos_data = df[df['position'] == position]
        if len(pos_data) > 1:
            corr, p_value = stats.pearsonr(pos_data['salary'], pos_data['points'])
            print(f"{position:>3}: {corr:>7.4f} (p-value: {p_value:>7.4f}) - {len(pos_data):>3} players")
    
    # Value analysis
    df['value'] = df['points'] / df['salary']
    df['value'] = df['value'].replace([float('inf'), -float('inf')], 0)
    
    print(f"\nValue Analysis (Points per Dollar):")
    for position in ['QB', 'RB', 'WR', 'TE', 'DEF']:
        pos_data = df[df['position'] == position]
        if len(pos_data) > 0:
            avg_value = pos_data['value'].mean()
            max_value = pos_data['value'].max()
            print(f"{position:>3}: Avg {avg_value:>6.3f}, Max {max_value:>6.3f}")

if __name__ == "__main__":
    # Create the main salary vs points plots
    df = create_salary_vs_points_plots()
    
    if df is not None:
        # Create value analysis plot
        create_value_analysis_plot()
        
        # Print correlation summary
        print_correlation_summary()

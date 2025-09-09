#!/usr/bin/env python3
"""
Analyze the impact of removing players with 0 fantasy points
on value metrics and correlation analysis
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy import stats

def analyze_zero_points_impact(csv_file="data_csv/modeling_dataset_2025_week1.csv"):
    """
    Analyze the impact of removing players with 0 fantasy points
    """
    print("🔍 Analyzing impact of removing zero-point players")
    
    # Read the data
    df = pd.read_csv(csv_file)
    print(f"📊 Original dataset: {len(df)} players")
    print(f"📊 Players with 0 points: {len(df[df['points'] == 0])}")
    
    # Create filtered dataset (remove zero points)
    df_filtered = df[df['points'] > 0].copy()
    print(f"📊 Filtered dataset: {len(df_filtered)} players")
    
    # Calculate value metrics (points per dollar)
    df['value'] = df['points'] / df['salary']
    df['value'] = df['value'].replace([float('inf'), -float('inf')], 0)
    
    df_filtered['value'] = df_filtered['points'] / df_filtered['salary']
    df_filtered['value'] = df_filtered['value'].replace([float('inf'), -float('inf')], 0)
    
    # Calculate correlations
    original_corr, original_p = stats.pearsonr(df['salary'], df['points'])
    filtered_corr, filtered_p = stats.pearsonr(df_filtered['salary'], df_filtered['points'])
    
    print(f"\n📈 CORRELATION ANALYSIS:")
    print(f"Original dataset (salary vs points): {original_corr:.4f} (p={original_p:.4f})")
    print(f"Filtered dataset (salary vs points): {filtered_corr:.4f} (p={filtered_p:.4f})")
    print(f"Correlation change: {filtered_corr - original_corr:.4f}")
    
    # Value analysis
    print(f"\n💎 VALUE ANALYSIS:")
    print(f"Original dataset - Mean value: {df['value'].mean():.4f}")
    print(f"Filtered dataset - Mean value: {df_filtered['value'].mean():.4f}")
    print(f"Value change: {df_filtered['value'].mean() - df['value'].mean():.4f}")
    
    # Position-specific analysis
    positions = ['QB', 'RB', 'WR', 'TE', 'DEF']
    print(f"\n🎯 POSITION-SPECIFIC ANALYSIS:")
    
    for position in positions:
        pos_original = df[df['position'] == position]
        pos_filtered = df_filtered[df_filtered['position'] == position]
        
        if len(pos_original) > 0 and len(pos_filtered) > 0:
            orig_corr, orig_p = stats.pearsonr(pos_original['salary'], pos_original['points'])
            filt_corr, filt_p = stats.pearsonr(pos_filtered['salary'], pos_filtered['points'])
            
            print(f"{position}:")
            print(f"  Original: {len(pos_original)} players, correlation: {orig_corr:.4f}")
            print(f"  Filtered: {len(pos_filtered)} players, correlation: {filt_corr:.4f}")
            print(f"  Change: {filt_corr - orig_corr:.4f}")
    
    # Create comparison visualization
    create_comparison_plots(df, df_filtered, original_corr, filtered_corr)
    
    return df, df_filtered

def create_comparison_plots(df_original, df_filtered, orig_corr, filt_corr):
    """
    Create comparison plots showing the impact of filtering
    """
    print("\n📊 Creating comparison visualizations...")
    
    # Set up the plotting style
    plt.style.use('default')
    sns.set_palette("husl")
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('Impact of Removing Zero-Point Players on Fantasy Analysis', fontsize=16, fontweight='bold')
    
    positions = ['QB', 'RB', 'WR', 'TE', 'DEF']
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    
    # Plot each position - Original vs Filtered
    for i, position in enumerate(positions):
        row = i // 3
        col = i % 3
        ax = axes[row, col]
        
        # Original data
        pos_orig = df_original[df_original['position'] == position]
        pos_filt = df_filtered[df_filtered['position'] == position]
        
        if len(pos_orig) > 0:
            # Plot original data (including zeros)
            ax.scatter(pos_orig['salary'], pos_orig['points'], 
                      alpha=0.6, s=50, c=colors[i], label=f'All ({len(pos_orig)})', 
                      edgecolors='black', linewidth=0.5)
            
            # Plot filtered data (no zeros)
            if len(pos_filt) > 0:
                ax.scatter(pos_filt['salary'], pos_filt['points'], 
                          alpha=0.8, s=60, c=colors[i], marker='^', 
                          label=f'No Zeros ({len(pos_filt)})', 
                          edgecolors='red', linewidth=1)
            
            # Add trend lines
            if len(pos_orig) > 1:
                z_orig = np.polyfit(pos_orig['salary'], pos_orig['points'], 1)
                p_orig = np.poly1d(z_orig)
                ax.plot(pos_orig['salary'], p_orig(pos_orig['salary']), 
                       color='blue', linestyle='--', alpha=0.7, linewidth=2, label='Original trend')
            
            if len(pos_filt) > 1:
                z_filt = np.polyfit(pos_filt['salary'], pos_filt['points'], 1)
                p_filt = np.poly1d(z_filt)
                ax.plot(pos_filt['salary'], p_filt(pos_filt['salary']), 
                       color='red', linestyle='-', alpha=0.8, linewidth=2, label='Filtered trend')
            
            # Calculate correlations
            if len(pos_orig) > 1:
                corr_orig, p_orig = stats.pearsonr(pos_orig['salary'], pos_orig['points'])
            if len(pos_filt) > 1:
                corr_filt, p_filt = stats.pearsonr(pos_filt['salary'], pos_filt['points'])
            
            # Add correlation info
            ax.text(0.05, 0.95, f'Original: r={corr_orig:.3f}\nFiltered: r={corr_filt:.3f}', 
                   transform=ax.transAxes, fontsize=9, 
                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
            
            # Customize the plot
            ax.set_xlabel('Salary ($)', fontsize=10)
            ax.set_ylabel('Fantasy Points', fontsize=10)
            ax.set_title(f'{position}', fontsize=12, fontweight='bold')
            ax.grid(True, alpha=0.3)
            ax.legend(fontsize=8)
            
            # Set axis limits
            ax.set_xlim(9, 41)
            ax.set_ylim(-4, 40)
    
    # Remove the empty subplot
    axes[1, 2].remove()
    
    # Add overall comparison plot in the bottom right
    ax_overall = fig.add_subplot(2, 3, 6)
    
    # Overall scatter plot
    ax_overall.scatter(df_original['salary'], df_original['points'], 
                      alpha=0.4, s=40, c='lightblue', label=f'All Players ({len(df_original)})', 
                      edgecolors='black', linewidth=0.3)
    ax_overall.scatter(df_filtered['salary'], df_filtered['points'], 
                      alpha=0.7, s=50, c='red', marker='^', 
                      label=f'No Zeros ({len(df_filtered)})', 
                      edgecolors='black', linewidth=0.5)
    
    # Overall trend lines
    z_orig = np.polyfit(df_original['salary'], df_original['points'], 1)
    p_orig = np.poly1d(z_orig)
    ax_overall.plot(df_original['salary'], p_orig(df_original['salary']), 
                   color='blue', linestyle='--', alpha=0.7, linewidth=3, label='Original trend')
    
    z_filt = np.polyfit(df_filtered['salary'], df_filtered['points'], 1)
    p_filt = np.poly1d(z_filt)
    ax_overall.plot(df_filtered['salary'], p_filt(df_filtered['salary']), 
                   color='red', linestyle='-', alpha=0.8, linewidth=3, label='Filtered trend')
    
    # Overall correlation info
    ax_overall.text(0.05, 0.95, f'Original: r={orig_corr:.3f}\nFiltered: r={filt_corr:.3f}\nChange: {filt_corr-orig_corr:.3f}', 
                   transform=ax_overall.transAxes, fontsize=10, 
                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    ax_overall.set_xlabel('Salary ($)', fontsize=12)
    ax_overall.set_ylabel('Fantasy Points', fontsize=12)
    ax_overall.set_title('All Positions Combined', fontsize=14, fontweight='bold')
    ax_overall.legend(fontsize=10)
    ax_overall.grid(True, alpha=0.3)
    ax_overall.set_xlim(9, 41)
    ax_overall.set_ylim(-4, 40)
    
    plt.tight_layout()
    
    # Save the plot
    output_file = "plots_images/zero_points_impact_analysis.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ Comparison plot saved as: {output_file}")
    
    plt.show()
    
    # Create value analysis plot
    create_value_comparison_plot(df_original, df_filtered)

def create_value_comparison_plot(df_original, df_filtered):
    """
    Create value analysis comparison plot
    """
    print("💎 Creating value analysis comparison...")
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle('Value Analysis: Impact of Removing Zero-Point Players', fontsize=16, fontweight='bold')
    
    # Box plot comparison
    positions = ['QB', 'RB', 'WR', 'TE', 'DEF']
    
    # Original value data
    orig_value_data = [df_original[df_original['position'] == pos]['value'].values for pos in positions]
    filt_value_data = [df_filtered[df_filtered['position'] == pos]['value'].values for pos in positions]
    
    # Create box plots side by side
    x_pos = np.arange(len(positions))
    width = 0.35
    
    bp1 = ax1.boxplot(orig_value_data, positions=x_pos - width/2, widths=width, 
                     patch_artist=True, labels=positions)
    bp2 = ax1.boxplot(filt_value_data, positions=x_pos + width/2, widths=width, 
                     patch_artist=True, labels=positions)
    
    # Color the boxes
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    for patch in bp1['boxes']:
        patch.set_facecolor('lightblue')
        patch.set_alpha(0.7)
    for patch in bp2['boxes']:
        patch.set_facecolor('lightcoral')
        patch.set_alpha(0.7)
    
    ax1.set_ylabel('Points per Dollar', fontsize=12)
    ax1.set_title('Value Distribution by Position', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend([bp1["boxes"][0], bp2["boxes"][0]], ['All Players', 'No Zeros'], loc='upper right')
    
    # Scatter plot: Value vs Salary
    ax2.scatter(df_original['salary'], df_original['value'], 
               alpha=0.4, s=40, c='lightblue', label=f'All Players ({len(df_original)})', 
               edgecolors='black', linewidth=0.3)
    ax2.scatter(df_filtered['salary'], df_filtered['value'], 
               alpha=0.7, s=50, c='red', marker='^', 
               label=f'No Zeros ({len(df_filtered)})', 
               edgecolors='black', linewidth=0.5)
    
    ax2.set_xlabel('Salary ($)', fontsize=12)
    ax2.set_ylabel('Points per Dollar', fontsize=12)
    ax2.set_title('Value vs Salary', fontsize=14, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save the plot
    output_file = "plots_images/value_analysis_zero_points_impact.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ Value analysis plot saved as: {output_file}")
    
    plt.show()

if __name__ == "__main__":
    # Run the analysis
    df_orig, df_filt = analyze_zero_points_impact()
    
    print(f"\n📋 SUMMARY:")
    print(f"• Removed {len(df_orig) - len(df_filt)} players with 0 points")
    print(f"• Original correlation: {stats.pearsonr(df_orig['salary'], df_orig['points'])[0]:.4f}")
    print(f"• Filtered correlation: {stats.pearsonr(df_filt['salary'], df_filt['points'])[0]:.4f}")
    print(f"• Original mean value: {df_orig['value'].mean():.4f}")
    print(f"• Filtered mean value: {df_filt['value'].mean():.4f}")

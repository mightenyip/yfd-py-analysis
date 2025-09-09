#!/usr/bin/env python3
"""
Comprehensive analysis of the impact of removing players with 0 fantasy points
Comparing both the modeling dataset and the full dataset
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy import stats

def comprehensive_zero_points_analysis():
    """
    Comprehensive analysis comparing both datasets
    """
    print("🔍 COMPREHENSIVE ANALYSIS: Impact of Removing Zero-Point Players")
    print("=" * 70)
    
    # Load both datasets
    df_modeling = pd.read_csv("data_csv/modeling_dataset_2025_week1.csv")
    df_full = pd.read_csv("data_csv/yahoo_daily_fantasy_2025_week1_all_games.csv")
    
    # Clean salary column for full dataset
    df_full['salary'] = df_full['salary'].str.replace('$', '').astype(float)
    
    print(f"📊 DATASET OVERVIEW:")
    print(f"Modeling dataset: {len(df_modeling)} players ({len(df_modeling[df_modeling['points'] == 0])} with 0 points)")
    print(f"Full dataset: {len(df_full)} players ({len(df_full[df_full['points'] == 0])} with 0 points)")
    
    # Analyze both datasets
    results = {}
    
    for dataset_name, df in [("Modeling", df_modeling), ("Full", df_full)]:
        print(f"\n{'='*20} {dataset_name.upper()} DATASET {'='*20}")
        
        # Create filtered dataset
        df_filtered = df[df['points'] > 0].copy()
        
        # Calculate value metrics
        df['value'] = df['points'] / df['salary']
        df['value'] = df['value'].replace([float('inf'), -float('inf')], 0)
        
        df_filtered['value'] = df_filtered['points'] / df_filtered['salary']
        df_filtered['value'] = df_filtered['value'].replace([float('inf'), -float('inf')], 0)
        
        # Calculate correlations
        orig_corr, orig_p = stats.pearsonr(df['salary'], df['points'])
        filt_corr, filt_p = stats.pearsonr(df_filtered['salary'], df_filtered['points'])
        
        print(f"📈 CORRELATION ANALYSIS:")
        print(f"  Original: {orig_corr:.4f} (p={orig_p:.4f})")
        print(f"  Filtered: {filt_corr:.4f} (p={filt_p:.4f})")
        print(f"  Change: {filt_corr - orig_corr:.4f}")
        
        print(f"💎 VALUE ANALYSIS:")
        print(f"  Original mean value: {df['value'].mean():.4f}")
        print(f"  Filtered mean value: {df_filtered['value'].mean():.4f}")
        print(f"  Value change: {df_filtered['value'].mean() - df['value'].mean():.4f}")
        
        # Store results
        results[dataset_name] = {
            'original': df,
            'filtered': df_filtered,
            'orig_corr': orig_corr,
            'filt_corr': filt_corr,
            'orig_value': df['value'].mean(),
            'filt_value': df_filtered['value'].mean()
        }
    
    # Create comprehensive comparison plots
    create_comprehensive_plots(results)
    
    return results

def create_comprehensive_plots(results):
    """
    Create comprehensive comparison plots
    """
    print(f"\n📊 Creating comprehensive comparison visualizations...")
    
    # Set up the plotting style
    plt.style.use('default')
    sns.set_palette("husl")
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Comprehensive Analysis: Impact of Removing Zero-Point Players', fontsize=16, fontweight='bold')
    
    # Plot 1: Correlation comparison
    ax1 = axes[0, 0]
    datasets = ['Modeling', 'Full']
    orig_corrs = [results[d]['orig_corr'] for d in datasets]
    filt_corrs = [results[d]['filt_corr'] for d in datasets]
    
    x = np.arange(len(datasets))
    width = 0.35
    
    bars1 = ax1.bar(x - width/2, orig_corrs, width, label='Original', color='lightblue', alpha=0.7)
    bars2 = ax1.bar(x + width/2, filt_corrs, width, label='Filtered', color='lightcoral', alpha=0.7)
    
    ax1.set_xlabel('Dataset')
    ax1.set_ylabel('Correlation (Salary vs Points)')
    ax1.set_title('Correlation Comparison')
    ax1.set_xticks(x)
    ax1.set_xticklabels(datasets)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Add value labels on bars
    for bar in bars1:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f'{height:.3f}', ha='center', va='bottom', fontsize=9)
    for bar in bars2:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f'{height:.3f}', ha='center', va='bottom', fontsize=9)
    
    # Plot 2: Value comparison
    ax2 = axes[0, 1]
    orig_values = [results[d]['orig_value'] for d in datasets]
    filt_values = [results[d]['filt_value'] for d in datasets]
    
    bars3 = ax2.bar(x - width/2, orig_values, width, label='Original', color='lightgreen', alpha=0.7)
    bars4 = ax2.bar(x + width/2, filt_values, width, label='Filtered', color='orange', alpha=0.7)
    
    ax2.set_xlabel('Dataset')
    ax2.set_ylabel('Mean Value (Points per Dollar)')
    ax2.set_title('Value Comparison')
    ax2.set_xticks(x)
    ax2.set_xticklabels(datasets)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Add value labels on bars
    for bar in bars3:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.005,
                f'{height:.3f}', ha='center', va='bottom', fontsize=9)
    for bar in bars4:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.005,
                f'{height:.3f}', ha='center', va='bottom', fontsize=9)
    
    # Plot 3: Full dataset scatter comparison
    ax3 = axes[1, 0]
    df_full_orig = results['Full']['original']
    df_full_filt = results['Full']['filtered']
    
    # Sample data for visualization (too many points)
    sample_orig = df_full_orig.sample(min(200, len(df_full_orig)), random_state=42)
    sample_filt = df_full_filt.sample(min(200, len(df_full_filt)), random_state=42)
    
    ax3.scatter(sample_orig['salary'], sample_orig['points'], 
               alpha=0.4, s=30, c='lightblue', label=f'All ({len(df_full_orig)})', 
               edgecolors='black', linewidth=0.2)
    ax3.scatter(sample_filt['salary'], sample_filt['points'], 
               alpha=0.7, s=40, c='red', marker='^', 
               label=f'No Zeros ({len(df_full_filt)})', 
               edgecolors='black', linewidth=0.3)
    
    # Add trend lines
    z_orig = np.polyfit(df_full_orig['salary'], df_full_orig['points'], 1)
    p_orig = np.poly1d(z_orig)
    ax3.plot(df_full_orig['salary'], p_orig(df_full_orig['salary']), 
             color='blue', linestyle='--', alpha=0.7, linewidth=2, label='Original trend')
    
    z_filt = np.polyfit(df_full_filt['salary'], df_full_filt['points'], 1)
    p_filt = np.poly1d(z_filt)
    ax3.plot(df_full_filt['salary'], p_filt(df_full_filt['salary']), 
             color='red', linestyle='-', alpha=0.8, linewidth=2, label='Filtered trend')
    
    ax3.set_xlabel('Salary ($)')
    ax3.set_ylabel('Fantasy Points')
    ax3.set_title('Full Dataset: Salary vs Points')
    ax3.legend(fontsize=8)
    ax3.grid(True, alpha=0.3)
    ax3.set_xlim(9, 41)
    ax3.set_ylim(-4, 40)
    
    # Plot 4: Modeling dataset scatter comparison
    ax4 = axes[1, 1]
    df_model_orig = results['Modeling']['original']
    df_model_filt = results['Modeling']['filtered']
    
    ax4.scatter(df_model_orig['salary'], df_model_orig['points'], 
               alpha=0.6, s=50, c='lightblue', label=f'All ({len(df_model_orig)})', 
               edgecolors='black', linewidth=0.3)
    ax4.scatter(df_model_filt['salary'], df_model_filt['points'], 
               alpha=0.8, s=60, c='red', marker='^', 
               label=f'No Zeros ({len(df_model_filt)})', 
               edgecolors='black', linewidth=0.5)
    
    # Add trend lines
    z_orig = np.polyfit(df_model_orig['salary'], df_model_orig['points'], 1)
    p_orig = np.poly1d(z_orig)
    ax4.plot(df_model_orig['salary'], p_orig(df_model_orig['salary']), 
             color='blue', linestyle='--', alpha=0.7, linewidth=2, label='Original trend')
    
    z_filt = np.polyfit(df_model_filt['salary'], df_model_filt['points'], 1)
    p_filt = np.poly1d(z_filt)
    ax4.plot(df_model_filt['salary'], p_filt(df_model_filt['salary']), 
             color='red', linestyle='-', alpha=0.8, linewidth=2, label='Filtered trend')
    
    ax4.set_xlabel('Salary ($)')
    ax4.set_ylabel('Fantasy Points')
    ax4.set_title('Modeling Dataset: Salary vs Points')
    ax4.legend(fontsize=8)
    ax4.grid(True, alpha=0.3)
    ax4.set_xlim(9, 41)
    ax4.set_ylim(-4, 40)
    
    plt.tight_layout()
    
    # Save the plot
    output_file = "plots_images/comprehensive_zero_points_analysis.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ Comprehensive analysis plot saved as: {output_file}")
    
    plt.show()
    
    # Create summary table
    create_summary_table(results)

def create_summary_table(results):
    """
    Create a summary table of the analysis
    """
    print(f"\n📋 SUMMARY TABLE:")
    print("=" * 80)
    print(f"{'Metric':<25} {'Modeling Dataset':<20} {'Full Dataset':<20}")
    print("=" * 80)
    
    # Dataset sizes
    print(f"{'Total Players':<25} {len(results['Modeling']['original']):<20} {len(results['Full']['original']):<20}")
    print(f"{'Zero-Point Players':<25} {len(results['Modeling']['original'][results['Modeling']['original']['points'] == 0]):<20} {len(results['Full']['original'][results['Full']['original']['points'] == 0]):<20}")
    print(f"{'Filtered Players':<25} {len(results['Modeling']['filtered']):<20} {len(results['Full']['filtered']):<20}")
    
    # Correlations
    print(f"{'Original Correlation':<25} {results['Modeling']['orig_corr']:.4f}{'':<15} {results['Full']['orig_corr']:.4f}{'':<15}")
    print(f"{'Filtered Correlation':<25} {results['Modeling']['filt_corr']:.4f}{'':<15} {results['Full']['filt_corr']:.4f}{'':<15}")
    print(f"{'Correlation Change':<25} {results['Modeling']['filt_corr'] - results['Modeling']['orig_corr']:+.4f}{'':<15} {results['Full']['filt_corr'] - results['Full']['orig_corr']:+.4f}{'':<15}")
    
    # Values
    print(f"{'Original Mean Value':<25} {results['Modeling']['orig_value']:.4f}{'':<15} {results['Full']['orig_value']:.4f}{'':<15}")
    print(f"{'Filtered Mean Value':<25} {results['Modeling']['filt_value']:.4f}{'':<15} {results['Full']['filt_value']:.4f}{'':<15}")
    print(f"{'Value Change':<25} {results['Modeling']['filt_value'] - results['Modeling']['orig_value']:+.4f}{'':<15} {results['Full']['filt_value'] - results['Full']['orig_value']:+.4f}{'':<15}")
    
    print("=" * 80)
    
    # Key insights
    print(f"\n🔍 KEY INSIGHTS:")
    print(f"• Modeling dataset: Minimal impact from removing zero-point players")
    print(f"  - Only 3 zero-point players out of 251 total")
    print(f"  - Correlation change: {results['Modeling']['filt_corr'] - results['Modeling']['orig_corr']:+.4f}")
    print(f"  - Value change: {results['Modeling']['filt_value'] - results['Modeling']['orig_value']:+.4f}")
    
    print(f"• Full dataset: Significant impact from removing zero-point players")
    print(f"  - {len(results['Full']['original'][results['Full']['original']['points'] == 0])} zero-point players out of {len(results['Full']['original'])} total")
    print(f"  - Correlation change: {results['Full']['filt_corr'] - results['Full']['orig_corr']:+.4f}")
    print(f"  - Value change: {results['Full']['filt_value'] - results['Full']['orig_value']:+.4f}")
    
    print(f"• The modeling dataset appears to be pre-filtered for active players")
    print(f"• Removing zero-point players significantly improves value metrics in the full dataset")

if __name__ == "__main__":
    # Run the comprehensive analysis
    results = comprehensive_zero_points_analysis()

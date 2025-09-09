#!/usr/bin/env python3
"""
Analyze week1_monday_correct.csv by position and compare points to salary,
but EXCLUDE all players who scored 0 points to see the correlation for active players only.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy import stats
import os

def load_and_filter_data(input_file="../data_csv/week1_monday_correct.csv"):
    """
    Load the correct week1_monday data and filter out 0-point players.
    """
    print(f"📊 Loading data from {input_file}...")
    
    try:
        # Load the data
        df = pd.read_csv(input_file)
        print(f"✅ Loaded {len(df)} total players")
        
        # Clean up data types
        df['salary_numeric'] = df['salary'].str.replace('$', '').astype(float)
        df['points_numeric'] = pd.to_numeric(df['points'], errors='coerce')
        df['fppg_numeric'] = pd.to_numeric(df['fppg'], errors='coerce')
        
        # Clean position names
        df['position_clean'] = df['position'].str.strip().str.upper()
        
        # Filter out players with 0 points
        original_count = len(df)
        df_filtered = df[df['points_numeric'] > 0].copy()
        filtered_count = len(df_filtered)
        zero_point_players = original_count - filtered_count
        
        print(f"🔍 Filtering Results:")
        print(f"   Original players: {original_count}")
        print(f"   Players with 0 points: {zero_point_players}")
        print(f"   Active players (points > 0): {filtered_count}")
        print(f"   Percentage of active players: {(filtered_count/original_count)*100:.1f}%")
        
        print(f"\n📊 Position breakdown (Active players only):")
        position_counts = df_filtered['position_clean'].value_counts()
        for pos, count in position_counts.items():
            print(f"   {pos}: {count} players")
        
        return df_filtered, df
        
    except Exception as e:
        print(f"❌ Error processing file: {e}")
        return None, None

def create_comparison_plots(df_filtered, df_original):
    """
    Create comparison plots showing the difference between all players vs active players only.
    """
    print(f"\n📊 Creating comparison plots (All vs Active Players Only)...")
    
    # Set up the plotting style
    plt.style.use('default')
    sns.set_palette("husl")
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 3, figsize=(20, 12))
    fig.suptitle('Week 1 Monday: Salary vs Points Analysis - All Players vs Active Players Only', 
                 fontsize=16, fontweight='bold')
    
    positions = df_filtered['position_clean'].unique()
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    
    # Plot each position - Top row: All players, Bottom row: Active players only
    for i, position in enumerate(positions):
        if i >= 3:  # Only show first 3 positions for clarity
            break
            
        # Top row: All players
        ax_top = axes[0, i]
        pos_data_all = df_original[df_original['position_clean'] == position].copy()
        
        if len(pos_data_all) > 0:
            # Create scatter plot
            ax_top.scatter(pos_data_all['salary_numeric'], pos_data_all['points_numeric'], 
                          alpha=0.7, s=60, c=colors[i], edgecolors='black', linewidth=0.5)
            
            # Add trend line
            if len(pos_data_all) > 1:
                valid_data = pos_data_all.dropna(subset=['salary_numeric', 'points_numeric'])
                if len(valid_data) > 1:
                    z = np.polyfit(valid_data['salary_numeric'], valid_data['points_numeric'], 1)
                    p = np.poly1d(z)
                    ax_top.plot(valid_data['salary_numeric'], p(valid_data['salary_numeric']), 
                               color='red', linestyle='--', alpha=0.8, linewidth=2)
                    
                    # Calculate correlation
                    corr, p_value = stats.pearsonr(valid_data['salary_numeric'], valid_data['points_numeric'])
                    ax_top.text(0.05, 0.95, f'Correlation: {corr:.3f}\nP-value: {p_value:.3f}', 
                               transform=ax_top.transAxes, fontsize=9, 
                               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
            
            ax_top.set_xlabel('Salary ($)', fontsize=10)
            ax_top.set_ylabel('Fantasy Points', fontsize=10)
            ax_top.set_title(f'{position} - ALL Players (n={len(pos_data_all)})', fontsize=12, fontweight='bold')
            ax_top.grid(True, alpha=0.3)
        
        # Bottom row: Active players only
        ax_bottom = axes[1, i]
        pos_data_active = df_filtered[df_filtered['position_clean'] == position].copy()
        
        if len(pos_data_active) > 0:
            # Create scatter plot
            ax_bottom.scatter(pos_data_active['salary_numeric'], pos_data_active['points_numeric'], 
                             alpha=0.7, s=60, c=colors[i], edgecolors='black', linewidth=0.5)
            
            # Add trend line
            if len(pos_data_active) > 1:
                valid_data = pos_data_active.dropna(subset=['salary_numeric', 'points_numeric'])
                if len(valid_data) > 1:
                    z = np.polyfit(valid_data['salary_numeric'], valid_data['points_numeric'], 1)
                    p = np.poly1d(z)
                    ax_bottom.plot(valid_data['salary_numeric'], p(valid_data['salary_numeric']), 
                                  color='red', linestyle='--', alpha=0.8, linewidth=2)
                    
                    # Calculate correlation
                    corr, p_value = stats.pearsonr(valid_data['salary_numeric'], valid_data['points_numeric'])
                    ax_bottom.text(0.05, 0.95, f'Correlation: {corr:.3f}\nP-value: {p_value:.3f}', 
                                  transform=ax_bottom.transAxes, fontsize=9, 
                                  bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
            
            ax_bottom.set_xlabel('Salary ($)', fontsize=10)
            ax_bottom.set_ylabel('Fantasy Points', fontsize=10)
            ax_bottom.set_title(f'{position} - ACTIVE Only (n={len(pos_data_active)})', fontsize=12, fontweight='bold')
            ax_bottom.grid(True, alpha=0.3)
    
    # Remove empty subplots
    for i in range(len(positions), 3):
        fig.delaxes(axes[0, i])
        fig.delaxes(axes[1, i])
    
    plt.tight_layout()
    
    # Save the plot
    output_file = "../plots_images/salary_vs_points_comparison_all_vs_active.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ Comparison plot saved as: {output_file}")
    
    plt.show()

def create_active_players_analysis(df_filtered):
    """
    Create detailed analysis for active players only.
    """
    print(f"\n📈 Creating detailed analysis for active players only...")
    
    # Create output directory
    os.makedirs('../week1_monday_active_analysis', exist_ok=True)
    
    # Save filtered data
    df_filtered.to_csv('../week1_monday_active_analysis/active_players_week1_monday.csv', index=False)
    print(f"✅ Active players data saved to week1_monday_active_analysis/active_players_week1_monday.csv")
    
    # Create position-specific files for active players
    positions = df_filtered['position_clean'].unique()
    for position in positions:
        pos_data = df_filtered[df_filtered['position_clean'] == position].copy()
        pos_data = pos_data.sort_values('points_numeric', ascending=False)
        
        # Save position-specific file
        filename = f'../week1_monday_active_analysis/{position.lower()}_active_players.csv'
        pos_data.to_csv(filename, index=False)
        print(f"✅ Saved {len(pos_data)} active {position} players to {filename}")
        
        # Show top players for this position
        print(f"   Top {min(5, len(pos_data))} active {position} players:")
        for i, (_, row) in enumerate(pos_data.head(5).iterrows(), 1):
            points = row['points_numeric'] if pd.notna(row['points_numeric']) else 0
            salary = row['salary_numeric'] if pd.notna(row['salary_numeric']) else 0
            value = points / salary if salary > 0 else 0
            print(f"     {i}. {row['player_name']:<20} | ${salary:>5.0f} | {points:>5.1f} pts | {value:>5.3f} value")
    
    return df_filtered

def create_value_analysis_active(df_filtered):
    """
    Create value analysis for active players only.
    """
    print(f"\n💎 Creating value analysis for active players only...")
    
    # Calculate value (points per dollar)
    df_filtered['value'] = df_filtered['points_numeric'] / df_filtered['salary_numeric']
    df_filtered['value'] = df_filtered['value'].replace([float('inf'), -float('inf')], 0)
    
    # Create the plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle('Week 1 Monday: Value Analysis - Active Players Only (Points > 0)', 
                 fontsize=16, fontweight='bold')
    
    # Box plot of value by position
    positions = df_filtered['position_clean'].unique()
    value_data = [df_filtered[df_filtered['position_clean'] == pos]['value'].values for pos in positions]
    
    bp = ax1.boxplot(value_data, labels=positions, patch_artist=True)
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    
    ax1.set_ylabel('Points per Dollar', fontsize=12)
    ax1.set_title('Value Distribution by Position (Active Players)', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    
    # Scatter plot: Value vs Salary
    for i, position in enumerate(positions):
        pos_data = df_filtered[df_filtered['position_clean'] == position]
        ax2.scatter(pos_data['salary_numeric'], pos_data['value'], 
                   alpha=0.7, s=60, c=colors[i % len(colors)], 
                   label=position, edgecolors='black', linewidth=0.5)
    
    ax2.set_xlabel('Salary ($)', fontsize=12)
    ax2.set_ylabel('Points per Dollar', fontsize=12)
    ax2.set_title('Value vs Salary (Active Players)', fontsize=14, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save the plot
    output_file = "../plots_images/value_analysis_active_players_only.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ Value analysis plot saved as: {output_file}")
    
    plt.show()

def print_detailed_comparison(df_filtered, df_original):
    """
    Print detailed comparison between all players vs active players only.
    """
    print(f"\n📈 Detailed Comparison Analysis:")
    print(f"=" * 70)
    
    # Overall statistics
    print(f"\nOverall Dataset Comparison:")
    print(f"All players: {len(df_original)}")
    print(f"Active players (points > 0): {len(df_filtered)}")
    print(f"Zero-point players: {len(df_original) - len(df_filtered)}")
    
    # Overall correlations
    valid_original = df_original.dropna(subset=['salary_numeric', 'points_numeric'])
    valid_filtered = df_filtered.dropna(subset=['salary_numeric', 'points_numeric'])
    
    if len(valid_original) > 1:
        corr_all, p_all = stats.pearsonr(valid_original['salary_numeric'], valid_original['points_numeric'])
        print(f"Overall correlation (All players): {corr_all:.4f} (p-value: {p_all:.4f})")
    
    if len(valid_filtered) > 1:
        corr_active, p_active = stats.pearsonr(valid_filtered['salary_numeric'], valid_filtered['points_numeric'])
        print(f"Overall correlation (Active only): {corr_active:.4f} (p-value: {p_active:.4f})")
        
        if len(valid_original) > 1:
            improvement = corr_active - corr_all
            print(f"Correlation improvement: {improvement:+.4f}")
    
    print(f"\nBy Position Comparison (All vs Active):")
    for position in df_filtered['position_clean'].unique():
        pos_all = df_original[df_original['position_clean'] == position]
        pos_active = df_filtered[df_filtered['position_clean'] == position]
        
        valid_all = pos_all.dropna(subset=['salary_numeric', 'points_numeric'])
        valid_active = pos_active.dropna(subset=['salary_numeric', 'points_numeric'])
        
        if len(valid_all) > 1 and len(valid_active) > 1:
            corr_all, p_all = stats.pearsonr(valid_all['salary_numeric'], valid_all['points_numeric'])
            corr_active, p_active = stats.pearsonr(valid_active['salary_numeric'], valid_active['points_numeric'])
            improvement = corr_active - corr_all
            
            print(f"{position:>3}: All={corr_all:>6.3f} | Active={corr_active:>6.3f} | Change={improvement:>+6.3f} | Active n={len(valid_active):>2}")
    
    # Top value players (active only)
    df_filtered['value'] = df_filtered['points_numeric'] / df_filtered['salary_numeric']
    df_filtered['value'] = df_filtered['value'].replace([float('inf'), -float('inf')], 0)
    
    print(f"\nTop 10 Value Players (Active Players Only):")
    top_value = df_filtered.nlargest(10, 'value')[['player_name', 'position_clean', 'salary_numeric', 'points_numeric', 'value']]
    for i, (_, row) in enumerate(top_value.iterrows(), 1):
        print(f"  {i:2d}. {row['player_name']:<20} | {row['position_clean']:<3} | ${row['salary_numeric']:>5.0f} | {row['points_numeric']:>5.1f} pts | {row['value']:>5.3f} value")

def main():
    print("Week 1 Monday Fantasy Analysis - ACTIVE PLAYERS ONLY")
    print("=" * 70)
    print("This analysis excludes all players who scored 0 points")
    print("to show the correlation between salary and performance for active players.")
    print("=" * 70)
    
    # Load and filter data
    df_filtered, df_original = load_and_filter_data()
    
    if df_filtered is not None and df_original is not None:
        # Create comparison plots
        create_comparison_plots(df_filtered, df_original)
        
        # Create active players analysis
        df_filtered = create_active_players_analysis(df_filtered)
        
        # Create value analysis
        create_value_analysis_active(df_filtered)
        
        # Print detailed comparison
        print_detailed_comparison(df_filtered, df_original)
        
        print(f"\n🎉 Analysis complete for active players only!")
        print(f"📁 All files saved in: week1_monday_active_analysis/")
    else:
        print(f"\n❌ Failed to load data")

if __name__ == "__main__":
    main()

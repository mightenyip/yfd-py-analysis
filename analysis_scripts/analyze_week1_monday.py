#!/usr/bin/env python3
"""
Analyze week1_monday.csv by position and compare points to salary.
This script parses the raw selenium data and creates clean analysis.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import re
from scipy import stats
import os

def parse_raw_player_data(raw_data_str):
    """
    Parse the raw_data string to extract clean player information.
    """
    try:
        # Convert string representation of list back to actual list
        import ast
        raw_data = ast.literal_eval(raw_data_str)
        
        # Extract player name from the 3rd element (index 2)
        player_info = raw_data[2] if len(raw_data) > 2 else ""
        
        # Split by newlines to get player name and game info
        lines = player_info.split('\n')
        player_name = lines[0].strip() if lines else "Unknown"
        
        # Extract game info
        game_info = lines[1] if len(lines) > 1 else ""
        
        # Extract stats
        stats = lines[2] if len(lines) > 2 else ""
        
        # Find salary (look for $ pattern)
        salary = None
        for item in raw_data:
            if '$' in str(item) and str(item).replace('$', '').replace(',', '').isdigit():
                salary = str(item)
                break
        
        # Find points (look for decimal numbers)
        points = None
        for item in raw_data:
            if isinstance(item, str) and '.' in item:
                try:
                    float(item)
                    if len(item) <= 6:  # Reasonable points range
                        points = item
                        break
                except ValueError:
                    continue
        
        # Extract position from first element
        position = raw_data[0] if len(raw_data) > 0 else "Unknown"
        
        return {
            'player_name': player_name,
            'position': position,
            'game_info': game_info,
            'stats': stats,
            'salary': salary,
            'points': points
        }
        
    except Exception as e:
        print(f"Error parsing raw data: {e}")
        return None

def clean_and_parse_week1_data(input_file="week1_monday.csv"):
    """
    Clean and parse the week1_monday.csv file.
    """
    print(f"📊 Loading and parsing {input_file}...")
    
    try:
        # Load the raw data
        df = pd.read_csv(input_file)
        print(f"✅ Loaded {len(df)} raw records")
        
        # Parse each row
        parsed_data = []
        for idx, row in df.iterrows():
            parsed = parse_raw_player_data(row['raw_data'])
            if parsed:
                parsed_data.append(parsed)
        
        # Create clean DataFrame
        clean_df = pd.DataFrame(parsed_data)
        
        # Clean up data types
        clean_df['salary_numeric'] = clean_df['salary'].str.replace('$', '').astype(float)
        clean_df['points_numeric'] = pd.to_numeric(clean_df['points'], errors='coerce')
        
        # Clean position names
        clean_df['position_clean'] = clean_df['position'].str.strip().str.upper()
        
        print(f"✅ Successfully parsed {len(clean_df)} players")
        print(f"📊 Position breakdown:")
        position_counts = clean_df['position_clean'].value_counts()
        for pos, count in position_counts.items():
            print(f"   {pos}: {count} players")
        
        return clean_df
        
    except Exception as e:
        print(f"❌ Error processing file: {e}")
        return None

def create_position_analysis(clean_df):
    """
    Create detailed analysis by position.
    """
    print(f"\n📈 Creating position analysis...")
    
    # Create output directory
    os.makedirs('week1_monday_analysis', exist_ok=True)
    
    # Save clean data
    clean_df.to_csv('week1_monday_analysis/clean_week1_monday.csv', index=False)
    print(f"✅ Clean data saved to week1_monday_analysis/clean_week1_monday.csv")
    
    # Create position-specific files
    positions = clean_df['position_clean'].unique()
    for position in positions:
        pos_data = clean_df[clean_df['position_clean'] == position].copy()
        pos_data = pos_data.sort_values('points_numeric', ascending=False)
        
        # Save position-specific file
        filename = f'week1_monday_analysis/{position.lower()}_players_week1_monday.csv'
        pos_data.to_csv(filename, index=False)
        print(f"✅ Saved {len(pos_data)} {position} players to {filename}")
        
        # Show top players for this position
        print(f"   Top {min(5, len(pos_data))} {position} players:")
        for i, (_, row) in enumerate(pos_data.head(5).iterrows(), 1):
            points = row['points_numeric'] if pd.notna(row['points_numeric']) else 0
            salary = row['salary_numeric'] if pd.notna(row['salary_numeric']) else 0
            value = points / salary if salary > 0 else 0
            print(f"     {i}. {row['player_name']:<20} | ${salary:>5.0f} | {points:>5.1f} pts | {value:>5.3f} value")
    
    return clean_df

def create_salary_vs_points_plots(clean_df):
    """
    Create comprehensive salary vs points analysis plots.
    """
    print(f"\n📊 Creating salary vs points plots...")
    
    # Set up the plotting style
    plt.style.use('default')
    sns.set_palette("husl")
    
    # Create figure with subplots
    positions = clean_df['position_clean'].unique()
    n_positions = len(positions)
    
    if n_positions <= 3:
        fig, axes = plt.subplots(1, n_positions, figsize=(6*n_positions, 6))
        if n_positions == 1:
            axes = [axes]
    else:
        rows = (n_positions + 2) // 3
        fig, axes = plt.subplots(rows, 3, figsize=(18, 6*rows))
        axes = axes.flatten()
    
    fig.suptitle('Week 1 Monday: Fantasy Points vs Salary by Position', fontsize=16, fontweight='bold')
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2']
    
    # Plot each position
    for i, position in enumerate(positions):
        ax = axes[i]
        
        # Filter data for this position
        pos_data = clean_df[clean_df['position_clean'] == position].copy()
        
        if len(pos_data) > 0:
            # Create scatter plot
            scatter = ax.scatter(pos_data['salary_numeric'], pos_data['points_numeric'], 
                               alpha=0.7, s=80, c=colors[i % len(colors)], 
                               edgecolors='black', linewidth=0.5)
            
            # Add trend line
            if len(pos_data) > 1:
                valid_data = pos_data.dropna(subset=['salary_numeric', 'points_numeric'])
                if len(valid_data) > 1:
                    z = np.polyfit(valid_data['salary_numeric'], valid_data['points_numeric'], 1)
                    p = np.poly1d(z)
                    ax.plot(valid_data['salary_numeric'], p(valid_data['salary_numeric']), 
                           color='red', linestyle='--', alpha=0.8, linewidth=2)
                    
                    # Calculate correlation
                    corr, p_value = stats.pearsonr(valid_data['salary_numeric'], valid_data['points_numeric'])
                    ax.text(0.05, 0.95, f'Correlation: {corr:.3f}\nP-value: {p_value:.3f}', 
                           transform=ax.transAxes, fontsize=10, 
                           bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
            
            # Customize the plot
            ax.set_xlabel('Salary ($)', fontsize=12)
            ax.set_ylabel('Fantasy Points', fontsize=12)
            ax.set_title(f'{position} (n={len(pos_data)})', fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3)
            
            # Add some statistics
            avg_salary = pos_data['salary_numeric'].mean()
            avg_points = pos_data['points_numeric'].mean()
            ax.axhline(y=avg_points, color='gray', linestyle=':', alpha=0.5, label=f'Avg Points: {avg_points:.1f}')
            ax.axvline(x=avg_salary, color='gray', linestyle=':', alpha=0.5, label=f'Avg Salary: ${avg_salary:.0f}')
            ax.legend(fontsize=8)
    
    # Remove empty subplots
    for i in range(len(positions), len(axes)):
        fig.delaxes(axes[i])
    
    plt.tight_layout()
    
    # Save the plot
    output_file = "week1_monday_analysis/salary_vs_points_week1_monday.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ Plot saved as: {output_file}")
    
    plt.show()
    
    return clean_df

def create_value_analysis(clean_df):
    """
    Create value analysis (points per dollar) plots.
    """
    print(f"\n💎 Creating value analysis...")
    
    # Calculate value (points per dollar)
    clean_df['value'] = clean_df['points_numeric'] / clean_df['salary_numeric']
    clean_df['value'] = clean_df['value'].replace([float('inf'), -float('inf')], 0)
    
    # Create the plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle('Week 1 Monday: Value Analysis (Points per Dollar)', fontsize=16, fontweight='bold')
    
    # Box plot of value by position
    positions = clean_df['position_clean'].unique()
    value_data = [clean_df[clean_df['position_clean'] == pos]['value'].values for pos in positions]
    
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
        pos_data = clean_df[clean_df['position_clean'] == position]
        ax2.scatter(pos_data['salary_numeric'], pos_data['value'], 
                   alpha=0.7, s=60, c=colors[i % len(colors)], 
                   label=position, edgecolors='black', linewidth=0.5)
    
    ax2.set_xlabel('Salary ($)', fontsize=12)
    ax2.set_ylabel('Points per Dollar', fontsize=12)
    ax2.set_title('Value vs Salary', fontsize=14, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save the plot
    output_file = "week1_monday_analysis/value_analysis_week1_monday.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ Value analysis plot saved as: {output_file}")
    
    plt.show()

def print_detailed_analysis(clean_df):
    """
    Print detailed correlation and value analysis.
    """
    print(f"\n📈 Detailed Analysis Summary:")
    print(f"=" * 50)
    
    print(f"\nOverall Dataset:")
    print(f"Total players: {len(clean_df)}")
    print(f"Salary range: ${clean_df['salary_numeric'].min():.0f} - ${clean_df['salary_numeric'].max():.0f}")
    print(f"Points range: {clean_df['points_numeric'].min():.2f} - {clean_df['points_numeric'].max():.2f}")
    
    # Overall correlation
    valid_data = clean_df.dropna(subset=['salary_numeric', 'points_numeric'])
    if len(valid_data) > 1:
        corr, p_value = stats.pearsonr(valid_data['salary_numeric'], valid_data['points_numeric'])
        print(f"Overall correlation: {corr:.4f} (p-value: {p_value:.4f})")
    
    print(f"\nBy Position:")
    for position in clean_df['position_clean'].unique():
        pos_data = clean_df[clean_df['position_clean'] == position]
        valid_pos_data = pos_data.dropna(subset=['salary_numeric', 'points_numeric'])
        
        if len(valid_pos_data) > 1:
            corr, p_value = stats.pearsonr(valid_pos_data['salary_numeric'], valid_pos_data['points_numeric'])
            avg_salary = valid_pos_data['salary_numeric'].mean()
            avg_points = valid_pos_data['points_numeric'].mean()
            avg_value = (valid_pos_data['points_numeric'] / valid_pos_data['salary_numeric']).mean()
            
            print(f"{position:>3}: {corr:>7.4f} (p-value: {p_value:>7.4f}) - {len(valid_pos_data):>3} players")
            print(f"     Avg Salary: ${avg_salary:>5.0f}, Avg Points: {avg_points:>5.1f}, Avg Value: {avg_value:>5.3f}")
    
    # Top value players
    clean_df['value'] = clean_df['points_numeric'] / clean_df['salary_numeric']
    clean_df['value'] = clean_df['value'].replace([float('inf'), -float('inf')], 0)
    
    print(f"\nTop 10 Value Players (Points per Dollar):")
    top_value = clean_df.nlargest(10, 'value')[['player_name', 'position_clean', 'salary_numeric', 'points_numeric', 'value']]
    for i, (_, row) in enumerate(top_value.iterrows(), 1):
        print(f"  {i:2d}. {row['player_name']:<20} | {row['position_clean']:<3} | ${row['salary_numeric']:>5.0f} | {row['points_numeric']:>5.1f} pts | {row['value']:>5.3f} value")

def main():
    print("Week 1 Monday Fantasy Analysis")
    print("=" * 50)
    
    # Parse the raw data
    clean_df = clean_and_parse_week1_data()
    
    if clean_df is not None:
        # Create position analysis
        clean_df = create_position_analysis(clean_df)
        
        # Create plots
        create_salary_vs_points_plots(clean_df)
        create_value_analysis(clean_df)
        
        # Print detailed analysis
        print_detailed_analysis(clean_df)
        
        print(f"\n🎉 Analysis complete!")
        print(f"📁 All files saved in: week1_monday_analysis/")
    else:
        print(f"\n❌ Failed to parse data")

if __name__ == "__main__":
    main()

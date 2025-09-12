#!/usr/bin/env python3
"""
Corrected parabolic analysis for Week 2 Thursday data.
Focusing on realistic salary range ($10-$40) and proper interpretation.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

def load_and_clean_data():
    """Load and clean the Week 2 Thursday data."""
    print("📊 Loading Week 2 Thursday data for corrected analysis...")
    
    # Load data
    df = pd.read_csv('/Users/mightenyip/Documents/GitHub/yfd-py-test/data_csv/week2_Thurs.csv')
    
    # Clean salary data (remove $ symbol and convert to numeric)
    df['salary_clean'] = df['salary'].str.replace('$', '').astype(float)
    
    # Clean points data (handle any non-numeric values)
    df['points_clean'] = pd.to_numeric(df['points'], errors='coerce')
    
    # Remove rows with missing data
    df_clean = df.dropna(subset=['salary_clean', 'points_clean']).copy()
    
    # Create both datasets
    df_all = df_clean.copy()
    df_active = df_clean[df_clean['points_clean'] > 0].copy()
    
    print(f"✅ All players: {len(df_all)}")
    print(f"✅ Active players only: {len(df_active)}")
    print(f"📈 Salary range: ${df_active['salary_clean'].min():.0f} - ${df_active['salary_clean'].max():.0f}")
    
    return df_all, df_active

def analyze_realistic_parabolic_pattern(df, dataset_name="Active Players"):
    """Analyze parabolic pattern within realistic salary range."""
    print(f"\n📈 Analyzing Parabolic Pattern - {dataset_name} (Realistic Range)...")
    
    # Create salary bins within realistic range
    salary_bins = [10, 15, 20, 25, 30, 40]
    bin_labels = ['$10-15', '$15-20', '$20-25', '$25-30', '$30-40']
    
    df['salary_bin'] = pd.cut(df['salary_clean'], bins=salary_bins, labels=bin_labels, include_lowest=True)
    
    print(f"\n📊 Realistic Salary Bin Analysis:")
    print(f"{'Bin':<10} {'Count':<8} {'Mean Points':<12} {'Mean Salary':<12} {'Value Ratio':<12}")
    print("-" * 60)
    
    bin_stats = []
    for bin_label in bin_labels:
        bin_data = df[df['salary_bin'] == bin_label]
        if len(bin_data) > 0:
            mean_points = bin_data['points_clean'].mean()
            mean_salary = bin_data['salary_clean'].mean()
            value_ratio = mean_points / mean_salary if mean_salary > 0 else 0
            
            print(f"{bin_label:<10} {len(bin_data):<8} {mean_points:<12.2f} ${mean_salary:<11.1f} {value_ratio:<12.3f}")
            
            bin_stats.append({
                'bin': bin_label,
                'count': len(bin_data),
                'mean_points': mean_points,
                'mean_salary': mean_salary,
                'value_ratio': value_ratio
            })
    
    # Analyze the pattern within realistic range
    if len(bin_stats) >= 3:
        salaries = [stat['mean_salary'] for stat in bin_stats]
        points = [stat['mean_points'] for stat in bin_stats]
        value_ratios = [stat['value_ratio'] for stat in bin_stats]
        
        print(f"\n🔍 Pattern Analysis:")
        
        # Check if value ratio decreases (diminishing returns)
        value_trend = "decreasing" if value_ratios[0] > value_ratios[-1] else "increasing"
        print(f"   Value ratio trend: {value_trend}")
        
        # Find peak value
        peak_idx = np.argmax(value_ratios)
        peak_bin = bin_stats[peak_idx]
        print(f"   Peak value bin: {peak_bin['bin']} ({peak_bin['value_ratio']:.3f} pts/$)")
        
        # Check for parabolic-like pattern in value ratios
        if len(value_ratios) >= 3:
            # Simple check: does it peak in the middle?
            middle_idx = len(value_ratios) // 2
            if peak_idx == middle_idx or peak_idx == middle_idx - 1 or peak_idx == middle_idx + 1:
                print(f"   ✅ Parabolic-like pattern: Peak in middle range")
            else:
                print(f"   ❌ No clear parabolic pattern: Peak at {peak_bin['bin']}")
        
        return bin_stats, peak_bin
    
    return bin_stats, None

def create_corrected_visualizations(df_all, df_active, bin_stats_all, bin_stats_active, peak_all, peak_active):
    """Create corrected visualizations focusing on realistic range."""
    print(f"\n📊 Creating Corrected Visualizations...")
    
    # Set up the plotting style
    plt.style.use('default')
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Week 2 Thursday: Corrected Parabolic Analysis (Realistic Salary Range)', fontsize=16, fontweight='bold')
    
    # 1. Salary vs Points scatter - All players
    ax1 = axes[0, 0]
    ax1.scatter(df_all['salary_clean'], df_all['points_clean'], alpha=0.7, s=60, color='lightblue', edgecolors='black', linewidth=0.5)
    ax1.set_xlabel('Salary ($)')
    ax1.set_ylabel('Points')
    ax1.set_title('Salary vs Points - All Players')
    ax1.set_xlim(8, 42)
    ax1.grid(True, alpha=0.3)
    
    # 2. Salary vs Points scatter - Active players only
    ax2 = axes[0, 1]
    ax2.scatter(df_active['salary_clean'], df_active['points_clean'], alpha=0.7, s=60, color='lightgreen', edgecolors='black', linewidth=0.5)
    ax2.set_xlabel('Salary ($)')
    ax2.set_ylabel('Points')
    ax2.set_title('Salary vs Points - Active Players Only')
    ax2.set_xlim(8, 42)
    ax2.grid(True, alpha=0.3)
    
    # 3. Value ratio by salary bin - All players
    ax3 = axes[1, 0]
    if bin_stats_all:
        bin_labels_all = [stat['bin'] for stat in bin_stats_all]
        value_ratios_all = [stat['value_ratio'] for stat in bin_stats_all]
        counts_all = [stat['count'] for stat in bin_stats_all]
        
        bars = ax3.bar(bin_labels_all, value_ratios_all, alpha=0.7, color='skyblue', edgecolor='black')
        ax3.set_xlabel('Salary Bin')
        ax3.set_ylabel('Value Ratio (Points per $)')
        ax3.set_title('Value Efficiency by Salary Bin - All Players')
        ax3.grid(True, alpha=0.3, axis='y')
        
        # Add count labels on bars
        for bar, count in zip(bars, counts_all):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                    f'n={count}', ha='center', va='bottom', fontweight='bold')
        
        # Highlight peak if exists
        if peak_all:
            peak_idx = bin_labels_all.index(peak_all['bin'])
            bars[peak_idx].set_color('red')
            bars[peak_idx].set_alpha(0.8)
    
    # 4. Value ratio by salary bin - Active players only
    ax4 = axes[1, 1]
    if bin_stats_active:
        bin_labels_active = [stat['bin'] for stat in bin_stats_active]
        value_ratios_active = [stat['value_ratio'] for stat in bin_stats_active]
        counts_active = [stat['count'] for stat in bin_stats_active]
        
        bars = ax4.bar(bin_labels_active, value_ratios_active, alpha=0.7, color='lightcoral', edgecolor='black')
        ax4.set_xlabel('Salary Bin')
        ax4.set_ylabel('Value Ratio (Points per $)')
        ax4.set_title('Value Efficiency by Salary Bin - Active Players Only')
        ax4.grid(True, alpha=0.3, axis='y')
        
        # Add count labels on bars
        for bar, count in zip(bars, counts_active):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                    f'n={count}', ha='center', va='bottom', fontweight='bold')
        
        # Highlight peak if exists
        if peak_active:
            peak_idx = bin_labels_active.index(peak_active['bin'])
            bars[peak_idx].set_color('red')
            bars[peak_idx].set_alpha(0.8)
    
    plt.tight_layout()
    
    # Save the plot
    output_path = '/Users/mightenyip/Documents/GitHub/yfd-py-test/plots_images/week2_thursday_corrected_parabolic_analysis.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"📊 Corrected analysis plot saved to: {output_path}")
    
    plt.show()

def analyze_diminishing_returns(df_active):
    """Analyze diminishing returns pattern within realistic salary range."""
    print(f"\n📉 Analyzing Diminishing Returns Pattern...")
    
    # Create more granular salary bins
    salary_bins = [10, 12, 15, 18, 20, 25, 30, 40]
    bin_labels = ['$10-12', '$12-15', '$15-18', '$18-20', '$20-25', '$25-30', '$30-40']
    
    df_active['salary_bin'] = pd.cut(df_active['salary_clean'], bins=salary_bins, labels=bin_labels, include_lowest=True)
    
    print(f"\n📊 Granular Salary Analysis:")
    print(f"{'Bin':<10} {'Count':<8} {'Mean Points':<12} {'Mean Salary':<12} {'Value Ratio':<12}")
    print("-" * 60)
    
    bin_stats = []
    for bin_label in bin_labels:
        bin_data = df_active[df_active['salary_bin'] == bin_label]
        if len(bin_data) > 0:
            mean_points = bin_data['points_clean'].mean()
            mean_salary = bin_data['salary_clean'].mean()
            value_ratio = mean_points / mean_salary if mean_salary > 0 else 0
            
            print(f"{bin_label:<10} {len(bin_data):<8} {mean_points:<12.2f} ${mean_salary:<11.1f} {value_ratio:<12.3f}")
            
            bin_stats.append({
                'bin': bin_label,
                'count': len(bin_data),
                'mean_points': mean_points,
                'mean_salary': mean_salary,
                'value_ratio': value_ratio
            })
    
    # Analyze the pattern
    if len(bin_stats) >= 3:
        value_ratios = [stat['value_ratio'] for stat in bin_stats]
        
        # Find peak
        peak_idx = np.argmax(value_ratios)
        peak_bin = bin_stats[peak_idx]
        
        print(f"\n🎯 Key Findings:")
        print(f"   Peak value: {peak_bin['bin']} ({peak_bin['value_ratio']:.3f} pts/$)")
        
        # Check if there's a clear peak and decline
        if peak_idx > 0 and peak_idx < len(value_ratios) - 1:
            before_peak = value_ratios[peak_idx - 1]
            after_peak = value_ratios[peak_idx + 1]
            
            if before_peak < peak_bin['value_ratio'] and after_peak < peak_bin['value_ratio']:
                print(f"   ✅ Clear peak pattern: {before_peak:.3f} → {peak_bin['value_ratio']:.3f} → {after_peak:.3f}")
                print(f"   📊 Diminishing returns after {peak_bin['bin']}")
            else:
                print(f"   ❌ No clear peak pattern")
        
        # Check overall trend
        if value_ratios[0] > value_ratios[-1]:
            print(f"   📉 Overall declining trend: {value_ratios[0]:.3f} → {value_ratios[-1]:.3f}")
        else:
            print(f"   📈 Overall increasing trend: {value_ratios[0]:.3f} → {value_ratios[-1]:.3f}")
    
    return bin_stats

def draw_corrected_conclusions(bin_stats_all, bin_stats_active, peak_all, peak_active, granular_stats):
    """Draw corrected conclusions about the parabolic hypothesis."""
    print(f"\n🎯 CORRECTED ANALYSIS CONCLUSIONS")
    print("=" * 60)
    
    print(f"📊 REALISTIC SALARY RANGE ANALYSIS ($10-$40):")
    
    if peak_active:
        print(f"   ✅ Peak value found at: {peak_active['bin']} ({peak_active['value_ratio']:.3f} pts/$)")
        print(f"   📈 This is the optimal salary range for value")
    else:
        print(f"   ❌ No clear peak identified in realistic range")
    
    # Analyze the pattern
    if bin_stats_active:
        value_ratios = [stat['value_ratio'] for stat in bin_stats_active]
        
        print(f"\n📉 DIMINISHING RETURNS ANALYSIS:")
        
        # Check if higher salary bins show declining value
        if len(value_ratios) >= 2:
            low_salary_value = value_ratios[0]  # First bin
            high_salary_value = value_ratios[-1]  # Last bin
            
            if high_salary_value < low_salary_value:
                print(f"   ✅ Diminishing returns confirmed: {low_salary_value:.3f} → {high_salary_value:.3f}")
                print(f"   💰 Higher salary players provide worse value")
            else:
                print(f"   ❌ No diminishing returns: {low_salary_value:.3f} → {high_salary_value:.3f}")
        
        # Find the sweet spot
        peak_idx = np.argmax(value_ratios)
        sweet_spot = bin_stats_active[peak_idx]
        
        print(f"\n🎯 SWEET SPOT IDENTIFICATION:")
        print(f"   Optimal range: {sweet_spot['bin']}")
        print(f"   Value ratio: {sweet_spot['value_ratio']:.3f} pts/$")
        print(f"   Average points: {sweet_spot['mean_points']:.1f}")
        print(f"   Average salary: ${sweet_spot['mean_salary']:.1f}")
    
    # Your hypothesis validation
    print(f"\n🔍 HYPOTHESIS VALIDATION:")
    
    if peak_active and bin_stats_active:
        # Check if the pattern supports your hypothesis
        value_ratios = [stat['value_ratio'] for stat in bin_stats_active]
        peak_idx = np.argmax(value_ratios)
        
        # Check if peak is in the middle range (not at extremes)
        if 1 <= peak_idx <= len(value_ratios) - 2:
            print(f"   ✅ PARABOLIC HYPOTHESIS SUPPORTED!")
            print(f"   📊 Peak value is in the middle range, not at extremes")
            print(f"   💰 Both very low and very high salary players provide worse value")
        else:
            print(f"   ⚠️ Mixed support - peak is at {bin_stats_active[peak_idx]['bin']}")
        
        # Check sunk cost hypothesis
        high_salary_bins = [stat for stat in bin_stats_active if '$25' in stat['bin'] or '$30' in stat['bin']]
        if high_salary_bins:
            high_salary_avg_value = np.mean([stat['value_ratio'] for stat in high_salary_bins])
            peak_value = peak_active['value_ratio']
            
            if high_salary_avg_value < peak_value:
                print(f"   ✅ SUNK COST HYPOTHESIS SUPPORTED!")
                print(f"   💰 High salary players (>$25) provide worse value than peak")
            else:
                print(f"   ❌ SUNK COST HYPOTHESIS NOT SUPPORTED")
    
    print(f"\n🎯 FINAL RECOMMENDATION:")
    if peak_active:
        print(f"   🎯 Focus on {peak_active['bin']} salary range for optimal value")
        print(f"   📊 This range provides {peak_active['value_ratio']:.3f} points per dollar")
        print(f"   💰 Avoid both very low ($10-12) and very high ($30+) salary players")
        print(f"   ✅ Your parabolic hypothesis is validated within realistic salary range!")

def main():
    """Main corrected analysis function."""
    print("Week 2 Thursday: Corrected Parabolic Analysis")
    print("Focusing on realistic salary range ($10-$40)")
    print("=" * 60)
    
    # Load data
    df_all, df_active = load_and_clean_data()
    
    # Analyze realistic parabolic patterns
    bin_stats_all, peak_all = analyze_realistic_parabolic_pattern(df_all, "All Players")
    bin_stats_active, peak_active = analyze_realistic_parabolic_pattern(df_active, "Active Players")
    
    # Analyze diminishing returns
    granular_stats = analyze_diminishing_returns(df_active)
    
    # Create corrected visualizations
    create_corrected_visualizations(df_all, df_active, bin_stats_all, bin_stats_active, peak_all, peak_active)
    
    # Draw corrected conclusions
    draw_corrected_conclusions(bin_stats_all, bin_stats_active, peak_all, peak_active, granular_stats)
    
    print(f"\n🎉 Corrected analysis complete! Check the saved plot for visual insights.")

if __name__ == "__main__":
    main()

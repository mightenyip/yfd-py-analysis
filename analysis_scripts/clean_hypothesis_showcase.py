#!/usr/bin/env python3
"""
Clean hypothesis showcase - no text boxes, streamlined plots.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import r2_score
import warnings
warnings.filterwarnings('ignore')

def load_and_clean_data():
    """Load and clean the Week 2 Thursday data."""
    print("📊 Loading Week 2 Thursday data...")
    
    # Load data
    df = pd.read_csv('/Users/mightenyip/Documents/GitHub/yfd-py-test/data_csv/week2_Thurs.csv')
    
    # Clean salary data (remove $ symbol and convert to numeric)
    df['salary_clean'] = df['salary'].str.replace('$', '').astype(float)
    
    # Clean points data (handle any non-numeric values)
    df['points_clean'] = pd.to_numeric(df['points'], errors='coerce')
    
    # Remove rows with missing data
    df_clean = df.dropna(subset=['salary_clean', 'points_clean']).copy()
    
    # Create active players dataset
    df_active = df_clean[df_clean['points_clean'] > 0].copy()
    
    print(f"✅ Active players: {len(df_active)}")
    print(f"📈 Salary range: ${df_active['salary_clean'].min():.0f} - ${df_active['salary_clean'].max():.0f}")
    
    return df_active

def create_salary_bins_and_fit_models(df):
    """Create salary bins and fit models to both raw and binned data."""
    print(f"\n📊 Creating Salary Bins and Fitting Models...")
    
    # Create salary bins
    salary_bins = [10, 15, 20, 25, 30, 40]
    bin_labels = ['$10-15', '$15-20', '$20-25', '$25-30', '$30-40']
    
    df['salary_bin'] = pd.cut(df['salary_clean'], bins=salary_bins, labels=bin_labels, include_lowest=True)
    
    # Calculate bin statistics
    bin_stats = []
    for bin_label in bin_labels:
        bin_data = df[df['salary_bin'] == bin_label]
        if len(bin_data) > 0:
            mean_points = bin_data['points_clean'].mean()
            mean_salary = bin_data['salary_clean'].mean()
            value_ratio = mean_points / mean_salary if mean_salary > 0 else 0
            
            bin_stats.append({
                'bin': bin_label,
                'count': len(bin_data),
                'mean_points': mean_points,
                'mean_salary': mean_salary,
                'value_ratio': value_ratio,
                'data': bin_data
            })
    
    # Fit models to RAW data
    X_raw = df['salary_clean'].values.reshape(-1, 1)
    y_raw = df['points_clean'].values
    
    # Quadratic model (raw)
    poly_features_quad_raw = PolynomialFeatures(degree=2)
    X_poly_quad_raw = poly_features_quad_raw.fit_transform(X_raw)
    quad_raw = LinearRegression()
    quad_raw.fit(X_poly_quad_raw, y_raw)
    y_pred_quad_raw = quad_raw.predict(X_poly_quad_raw)
    r2_quad_raw = r2_score(y_raw, y_pred_quad_raw)
    
    # Cubic model (raw)
    poly_features_cubic_raw = PolynomialFeatures(degree=3)
    X_poly_cubic_raw = poly_features_cubic_raw.fit_transform(X_raw)
    cubic_raw = LinearRegression()
    cubic_raw.fit(X_poly_cubic_raw, y_raw)
    y_pred_cubic_raw = cubic_raw.predict(X_poly_cubic_raw)
    r2_cubic_raw = r2_score(y_raw, y_pred_cubic_raw)
    
    # Fit models to BINNED data
    salaries_binned = [stat['mean_salary'] for stat in bin_stats]
    points_binned = [stat['mean_points'] for stat in bin_stats]
    
    X_binned = np.array(salaries_binned).reshape(-1, 1)
    y_binned = np.array(points_binned)
    
    # Cubic model (binned)
    poly_features_cubic_binned = PolynomialFeatures(degree=3)
    X_poly_cubic_binned = poly_features_cubic_binned.fit_transform(X_binned)
    cubic_binned = LinearRegression()
    cubic_binned.fit(X_poly_cubic_binned, y_binned)
    y_pred_cubic_binned = cubic_binned.predict(X_poly_cubic_binned)
    r2_cubic_binned = r2_score(y_binned, y_pred_cubic_binned)
    
    print(f"📊 Model Results:")
    print(f"   RAW DATA:")
    print(f"     Quadratic: R² = {r2_quad_raw:.4f}")
    print(f"     Cubic: R² = {r2_cubic_raw:.4f}")
    print(f"   BINNED DATA:")
    print(f"     Cubic: R² = {r2_cubic_binned:.4f}")
    
    return (bin_stats, 
            quad_raw, cubic_raw, poly_features_quad_raw, poly_features_cubic_raw,
            r2_quad_raw, r2_cubic_raw,
            cubic_binned, poly_features_cubic_binned, r2_cubic_binned,
            salaries_binned, points_binned)

def create_clean_hypothesis_showcase(df, bin_stats, cubic_binned, poly_features_cubic_binned, r2_cubic_binned):
    """Create clean hypothesis showcase - no text boxes."""
    print(f"\n📊 Creating Clean Hypothesis Showcase...")
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    fig.suptitle('Week 2 Thursday: Parabolic Hypothesis Validation', 
                 fontsize=18, fontweight='bold')
    
    # Extract data for plotting
    bin_labels = [stat['bin'] for stat in bin_stats]
    bin_counts = [stat['count'] for stat in bin_stats]
    bin_means = [stat['mean_points'] for stat in bin_stats]
    bin_salaries = [stat['mean_salary'] for stat in bin_stats]
    value_ratios = [stat['value_ratio'] for stat in bin_stats]
    
    # 1. Main plot: Salary vs Points with cubic fit and histogram bins
    ax1.scatter(bin_salaries, bin_means, s=[count*80 for count in bin_counts], 
               alpha=0.8, color='steelblue', edgecolors='black', linewidth=2, 
               label='Salary Bins (size = sample count)', zorder=5)
    
    # Add count labels on each point
    for i, (salary, points, count) in enumerate(zip(bin_salaries, bin_means, bin_counts)):
        ax1.annotate(f'n={count}', (salary, points), xytext=(8, 8), textcoords='offset points', 
                    fontweight='bold', fontsize=12, color='darkblue',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8, edgecolor='darkblue'))
    
    # Plot cubic curve
    X_smooth = np.linspace(min(bin_salaries), max(bin_salaries), 100)
    X_smooth_poly = poly_features_cubic_binned.transform(X_smooth.reshape(-1, 1))
    y_smooth = cubic_binned.predict(X_smooth_poly)
    
    ax1.plot(X_smooth, y_smooth, 'r-', linewidth=4, alpha=0.9, 
            label=f'Cubic Fit (R² = {r2_cubic_binned:.3f})', zorder=4)
    
    # Highlight the sweet spot ($15-20)
    sweet_spot_idx = 1  # $15-20 bin
    sweet_spot_salary = bin_salaries[sweet_spot_idx]
    sweet_spot_points = bin_means[sweet_spot_idx]
    sweet_spot_value = value_ratios[sweet_spot_idx]
    
    ax1.scatter(sweet_spot_salary, sweet_spot_points, s=300, color='gold', 
               edgecolors='darkorange', linewidth=3, label=f'Optimal Range: {bin_labels[sweet_spot_idx]}', zorder=6)
    
    # Add Jayden Daniels highlight
    jayden_salary = 39
    jayden_points = 19.7
    ax1.scatter(jayden_salary, jayden_points, s=200, color='red', 
               edgecolors='darkred', linewidth=2, marker='*', 
               label='Jayden Daniels ($39, 19.7 pts)', zorder=6)
    
    ax1.set_xlabel('Mean Salary ($)', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Mean Points', fontsize=14, fontweight='bold')
    ax1.set_title('Salary vs Points Relationship: \nCubic Model with Histogram Bins', 
                 fontsize=16, fontweight='bold')
    ax1.legend(fontsize=12, loc='upper right')
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(8, 42)
    
    # 2. Value ratio plot
    bars = ax2.bar(bin_labels, value_ratios, alpha=0.8, color=['lightcoral', 'gold', 'lightgreen', 'lightblue', 'plum'], 
                  edgecolor='black', linewidth=1.5)
    
    # Highlight the sweet spot bar
    bars[sweet_spot_idx].set_color('gold')
    bars[sweet_spot_idx].set_edgecolor('darkorange')
    bars[sweet_spot_idx].set_linewidth(3)
    
    # Add value labels on bars
    for i, (bar, value, count) in enumerate(zip(bars, value_ratios, bin_counts)):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f'{value:.3f}\nn={count}', ha='center', va='bottom', 
                fontweight='bold', fontsize=11)
    
    # Add horizontal line at sweet spot value
    ax2.axhline(y=sweet_spot_value, color='darkorange', linestyle='--', linewidth=2, alpha=0.7, 
               label=f'Optimal Value: {sweet_spot_value:.3f} pts/$')
    
    ax2.set_xlabel('Salary Bin', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Value Ratio (Points per $)', fontsize=14, fontweight='bold')
    ax2.set_title('Value Efficiency by Salary Range\n(Peak at $15-20 Range)', 
                 fontsize=16, fontweight='bold')
    ax2.legend(fontsize=12)
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.set_ylim(0, max(value_ratios) * 1.2)
    
    # Save the plot
    output_path = '/Users/mightenyip/Documents/GitHub/yfd-py-test/plots_images/week2_thursday_clean_hypothesis_showcase.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"📊 Clean hypothesis showcase plot saved to: {output_path}")
    
    plt.show()

def create_raw_data_comparison(df, quad_raw, cubic_raw, poly_features_quad_raw, poly_features_cubic_raw, r2_quad_raw, r2_cubic_raw):
    """Create comparison showing only raw data quadratic and cubic models."""
    print(f"\n📊 Creating Raw Data Comparison...")
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    fig.suptitle('Week 2 Thursday: Raw Data Models\nQuadratic vs Cubic Relationship', 
                 fontsize=18, fontweight='bold')
    
    # 1. Raw data - Quadratic model
    ax1.scatter(df['salary_clean'], df['points_clean'], alpha=0.7, s=60, color='steelblue', edgecolors='black', linewidth=0.5)
    
    X_smooth = np.linspace(df['salary_clean'].min(), df['salary_clean'].max(), 100)
    X_smooth_poly = poly_features_quad_raw.transform(X_smooth.reshape(-1, 1))
    y_smooth = quad_raw.predict(X_smooth_poly)
    ax1.plot(X_smooth, y_smooth, 'g-', linewidth=3, alpha=0.8, label=f'Quadratic (R²={r2_quad_raw:.3f})')
    
    ax1.set_xlabel('Salary ($)', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Points', fontsize=14, fontweight='bold')
    ax1.set_title('Raw Data - Quadratic Model', fontsize=16, fontweight='bold')
    ax1.legend(fontsize=12)
    ax1.grid(True, alpha=0.3)
    
    # 2. Raw data - Cubic model
    ax2.scatter(df['salary_clean'], df['points_clean'], alpha=0.7, s=60, color='steelblue', edgecolors='black', linewidth=0.5)
    
    X_smooth_poly = poly_features_cubic_raw.transform(X_smooth.reshape(-1, 1))
    y_smooth = cubic_raw.predict(X_smooth_poly)
    ax2.plot(X_smooth, y_smooth, 'b-', linewidth=3, alpha=0.8, label=f'Cubic (R²={r2_cubic_raw:.3f})')
    
    ax2.set_xlabel('Salary ($)', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Points', fontsize=14, fontweight='bold')
    ax2.set_title('Raw Data - Cubic Model', fontsize=16, fontweight='bold')
    ax2.legend(fontsize=12)
    ax2.grid(True, alpha=0.3)
    
    # Save the plot
    output_path = '/Users/mightenyip/Documents/GitHub/yfd-py-test/plots_images/week2_thursday_raw_data_models.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"📊 Raw data comparison plot saved to: {output_path}")
    
    plt.show()

def main():
    """Main analysis function."""
    print("Week 2 Thursday: Clean Hypothesis Showcase")
    print("=" * 50)
    
    # Load data
    df = load_and_clean_data()
    
    # Create salary bins and fit models
    (bin_stats, 
     quad_raw, cubic_raw, poly_features_quad_raw, poly_features_cubic_raw,
     r2_quad_raw, r2_cubic_raw,
     cubic_binned, poly_features_cubic_binned, r2_cubic_binned,
     salaries_binned, points_binned) = create_salary_bins_and_fit_models(df)
    
    # Create clean showcase plot
    create_clean_hypothesis_showcase(df, bin_stats, cubic_binned, poly_features_cubic_binned, r2_cubic_binned)
    
    # Create raw data comparison
    create_raw_data_comparison(df, quad_raw, cubic_raw, poly_features_quad_raw, poly_features_cubic_raw, r2_quad_raw, r2_cubic_raw)
    
    print(f"\n🎯 CLEAN ANALYSIS SUMMARY:")
    print("=" * 40)
    print(f"✅ RAW DATA RESULTS:")
    print(f"   • Quadratic: R² = {r2_quad_raw:.4f}")
    print(f"   • Cubic: R² = {r2_cubic_raw:.4f}")
    print(f"✅ BINNED DATA RESULTS:")
    print(f"   • Cubic: R² = {r2_cubic_binned:.4f}")

if __name__ == "__main__":
    main()

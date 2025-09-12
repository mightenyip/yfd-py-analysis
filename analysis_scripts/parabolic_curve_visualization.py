#!/usr/bin/env python3
"""
Parabolic curve visualization and outlier analysis for Week 2 Thursday data.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from scipy.optimize import curve_fit
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
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

def fit_parabolic_curve(df):
    """Fit a parabolic curve to the data and calculate statistics."""
    print(f"\n🧮 Fitting Parabolic Curve...")
    
    X = df['salary_clean'].values.reshape(-1, 1)
    y = df['points_clean'].values
    
    # Fit quadratic (parabolic) model
    poly_features = PolynomialFeatures(degree=2)
    X_poly = poly_features.fit_transform(X)
    poly_model = LinearRegression()
    poly_model.fit(X_poly, y)
    y_pred = poly_model.predict(X_poly)
    
    # Calculate R²
    r_squared = r2_score(y, y_pred)
    
    # Calculate correlation
    correlation = df['salary_clean'].corr(df['points_clean'])
    
    # Calculate p-value for correlation
    correlation_coef, p_value = stats.pearsonr(df['salary_clean'], df['points_clean'])
    
    # Get coefficients
    coeffs = poly_model.coef_
    intercept = poly_model.intercept_
    
    print(f"📈 Parabolic Model Results:")
    print(f"   Equation: y = {coeffs[2]:.4f}x² + {coeffs[1]:.4f}x + {intercept:.4f}")
    print(f"   R² = {r_squared:.4f}")
    print(f"   Correlation (r) = {correlation:.4f}")
    print(f"   P-value = {p_value:.4f}")
    
    # Check if it's actually parabolic (negative x² coefficient)
    if coeffs[2] < 0:
        print(f"   ✅ Downward parabolic curve (concave down)")
        # Find peak within realistic range
        peak_salary = -coeffs[1] / (2 * coeffs[2])
        if 10 <= peak_salary <= 40:
            peak_points = coeffs[2] * peak_salary**2 + coeffs[1] * peak_salary + intercept
            print(f"   📊 Peak at: ${peak_salary:.1f} salary, {peak_points:.1f} points")
        else:
            print(f"   📊 Peak outside realistic range: ${peak_salary:.1f}")
    else:
        print(f"   ❌ Upward parabolic curve (concave up)")
    
    return {
        'model': poly_model,
        'poly_features': poly_features,
        'r_squared': r_squared,
        'correlation': correlation,
        'p_value': p_value,
        'coeffs': coeffs,
        'intercept': intercept,
        'y_pred': y_pred
    }

def remove_outlier_and_analyze(df, outlier_name="Jayden Daniels"):
    """Remove the specified outlier and re-analyze."""
    print(f"\n🔍 Removing Outlier: {outlier_name}...")
    
    # Find the outlier
    outlier_mask = df['player_name'].str.contains(outlier_name, case=False, na=False)
    outlier_data = df[outlier_mask]
    
    if len(outlier_data) > 0:
        print(f"   Found outlier: {outlier_data.iloc[0]['player_name']} (${outlier_data.iloc[0]['salary_clean']:.0f}, {outlier_data.iloc[0]['points_clean']:.1f} pts)")
        
        # Remove outlier
        df_no_outlier = df[~outlier_mask].copy()
        
        print(f"   Dataset size: {len(df)} → {len(df_no_outlier)} players")
        
        # Re-fit parabolic curve
        results_no_outlier = fit_parabolic_curve(df_no_outlier)
        
        return df_no_outlier, results_no_outlier, outlier_data.iloc[0]
    else:
        print(f"   ❌ Outlier '{outlier_name}' not found")
        return df, None, None

def create_parabolic_visualization(df, results, df_no_outlier=None, results_no_outlier=None, outlier=None):
    """Create comprehensive visualization with parabolic curves."""
    print(f"\n📊 Creating Parabolic Curve Visualization...")
    
    # Set up the plotting style
    plt.style.use('default')
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Week 2 Thursday: Parabolic Curve Analysis', fontsize=16, fontweight='bold')
    
    # 1. Original data with parabolic curve
    ax1 = axes[0, 0]
    
    # Scatter plot
    ax1.scatter(df['salary_clean'], df['points_clean'], alpha=0.7, s=60, color='steelblue', edgecolors='black', linewidth=0.5, label='Data Points')
    
    # Highlight outlier if exists
    if outlier is not None:
        ax1.scatter(outlier['salary_clean'], outlier['points_clean'], s=100, color='red', edgecolors='darkred', linewidth=2, label=f'Outlier: {outlier["player_name"]}')
    
    # Plot parabolic curve
    X_smooth = np.linspace(df['salary_clean'].min(), df['salary_clean'].max(), 100)
    X_smooth_poly = results['poly_features'].transform(X_smooth.reshape(-1, 1))
    y_smooth = results['model'].predict(X_smooth_poly)
    
    ax1.plot(X_smooth, y_smooth, 'g-', linewidth=3, alpha=0.8, label=f'Parabolic Fit (R²={results["r_squared"]:.3f})')
    
    ax1.set_xlabel('Salary ($)')
    ax1.set_ylabel('Points')
    ax1.set_title('Original Data with Parabolic Curve')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Data without outlier
    ax2 = axes[0, 1]
    
    if df_no_outlier is not None and results_no_outlier is not None:
        # Scatter plot
        ax2.scatter(df_no_outlier['salary_clean'], df_no_outlier['points_clean'], alpha=0.7, s=60, color='lightgreen', edgecolors='black', linewidth=0.5, label='Data Points (No Outlier)')
        
        # Plot parabolic curve
        X_smooth_no_outlier = np.linspace(df_no_outlier['salary_clean'].min(), df_no_outlier['salary_clean'].max(), 100)
        X_smooth_poly_no_outlier = results_no_outlier['poly_features'].transform(X_smooth_no_outlier.reshape(-1, 1))
        y_smooth_no_outlier = results_no_outlier['model'].predict(X_smooth_poly_no_outlier)
        
        ax2.plot(X_smooth_no_outlier, y_smooth_no_outlier, 'r-', linewidth=3, alpha=0.8, label=f'Parabolic Fit (R²={results_no_outlier["r_squared"]:.3f})')
        
        ax2.set_xlabel('Salary ($)')
        ax2.set_ylabel('Points')
        ax2.set_title('Data Without Outlier')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
    else:
        ax2.text(0.5, 0.5, 'No outlier analysis', ha='center', va='center', transform=ax2.transAxes, fontsize=14)
        ax2.set_title('Data Without Outlier')
    
    # 3. Histogram with parabolic curve overlay
    ax3 = axes[1, 0]
    
    # Create histogram
    n, bins, patches = ax3.hist(df['points_clean'], bins=10, alpha=0.7, color='lightblue', edgecolor='black', density=True, label='Points Distribution')
    
    # Overlay parabolic curve (transformed to points space)
    # This is a bit tricky - we need to show how the parabolic relationship affects the distribution
    ax3.set_xlabel('Points')
    ax3.set_ylabel('Density')
    ax3.set_title('Points Distribution Histogram')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. Comparison of models
    ax4 = axes[1, 1]
    
    if df_no_outlier is not None and results_no_outlier is not None:
        # Plot both curves
        X_compare = np.linspace(10, 40, 100)
        
        # Original curve
        X_compare_poly = results['poly_features'].transform(X_compare.reshape(-1, 1))
        y_compare = results['model'].predict(X_compare_poly)
        ax4.plot(X_compare, y_compare, 'b-', linewidth=2, label=f'With Outlier (R²={results["r_squared"]:.3f})')
        
        # No outlier curve
        X_compare_poly_no_outlier = results_no_outlier['poly_features'].transform(X_compare.reshape(-1, 1))
        y_compare_no_outlier = results_no_outlier['model'].predict(X_compare_poly_no_outlier)
        ax4.plot(X_compare, y_compare_no_outlier, 'r-', linewidth=2, label=f'Without Outlier (R²={results_no_outlier["r_squared"]:.3f})')
        
        ax4.set_xlabel('Salary ($)')
        ax4.set_ylabel('Points')
        ax4.set_title('Model Comparison')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
    else:
        ax4.text(0.5, 0.5, 'No outlier comparison', ha='center', va='center', transform=ax4.transAxes, fontsize=14)
        ax4.set_title('Model Comparison')
    
    plt.tight_layout()
    
    # Save the plot
    output_path = '/Users/mightenyip/Documents/GitHub/yfd-py-test/plots_images/week2_thursday_parabolic_curve_analysis.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"📊 Parabolic curve plot saved to: {output_path}")
    
    plt.show()

def create_histogram_with_parabolic_overlay(df, results):
    """Create a histogram showing the parabolic relationship."""
    print(f"\n📊 Creating Histogram with Parabolic Overlay...")
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    fig.suptitle('Week 2 Thursday: Histogram with Parabolic Curve Overlay', fontsize=16, fontweight='bold')
    
    # 1. Salary vs Points with parabolic curve
    ax1.scatter(df['salary_clean'], df['points_clean'], alpha=0.7, s=60, color='steelblue', edgecolors='black', linewidth=0.5)
    
    # Plot parabolic curve
    X_smooth = np.linspace(df['salary_clean'].min(), df['salary_clean'].max(), 100)
    X_smooth_poly = results['poly_features'].transform(X_smooth.reshape(-1, 1))
    y_smooth = results['model'].predict(X_smooth_poly)
    
    ax1.plot(X_smooth, y_smooth, 'g-', linewidth=3, alpha=0.8, label=f'Parabolic Curve (R²={results["r_squared"]:.3f})')
    
    ax1.set_xlabel('Salary ($)')
    ax1.set_ylabel('Points')
    ax1.set_title('Salary vs Points with Parabolic Curve')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Histogram of points with normal distribution overlay
    ax2.hist(df['points_clean'], bins=10, alpha=0.7, color='lightblue', edgecolor='black', density=True, label='Points Distribution')
    
    # Overlay normal distribution
    mean_points = df['points_clean'].mean()
    std_points = df['points_clean'].std()
    x_norm = np.linspace(df['points_clean'].min(), df['points_clean'].max(), 100)
    y_norm = stats.norm.pdf(x_norm, mean_points, std_points)
    ax2.plot(x_norm, y_norm, 'r-', linewidth=2, label=f'Normal Fit (μ={mean_points:.1f}, σ={std_points:.1f})')
    
    ax2.set_xlabel('Points')
    ax2.set_ylabel('Density')
    ax2.set_title('Points Distribution with Normal Overlay')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save the plot
    output_path = '/Users/mightenyip/Documents/GitHub/yfd-py-test/plots_images/week2_thursday_histogram_parabolic_overlay.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"📊 Histogram with parabolic overlay saved to: {output_path}")
    
    plt.show()

def compare_with_without_outlier(results, results_no_outlier, outlier):
    """Compare the models with and without the outlier."""
    print(f"\n🔍 OUTLIER IMPACT ANALYSIS:")
    print("=" * 50)
    
    if results_no_outlier is None:
        print("❌ No outlier analysis available")
        return
    
    print(f"📊 Model Comparison:")
    print(f"{'Metric':<20} {'With Outlier':<15} {'Without Outlier':<15} {'Difference':<15}")
    print("-" * 65)
    
    # R² comparison
    r2_diff = results_no_outlier['r_squared'] - results['r_squared']
    print(f"{'R²':<20} {results['r_squared']:<15.4f} {results_no_outlier['r_squared']:<15.4f} {r2_diff:<15.4f}")
    
    # Correlation comparison
    corr_diff = results_no_outlier['correlation'] - results['correlation']
    print(f"{'Correlation (r)':<20} {results['correlation']:<15.4f} {results_no_outlier['correlation']:<15.4f} {corr_diff:<15.4f}")
    
    # P-value comparison
    p_diff = results_no_outlier['p_value'] - results['p_value']
    print(f"{'P-value':<20} {results['p_value']:<15.4f} {results_no_outlier['p_value']:<15.4f} {p_diff:<15.4f}")
    
    # Coefficient comparison
    coeff_diff = results_no_outlier['coeffs'][2] - results['coeffs'][2]
    print(f"{'x² Coefficient':<20} {results['coeffs'][2]:<15.4f} {results_no_outlier['coeffs'][2]:<15.4f} {coeff_diff:<15.4f}")
    
    print(f"\n🎯 Key Insights:")
    
    if r2_diff > 0:
        print(f"   ✅ Removing outlier improves model fit (R² increases by {r2_diff:.4f})")
    else:
        print(f"   ❌ Removing outlier worsens model fit (R² decreases by {abs(r2_diff):.4f})")
    
    if abs(corr_diff) > 0.05:
        print(f"   📊 Correlation changes significantly ({corr_diff:+.4f})")
    else:
        print(f"   📊 Correlation remains stable ({corr_diff:+.4f})")
    
    if results_no_outlier['coeffs'][2] < 0 and results['coeffs'][2] < 0:
        print(f"   ✅ Both models show downward parabolic curve")
    elif results_no_outlier['coeffs'][2] < 0 and results['coeffs'][2] >= 0:
        print(f"   🔄 Removing outlier reveals downward parabolic curve")
    elif results_no_outlier['coeffs'][2] >= 0 and results['coeffs'][2] < 0:
        print(f"   🔄 Outlier was creating downward parabolic curve")
    
    print(f"\n💰 Outlier Impact on Hypothesis:")
    if outlier is not None:
        print(f"   Outlier: {outlier['player_name']} (${outlier['salary_clean']:.0f}, {outlier['points_clean']:.1f} pts)")
        print(f"   Value ratio: {outlier['points_clean'] / outlier['salary_clean']:.3f} pts/$")
        
        # Check if outlier supports or contradicts hypothesis
        if outlier['salary_clean'] > 20:
            if outlier['points_clean'] / outlier['salary_clean'] > 0.5:
                print(f"   📊 Outlier contradicts sunk cost hypothesis (high salary, good value)")
            else:
                print(f"   📊 Outlier supports sunk cost hypothesis (high salary, poor value)")
        else:
            print(f"   📊 Outlier is not in high salary range")

def main():
    """Main analysis function."""
    print("Week 2 Thursday: Parabolic Curve Visualization and Outlier Analysis")
    print("=" * 70)
    
    # Load data
    df = load_and_clean_data()
    
    # Fit parabolic curve to original data
    results = fit_parabolic_curve(df)
    
    # Remove outlier and re-analyze
    df_no_outlier, results_no_outlier, outlier = remove_outlier_and_analyze(df, "Jayden Daniels")
    
    # Create visualizations
    create_parabolic_visualization(df, results, df_no_outlier, results_no_outlier, outlier)
    create_histogram_with_parabolic_overlay(df, results)
    
    # Compare models
    compare_with_without_outlier(results, results_no_outlier, outlier)
    
    print(f"\n🎉 Parabolic curve analysis complete! Check the saved plots for visual insights.")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Compare Week 1, Week 2 Thursday, and Combined Week 1+Week 2 Sunday analysis results.
This script creates a comprehensive comparison of all our analyses.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import r2_score
import warnings
warnings.filterwarnings('ignore')

def load_all_datasets():
    """Load all available datasets."""
    print("📊 Loading all datasets...")
    
    datasets = {}
    
    # Week 1 data
    try:
        week1_df = pd.read_csv('data_csv/yahoo_daily_fantasy_2025_week1_completed_page.csv')
        week1_df['salary_clean'] = week1_df['salary'].str.replace('$', '').astype(float)
        week1_df['points_clean'] = pd.to_numeric(week1_df['points'], errors='coerce')
        week1_df = week1_df.dropna(subset=['salary_clean', 'points_clean'])
        week1_active = week1_df[week1_df['points_clean'] > 0].copy()
        datasets['Week 1'] = week1_active
        print(f"   Week 1: {len(week1_active)} active players")
    except Exception as e:
        print(f"   Week 1: Error loading - {e}")
    
    # Week 2 Thursday data
    try:
        week2_thurs_df = pd.read_csv('data_csv/week2_Thurs.csv')
        week2_thurs_df['salary_clean'] = week2_thurs_df['salary'].str.replace('$', '').astype(float)
        week2_thurs_df['points_clean'] = pd.to_numeric(week2_thurs_df['points'], errors='coerce')
        week2_thurs_df = week2_thurs_df.dropna(subset=['salary_clean', 'points_clean'])
        week2_thurs_active = week2_thurs_df[week2_thurs_df['points_clean'] > 0].copy()
        datasets['Week 2 Thursday'] = week2_thurs_active
        print(f"   Week 2 Thursday: {len(week2_thurs_active)} active players")
    except Exception as e:
        print(f"   Week 2 Thursday: Error loading - {e}")
    
    # Week 2 Sunday data
    try:
        week2_sun_df = pd.read_csv('data_csv/week2_Sunday.csv')
        week2_sun_df['salary_clean'] = week2_sun_df['salary'].str.replace('$', '').astype(float)
        week2_sun_df['points_clean'] = pd.to_numeric(week2_sun_df['points'], errors='coerce')
        week2_sun_df = week2_sun_df.dropna(subset=['salary_clean', 'points_clean'])
        week2_sun_active = week2_sun_df[week2_sun_df['points_clean'] > 0].copy()
        datasets['Week 2 Sunday'] = week2_sun_active
        print(f"   Week 2 Sunday: {len(week2_sun_active)} active players")
    except Exception as e:
        print(f"   Week 2 Sunday: Error loading - {e}")
    
    # Combined Week 1 + Week 2 Sunday
    if 'Week 1' in datasets and 'Week 2 Sunday' in datasets:
        combined_df = pd.concat([datasets['Week 1'], datasets['Week 2 Sunday']], ignore_index=True)
        datasets['Combined (Week 1 + Week 2 Sunday)'] = combined_df
        print(f"   Combined: {len(combined_df)} active players")
    
    return datasets

def analyze_dataset(df, name):
    """Analyze a single dataset."""
    if len(df) == 0:
        return None
    
    X = df['salary_clean'].values.reshape(-1, 1)
    y = df['points_clean'].values
    
    # Calculate correlation
    correlation, p_value = stats.pearsonr(X.flatten(), y)
    
    # Fit models
    models = {}
    
    # Linear
    linear_model = LinearRegression()
    linear_model.fit(X, y)
    linear_pred = linear_model.predict(X)
    models['Linear'] = r2_score(y, linear_pred)
    
    # Quadratic
    poly2 = PolynomialFeatures(degree=2)
    X_poly2 = poly2.fit_transform(X)
    quad_model = LinearRegression()
    quad_model.fit(X_poly2, y)
    quad_pred = quad_model.predict(X_poly2)
    models['Quadratic'] = r2_score(y, quad_pred)
    
    # Cubic
    poly3 = PolynomialFeatures(degree=3)
    X_poly3 = poly3.fit_transform(X)
    cubic_model = LinearRegression()
    cubic_model.fit(X_poly3, y)
    cubic_pred = cubic_model.predict(X_poly3)
    models['Cubic'] = r2_score(y, cubic_pred)
    
    # Value analysis by salary range
    df_copy = df.copy()
    df_copy['salary_bin'] = pd.cut(df_copy['salary_clean'], 
                                  bins=[0, 15, 20, 25, 30, 35, 40], 
                                  labels=['$10-15', '$15-20', '$20-25', '$25-30', '$30-35', '$35-40'])
    
    value_analysis = df_copy.groupby('salary_bin').agg({
        'points_clean': ['count', 'mean'],
        'salary_clean': 'mean'
    })
    
    if len(value_analysis) > 0:
        value_analysis['points_per_dollar'] = (value_analysis['points_clean']['mean'] / 
                                              value_analysis['salary_clean']['mean'])
        best_range = value_analysis['points_per_dollar'].idxmax()
        best_value = float(value_analysis.loc[best_range, 'points_per_dollar'])
    else:
        best_range = "N/A"
        best_value = 0
    
    return {
        'name': name,
        'n_players': len(df),
        'correlation': correlation,
        'r_squared': correlation**2,
        'p_value': p_value,
        'models': models,
        'best_range': best_range,
        'best_value': best_value,
        'data': df
    }

def create_comparison_plot(results):
    """Create a comprehensive comparison plot."""
    print("\n📊 Creating comparison visualization...")
    
    # Set up the plot
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('Fantasy Football Salary vs Points Analysis: Complete Comparison', fontsize=16, fontweight='bold')
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
    
    # Plot each dataset
    for i, result in enumerate(results):
        if result is None:
            continue
            
        row = i // 3
        col = i % 3
        ax = axes[row, col]
        
        df = result['data']
        X = df['salary_clean'].values.reshape(-1, 1)
        y = df['points_clean'].values
        
        # Scatter plot
        ax.scatter(df['salary_clean'], df['points_clean'], 
                  alpha=0.6, s=30, c=colors[i], edgecolors='black', linewidth=0.3)
        
        # Add regression lines
        # Linear
        linear_model = LinearRegression()
        linear_model.fit(X, y)
        linear_pred = linear_model.predict(X)
        sort_idx = np.argsort(X.flatten())
        ax.plot(X[sort_idx].flatten(), linear_pred[sort_idx], 'k-', linewidth=2, alpha=0.8, label='Linear')
        
        # Quadratic
        poly2 = PolynomialFeatures(degree=2)
        X_poly2 = poly2.fit_transform(X)
        quad_model = LinearRegression()
        quad_model.fit(X_poly2, y)
        quad_pred = quad_model.predict(X_poly2)
        ax.plot(X[sort_idx].flatten(), quad_pred[sort_idx], 'r--', linewidth=2, alpha=0.8, label='Quadratic')
        
        # Cubic
        poly3 = PolynomialFeatures(degree=3)
        X_poly3 = poly3.fit_transform(X)
        cubic_model = LinearRegression()
        cubic_model.fit(X_poly3, y)
        cubic_pred = cubic_model.predict(X_poly3)
        ax.plot(X[sort_idx].flatten(), cubic_pred[sort_idx], 'g:', linewidth=2, alpha=0.8, label='Cubic')
        
        # Customize plot
        ax.set_xlabel('Salary ($)')
        ax.set_ylabel('Points')
        ax.set_title(f'{result["name"]}\n(n={result["n_players"]}, r={result["correlation"]:.3f}, R²={result["r_squared"]:.3f})')
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
        
        # Add text box with key stats
        textstr = f'Best Value: {result["best_range"]}\n({result["best_value"]:.3f} pts/$)'
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
        ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=9,
                verticalalignment='top', bbox=props)
    
    # Hide empty subplots
    for i in range(len(results), 6):
        row = i // 3
        col = i % 3
        axes[row, col].set_visible(False)
    
    plt.tight_layout()
    plt.savefig('plots_images/complete_comparison_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("   ✅ Saved: plots_images/complete_comparison_analysis.png")

def create_summary_table(results):
    """Create a summary comparison table."""
    print("\n📋 SUMMARY COMPARISON TABLE")
    print("=" * 80)
    print(f"{'Dataset':<25} {'Players':<8} {'Correlation':<12} {'R²':<8} {'Best Model':<12} {'Best Value':<15}")
    print("-" * 80)
    
    for result in results:
        if result is None:
            continue
        
        best_model = max(result['models'].keys(), key=lambda k: result['models'][k])
        best_r2 = result['models'][best_model]
        
        print(f"{result['name']:<25} {result['n_players']:<8} {result['correlation']:<12.4f} "
              f"{result['r_squared']:<8.4f} {best_model:<12} {result['best_range']} ({result['best_value']:.3f})")
    
    print("=" * 80)

def create_detailed_analysis(results):
    """Create detailed analysis comparison."""
    print("\n🔍 DETAILED ANALYSIS COMPARISON")
    print("=" * 60)
    
    for result in results:
        if result is None:
            continue
            
        print(f"\n📊 {result['name']}")
        print("-" * 40)
        print(f"Sample Size: {result['n_players']} active players")
        print(f"Correlation (r): {result['correlation']:.4f}")
        print(f"R²: {result['r_squared']:.4f}")
        print(f"P-value: {result['p_value']:.6f}")
        print(f"Optimal Value Range: {result['best_range']} ({result['best_value']:.3f} pts/$)")
        
        print("Model Performance:")
        for model_name, r2 in result['models'].items():
            print(f"  {model_name}: R² = {r2:.4f}")
        
        # Statistical significance
        if result['p_value'] < 0.001:
            significance = "Highly significant (p < 0.001)"
        elif result['p_value'] < 0.01:
            significance = "Very significant (p < 0.01)"
        elif result['p_value'] < 0.05:
            significance = "Significant (p < 0.05)"
        else:
            significance = "Not significant (p ≥ 0.05)"
        
        print(f"Statistical Significance: {significance}")

def main():
    """Main analysis function."""
    print("🔍 Complete Fantasy Football Analysis Comparison")
    print("=" * 60)
    
    # Load all datasets
    datasets = load_all_datasets()
    
    # Analyze each dataset
    results = []
    for name, df in datasets.items():
        result = analyze_dataset(df, name)
        results.append(result)
    
    # Create visualizations
    create_comparison_plot(results)
    
    # Create summary
    create_summary_table(results)
    create_detailed_analysis(results)
    
    # Key insights
    print("\n🎯 KEY INSIGHTS")
    print("=" * 60)
    
    # Find best correlation
    best_corr = max([r for r in results if r is not None], key=lambda x: abs(x['correlation']))
    print(f"Strongest Correlation: {best_corr['name']} (r = {best_corr['correlation']:.4f})")
    
    # Find largest sample
    largest_sample = max([r for r in results if r is not None], key=lambda x: x['n_players'])
    print(f"Largest Sample: {largest_sample['name']} ({largest_sample['n_players']} players)")
    
    # Find best R²
    best_r2 = max([r for r in results if r is not None], key=lambda x: max(x['models'].values()))
    best_model = max(best_r2['models'].keys(), key=lambda k: best_r2['models'][k])
    print(f"Best Model Fit: {best_r2['name']} - {best_model} (R² = {best_r2['models'][best_model]:.4f})")
    
    # Compare Week 1 vs Combined
    week1_result = next((r for r in results if r and 'Week 1' in r['name'] and 'Combined' not in r['name']), None)
    combined_result = next((r for r in results if r and 'Combined' in r['name']), None)
    
    if week1_result and combined_result:
        print(f"\n📈 Week 1 vs Combined Analysis:")
        print(f"  Week 1 only: r = {week1_result['correlation']:.4f}, n = {week1_result['n_players']}")
        print(f"  Combined: r = {combined_result['correlation']:.4f}, n = {combined_result['n_players']}")
        
        if abs(combined_result['correlation']) > abs(week1_result['correlation']):
            print(f"  ✅ Combined dataset shows stronger correlation (+{abs(combined_result['correlation']) - abs(week1_result['correlation']):.4f})")
        else:
            print(f"  ❌ Combined dataset shows weaker correlation ({abs(combined_result['correlation']) - abs(week1_result['correlation']):.4f})")
    
    print(f"\n📊 Complete comparison saved to: plots_images/complete_comparison_analysis.png")

if __name__ == "__main__":
    main()

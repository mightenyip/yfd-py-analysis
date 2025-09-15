#!/usr/bin/env python3
"""
Direct comparison between Week 1 only vs Combined Week 1 + Week 2 Sunday analysis.
This script creates a focused comparison to answer the user's specific question.
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

def load_week1_and_combined():
    """Load Week 1 and Combined datasets."""
    print("📊 Loading Week 1 and Combined datasets...")
    
    # Week 1 data
    week1_df = pd.read_csv('data_csv/yahoo_daily_fantasy_2025_week1_completed_page.csv')
    week1_df['salary_clean'] = week1_df['salary'].str.replace('$', '').astype(float)
    week1_df['points_clean'] = pd.to_numeric(week1_df['points'], errors='coerce')
    week1_df = week1_df.dropna(subset=['salary_clean', 'points_clean'])
    week1_active = week1_df[week1_df['points_clean'] > 0].copy()
    
    # Week 2 Sunday data
    week2_sun_df = pd.read_csv('data_csv/week2_Sunday.csv')
    week2_sun_df['salary_clean'] = week2_sun_df['salary'].str.replace('$', '').astype(float)
    week2_sun_df['points_clean'] = pd.to_numeric(week2_sun_df['points'], errors='coerce')
    week2_sun_df = week2_sun_df.dropna(subset=['salary_clean', 'points_clean'])
    week2_sun_active = week2_sun_df[week2_sun_df['points_clean'] > 0].copy()
    
    # Combined dataset
    combined_df = pd.concat([week1_active, week2_sun_active], ignore_index=True)
    
    print(f"   Week 1: {len(week1_active)} active players")
    print(f"   Week 2 Sunday: {len(week2_sun_active)} active players")
    print(f"   Combined: {len(combined_df)} active players")
    
    return week1_active, combined_df

def analyze_dataset(df, name):
    """Analyze a dataset and return key metrics."""
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
        'data': df,
        'value_analysis': value_analysis
    }

def create_comparison_plot(week1_result, combined_result):
    """Create a focused comparison plot."""
    print("\n📊 Creating Week 1 vs Combined comparison plot...")
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Week 1 vs Combined (Week 1 + Week 2 Sunday) Analysis Comparison', fontsize=16, fontweight='bold')
    
    # Plot 1: Week 1 scatter with regression lines
    ax1 = axes[0, 0]
    df1 = week1_result['data']
    X1 = df1['salary_clean'].values.reshape(-1, 1)
    y1 = df1['points_clean'].values
    
    ax1.scatter(df1['salary_clean'], df1['points_clean'], 
               alpha=0.6, s=30, c='blue', edgecolors='black', linewidth=0.3)
    
    # Add regression lines
    sort_idx1 = np.argsort(X1.flatten())
    
    # Linear
    linear_model1 = LinearRegression()
    linear_model1.fit(X1, y1)
    linear_pred1 = linear_model1.predict(X1)
    ax1.plot(X1[sort_idx1].flatten(), linear_pred1[sort_idx1], 'k-', linewidth=2, alpha=0.8, label='Linear')
    
    # Quadratic
    poly2_1 = PolynomialFeatures(degree=2)
    X_poly2_1 = poly2_1.fit_transform(X1)
    quad_model1 = LinearRegression()
    quad_model1.fit(X_poly2_1, y1)
    quad_pred1 = quad_model1.predict(X_poly2_1)
    ax1.plot(X1[sort_idx1].flatten(), quad_pred1[sort_idx1], 'r--', linewidth=2, alpha=0.8, label='Quadratic')
    
    # Cubic
    poly3_1 = PolynomialFeatures(degree=3)
    X_poly3_1 = poly3_1.fit_transform(X1)
    cubic_model1 = LinearRegression()
    cubic_model1.fit(X_poly3_1, y1)
    cubic_pred1 = cubic_model1.predict(X_poly3_1)
    ax1.plot(X1[sort_idx1].flatten(), cubic_pred1[sort_idx1], 'g:', linewidth=2, alpha=0.8, label='Cubic')
    
    ax1.set_xlabel('Salary ($)')
    ax1.set_ylabel('Points')
    ax1.set_title(f'Week 1 Only\n(n={week1_result["n_players"]}, r={week1_result["correlation"]:.4f}, R²={week1_result["r_squared"]:.4f})')
    ax1.legend(fontsize=8)
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Combined scatter with regression lines
    ax2 = axes[0, 1]
    df2 = combined_result['data']
    X2 = df2['salary_clean'].values.reshape(-1, 1)
    y2 = df2['points_clean'].values
    
    # Color by dataset
    week1_mask = df2.index < len(week1_result['data'])
    ax2.scatter(df2.loc[week1_mask, 'salary_clean'], df2.loc[week1_mask, 'points_clean'], 
               alpha=0.6, s=30, c='blue', edgecolors='black', linewidth=0.3, label='Week 1')
    ax2.scatter(df2.loc[~week1_mask, 'salary_clean'], df2.loc[~week1_mask, 'points_clean'], 
               alpha=0.6, s=30, c='red', edgecolors='black', linewidth=0.3, label='Week 2 Sunday')
    
    # Add regression lines
    sort_idx2 = np.argsort(X2.flatten())
    
    # Linear
    linear_model2 = LinearRegression()
    linear_model2.fit(X2, y2)
    linear_pred2 = linear_model2.predict(X2)
    ax2.plot(X2[sort_idx2].flatten(), linear_pred2[sort_idx2], 'k-', linewidth=2, alpha=0.8, label='Linear')
    
    # Quadratic
    poly2_2 = PolynomialFeatures(degree=2)
    X_poly2_2 = poly2_2.fit_transform(X2)
    quad_model2 = LinearRegression()
    quad_model2.fit(X_poly2_2, y2)
    quad_pred2 = quad_model2.predict(X_poly2_2)
    ax2.plot(X2[sort_idx2].flatten(), quad_pred2[sort_idx2], 'r--', linewidth=2, alpha=0.8, label='Quadratic')
    
    # Cubic
    poly3_2 = PolynomialFeatures(degree=3)
    X_poly3_2 = poly3_2.fit_transform(X2)
    cubic_model2 = LinearRegression()
    cubic_model2.fit(X_poly3_2, y2)
    cubic_pred2 = cubic_model2.predict(X_poly3_2)
    ax2.plot(X2[sort_idx2].flatten(), cubic_pred2[sort_idx2], 'g:', linewidth=2, alpha=0.8, label='Cubic')
    
    ax2.set_xlabel('Salary ($)')
    ax2.set_ylabel('Points')
    ax2.set_title(f'Combined (Week 1 + Week 2 Sunday)\n(n={combined_result["n_players"]}, r={combined_result["correlation"]:.4f}, R²={combined_result["r_squared"]:.4f})')
    ax2.legend(fontsize=8)
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Value analysis comparison
    ax3 = axes[1, 0]
    
    # Week 1 value analysis
    week1_values = []
    week1_ranges = []
    for bin_name in week1_result['value_analysis'].index:
        if pd.notna(bin_name):
            pts_per_dollar = float(week1_result['value_analysis'].loc[bin_name, 'points_per_dollar'])
            week1_values.append(pts_per_dollar)
            week1_ranges.append(bin_name)
    
    # Combined value analysis
    combined_values = []
    combined_ranges = []
    for bin_name in combined_result['value_analysis'].index:
        if pd.notna(bin_name):
            pts_per_dollar = float(combined_result['value_analysis'].loc[bin_name, 'points_per_dollar'])
            combined_values.append(pts_per_dollar)
            combined_ranges.append(bin_name)
    
    x_pos = np.arange(len(week1_ranges))
    width = 0.35
    
    ax3.bar(x_pos - width/2, week1_values, width, label='Week 1 Only', alpha=0.8, color='blue')
    ax3.bar(x_pos + width/2, combined_values, width, label='Combined', alpha=0.8, color='red')
    
    ax3.set_xlabel('Salary Range')
    ax3.set_ylabel('Points per Dollar')
    ax3.set_title('Value Analysis Comparison (Points per Dollar)')
    ax3.set_xticks(x_pos)
    ax3.set_xticklabels(week1_ranges, rotation=45)
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Model performance comparison
    ax4 = axes[1, 1]
    
    models = ['Linear', 'Quadratic', 'Cubic']
    week1_r2s = [week1_result['models'][m] for m in models]
    combined_r2s = [combined_result['models'][m] for m in models]
    
    x_pos = np.arange(len(models))
    width = 0.35
    
    ax4.bar(x_pos - width/2, week1_r2s, width, label='Week 1 Only', alpha=0.8, color='blue')
    ax4.bar(x_pos + width/2, combined_r2s, width, label='Combined', alpha=0.8, color='red')
    
    ax4.set_xlabel('Model Type')
    ax4.set_ylabel('R² Score')
    ax4.set_title('Model Performance Comparison (R²)')
    ax4.set_xticks(x_pos)
    ax4.set_xticklabels(models)
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    # Add value labels on bars
    for i, (w1, c1) in enumerate(zip(week1_r2s, combined_r2s)):
        ax4.text(i - width/2, w1 + 0.01, f'{w1:.3f}', ha='center', va='bottom', fontsize=9)
        ax4.text(i + width/2, c1 + 0.01, f'{c1:.3f}', ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    plt.savefig('plots_images/week1_vs_combined_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("   ✅ Saved: plots_images/week1_vs_combined_comparison.png")

def print_detailed_comparison(week1_result, combined_result):
    """Print detailed comparison analysis."""
    print("\n" + "="*70)
    print("📊 DETAILED WEEK 1 vs COMBINED COMPARISON")
    print("="*70)
    
    print(f"\n🔍 SAMPLE SIZE COMPARISON:")
    print(f"   Week 1 Only: {week1_result['n_players']} players")
    print(f"   Combined: {combined_result['n_players']} players")
    print(f"   Increase: +{combined_result['n_players'] - week1_result['n_players']} players (+{((combined_result['n_players'] - week1_result['n_players']) / week1_result['n_players'] * 100):.1f}%)")
    
    print(f"\n📈 CORRELATION COMPARISON:")
    print(f"   Week 1 Only: r = {week1_result['correlation']:.4f}")
    print(f"   Combined: r = {combined_result['correlation']:.4f}")
    diff = combined_result['correlation'] - week1_result['correlation']
    print(f"   Difference: {diff:+.4f} ({'Stronger' if diff > 0 else 'Weaker'} correlation)")
    
    print(f"\n📊 R² COMPARISON:")
    print(f"   Week 1 Only: R² = {week1_result['r_squared']:.4f}")
    print(f"   Combined: R² = {combined_result['r_squared']:.4f}")
    r2_diff = combined_result['r_squared'] - week1_result['r_squared']
    print(f"   Difference: {r2_diff:+.4f} ({'Better' if r2_diff > 0 else 'Worse'} fit)")
    
    print(f"\n🎯 OPTIMAL VALUE RANGE:")
    print(f"   Week 1 Only: {week1_result['best_range']} ({week1_result['best_value']:.3f} pts/$)")
    print(f"   Combined: {combined_result['best_range']} ({combined_result['best_value']:.3f} pts/$)")
    
    print(f"\n🔧 MODEL PERFORMANCE COMPARISON:")
    print(f"   {'Model':<12} {'Week 1 R²':<12} {'Combined R²':<12} {'Difference':<12}")
    print("   " + "-"*50)
    for model in ['Linear', 'Quadratic', 'Cubic']:
        w1_r2 = week1_result['models'][model]
        c_r2 = combined_result['models'][model]
        diff = c_r2 - w1_r2
        print(f"   {model:<12} {w1_r2:<12.4f} {c_r2:<12.4f} {diff:+.4f}")
    
    print(f"\n📋 STATISTICAL SIGNIFICANCE:")
    print(f"   Week 1 Only: p = {week1_result['p_value']:.6f} ({'Highly significant' if week1_result['p_value'] < 0.001 else 'Significant' if week1_result['p_value'] < 0.05 else 'Not significant'})")
    print(f"   Combined: p = {combined_result['p_value']:.6f} ({'Highly significant' if combined_result['p_value'] < 0.001 else 'Significant' if combined_result['p_value'] < 0.05 else 'Not significant'})")
    
    print(f"\n🎯 CONCLUSION:")
    if abs(combined_result['correlation']) > abs(week1_result['correlation']):
        print("   ✅ COMBINING DATASETS IMPROVED CORRELATION")
        print(f"   The larger sample size (Week 1 + Week 2 Sunday) shows a stronger relationship")
        print(f"   between salary and points, suggesting more robust findings.")
    else:
        print("   ❌ COMBINING DATASETS WEAKENED CORRELATION")
        print(f"   The larger sample size (Week 1 + Week 2 Sunday) shows a weaker relationship")
        print(f"   between salary and points, suggesting Week 1 had a stronger pattern.")
    
    print(f"\n   However, the combined dataset provides:")
    print(f"   • Larger sample size for more robust statistical power")
    print(f"   • Cross-week validation of the salary-performance relationship")
    print(f"   • More generalizable findings across different game contexts")

def main():
    """Main analysis function."""
    print("🔍 Week 1 vs Combined Analysis Comparison")
    print("=" * 50)
    
    # Load datasets
    week1_df, combined_df = load_week1_and_combined()
    
    # Analyze datasets
    week1_result = analyze_dataset(week1_df, "Week 1 Only")
    combined_result = analyze_dataset(combined_df, "Combined (Week 1 + Week 2 Sunday)")
    
    # Create comparison plot
    create_comparison_plot(week1_result, combined_result)
    
    # Print detailed comparison
    print_detailed_comparison(week1_result, combined_result)
    
    print(f"\n📊 Comparison plot saved to: plots_images/week1_vs_combined_comparison.png")

if __name__ == "__main__":
    main()

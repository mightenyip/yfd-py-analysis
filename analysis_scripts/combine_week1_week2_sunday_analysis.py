#!/usr/bin/env python3
"""
Combine Week 1 and Week 2 Sunday data to analyze points vs salary correlation.
This script will merge the datasets and perform comprehensive analysis.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import r2_score, mean_squared_error
import warnings
warnings.filterwarnings('ignore')

def load_and_clean_data():
    """Load and clean both datasets."""
    print("📊 Loading Week 1 and Week 2 Sunday data...")
    
    # Load Week 1 data
    week1_df = pd.read_csv('data_csv/yahoo_daily_fantasy_2025_week1_completed_page.csv')
    print(f"   Week 1 data: {len(week1_df)} players")
    
    # Load Week 2 Sunday data
    week2_sunday_df = pd.read_csv('data_csv/week2_Sunday.csv')
    print(f"   Week 2 Sunday data: {len(week2_sunday_df)} players")
    
    # Clean Week 1 data
    week1_clean = week1_df.copy()
    week1_clean['salary_clean'] = week1_clean['salary'].str.replace('$', '').astype(float)
    week1_clean['points_clean'] = pd.to_numeric(week1_clean['points'], errors='coerce')
    week1_clean['week'] = 'Week 1'
    week1_clean['day'] = 'Mixed'  # Since we can't separate Sunday games
    
    # Clean Week 2 Sunday data
    week2_clean = week2_sunday_df.copy()
    week2_clean['salary_clean'] = week2_clean['salary'].str.replace('$', '').astype(float)
    week2_clean['points_clean'] = pd.to_numeric(week2_clean['points'], errors='coerce')
    
    # Remove rows with missing data
    week1_clean = week1_clean.dropna(subset=['salary_clean', 'points_clean'])
    week2_clean = week2_clean.dropna(subset=['salary_clean', 'points_clean'])
    
    print(f"   Week 1 clean data: {len(week1_clean)} players")
    print(f"   Week 2 Sunday clean data: {len(week2_clean)} players")
    
    return week1_clean, week2_clean

def combine_datasets(week1_df, week2_df):
    """Combine the two datasets."""
    print("\n🔄 Combining datasets...")
    
    # Select common columns
    common_cols = ['player_name', 'position', 'salary_clean', 'points_clean', 'week', 'day']
    
    # Ensure both dataframes have the required columns
    week1_combined = week1_df[common_cols].copy()
    week2_combined = week2_df[common_cols].copy()
    
    # Add dataset identifier
    week1_combined['dataset'] = 'Week 1 (Mixed Days)'
    week2_combined['dataset'] = 'Week 2 Sunday'
    
    # Combine datasets
    combined_df = pd.concat([week1_combined, week2_combined], ignore_index=True)
    
    print(f"   Combined dataset: {len(combined_df)} total players")
    print(f"   Week 1: {len(week1_combined)} players")
    print(f"   Week 2 Sunday: {len(week2_combined)} players")
    
    return combined_df

def analyze_correlation(combined_df):
    """Analyze correlation between salary and points."""
    print("\n📈 Analyzing correlation...")
    
    # Remove zero-point players for active analysis
    active_df = combined_df[combined_df['points_clean'] > 0].copy()
    print(f"   Active players (points > 0): {len(active_df)}")
    
    # Calculate correlation
    correlation, p_value = stats.pearsonr(active_df['salary_clean'], active_df['points_clean'])
    
    print(f"   Correlation (r): {correlation:.4f}")
    print(f"   P-value: {p_value:.6f}")
    print(f"   R²: {correlation**2:.4f}")
    
    # Compare with individual datasets
    week1_active = active_df[active_df['dataset'] == 'Week 1 (Mixed Days)']
    week2_active = active_df[active_df['dataset'] == 'Week 2 Sunday']
    
    if len(week1_active) > 0:
        corr1, p1 = stats.pearsonr(week1_active['salary_clean'], week1_active['points_clean'])
        print(f"   Week 1 only - Correlation: {corr1:.4f}, R²: {corr1**2:.4f}")
    
    if len(week2_active) > 0:
        corr2, p2 = stats.pearsonr(week2_active['salary_clean'], week2_active['points_clean'])
        print(f"   Week 2 Sunday only - Correlation: {corr2:.4f}, R²: {corr2**2:.4f}")
    
    return active_df, correlation, p_value

def fit_models(active_df):
    """Fit various regression models."""
    print("\n🔧 Fitting regression models...")
    
    X = active_df['salary_clean'].values.reshape(-1, 1)
    y = active_df['points_clean'].values
    
    models = {}
    
    # Linear model
    linear_model = LinearRegression()
    linear_model.fit(X, y)
    linear_pred = linear_model.predict(X)
    models['Linear'] = {
        'model': linear_model,
        'predictions': linear_pred,
        'r2': r2_score(y, linear_pred),
        'mse': mean_squared_error(y, linear_pred)
    }
    
    # Quadratic model
    poly2 = PolynomialFeatures(degree=2)
    X_poly2 = poly2.fit_transform(X)
    quad_model = LinearRegression()
    quad_model.fit(X_poly2, y)
    quad_pred = quad_model.predict(X_poly2)
    models['Quadratic'] = {
        'model': quad_model,
        'poly_features': poly2,
        'predictions': quad_pred,
        'r2': r2_score(y, quad_pred),
        'mse': mean_squared_error(y, quad_pred)
    }
    
    # Cubic model
    poly3 = PolynomialFeatures(degree=3)
    X_poly3 = poly3.fit_transform(X)
    cubic_model = LinearRegression()
    cubic_model.fit(X_poly3, y)
    cubic_pred = cubic_model.predict(X_poly3)
    models['Cubic'] = {
        'model': cubic_model,
        'poly_features': poly3,
        'predictions': cubic_pred,
        'r2': r2_score(y, cubic_pred),
        'mse': mean_squared_error(y, cubic_pred)
    }
    
    # Print model performance
    print("   Model Performance:")
    for name, model_data in models.items():
        print(f"   {name}: R² = {model_data['r2']:.4f}, MSE = {model_data['mse']:.2f}")
    
    return models

def create_visualizations(active_df, models, correlation, p_value):
    """Create comprehensive visualizations."""
    print("\n📊 Creating visualizations...")
    
    # Set up the plot style
    plt.style.use('default')
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Combined Week 1 & Week 2 Sunday: Salary vs Points Analysis', fontsize=16, fontweight='bold')
    
    # 1. Scatter plot with linear regression
    ax1 = axes[0, 0]
    scatter = ax1.scatter(active_df['salary_clean'], active_df['points_clean'], 
                         c=active_df['dataset'].map({'Week 1 (Mixed Days)': 'blue', 'Week 2 Sunday': 'red'}),
                         alpha=0.6, s=30)
    
    # Add linear regression line
    X = active_df['salary_clean'].values.reshape(-1, 1)
    y = active_df['points_clean'].values
    linear_pred = models['Linear']['predictions']
    
    # Sort for smooth line
    sort_idx = np.argsort(X.flatten())
    ax1.plot(X[sort_idx].flatten(), linear_pred[sort_idx], 'k-', linewidth=2, label='Linear Fit')
    
    ax1.set_xlabel('Salary ($)')
    ax1.set_ylabel('Points')
    ax1.set_title(f'Linear Regression\nR² = {models["Linear"]["r2"]:.4f}, r = {correlation:.4f}')
    ax1.legend(['Linear Fit', 'Week 1', 'Week 2 Sunday'])
    ax1.grid(True, alpha=0.3)
    
    # 2. Scatter plot with quadratic regression
    ax2 = axes[0, 1]
    ax2.scatter(active_df['salary_clean'], active_df['points_clean'], 
               c=active_df['dataset'].map({'Week 1 (Mixed Days)': 'blue', 'Week 2 Sunday': 'red'}),
               alpha=0.6, s=30)
    
    # Add quadratic regression line
    quad_pred = models['Quadratic']['predictions']
    ax2.plot(X[sort_idx].flatten(), quad_pred[sort_idx], 'g-', linewidth=2, label='Quadratic Fit')
    
    ax2.set_xlabel('Salary ($)')
    ax2.set_ylabel('Points')
    ax2.set_title(f'Quadratic Regression\nR² = {models["Quadratic"]["r2"]:.4f}')
    ax2.legend(['Quadratic Fit', 'Week 1', 'Week 2 Sunday'])
    ax2.grid(True, alpha=0.3)
    
    # 3. Scatter plot with cubic regression
    ax3 = axes[1, 0]
    ax3.scatter(active_df['salary_clean'], active_df['points_clean'], 
               c=active_df['dataset'].map({'Week 1 (Mixed Days)': 'blue', 'Week 1 (Mixed Days)': 'blue', 'Week 2 Sunday': 'red'}),
               alpha=0.6, s=30)
    
    # Add cubic regression line
    cubic_pred = models['Cubic']['predictions']
    ax3.plot(X[sort_idx].flatten(), cubic_pred[sort_idx], 'purple', linewidth=2, label='Cubic Fit')
    
    ax3.set_xlabel('Salary ($)')
    ax3.set_ylabel('Points')
    ax3.set_title(f'Cubic Regression\nR² = {models["Cubic"]["r2"]:.4f}')
    ax3.legend(['Cubic Fit', 'Week 1', 'Week 2 Sunday'])
    ax3.grid(True, alpha=0.3)
    
    # 4. Residuals plot
    ax4 = axes[1, 1]
    residuals = y - linear_pred
    ax4.scatter(linear_pred, residuals, alpha=0.6, s=30)
    ax4.axhline(y=0, color='r', linestyle='--')
    ax4.set_xlabel('Predicted Points')
    ax4.set_ylabel('Residuals')
    ax4.set_title('Residuals Plot (Linear Model)')
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('plots_images/combined_week1_week2_sunday_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("   ✅ Saved: plots_images/combined_week1_week2_sunday_analysis.png")

def analyze_value_by_salary_range(active_df):
    """Analyze value (points per dollar) by salary range."""
    print("\n💰 Analyzing value by salary range...")
    
    # Create salary bins
    active_df['salary_bin'] = pd.cut(active_df['salary_clean'], 
                                    bins=[0, 15, 20, 25, 30, 35, 40], 
                                    labels=['$10-15', '$15-20', '$20-25', '$25-30', '$30-35', '$35-40'])
    
    # Calculate value metrics by bin
    value_analysis = active_df.groupby('salary_bin').agg({
        'points_clean': ['count', 'mean', 'std'],
        'salary_clean': 'mean'
    }).round(2)
    
    # Calculate points per dollar
    value_analysis['points_per_dollar'] = (value_analysis['points_clean']['mean'] / 
                                          value_analysis['salary_clean']['mean']).round(3)
    
    print("   Value Analysis by Salary Range:")
    print("   " + "="*60)
    print(f"   {'Range':<10} {'Count':<6} {'Avg Points':<10} {'Avg Salary':<10} {'Pts/$':<8}")
    print("   " + "-"*60)
    
    for bin_name in value_analysis.index:
        if pd.notna(bin_name):
            count = int(value_analysis.loc[bin_name, ('points_clean', 'count')])
            avg_points = float(value_analysis.loc[bin_name, ('points_clean', 'mean')])
            avg_salary = float(value_analysis.loc[bin_name, ('salary_clean', 'mean')])
            pts_per_dollar = float(value_analysis.loc[bin_name, 'points_per_dollar'])
            print(f"   {bin_name:<10} {count:<6} {avg_points:<10.1f} {avg_salary:<10.1f} {pts_per_dollar:<8.3f}")
    
    return value_analysis

def main():
    """Main analysis function."""
    print("🔍 Combined Week 1 & Week 2 Sunday Analysis")
    print("=" * 60)
    
    # Load and clean data
    week1_df, week2_df = load_and_clean_data()
    
    # Combine datasets
    combined_df = combine_datasets(week1_df, week2_df)
    
    # Analyze correlation
    active_df, correlation, p_value = analyze_correlation(combined_df)
    
    # Fit models
    models = fit_models(active_df)
    
    # Create visualizations
    create_visualizations(active_df, models, correlation, p_value)
    
    # Analyze value by salary range
    value_analysis = analyze_value_by_salary_range(active_df)
    
    # Summary
    print("\n" + "="*60)
    print("📋 SUMMARY")
    print("="*60)
    print(f"Total players analyzed: {len(active_df)}")
    print(f"Combined correlation (r): {correlation:.4f}")
    print(f"Combined R²: {correlation**2:.4f}")
    print(f"P-value: {p_value:.6f}")
    print(f"Best model: {max(models.keys(), key=lambda k: models[k]['r2'])} (R² = {max(models[k]['r2'] for k in models):.4f})")
    
    # Find optimal salary range
    best_range = value_analysis['points_per_dollar'].idxmax()
    best_value = float(value_analysis.loc[best_range, 'points_per_dollar'])
    print(f"Optimal value range: {best_range} ({best_value:.3f} pts/$)")
    
    print(f"\n📊 Visualizations saved to: plots_images/combined_week1_week2_sunday_analysis.png")

if __name__ == "__main__":
    main()

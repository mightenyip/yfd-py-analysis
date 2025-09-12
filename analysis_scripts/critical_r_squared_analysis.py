#!/usr/bin/env python3
"""
Critical analysis of R² values and model quality for Week 2 Thursday data.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import r2_score, mean_squared_error
import warnings
warnings.filterwarnings('ignore')

def load_and_clean_data():
    """Load and clean the Week 2 Thursday data."""
    print("📊 Loading Week 2 Thursday data for critical R² analysis...")
    
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

def analyze_model_quality(df):
    """Analyze the quality of different models."""
    print(f"\n🧮 Critical Model Quality Analysis...")
    
    X = df['salary_clean'].values.reshape(-1, 1)
    y = df['points_clean'].values
    
    models = {}
    
    # 1. Linear model
    linear_model = LinearRegression()
    linear_model.fit(X, y)
    y_pred_linear = linear_model.predict(X)
    r2_linear = r2_score(y, y_pred_linear)
    mse_linear = mean_squared_error(y, y_pred_linear)
    
    models['Linear'] = {
        'model': linear_model,
        'r2': r2_linear,
        'mse': mse_linear,
        'y_pred': y_pred_linear
    }
    
    # 2. Quadratic (parabolic) model
    poly_features = PolynomialFeatures(degree=2)
    X_poly = poly_features.fit_transform(X)
    poly_model = LinearRegression()
    poly_model.fit(X_poly, y)
    y_pred_poly = poly_model.predict(X_poly)
    r2_poly = r2_score(y, y_pred_poly)
    mse_poly = mean_squared_error(y, y_pred_poly)
    
    models['Quadratic'] = {
        'model': poly_model,
        'poly_features': poly_features,
        'r2': r2_poly,
        'mse': mse_poly,
        'y_pred': y_pred_poly
    }
    
    # 3. Cubic model
    poly_features_cubic = PolynomialFeatures(degree=3)
    X_poly_cubic = poly_features_cubic.fit_transform(X)
    poly_model_cubic = LinearRegression()
    poly_model_cubic.fit(X_poly_cubic, y)
    y_pred_cubic = poly_model_cubic.predict(X_poly_cubic)
    r2_cubic = r2_score(y, y_pred_cubic)
    mse_cubic = mean_squared_error(y, y_pred_cubic)
    
    models['Cubic'] = {
        'model': poly_model_cubic,
        'poly_features': poly_features_cubic,
        'r2': r2_cubic,
        'mse': mse_cubic,
        'y_pred': y_pred_cubic
    }
    
    # 4. Logarithmic model
    X_log = np.log(X)
    log_model = LinearRegression()
    log_model.fit(X_log, y)
    y_pred_log = log_model.predict(X_log)
    r2_log = r2_score(y, y_pred_log)
    mse_log = mean_squared_error(y, y_pred_log)
    
    models['Logarithmic'] = {
        'model': log_model,
        'r2': r2_log,
        'mse': mse_log,
        'y_pred': y_pred_log
    }
    
    # 5. Square root model
    X_sqrt = np.sqrt(X)
    sqrt_model = LinearRegression()
    sqrt_model.fit(X_sqrt, y)
    y_pred_sqrt = sqrt_model.predict(X_sqrt)
    r2_sqrt = r2_score(y, y_pred_sqrt)
    mse_sqrt = mean_squared_error(y, y_pred_sqrt)
    
    models['Square Root'] = {
        'model': sqrt_model,
        'r2': r2_sqrt,
        'mse': mse_sqrt,
        'y_pred': y_pred_sqrt
    }
    
    # Display results
    print(f"\n📊 Model Comparison:")
    print(f"{'Model':<15} {'R²':<8} {'MSE':<8} {'Quality':<15}")
    print("-" * 50)
    
    for name, model_data in models.items():
        r2 = model_data['r2']
        mse = model_data['mse']
        
        if r2 >= 0.8:
            quality = "Excellent"
        elif r2 >= 0.6:
            quality = "Good"
        elif r2 >= 0.4:
            quality = "Fair"
        elif r2 >= 0.2:
            quality = "Poor"
        else:
            quality = "Very Poor"
        
        print(f"{name:<15} {r2:<8.4f} {mse:<8.2f} {quality:<15}")
    
    return models

def analyze_residuals(df, models):
    """Analyze residuals to understand model limitations."""
    print(f"\n🔍 Residual Analysis...")
    
    # Calculate residuals for each model
    residuals_analysis = {}
    
    for name, model_data in models.items():
        y_pred = model_data['y_pred']
        residuals = df['points_clean'] - y_pred
        
        # Calculate residual statistics
        mean_residual = np.mean(residuals)
        std_residual = np.std(residuals)
        max_residual = np.max(np.abs(residuals))
        
        # Check for patterns in residuals
        correlation_residuals = np.corrcoef(df['salary_clean'], residuals)[0, 1]
        
        residuals_analysis[name] = {
            'residuals': residuals,
            'mean': mean_residual,
            'std': std_residual,
            'max': max_residual,
            'correlation': correlation_residuals
        }
        
        print(f"   {name}: Mean={mean_residual:.2f}, Std={std_residual:.2f}, Max={max_residual:.2f}, Corr={correlation_residuals:.3f}")
    
    return residuals_analysis

def identify_outliers_and_influential_points(df):
    """Identify outliers and influential points that might be affecting model quality."""
    print(f"\n🎯 Identifying Outliers and Influential Points...")
    
    # Calculate standardized residuals for linear model
    X = df['salary_clean'].values.reshape(-1, 1)
    y = df['points_clean'].values
    
    linear_model = LinearRegression()
    linear_model.fit(X, y)
    y_pred = linear_model.predict(X)
    residuals = y - y_pred
    
    # Calculate standard error
    mse = np.mean(residuals**2)
    std_error = np.sqrt(mse)
    
    # Standardized residuals
    standardized_residuals = residuals / std_error
    
    # Identify outliers (|standardized residual| > 2)
    outlier_mask = np.abs(standardized_residuals) > 2
    outliers = df[outlier_mask].copy()
    outliers['standardized_residual'] = standardized_residuals[outlier_mask]
    
    print(f"📊 Outlier Analysis:")
    print(f"   Total players: {len(df)}")
    print(f"   Outliers (|std residual| > 2): {len(outliers)}")
    
    if len(outliers) > 0:
        print(f"\n   Outliers:")
        for _, row in outliers.iterrows():
            print(f"     {row['player_name']:<20} | ${row['salary_clean']:>4.0f} | {row['points_clean']:>5.1f} pts | Std Res: {row['standardized_residual']:>5.2f}")
    
    # Calculate leverage (influence)
    # For simple linear regression: h_ii = 1/n + (x_i - x̄)² / Σ(x_j - x̄)²
    n = len(df)
    x_mean = np.mean(X)
    x_centered = X - x_mean
    leverage = 1/n + (x_centered**2) / np.sum(x_centered**2)
    
    # High leverage points (leverage > 2p/n where p=1 for simple regression)
    high_leverage_threshold = 2 * 1 / n
    high_leverage_mask = leverage.flatten() > high_leverage_threshold
    high_leverage = df[high_leverage_mask].copy()
    high_leverage['leverage'] = leverage[high_leverage_mask]
    
    print(f"\n   High Leverage Points (leverage > {high_leverage_threshold:.3f}): {len(high_leverage)}")
    if len(high_leverage) > 0:
        for _, row in high_leverage.iterrows():
            print(f"     {row['player_name']:<20} | ${row['salary_clean']:>4.0f} | {row['points_clean']:>5.1f} pts | Leverage: {row['leverage']:>5.3f}")
    
    return outliers, high_leverage

def analyze_data_limitations(df):
    """Analyze limitations of the dataset that might explain low R²."""
    print(f"\n📊 Data Limitations Analysis...")
    
    # Sample size
    print(f"   Sample size: {len(df)} players")
    if len(df) < 30:
        print(f"   ⚠️ Small sample size may limit model reliability")
    
    # Salary range
    salary_range = df['salary_clean'].max() - df['salary_clean'].min()
    print(f"   Salary range: ${salary_range:.0f} (${df['salary_clean'].min():.0f} - ${df['salary_clean'].max():.0f})")
    
    # Points range
    points_range = df['points_clean'].max() - df['points_clean'].min()
    print(f"   Points range: {points_range:.1f} ({df['points_clean'].min():.1f} - {df['points_clean'].max():.1f})")
    
    # Coefficient of variation
    cv_salary = df['salary_clean'].std() / df['salary_clean'].mean()
    cv_points = df['points_clean'].std() / df['points_clean'].mean()
    print(f"   Coefficient of variation - Salary: {cv_salary:.3f}, Points: {cv_points:.3f}")
    
    # Check for non-linear patterns
    correlation = df['salary_clean'].corr(df['points_clean'])
    print(f"   Linear correlation: {correlation:.3f}")
    
    # Check if there are clear clusters or groups
    print(f"\n   Position breakdown:")
    position_stats = df.groupby('position').agg({
        'salary_clean': ['count', 'mean', 'std'],
        'points_clean': ['mean', 'std']
    }).round(2)
    print(position_stats)
    
    # Check for heteroscedasticity (unequal variance)
    # Group by salary ranges and check variance
    df['salary_bin'] = pd.cut(df['salary_clean'], bins=3, labels=['Low', 'Mid', 'High'])
    variance_by_bin = df.groupby('salary_bin')['points_clean'].var()
    print(f"\n   Variance by salary bin:")
    for bin_name, variance in variance_by_bin.items():
        print(f"     {bin_name}: {variance:.2f}")
    
    # Check if variance is roughly equal (homoscedasticity)
    max_var = variance_by_bin.max()
    min_var = variance_by_bin.min()
    if max_var / min_var > 4:  # Rule of thumb: ratio > 4 indicates heteroscedasticity
        print(f"   ⚠️ Heteroscedasticity detected (variance ratio: {max_var/min_var:.1f})")
    else:
        print(f"   ✅ Homoscedasticity (variance ratio: {max_var/min_var:.1f})")

def create_model_quality_visualization(df, models, outliers, high_leverage):
    """Create visualization showing model quality and limitations."""
    print(f"\n📊 Creating Model Quality Visualization...")
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('Week 2 Thursday: Model Quality Analysis', fontsize=16, fontweight='bold')
    
    # 1. All models comparison
    ax1 = axes[0, 0]
    ax1.scatter(df['salary_clean'], df['points_clean'], alpha=0.7, s=60, color='steelblue', edgecolors='black', linewidth=0.5, label='Data')
    
    # Plot all model fits
    X_smooth = np.linspace(df['salary_clean'].min(), df['salary_clean'].max(), 100)
    colors = ['red', 'green', 'orange', 'purple', 'brown']
    
    for i, (name, model_data) in enumerate(models.items()):
        if name == 'Linear':
            y_smooth = model_data['model'].predict(X_smooth.reshape(-1, 1))
        elif name in ['Quadratic', 'Cubic']:
            X_smooth_poly = model_data['poly_features'].transform(X_smooth.reshape(-1, 1))
            y_smooth = model_data['model'].predict(X_smooth_poly)
        elif name == 'Logarithmic':
            y_smooth = model_data['model'].predict(np.log(X_smooth.reshape(-1, 1)))
        elif name == 'Square Root':
            y_smooth = model_data['model'].predict(np.sqrt(X_smooth.reshape(-1, 1)))
        
        ax1.plot(X_smooth, y_smooth, color=colors[i], linewidth=2, alpha=0.8, label=f'{name} (R²={model_data["r2"]:.3f})')
    
    ax1.set_xlabel('Salary ($)')
    ax1.set_ylabel('Points')
    ax1.set_title('Model Comparison')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. R² comparison
    ax2 = axes[0, 1]
    model_names = list(models.keys())
    r2_values = [models[name]['r2'] for name in model_names]
    colors_bar = ['red' if r2 < 0.4 else 'orange' if r2 < 0.6 else 'green' for r2 in r2_values]
    
    bars = ax2.bar(model_names, r2_values, color=colors_bar, alpha=0.7, edgecolor='black')
    ax2.axhline(y=0.8, color='green', linestyle='--', alpha=0.7, label='Good Model (R²=0.8)')
    ax2.axhline(y=0.6, color='orange', linestyle='--', alpha=0.7, label='Fair Model (R²=0.6)')
    ax2.axhline(y=0.4, color='red', linestyle='--', alpha=0.7, label='Poor Model (R²=0.4)')
    ax2.set_ylabel('R²')
    ax2.set_title('Model Quality (R²)')
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for bar, r2 in zip(bars, r2_values):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f'{r2:.3f}', ha='center', va='bottom', fontweight='bold')
    
    # 3. Residuals plot
    ax3 = axes[0, 2]
    best_model_name = max(models.keys(), key=lambda x: models[x]['r2'])
    best_model = models[best_model_name]
    residuals = df['points_clean'] - best_model['y_pred']
    
    ax3.scatter(df['salary_clean'], residuals, alpha=0.7, s=60, color='purple', edgecolors='black', linewidth=0.5)
    ax3.axhline(y=0, color='red', linestyle='-', alpha=0.7)
    ax3.set_xlabel('Salary ($)')
    ax3.set_ylabel('Residuals')
    ax3.set_title(f'Residuals Plot ({best_model_name})')
    ax3.grid(True, alpha=0.3)
    
    # 4. Outliers and influential points
    ax4 = axes[1, 0]
    ax4.scatter(df['salary_clean'], df['points_clean'], alpha=0.7, s=60, color='lightblue', edgecolors='black', linewidth=0.5, label='Normal Points')
    
    if len(outliers) > 0:
        ax4.scatter(outliers['salary_clean'], outliers['points_clean'], s=100, color='red', edgecolors='darkred', linewidth=2, label=f'Outliers (n={len(outliers)})')
    
    if len(high_leverage) > 0:
        ax4.scatter(high_leverage['salary_clean'], high_leverage['points_clean'], s=100, color='orange', edgecolors='darkorange', linewidth=2, label=f'High Leverage (n={len(high_leverage)})')
    
    ax4.set_xlabel('Salary ($)')
    ax4.set_ylabel('Points')
    ax4.set_title('Outliers and Influential Points')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    # 5. Position analysis
    ax5 = axes[1, 1]
    position_stats = df.groupby('position').agg({
        'salary_clean': 'mean',
        'points_clean': 'mean'
    })
    
    scatter = ax5.scatter(position_stats['salary_clean'], position_stats['points_clean'], 
                         s=100, alpha=0.7, edgecolors='black', linewidth=1)
    
    for pos, row in position_stats.iterrows():
        ax5.annotate(pos, (row['salary_clean'], row['points_clean']), 
                    xytext=(5, 5), textcoords='offset points', fontweight='bold')
    
    ax5.set_xlabel('Mean Salary ($)')
    ax5.set_ylabel('Mean Points')
    ax5.set_title('Position Analysis')
    ax5.grid(True, alpha=0.3)
    
    # 6. Model quality summary
    ax6 = axes[1, 2]
    ax6.axis('off')
    
    # Create text summary
    summary_text = f"""
    Model Quality Summary:
    
    Best Model: {best_model_name}
    R² = {best_model['r2']:.3f}
    
    Quality Assessment:
    • R² < 0.4: Poor
    • R² 0.4-0.6: Fair  
    • R² 0.6-0.8: Good
    • R² > 0.8: Excellent
    
    Current Status: {'Poor' if best_model['r2'] < 0.4 else 'Fair' if best_model['r2'] < 0.6 else 'Good' if best_model['r2'] < 0.8 else 'Excellent'}
    
    Limitations:
    • Small sample size (n={len(df)})
    • High variability in points
    • Possible non-linear relationships
    • Position-specific patterns
    """
    
    ax6.text(0.1, 0.9, summary_text, transform=ax6.transAxes, fontsize=10, 
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
    
    plt.tight_layout()
    
    # Save the plot
    output_path = '/Users/mightenyip/Documents/GitHub/yfd-py-test/plots_images/week2_thursday_model_quality_analysis.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"📊 Model quality analysis plot saved to: {output_path}")
    
    plt.show()

def main():
    """Main analysis function."""
    print("Week 2 Thursday: Critical R² Analysis")
    print("=" * 50)
    
    # Load data
    df = load_and_clean_data()
    
    # Analyze model quality
    models = analyze_model_quality(df)
    
    # Analyze residuals
    residuals_analysis = analyze_residuals(df, models)
    
    # Identify outliers and influential points
    outliers, high_leverage = identify_outliers_and_influential_points(df)
    
    # Analyze data limitations
    analyze_data_limitations(df)
    
    # Create visualization
    create_model_quality_visualization(df, models, outliers, high_leverage)
    
    print(f"\n🎯 CRITICAL ASSESSMENT:")
    print("=" * 30)
    
    best_model_name = max(models.keys(), key=lambda x: models[x]['r2'])
    best_r2 = models[best_model_name]['r2']
    
    print(f"Best model: {best_model_name}")
    print(f"Best R²: {best_r2:.3f}")
    
    if best_r2 < 0.4:
        print("❌ POOR MODEL QUALITY - R² < 0.4")
        print("   The relationship is weak and not very predictive")
    elif best_r2 < 0.6:
        print("⚠️ FAIR MODEL QUALITY - R² 0.4-0.6")
        print("   The relationship is moderate but not strong")
    elif best_r2 < 0.8:
        print("✅ GOOD MODEL QUALITY - R² 0.6-0.8")
        print("   The relationship is reasonably strong")
    else:
        print("🎉 EXCELLENT MODEL QUALITY - R² > 0.8")
        print("   The relationship is very strong and predictive")
    
    print(f"\n💡 RECOMMENDATION:")
    if best_r2 < 0.6:
        print("   The current models are not very reliable for prediction.")
        print("   Consider:")
        print("   • Collecting more data")
        print("   • Including additional variables (position, team, etc.)")
        print("   • Using more sophisticated models")
        print("   • Acknowledging that salary alone may not be a strong predictor")
    else:
        print("   The model provides reasonable insights for the available data.")

if __name__ == "__main__":
    main()

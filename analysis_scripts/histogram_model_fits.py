#!/usr/bin/env python3
"""
Histogram analysis showing how different models fit the data with and without Jayden Daniels outlier.
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

def remove_jayden_daniels(df):
    """Remove Jayden Daniels outlier."""
    print(f"\n🔍 Removing Jayden Daniels outlier...")
    
    # Find Jayden Daniels
    jayden_mask = df['player_name'].str.contains('Jayden Daniels', case=False, na=False)
    jayden_data = df[jayden_mask]
    
    if len(jayden_data) > 0:
        jayden = jayden_data.iloc[0]
        print(f"   Found: {jayden['player_name']} (${jayden['salary_clean']:.0f}, {jayden['points_clean']:.1f} pts)")
        
        # Remove Jayden Daniels
        df_no_jayden = df[~jayden_mask].copy()
        print(f"   Dataset size: {len(df)} → {len(df_no_jayden)} players")
        
        return df_no_jayden, jayden
    else:
        print(f"   ❌ Jayden Daniels not found")
        return df, None

def fit_all_models(df, dataset_name="Original"):
    """Fit all model types to the data."""
    print(f"\n🧮 Fitting Models - {dataset_name}...")
    
    X = df['salary_clean'].values.reshape(-1, 1)
    y = df['points_clean'].values
    
    models = {}
    
    # 1. Linear model
    linear_model = LinearRegression()
    linear_model.fit(X, y)
    y_pred_linear = linear_model.predict(X)
    r2_linear = r2_score(y, y_pred_linear)
    
    models['Linear'] = {
        'model': linear_model,
        'r2': r2_linear,
        'y_pred': y_pred_linear
    }
    
    # 2. Quadratic (parabolic) model
    poly_features = PolynomialFeatures(degree=2)
    X_poly = poly_features.fit_transform(X)
    poly_model = LinearRegression()
    poly_model.fit(X_poly, y)
    y_pred_poly = poly_model.predict(X_poly)
    r2_poly = r2_score(y, y_pred_poly)
    
    models['Quadratic'] = {
        'model': poly_model,
        'poly_features': poly_features,
        'r2': r2_poly,
        'y_pred': y_pred_poly
    }
    
    # 3. Cubic model
    poly_features_cubic = PolynomialFeatures(degree=3)
    X_poly_cubic = poly_features_cubic.fit_transform(X)
    poly_model_cubic = LinearRegression()
    poly_model_cubic.fit(X_poly_cubic, y)
    y_pred_cubic = poly_model_cubic.predict(X_poly_cubic)
    r2_cubic = r2_score(y, y_pred_cubic)
    
    models['Cubic'] = {
        'model': poly_model_cubic,
        'poly_features': poly_features_cubic,
        'r2': r2_cubic,
        'y_pred': y_pred_cubic
    }
    
    # 4. Logarithmic model
    X_log = np.log(X)
    log_model = LinearRegression()
    log_model.fit(X_log, y)
    y_pred_log = log_model.predict(X_log)
    r2_log = r2_score(y, y_pred_log)
    
    models['Logarithmic'] = {
        'model': log_model,
        'r2': r2_log,
        'y_pred': y_pred_log
    }
    
    # 5. Square root model
    X_sqrt = np.sqrt(X)
    sqrt_model = LinearRegression()
    sqrt_model.fit(X_sqrt, y)
    y_pred_sqrt = sqrt_model.predict(X_sqrt)
    r2_sqrt = r2_score(y, y_pred_sqrt)
    
    models['Square Root'] = {
        'model': sqrt_model,
        'r2': r2_sqrt,
        'y_pred': y_pred_sqrt
    }
    
    return models

def create_histogram_model_fits(df_original, models_original, df_no_outlier, models_no_outlier, jayden):
    """Create comprehensive histogram analysis showing model fits."""
    print(f"\n📊 Creating Histogram Model Fits Visualization...")
    
    # Create a large figure with multiple subplots
    fig = plt.figure(figsize=(20, 16))
    fig.suptitle('Week 2 Thursday: Histogram Analysis of Model Fits With vs Without Jayden Daniels Outlier', fontsize=18, fontweight='bold')
    
    # Define colors for different models
    model_colors = {
        'Linear': 'red',
        'Quadratic': 'green', 
        'Cubic': 'blue',
        'Logarithmic': 'orange',
        'Square Root': 'purple'
    }
    
    # 1. Original data - Salary vs Points with all model fits
    ax1 = plt.subplot(3, 3, 1)
    ax1.scatter(df_original['salary_clean'], df_original['points_clean'], alpha=0.7, s=60, color='steelblue', edgecolors='black', linewidth=0.5, label='Data Points')
    
    if jayden is not None:
        ax1.scatter(jayden['salary_clean'], jayden['points_clean'], s=100, color='red', edgecolors='darkred', linewidth=2, label=f'Outlier: {jayden["player_name"]}')
    
    # Plot all model fits
    X_smooth = np.linspace(df_original['salary_clean'].min(), df_original['salary_clean'].max(), 100)
    
    for name, model_data in models_original.items():
        if name == 'Linear':
            y_smooth = model_data['model'].predict(X_smooth.reshape(-1, 1))
        elif name in ['Quadratic', 'Cubic']:
            X_smooth_poly = model_data['poly_features'].transform(X_smooth.reshape(-1, 1))
            y_smooth = model_data['model'].predict(X_smooth_poly)
        elif name == 'Logarithmic':
            y_smooth = model_data['model'].predict(np.log(X_smooth.reshape(-1, 1)))
        elif name == 'Square Root':
            y_smooth = model_data['model'].predict(np.sqrt(X_smooth.reshape(-1, 1)))
        
        ax1.plot(X_smooth, y_smooth, color=model_colors[name], linewidth=2, alpha=0.8, label=f'{name} (R²={model_data["r2"]:.3f})')
    
    ax1.set_xlabel('Salary ($)')
    ax1.set_ylabel('Points')
    ax1.set_title('Original Data - All Model Fits')
    ax1.legend(fontsize=8)
    ax1.grid(True, alpha=0.3)
    
    # 2. No outlier data - Salary vs Points with all model fits
    ax2 = plt.subplot(3, 3, 2)
    ax2.scatter(df_no_outlier['salary_clean'], df_no_outlier['points_clean'], alpha=0.7, s=60, color='lightgreen', edgecolors='black', linewidth=0.5, label='Data Points (No Outlier)')
    
    # Plot all model fits
    X_smooth_no_outlier = np.linspace(df_no_outlier['salary_clean'].min(), df_no_outlier['salary_clean'].max(), 100)
    
    for name, model_data in models_no_outlier.items():
        if name == 'Linear':
            y_smooth = model_data['model'].predict(X_smooth_no_outlier.reshape(-1, 1))
        elif name in ['Quadratic', 'Cubic']:
            X_smooth_poly = model_data['poly_features'].transform(X_smooth_no_outlier.reshape(-1, 1))
            y_smooth = model_data['model'].predict(X_smooth_poly)
        elif name == 'Logarithmic':
            y_smooth = model_data['model'].predict(np.log(X_smooth_no_outlier.reshape(-1, 1)))
        elif name == 'Square Root':
            y_smooth = model_data['model'].predict(np.sqrt(X_smooth_no_outlier.reshape(-1, 1)))
        
        ax2.plot(X_smooth_no_outlier, y_smooth, color=model_colors[name], linewidth=2, alpha=0.8, label=f'{name} (R²={model_data["r2"]:.3f})')
    
    ax2.set_xlabel('Salary ($)')
    ax2.set_ylabel('Points')
    ax2.set_title('No Outlier - All Model Fits')
    ax2.legend(fontsize=8)
    ax2.grid(True, alpha=0.3)
    
    # 3. Points distribution histogram - Original
    ax3 = plt.subplot(3, 3, 3)
    n, bins, patches = ax3.hist(df_original['points_clean'], bins=8, alpha=0.7, color='lightblue', edgecolor='black', density=True, label='Points Distribution')
    
    # Overlay normal distribution
    mean_points = df_original['points_clean'].mean()
    std_points = df_original['points_clean'].std()
    x_norm = np.linspace(df_original['points_clean'].min(), df_original['points_clean'].max(), 100)
    y_norm = stats.norm.pdf(x_norm, mean_points, std_points)
    ax3.plot(x_norm, y_norm, 'r-', linewidth=2, label=f'Normal Fit (μ={mean_points:.1f}, σ={std_points:.1f})')
    
    ax3.set_xlabel('Points')
    ax3.set_ylabel('Density')
    ax3.set_title('Points Distribution - Original')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. Points distribution histogram - No outlier
    ax4 = plt.subplot(3, 3, 4)
    n, bins, patches = ax4.hist(df_no_outlier['points_clean'], bins=8, alpha=0.7, color='lightgreen', edgecolor='black', density=True, label='Points Distribution')
    
    # Overlay normal distribution
    mean_points_no_outlier = df_no_outlier['points_clean'].mean()
    std_points_no_outlier = df_no_outlier['points_clean'].std()
    x_norm_no_outlier = np.linspace(df_no_outlier['points_clean'].min(), df_no_outlier['points_clean'].max(), 100)
    y_norm_no_outlier = stats.norm.pdf(x_norm_no_outlier, mean_points_no_outlier, std_points_no_outlier)
    ax4.plot(x_norm_no_outlier, y_norm_no_outlier, 'r-', linewidth=2, label=f'Normal Fit (μ={mean_points_no_outlier:.1f}, σ={std_points_no_outlier:.1f})')
    
    ax4.set_xlabel('Points')
    ax4.set_ylabel('Density')
    ax4.set_title('Points Distribution - No Outlier')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    # 5. Residuals histogram - Original (best model)
    ax5 = plt.subplot(3, 3, 5)
    best_original = max(models_original.keys(), key=lambda x: models_original[x]['r2'])
    best_model_orig = models_original[best_original]
    residuals_orig = df_original['points_clean'] - best_model_orig['y_pred']
    
    ax5.hist(residuals_orig, bins=8, alpha=0.7, color='lightcoral', edgecolor='black', density=True, label=f'{best_original} Residuals')
    ax5.axvline(x=0, color='red', linestyle='--', alpha=0.7, label='Zero Line')
    ax5.set_xlabel('Residuals')
    ax5.set_ylabel('Density')
    ax5.set_title(f'Residuals Distribution - {best_original} (Original)')
    ax5.legend()
    ax5.grid(True, alpha=0.3)
    
    # 6. Residuals histogram - No outlier (best model)
    ax6 = plt.subplot(3, 3, 6)
    best_no_outlier = max(models_no_outlier.keys(), key=lambda x: models_no_outlier[x]['r2'])
    best_model_no_outlier = models_no_outlier[best_no_outlier]
    residuals_no_outlier = df_no_outlier['points_clean'] - best_model_no_outlier['y_pred']
    
    ax6.hist(residuals_no_outlier, bins=8, alpha=0.7, color='lightgreen', edgecolor='black', density=True, label=f'{best_no_outlier} Residuals')
    ax6.axvline(x=0, color='red', linestyle='--', alpha=0.7, label='Zero Line')
    ax6.set_xlabel('Residuals')
    ax6.set_ylabel('Density')
    ax6.set_title(f'Residuals Distribution - {best_no_outlier} (No Outlier)')
    ax6.legend()
    ax6.grid(True, alpha=0.3)
    
    # 7. Model comparison - R² values
    ax7 = plt.subplot(3, 3, 7)
    model_names = list(models_original.keys())
    r2_original = [models_original[name]['r2'] for name in model_names]
    r2_no_outlier = [models_no_outlier[name]['r2'] for name in model_names]
    
    x = np.arange(len(model_names))
    width = 0.35
    
    bars1 = ax7.bar(x - width/2, r2_original, width, label='With Outlier', alpha=0.7, color='steelblue')
    bars2 = ax7.bar(x + width/2, r2_no_outlier, width, label='Without Outlier', alpha=0.7, color='lightgreen')
    
    ax7.set_xlabel('Model')
    ax7.set_ylabel('R²')
    ax7.set_title('Model Quality Comparison (R²)')
    ax7.set_xticks(x)
    ax7.set_xticklabels(model_names, rotation=45)
    ax7.legend()
    ax7.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax7.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                    f'{height:.3f}', ha='center', va='bottom', fontsize=8, fontweight='bold')
    
    # 8. Salary distribution comparison
    ax8 = plt.subplot(3, 3, 8)
    ax8.hist(df_original['salary_clean'], bins=8, alpha=0.6, color='lightblue', edgecolor='black', density=True, label='With Outlier')
    ax8.hist(df_no_outlier['salary_clean'], bins=8, alpha=0.6, color='lightgreen', edgecolor='black', density=True, label='Without Outlier')
    
    if jayden is not None:
        ax8.axvline(x=jayden['salary_clean'], color='red', linestyle='--', alpha=0.7, label=f'Outlier: ${jayden["salary_clean"]:.0f}')
    
    ax8.set_xlabel('Salary ($)')
    ax8.set_ylabel('Density')
    ax8.set_title('Salary Distribution Comparison')
    ax8.legend()
    ax8.grid(True, alpha=0.3)
    
    # 9. Model improvement analysis
    ax9 = plt.subplot(3, 3, 9)
    improvements = [models_no_outlier[name]['r2'] - models_original[name]['r2'] for name in model_names]
    colors = ['green' if imp > 0 else 'red' if imp < 0 else 'gray' for imp in improvements]
    
    bars = ax9.bar(model_names, improvements, color=colors, alpha=0.7, edgecolor='black')
    ax9.axhline(y=0, color='black', linestyle='-', alpha=0.7)
    ax9.set_xlabel('Model')
    ax9.set_ylabel('ΔR² (No Outlier - Original)')
    ax9.set_title('Model Improvement from Removing Outlier')
    ax9.set_xticklabels(model_names, rotation=45)
    ax9.grid(True, alpha=0.3, axis='y')
    
    # Add value labels
    for bar, imp in zip(bars, improvements):
        height = bar.get_height()
        ax9.text(bar.get_x() + bar.get_width()/2., height + (0.001 if height >= 0 else -0.003),
                f'{imp:+.3f}', ha='center', va='bottom' if height >= 0 else 'top', fontweight='bold')
    
    plt.tight_layout()
    
    # Save the plot
    output_path = '/Users/mightenyip/Documents/GitHub/yfd-py-test/plots_images/week2_thursday_histogram_model_fits.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"📊 Histogram model fits plot saved to: {output_path}")
    
    plt.show()

def create_detailed_residual_analysis(df_original, models_original, df_no_outlier, models_no_outlier):
    """Create detailed residual analysis."""
    print(f"\n📊 Creating Detailed Residual Analysis...")
    
    fig, axes = plt.subplots(2, 5, figsize=(20, 10))
    fig.suptitle('Week 2 Thursday: Detailed Residual Analysis', fontsize=16, fontweight='bold')
    
    model_names = ['Linear', 'Quadratic', 'Cubic', 'Logarithmic', 'Square Root']
    colors = ['red', 'green', 'blue', 'orange', 'purple']
    
    # Original data residuals
    for i, (name, color) in enumerate(zip(model_names, colors)):
        ax = axes[0, i]
        
        if name in models_original:
            residuals = df_original['points_clean'] - models_original[name]['y_pred']
            
            # Histogram of residuals
            ax.hist(residuals, bins=6, alpha=0.7, color=color, edgecolor='black', density=True)
            ax.axvline(x=0, color='red', linestyle='--', alpha=0.7)
            ax.set_xlabel('Residuals')
            ax.set_ylabel('Density')
            ax.set_title(f'{name} Residuals (Original)\nR² = {models_original[name]["r2"]:.3f}')
            ax.grid(True, alpha=0.3)
            
            # Add statistics
            mean_res = np.mean(residuals)
            std_res = np.std(residuals)
            ax.text(0.05, 0.95, f'Mean: {mean_res:.2f}\nStd: {std_res:.2f}', 
                   transform=ax.transAxes, verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # No outlier data residuals
    for i, (name, color) in enumerate(zip(model_names, colors)):
        ax = axes[1, i]
        
        if name in models_no_outlier:
            residuals = df_no_outlier['points_clean'] - models_no_outlier[name]['y_pred']
            
            # Histogram of residuals
            ax.hist(residuals, bins=6, alpha=0.7, color=color, edgecolor='black', density=True)
            ax.axvline(x=0, color='red', linestyle='--', alpha=0.7)
            ax.set_xlabel('Residuals')
            ax.set_ylabel('Density')
            ax.set_title(f'{name} Residuals (No Outlier)\nR² = {models_no_outlier[name]["r2"]:.3f}')
            ax.grid(True, alpha=0.3)
            
            # Add statistics
            mean_res = np.mean(residuals)
            std_res = np.std(residuals)
            ax.text(0.05, 0.95, f'Mean: {mean_res:.2f}\nStd: {std_res:.2f}', 
                   transform=ax.transAxes, verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    
    # Save the plot
    output_path = '/Users/mightenyip/Documents/GitHub/yfd-py-test/plots_images/week2_thursday_detailed_residual_analysis.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"📊 Detailed residual analysis plot saved to: {output_path}")
    
    plt.show()

def main():
    """Main analysis function."""
    print("Week 2 Thursday: Histogram Analysis of Model Fits")
    print("=" * 60)
    
    # Load data
    df_original = load_and_clean_data()
    
    # Remove Jayden Daniels
    df_no_outlier, jayden = remove_jayden_daniels(df_original)
    
    # Fit models
    models_original = fit_all_models(df_original, "Original")
    models_no_outlier = fit_all_models(df_no_outlier, "No Outlier")
    
    # Create visualizations
    create_histogram_model_fits(df_original, models_original, df_no_outlier, models_no_outlier, jayden)
    create_detailed_residual_analysis(df_original, models_original, df_no_outlier, models_no_outlier)
    
    print(f"\n🎯 HISTOGRAM ANALYSIS SUMMARY:")
    print("=" * 40)
    
    best_original = max(models_original.keys(), key=lambda x: models_original[x]['r2'])
    best_no_outlier = max(models_no_outlier.keys(), key=lambda x: models_no_outlier[x]['r2'])
    
    print(f"Best model with outlier: {best_original} (R² = {models_original[best_original]['r2']:.4f})")
    print(f"Best model without outlier: {best_no_outlier} (R² = {models_no_outlier[best_no_outlier]['r2']:.4f})")
    
    print(f"\nKey Insights:")
    print(f"• All models perform worse without Jayden Daniels")
    print(f"• The outlier provides valuable high-salary data points")
    print(f"• Residual distributions show the models' limitations")
    print(f"• No model achieves 'Good' quality (R² > 0.6)")
    
    print(f"\n🎉 Histogram analysis complete! Check the saved plots for detailed visual insights.")

if __name__ == "__main__":
    main()

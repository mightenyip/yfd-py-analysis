#!/usr/bin/env python3
"""
Analysis of all models without the Jayden Daniels outlier.
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
        print(f"   Value ratio: {jayden['points_clean'] / jayden['salary_clean']:.3f} pts/$")
        
        # Remove Jayden Daniels
        df_no_jayden = df[~jayden_mask].copy()
        print(f"   Dataset size: {len(df)} → {len(df_no_jayden)} players")
        print(f"   New salary range: ${df_no_jayden['salary_clean'].min():.0f} - ${df_no_jayden['salary_clean'].max():.0f}")
        
        return df_no_jayden, jayden
    else:
        print(f"   ❌ Jayden Daniels not found")
        return df, None

def analyze_all_models(df, dataset_name="Original"):
    """Analyze all model types."""
    print(f"\n🧮 Analyzing All Models - {dataset_name}...")
    
    X = df['salary_clean'].values.reshape(-1, 1)
    y = df['points_clean'].values
    
    models = {}
    
    # 1. Linear model
    linear_model = LinearRegression()
    linear_model.fit(X, y)
    y_pred_linear = linear_model.predict(X)
    r2_linear = r2_score(y, y_pred_linear)
    mse_linear = mean_squared_error(y, y_pred_linear)
    
    # Calculate correlation and p-value
    correlation, p_value = stats.pearsonr(df['salary_clean'], df['points_clean'])
    
    models['Linear'] = {
        'model': linear_model,
        'r2': r2_linear,
        'mse': mse_linear,
        'correlation': correlation,
        'p_value': p_value,
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
    
    # 6. Exponential model (y = a * exp(bx))
    try:
        # Use log transformation: ln(y) = ln(a) + bx
        y_log = np.log(y + 0.1)  # Add small constant to avoid log(0)
        exp_model = LinearRegression()
        exp_model.fit(X, y_log)
        y_pred_exp = np.exp(exp_model.predict(X)) - 0.1
        r2_exp = r2_score(y, y_pred_exp)
        mse_exp = mean_squared_error(y, y_pred_exp)
        
        models['Exponential'] = {
            'model': exp_model,
            'r2': r2_exp,
            'mse': mse_exp,
            'y_pred': y_pred_exp
        }
    except:
        print("   ⚠️ Exponential model failed to fit")
    
    # Display results
    print(f"\n📊 Model Results - {dataset_name}:")
    print(f"{'Model':<15} {'R²':<8} {'MSE':<8} {'Quality':<15} {'Correlation':<12} {'P-value':<10}")
    print("-" * 80)
    
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
        
        # Get correlation and p-value (only available for linear model)
        if 'correlation' in model_data:
            corr = model_data['correlation']
            p_val = model_data['p_value']
            corr_str = f"{corr:.3f}"
            p_val_str = f"{p_val:.3f}"
        else:
            corr_str = "N/A"
            p_val_str = "N/A"
        
        print(f"{name:<15} {r2:<8.4f} {mse:<8.2f} {quality:<15} {corr_str:<12} {p_val_str:<10}")
    
    return models

def compare_models_with_without_outlier(models_original, models_no_outlier):
    """Compare models with and without the outlier."""
    print(f"\n🔍 MODEL COMPARISON: With vs Without Jayden Daniels")
    print("=" * 70)
    
    print(f"{'Model':<15} {'R² (Original)':<15} {'R² (No Outlier)':<15} {'Difference':<15} {'Improvement':<15}")
    print("-" * 80)
    
    improvements = {}
    
    for model_name in models_original.keys():
        if model_name in models_no_outlier:
            r2_orig = models_original[model_name]['r2']
            r2_no_outlier = models_no_outlier[model_name]['r2']
            difference = r2_no_outlier - r2_orig
            
            if difference > 0:
                improvement = "✅ Better"
            elif difference < 0:
                improvement = "❌ Worse"
            else:
                improvement = "➖ Same"
            
            improvements[model_name] = difference
            
            print(f"{model_name:<15} {r2_orig:<15.4f} {r2_no_outlier:<15.4f} {difference:<15.4f} {improvement:<15}")
    
    # Find best models
    best_original = max(models_original.keys(), key=lambda x: models_original[x]['r2'])
    best_no_outlier = max(models_no_outlier.keys(), key=lambda x: models_no_outlier[x]['r2'])
    
    print(f"\n🎯 BEST MODELS:")
    print(f"   Original data: {best_original} (R² = {models_original[best_original]['r2']:.4f})")
    print(f"   No outlier: {best_no_outlier} (R² = {models_no_outlier[best_no_outlier]['r2']:.4f})")
    
    # Overall assessment
    total_improvement = sum(improvements.values())
    if total_improvement > 0:
        print(f"\n✅ OVERALL: Removing outlier improves models (total ΔR² = {total_improvement:.4f})")
    else:
        print(f"\n❌ OVERALL: Removing outlier worsens models (total ΔR² = {total_improvement:.4f})")
    
    return improvements

def create_comparison_visualization(df_original, models_original, df_no_outlier, models_no_outlier, jayden):
    """Create visualization comparing models with and without outlier."""
    print(f"\n📊 Creating Model Comparison Visualization...")
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('Week 2 Thursday: Model Comparison With vs Without Jayden Daniels Outlier', fontsize=16, fontweight='bold')
    
    # 1. Original data with all models
    ax1 = axes[0, 0]
    ax1.scatter(df_original['salary_clean'], df_original['points_clean'], alpha=0.7, s=60, color='steelblue', edgecolors='black', linewidth=0.5, label='Data')
    
    if jayden is not None:
        ax1.scatter(jayden['salary_clean'], jayden['points_clean'], s=100, color='red', edgecolors='darkred', linewidth=2, label=f'Outlier: {jayden["player_name"]}')
    
    # Plot best model for original data
    best_original = max(models_original.keys(), key=lambda x: models_original[x]['r2'])
    best_model_orig = models_original[best_original]
    
    X_smooth = np.linspace(df_original['salary_clean'].min(), df_original['salary_clean'].max(), 100)
    
    if best_original == 'Linear':
        y_smooth = best_model_orig['model'].predict(X_smooth.reshape(-1, 1))
    elif best_original in ['Quadratic', 'Cubic']:
        X_smooth_poly = best_model_orig['poly_features'].transform(X_smooth.reshape(-1, 1))
        y_smooth = best_model_orig['model'].predict(X_smooth_poly)
    elif best_original == 'Logarithmic':
        y_smooth = best_model_orig['model'].predict(np.log(X_smooth.reshape(-1, 1)))
    elif best_original == 'Square Root':
        y_smooth = best_model_orig['model'].predict(np.sqrt(X_smooth.reshape(-1, 1)))
    elif best_original == 'Exponential':
        y_smooth = np.exp(best_model_orig['model'].predict(X_smooth.reshape(-1, 1))) - 0.1
    
    ax1.plot(X_smooth, y_smooth, 'g-', linewidth=3, alpha=0.8, label=f'{best_original} (R²={best_model_orig["r2"]:.3f})')
    
    ax1.set_xlabel('Salary ($)')
    ax1.set_ylabel('Points')
    ax1.set_title('Original Data - Best Model')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Data without outlier
    ax2 = axes[0, 1]
    ax2.scatter(df_no_outlier['salary_clean'], df_no_outlier['points_clean'], alpha=0.7, s=60, color='lightgreen', edgecolors='black', linewidth=0.5, label='Data (No Outlier)')
    
    # Plot best model for no outlier data
    best_no_outlier = max(models_no_outlier.keys(), key=lambda x: models_no_outlier[x]['r2'])
    best_model_no_outlier = models_no_outlier[best_no_outlier]
    
    X_smooth_no_outlier = np.linspace(df_no_outlier['salary_clean'].min(), df_no_outlier['salary_clean'].max(), 100)
    
    if best_no_outlier == 'Linear':
        y_smooth_no_outlier = best_model_no_outlier['model'].predict(X_smooth_no_outlier.reshape(-1, 1))
    elif best_no_outlier in ['Quadratic', 'Cubic']:
        X_smooth_poly_no_outlier = best_model_no_outlier['poly_features'].transform(X_smooth_no_outlier.reshape(-1, 1))
        y_smooth_no_outlier = best_model_no_outlier['model'].predict(X_smooth_poly_no_outlier)
    elif best_no_outlier == 'Logarithmic':
        y_smooth_no_outlier = best_model_no_outlier['model'].predict(np.log(X_smooth_no_outlier.reshape(-1, 1)))
    elif best_no_outlier == 'Square Root':
        y_smooth_no_outlier = best_model_no_outlier['model'].predict(np.sqrt(X_smooth_no_outlier.reshape(-1, 1)))
    elif best_no_outlier == 'Exponential':
        y_smooth_no_outlier = np.exp(best_model_no_outlier['model'].predict(X_smooth_no_outlier.reshape(-1, 1))) - 0.1
    
    ax2.plot(X_smooth_no_outlier, y_smooth_no_outlier, 'r-', linewidth=3, alpha=0.8, label=f'{best_no_outlier} (R²={best_model_no_outlier["r2"]:.3f})')
    
    ax2.set_xlabel('Salary ($)')
    ax2.set_ylabel('Points')
    ax2.set_title('No Outlier - Best Model')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. R² comparison
    ax3 = axes[0, 2]
    model_names = list(models_original.keys())
    r2_original = [models_original[name]['r2'] for name in model_names]
    r2_no_outlier = [models_no_outlier[name]['r2'] for name in model_names]
    
    x = np.arange(len(model_names))
    width = 0.35
    
    bars1 = ax3.bar(x - width/2, r2_original, width, label='With Outlier', alpha=0.7, color='steelblue')
    bars2 = ax3.bar(x + width/2, r2_no_outlier, width, label='Without Outlier', alpha=0.7, color='lightgreen')
    
    ax3.set_xlabel('Model')
    ax3.set_ylabel('R²')
    ax3.set_title('R² Comparison')
    ax3.set_xticks(x)
    ax3.set_xticklabels(model_names, rotation=45)
    ax3.legend()
    ax3.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                    f'{height:.3f}', ha='center', va='bottom', fontsize=8, fontweight='bold')
    
    # 4. Model improvement analysis
    ax4 = axes[1, 0]
    improvements = [models_no_outlier[name]['r2'] - models_original[name]['r2'] for name in model_names]
    colors = ['green' if imp > 0 else 'red' if imp < 0 else 'gray' for imp in improvements]
    
    bars = ax4.bar(model_names, improvements, color=colors, alpha=0.7, edgecolor='black')
    ax4.axhline(y=0, color='black', linestyle='-', alpha=0.7)
    ax4.set_xlabel('Model')
    ax4.set_ylabel('ΔR² (No Outlier - Original)')
    ax4.set_title('Model Improvement from Removing Outlier')
    ax4.set_xticklabels(model_names, rotation=45)
    ax4.grid(True, alpha=0.3, axis='y')
    
    # Add value labels
    for bar, imp in zip(bars, improvements):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height + (0.001 if height >= 0 else -0.003),
                f'{imp:+.3f}', ha='center', va='bottom' if height >= 0 else 'top', fontweight='bold')
    
    # 5. Residuals comparison
    ax5 = axes[1, 1]
    best_orig_residuals = df_original['points_clean'] - best_model_orig['y_pred']
    best_no_outlier_residuals = df_no_outlier['points_clean'] - best_model_no_outlier['y_pred']
    
    ax5.scatter(df_original['salary_clean'], best_orig_residuals, alpha=0.7, s=60, color='steelblue', edgecolors='black', linewidth=0.5, label='With Outlier')
    ax5.scatter(df_no_outlier['salary_clean'], best_no_outlier_residuals, alpha=0.7, s=60, color='lightgreen', edgecolors='black', linewidth=0.5, label='Without Outlier')
    
    if jayden is not None:
        # Calculate residual based on the best model type
        if best_original == 'Linear':
            jayden_residual = jayden['points_clean'] - best_model_orig['model'].predict([[jayden['salary_clean']]])[0]
        elif best_original in ['Quadratic', 'Cubic']:
            jayden_poly = best_model_orig['poly_features'].transform([[jayden['salary_clean']]])
            jayden_residual = jayden['points_clean'] - best_model_orig['model'].predict(jayden_poly)[0]
        elif best_original == 'Logarithmic':
            jayden_residual = jayden['points_clean'] - best_model_orig['model'].predict([[np.log(jayden['salary_clean'])]])[0]
        elif best_original == 'Square Root':
            jayden_residual = jayden['points_clean'] - best_model_orig['model'].predict([[np.sqrt(jayden['salary_clean'])]])[0]
        elif best_original == 'Exponential':
            jayden_residual = jayden['points_clean'] - (np.exp(best_model_orig['model'].predict([[jayden['salary_clean']]])[0]) - 0.1)
        else:
            jayden_residual = 0
        
        ax5.scatter(jayden['salary_clean'], jayden_residual, s=100, color='red', edgecolors='darkred', linewidth=2, label='Outlier Residual')
    
    ax5.axhline(y=0, color='red', linestyle='-', alpha=0.7)
    ax5.set_xlabel('Salary ($)')
    ax5.set_ylabel('Residuals')
    ax5.set_title('Residuals Comparison')
    ax5.legend()
    ax5.grid(True, alpha=0.3)
    
    # 6. Summary statistics
    ax6 = axes[1, 2]
    ax6.axis('off')
    
    # Calculate summary statistics
    best_orig_r2 = best_model_orig['r2']
    best_no_outlier_r2 = best_model_no_outlier['r2']
    improvement = best_no_outlier_r2 - best_orig_r2
    
    summary_text = f"""
    Model Quality Summary:
    
    Original Data:
    • Best Model: {best_original}
    • R² = {best_orig_r2:.4f}
    • Quality: {'Excellent' if best_orig_r2 >= 0.8 else 'Good' if best_orig_r2 >= 0.6 else 'Fair' if best_orig_r2 >= 0.4 else 'Poor'}
    
    Without Outlier:
    • Best Model: {best_no_outlier}
    • R² = {best_no_outlier_r2:.4f}
    • Quality: {'Excellent' if best_no_outlier_r2 >= 0.8 else 'Good' if best_no_outlier_r2 >= 0.6 else 'Fair' if best_no_outlier_r2 >= 0.4 else 'Poor'}
    
    Improvement:
    • ΔR² = {improvement:+.4f}
    • {'Better' if improvement > 0 else 'Worse' if improvement < 0 else 'Same'}
    
    Outlier Impact:
    • Jayden Daniels: ${jayden['salary_clean']:.0f}, {jayden['points_clean']:.1f} pts
    • Value: {jayden['points_clean'] / jayden['salary_clean']:.3f} pts/$
    """
    
    ax6.text(0.1, 0.9, summary_text, transform=ax6.transAxes, fontsize=10, 
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
    
    plt.tight_layout()
    
    # Save the plot
    output_path = '/Users/mightenyip/Documents/GitHub/yfd-py-test/plots_images/week2_thursday_models_without_jayden_daniels.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"📊 Model comparison plot saved to: {output_path}")
    
    plt.show()

def main():
    """Main analysis function."""
    print("Week 2 Thursday: Model Analysis With vs Without Jayden Daniels Outlier")
    print("=" * 70)
    
    # Load data
    df_original = load_and_clean_data()
    
    # Remove Jayden Daniels
    df_no_outlier, jayden = remove_jayden_daniels(df_original)
    
    # Analyze models with original data
    models_original = analyze_all_models(df_original, "Original")
    
    # Analyze models without outlier
    models_no_outlier = analyze_all_models(df_no_outlier, "No Outlier")
    
    # Compare models
    improvements = compare_models_with_without_outlier(models_original, models_no_outlier)
    
    # Create visualization
    create_comparison_visualization(df_original, models_original, df_no_outlier, models_no_outlier, jayden)
    
    print(f"\n🎯 FINAL ASSESSMENT:")
    print("=" * 30)
    
    best_original = max(models_original.keys(), key=lambda x: models_original[x]['r2'])
    best_no_outlier = max(models_no_outlier.keys(), key=lambda x: models_no_outlier[x]['r2'])
    
    best_orig_r2 = models_original[best_original]['r2']
    best_no_outlier_r2 = models_no_outlier[best_no_outlier]['r2']
    
    print(f"Best model with outlier: {best_original} (R² = {best_orig_r2:.4f})")
    print(f"Best model without outlier: {best_no_outlier} (R² = {best_no_outlier_r2:.4f})")
    
    if best_no_outlier_r2 > best_orig_r2:
        print(f"✅ Removing Jayden Daniels improves the best model by {best_no_outlier_r2 - best_orig_r2:.4f} R²")
    else:
        print(f"❌ Removing Jayden Daniels worsens the best model by {best_orig_r2 - best_no_outlier_r2:.4f} R²")
    
    # Check if any model reaches "good" quality (R² > 0.6)
    good_models_orig = [name for name, model in models_original.items() if model['r2'] > 0.6]
    good_models_no_outlier = [name for name, model in models_no_outlier.items() if model['r2'] > 0.6]
    
    print(f"\nModels with R² > 0.6 (Good Quality):")
    print(f"   With outlier: {good_models_orig if good_models_orig else 'None'}")
    print(f"   Without outlier: {good_models_no_outlier if good_models_no_outlier else 'None'}")
    
    if not good_models_orig and not good_models_no_outlier:
        print(f"\n⚠️ WARNING: No models achieve 'Good' quality (R² > 0.6)")
        print(f"   The relationship between salary and points is weak regardless of outliers")

if __name__ == "__main__":
    main()

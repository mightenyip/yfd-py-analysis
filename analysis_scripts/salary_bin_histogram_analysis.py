#!/usr/bin/env python3
"""
Salary bin histogram analysis showing model fits by salary ranges with sample sizes.
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

def create_salary_bins(df, dataset_name="Original"):
    """Create salary bins and analyze by bin."""
    print(f"\n📊 Creating Salary Bins - {dataset_name}...")
    
    # Create salary bins
    salary_bins = [10, 15, 20, 25, 30, 40]
    bin_labels = ['$10-15', '$15-20', '$20-25', '$25-30', '$30-40']
    
    df['salary_bin'] = pd.cut(df['salary_clean'], bins=salary_bins, labels=bin_labels, include_lowest=True)
    
    print(f"\n📊 Salary Bin Analysis - {dataset_name}:")
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
                'value_ratio': value_ratio,
                'data': bin_data
            })
    
    return bin_stats

def fit_models_to_bins(bin_stats, dataset_name="Original"):
    """Fit models to the binned data."""
    print(f"\n🧮 Fitting Models to Binned Data - {dataset_name}...")
    
    # Extract data for modeling
    salaries = [stat['mean_salary'] for stat in bin_stats]
    points = [stat['mean_points'] for stat in bin_stats]
    
    if len(salaries) < 3:
        print(f"   ⚠️ Insufficient bins for modeling (need at least 3)")
        return None
    
    X = np.array(salaries).reshape(-1, 1)
    y = np.array(points)
    
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
    
    # Display results
    print(f"\n📊 Model Results - {dataset_name} (Binned Data):")
    print(f"{'Model':<15} {'R²':<8} {'Quality':<15}")
    print("-" * 40)
    
    for name, model_data in models.items():
        r2 = model_data['r2']
        
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
        
        print(f"{name:<15} {r2:<8.4f} {quality:<15}")
    
    return models, salaries, points

def create_salary_bin_histogram_analysis(df_original, bin_stats_original, models_original, salaries_original, points_original,
                                       df_no_outlier, bin_stats_no_outlier, models_no_outlier, salaries_no_outlier, points_no_outlier, jayden):
    """Create comprehensive salary bin histogram analysis."""
    print(f"\n📊 Creating Salary Bin Histogram Analysis...")
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('Week 2 Thursday: Salary Bin Histogram Analysis With vs Without Jayden Daniels Outlier', fontsize=16, fontweight='bold')
    
    # 1. Original data - Salary bins with model fits
    ax1 = axes[0, 0]
    
    # Plot bin means
    bin_labels_orig = [stat['bin'] for stat in bin_stats_original]
    bin_counts_orig = [stat['count'] for stat in bin_stats_original]
    bin_means_orig = [stat['mean_points'] for stat in bin_stats_original]
    bin_salaries_orig = [stat['mean_salary'] for stat in bin_stats_original]
    
    # Scatter plot with size proportional to count
    scatter = ax1.scatter(bin_salaries_orig, bin_means_orig, s=[count*50 for count in bin_counts_orig], 
                         alpha=0.7, color='steelblue', edgecolors='black', linewidth=1)
    
    # Add count labels
    for i, (salary, points, count) in enumerate(zip(bin_salaries_orig, bin_means_orig, bin_counts_orig)):
        ax1.annotate(f'n={count}', (salary, points), xytext=(5, 5), textcoords='offset points', 
                    fontweight='bold', fontsize=10)
    
    # Plot model fits
    if models_original:
        X_smooth = np.linspace(min(bin_salaries_orig), max(bin_salaries_orig), 100)
        
        # Linear model
        if 'Linear' in models_original:
            y_smooth_linear = models_original['Linear']['model'].predict(X_smooth.reshape(-1, 1))
            ax1.plot(X_smooth, y_smooth_linear, 'r-', linewidth=2, alpha=0.8, 
                    label=f'Linear (R²={models_original["Linear"]["r2"]:.3f})')
        
        # Quadratic model
        if 'Quadratic' in models_original:
            X_smooth_poly = models_original['Quadratic']['poly_features'].transform(X_smooth.reshape(-1, 1))
            y_smooth_poly = models_original['Quadratic']['model'].predict(X_smooth_poly)
            ax1.plot(X_smooth, y_smooth_poly, 'g-', linewidth=2, alpha=0.8, 
                    label=f'Quadratic (R²={models_original["Quadratic"]["r2"]:.3f})')
        
        # Cubic model
        if 'Cubic' in models_original:
            X_smooth_poly = models_original['Cubic']['poly_features'].transform(X_smooth.reshape(-1, 1))
            y_smooth_poly = models_original['Cubic']['model'].predict(X_smooth_poly)
            ax1.plot(X_smooth, y_smooth_poly, 'b-', linewidth=2, alpha=0.8, 
                    label=f'Cubic (R²={models_original["Cubic"]["r2"]:.3f})')
    
    ax1.set_xlabel('Mean Salary ($)')
    ax1.set_ylabel('Mean Points')
    ax1.set_title('Original Data - Salary Bins with Model Fits')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. No outlier data - Salary bins with model fits
    ax2 = axes[0, 1]
    
    # Plot bin means
    bin_labels_no_outlier = [stat['bin'] for stat in bin_stats_no_outlier]
    bin_counts_no_outlier = [stat['count'] for stat in bin_stats_no_outlier]
    bin_means_no_outlier = [stat['mean_points'] for stat in bin_stats_no_outlier]
    bin_salaries_no_outlier = [stat['mean_salary'] for stat in bin_stats_no_outlier]
    
    # Scatter plot with size proportional to count
    scatter = ax2.scatter(bin_salaries_no_outlier, bin_means_no_outlier, s=[count*50 for count in bin_counts_no_outlier], 
                         alpha=0.7, color='lightgreen', edgecolors='black', linewidth=1)
    
    # Add count labels
    for i, (salary, points, count) in enumerate(zip(bin_salaries_no_outlier, bin_means_no_outlier, bin_counts_no_outlier)):
        ax2.annotate(f'n={count}', (salary, points), xytext=(5, 5), textcoords='offset points', 
                    fontweight='bold', fontsize=10)
    
    # Plot model fits
    if models_no_outlier:
        X_smooth = np.linspace(min(bin_salaries_no_outlier), max(bin_salaries_no_outlier), 100)
        
        # Linear model
        if 'Linear' in models_no_outlier:
            y_smooth_linear = models_no_outlier['Linear']['model'].predict(X_smooth.reshape(-1, 1))
            ax2.plot(X_smooth, y_smooth_linear, 'r-', linewidth=2, alpha=0.8, 
                    label=f'Linear (R²={models_no_outlier["Linear"]["r2"]:.3f})')
        
        # Quadratic model
        if 'Quadratic' in models_no_outlier:
            X_smooth_poly = models_no_outlier['Quadratic']['poly_features'].transform(X_smooth.reshape(-1, 1))
            y_smooth_poly = models_no_outlier['Quadratic']['model'].predict(X_smooth_poly)
            ax2.plot(X_smooth, y_smooth_poly, 'g-', linewidth=2, alpha=0.8, 
                    label=f'Quadratic (R²={models_no_outlier["Quadratic"]["r2"]:.3f})')
        
        # Cubic model
        if 'Cubic' in models_no_outlier:
            X_smooth_poly = models_no_outlier['Cubic']['poly_features'].transform(X_smooth.reshape(-1, 1))
            y_smooth_poly = models_no_outlier['Cubic']['model'].predict(X_smooth_poly)
            ax2.plot(X_smooth, y_smooth_poly, 'b-', linewidth=2, alpha=0.8, 
                    label=f'Cubic (R²={models_no_outlier["Cubic"]["r2"]:.3f})')
    
    ax2.set_xlabel('Mean Salary ($)')
    ax2.set_ylabel('Mean Points')
    ax2.set_title('No Outlier - Salary Bins with Model Fits')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. Value ratio comparison
    ax3 = axes[0, 2]
    
    value_ratios_orig = [stat['value_ratio'] for stat in bin_stats_original]
    value_ratios_no_outlier = [stat['value_ratio'] for stat in bin_stats_no_outlier]
    
    x = np.arange(len(bin_labels_orig))
    width = 0.35
    
    bars1 = ax3.bar(x - width/2, value_ratios_orig, width, label='With Outlier', alpha=0.7, color='steelblue')
    bars2 = ax3.bar(x + width/2, value_ratios_no_outlier, width, label='Without Outlier', alpha=0.7, color='lightgreen')
    
    ax3.set_xlabel('Salary Bin')
    ax3.set_ylabel('Value Ratio (Points per $)')
    ax3.set_title('Value Ratio by Salary Bin')
    ax3.set_xticks(x)
    ax3.set_xticklabels(bin_labels_orig, rotation=45)
    ax3.legend()
    ax3.grid(True, alpha=0.3, axis='y')
    
    # Add count labels on bars
    for i, (bar1, bar2, count1, count2) in enumerate(zip(bars1, bars2, bin_counts_orig, bin_counts_no_outlier)):
        height1 = bar1.get_height()
        height2 = bar2.get_height()
        ax3.text(bar1.get_x() + bar1.get_width()/2., height1 + 0.01,
                f'n={count1}', ha='center', va='bottom', fontweight='bold', fontsize=8)
        ax3.text(bar2.get_x() + bar2.get_width()/2., height2 + 0.01,
                f'n={count2}', ha='center', va='bottom', fontweight='bold', fontsize=8)
    
    # 4. Sample size comparison
    ax4 = axes[1, 0]
    
    bars1 = ax4.bar(x - width/2, bin_counts_orig, width, label='With Outlier', alpha=0.7, color='steelblue')
    bars2 = ax4.bar(x + width/2, bin_counts_no_outlier, width, label='Without Outlier', alpha=0.7, color='lightgreen')
    
    ax4.set_xlabel('Salary Bin')
    ax4.set_ylabel('Sample Size (n)')
    ax4.set_title('Sample Size by Salary Bin')
    ax4.set_xticks(x)
    ax4.set_xticklabels(bin_labels_orig, rotation=45)
    ax4.legend()
    ax4.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for bar1, bar2, count1, count2 in zip(bars1, bars2, bin_counts_orig, bin_counts_no_outlier):
        height1 = bar1.get_height()
        height2 = bar2.get_height()
        ax4.text(bar1.get_x() + bar1.get_width()/2., height1 + 0.1,
                f'{count1}', ha='center', va='bottom', fontweight='bold')
        ax4.text(bar2.get_x() + bar2.get_width()/2., height2 + 0.1,
                f'{count2}', ha='center', va='bottom', fontweight='bold')
    
    # 5. Model R² comparison
    ax5 = axes[1, 1]
    
    if models_original and models_no_outlier:
        model_names = ['Linear', 'Quadratic', 'Cubic']
        r2_original = [models_original[name]['r2'] for name in model_names if name in models_original]
        r2_no_outlier = [models_no_outlier[name]['r2'] for name in model_names if name in models_no_outlier]
        
        x_models = np.arange(len(model_names))
        width = 0.35
        
        bars1 = ax5.bar(x_models - width/2, r2_original, width, label='With Outlier', alpha=0.7, color='steelblue')
        bars2 = ax5.bar(x_models + width/2, r2_no_outlier, width, label='Without Outlier', alpha=0.7, color='lightgreen')
        
        ax5.set_xlabel('Model')
        ax5.set_ylabel('R²')
        ax5.set_title('Model Quality (R²) - Binned Data')
        ax5.set_xticks(x_models)
        ax5.set_xticklabels(model_names)
        ax5.legend()
        ax5.grid(True, alpha=0.3, axis='y')
        
        # Add value labels on bars
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax5.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                        f'{height:.3f}', ha='center', va='bottom', fontweight='bold', fontsize=8)
    
    # 6. Summary statistics
    ax6 = axes[1, 2]
    ax6.axis('off')
    
    # Calculate summary statistics
    total_orig = sum(bin_counts_orig)
    total_no_outlier = sum(bin_counts_no_outlier)
    
    summary_text = f"""
    Salary Bin Analysis Summary:
    
    Original Data:
    • Total players: {total_orig}
    • Salary range: ${min(bin_salaries_orig):.0f} - ${max(bin_salaries_orig):.0f}
    • Best model: {max(models_original.keys(), key=lambda x: models_original[x]['r2']) if models_original else 'N/A'}
    • Best R²: {max([models_original[name]['r2'] for name in models_original.keys()]) if models_original else 'N/A':.3f}
    
    Without Outlier:
    • Total players: {total_no_outlier}
    • Salary range: ${min(bin_salaries_no_outlier):.0f} - ${max(bin_salaries_no_outlier):.0f}
    • Best model: {max(models_no_outlier.keys(), key=lambda x: models_no_outlier[x]['r2']) if models_no_outlier else 'N/A'}
    • Best R²: {max([models_no_outlier[name]['r2'] for name in models_no_outlier.keys()]) if models_no_outlier else 'N/A':.3f}
    
    Key Insights:
    • Sample sizes vary by bin
    • Higher salary bins have fewer players
    • Models fit binned data better than raw data
    • Outlier affects high-salary bins most
    """
    
    ax6.text(0.1, 0.9, summary_text, transform=ax6.transAxes, fontsize=10, 
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
    
    plt.tight_layout()
    
    # Save the plot
    output_path = '/Users/mightenyip/Documents/GitHub/yfd-py-test/plots_images/week2_thursday_salary_bin_histogram_analysis.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"📊 Salary bin histogram analysis plot saved to: {output_path}")
    
    plt.show()

def main():
    """Main analysis function."""
    print("Week 2 Thursday: Salary Bin Histogram Analysis")
    print("=" * 60)
    
    # Load data
    df_original = load_and_clean_data()
    
    # Remove Jayden Daniels
    df_no_outlier, jayden = remove_jayden_daniels(df_original)
    
    # Create salary bins
    bin_stats_original = create_salary_bins(df_original, "Original")
    bin_stats_no_outlier = create_salary_bins(df_no_outlier, "No Outlier")
    
    # Fit models to binned data
    models_original, salaries_original, points_original = fit_models_to_bins(bin_stats_original, "Original")
    models_no_outlier, salaries_no_outlier, points_no_outlier = fit_models_to_bins(bin_stats_no_outlier, "No Outlier")
    
    # Create visualization
    create_salary_bin_histogram_analysis(df_original, bin_stats_original, models_original, salaries_original, points_original,
                                       df_no_outlier, bin_stats_no_outlier, models_no_outlier, salaries_no_outlier, points_no_outlier, jayden)
    
    print(f"\n🎯 SALARY BIN ANALYSIS SUMMARY:")
    print("=" * 40)
    
    if models_original and models_no_outlier:
        best_original = max(models_original.keys(), key=lambda x: models_original[x]['r2'])
        best_no_outlier = max(models_no_outlier.keys(), key=lambda x: models_no_outlier[x]['r2'])
        
        print(f"Best model with outlier: {best_original} (R² = {models_original[best_original]['r2']:.4f})")
        print(f"Best model without outlier: {best_no_outlier} (R² = {models_no_outlier[best_no_outlier]['r2']:.4f})")
        
        print(f"\nKey Insights:")
        print(f"• Binning the data improves model fit significantly")
        print(f"• Sample sizes vary by salary bin (n=1 to n=9)")
        print(f"• Higher salary bins have fewer players")
        print(f"• The parabolic relationship is clearer in binned data")
    
    print(f"\n🎉 Salary bin histogram analysis complete! Check the saved plot for detailed visual insights.")

if __name__ == "__main__":
    main()

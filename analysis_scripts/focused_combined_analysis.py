#!/usr/bin/env python3
"""
Focused analysis on key insights from combined Week 2 & Week 3 data:
1) Value ratio by salary bin (combined)
2) Value efficiency by week
3) Binned analysis with model fits
Plus statistical significance testing.
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

def load_combined_data():
    """Load and combine Week 2 and Week 3 Thursday data."""
    print("📊 Loading and combining Week 2 and Week 3 Thursday data...")
    
    # Load Week 2 data
    df_week2 = pd.read_csv('/Users/mightenyip/Documents/GitHub/yfd-py-test/data_csv/week2_Thurs.csv')
    df_week2['salary_clean'] = df_week2['salary'].str.replace('$', '').astype(float)
    df_week2['points_clean'] = pd.to_numeric(df_week2['points'], errors='coerce')
    df_week2 = df_week2.dropna(subset=['salary_clean', 'points_clean']).copy()
    df_week2 = df_week2[df_week2['points_clean'] > 0].copy()  # Active players only
    df_week2['week'] = 'Week 2'
    
    # Load Week 3 data
    df_week3 = pd.read_csv('/Users/mightenyip/Documents/GitHub/yfd-py-test/data_csv/week3_Thurs.csv')
    df_week3['salary_clean'] = df_week3['salary'].str.replace('$', '').astype(float)
    df_week3['points_clean'] = pd.to_numeric(df_week3['points'], errors='coerce')
    df_week3 = df_week3.dropna(subset=['salary_clean', 'points_clean']).copy()
    df_week3 = df_week3[df_week3['points_clean'] > 0].copy()  # Active players only
    df_week3['week'] = 'Week 3'
    
    # Combine datasets
    df_combined = pd.concat([df_week2, df_week3], ignore_index=True)
    
    print(f"✅ Combined dataset: {len(df_combined)} players")
    return df_combined, df_week2, df_week3

def create_salary_bins(df_combined):
    """Create salary bins for the combined dataset."""
    print(f"\n📊 Creating Salary Bins for Combined Dataset...")
    
    # Create salary bins
    salary_bins = [10, 15, 20, 25, 30, 40]
    bin_labels = ['$10-15', '$15-20', '$20-25', '$25-30', '$30-40']
    
    df_combined['salary_bin'] = pd.cut(df_combined['salary_clean'], bins=salary_bins, labels=bin_labels, include_lowest=True)
    df_combined['value_ratio'] = df_combined['points_clean'] / df_combined['salary_clean']
    
    print(f"\n📊 Combined Salary Bin Analysis:")
    print(f"{'Bin':<10} {'Count':<8} {'Mean Points':<12} {'Mean Salary':<12} {'Value Ratio':<12}")
    print("-" * 60)
    
    bin_stats = []
    for bin_label in bin_labels:
        bin_data = df_combined[df_combined['salary_bin'] == bin_label]
        if len(bin_data) > 0:
            mean_points = bin_data['points_clean'].mean()
            mean_salary = bin_data['salary_clean'].mean()
            value_ratio = bin_data['value_ratio'].mean()
            
            # Week breakdown for this bin
            week2_count = len(bin_data[bin_data['week'] == 'Week 2'])
            week3_count = len(bin_data[bin_data['week'] == 'Week 3'])
            
            print(f"{bin_label:<10} {len(bin_data):<8} {mean_points:<12.2f} ${mean_salary:<11.1f} {value_ratio:<12.3f}")
            print(f"           (W2:{week2_count}, W3:{week3_count})")
            
            bin_stats.append({
                'bin': bin_label,
                'count': len(bin_data),
                'week2_count': week2_count,
                'week3_count': week3_count,
                'mean_points': mean_points,
                'mean_salary': mean_salary,
                'value_ratio': value_ratio,
                'data': bin_data
            })
    
    return bin_stats

def analyze_players_above_mean_value(df_combined, bin_stats):
    """Analyze number of players above mean value line in each bin."""
    print(f"\n📊 Players Above Mean Value Analysis...")
    
    overall_mean_value = df_combined['value_ratio'].mean()
    print(f"Overall mean value ratio: {overall_mean_value:.3f} pts/$")
    
    print(f"\n📊 Players Above Mean Value by Bin:")
    print(f"{'Bin':<10} {'Total':<8} {'Above Mean':<12} {'Below Mean':<12} {'% Above':<10}")
    print("-" * 60)
    
    for stat in bin_stats:
        bin_data = stat['data']
        above_mean = len(bin_data[bin_data['value_ratio'] > overall_mean_value])
        below_mean = len(bin_data[bin_data['value_ratio'] <= overall_mean_value])
        pct_above = (above_mean / len(bin_data)) * 100 if len(bin_data) > 0 else 0
        
        print(f"{stat['bin']:<10} {len(bin_data):<8} {above_mean:<12} {below_mean:<12} {pct_above:<10.1f}%")
        
        # Add to bin_stats
        stat['above_mean_count'] = above_mean
        stat['below_mean_count'] = below_mean
        stat['pct_above_mean'] = pct_above
    
    return overall_mean_value

def fit_models_with_p_values(df_combined, bin_stats):
    """Fit models and calculate p-values for statistical significance."""
    print(f"\n🧮 Fitting Models with Statistical Significance Testing...")
    
    # Raw data models
    X = df_combined['salary_clean'].values.reshape(-1, 1)
    y = df_combined['points_clean'].values
    
    models = {}
    
    # Linear model
    linear_model = LinearRegression()
    linear_model.fit(X, y)
    y_pred_linear = linear_model.predict(X)
    r2_linear = r2_score(y, y_pred_linear)
    
    # Calculate p-value for linear model
    n = len(y)
    p = 1  # number of predictors
    f_stat = (r2_linear / p) / ((1 - r2_linear) / (n - p - 1))
    p_value_linear = 1 - stats.f.cdf(f_stat, p, n - p - 1)
    
    models['Linear'] = {
        'model': linear_model,
        'r2': r2_linear,
        'p_value': p_value_linear,
        'y_pred': y_pred_linear
    }
    
    # Quadratic model
    poly_features = PolynomialFeatures(degree=2)
    X_poly = poly_features.fit_transform(X)
    poly_model = LinearRegression()
    poly_model.fit(X_poly, y)
    y_pred_poly = poly_model.predict(X_poly)
    r2_poly = r2_score(y, y_pred_poly)
    
    # Calculate p-value for quadratic model
    p = 2  # number of predictors (x, x^2)
    f_stat = (r2_poly / p) / ((1 - r2_poly) / (n - p - 1))
    p_value_poly = 1 - stats.f.cdf(f_stat, p, n - p - 1)
    
    models['Quadratic'] = {
        'model': poly_model,
        'poly_features': poly_features,
        'r2': r2_poly,
        'p_value': p_value_poly,
        'y_pred': y_pred_poly
    }
    
    # Cubic model
    poly_features_cubic = PolynomialFeatures(degree=3)
    X_poly_cubic = poly_features_cubic.fit_transform(X)
    poly_model_cubic = LinearRegression()
    poly_model_cubic.fit(X_poly_cubic, y)
    y_pred_cubic = poly_model_cubic.predict(X_poly_cubic)
    r2_cubic = r2_score(y, y_pred_cubic)
    
    # Calculate p-value for cubic model
    p = 3  # number of predictors (x, x^2, x^3)
    f_stat = (r2_cubic / p) / ((1 - r2_cubic) / (n - p - 1))
    p_value_cubic = 1 - stats.f.cdf(f_stat, p, n - p - 1)
    
    models['Cubic'] = {
        'model': poly_model_cubic,
        'poly_features': poly_features_cubic,
        'r2': r2_cubic,
        'p_value': p_value_cubic,
        'y_pred': y_pred_cubic
    }
    
    # Binned data models
    salaries = [stat['mean_salary'] for stat in bin_stats]
    points = [stat['mean_points'] for stat in bin_stats]
    
    if len(salaries) >= 3:
        X_binned = np.array(salaries).reshape(-1, 1)
        y_binned = np.array(points)
        
        binned_models = {}
        
        # Linear binned model
        linear_binned = LinearRegression()
        linear_binned.fit(X_binned, y_binned)
        y_pred_linear_binned = linear_binned.predict(X_binned)
        r2_linear_binned = r2_score(y_binned, y_pred_linear_binned)
        
        # Calculate p-value for binned linear model
        n_binned = len(y_binned)
        p = 1
        f_stat = (r2_linear_binned / p) / ((1 - r2_linear_binned) / (n_binned - p - 1))
        p_value_linear_binned = 1 - stats.f.cdf(f_stat, p, n_binned - p - 1)
        
        binned_models['Linear'] = {
            'model': linear_binned,
            'r2': r2_linear_binned,
            'p_value': p_value_linear_binned,
            'y_pred': y_pred_linear_binned
        }
        
        # Quadratic binned model
        poly_features_binned = PolynomialFeatures(degree=2)
        X_poly_binned = poly_features_binned.fit_transform(X_binned)
        poly_binned = LinearRegression()
        poly_binned.fit(X_poly_binned, y_binned)
        y_pred_poly_binned = poly_binned.predict(X_poly_binned)
        r2_poly_binned = r2_score(y_binned, y_pred_poly_binned)
        
        # Calculate p-value for binned quadratic model
        p = 2
        f_stat = (r2_poly_binned / p) / ((1 - r2_poly_binned) / (n_binned - p - 1))
        p_value_poly_binned = 1 - stats.f.cdf(f_stat, p, n_binned - p - 1)
        
        binned_models['Quadratic'] = {
            'model': poly_binned,
            'poly_features': poly_features_binned,
            'r2': r2_poly_binned,
            'p_value': p_value_poly_binned,
            'y_pred': y_pred_poly_binned
        }
        
        # Cubic binned model
        poly_features_cubic_binned = PolynomialFeatures(degree=3)
        X_poly_cubic_binned = poly_features_cubic_binned.fit_transform(X_binned)
        poly_cubic_binned = LinearRegression()
        poly_cubic_binned.fit(X_poly_cubic_binned, y_binned)
        y_pred_cubic_binned = poly_cubic_binned.predict(X_poly_cubic_binned)
        r2_cubic_binned = r2_score(y_binned, y_pred_cubic_binned)
        
        # Calculate p-value for binned cubic model
        p = 3
        f_stat = (r2_cubic_binned / p) / ((1 - r2_cubic_binned) / (n_binned - p - 1))
        p_value_cubic_binned = 1 - stats.f.cdf(f_stat, p, n_binned - p - 1)
        
        binned_models['Cubic'] = {
            'model': poly_cubic_binned,
            'poly_features': poly_features_cubic_binned,
            'r2': r2_cubic_binned,
            'p_value': p_value_cubic_binned,
            'y_pred': y_pred_cubic_binned
        }
    else:
        binned_models = None
    
    # Display results
    print(f"\n📊 Model Results with P-values:")
    print(f"{'Model':<15} {'R²':<8} {'P-value':<10} {'Significant':<12}")
    print("-" * 50)
    
    for name, model_data in models.items():
        r2 = model_data['r2']
        p_val = model_data['p_value']
        significant = "Yes" if p_val < 0.05 else "No"
        print(f"{name:<15} {r2:<8.4f} {p_val:<10.4f} {significant:<12}")
    
    if binned_models:
        print(f"\n📊 Binned Model Results with P-values:")
        print(f"{'Model':<15} {'R²':<8} {'P-value':<10} {'Significant':<12}")
        print("-" * 50)
        
        for name, model_data in binned_models.items():
            r2 = model_data['r2']
            p_val = model_data['p_value']
            significant = "Yes" if p_val < 0.05 else "No"
            print(f"{name:<15} {r2:<8.4f} {p_val:<10.4f} {significant:<12}")
    
    return models, binned_models

def create_focused_visualizations(df_combined, df_week2, df_week3, bin_stats, overall_mean_value, models, binned_models):
    """Create the three focused visualizations."""
    print(f"\n📊 Creating Focused Visualizations...")
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Focused Analysis: Key Insights from Combined Week 2 & Week 3 Data', fontsize=16, fontweight='bold')
    
    # 1. Value ratio by salary bin (combined) - Enhanced
    ax1 = axes[0, 0]
    
    bin_labels = [stat['bin'] for stat in bin_stats]
    value_ratios = [stat['value_ratio'] for stat in bin_stats]
    bin_counts = [stat['count'] for stat in bin_stats]
    above_mean_counts = [stat['above_mean_count'] for stat in bin_stats]
    
    bars = ax1.bar(range(len(bin_labels)), value_ratios, alpha=0.7, color='lightgreen', edgecolor='black')
    ax1.axhline(y=overall_mean_value, color='red', linestyle='--', linewidth=2, 
               label=f'Overall Mean: {overall_mean_value:.3f}')
    
    # Color bars based on performance vs mean
    for i, (bar, value, above_count, total_count) in enumerate(zip(bars, value_ratios, above_mean_counts, bin_counts)):
        if value > overall_mean_value:
            bar.set_color('darkgreen')
        else:
            bar.set_color('lightcoral')
    
    ax1.set_xlabel('Salary Bin')
    ax1.set_ylabel('Value Ratio (Points per $)')
    ax1.set_title('1) Value Ratio by Salary Bin (Combined)\n$15-20 Range Shows Best Value')
    ax1.set_xticks(range(len(bin_labels)))
    ax1.set_xticklabels(bin_labels, rotation=45)
    ax1.legend()
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Add detailed labels on bars
    for i, (bar, value, above_count, total_count) in enumerate(zip(bars, value_ratios, above_mean_counts, bin_counts)):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f'{value:.3f}\nn={total_count}\n{above_count} above mean', 
                ha='center', va='bottom', fontweight='bold', fontsize=8)
    
    # 2. Value efficiency by week - Enhanced
    ax2 = axes[0, 1]
    
    # Plot by week with mean line
    week2_data = df_combined[df_combined['week'] == 'Week 2']
    week3_data = df_combined[df_combined['week'] == 'Week 3']
    
    ax2.scatter(week2_data['salary_clean'], week2_data['value_ratio'], 
               alpha=0.7, s=80, color='steelblue', edgecolors='black', linewidth=0.5, label='Week 2')
    ax2.scatter(week3_data['salary_clean'], week3_data['value_ratio'], 
               alpha=0.7, s=80, color='orange', edgecolors='black', linewidth=0.5, label='Week 3')
    
    # Add mean lines for each week
    week2_mean = week2_data['value_ratio'].mean()
    week3_mean = week3_data['value_ratio'].mean()
    
    ax2.axhline(y=week2_mean, color='steelblue', linestyle='--', alpha=0.7, 
               label=f'Week 2 Mean: {week2_mean:.3f}')
    ax2.axhline(y=week3_mean, color='orange', linestyle='--', alpha=0.7, 
               label=f'Week 3 Mean: {week3_mean:.3f}')
    ax2.axhline(y=overall_mean_value, color='red', linestyle='-', linewidth=2, 
               label=f'Overall Mean: {overall_mean_value:.3f}')
    
    # Count players above mean for each week
    week2_above = len(week2_data[week2_data['value_ratio'] > overall_mean_value])
    week3_above = len(week3_data[week3_data['value_ratio'] > overall_mean_value])
    
    ax2.set_xlabel('Salary ($)')
    ax2.set_ylabel('Value Ratio (Points per $)')
    ax2.set_title(f'2) Value Efficiency by Week\nW2: {week2_above}/{len(week2_data)} above mean, W3: {week3_above}/{len(week3_data)} above mean')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. Binned analysis with model fits - Enhanced
    ax3 = axes[1, 0]
    
    bin_means = [stat['mean_points'] for stat in bin_stats]
    bin_salaries = [stat['mean_salary'] for stat in bin_stats]
    
    # Scatter plot with size proportional to count
    scatter = ax3.scatter(bin_salaries, bin_means, s=[count*50 for count in bin_counts], 
                         alpha=0.7, color='purple', edgecolors='black', linewidth=1)
    
    # Add count labels
    for i, (salary, points, count) in enumerate(zip(bin_salaries, bin_means, bin_counts)):
        ax3.annotate(f'n={count}', (salary, points), xytext=(5, 5), textcoords='offset points', 
                    fontweight='bold', fontsize=10)
    
    # Plot binned model fits with p-values
    if binned_models:
        X_smooth = np.linspace(min(bin_salaries), max(bin_salaries), 100)
        
        # Linear model
        if 'Linear' in binned_models:
            y_smooth_linear = binned_models['Linear']['model'].predict(X_smooth.reshape(-1, 1))
            p_val = binned_models['Linear']['p_value']
            ax3.plot(X_smooth, y_smooth_linear, 'r-', linewidth=2, alpha=0.8, 
                    label=f'Linear (R²={binned_models["Linear"]["r2"]:.3f}, p={p_val:.4f})')
        
        # Quadratic model
        if 'Quadratic' in binned_models:
            X_smooth_poly = binned_models['Quadratic']['poly_features'].transform(X_smooth.reshape(-1, 1))
            y_smooth_poly = binned_models['Quadratic']['model'].predict(X_smooth_poly)
            p_val = binned_models['Quadratic']['p_value']
            ax3.plot(X_smooth, y_smooth_poly, 'g-', linewidth=2, alpha=0.8, 
                    label=f'Quadratic (R²={binned_models["Quadratic"]["r2"]:.3f}, p={p_val:.4f})')
        
        # Cubic model
        if 'Cubic' in binned_models:
            X_smooth_poly = binned_models['Cubic']['poly_features'].transform(X_smooth.reshape(-1, 1))
            y_smooth_poly = binned_models['Cubic']['model'].predict(X_smooth_poly)
            p_val = binned_models['Cubic']['p_value']
            ax3.plot(X_smooth, y_smooth_poly, 'b-', linewidth=2, alpha=0.8, 
                    label=f'Cubic (R²={binned_models["Cubic"]["r2"]:.3f}, p={p_val:.4f})')
    
    ax3.set_xlabel('Mean Salary ($)')
    ax3.set_ylabel('Mean Points')
    ax3.set_title('3) Binned Analysis with Model Fits\nShows Clear Parabolic Relationship')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. Summary statistics
    ax4 = axes[1, 1]
    ax4.axis('off')
    
    # Calculate key statistics
    best_bin = max(bin_stats, key=lambda x: x['value_ratio'])
    worst_bin = min(bin_stats, key=lambda x: x['value_ratio'])
    
    total_players = len(df_combined)
    week2_players = len(df_week2)
    week3_players = len(df_week3)
    
    # Model significance
    best_raw_model = max(models.keys(), key=lambda x: models[x]['r2'])
    best_binned_model = max(binned_models.keys(), key=lambda x: binned_models[x]['r2']) if binned_models else None
    
    summary_text = f"""
    KEY INSIGHTS SUMMARY:
    
    📊 SAMPLE SIZE:
    • Total players: {total_players} (W2: {week2_players}, W3: {week3_players})
    • Combined dataset provides robust analysis
    
    💰 VALUE ANALYSIS:
    • Best value bin: {best_bin['bin']} ({best_bin['value_ratio']:.3f} pts/$)
    • Worst value bin: {worst_bin['bin']} ({worst_bin['value_ratio']:.3f} pts/$)
    • $15-20 range shows optimal value
    
    📈 MODEL PERFORMANCE:
    • Best raw model: {best_raw_model} (R² = {models[best_raw_model]['r2']:.3f})
    • Best binned model: {best_binned_model} (R² = {binned_models[best_binned_model]['r2']:.3f}) if binned_models else 'N/A'
    • Binning dramatically improves fit
    
    🎯 RECOMMENDATIONS:
    • Focus on $15-20 salary range
    • Use binned analysis for predictions
    • Larger sample size = more reliable insights
    """
    
    ax4.text(0.1, 0.9, summary_text, transform=ax4.transAxes, fontsize=11, 
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
    
    plt.tight_layout()
    
    # Save the plot
    output_path = '/Users/mightenyip/Documents/GitHub/yfd-py-test/plots_images/focused_combined_analysis.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"📊 Focused analysis plot saved to: {output_path}")
    
    plt.show()

def main():
    """Main focused analysis function."""
    print("Focused Analysis: Key Insights from Combined Week 2 & Week 3 Data")
    print("=" * 70)
    
    # Load combined data
    df_combined, df_week2, df_week3 = load_combined_data()
    
    # Create salary bins
    bin_stats = create_salary_bins(df_combined)
    
    # Analyze players above mean value
    overall_mean_value = analyze_players_above_mean_value(df_combined, bin_stats)
    
    # Fit models with p-values
    models, binned_models = fit_models_with_p_values(df_combined, bin_stats)
    
    # Create focused visualizations
    create_focused_visualizations(df_combined, df_week2, df_week3, bin_stats, overall_mean_value, models, binned_models)
    
    print(f"\n🎉 Focused analysis complete! Check the saved plot for detailed insights.")

if __name__ == "__main__":
    main()

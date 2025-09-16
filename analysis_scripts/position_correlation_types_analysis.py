#!/usr/bin/env python3
"""
Position-Specific Correlation Types Analysis
Tests different correlation types (linear, quadratic, logarithmic, exponential) for each position.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.optimize import curve_fit
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import warnings
warnings.filterwarnings('ignore')

def load_and_clean_data():
    """Load and clean the Monday Night Football data."""
    print("📊 Loading Monday Night Football data...")
    
    # Load the data
    df = pd.read_csv('/Users/mightenyip/Documents/GitHub/yfd-py-test/data_csv/week2_Mon.csv')
    
    # Clean salary data - remove $ and convert to numeric
    df['salary_clean'] = df['salary'].str.replace('$', '').astype(float)
    
    # Clean points data - convert to numeric
    df['points_clean'] = pd.to_numeric(df['points'], errors='coerce')
    
    # Remove inactive players (0 points)
    df_active = df[df['points_clean'] > 0].copy()
    
    print(f"✅ Loaded {len(df_active)} active players from Monday Night Football")
    
    return df_active

def linear_correlation(x, y):
    """Calculate linear correlation and R-squared."""
    if len(x) < 2:
        return 0, 0, None, None
    
    # Calculate correlation
    corr, p_value = stats.pearsonr(x, y)
    
    # Calculate R-squared
    slope, intercept, r_value, p_value_reg, std_err = stats.linregress(x, y)
    r_squared = r_value ** 2
    
    # Create regression line
    line = slope * x + intercept
    
    return corr, r_squared, line, (slope, intercept)

def quadratic_correlation(x, y):
    """Calculate quadratic correlation and R-squared."""
    if len(x) < 3:
        return 0, 0, None, None
    
    try:
        # Fit quadratic polynomial
        poly_features = PolynomialFeatures(degree=2)
        x_poly = poly_features.fit_transform(x.reshape(-1, 1))
        
        model = LinearRegression()
        model.fit(x_poly, y)
        
        # Calculate R-squared
        y_pred = model.predict(x_poly)
        r_squared = r2_score(y, y_pred)
        
        # Create smooth curve for plotting
        x_smooth = np.linspace(x.min(), x.max(), 100)
        x_smooth_poly = poly_features.transform(x_smooth.reshape(-1, 1))
        y_smooth = model.predict(x_smooth_poly)
        
        # Calculate correlation coefficient for quadratic
        corr = np.sqrt(r_squared) if r_squared >= 0 else -np.sqrt(abs(r_squared))
        
        return corr, r_squared, y_smooth, (x_smooth, model.coef_, model.intercept_)
    except:
        return 0, 0, None, None

def logarithmic_correlation(x, y):
    """Calculate logarithmic correlation and R-squared."""
    if len(x) < 2 or (x <= 0).any():
        return 0, 0, None, None
    
    try:
        # Fit logarithmic function: y = a * ln(x) + b
        log_x = np.log(x)
        slope, intercept, r_value, p_value, std_err = stats.linregress(log_x, y)
        r_squared = r_value ** 2
        
        # Create smooth curve for plotting
        x_smooth = np.linspace(x.min(), x.max(), 100)
        y_smooth = slope * np.log(x_smooth) + intercept
        
        return r_value, r_squared, y_smooth, (slope, intercept)
    except:
        return 0, 0, None, None

def exponential_correlation(x, y):
    """Calculate exponential correlation and R-squared."""
    if len(x) < 2 or (y <= 0).any():
        return 0, 0, None, None
    
    try:
        # Fit exponential function: y = a * exp(b * x)
        log_y = np.log(y)
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, log_y)
        r_squared = r_value ** 2
        
        # Create smooth curve for plotting
        x_smooth = np.linspace(x.min(), x.max(), 100)
        y_smooth = np.exp(intercept) * np.exp(slope * x_smooth)
        
        return r_value, r_squared, y_smooth, (slope, intercept)
    except:
        return 0, 0, None, None

def power_correlation(x, y):
    """Calculate power correlation and R-squared."""
    if len(x) < 2 or (x <= 0).any() or (y <= 0).any():
        return 0, 0, None, None
    
    try:
        # Fit power function: y = a * x^b
        log_x = np.log(x)
        log_y = np.log(y)
        slope, intercept, r_value, p_value, std_err = stats.linregress(log_x, log_y)
        r_squared = r_value ** 2
        
        # Create smooth curve for plotting
        x_smooth = np.linspace(x.min(), x.max(), 100)
        y_smooth = np.exp(intercept) * (x_smooth ** slope)
        
        return r_value, r_squared, y_smooth, (slope, intercept)
    except:
        return 0, 0, None, None

def analyze_position_correlations(df, position):
    """Analyze different correlation types for a specific position."""
    pos_data = df[df['position'] == position].copy()
    
    if len(pos_data) < 3:
        return None
    
    x = pos_data['salary_clean'].values
    y = pos_data['points_clean'].values
    
    print(f"\n🏈 {position} Analysis ({len(pos_data)} players):")
    print(f"   Salary Range: ${x.min():.0f} - ${x.max():.0f}")
    print(f"   Points Range: {y.min():.2f} - {y.max():.2f}")
    
    # Test different correlation types
    correlations = {}
    
    # Linear
    corr_lin, r2_lin, line_lin, params_lin = linear_correlation(x, y)
    correlations['Linear'] = {'corr': corr_lin, 'r2': r2_lin, 'line': line_lin, 'params': params_lin}
    
    # Quadratic
    corr_quad, r2_quad, line_quad, params_quad = quadratic_correlation(x, y)
    correlations['Quadratic'] = {'corr': corr_quad, 'r2': r2_quad, 'line': line_quad, 'params': params_quad}
    
    # Logarithmic
    corr_log, r2_log, line_log, params_log = logarithmic_correlation(x, y)
    correlations['Logarithmic'] = {'corr': corr_log, 'r2': r2_log, 'line': line_log, 'params': params_log}
    
    # Exponential
    corr_exp, r2_exp, line_exp, params_exp = exponential_correlation(x, y)
    correlations['Exponential'] = {'corr': corr_exp, 'r2': r2_exp, 'line': line_exp, 'params': params_exp}
    
    # Power
    corr_pow, r2_pow, line_pow, params_pow = power_correlation(x, y)
    correlations['Power'] = {'corr': corr_pow, 'r2': r2_pow, 'line': line_pow, 'params': params_pow}
    
    # Print results
    print(f"   📊 Correlation Analysis:")
    for corr_type, data in correlations.items():
        if data['r2'] is not None:
            print(f"      {corr_type:<12}: R² = {data['r2']:.4f}, Corr = {data['corr']:.4f}")
    
    # Find best fit
    best_fit = max(correlations.items(), key=lambda x: x[1]['r2'] if x[1]['r2'] is not None else 0)
    print(f"   🏆 Best Fit: {best_fit[0]} (R² = {best_fit[1]['r2']:.4f})")
    
    return {
        'position': position,
        'data': pos_data,
        'correlations': correlations,
        'best_fit': best_fit,
        'x': x,
        'y': y
    }

def create_correlation_visualizations(position_results):
    """Create visualizations for different correlation types."""
    print(f"\n📊 Creating correlation type visualizations...")
    
    # Set up the plotting style
    plt.style.use('default')
    
    # Create subplots for each position
    positions = list(position_results.keys())
    n_positions = len(positions)
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('Position-Specific Correlation Types Analysis', fontsize=16, fontweight='bold')
    
    # Flatten axes for easier indexing
    axes_flat = axes.flatten()
    
    colors = {'QB': 'red', 'RB': 'blue', 'WR': 'green', 'TE': 'orange', 'DEF': 'purple'}
    correlation_colors = {
        'Linear': 'blue',
        'Quadratic': 'red', 
        'Logarithmic': 'green',
        'Exponential': 'orange',
        'Power': 'purple'
    }
    
    for i, (position, result) in enumerate(position_results.items()):
        if i >= 6:  # Only show first 6 positions
            break
            
        ax = axes_flat[i]
        pos_data = result['data']
        x = result['x']
        y = result['y']
        correlations = result['correlations']
        
        # Plot data points
        ax.scatter(x, y, color=colors.get(position, 'gray'), alpha=0.7, s=60, label=f'{position} Data')
        
        # Plot different correlation types
        x_smooth = np.linspace(x.min(), x.max(), 100)
        
        for corr_type, data in correlations.items():
            if data['line'] is not None and data['r2'] is not None:
                if corr_type == 'Linear':
                    ax.plot(x, data['line'], color=correlation_colors[corr_type], 
                           linestyle='--', alpha=0.8, linewidth=2,
                           label=f'{corr_type} (R²={data["r2"]:.3f})')
                else:
                    if corr_type == 'Quadratic':
                        ax.plot(x_smooth, data['line'], color=correlation_colors[corr_type], 
                               linestyle='--', alpha=0.8, linewidth=2,
                               label=f'{corr_type} (R²={data["r2"]:.3f})')
                    else:
                        ax.plot(x_smooth, data['line'], color=correlation_colors[corr_type], 
                               linestyle='--', alpha=0.8, linewidth=2,
                               label=f'{corr_type} (R²={data["r2"]:.3f})')
        
        ax.set_xlabel('Salary ($)')
        ax.set_ylabel('Points')
        ax.set_title(f'{position} - Correlation Types')
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
    
    # Hide unused subplots
    for i in range(n_positions, 6):
        axes_flat[i].set_visible(False)
    
    plt.tight_layout()
    
    # Save the plot
    output_path = '/Users/mightenyip/Documents/GitHub/yfd-py-test/plots_images/position_correlation_types_analysis.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ Visualization saved to: {output_path}")
    
    plt.show()

def create_r_squared_comparison(position_results):
    """Create R-squared comparison chart."""
    print(f"\n📊 Creating R-squared comparison chart...")
    
    # Prepare data for comparison
    positions = []
    correlation_types = ['Linear', 'Quadratic', 'Logarithmic', 'Exponential', 'Power']
    r2_data = {corr_type: [] for corr_type in correlation_types}
    
    for position, result in position_results.items():
        positions.append(position)
        correlations = result['correlations']
        
        for corr_type in correlation_types:
            r2_value = correlations[corr_type]['r2'] if correlations[corr_type]['r2'] is not None else 0
            r2_data[corr_type].append(r2_value)
    
    # Create comparison chart
    fig, ax = plt.subplots(figsize=(12, 8))
    
    x = np.arange(len(positions))
    width = 0.15
    
    colors = ['blue', 'red', 'green', 'orange', 'purple']
    
    for i, (corr_type, r2_values) in enumerate(r2_data.items()):
        ax.bar(x + i * width, r2_values, width, label=corr_type, color=colors[i], alpha=0.8)
    
    ax.set_xlabel('Position')
    ax.set_ylabel('R-squared Value')
    ax.set_title('R-squared Comparison by Position and Correlation Type')
    ax.set_xticks(x + width * 2)
    ax.set_xticklabels(positions)
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for i, (corr_type, r2_values) in enumerate(r2_data.items()):
        for j, value in enumerate(r2_values):
            if value > 0:
                ax.text(j + i * width, value + 0.01, f'{value:.3f}', 
                       ha='center', va='bottom', fontsize=8, fontweight='bold')
    
    plt.tight_layout()
    
    # Save the plot
    output_path = '/Users/mightenyip/Documents/GitHub/yfd-py-test/plots_images/r_squared_comparison.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ R-squared comparison saved to: {output_path}")
    
    plt.show()

def generate_summary_report(position_results):
    """Generate a comprehensive summary report."""
    print(f"\n📈 CORRELATION TYPES SUMMARY REPORT")
    print("=" * 60)
    
    for position, result in position_results.items():
        print(f"\n🏈 {position} Position:")
        print(f"   Players: {len(result['data'])}")
        print(f"   Best Fit: {result['best_fit'][0]} (R² = {result['best_fit'][1]['r2']:.4f})")
        
        correlations = result['correlations']
        print(f"   📊 All Correlation Types:")
        for corr_type, data in correlations.items():
            if data['r2'] is not None:
                print(f"      {corr_type:<12}: R² = {data['r2']:.4f}")
    
    # Overall best correlations by type
    print(f"\n🏆 BEST CORRELATIONS BY TYPE:")
    correlation_types = ['Linear', 'Quadratic', 'Logarithmic', 'Exponential', 'Power']
    
    for corr_type in correlation_types:
        best_r2 = 0
        best_position = ""
        for position, result in position_results.items():
            r2_value = result['correlations'][corr_type]['r2']
            if r2_value is not None and r2_value > best_r2:
                best_r2 = r2_value
                best_position = position
        
        if best_r2 > 0:
            print(f"   {corr_type:<12}: {best_position} (R² = {best_r2:.4f})")

def main():
    """Main analysis function."""
    print("🏈 POSITION-SPECIFIC CORRELATION TYPES ANALYSIS")
    print("=" * 60)
    print("Testing Linear, Quadratic, Logarithmic, Exponential, and Power correlations")
    print("=" * 60)
    
    # Load and clean data
    df = load_and_clean_data()
    
    # Analyze each position
    position_results = {}
    positions = ['QB', 'RB', 'WR', 'TE', 'DEF']  # Order: QB first, DEF last
    
    for position in positions:
        if position in df['position'].unique():
            result = analyze_position_correlations(df, position)
            if result:
                position_results[position] = result
    
    # Create visualizations
    create_correlation_visualizations(position_results)
    create_r_squared_comparison(position_results)
    
    # Generate summary report
    generate_summary_report(position_results)
    
    print(f"\n🎉 Analysis Complete!")
    print(f"📁 Results saved to plots_images/")

if __name__ == "__main__":
    main()

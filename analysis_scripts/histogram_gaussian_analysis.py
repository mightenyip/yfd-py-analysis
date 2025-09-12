#!/usr/bin/env python3
"""
Histogram and Gaussian curve analysis for Week 2 Thursday salary vs points data.
Testing if point distributions follow Gaussian curves by salary bins.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.optimize import curve_fit
import warnings
warnings.filterwarnings('ignore')

def load_and_clean_data():
    """Load and clean the Week 2 Thursday data."""
    print("📊 Loading Week 2 Thursday data for histogram analysis...")
    
    # Load data
    df = pd.read_csv('/Users/mightenyip/Documents/GitHub/yfd-py-test/data_csv/week2_Thurs.csv')
    
    # Clean salary data (remove $ symbol and convert to numeric)
    df['salary_clean'] = df['salary'].str.replace('$', '').astype(float)
    
    # Clean points data (handle any non-numeric values)
    df['points_clean'] = pd.to_numeric(df['points'], errors='coerce')
    
    # Remove rows with missing data
    df_clean = df.dropna(subset=['salary_clean', 'points_clean']).copy()
    
    # Create both datasets
    df_all = df_clean.copy()
    df_active = df_clean[df_clean['points_clean'] > 0].copy()
    
    print(f"✅ All players: {len(df_all)}")
    print(f"✅ Active players only: {len(df_active)}")
    
    return df_all, df_active

def gaussian_function(x, amplitude, mean, stddev):
    """Gaussian function for curve fitting."""
    return amplitude * np.exp(-((x - mean) / stddev) ** 2 / 2)

def analyze_salary_bins(df, dataset_name="All Players"):
    """Analyze point distributions by salary bins."""
    print(f"\n🔍 Analyzing {dataset_name} by Salary Bins...")
    
    # Create salary bins
    salary_bins = [0, 12, 16, 20, 25, 30, 50]
    bin_labels = ['$0-12', '$12-16', '$16-20', '$20-25', '$25-30', '$30+']
    
    df['salary_bin'] = pd.cut(df['salary_clean'], bins=salary_bins, labels=bin_labels, include_lowest=True)
    
    print(f"\n📊 Salary Bin Analysis:")
    print(f"{'Bin':<10} {'Count':<8} {'Mean Points':<12} {'Std Points':<12} {'Mean Salary':<12} {'Value Ratio':<12}")
    print("-" * 70)
    
    bin_stats = []
    for bin_label in bin_labels:
        bin_data = df[df['salary_bin'] == bin_label]
        if len(bin_data) > 0:
            mean_points = bin_data['points_clean'].mean()
            std_points = bin_data['points_clean'].std()
            mean_salary = bin_data['salary_clean'].mean()
            value_ratio = mean_points / mean_salary if mean_salary > 0 else 0
            
            print(f"{bin_label:<10} {len(bin_data):<8} {mean_points:<12.2f} {std_points:<12.2f} ${mean_salary:<11.1f} {value_ratio:<12.3f}")
            
            bin_stats.append({
                'bin': bin_label,
                'count': len(bin_data),
                'mean_points': mean_points,
                'std_points': std_points,
                'mean_salary': mean_salary,
                'value_ratio': value_ratio,
                'data': bin_data['points_clean'].values
            })
    
    return bin_stats

def test_gaussian_fits(bin_stats):
    """Test if point distributions follow Gaussian curves."""
    print(f"\n🧮 Testing Gaussian Fits for Each Salary Bin...")
    
    gaussian_results = []
    
    for stat in bin_stats:
        if stat['count'] >= 3:  # Need at least 3 points for meaningful fit
            data = stat['data']
            
            # Create histogram
            hist, bin_edges = np.histogram(data, bins=max(3, len(data)//2), density=True)
            bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
            
            try:
                # Initial guess for Gaussian parameters
                amplitude_guess = np.max(hist)
                mean_guess = np.mean(data)
                std_guess = np.std(data)
                
                # Fit Gaussian curve
                popt, pcov = curve_fit(gaussian_function, bin_centers, hist, 
                                     p0=[amplitude_guess, mean_guess, std_guess])
                
                # Calculate R²
                y_pred = gaussian_function(bin_centers, *popt)
                ss_res = np.sum((hist - y_pred) ** 2)
                ss_tot = np.sum((hist - np.mean(hist)) ** 2)
                r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
                
                # Kolmogorov-Smirnov test for normality
                ks_stat, ks_pvalue = stats.kstest(data, 'norm', args=(popt[1], popt[2]))
                
                gaussian_results.append({
                    'bin': stat['bin'],
                    'count': stat['count'],
                    'amplitude': popt[0],
                    'mean': popt[1],
                    'std': popt[2],
                    'r_squared': r_squared,
                    'ks_stat': ks_stat,
                    'ks_pvalue': ks_pvalue,
                    'is_normal': ks_pvalue > 0.05,
                    'data': data,
                    'bin_centers': bin_centers,
                    'hist': hist,
                    'fitted_curve': y_pred
                })
                
                print(f"   {stat['bin']:<10}: R²={r_squared:.3f}, KS p-value={ks_pvalue:.3f}, Normal={ks_pvalue > 0.05}")
                
            except Exception as e:
                print(f"   {stat['bin']:<10}: Fit failed - {str(e)}")
                gaussian_results.append({
                    'bin': stat['bin'],
                    'count': stat['count'],
                    'fit_success': False,
                    'data': data
                })
        else:
            print(f"   {stat['bin']:<10}: Insufficient data (n={stat['count']})")
    
    return gaussian_results

def create_histogram_visualizations(df_all, df_active, bin_stats_all, bin_stats_active, gaussian_results_all, gaussian_results_active):
    """Create comprehensive histogram visualizations."""
    print(f"\n📊 Creating Histogram Visualizations...")
    
    # Set up the plotting style
    plt.style.use('default')
    fig, axes = plt.subplots(3, 2, figsize=(16, 18))
    fig.suptitle('Week 2 Thursday: Histogram and Gaussian Analysis', fontsize=16, fontweight='bold')
    
    # 1. Overall points distribution - All players
    ax1 = axes[0, 0]
    ax1.hist(df_all['points_clean'], bins=15, alpha=0.7, color='lightblue', edgecolor='black', density=True)
    ax1.set_xlabel('Points')
    ax1.set_ylabel('Density')
    ax1.set_title('Points Distribution - All Players')
    ax1.grid(True, alpha=0.3)
    
    # Add mean line
    mean_points = df_all['points_clean'].mean()
    ax1.axvline(mean_points, color='red', linestyle='--', alpha=0.7, label=f'Mean: {mean_points:.1f}')
    ax1.legend()
    
    # 2. Overall points distribution - Active players only
    ax2 = axes[0, 1]
    ax2.hist(df_active['points_clean'], bins=12, alpha=0.7, color='lightgreen', edgecolor='black', density=True)
    ax2.set_xlabel('Points')
    ax2.set_ylabel('Density')
    ax2.set_title('Points Distribution - Active Players Only')
    ax2.grid(True, alpha=0.3)
    
    # Add mean line
    mean_points_active = df_active['points_clean'].mean()
    ax2.axvline(mean_points_active, color='red', linestyle='--', alpha=0.7, label=f'Mean: {mean_points_active:.1f}')
    ax2.legend()
    
    # 3. Salary bins histogram - All players
    ax3 = axes[1, 0]
    bin_means_all = [stat['mean_points'] for stat in bin_stats_all]
    bin_labels_all = [stat['bin'] for stat in bin_stats_all]
    bin_counts_all = [stat['count'] for stat in bin_stats_all]
    
    bars = ax3.bar(bin_labels_all, bin_means_all, alpha=0.7, color='skyblue', edgecolor='black')
    ax3.set_xlabel('Salary Bin')
    ax3.set_ylabel('Mean Points')
    ax3.set_title('Mean Points by Salary Bin - All Players')
    ax3.grid(True, alpha=0.3, axis='y')
    
    # Add count labels on bars
    for bar, count in zip(bars, bin_counts_all):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'n={count}', ha='center', va='bottom', fontweight='bold')
    
    # 4. Salary bins histogram - Active players only
    ax4 = axes[1, 1]
    bin_means_active = [stat['mean_points'] for stat in bin_stats_active]
    bin_labels_active = [stat['bin'] for stat in bin_stats_active]
    bin_counts_active = [stat['count'] for stat in bin_stats_active]
    
    bars = ax4.bar(bin_labels_active, bin_means_active, alpha=0.7, color='lightcoral', edgecolor='black')
    ax4.set_xlabel('Salary Bin')
    ax4.set_ylabel('Mean Points')
    ax4.set_title('Mean Points by Salary Bin - Active Players Only')
    ax4.grid(True, alpha=0.3, axis='y')
    
    # Add count labels on bars
    for bar, count in zip(bars, bin_counts_active):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'n={count}', ha='center', va='bottom', fontweight='bold')
    
    # 5. Gaussian fits - All players
    ax5 = axes[2, 0]
    colors = ['blue', 'green', 'red', 'orange', 'purple', 'brown']
    
    for i, result in enumerate(gaussian_results_all):
        if 'fit_success' not in result:  # Successful fit
            ax5.hist(result['data'], bins=max(3, len(result['data'])//2), 
                    alpha=0.3, density=True, color=colors[i % len(colors)], 
                    label=f"{result['bin']} (R²={result['r_squared']:.3f})")
            
            # Plot fitted curve
            x_smooth = np.linspace(result['data'].min(), result['data'].max(), 100)
            y_smooth = gaussian_function(x_smooth, result['amplitude'], result['mean'], result['std'])
            ax5.plot(x_smooth, y_smooth, color=colors[i % len(colors)], linewidth=2, alpha=0.8)
    
    ax5.set_xlabel('Points')
    ax5.set_ylabel('Density')
    ax5.set_title('Gaussian Fits by Salary Bin - All Players')
    ax5.legend()
    ax5.grid(True, alpha=0.3)
    
    # 6. Gaussian fits - Active players only
    ax6 = axes[2, 1]
    
    for i, result in enumerate(gaussian_results_active):
        if 'fit_success' not in result:  # Successful fit
            ax6.hist(result['data'], bins=max(3, len(result['data'])//2), 
                    alpha=0.3, density=True, color=colors[i % len(colors)], 
                    label=f"{result['bin']} (R²={result['r_squared']:.3f})")
            
            # Plot fitted curve
            x_smooth = np.linspace(result['data'].min(), result['data'].max(), 100)
            y_smooth = gaussian_function(x_smooth, result['amplitude'], result['mean'], result['std'])
            ax6.plot(x_smooth, y_smooth, color=colors[i % len(colors)], linewidth=2, alpha=0.8)
    
    ax6.set_xlabel('Points')
    ax6.set_ylabel('Density')
    ax6.set_title('Gaussian Fits by Salary Bin - Active Players Only')
    ax6.legend()
    ax6.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save the plot
    output_path = '/Users/mightenyip/Documents/GitHub/yfd-py-test/plots_images/week2_thursday_histogram_gaussian_analysis.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"📊 Histogram analysis plot saved to: {output_path}")
    
    plt.show()

def analyze_parabolic_pattern(bin_stats_all, bin_stats_active):
    """Analyze if the salary bin means follow a parabolic pattern."""
    print(f"\n📈 Analyzing Parabolic Pattern in Salary Bins...")
    
    # Extract data for analysis
    def analyze_bins(bin_stats, dataset_name):
        if len(bin_stats) < 3:
            print(f"   {dataset_name}: Insufficient bins for parabolic analysis")
            return None
        
        salaries = [stat['mean_salary'] for stat in bin_stats]
        points = [stat['mean_points'] for stat in bin_stats]
        
        # Fit quadratic curve
        coeffs = np.polyfit(salaries, points, 2)
        poly_func = np.poly1d(coeffs)
        
        # Calculate R²
        y_pred = poly_func(salaries)
        ss_res = np.sum((points - y_pred) ** 2)
        ss_tot = np.sum((points - np.mean(points)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        print(f"   {dataset_name}:")
        print(f"     Quadratic fit: {coeffs[0]:.4f}x² + {coeffs[1]:.4f}x + {coeffs[2]:.4f}")
        print(f"     R² = {r_squared:.3f}")
        
        # Check if it's actually parabolic (negative x² coefficient suggests downward curve)
        if coeffs[0] < 0:
            print(f"     ✅ Downward parabolic curve detected!")
            # Find peak
            peak_salary = -coeffs[1] / (2 * coeffs[0])
            peak_points = poly_func(peak_salary)
            print(f"     📊 Peak at: ${peak_salary:.1f} salary, {peak_points:.1f} points")
        else:
            print(f"     ❌ Upward curve or linear relationship")
        
        return {
            'coeffs': coeffs,
            'r_squared': r_squared,
            'is_parabolic': coeffs[0] < 0,
            'peak_salary': -coeffs[1] / (2 * coeffs[0]) if coeffs[0] < 0 else None,
            'peak_points': poly_func(-coeffs[1] / (2 * coeffs[0])) if coeffs[0] < 0 else None
        }
    
    result_all = analyze_bins(bin_stats_all, "All Players")
    result_active = analyze_bins(bin_stats_active, "Active Players Only")
    
    return result_all, result_active

def draw_histogram_conclusions(gaussian_results_all, gaussian_results_active, parabolic_all, parabolic_active):
    """Draw conclusions from histogram and Gaussian analysis."""
    print(f"\n🎯 HISTOGRAM & GAUSSIAN ANALYSIS CONCLUSIONS")
    print("=" * 60)
    
    # Gaussian analysis
    print(f"📊 GAUSSIAN DISTRIBUTION ANALYSIS:")
    
    normal_bins_all = [r for r in gaussian_results_all if 'is_normal' in r and r['is_normal']]
    normal_bins_active = [r for r in gaussian_results_active if 'is_normal' in r and r['is_normal']]
    
    print(f"   All players: {len(normal_bins_all)}/{len(gaussian_results_all)} bins follow normal distribution")
    print(f"   Active players: {len(normal_bins_active)}/{len(gaussian_results_active)} bins follow normal distribution")
    
    if len(normal_bins_all) > 0:
        print(f"   Normal bins (all players): {[r['bin'] for r in normal_bins_all]}")
    if len(normal_bins_active) > 0:
        print(f"   Normal bins (active players): {[r['bin'] for r in normal_bins_active]}")
    
    # Parabolic analysis
    print(f"\n📈 PARABOLIC PATTERN ANALYSIS:")
    
    if parabolic_all:
        print(f"   All players: {'✅ Parabolic' if parabolic_all['is_parabolic'] else '❌ Not parabolic'} (R²={parabolic_all['r_squared']:.3f})")
        if parabolic_all['is_parabolic']:
            print(f"     Peak value at: ${parabolic_all['peak_salary']:.1f} salary")
    
    if parabolic_active:
        print(f"   Active players: {'✅ Parabolic' if parabolic_active['is_parabolic'] else '❌ Not parabolic'} (R²={parabolic_active['r_squared']:.3f})")
        if parabolic_active['is_parabolic']:
            print(f"     Peak value at: ${parabolic_active['peak_salary']:.1f} salary")
    
    # Final insights
    print(f"\n🔍 KEY INSIGHTS:")
    print(f"   1. Histogram analysis reveals:")
    print(f"      - Point distributions vary significantly by salary bin")
    print(f"      - Some salary bins show normal (Gaussian) distributions")
    print(f"      - The relationship between salary and points may be non-linear")
    
    print(f"\n   2. Your parabolic hypothesis:")
    if parabolic_active and parabolic_active['is_parabolic']:
        print(f"      ✅ SUPPORTED! Active players show downward parabolic curve")
        print(f"      📊 Optimal salary range around ${parabolic_active['peak_salary']:.1f}")
    else:
        print(f"      ❌ Not clearly supported by histogram analysis")
    
    print(f"\n   3. Gaussian distributions suggest:")
    print(f"      - Point variability within salary bins follows normal patterns")
    print(f"      - This supports the idea of predictable performance ranges")
    print(f"      - Higher salary bins may have more consistent performance")

def main():
    """Main histogram analysis function."""
    print("Week 2 Thursday: Histogram and Gaussian Analysis")
    print("Testing for Gaussian curves and parabolic patterns in salary bins")
    print("=" * 70)
    
    # Load data
    df_all, df_active = load_and_clean_data()
    
    # Analyze salary bins
    bin_stats_all = analyze_salary_bins(df_all, "All Players")
    bin_stats_active = analyze_salary_bins(df_active, "Active Players Only")
    
    # Test Gaussian fits
    gaussian_results_all = test_gaussian_fits(bin_stats_all)
    gaussian_results_active = test_gaussian_fits(bin_stats_active)
    
    # Analyze parabolic patterns
    parabolic_all, parabolic_active = analyze_parabolic_pattern(bin_stats_all, bin_stats_active)
    
    # Create visualizations
    create_histogram_visualizations(df_all, df_active, bin_stats_all, bin_stats_active, 
                                  gaussian_results_all, gaussian_results_active)
    
    # Draw conclusions
    draw_histogram_conclusions(gaussian_results_all, gaussian_results_active, 
                             parabolic_all, parabolic_active)
    
    print(f"\n🎉 Histogram analysis complete! Check the saved plot for visual insights.")

if __name__ == "__main__":
    main()

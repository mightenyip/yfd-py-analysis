#!/usr/bin/env python3
"""
Positional analysis of salary vs points relationship, excluding 0-point players.
This script analyzes the relationship by position (QB, RB, WR, TE, DEF, K) and compares
Week 1, Week 2 Sunday, and Combined datasets.
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

def load_and_clean_data():
    """Load and clean all datasets, removing 0-point players."""
    print("📊 Loading datasets and removing 0-point players...")
    
    datasets = {}
    
    # Week 1 data
    try:
        week1_df = pd.read_csv('data_csv/yahoo_daily_fantasy_2025_week1_completed_page.csv')
        week1_df['salary_clean'] = week1_df['salary'].str.replace('$', '').astype(float)
        week1_df['points_clean'] = pd.to_numeric(week1_df['points'], errors='coerce')
        week1_df = week1_df.dropna(subset=['salary_clean', 'points_clean'])
        week1_active = week1_df[week1_df['points_clean'] > 0].copy()  # Remove 0-point players
        datasets['Week 1'] = week1_active
        print(f"   Week 1: {len(week1_active)} active players (removed {len(week1_df) - len(week1_active)} zero-point players)")
    except Exception as e:
        print(f"   Week 1: Error loading - {e}")
    
    # Week 2 Sunday data
    try:
        week2_sun_df = pd.read_csv('data_csv/week2_Sunday.csv')
        week2_sun_df['salary_clean'] = week2_sun_df['salary'].str.replace('$', '').astype(float)
        week2_sun_df['points_clean'] = pd.to_numeric(week2_sun_df['points'], errors='coerce')
        week2_sun_df = week2_sun_df.dropna(subset=['salary_clean', 'points_clean'])
        week2_sun_active = week2_sun_df[week2_sun_df['points_clean'] > 0].copy()  # Remove 0-point players
        datasets['Week 2 Sunday'] = week2_sun_active
        print(f"   Week 2 Sunday: {len(week2_sun_active)} active players (removed {len(week2_sun_df) - len(week2_sun_active)} zero-point players)")
    except Exception as e:
        print(f"   Week 2 Sunday: Error loading - {e}")
    
    # Combined dataset
    if 'Week 1' in datasets and 'Week 2 Sunday' in datasets:
        combined_df = pd.concat([datasets['Week 1'], datasets['Week 2 Sunday']], ignore_index=True)
        datasets['Combined'] = combined_df
        print(f"   Combined: {len(combined_df)} active players")
    
    return datasets

def analyze_position(df, position, dataset_name):
    """Analyze salary vs points relationship for a specific position."""
    pos_data = df[df['position'] == position].copy()
    
    if len(pos_data) < 3:  # Need at least 3 points for meaningful analysis
        return None
    
    X = pos_data['salary_clean'].values.reshape(-1, 1)
    y = pos_data['points_clean'].values
    
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
    pos_data['salary_bin'] = pd.cut(pos_data['salary_clean'], 
                                   bins=[0, 15, 20, 25, 30, 35, 40], 
                                   labels=['$10-15', '$15-20', '$20-25', '$25-30', '$30-35', '$35-40'])
    
    value_analysis = pos_data.groupby('salary_bin').agg({
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
        'position': position,
        'dataset': dataset_name,
        'n_players': len(pos_data),
        'correlation': correlation,
        'r_squared': correlation**2,
        'p_value': p_value,
        'models': models,
        'best_range': best_range,
        'best_value': best_value,
        'data': pos_data,
        'value_analysis': value_analysis
    }

def create_positional_analysis_plot(all_results):
    """Create comprehensive positional analysis plots."""
    print("\n📊 Creating positional analysis visualizations...")
    
    # Get unique positions and datasets
    positions = sorted(list(set([r['position'] for r in all_results if r is not None])))
    datasets = sorted(list(set([r['dataset'] for r in all_results if r is not None])))
    
    # Create subplots
    n_positions = len(positions)
    n_datasets = len(datasets)
    
    fig, axes = plt.subplots(n_positions, n_datasets, figsize=(6*n_datasets, 5*n_positions))
    if n_positions == 1:
        axes = axes.reshape(1, -1)
    if n_datasets == 1:
        axes = axes.reshape(-1, 1)
    
    fig.suptitle('Positional Analysis: Salary vs Points (No Zero-Point Players)', fontsize=16, fontweight='bold')
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
    
    for i, position in enumerate(positions):
        for j, dataset in enumerate(datasets):
            ax = axes[i, j]
            
            # Find result for this position and dataset
            result = next((r for r in all_results if r and r['position'] == position and r['dataset'] == dataset), None)
            
            if result is None or result['n_players'] < 3:
                ax.text(0.5, 0.5, f'Insufficient data\n(n < 3)', 
                       transform=ax.transAxes, ha='center', va='center', fontsize=12)
                ax.set_title(f'{position} - {dataset}\n(No data)')
                continue
            
            df = result['data']
            X = df['salary_clean'].values.reshape(-1, 1)
            y = df['points_clean'].values
            
            # Scatter plot
            ax.scatter(df['salary_clean'], df['points_clean'], 
                      alpha=0.7, s=50, c=colors[j % len(colors)], edgecolors='black', linewidth=0.5)
            
            # Add regression lines
            sort_idx = np.argsort(X.flatten())
            
            # Linear
            linear_model = LinearRegression()
            linear_model.fit(X, y)
            linear_pred = linear_model.predict(X)
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
            ax.set_title(f'{position} - {dataset}\n(n={result["n_players"]}, r={result["correlation"]:.3f}, R²={result["r_squared"]:.3f})')
            ax.legend(fontsize=8)
            ax.grid(True, alpha=0.3)
            
            # Add text box with key stats
            textstr = f'Best Value: {result["best_range"]}\n({result["best_value"]:.3f} pts/$)'
            props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
            ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=9,
                    verticalalignment='top', bbox=props)
    
    plt.tight_layout()
    plt.savefig('plots_images/positional_analysis_no_zeros.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("   ✅ Saved: plots_images/positional_analysis_no_zeros.png")

def create_positional_summary_table(all_results):
    """Create a summary table of positional analysis."""
    print("\n📋 POSITIONAL ANALYSIS SUMMARY TABLE")
    print("=" * 100)
    print(f"{'Position':<8} {'Dataset':<15} {'Players':<8} {'Correlation':<12} {'R²':<8} {'Best Model':<12} {'Best Value':<15}")
    print("-" * 100)
    
    # Group results by position
    positions = sorted(list(set([r['position'] for r in all_results if r is not None])))
    datasets = sorted(list(set([r['dataset'] for r in all_results if r is not None])))
    
    for position in positions:
        for dataset in datasets:
            result = next((r for r in all_results if r and r['position'] == position and r['dataset'] == dataset), None)
            
            if result is None or result['n_players'] < 3:
                print(f"{position:<8} {dataset:<15} {'<3':<8} {'N/A':<12} {'N/A':<8} {'N/A':<12} {'N/A':<15}")
            else:
                best_model = max(result['models'].keys(), key=lambda k: result['models'][k])
                best_r2 = result['models'][best_model]
                print(f"{position:<8} {dataset:<15} {result['n_players']:<8} {result['correlation']:<12.4f} "
                      f"{result['r_squared']:<8.4f} {best_model:<12} {result['best_range']} ({result['best_value']:.3f})")
    
    print("=" * 100)

def create_positional_correlation_heatmap(all_results):
    """Create a heatmap showing correlations by position and dataset."""
    print("\n📊 Creating positional correlation heatmap...")
    
    positions = sorted(list(set([r['position'] for r in all_results if r is not None])))
    datasets = sorted(list(set([r['dataset'] for r in all_results if r is not None])))
    
    # Create correlation matrix
    corr_matrix = np.zeros((len(positions), len(datasets)))
    
    for i, position in enumerate(positions):
        for j, dataset in enumerate(datasets):
            result = next((r for r in all_results if r and r['position'] == position and r['dataset'] == dataset), None)
            if result is not None and result['n_players'] >= 3:
                corr_matrix[i, j] = result['correlation']
            else:
                corr_matrix[i, j] = np.nan
    
    # Create heatmap
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr_matrix, 
                xticklabels=datasets, 
                yticklabels=positions,
                annot=True, 
                fmt='.3f', 
                cmap='RdYlBu_r', 
                center=0,
                cbar_kws={'label': 'Correlation (r)'})
    
    plt.title('Positional Correlation Heatmap: Salary vs Points\n(No Zero-Point Players)', fontsize=14, fontweight='bold')
    plt.xlabel('Dataset')
    plt.ylabel('Position')
    plt.tight_layout()
    plt.savefig('plots_images/positional_correlation_heatmap.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("   ✅ Saved: plots_images/positional_correlation_heatmap.png")

def analyze_positional_insights(all_results):
    """Analyze key insights from positional data."""
    print("\n🔍 POSITIONAL INSIGHTS ANALYSIS")
    print("=" * 60)
    
    # Group by position
    position_insights = {}
    positions = sorted(list(set([r['position'] for r in all_results if r is not None])))
    
    for position in positions:
        pos_results = [r for r in all_results if r and r['position'] == position and r['n_players'] >= 3]
        
        if len(pos_results) == 0:
            continue
        
        position_insights[position] = {
            'total_players': sum(r['n_players'] for r in pos_results),
            'avg_correlation': np.mean([r['correlation'] for r in pos_results]),
            'max_correlation': max([r['correlation'] for r in pos_results]),
            'min_correlation': min([r['correlation'] for r in pos_results]),
            'avg_r2': np.mean([r['r_squared'] for r in pos_results]),
            'best_dataset': max(pos_results, key=lambda x: abs(x['correlation']))['dataset'],
            'results': pos_results
        }
    
    # Print insights
    print(f"{'Position':<8} {'Total Players':<15} {'Avg Correlation':<15} {'Best Dataset':<15} {'Avg R²':<10}")
    print("-" * 70)
    
    for position, insights in position_insights.items():
        print(f"{position:<8} {insights['total_players']:<15} {insights['avg_correlation']:<15.4f} "
              f"{insights['best_dataset']:<15} {insights['avg_r2']:<10.4f}")
    
    # Find strongest and weakest positions
    if position_insights:
        strongest_pos = max(position_insights.keys(), key=lambda p: position_insights[p]['avg_correlation'])
        weakest_pos = min(position_insights.keys(), key=lambda p: position_insights[p]['avg_correlation'])
        
        print(f"\n🎯 KEY INSIGHTS:")
        print(f"   Strongest Position Correlation: {strongest_pos} (r = {position_insights[strongest_pos]['avg_correlation']:.4f})")
        print(f"   Weakest Position Correlation: {weakest_pos} (r = {position_insights[weakest_pos]['avg_correlation']:.4f})")
        
        # Find most consistent position
        most_consistent = min(position_insights.keys(), 
                            key=lambda p: position_insights[p]['max_correlation'] - position_insights[p]['min_correlation'])
        print(f"   Most Consistent Position: {most_consistent} (range: {position_insights[most_consistent]['min_correlation']:.3f} to {position_insights[most_consistent]['max_correlation']:.3f})")
        
        # Find most variable position
        most_variable = max(position_insights.keys(), 
                          key=lambda p: position_insights[p]['max_correlation'] - position_insights[p]['min_correlation'])
        print(f"   Most Variable Position: {most_variable} (range: {position_insights[most_variable]['min_correlation']:.3f} to {position_insights[most_variable]['max_correlation']:.3f})")

def main():
    """Main analysis function."""
    print("🔍 Positional Analysis: Salary vs Points (No Zero-Point Players)")
    print("=" * 70)
    
    # Load and clean data
    datasets = load_and_clean_data()
    
    # Analyze each position for each dataset
    all_results = []
    
    for dataset_name, df in datasets.items():
        print(f"\n📊 Analyzing {dataset_name}...")
        
        # Get unique positions
        positions = df['position'].unique()
        print(f"   Positions found: {sorted(positions)}")
        
        for position in positions:
            result = analyze_position(df, position, dataset_name)
            if result is not None:
                all_results.append(result)
                print(f"   {position}: {result['n_players']} players, r={result['correlation']:.4f}, R²={result['r_squared']:.4f}")
    
    # Create visualizations
    create_positional_analysis_plot(all_results)
    create_positional_correlation_heatmap(all_results)
    
    # Create summary
    create_positional_summary_table(all_results)
    analyze_positional_insights(all_results)
    
    print(f"\n📊 Visualizations saved:")
    print(f"   - plots_images/positional_analysis_no_zeros.png")
    print(f"   - plots_images/positional_correlation_heatmap.png")

if __name__ == "__main__":
    main()

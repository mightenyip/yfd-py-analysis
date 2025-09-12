#!/usr/bin/env python3
"""
Analysis of Week 2 Thursday salary vs points relationship.
Testing hypothesis: Parabolic function with players >$20 being sunk costs.
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
    
    print(f"✅ Loaded {len(df_clean)} players with complete data")
    print(f"📈 Salary range: ${df_clean['salary_clean'].min():.0f} - ${df_clean['salary_clean'].max():.0f}")
    print(f"📈 Points range: {df_clean['points_clean'].min():.1f} - {df_clean['points_clean'].max():.1f}")
    
    return df_clean

def explore_relationship(df):
    """Explore the salary vs points relationship."""
    print("\n🔍 Exploring Salary vs Points Relationship...")
    
    # Basic statistics
    print(f"\n📊 Basic Statistics:")
    print(f"   Correlation: {df['salary_clean'].corr(df['points_clean']):.3f}")
    print(f"   Mean salary: ${df['salary_clean'].mean():.1f}")
    print(f"   Mean points: {df['points_clean'].mean():.1f}")
    
    # Analyze by salary ranges
    print(f"\n📊 Performance by Salary Range:")
    salary_ranges = [
        (0, 15, "Budget ($0-15)"),
        (15, 20, "Mid-tier ($15-20)"),
        (20, 30, "High ($20-30)"),
        (30, 50, "Premium ($30+)")
    ]
    
    for min_sal, max_sal, label in salary_ranges:
        subset = df[(df['salary_clean'] >= min_sal) & (df['salary_clean'] < max_sal)]
        if len(subset) > 0:
            avg_points = subset['points_clean'].mean()
            avg_salary = subset['salary_clean'].mean()
            value_ratio = avg_points / avg_salary if avg_salary > 0 else 0
            print(f"   {label}: {len(subset)} players, Avg: {avg_points:.1f} pts (${avg_salary:.1f}), Value: {value_ratio:.3f} pts/$")
    
    return df

def fit_models(df):
    """Fit linear and parabolic models to test the hypothesis."""
    print("\n🧮 Fitting Models...")
    
    X = df['salary_clean'].values.reshape(-1, 1)
    y = df['points_clean'].values
    
    # Linear model
    linear_model = LinearRegression()
    linear_model.fit(X, y)
    y_pred_linear = linear_model.predict(X)
    r2_linear = r2_score(y, y_pred_linear)
    mse_linear = mean_squared_error(y, y_pred_linear)
    
    # Parabolic model (quadratic)
    poly_features = PolynomialFeatures(degree=2)
    X_poly = poly_features.fit_transform(X)
    poly_model = LinearRegression()
    poly_model.fit(X_poly, y)
    y_pred_poly = poly_model.predict(X_poly)
    r2_poly = r2_score(y, y_pred_poly)
    mse_poly = mean_squared_error(y, y_pred_poly)
    
    print(f"📈 Linear Model:")
    print(f"   R² = {r2_linear:.3f}")
    print(f"   MSE = {mse_linear:.3f}")
    print(f"   Slope = {linear_model.coef_[0]:.3f} points per $")
    
    print(f"📈 Parabolic Model:")
    print(f"   R² = {r2_poly:.3f}")
    print(f"   MSE = {mse_poly:.3f}")
    print(f"   Coefficients: {poly_model.coef_[1]:.3f}x + {poly_model.coef_[2]:.3f}x²")
    
    # Determine which model is better
    if r2_poly > r2_linear:
        print(f"✅ Parabolic model is better (ΔR² = {r2_poly - r2_linear:.3f})")
        better_model = "parabolic"
    else:
        print(f"✅ Linear model is better (ΔR² = {r2_linear - r2_poly:.3f})")
        better_model = "linear"
    
    return {
        'linear_model': linear_model,
        'poly_model': poly_model,
        'poly_features': poly_features,
        'y_pred_linear': y_pred_linear,
        'y_pred_poly': y_pred_poly,
        'r2_linear': r2_linear,
        'r2_poly': r2_poly,
        'better_model': better_model
    }

def analyze_high_salary_players(df, models):
    """Analyze players over $20 to test the sunk cost hypothesis."""
    print("\n💰 Analyzing High Salary Players (>$20)...")
    
    high_salary = df[df['salary_clean'] > 20].copy()
    
    if len(high_salary) == 0:
        print("❌ No players with salary >$20 found")
        return
    
    print(f"📊 Found {len(high_salary)} players with salary >$20:")
    
    # Calculate expected vs actual performance
    X_high = high_salary['salary_clean'].values.reshape(-1, 1)
    
    # Linear predictions
    y_pred_linear_high = models['linear_model'].predict(X_high)
    
    # Parabolic predictions
    X_poly_high = models['poly_features'].transform(X_high)
    y_pred_poly_high = models['poly_model'].predict(X_poly_high)
    
    high_salary['pred_linear'] = y_pred_linear_high
    high_salary['pred_poly'] = y_pred_poly_high
    high_salary['actual'] = high_salary['points_clean']
    
    # Calculate value metrics
    high_salary['value_ratio'] = high_salary['actual'] / high_salary['salary_clean']
    high_salary['linear_underperformance'] = high_salary['actual'] - high_salary['pred_linear']
    high_salary['poly_underperformance'] = high_salary['actual'] - high_salary['pred_poly']
    
    print(f"\n📋 High Salary Players Performance:")
    for _, row in high_salary.iterrows():
        print(f"   {row['player_name']:<20} | ${row['salary_clean']:>4.0f} | {row['actual']:>5.1f} pts | Value: {row['value_ratio']:>5.3f} | Underperf: {row['linear_underperformance']:>5.1f}")
    
    # Summary statistics
    avg_value = high_salary['value_ratio'].mean()
    avg_underperformance = high_salary['linear_underperformance'].mean()
    underperformers = len(high_salary[high_salary['linear_underperformance'] < 0])
    
    print(f"\n📊 High Salary Summary:")
    print(f"   Average value ratio: {avg_value:.3f} pts/$")
    print(f"   Average underperformance: {avg_underperformance:.1f} points")
    print(f"   Players underperforming: {underperformers}/{len(high_salary)} ({underperformers/len(high_salary)*100:.1f}%)")
    
    # Compare to lower salary players
    low_salary = df[df['salary_clean'] <= 20]
    if len(low_salary) > 0:
        low_avg_value = (low_salary['points_clean'] / low_salary['salary_clean']).mean()
        print(f"   Low salary avg value: {low_avg_value:.3f} pts/$")
        print(f"   Value difference: {low_avg_value - avg_value:.3f} pts/$")
        
        if low_avg_value > avg_value:
            print(f"✅ HYPOTHESIS SUPPORTED: Lower salary players provide better value!")
        else:
            print(f"❌ HYPOTHESIS NOT SUPPORTED: Higher salary players provide better value")
    
    return high_salary

def create_visualizations(df, models):
    """Create comprehensive visualizations."""
    print("\n📊 Creating Visualizations...")
    
    # Set up the plotting style
    plt.style.use('default')
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Week 2 Thursday: Salary vs Points Analysis', fontsize=16, fontweight='bold')
    
    # 1. Scatter plot with both models
    ax1 = axes[0, 0]
    ax1.scatter(df['salary_clean'], df['points_clean'], alpha=0.7, s=60, color='steelblue', edgecolors='black', linewidth=0.5)
    
    # Sort for smooth line plotting
    X_sorted = np.sort(df['salary_clean'].values)
    X_sorted_reshaped = X_sorted.reshape(-1, 1)
    
    # Linear model line
    y_linear_sorted = models['linear_model'].predict(X_sorted_reshaped)
    ax1.plot(X_sorted, y_linear_sorted, 'r-', linewidth=2, label=f'Linear (R²={models["r2_linear"]:.3f})')
    
    # Parabolic model line
    X_poly_sorted = models['poly_features'].transform(X_sorted_reshaped)
    y_poly_sorted = models['poly_model'].predict(X_poly_sorted)
    ax1.plot(X_sorted, y_poly_sorted, 'g-', linewidth=2, label=f'Parabolic (R²={models["r2_poly"]:.3f})')
    
    # Highlight high salary players
    high_salary = df[df['salary_clean'] > 20]
    if len(high_salary) > 0:
        ax1.scatter(high_salary['salary_clean'], high_salary['points_clean'], 
                   color='red', s=80, alpha=0.8, edgecolors='darkred', linewidth=1, 
                   label=f'High Salary >$20 (n={len(high_salary)})')
    
    ax1.set_xlabel('Salary ($)')
    ax1.set_ylabel('Points')
    ax1.set_title('Salary vs Points with Model Fits')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Value ratio (points per dollar)
    ax2 = axes[0, 1]
    df['value_ratio'] = df['points_clean'] / df['salary_clean']
    ax2.scatter(df['salary_clean'], df['value_ratio'], alpha=0.7, s=60, color='orange', edgecolors='black', linewidth=0.5)
    
    # Highlight high salary players
    if len(high_salary) > 0:
        high_salary['value_ratio'] = high_salary['points_clean'] / high_salary['salary_clean']
        ax2.scatter(high_salary['salary_clean'], high_salary['value_ratio'], 
                   color='red', s=80, alpha=0.8, edgecolors='darkred', linewidth=1)
    
    ax2.axhline(y=df['value_ratio'].mean(), color='red', linestyle='--', alpha=0.7, label=f'Mean Value: {df["value_ratio"].mean():.3f}')
    ax2.set_xlabel('Salary ($)')
    ax2.set_ylabel('Value Ratio (Points per $)')
    ax2.set_title('Value Efficiency by Salary')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. Residuals plot
    ax3 = axes[1, 0]
    residuals = df['points_clean'] - models['y_pred_linear']
    ax3.scatter(df['salary_clean'], residuals, alpha=0.7, s=60, color='purple', edgecolors='black', linewidth=0.5)
    ax3.axhline(y=0, color='red', linestyle='-', alpha=0.7)
    
    # Highlight high salary players
    if len(high_salary) > 0:
        high_residuals = high_salary['points_clean'] - models['linear_model'].predict(high_salary['salary_clean'].values.reshape(-1, 1))
        ax3.scatter(high_salary['salary_clean'], high_residuals, 
                   color='red', s=80, alpha=0.8, edgecolors='darkred', linewidth=1)
    
    ax3.set_xlabel('Salary ($)')
    ax3.set_ylabel('Residuals (Actual - Predicted)')
    ax3.set_title('Model Residuals')
    ax3.grid(True, alpha=0.3)
    
    # 4. Position analysis
    ax4 = axes[1, 1]
    position_stats = df.groupby('position').agg({
        'salary_clean': 'mean',
        'points_clean': 'mean',
        'player_name': 'count'
    }).round(2)
    position_stats['value_ratio'] = position_stats['points_clean'] / position_stats['salary_clean']
    
    bars = ax4.bar(position_stats.index, position_stats['value_ratio'], 
                   color=['skyblue', 'lightgreen', 'lightcoral', 'gold', 'plum'])
    ax4.set_xlabel('Position')
    ax4.set_ylabel('Average Value Ratio (Points per $)')
    ax4.set_title('Value Efficiency by Position')
    ax4.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for bar, value in zip(bars, position_stats['value_ratio']):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f'{value:.3f}', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    
    # Save the plot
    output_path = '/Users/mightenyip/Documents/GitHub/yfd-py-test/plots_images/week2_thursday_salary_analysis.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"📊 Plot saved to: {output_path}")
    
    plt.show()
    
    return position_stats

def draw_conclusions(df, models, high_salary_analysis, position_stats):
    """Draw final conclusions about the hypothesis."""
    print("\n🎯 FINAL CONCLUSIONS")
    print("=" * 60)
    
    # Model comparison
    print(f"📈 MODEL PERFORMANCE:")
    print(f"   Linear Model R²: {models['r2_linear']:.3f}")
    print(f"   Parabolic Model R²: {models['r2_poly']:.3f}")
    
    if models['better_model'] == 'parabolic':
        print(f"   ✅ PARABOLIC HYPOTHESIS SUPPORTED: Parabolic model fits better")
        improvement = models['r2_poly'] - models['r2_linear']
        print(f"   📊 Improvement: {improvement:.3f} R² points")
    else:
        print(f"   ❌ PARABOLIC HYPOTHESIS NOT SUPPORTED: Linear model fits better")
        improvement = models['r2_linear'] - models['r2_poly']
        print(f"   📊 Linear advantage: {improvement:.3f} R² points")
    
    # High salary analysis
    if len(high_salary_analysis) > 0:
        print(f"\n💰 HIGH SALARY ANALYSIS (>$20):")
        avg_high_value = high_salary_analysis['value_ratio'].mean()
        avg_low_value = (df[df['salary_clean'] <= 20]['points_clean'] / df[df['salary_clean'] <= 20]['salary_clean']).mean()
        
        print(f"   High salary avg value: {avg_high_value:.3f} pts/$")
        print(f"   Low salary avg value: {avg_low_value:.3f} pts/$")
        print(f"   Value difference: {avg_low_value - avg_high_value:.3f} pts/$")
        
        if avg_low_value > avg_high_value:
            print(f"   ✅ SUNK COST HYPOTHESIS SUPPORTED: Players >$20 provide worse value!")
        else:
            print(f"   ❌ SUNK COST HYPOTHESIS NOT SUPPORTED: Players >$20 provide better value")
        
        # Underperformance analysis
        underperformers = len(high_salary_analysis[high_salary_analysis['linear_underperformance'] < 0])
        print(f"   Underperforming high salary players: {underperformers}/{len(high_salary_analysis)} ({underperformers/len(high_salary_analysis)*100:.1f}%)")
    
    # Position insights
    print(f"\n🏈 POSITION INSIGHTS:")
    best_position = position_stats.loc[position_stats['value_ratio'].idxmax()]
    worst_position = position_stats.loc[position_stats['value_ratio'].idxmin()]
    print(f"   Best value position: {best_position.name} ({best_position['value_ratio']:.3f} pts/$)")
    print(f"   Worst value position: {worst_position.name} ({worst_position['value_ratio']:.3f} pts/$)")
    
    # Overall correlation
    correlation = df['salary_clean'].corr(df['points_clean'])
    print(f"\n📊 OVERALL RELATIONSHIP:")
    print(f"   Salary-Points correlation: {correlation:.3f}")
    if correlation > 0.5:
        print(f"   ✅ Strong positive relationship between salary and points")
    elif correlation > 0.3:
        print(f"   ⚠️ Moderate positive relationship")
    else:
        print(f"   ❌ Weak relationship - salary not strongly predictive of points")
    
    # Final recommendation
    print(f"\n🎯 RECOMMENDATION:")
    if models['better_model'] == 'parabolic' and len(high_salary_analysis) > 0 and avg_low_value > avg_high_value:
        print(f"   ✅ BOTH HYPOTHESES SUPPORTED!")
        print(f"   📈 Use parabolic model for predictions")
        print(f"   💰 Avoid players >$20 - they are sunk costs")
        print(f"   🎯 Focus on mid-tier players ($15-20) for best value")
    else:
        print(f"   ⚠️ Mixed results - hypotheses partially supported")
        print(f"   📊 Consider both linear and parabolic models")
        print(f"   💰 High salary players may still provide value in some cases")

def main():
    """Main analysis function."""
    print("Week 2 Thursday Salary vs Points Analysis")
    print("Testing Hypothesis: Parabolic function with >$20 players as sunk costs")
    print("=" * 70)
    
    # Load and clean data
    df = load_and_clean_data()
    
    # Explore relationship
    df = explore_relationship(df)
    
    # Fit models
    models = fit_models(df)
    
    # Analyze high salary players
    high_salary_analysis = analyze_high_salary_players(df, models)
    
    # Create visualizations
    position_stats = create_visualizations(df, models)
    
    # Draw conclusions
    draw_conclusions(df, models, high_salary_analysis, position_stats)
    
    print(f"\n🎉 Analysis complete! Check the saved plot for visual insights.")

if __name__ == "__main__":
    main()

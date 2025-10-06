#!/usr/bin/env python3
"""
Combined Weeks Position Analysis
Analyzes points/salary by position across all weeks (week1 through week5)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

def load_and_combine_data():
    """Load and combine all weekly data files"""
    data_dir = Path('/Users/mightenyip/Documents/GitHub/yfd-py-test/data_csv')
    
    # Define the files to load (all weekly data)
    weekly_files = [
        'week1_monday_correct.csv',
        'week2_Mon.csv', 'week2_Sunday.csv', 'week2_Thurs.csv',
        'week3_Mon.csv', 'week3_Sunday.csv', 'week3_Thurs.csv',
        'week4_Mon.csv', 'week4_Sunday_all_games.csv', 'week4_Sunday_complete.csv', 
        'week4_Sunday.csv', 'week4_Thurs.csv',
        'week5_Thurs.csv'
    ]
    
    all_data = []
    
    for file in weekly_files:
        file_path = data_dir / file
        if file_path.exists():
            try:
                df = pd.read_csv(file_path)
                # Add week and day information if not present
                if 'week' not in df.columns:
                    if 'week1' in file:
                        df['week'] = 'Week 1'
                    elif 'week2' in file:
                        df['week'] = 'Week 2'
                    elif 'week3' in file:
                        df['week'] = 'Week 3'
                    elif 'week4' in file:
                        df['week'] = 'Week 4'
                    elif 'week5' in file:
                        df['week'] = 'Week 5'
                
                if 'day' not in df.columns:
                    if 'Mon' in file:
                        df['day'] = 'Monday'
                    elif 'Sunday' in file:
                        df['day'] = 'Sunday'
                    elif 'Thurs' in file:
                        df['day'] = 'Thursday'
                    else:
                        df['day'] = 'Unknown'
                
                df['source_file'] = file
                all_data.append(df)
                print(f"Loaded {file}: {len(df)} records")
            except Exception as e:
                print(f"Error loading {file}: {e}")
        else:
            print(f"File not found: {file}")
    
    if not all_data:
        raise ValueError("No data files could be loaded")
    
    # Combine all data
    combined_df = pd.concat(all_data, ignore_index=True)
    print(f"\nTotal combined records: {len(combined_df)}")
    
    return combined_df

def clean_salary_data(df):
    """Clean and convert salary data"""
    # Remove $ symbol and convert to numeric
    df['salary_clean'] = df['salary'].astype(str).str.replace('$', '').str.replace(',', '')
    df['salary_clean'] = pd.to_numeric(df['salary_clean'], errors='coerce')
    
    # Convert points to numeric
    df['points_clean'] = pd.to_numeric(df['points'], errors='coerce')
    
    # Remove rows with missing salary or points
    df_clean = df.dropna(subset=['salary_clean', 'points_clean'])
    
    # Remove zero salary or points (likely inactive players)
    df_clean = df_clean[(df_clean['salary_clean'] > 0) & (df_clean['points_clean'] >= 0)]
    
    return df_clean

def remove_duplicates_and_inactive(df):
    """Remove duplicate players per week and filter inactive players"""
    print(f"Before deduplication: {len(df)} records")
    
    # Create a unique identifier for each player-week combination
    df['player_week_key'] = df['player_name'] + '_' + df['week'].astype(str)
    
    # Check for duplicates
    duplicates = df.duplicated(subset=['player_week_key'], keep=False)
    if duplicates.any():
        print(f"Found {duplicates.sum()} duplicate player-week combinations")
        duplicate_examples = df[duplicates].groupby('player_week_key').size().head()
        print("Example duplicates:")
        for key, count in duplicate_examples.items():
            print(f"  {key}: {count} records")
    
    # Remove duplicates - keep the first occurrence (highest points if sorted properly)
    df_deduped = df.drop_duplicates(subset=['player_week_key'], keep='first')
    print(f"After removing duplicates: {len(df_deduped)} records")
    
    # Filter out inactive players (0 points and very low salary or missing stats)
    # Consider a player inactive if they have 0 points AND either:
    # 1. Very low salary (likely inactive)
    # 2. Missing or empty stats
    # 3. Status indicators like "IR", "PUP", "SUSP", "O", "D", "Q"
    
    # Check for status indicators in player names
    status_indicators = ['IR', 'PUP', 'SUSP', 'O', 'D', 'Q']
    has_status = df_deduped['player_name'].str.contains('|'.join(status_indicators), case=False, na=False)
    
    # Check for empty or missing stats
    empty_stats = (df_deduped['stats'].isna() | 
                   df_deduped['stats'].str.strip().eq('') | 
                   df_deduped['stats'].str.strip().eq('—'))
    
    # Check for very low salary (likely inactive)
    very_low_salary = df_deduped['salary_clean'] <= 10
    
    # Inactive players are those with 0 points AND (status indicators OR empty stats OR very low salary)
    inactive_mask = ((df_deduped['points_clean'] == 0) & 
                     (has_status | empty_stats | very_low_salary))
    
    print(f"Identified {inactive_mask.sum()} inactive players to remove")
    
    # Show examples of inactive players being removed
    if inactive_mask.any():
        inactive_examples = df_deduped[inactive_mask][['player_name', 'position', 'salary_clean', 'points_clean', 'stats']].head(10)
        print("Examples of inactive players being removed:")
        for _, row in inactive_examples.iterrows():
            print(f"  {row['player_name']} ({row['position']}): ${row['salary_clean']} → {row['points_clean']} pts - '{row['stats']}'")
    
    # Remove inactive players
    df_active = df_deduped[~inactive_mask].copy()
    print(f"After removing inactive players: {len(df_active)} records")
    
    # Drop the temporary key column
    df_active = df_active.drop('player_week_key', axis=1)
    
    return df_active

def identify_high_performers(df):
    """Identify high-performing players (1-2 std dev above mean)"""
    # Calculate points per dollar first
    df['points_per_dollar'] = df['points_clean'] / df['salary_clean']
    
    # Calculate thresholds for high performers by position
    position_thresholds = {}
    for pos in df['position'].unique():
        pos_data = df[df['position'] == pos]
        mean_ppd = pos_data['points_per_dollar'].mean()
        std_ppd = pos_data['points_per_dollar'].std()
        
        # Define thresholds: 1 std dev and 2 std dev above mean
        threshold_1std = mean_ppd + std_ppd
        threshold_2std = mean_ppd + (2 * std_ppd)
        
        position_thresholds[pos] = {
            'mean': mean_ppd,
            'std': std_ppd,
            'threshold_1std': threshold_1std,
            'threshold_2std': threshold_2std
        }
    
    # Add performance categories
    df['performance_category'] = 'Average'
    df['std_devs_above_mean'] = 0.0
    
    for pos in df['position'].unique():
        pos_mask = df['position'] == pos
        pos_data = df[pos_mask]
        thresholds = position_thresholds[pos]
        
        # Calculate how many standard deviations above mean each player is
        std_devs = (pos_data['points_per_dollar'] - thresholds['mean']) / thresholds['std']
        df.loc[pos_mask, 'std_devs_above_mean'] = std_devs
        
        # Categorize players
        df.loc[pos_mask & (pos_data['points_per_dollar'] >= thresholds['threshold_2std']), 'performance_category'] = 'Elite (2+ std)'
        df.loc[pos_mask & (pos_data['points_per_dollar'] >= thresholds['threshold_1std']) & 
               (pos_data['points_per_dollar'] < thresholds['threshold_2std']), 'performance_category'] = 'High (1-2 std)'
        df.loc[pos_mask & (pos_data['points_per_dollar'] < thresholds['threshold_1std']), 'performance_category'] = 'Average/Below'
    
    return df, position_thresholds

def calculate_high_performer_metrics(df):
    """Calculate metrics for high-performing players"""
    # Overall position stats
    position_stats = df.groupby('position').agg({
        'points_clean': ['count', 'mean', 'median', 'std'],
        'salary_clean': ['mean', 'median', 'std'],
        'points_per_dollar': ['mean', 'median', 'std']
    }).round(3)
    
    # Flatten column names
    position_stats.columns = ['_'.join(col).strip() for col in position_stats.columns]
    position_stats = position_stats.reset_index()
    
    # High performer stats (1+ std dev above mean)
    high_performers = df[df['performance_category'].isin(['High (1-2 std)', 'Elite (2+ std)'])]
    
    if len(high_performers) > 0:
        high_performer_stats = high_performers.groupby('position').agg({
            'points_clean': ['count', 'mean', 'median', 'std'],
            'salary_clean': ['mean', 'median', 'std'],
            'points_per_dollar': ['mean', 'median', 'std']
        }).round(3)
        
        high_performer_stats.columns = ['hp_' + '_'.join(col).strip() for col in high_performer_stats.columns]
        high_performer_stats = high_performer_stats.reset_index()
        
        # Merge with overall stats
        position_stats = position_stats.merge(high_performer_stats, on='position', how='left')
    else:
        print("Warning: No high performers found")
    
    return position_stats, high_performers

def create_visualizations(df, position_stats, high_performers):
    """Create comprehensive visualizations focused on high performers"""
    plt.style.use('default')
    fig = plt.figure(figsize=(20, 16))
    
    # 1. High Performers vs Overall Average by Position
    plt.subplot(3, 3, 1)
    pos_order = position_stats.sort_values('points_per_dollar_mean', ascending=False)['position']
    
    # Overall average
    overall_avg = position_stats.set_index('position').loc[pos_order, 'points_per_dollar_mean']
    bars1 = plt.bar([x - 0.2 for x in range(len(pos_order))], overall_avg, 
                   width=0.4, label='Overall Average', alpha=0.7)
    
    # High performers average (if available)
    if 'hp_points_per_dollar_mean' in position_stats.columns:
        hp_avg = position_stats.set_index('position').loc[pos_order, 'hp_points_per_dollar_mean']
        bars2 = plt.bar([x + 0.2 for x in range(len(pos_order))], hp_avg, 
                       width=0.4, label='High Performers (1+ std)', alpha=0.9)
    
    plt.title('Points per Dollar: Overall vs High Performers', fontsize=14, fontweight='bold')
    plt.xlabel('Position')
    plt.ylabel('Points per Dollar')
    plt.xticks(range(len(pos_order)), pos_order, rotation=45)
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Add value labels
    for i, (bar1, bar2) in enumerate(zip(bars1, bars2)):
        plt.text(bar1.get_x() + bar1.get_width()/2., bar1.get_height() + 0.01,
                f'{bar1.get_height():.3f}', ha='center', va='bottom', fontsize=9)
        if 'hp_points_per_dollar_mean' in position_stats.columns:
            plt.text(bar2.get_x() + bar2.get_width()/2., bar2.get_height() + 0.01,
                    f'{bar2.get_height():.3f}', ha='center', va='bottom', fontsize=9)
    
    # 2. High Performers Distribution by Position
    plt.subplot(3, 3, 2)
    if len(high_performers) > 0:
        performance_counts = high_performers['position'].value_counts()
        plt.bar(performance_counts.index, performance_counts.values)
        plt.title('High Performers Count by Position', fontsize=14, fontweight='bold')
        plt.xlabel('Position')
        plt.ylabel('Number of High Performers')
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        
        # Add value labels
        for i, v in enumerate(performance_counts.values):
            plt.text(i, v + 0.1, str(v), ha='center', va='bottom', fontsize=10)
    else:
        plt.text(0.5, 0.5, 'No High Performers Found', ha='center', va='center', 
                transform=plt.gca().transAxes, fontsize=14)
        plt.title('High Performers Count by Position', fontsize=14, fontweight='bold')
    
    # 3. Performance Categories Distribution
    plt.subplot(3, 3, 3)
    category_counts = df['performance_category'].value_counts()
    colors = ['gold', 'orange', 'lightcoral']
    plt.pie(category_counts.values, labels=category_counts.index, autopct='%1.1f%%', 
            colors=colors[:len(category_counts)], startangle=90)
    plt.title('Player Performance Distribution', fontsize=14, fontweight='bold')
    
    # 4. Scatter Plot: Salary vs Points by Position
    plt.subplot(3, 3, 4)
    positions = df['position'].unique()
    colors = plt.cm.Set3(np.linspace(0, 1, len(positions)))
    
    for i, pos in enumerate(positions):
        pos_data = df[df['position'] == pos]
        plt.scatter(pos_data['salary_clean'], pos_data['points_clean'], 
                   label=pos, alpha=0.6, color=colors[i], s=30)
    
    plt.title('Salary vs Points by Position', fontsize=14, fontweight='bold')
    plt.xlabel('Salary ($)')
    plt.ylabel('Points')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    
    # 5. Points per Dollar Distribution by Position (Violin Plot)
    plt.subplot(3, 3, 5)
    df_violin = df[df['points_per_dollar'] <= df['points_per_dollar'].quantile(0.95)]  # Remove outliers
    sns.violinplot(data=df_violin, x='position', y='points_per_dollar')
    plt.title('Points per Dollar Distribution by Position', fontsize=14, fontweight='bold')
    plt.xlabel('Position')
    plt.ylabel('Points per Dollar')
    plt.xticks(rotation=45)
    
    # 6. Weekly Trends by Position
    plt.subplot(3, 3, 6)
    weekly_pos = df.groupby(['week', 'position'])['points_per_dollar'].mean().unstack()
    for pos in weekly_pos.columns:
        plt.plot(weekly_pos.index, weekly_pos[pos], marker='o', label=pos, linewidth=2)
    plt.title('Weekly Points per Dollar Trends by Position', fontsize=14, fontweight='bold')
    plt.xlabel('Week')
    plt.ylabel('Average Points per Dollar')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    
    # 7. Top Performers by Position (Top 10%)
    plt.subplot(3, 3, 7)
    top_performers = df.groupby('position').apply(
        lambda x: x.nlargest(max(1, len(x)//10), 'points_per_dollar')
    ).reset_index(drop=True)
    
    top_per_pos = top_performers.groupby('position')['points_per_dollar'].mean()
    bars = plt.bar(top_per_pos.index, top_per_pos.values)
    plt.title('Top 10% Performers: Points per Dollar by Position', fontsize=14, fontweight='bold')
    plt.xlabel('Position')
    plt.ylabel('Average Points per Dollar (Top 10%)')
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f'{height:.3f}', ha='center', va='bottom', fontsize=10)
    
    # 8. Position Count Distribution
    plt.subplot(3, 3, 8)
    pos_counts = df['position'].value_counts()
    plt.pie(pos_counts.values, labels=pos_counts.index, autopct='%1.1f%%', startangle=90)
    plt.title('Player Count by Position', fontsize=14, fontweight='bold')
    
    # 9. Salary vs Points per Dollar Heatmap
    plt.subplot(3, 3, 9)
    # Create salary bins
    df['salary_bin'] = pd.cut(df['salary_clean'], bins=5, labels=['Very Low', 'Low', 'Medium', 'High', 'Very High'])
    heatmap_data = df.groupby(['position', 'salary_bin'])['points_per_dollar'].mean().unstack()
    sns.heatmap(heatmap_data, annot=True, fmt='.3f', cmap='YlOrRd', cbar_kws={'label': 'Points per Dollar'})
    plt.title('Points per Dollar Heatmap: Position vs Salary Tier', fontsize=14, fontweight='bold')
    plt.xlabel('Salary Tier')
    plt.ylabel('Position')
    
    plt.tight_layout()
    plt.savefig('/Users/mightenyip/Documents/GitHub/yfd-py-test/plots_images/combined_weeks_position_analysis.png', 
                dpi=300, bbox_inches='tight')
    plt.show()

def print_summary_statistics(df, position_stats, high_performers, position_thresholds):
    """Print comprehensive summary statistics focused on high performers"""
    print("\n" + "="*80)
    print("HIGH PERFORMER ANALYSIS - COMBINED WEEKS (1-5)")
    print("="*80)
    
    print(f"\nTotal Players Analyzed: {len(df):,}")
    print(f"High Performers (1+ std dev above mean): {len(high_performers):,}")
    print(f"Date Range: {df['week'].min()} to {df['week'].max()}")
    print(f"Positions Included: {', '.join(sorted(df['position'].unique()))}")
    
    # Performance category breakdown
    print(f"\nPerformance Category Breakdown:")
    print("-" * 50)
    category_counts = df['performance_category'].value_counts()
    for category, count in category_counts.items():
        percentage = (count / len(df)) * 100
        print(f"{category:20}: {count:>3} players ({percentage:>5.1f}%)")
    
    print(f"\nHigh Performer Thresholds by Position:")
    print("-" * 50)
    for pos in sorted(df['position'].unique()):
        thresholds = position_thresholds[pos]
        pos_data = df[df['position'] == pos]
        hp_count = len(pos_data[pos_data['performance_category'].isin(['High (1-2 std)', 'Elite (2+ std)'])])
        print(f"{pos:>4}: Mean={thresholds['mean']:.3f}, 1std={thresholds['threshold_1std']:.3f}, "
              f"2std={thresholds['threshold_2std']:.3f} ({hp_count} high performers)")
    
    if len(high_performers) > 0:
        print(f"\nHigh Performers vs Overall Average:")
        print("-" * 50)
        print(f"{'Position':<6} {'Overall PPD':<12} {'High Perf PPD':<15} {'Improvement':<12}")
        print("-" * 50)
        
        for pos in sorted(df['position'].unique()):
            overall_ppd = df[df['position'] == pos]['points_per_dollar'].mean()
            hp_ppd = high_performers[high_performers['position'] == pos]['points_per_dollar'].mean()
            if not pd.isna(hp_ppd):
                improvement = ((hp_ppd - overall_ppd) / overall_ppd) * 100
                print(f"{pos:<6} {overall_ppd:<12.3f} {hp_ppd:<15.3f} {improvement:>+10.1f}%")
    
    print(f"\nTop 15 High Performers by Points per Dollar:")
    print("-" * 70)
    if len(high_performers) > 0:
        top_hp = high_performers.nlargest(15, 'points_per_dollar')[['player_name', 'position', 'salary_clean', 'points_clean', 'points_per_dollar', 'std_devs_above_mean']]
        for i, (_, player) in enumerate(top_hp.iterrows(), 1):
            print(f"{i:2}. {player['player_name']:20} ({player['position']:>2}) "
                  f"${player['salary_clean']:>3} → {player['points_clean']:>5.1f} pts "
                  f"({player['points_per_dollar']:.3f} pts/$, {player['std_devs_above_mean']:+.1f}σ)")
    else:
        print("No high performers found")
    
    print(f"\nElite Performers (2+ std dev above mean):")
    print("-" * 50)
    elite_performers = df[df['performance_category'] == 'Elite (2+ std)']
    if len(elite_performers) > 0:
        elite_sorted = elite_performers.sort_values('points_per_dollar', ascending=False)
        for i, (_, player) in enumerate(elite_sorted.iterrows(), 1):
            print(f"{i:2}. {player['player_name']:20} ({player['position']:>2}) "
                  f"${player['salary_clean']:>3} → {player['points_clean']:>5.1f} pts "
                  f"({player['points_per_dollar']:.3f} pts/$, {player['std_devs_above_mean']:+.1f}σ)")
    else:
        print("No elite performers found")
    
    print(f"\nPosition Efficiency Analysis (High Performers Only):")
    print("-" * 60)
    for pos in sorted(df['position'].unique()):
        pos_data = df[df['position'] == pos]
        hp_data = high_performers[high_performers['position'] == pos]
        
        if len(hp_data) > 0:
            print(f"{pos:>4}: {len(hp_data):>3} high performers, "
                  f"avg {hp_data['points_per_dollar'].mean():.3f} pts/$, "
                  f"salary range ${hp_data['salary_clean'].min():.0f}-${hp_data['salary_clean'].max():.0f}")
        else:
            print(f"{pos:>4}: No high performers found")

def main():
    """Main analysis function"""
    print("Loading and combining weekly data...")
    df = load_and_combine_data()
    
    print("Cleaning data...")
    df_clean = clean_salary_data(df)
    print(f"After cleaning: {len(df_clean)} records")
    
    print("Removing duplicates and inactive players...")
    df_final = remove_duplicates_and_inactive(df_clean)
    
    print("Identifying high performers...")
    df_with_performance, position_thresholds = identify_high_performers(df_final)
    
    print("Calculating high performer metrics...")
    position_stats, high_performers = calculate_high_performer_metrics(df_with_performance)
    
    print("Creating visualizations...")
    create_visualizations(df_with_performance, position_stats, high_performers)
    
    print("Generating summary statistics...")
    print_summary_statistics(df_with_performance, position_stats, high_performers, position_thresholds)
    
    # Save detailed results
    position_stats.to_csv('/Users/mightenyip/Documents/GitHub/yfd-py-test/position_data/combined_weeks_position_stats.csv', index=False)
    df_with_performance.to_csv('/Users/mightenyip/Documents/GitHub/yfd-py-test/position_data/combined_weeks_all_data.csv', index=False)
    high_performers.to_csv('/Users/mightenyip/Documents/GitHub/yfd-py-test/position_data/high_performers_data.csv', index=False)
    
    print(f"\nAnalysis complete! Results saved to:")
    print(f"- Combined position stats: position_data/combined_weeks_position_stats.csv")
    print(f"- All data with metrics: position_data/combined_weeks_all_data.csv")
    print(f"- High performers data: position_data/high_performers_data.csv")
    print(f"- Visualization: plots_images/combined_weeks_position_analysis.png")

if __name__ == "__main__":
    main()

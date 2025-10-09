import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Read all Thursday data
data_dir = Path('/Users/mightenyip/Documents/GitHub/yfd-py-test/data_csv')

week2 = pd.read_csv(data_dir / 'week2_Thurs.csv')
week3 = pd.read_csv(data_dir / 'week3_Thurs.csv')
week4 = pd.read_csv(data_dir / 'week4_Thurs.csv')
week5 = pd.read_csv(data_dir / 'week5_Thurs.csv')

# Combine all data
all_data = pd.concat([week2, week3, week4, week5], ignore_index=True)

# Clean salary column (remove $ and convert to int)
all_data['salary'] = all_data['salary'].str.replace('$', '').astype(int)

# Filter out inactive players (points > 0)
active_data = all_data[all_data['points'] > 0].copy()

# Calculate points per dollar
active_data['points_per_dollar'] = active_data['points'] / active_data['salary']

print("=" * 80)
print("THURSDAY NIGHT FOOTBALL ANALYSIS (Weeks 2-5)")
print("Analyzing Active Players Only (Points > 0)")
print("=" * 80)
print()

# Tonight's available players
tonights_players = {
    'QB': [
        ('Jalen Hurts', 38, 'PHI'),
        ('Jaxson Dart', 22, 'NYG'),
        ('Russell Wilson', 20, 'NYG'),
        ('Jameis Winston', 20, 'NYG'),
        ('Tanner McKee', 20, 'PHI'),
        ('Sam Howell', 20, 'PHI'),
    ],
    'RB': [
        ('Saquon Barkley', 36, 'PHI'),
        ('Cam Skattebo', 30, 'NYG'),
        ('Tyrone Tracy Jr.', 18, 'NYG'),
        ('A.J. Dillon', 10, 'PHI'),
        ('Will Shipley', 10, 'PHI'),
        ('Tank Bigsby', 10, 'PHI'),
        ('Devin Singletary', 10, 'NYG'),
    ],
    'WR': [
        ('DeVonta Smith', 24, 'PHI'),
        ('A.J. Brown', 22, 'PHI'),
        ('Wan\'Dale Robinson', 20, 'NYG'),
        ('Darius Slayton', 16, 'NYG'),
        ('Jahan Dotson', 10, 'PHI'),
        ('John Metchie III', 10, 'PHI'),
        ('Xavier Gipson', 10, 'PHI'),
        ('Jalin Hyatt', 10, 'NYG'),
        ('Beaux Collins', 10, 'NYG'),
        ('Gunner Olszewski', 10, 'NYG'),
    ],
    'TE': [
        ('Dallas Goedert', 18, 'PHI'),
        ('Theo Johnson', 14, 'NYG'),
        ('Grant Calcaterra', 10, 'PHI'),
        ('Kylen Granson', 10, 'PHI'),
        ('Cameron Latu', 10, 'PHI'),
        ('Daniel Bellinger', 10, 'NYG'),
        ('Chris Manhertz', 10, 'NYG'),
        ('Thomas Fidone II', 10, 'NYG'),
    ],
    'DEF': [
        ('Philadelphia Eagles', 15, 'PHI'),
        ('New York Giants', 11, 'NYG'),
    ]
}

# Analyze by position
for position in ['QB', 'RB', 'WR', 'TE', 'DEF']:
    pos_data = active_data[active_data['position'] == position].copy()
    
    if len(pos_data) == 0:
        continue
    
    print(f"\n{'=' * 80}")
    print(f"{position} ANALYSIS")
    print('=' * 80)
    
    # Overall stats
    print(f"\nOverall {position} Stats (Active Players):")
    print(f"  Average Points: {pos_data['points'].mean():.2f}")
    print(f"  Median Points: {pos_data['points'].median():.2f}")
    print(f"  Average Salary: ${pos_data['salary'].mean():.0f}")
    print(f"  Average Points per $: {pos_data['points_per_dollar'].mean():.4f}")
    
    # Top performers
    print(f"\nTop 5 {position} Performances:")
    top_performers = pos_data.nlargest(5, 'points')[['player_name', 'salary', 'points', 'points_per_dollar', 'week', 'game_info']]
    for idx, row in top_performers.iterrows():
        print(f"  {row['player_name']:25s} ${row['salary']:2d} -> {row['points']:5.2f} pts ({row['points_per_dollar']:.4f} pts/$) - {row['week']}")
    
    # Salary bracket analysis
    salary_brackets = [
        (10, 15, '$10-15'),
        (16, 25, '$16-25'),
        (26, 35, '$26-35'),
        (36, 50, '$36+')
    ]
    
    print(f"\n{position} Performance by Salary Bracket:")
    for min_sal, max_sal, label in salary_brackets:
        bracket_data = pos_data[(pos_data['salary'] >= min_sal) & (pos_data['salary'] <= max_sal)]
        if len(bracket_data) > 0:
            print(f"  {label:8s}: {len(bracket_data):2d} performances, "
                  f"Avg {bracket_data['points'].mean():.2f} pts, "
                  f"Avg {bracket_data['points_per_dollar'].mean():.4f} pts/$")
    
    # Best value plays (min $10 salary, sort by points per dollar)
    print(f"\nBest Value {position} Plays (sorted by points per $):")
    value_plays = pos_data.nlargest(5, 'points_per_dollar')[['player_name', 'salary', 'points', 'points_per_dollar', 'week']]
    for idx, row in value_plays.iterrows():
        print(f"  {row['player_name']:25s} ${row['salary']:2d} -> {row['points']:5.2f} pts ({row['points_per_dollar']:.4f} pts/$) - {row['week']}")

# Now analyze specific salary ranges for tonight's players
print("\n" + "=" * 80)
print("RECOMMENDATIONS FOR TONIGHT'S GAME")
print("Philadelphia Eagles vs New York Giants")
print("O/U 40.5, NYG +7.5")
print("=" * 80)

for position, players in tonights_players.items():
    print(f"\n{position} RECOMMENDATIONS:")
    print("-" * 80)
    
    for player_name, salary, team in players:
        pos_data = active_data[active_data['position'] == position].copy()
        
        # Find similar salary range (+/- $5)
        similar_salary = pos_data[(pos_data['salary'] >= salary - 5) & 
                                  (pos_data['salary'] <= salary + 5)]
        
        if len(similar_salary) > 0:
            avg_pts = similar_salary['points'].mean()
            median_pts = similar_salary['points'].median()
            max_pts = similar_salary['points'].max()
            avg_ppd = similar_salary['points_per_dollar'].mean()
            
            # Calculate a value rating (expected points relative to salary)
            expected_ppd = avg_ppd
            
            print(f"\n{player_name} ({team}) - ${salary}")
            print(f"  Similar salary range (${salary-5}-${salary+5}): {len(similar_salary)} performances")
            print(f"  Expected: {avg_pts:.2f} pts (median: {median_pts:.2f}, max: {max_pts:.2f})")
            print(f"  Expected points per $: {avg_ppd:.4f}")
            print(f"  Projected fantasy points: {salary * avg_ppd:.2f}")
        else:
            print(f"\n{player_name} ({team}) - ${salary}")
            print(f"  No historical data in similar salary range")

# Final recommendations
print("\n" + "=" * 80)
print("KEY INSIGHTS & RECOMMENDATIONS")
print("=" * 80)

# Find the best values at each salary tier
print("\n1. PREMIUM PLAYS ($25+):")
premium = active_data[active_data['salary'] >= 25].nlargest(10, 'points_per_dollar')
for idx, row in premium.head(5).iterrows():
    print(f"   {row['player_name']:25s} ({row['position']}) ${row['salary']:2d} -> {row['points']:5.2f} pts ({row['points_per_dollar']:.4f} pts/$)")

print("\n2. MID-RANGE PLAYS ($16-24):")
midrange = active_data[(active_data['salary'] >= 16) & (active_data['salary'] <= 24)].nlargest(10, 'points_per_dollar')
for idx, row in midrange.head(5).iterrows():
    print(f"   {row['player_name']:25s} ({row['position']}) ${row['salary']:2d} -> {row['points']:5.2f} pts ({row['points_per_dollar']:.4f} pts/$)")

print("\n3. VALUE PLAYS ($10-15):")
value = active_data[(active_data['salary'] >= 10) & (active_data['salary'] <= 15)].nlargest(10, 'points_per_dollar')
for idx, row in value.head(5).iterrows():
    print(f"   {row['player_name']:25s} ({row['position']}) ${row['salary']:2d} -> {row['points']:5.2f} pts ({row['points_per_dollar']:.4f} pts/$)")

# Position-specific trends
print("\n4. POSITION TRENDS ON THURSDAY NIGHTS:")
for position in ['QB', 'RB', 'WR', 'TE', 'DEF']:
    pos_data = active_data[active_data['position'] == position]
    if len(pos_data) > 0:
        print(f"   {position}: Avg {pos_data['points'].mean():.2f} pts, "
              f"{len(pos_data)} active performances out of {len(all_data[all_data['position'] == position])} total")

# Create visualizations
fig, axes = plt.subplots(2, 2, figsize=(15, 12))

# Plot 1: Points distribution by position
ax1 = axes[0, 0]
position_order = ['QB', 'RB', 'WR', 'TE', 'DEF']
active_data_ordered = active_data[active_data['position'].isin(position_order)]
sns.boxplot(data=active_data_ordered, x='position', y='points', order=position_order, ax=ax1)
ax1.set_title('Points Distribution by Position (Active Players)', fontsize=14, fontweight='bold')
ax1.set_xlabel('Position', fontsize=12)
ax1.set_ylabel('Fantasy Points', fontsize=12)
ax1.grid(True, alpha=0.3)

# Plot 2: Salary vs Points
ax2 = axes[0, 1]
for position in position_order:
    pos_data = active_data[active_data['position'] == position]
    ax2.scatter(pos_data['salary'], pos_data['points'], alpha=0.6, label=position, s=100)
ax2.set_title('Salary vs Points (All Active Players)', fontsize=14, fontweight='bold')
ax2.set_xlabel('Salary ($)', fontsize=12)
ax2.set_ylabel('Fantasy Points', fontsize=12)
ax2.legend()
ax2.grid(True, alpha=0.3)

# Plot 3: Points per Dollar by Position
ax3 = axes[1, 0]
ppd_by_pos = active_data.groupby('position')['points_per_dollar'].mean().reindex(position_order)
bars = ax3.bar(position_order, ppd_by_pos, color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'])
ax3.set_title('Average Points per Dollar by Position', fontsize=14, fontweight='bold')
ax3.set_xlabel('Position', fontsize=12)
ax3.set_ylabel('Points per Dollar', fontsize=12)
ax3.grid(True, alpha=0.3, axis='y')
for bar in bars:
    height = bar.get_height()
    ax3.text(bar.get_x() + bar.get_width()/2., height,
             f'{height:.4f}', ha='center', va='bottom', fontsize=10)

# Plot 4: Top value plays
ax4 = axes[1, 1]
top_values = active_data.nlargest(15, 'points_per_dollar')
colors = {'QB': '#1f77b4', 'RB': '#ff7f0e', 'WR': '#2ca02c', 'TE': '#d62728', 'DEF': '#9467bd'}
bar_colors = [colors[pos] for pos in top_values['position']]
bars = ax4.barh(range(len(top_values)), top_values['points_per_dollar'], color=bar_colors)
ax4.set_yticks(range(len(top_values)))
labels = [f"{row['player_name'][:18]} (${row['salary']})" for _, row in top_values.iterrows()]
ax4.set_yticklabels(labels, fontsize=8)
ax4.set_title('Top 15 Value Plays (Points per Dollar)', fontsize=14, fontweight='bold')
ax4.set_xlabel('Points per Dollar', fontsize=12)
ax4.grid(True, alpha=0.3, axis='x')
ax4.invert_yaxis()

plt.tight_layout()
plt.savefig('/Users/mightenyip/Documents/GitHub/yfd-py-test/plots_images/thursday_night_analysis.png', dpi=300, bbox_inches='tight')
print(f"\n\nVisualization saved to: plots_images/thursday_night_analysis.png")

# Create a specific recommendations CSV
recommendations = []
for position, players in tonights_players.items():
    for player_name, salary, team in players:
        pos_data = active_data[active_data['position'] == position].copy()
        similar_salary = pos_data[(pos_data['salary'] >= salary - 5) & 
                                  (pos_data['salary'] <= salary + 5)]
        
        if len(similar_salary) > 0:
            avg_pts = similar_salary['points'].mean()
            median_pts = similar_salary['points'].median()
            avg_ppd = similar_salary['points_per_dollar'].mean()
            projected_pts = salary * avg_ppd
            
            recommendations.append({
                'Player': player_name,
                'Team': team,
                'Position': position,
                'Salary': salary,
                'Projected_Points': round(projected_pts, 2),
                'Expected_Avg': round(avg_pts, 2),
                'Expected_Median': round(median_pts, 2),
                'Expected_PPD': round(avg_ppd, 4),
                'Similar_Performances': len(similar_salary)
            })

rec_df = pd.DataFrame(recommendations)
rec_df = rec_df.sort_values(['Position', 'Projected_Points'], ascending=[True, False])
rec_df.to_csv('/Users/mightenyip/Documents/GitHub/yfd-py-test/data_csv/tonight_recommendations.csv', index=False)
print(f"\nRecommendations saved to: data_csv/tonight_recommendations.csv")

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)


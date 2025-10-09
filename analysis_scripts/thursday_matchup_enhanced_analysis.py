"""
Enhanced Thursday Night Analysis with Defensive Matchup Data
Incorporates CBS Sports defensive rankings vs positions
"""
import pandas as pd
import numpy as np
from pathlib import Path

# Load original Thursday night analysis
data_dir = Path('/Users/mightenyip/Documents/GitHub/yfd-py-test/data_csv')
recommendations = pd.read_csv(data_dir / 'tonight_recommendations.csv')

print("="*80)
print("ENHANCED THURSDAY NIGHT ANALYSIS")
print("Philadelphia Eagles @ New York Giants")
print("O/U 40.5, NYG +7.5")
print("="*80)

# CBS Sports Defensive Rankings (from web research)
# Source: https://www.cbssports.com/fantasy/football/stats/posvsdef/
defensive_data = {
    'NYG': {
        'WR': {'rank': 30, 'fpts_allowed': 25.2, 'rating': 'ELITE_MATCHUP'},
        'RB': {'rank': 'Unknown', 'fpts_allowed': 'Unknown', 'rating': 'UNKNOWN'},
        'TE': {'rank': 'Unknown', 'fpts_allowed': 'Unknown', 'rating': 'UNKNOWN'},
        'QB': {'rank': 'Unknown', 'fpts_allowed': 'Unknown', 'rating': 'UNKNOWN'},
    },
    'PHI': {
        'WR': {'rank': 14, 'fpts_allowed': 19.0, 'rating': 'NEUTRAL'},
        'RB': {'rank': 'Unknown', 'fpts_allowed': 'Unknown', 'rating': 'UNKNOWN'},
        'TE': {'rank': 'Unknown', 'fpts_allowed': 'Unknown', 'rating': 'UNKNOWN'},
        'QB': {'rank': 'Unknown', 'fpts_allowed': 'Unknown', 'rating': 'UNKNOWN'},
    }
}

def calculate_matchup_multiplier(rank, fpts_allowed):
    """
    Calculate a multiplier based on defensive ranking
    Rank 25-32 (bottom 8): 1.20-1.35x (great matchup)
    Rank 17-24: 1.05-1.15x (good matchup)
    Rank 9-16: 1.0x (neutral)
    Rank 1-8: 0.85-0.95x (tough matchup)
    """
    if isinstance(rank, str):
        return 1.0  # No data, neutral
    
    if rank >= 28:
        return 1.35
    elif rank >= 25:
        return 1.25
    elif rank >= 22:
        return 1.15
    elif rank >= 17:
        return 1.08
    elif rank >= 9:
        return 1.0
    elif rank >= 5:
        return 0.92
    else:
        return 0.85

print("\n" + "="*80)
print("DEFENSIVE MATCHUP DATA")
print("="*80)

print("\nNYG DEFENSE (PHI Offense faces):")
print("-" * 80)
for pos, data in defensive_data['NYG'].items():
    rank = data['rank']
    fpts = data['fpts_allowed']
    rating = data['rating']
    
    if rating == 'ELITE_MATCHUP':
        emoji = "🔥🔥🔥"
        interpretation = "SMASH SPOT - Among worst defenses vs this position"
    elif rating == 'NEUTRAL':
        emoji = "➖"
        interpretation = "Average matchup"
    else:
        emoji = "❓"
        interpretation = "Data not yet available"
    
    print(f"{pos}: Rank #{rank}/32, {fpts} fantasy PPG allowed {emoji}")
    print(f"   {interpretation}")

print("\nPHI DEFENSE (NYG Offense faces):")
print("-" * 80)
for pos, data in defensive_data['PHI'].items():
    rank = data['rank']
    fpts = data['fpts_allowed']
    rating = data['rating']
    
    if rating == 'ELITE_MATCHUP':
        emoji = "🔥🔥🔥"
        interpretation = "SMASH SPOT - Among worst defenses vs this position"
    elif rating == 'NEUTRAL':
        emoji = "➖"
        interpretation = "Average matchup"
    else:
        emoji = "❓"
        interpretation = "Data not yet available"
    
    print(f"{pos}: Rank #{rank}/32, {fpts} fantasy PPG allowed {emoji}")
    print(f"   {interpretation}")

print("\n" + "="*80)
print("ADJUSTED PLAYER RECOMMENDATIONS")
print("="*80)

# Create adjusted recommendations
adjusted_recs = []

for idx, row in recommendations.iterrows():
    player = row['Player']
    team = row['Team']
    position = row['Position']
    salary = row['Salary']
    base_projection = row['Projected_Points']
    
    # Determine opponent
    opponent = 'NYG' if team == 'PHI' else 'PHI'
    
    # Get defensive matchup data
    if position in defensive_data[opponent]:
        def_data = defensive_data[opponent][position]
        rank = def_data['rank']
        multiplier = calculate_matchup_multiplier(rank, def_data['fpts_allowed'])
    else:
        multiplier = 1.0
        rank = 'N/A'
    
    adjusted_projection = base_projection * multiplier
    adjustment = adjusted_projection - base_projection
    
    adjusted_recs.append({
        'Player': player,
        'Team': team,
        'Position': position,
        'Salary': salary,
        'Base_Projection': round(base_projection, 2),
        'Matchup_Multiplier': round(multiplier, 2),
        'Adjusted_Projection': round(adjusted_projection, 2),
        'Adjustment': round(adjustment, 2),
        'Opp_Def_Rank': rank
    })

adj_df = pd.DataFrame(adjusted_recs)

# Sort by adjusted projection within each position
adj_df = adj_df.sort_values(['Position', 'Adjusted_Projection'], ascending=[True, False])

print("\n🔥 TOP PLAYS AFTER MATCHUP ADJUSTMENTS:")
print("-" * 80)

# Get top plays by biggest positive adjustments
top_upgrades = adj_df[adj_df['Adjustment'] > 0].nlargest(10, 'Adjusted_Projection')

for idx, row in top_upgrades.iterrows():
    stars = "⭐" * min(3, int(row['Adjusted_Projection'] / 10))
    arrow = "⬆️" if row['Adjustment'] > 1 else "↗️"
    print(f"\n{row['Player']} ({row['Team']}) - {row['Position']} ${row['Salary']}")
    print(f"  Base: {row['Base_Projection']:.1f} pts → Adjusted: {row['Adjusted_Projection']:.1f} pts {arrow} (+{row['Adjustment']:.1f})")
    print(f"  Opponent Defense Rank vs {row['Position']}: #{row['Opp_Def_Rank']}")
    print(f"  Rating: {stars}")

print("\n" + "="*80)
print("POSITION-BY-POSITION BREAKDOWN")
print("="*80)

for position in ['QB', 'RB', 'WR', 'TE', 'DEF']:
    pos_players = adj_df[adj_df['Position'] == position]
    if len(pos_players) == 0:
        continue
    
    print(f"\n{position}:")
    print("-" * 80)
    
    for idx, row in pos_players.head(5).iterrows():
        change_indicator = ""
        if row['Adjustment'] > 2:
            change_indicator = "🔥 MAJOR UPGRADE"
        elif row['Adjustment'] > 0.5:
            change_indicator = "↗️ Upgrade"
        elif row['Adjustment'] < -2:
            change_indicator = "❄️ MAJOR DOWNGRADE"
        elif row['Adjustment'] < -0.5:
            change_indicator = "↘️ Downgrade"
        
        print(f"  {row['Player']:25s} ({row['Team']}) ${row['Salary']:2d} -> {row['Adjusted_Projection']:5.1f} pts {change_indicator}")

print("\n" + "="*80)
print("🎯 FINAL RECOMMENDATIONS")
print("="*80)

print("\n1️⃣ MUST-START PLAYS:")
must_starts = adj_df[adj_df['Adjusted_Projection'] >= 18].head(5)
for idx, row in must_starts.iterrows():
    print(f"   ✓ {row['Player']} ({row['Position']}) - ${row['Salary']} → {row['Adjusted_Projection']:.1f} pts")

print("\n2️⃣ VALUE PLAYS:")
value_plays = adj_df[(adj_df['Salary'] <= 20) & (adj_df['Adjusted_Projection'] >= 10)].head(5)
if len(value_plays) > 0:
    for idx, row in value_plays.iterrows():
        print(f"   ✓ {row['Player']} ({row['Position']}) - ${row['Salary']} → {row['Adjusted_Projection']:.1f} pts")
else:
    print("   No elite value plays at low salaries")

print("\n3️⃣ AVOID/FADE:")
fades = adj_df[adj_df['Adjustment'] < -1].head(5)
if len(fades) > 0:
    for idx, row in fades.iterrows():
        print(f"   ✗ {row['Player']} ({row['Position']}) - Projected down to {row['Adjusted_Projection']:.1f} pts")
else:
    print("   No clear fades based on matchup data")

# Save adjusted recommendations
output_file = data_dir / 'tonight_recommendations_enhanced.csv'
adj_df.to_csv(output_file, index=False)
print(f"\n\nEnhanced recommendations saved to: {output_file}")

print("\n" + "="*80)
print("KEY INSIGHT: NYG DEFENSE IS 30TH VS WR!")
print("="*80)
print("\n🔥 This is the #1 takeaway: The Giants allow 25.2 fantasy PPG to WRs,")
print("   making them the 3rd WORST defense against wide receivers.")
print("\n   ACTION ITEMS:")
print("   • DeVonta Smith & A.J. Brown are SMASH PLAYS")
print("   • Jalen Hurts gets a boost (will throw more vs bad secondary)")
print("   • Stack PHI passing game for maximum upside")
print("\n" + "="*80)


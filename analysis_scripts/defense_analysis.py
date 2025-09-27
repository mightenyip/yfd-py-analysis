#!/usr/bin/env python3
"""
Quick analysis of defenses above $20
"""

import pandas as pd
import numpy as np

# Load Sunday data
week2_df = pd.read_csv('data_csv/week2_Sunday.csv')
week3_df = pd.read_csv('data_csv/week3_Sunday.csv')
all_sunday = pd.concat([week2_df, week3_df], ignore_index=True)

# Clean salary data
all_sunday['salary_numeric'] = all_sunday['salary'].str.replace('$', '').astype(float)
all_sunday['points_numeric'] = pd.to_numeric(all_sunday['points'], errors='coerce')

# Filter for defenses only
defenses = all_sunday[all_sunday['position'] == 'DEF'].copy()

# Filter for defenses above $20
defenses_above_20 = defenses[defenses['salary_numeric'] > 20]

print('📊 DEFENSES ABOVE $20 ANALYSIS:')
print(f'Total defenses: {len(defenses)}')
print(f'Defenses above $20: {len(defenses_above_20)}')
print(f'Percentage above $20: {len(defenses_above_20)/len(defenses)*100:.1f}%')

if len(defenses_above_20) > 0:
    print('\nDefenses above $20:')
    for _, row in defenses_above_20.iterrows():
        print(f'  {row["player_name"]} ({row["week"]}) - ${row["salary_numeric"]:.0f} | {row["points_numeric"]:.1f} pts')
else:
    print('\nNo defenses above $20 found')

# Also show all defenses for context
print('\nAll defenses by salary:')
defenses_sorted = defenses.sort_values('salary_numeric', ascending=False)
for _, row in defenses_sorted.iterrows():
    print(f'  {row["player_name"]} ({row["week"]}) - ${row["salary_numeric"]:.0f} | {row["points_numeric"]:.1f} pts')

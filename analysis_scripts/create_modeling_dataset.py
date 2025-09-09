#!/usr/bin/env python3
"""
Create a modeling dataset by filtering top performers by position
and extracting key data points (salary and points).
"""

import pandas as pd
import os
import re

def clean_salary(salary_str):
    """Convert salary string to numeric value"""
    if pd.isna(salary_str) or salary_str == '':
        return 0
    # Remove $ and convert to int
    return int(str(salary_str).replace('$', '').replace(',', ''))

def clean_points(points_str):
    """Convert points string to numeric value"""
    if pd.isna(points_str) or points_str == '':
        return 0
    try:
        return float(str(points_str))
    except:
        return 0

def create_modeling_dataset(input_file="yahoo_daily_fantasy_2025_week1_completed_page.csv"):
    """
    Create a modeling dataset with top performers by position
    """
    print(f"📊 Creating modeling dataset from {input_file}")
    
    # Read the data
    try:
        df = pd.read_csv(input_file)
        print(f"✅ Loaded {len(df)} players from {input_file}")
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return
    
    # Clean the data
    df['salary_numeric'] = df['salary'].apply(clean_salary)
    df['points_numeric'] = df['points'].apply(clean_points)
    
    # Remove game_day column if it exists
    if 'game_day' in df.columns:
        df = df.drop('game_day', axis=1)
        print("🗑️  Removed game_day column")
    
    # Filter by position and get top performers
    modeling_data = []
    
    # Top 25 QBs
    qb_data = df[df['position'] == 'QB'].copy()
    qb_data = qb_data.sort_values('points_numeric', ascending=False).head(25)
    print(f"📈 Selected top {len(qb_data)} QBs")
    modeling_data.append(qb_data)
    
    # Top 90 WRs
    wr_data = df[df['position'] == 'WR'].copy()
    wr_data = wr_data.sort_values('points_numeric', ascending=False).head(90)
    print(f"📈 Selected top {len(wr_data)} WRs")
    modeling_data.append(wr_data)
    
    # Top 65 RBs
    rb_data = df[df['position'] == 'RB'].copy()
    rb_data = rb_data.sort_values('points_numeric', ascending=False).head(65)
    print(f"📈 Selected top {len(rb_data)} RBs")
    modeling_data.append(rb_data)
    
    # Top 45 TEs
    te_data = df[df['position'] == 'TE'].copy()
    te_data = te_data.sort_values('points_numeric', ascending=False).head(45)
    print(f"📈 Selected top {len(te_data)} TEs")
    modeling_data.append(te_data)
    
    # All defenses
    def_data = df[df['position'] == 'DEF'].copy()
    def_data = def_data.sort_values('points_numeric', ascending=False)
    print(f"📈 Selected all {len(def_data)} defenses")
    modeling_data.append(def_data)
    
    # Combine all data
    modeling_df = pd.concat(modeling_data, ignore_index=True)
    
    # Create clean modeling dataset with key columns
    modeling_clean = modeling_df[['player_name', 'position', 'salary_numeric', 'points_numeric', 'fppg']].copy()
    
    # Rename columns for clarity
    modeling_clean = modeling_clean.rename(columns={
        'salary_numeric': 'salary',
        'points_numeric': 'points'
    })
    
    # Sort by position and points
    modeling_clean = modeling_clean.sort_values(['position', 'points'], ascending=[True, False])
    
    # Save the modeling dataset
    output_file = "modeling_dataset_2025_week1.csv"
    modeling_clean.to_csv(output_file, index=False)
    
    print(f"\n📊 Modeling Dataset Summary:")
    print(f"Total players: {len(modeling_clean)}")
    print(f"QBs: {len(modeling_clean[modeling_clean['position'] == 'QB'])}")
    print(f"WRs: {len(modeling_clean[modeling_clean['position'] == 'WR'])}")
    print(f"RBs: {len(modeling_clean[modeling_clean['position'] == 'RB'])}")
    print(f"TEs: {len(modeling_clean[modeling_clean['position'] == 'TE'])}")
    print(f"DEFs: {len(modeling_clean[modeling_clean['position'] == 'DEF'])}")
    
    print(f"\n💰 Salary Statistics:")
    print(f"Min salary: ${modeling_clean['salary'].min()}")
    print(f"Max salary: ${modeling_clean['salary'].max()}")
    print(f"Avg salary: ${modeling_clean['salary'].mean():.2f}")
    
    print(f"\n🎯 Points Statistics:")
    print(f"Min points: {modeling_clean['points'].min():.2f}")
    print(f"Max points: {modeling_clean['points'].max():.2f}")
    print(f"Avg points: {modeling_clean['points'].mean():.2f}")
    
    print(f"\n✅ Modeling dataset saved to: {output_file}")
    
    # Show top performers by position
    print(f"\n🏆 Top Performers by Position:")
    for position in ['QB', 'RB', 'WR', 'TE', 'DEF']:
        pos_data = modeling_clean[modeling_clean['position'] == position].head(3)
        if len(pos_data) > 0:
            print(f"\n{position}:")
            for _, player in pos_data.iterrows():
                print(f"  {player['player_name']:<20} | ${player['salary']:<3} | {player['points']:>6.2f} pts")
    
    return modeling_clean

def create_correlation_analysis(modeling_df):
    """
    Create correlation analysis between salary and points
    """
    print(f"\n📈 Correlation Analysis:")
    
    # Overall correlation
    overall_corr = modeling_df['salary'].corr(modeling_df['points'])
    print(f"Overall Salary-Points Correlation: {overall_corr:.4f}")
    
    # By position
    print(f"\nBy Position:")
    for position in ['QB', 'RB', 'WR', 'TE', 'DEF']:
        pos_data = modeling_df[modeling_df['position'] == position]
        if len(pos_data) > 1:
            corr = pos_data['salary'].corr(pos_data['points'])
            print(f"{position}: {corr:.4f} (n={len(pos_data)})")
    
    # Value analysis (points per dollar)
    modeling_df['value'] = modeling_df['points'] / modeling_df['salary']
    modeling_df['value'] = modeling_df['value'].replace([float('inf'), -float('inf')], 0)
    
    print(f"\n💎 Best Value Players (Points per Dollar):")
    top_value = modeling_df.nlargest(10, 'value')
    for _, player in top_value.iterrows():
        print(f"  {player['player_name']:<20} | {player['position']:<3} | ${player['salary']:<3} | {player['points']:>6.2f} pts | {player['value']:>6.3f} pts/$")

if __name__ == "__main__":
    # Create the modeling dataset
    modeling_data = create_modeling_dataset()
    
    if modeling_data is not None:
        # Create correlation analysis
        create_correlation_analysis(modeling_data)

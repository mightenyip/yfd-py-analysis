#!/usr/bin/env python3
"""
Weekly Fantasy Football Report Generator
Combines Yahoo scraped data with CBS defensive rankings to generate comprehensive reports
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import argparse
import glob
import os

class WeeklyReportGenerator:
    def __init__(self, data_dir="/Users/mightenyip/Documents/GitHub/yfd-py-test/data_csv"):
        self.data_dir = Path(data_dir)
        self.defensive_data = {}
        self.yahoo_data = {}
        
    def load_defensive_rankings(self):
        """Load CBS Sports defensive rankings."""
        print("📊 Loading defensive rankings...")
        
        positions = ['QB', 'RB', 'WR', 'TE']
        for position in positions:
            file_path = self.data_dir / f'cbs_defense_vs_{position.lower()}.csv'
            if file_path.exists():
                df = pd.read_csv(file_path)
                self.defensive_data[position] = df
                print(f"   ✅ Loaded {position} defensive rankings ({len(df)} teams)")
            else:
                print(f"   ⚠️  Missing {position} defensive rankings")
        
        return len(self.defensive_data) > 0
    
    def load_yahoo_data(self, week, day):
        """Load Yahoo scraped data for a specific week/day."""
        print(f"📊 Loading Yahoo data for Week {week} {day}...")
        
        # Try different filename formats
        day_short = day[:4] if day in ['Thursday', 'Sunday', 'Monday'] else day[:3]
        possible_files = [
            f'week{week}_{day_short}.csv',
            f'week{week}_{day}.csv',
            f'week_{week}_{day}.csv',
        ]
        
        for filename in possible_files:
            file_path = self.data_dir / filename
            if file_path.exists():
                df = pd.read_csv(file_path)
                self.yahoo_data[f'Week{week}_{day}'] = df
                print(f"   ✅ Loaded {len(df)} players from {filename}")
                return df
        
        print(f"   ⚠️  No Yahoo data found for Week {week} {day}")
        return None
    
    def get_defensive_rank(self, team, position):
        """Get defensive ranking for a team vs a position."""
        if position not in self.defensive_data:
            return None, None, 1.0
        
        df = self.defensive_data[position]
        team_row = df[df['Team'].str.contains(team, case=False, na=False)]
        
        if team_row.empty:
            return None, None, 1.0
        
        rank = team_row.iloc[0].get('Rank', None)
        fpts = team_row.iloc[0].get('FPTS', None)
        
        # Calculate multiplier based on rank
        try:
            rank_int = int(rank)
            if rank_int >= 28:
                multiplier = 1.35
            elif rank_int >= 25:
                multiplier = 1.25
            elif rank_int >= 20:
                multiplier = 1.15
            elif rank_int >= 15:
                multiplier = 1.05
            elif rank_int >= 10:
                multiplier = 1.00
            elif rank_int >= 5:
                multiplier = 0.90
            else:
                multiplier = 0.80
        except (ValueError, TypeError):
            multiplier = 1.0
        
        return rank, fpts, multiplier
    
    def analyze_upcoming_week(self, week, matchups):
        """
        Generate recommendations for upcoming week's matchups.
        matchups: list of (team1, team2) tuples
        """
        print(f"\n{'='*80}")
        print(f"WEEK {week} MATCHUP ANALYSIS & RECOMMENDATIONS")
        print('='*80)
        
        all_recommendations = []
        
        for team1, team2 in matchups:
            print(f"\n🏈 {team1} vs {team2}")
            print("-"*80)
            
            for position in ['QB', 'RB', 'WR', 'TE']:
                # Analyze team1 offense vs team2 defense
                def_rank1, fpts1, mult1 = self.get_defensive_rank(team2, position)
                
                # Analyze team2 offense vs team1 defense
                def_rank2, fpts2, mult2 = self.get_defensive_rank(team1, position)
                
                if def_rank1:
                    rating = self._get_matchup_rating(mult1)
                    print(f"\n{team1} {position}s vs {team2} Defense:")
                    print(f"   Defense Rank: #{def_rank1}/32 (allows {fpts1} FPPG)")
                    print(f"   Rating: {rating}")
                    print(f"   Multiplier: {mult1}x")
                    
                    all_recommendations.append({
                        'Week': week,
                        'Offense': team1,
                        'Defense': team2,
                        'Position': position,
                        'Def_Rank': def_rank1,
                        'FPPG_Allowed': fpts1,
                        'Multiplier': mult1,
                        'Rating': rating
                    })
                
                if def_rank2:
                    rating = self._get_matchup_rating(mult2)
                    print(f"\n{team2} {position}s vs {team1} Defense:")
                    print(f"   Defense Rank: #{def_rank2}/32 (allows {fpts2} FPPG)")
                    print(f"   Rating: {rating}")
                    print(f"   Multiplier: {mult2}x")
                    
                    all_recommendations.append({
                        'Week': week,
                        'Offense': team2,
                        'Defense': team1,
                        'Position': position,
                        'Def_Rank': def_rank2,
                        'FPPG_Allowed': fpts2,
                        'Multiplier': mult2,
                        'Rating': rating
                    })
        
        # Save recommendations
        if all_recommendations:
            rec_df = pd.DataFrame(all_recommendations)
            output_file = self.data_dir / f'week{week}_matchup_recommendations.csv'
            rec_df.to_csv(output_file, index=False)
            print(f"\n💾 Recommendations saved to: {output_file}")
            
            # Show top opportunities
            print(f"\n🔥 TOP OPPORTUNITIES FOR WEEK {week}:")
            print("-"*80)
            top_matches = rec_df[rec_df['Multiplier'] >= 1.20].sort_values('Multiplier', ascending=False)
            for _, row in top_matches.head(10).iterrows():
                print(f"   {row['Rating']} {row['Offense']} {row['Position']}s vs {row['Defense']} (#{row['Def_Rank']}, {row['Multiplier']}x)")
        
        return all_recommendations
    
    def _get_matchup_rating(self, multiplier):
        """Convert multiplier to rating string."""
        if multiplier >= 1.30:
            return "🔥🔥🔥 SMASH"
        elif multiplier >= 1.20:
            return "🔥🔥 GREAT"
        elif multiplier >= 1.10:
            return "🔥 GOOD"
        elif multiplier >= 1.00:
            return "➖ NEUTRAL"
        elif multiplier >= 0.85:
            return "❄️ TOUGH"
        else:
            return "❄️❄️ AVOID"
    
    def analyze_completed_week(self, week, day):
        """Analyze completed games from Yahoo data."""
        df = self.load_yahoo_data(week, day)
        
        if df is None:
            print(f"⚠️  No data available for Week {week} {day}")
            return None
        
        print(f"\n{'='*80}")
        print(f"WEEK {week} {day.upper()} GAMES ANALYSIS")
        print('='*80)
        
        # Clean data
        df['points'] = pd.to_numeric(df['points'], errors='coerce')
        df['salary'] = df['salary'].str.replace('$', '').astype(float)
        
        # Filter active players
        active = df[df['points'] > 0].copy()
        active['points_per_dollar'] = active['points'] / active['salary']
        
        print(f"\n📊 Overview:")
        print(f"   Total players: {len(df)}")
        print(f"   Active (scored points): {len(active)}")
        print(f"   Inactive: {len(df) - len(active)}")
        
        # Top performers by position
        print(f"\n🏆 TOP PERFORMERS:")
        print("-"*80)
        
        for position in ['QB', 'RB', 'WR', 'TE']:
            pos_players = active[active['position'] == position].nlargest(3, 'points')
            if len(pos_players) > 0:
                print(f"\n{position}:")
                for _, row in pos_players.iterrows():
                    print(f"   {row['player_name']:<25} ${row['salary']:<5.0f} -> {row['points']:.1f} pts ({row['points_per_dollar']:.3f} pts/$)")
        
        # Best values
        print(f"\n💎 BEST VALUE PLAYS:")
        print("-"*80)
        best_values = active.nlargest(10, 'points_per_dollar')
        for _, row in best_values.iterrows():
            print(f"   {row['player_name']:<25} ({row['position']}) ${row['salary']:<5.0f} -> {row['points']:.1f} pts ({row['points_per_dollar']:.3f} pts/$)")
        
        # Save summary
        summary_file = self.data_dir / f'week{week}_{day}_summary.csv'
        summary_stats = {
            'position': [],
            'total_players': [],
            'active_players': [],
            'avg_points': [],
            'avg_salary': [],
            'avg_ppd': []
        }
        
        for position in ['QB', 'RB', 'WR', 'TE', 'DEF']:
            pos_all = df[df['position'] == position]
            pos_active = active[active['position'] == position]
            
            summary_stats['position'].append(position)
            summary_stats['total_players'].append(len(pos_all))
            summary_stats['active_players'].append(len(pos_active))
            summary_stats['avg_points'].append(pos_active['points'].mean() if len(pos_active) > 0 else 0)
            summary_stats['avg_salary'].append(pos_active['salary'].mean() if len(pos_active) > 0 else 0)
            summary_stats['avg_ppd'].append(pos_active['points_per_dollar'].mean() if len(pos_active) > 0 else 0)
        
        summary_df = pd.DataFrame(summary_stats)
        summary_df.to_csv(summary_file, index=False)
        print(f"\n💾 Summary saved to: {summary_file}")
        
        return active
    
    def generate_full_report(self, current_week):
        """Generate comprehensive weekly report."""
        print("="*80)
        print("WEEKLY FANTASY FOOTBALL REPORT")
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        # Load defensive rankings
        if not self.load_defensive_rankings():
            print("⚠️  Could not load defensive rankings. Run CBS scraper first.")
            return
        
        # Analyze last completed games
        days = ['Thursday', 'Sunday', 'Monday']
        for day in days:
            print(f"\n{'='*80}")
            print(f"ANALYZING WEEK {current_week} {day.upper()}")
            print("="*80)
            self.analyze_completed_week(current_week, day)

def main():
    parser = argparse.ArgumentParser(description='Weekly Fantasy Football Report Generator')
    parser.add_argument('--week', type=int, required=True, help='NFL week number')
    parser.add_argument('--mode', choices=['upcoming', 'completed', 'full'], default='full',
                        help='Report mode: upcoming (next week preview), completed (past week review), full (both)')
    parser.add_argument('--matchups', nargs='+', help='Matchups for upcoming week (format: TEAM1-TEAM2)')
    parser.add_argument('--day', choices=['Thursday', 'Sunday', 'Monday'], help='Specific day to analyze')
    
    args = parser.parse_args()
    
    generator = WeeklyReportGenerator()
    
    # Load defensive rankings
    generator.load_defensive_rankings()
    
    if args.mode == 'upcoming' or args.mode == 'full':
        if args.matchups:
            # Parse matchups
            matchup_pairs = []
            for matchup in args.matchups:
                teams = matchup.split('-')
                if len(teams) == 2:
                    matchup_pairs.append((teams[0], teams[1]))
            
            if matchup_pairs:
                generator.analyze_upcoming_week(args.week, matchup_pairs)
        else:
            print("⚠️  Provide matchups with --matchups TEAM1-TEAM2 TEAM3-TEAM4")
    
    if args.mode == 'completed' or args.mode == 'full':
        if args.day:
            generator.analyze_completed_week(args.week, args.day)
        else:
            # Analyze all days
            for day in ['Thursday', 'Sunday', 'Monday']:
                generator.analyze_completed_week(args.week, day)

if __name__ == '__main__':
    main()


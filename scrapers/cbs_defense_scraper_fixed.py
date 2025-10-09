#!/usr/bin/env python3
"""
CBS Sports Defense vs Position Scraper (Fixed Version)
Scrapes defensive rankings against QB, RB, WR, TE positions
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
from pathlib import Path
from datetime import datetime

def scrape_defense_vs_position(position='WR'):
    """
    Scrape CBS Sports defense vs position data.
    Position options: QB, RB, WR, TE
    """
    url = f'https://www.cbssports.com/fantasy/football/stats/posvsdef/{position}/all/avg/standard'
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    print(f"🔄 Scraping {position} defensive rankings from CBS Sports...")
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the stats table - try multiple selectors
        table = soup.find('table', {'class': 'TableBase'}) or soup.find('table')
        
        if not table:
            print(f"❌ Could not find table for {position}")
            return None
        
        # Extract data rows
        data = []
        rows = table.find_all('tr')
        
        # Skip first row (header)
        for row in rows[1:]:
            cols = row.find_all(['td', 'th'])
            if len(cols) > 0:
                row_data = []
                for col in cols:
                    # Get text, handling links
                    text = col.get_text(strip=True)
                    row_data.append(text)
                
                if len(row_data) > 0:
                    data.append(row_data)
        
        if not data:
            print(f"❌ No data extracted for {position}")
            return None
        
        # Create DataFrame with proper column names
        # Columns: Rank, Team, Rush Att, Rush Yd, Rush Avg, Rush TD, Targets, Receptions, Rec Yd, Rec Avg, Rec TD, Fumbles, FPTS
        column_names = ['Rank', 'Team', 'Rush_Att', 'Rush_Yd', 'Rush_Avg', 'Rush_TD', 
                       'Targets', 'Receptions', 'Rec_Yd', 'Rec_Avg', 'Rec_TD', 'Fumbles', 'FPTS']
        
        # Adjust column names based on position
        if position == 'QB':
            column_names = ['Rank', 'Team', 'Pass_Att', 'Pass_Yd', 'Pass_TD', 'INT',
                           'Rush_Att', 'Rush_Yd', 'Rush_Avg', 'Rush_TD', 'Fumbles', 'FPTS']
        elif position in ['RB', 'WR']:
            column_names = ['Rank', 'Team', 'Rush_Att', 'Rush_Yd', 'Rush_Avg', 'Rush_TD',
                           'Targets', 'Receptions', 'Rec_Yd', 'Rec_Avg', 'Rec_TD', 'Fumbles', 'FPTS']
        elif position == 'TE':
            column_names = ['Rank', 'Team', 'Targets', 'Receptions', 'Rec_Yd', 
                           'Rec_Avg', 'Rec_TD', 'Fumbles', 'FPTS']
        
        # Create DataFrame with flexible column handling
        df = pd.DataFrame(data)
        
        # Ensure we have the right number of columns
        if len(df.columns) > len(column_names):
            # Use actual number of columns
            column_names = [f'Col_{i}' if i >= len(column_names) else column_names[i] 
                          for i in range(len(df.columns))]
        elif len(df.columns) < len(column_names):
            column_names = column_names[:len(df.columns)]
        
        df.columns = column_names
        
        # Clean team names (remove position prefix if exists)
        if 'Team' in df.columns:
            df['Team'] = df['Team'].str.replace(f'{position} vs ', '', regex=False)
            df['Team'] = df['Team'].str.replace(f'vs ', '', regex=False)
        
        # Add metadata
        df['Position'] = position
        df['Scrape_Date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        print(f"✅ Successfully scraped {len(df)} teams for {position}")
        
        # Display top 5 and bottom 5
        print(f"\n   Top 5 Best Defenses vs {position} (allow fewest points):")
        for _, row in df.head(5).iterrows():
            rank = row.get('Rank', 'N/A')
            team = row.get('Team', 'Unknown')
            fpts = row.get('FPTS', 'N/A')
            print(f"      #{rank}: {team} - {fpts} FPPG")
        
        print(f"\n   Top 5 Worst Defenses vs {position} (allow most points):")
        for _, row in df.tail(5).iterrows():
            rank = row.get('Rank', 'N/A')
            team = row.get('Team', 'Unknown')
            fpts = row.get('FPTS', 'N/A')
            print(f"      #{rank}: {team} - {fpts} FPPG")
        
        return df
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error scraping {position}: {str(e)}")
        return None
    except Exception as e:
        print(f"❌ Error scraping {position}: {str(e)}")
        return None

def scrape_all_positions(output_dir="/Users/mightenyip/Documents/GitHub/yfd-py-test/data_csv"):
    """
    Scrape all position defensive rankings and save to CSV files.
    """
    positions = ['QB', 'RB', 'WR', 'TE']
    results = {}
    
    print("="*80)
    print("CBS SPORTS DEFENSIVE RANKINGS SCRAPER")
    print("="*80)
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    for position in positions:
        df = scrape_defense_vs_position(position)
        
        if df is not None:
            results[position] = df
            
            # Save to CSV
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, f'cbs_defense_vs_{position.lower()}.csv')
            df.to_csv(output_file, index=False)
            print(f"   💾 Saved to: {output_file}\n")
        
        # Be nice to the server
        time.sleep(2)
    
    return results

def analyze_matchup(team1, team2, defensive_data):
    """
    Analyze a specific matchup using the defensive data.
    team1 and team2 are team names (e.g., 'Eagles', 'Giants')
    """
    print("\n" + "="*80)
    print(f"MATCHUP ANALYSIS: {team1} vs {team2}")
    print("="*80)
    
    matchup_summary = {
        'team1': team1,
        'team2': team2,
        'recommendations': []
    }
    
    for position, df in defensive_data.items():
        print(f"\n{position} MATCHUPS:")
        print("-"*80)
        
        # Find team1's defense vs this position
        team1_row = df[df['Team'].str.contains(team1, case=False, na=False)]
        # Find team2's defense vs this position
        team2_row = df[df['Team'].str.contains(team2, case=False, na=False)]
        
        if not team1_row.empty:
            rank = team1_row.iloc[0].get('Rank', 'N/A')
            fpts = team1_row.iloc[0].get('FPTS', 'N/A')
            
            print(f"{team1} Defense vs {position}:")
            print(f"  Rank: #{rank} of 32")
            print(f"  Fantasy Points Allowed: {fpts}")
            
            # Interpret ranking
            try:
                rank_int = int(rank)
                if rank_int >= 25:
                    rating = "🔥🔥🔥 ELITE MATCHUP"
                    impact = f"SMASH {team2} {position}s"
                    multiplier = 1.30
                elif rank_int >= 20:
                    rating = "🔥🔥 GREAT MATCHUP"
                    impact = f"Start {team2} {position}s confidently"
                    multiplier = 1.20
                elif rank_int >= 15:
                    rating = "🔥 GOOD MATCHUP"
                    impact = f"Upgrade {team2} {position}s"
                    multiplier = 1.10
                elif rank_int >= 10:
                    rating = "➖ NEUTRAL"
                    impact = f"{team2} {position}s at baseline"
                    multiplier = 1.00
                elif rank_int >= 5:
                    rating = "❄️ TOUGH MATCHUP"
                    impact = f"Downgrade {team2} {position}s"
                    multiplier = 0.90
                else:
                    rating = "❄️❄️ ELITE DEFENSE"
                    impact = f"Avoid {team2} {position}s"
                    multiplier = 0.80
                
                print(f"  Rating: {rating}")
                print(f"  Impact: {impact}")
                print(f"  Multiplier: {multiplier}x")
                
                matchup_summary['recommendations'].append({
                    'defense': team1,
                    'offense': team2,
                    'position': position,
                    'rank': rank_int,
                    'fpts_allowed': fpts,
                    'rating': rating,
                    'multiplier': multiplier,
                    'impact': impact
                })
            except (ValueError, TypeError):
                print(f"  ⚠️  Could not parse ranking")
        
        if not team2_row.empty:
            rank = team2_row.iloc[0].get('Rank', 'N/A')
            fpts = team2_row.iloc[0].get('FPTS', 'N/A')
            
            print(f"\n{team2} Defense vs {position}:")
            print(f"  Rank: #{rank} of 32")
            print(f"  Fantasy Points Allowed: {fpts}")
            
            # Interpret ranking
            try:
                rank_int = int(rank)
                if rank_int >= 25:
                    rating = "🔥🔥🔥 ELITE MATCHUP"
                    impact = f"SMASH {team1} {position}s"
                    multiplier = 1.30
                elif rank_int >= 20:
                    rating = "🔥🔥 GREAT MATCHUP"
                    impact = f"Start {team1} {position}s confidently"
                    multiplier = 1.20
                elif rank_int >= 15:
                    rating = "🔥 GOOD MATCHUP"
                    impact = f"Upgrade {team1} {position}s"
                    multiplier = 1.10
                elif rank_int >= 10:
                    rating = "➖ NEUTRAL"
                    impact = f"{team1} {position}s at baseline"
                    multiplier = 1.00
                elif rank_int >= 5:
                    rating = "❄️ TOUGH MATCHUP"
                    impact = f"Downgrade {team1} {position}s"
                    multiplier = 0.90
                else:
                    rating = "❄️❄️ ELITE DEFENSE"
                    impact = f"Avoid {team1} {position}s"
                    multiplier = 0.80
                
                print(f"  Rating: {rating}")
                print(f"  Impact: {impact}")
                print(f"  Multiplier: {multiplier}x")
                
                matchup_summary['recommendations'].append({
                    'defense': team2,
                    'offense': team1,
                    'position': position,
                    'rank': rank_int,
                    'fpts_allowed': fpts,
                    'rating': rating,
                    'multiplier': multiplier,
                    'impact': impact
                })
            except (ValueError, TypeError):
                print(f"  ⚠️  Could not parse ranking")
    
    return matchup_summary

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='CBS Sports Defense vs Position Scraper')
    parser.add_argument('--matchup', nargs=2, metavar=('TEAM1', 'TEAM2'),
                        help='Analyze specific matchup (e.g., --matchup Eagles Giants)')
    parser.add_argument('--output-dir', default='/Users/mightenyip/Documents/GitHub/yfd-py-test/data_csv',
                        help='Output directory for CSV files')
    
    args = parser.parse_args()
    
    # Scrape all defensive rankings
    defensive_data = scrape_all_positions(args.output_dir)
    
    if not defensive_data:
        print("\n❌ No data scraped. Exiting.")
        return
    
    print("\n" + "="*80)
    print("SCRAPING COMPLETE")
    print("="*80)
    print(f"✅ Successfully scraped defensive rankings for {len(defensive_data)} positions")
    print(f"💾 Data saved to: {args.output_dir}")
    print(f"⏰ Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # If matchup specified, analyze it
    if args.matchup:
        team1, team2 = args.matchup
        matchup_summary = analyze_matchup(team1, team2, defensive_data)
        
        # Save matchup analysis
        if matchup_summary['recommendations']:
            matchup_df = pd.DataFrame(matchup_summary['recommendations'])
            output_file = os.path.join(args.output_dir, f'matchup_{team1}_vs_{team2}.csv')
            matchup_df.to_csv(output_file, index=False)
            print(f"\n💾 Matchup analysis saved to: {output_file}")

if __name__ == '__main__':
    main()


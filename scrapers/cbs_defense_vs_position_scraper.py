"""
CBS Sports Defense vs Position Scraper
Scrapes defensive rankings against QB, RB, WR, TE positions
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from pathlib import Path

def scrape_defense_vs_position(position='WR'):
    """
    Scrape CBS Sports defense vs position data
    Position options: QB, RB, WR, TE, DST
    """
    url = f'https://www.cbssports.com/fantasy/football/stats/posvsdef/{position}/all/avg/standard'
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    print(f"Scraping {position} defensive rankings from CBS Sports...")
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the stats table
        table = soup.find('table')
        
        if not table:
            print(f"Could not find table for {position}")
            return None
        
        # Extract headers
        headers_row = table.find('tr')
        headers = [th.get_text(strip=True) for th in headers_row.find_all('th')]
        
        # Extract data rows
        data = []
        for row in table.find_all('tr')[1:]:  # Skip header row
            cols = row.find_all('td')
            if cols:
                row_data = [col.get_text(strip=True) for col in cols]
                data.append(row_data)
        
        # Create DataFrame
        df = pd.DataFrame(data, columns=headers)
        
        # Clean up team names (remove "vs" prefix)
        if 'Team' in df.columns:
            df['Team'] = df['Team'].str.replace(f'{position} vs ', '')
        
        print(f"Successfully scraped {len(df)} teams for {position}")
        return df
        
    except Exception as e:
        print(f"Error scraping {position}: {str(e)}")
        return None

def analyze_tonight_matchup(team1='Giants', team2='Eagles'):
    """
    Analyze tonight's specific matchup using CBS defensive data
    """
    positions = ['QB', 'RB', 'WR', 'TE']
    results = {}
    
    for position in positions:
        df = scrape_defense_vs_position(position)
        if df is not None:
            results[position] = df
            time.sleep(1)  # Be nice to the server
    
    # Analyze matchups
    print("\n" + "="*80)
    print(f"MATCHUP ANALYSIS: {team1} Defense vs {team2} Offense")
    print("="*80)
    
    for position, df in results.items():
        # Find the team's defensive ranking against this position
        team1_row = df[df['Team'].str.contains(team1, case=False, na=False)]
        team2_row = df[df['Team'].str.contains(team2, case=False, na=False)]
        
        if not team1_row.empty:
            rank = team1_row['Rank'].values[0]
            fpts = team1_row['FPTS'].values[0] if 'FPTS' in team1_row.columns else 'N/A'
            print(f"\n{team1} Defense vs {position}:")
            print(f"  Rank: {rank} of 32")
            print(f"  Avg Fantasy Points Allowed: {fpts}")
            
            # Interpret ranking
            rank_int = int(rank) if rank.isdigit() else 0
            if rank_int >= 25:
                rating = "⭐⭐⭐ ELITE MATCHUP (Top 25% worst defenses)"
                impact = f"UPGRADE {team2} {position}s significantly"
            elif rank_int >= 17:
                rating = "⭐⭐ GOOD MATCHUP (Below average defense)"
                impact = f"UPGRADE {team2} {position}s moderately"
            elif rank_int >= 9:
                rating = "⭐ NEUTRAL MATCHUP (Average defense)"
                impact = f"Keep {team2} {position}s at baseline projection"
            else:
                rating = "❌ TOUGH MATCHUP (Top tier defense)"
                impact = f"DOWNGRADE {team2} {position}s"
            
            print(f"  Rating: {rating}")
            print(f"  Impact: {impact}")
        
        if not team2_row.empty:
            rank = team2_row['Rank'].values[0]
            fpts = team2_row['FPTS'].values[0] if 'FPTS' in team2_row.columns else 'N/A'
            print(f"\n{team2} Defense vs {position}:")
            print(f"  Rank: {rank} of 32")
            print(f"  Avg Fantasy Points Allowed: {fpts}")
            
            # Interpret ranking
            rank_int = int(rank) if rank.isdigit() else 0
            if rank_int >= 25:
                rating = "⭐⭐⭐ ELITE MATCHUP (Top 25% worst defenses)"
                impact = f"UPGRADE {team1} {position}s significantly"
            elif rank_int >= 17:
                rating = "⭐⭐ GOOD MATCHUP (Below average defense)"
                impact = f"UPGRADE {team1} {position}s moderately"
            elif rank_int >= 9:
                rating = "⭐ NEUTRAL MATCHUP (Average defense)"
                impact = f"Keep {team1} {position}s at baseline projection"
            else:
                rating = "❌ TOUGH MATCHUP (Top tier defense)"
                impact = f"DOWNGRADE {team1} {position}s"
            
            print(f"  Rating: {rating}")
            print(f"  Impact: {impact}")
    
    # Save results
    output_dir = Path('/Users/mightenyip/Documents/GitHub/yfd-py-test/data_csv')
    
    for position, df in results.items():
        output_file = output_dir / f'cbs_defense_vs_{position.lower()}.csv'
        df.to_csv(output_file, index=False)
        print(f"\nSaved {position} data to: {output_file}")
    
    return results

if __name__ == '__main__':
    # Analyze tonight's game: Giants vs Eagles
    results = analyze_tonight_matchup('Giants', 'Eagles')
    
    print("\n" + "="*80)
    print("SCRAPING COMPLETE")
    print("="*80)


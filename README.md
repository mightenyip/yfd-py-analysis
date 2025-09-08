# Yahoo DFS NFL Web Scraper

A Selenium-based web scraper for Yahoo Daily Fantasy Sports that captures NFL player data from completed games.

*Author: Mighten Yip

## 🏈 Overview

This project scrapes Yahoo's Daily Fantasy Sports completed games page to extract NFL player statistics, including:
- Player names and positions
- Game information and matchups
- Salary and fantasy points
- Performance statistics

The scraper captures data from all completed NFL games and organizes players by position into separate CSV files.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Chrome browser installed
- ChromeDriver (automatically managed by Selenium)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd yfd-py-test
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the scraper:**
   ```bash
   python3 selenium_completed_page_scraper.py
   ```

4. **Parse players by position:**
   ```bash
   python3 parse_players_by_position.py yahoo_daily_fantasy_2025_week1_completed_page.csv
   ```

## 📁 Project Structure

### Main Scripts
- **`selenium_completed_page_scraper.py`** - Main scraper for Yahoo's completed games page
- **`parse_players_by_position.py`** - Parses scraped data into position-specific files
- **`selenium_correct_points_scraper.py`** - Alternative scraper implementation

### Data Files
- **`yahoo_daily_fantasy_2025_week1_completed_page.csv`** - Main dataset with all players
- **`position_data/`** - Directory containing position-specific CSV files:
  - `qb_players_2025_week1.csv` - Quarterbacks
  - `rb_players_2025_week1.csv` - Running Backs
  - `wr_players_2025_week1.csv` - Wide Receivers
  - `te_players_2025_week1.csv` - Tight Ends
  - `def_players_2025_week1.csv` - Defenses
  - `position_summary_2025_week1.csv` - Summary statistics

## 🎯 Features

### Data Capture
- **Complete Player Data**: Captures all players from completed NFL games
- **Week-Specific Naming**: Files include week information (e.g., `2025_week1`)
- **Position Organization**: Automatically separates players by position
- **Performance Metrics**: Includes salary, fantasy points, and game statistics

### Output Format
Each player record includes:
- `player_name` - Player's name
- `position` - Player position (QB, RB, WR, TE, DEF)
- `game_info` - Game matchup and final score
- `stats` - Detailed performance statistics
- `salary` - Daily fantasy salary
- `fppg` - Fantasy points per game average
- `points` - Actual fantasy points scored

## 📊 Usage Examples

### Basic Scraping
```bash
# Scrape current week's data
python3 selenium_completed_page_scraper.py

# Parse into position files
python3 parse_players_by_position.py yahoo_daily_fantasy_2025_week1_completed_page.csv
```

### Custom File Processing
```bash
# Parse a specific CSV file
python3 parse_players_by_position.py your_custom_file.csv
```

## 🔧 Configuration

### Week Information
The scraper automatically generates week-specific filenames. To modify the week calculation, edit the `get_week_info()` function in the scraper scripts.

### Output Directory
Position-specific files are saved to the `position_data/` directory by default. This can be modified in the `parse_players_by_position.py` script.

## 📈 Sample Output

### Top Performers (Example)
```
📋 Top 10 Overall Performers:
   1. Josh Allen           | QB  | $40    | 38.76  pts
   2. Justin Fields        | QB  | $20    | 29.52  pts
   3. Daniel Jones         | QB  | $20    | 29.48  pts
   4. Lamar Jackson        | QB  | $37    | 29.36  pts
   5. Derrick Henry        | RB  | $38    | 28.70  pts
```

### Position Summary
```
📊 Position Summary:
Position Players  Avg Pts  Max Pts  Min Pts  Median  
QB       97       4.49     38.76    0.0      0.0     
RB       172      2.61     28.7     -0.6     0.0     
WR       310      2.01     24.6     0.0      0.0     
TE       159      1.57     12.8     -1.6     0.0     
DEF      26       5.85     14.0     -3.0     6.5     
```

## 🛠️ Technical Details

### Selenium Configuration
- Uses Chrome WebDriver with headless mode option
- Implements scrolling to load all player data
- Handles dynamic content loading
- Robust error handling for network issues

### Data Processing
- CSV parsing with pandas
- Position-based filtering and organization
- Statistical analysis and summaries
- Week-specific file naming

## 📋 Requirements

### Python Packages
- `selenium` - Web scraping automation
- `pandas` - Data manipulation and analysis
- `webdriver-manager` - Automatic ChromeDriver management

### System Requirements
- Chrome browser installed
- Internet connection for scraping
- Sufficient disk space for CSV files

## 🚨 Important Notes

### Yahoo's Terms of Service
- This scraper is for educational and personal use only
- Respect Yahoo's robots.txt and rate limiting
- Do not overload their servers with excessive requests

### Data Accuracy
- Data is scraped from Yahoo's public completed games page
- Accuracy depends on Yahoo's data quality
- Always verify critical data points

### Legal Disclaimer
This tool is provided for educational purposes only. Users are responsible for complying with Yahoo's Terms of Service and applicable laws. The authors are not responsible for any misuse of this software.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

**ChromeDriver not found:**
```bash
# Install webdriver-manager
pip install webdriver-manager
```

**No data scraped:**
- Check internet connection
- Verify Yahoo's page structure hasn't changed
- Run with `headless=False` to see browser behavior

**CSV parsing errors:**
- Ensure the CSV file was created successfully
- Check for special characters in player names
- Verify file encoding (UTF-8)

### Getting Help
- Check the existing CSV files for expected data format
- Run individual scripts to isolate issues
- Review console output for error messages

---

**Happy Scraping! 🏈📊**

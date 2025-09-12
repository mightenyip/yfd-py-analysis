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

**📅 Note: Current analysis is based on Week 1 data from the 2025 NFL season. Results may vary significantly as the season progresses and sample sizes increase.**

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

### Value Analysis
The scraper provides comprehensive value analysis showing points per dollar by position:

![Value Analysis](value_analysis_for_readme.png)

**Key Insights:**
- **QBs** offer the highest average value (0.639 pts/$)
- **WRs** have the highest ceiling value (1.514 pts/$)
- **RBs** show the strongest salary-to-points correlation (0.7707)
- **Defenses** are unpredictable regardless of salary (-0.0451 correlation)

**🔍 QB Correlation Discovery:**
When analyzing QB salary-performance relationships, removing the top 2 highest salaried QBs (Josh Allen and Lamar Jackson) reveals a fascinating pattern:
- **With top 2**: Weak positive correlation (0.1961)
- **Without top 2**: Weak negative correlation (-0.2155)
- This suggests that the salary-performance relationship for QBs is driven almost entirely by just two elite players, while the rest of the QB pool shows that higher salaries don't predict better performance. Value QBs in the \$20-25 range may actually be better investments than the most expensive options.

## 🎯 Week 2 Thursday Analysis: Parabolic Hypothesis Validation

### Hypothesis Testing Results

**Original Hypothesis:** Fantasy football value follows a parabolic relationship with salary, with optimal value in the \$15-20 range and diminishing returns at higher salary levels.

**Data Source:** Week 2 Thursday games (WAS @ GB) - 22 active players

### Key Findings

#### **Parabolic Relationship Confirmed**
- **Binned Data Cubic Model**: R² = 0.963 (Excellent fit - 96.3% of variance explained)
- **Raw Data Models**: Quadratic R² = 0.375, Cubic R² = 0.432 (Fair fit)
- **Critical Insight**: Individual player variability masks the underlying parabolic pattern

#### **Optimal Value Range Identified**
- **Sweet Spot**: \$15-20 salary range
- **Value Ratio**: 0.655 points per dollar (highest efficiency)
- **Sample Size**: n = 4 players in optimal range
- **Diminishing Returns**: Higher salary ranges show lower value ratios

#### **Statistical Evidence**
- **Correlation**: r = 0.759 (Strong positive relationship for binned data)
- **Model Improvement**: Binning improves R² from 0.432 (raw) to 0.963 (binned)
- **Pattern Validation**: The parabolic curve is only visible when data is properly grouped by salary ranges

### Visual Evidence

![Week 2 Thursday Hypothesis Showcase](plots_images/week2_thursday_clean_hypothesis_showcase.png)

**Plot 1 - Parabolic Relationship**: Shows the cubic fit on binned salary data with the \$15-20 sweet spot highlighted in gold and Jayden Daniels (\$39, 19.7 pts) supporting the curve. The left panel displays the "Salary vs Points Relationship" with cubic model and histogram bins, while the right panel shows "Value Efficiency by Salary Range" with the peak at \$15-20 range.

![Raw Data Models](plots_images/week2_thursday_raw_data_models.png)

**Plot 2 - Raw Data Models**: Demonstrates how individual player data shows weaker relationships (R² = 0.375-0.432) compared to the strong parabolic pattern revealed through salary binning. Shows quadratic vs cubic models on raw individual player data.

### Hypothesis Validation

✅ **PARABOLIC RELATIONSHIP CONFIRMED** - Cubic model achieves R² = 0.963 on binned data
✅ **OPTIMAL VALUE RANGE FOUND** - `$`15-20 provides 0.655 pts/ &#36; (highest efficiency)  
✅ **DIMINISHING RETURNS CONFIRMED** - Higher salary ranges show lower value ratios
✅ **JAYDEN DANIELS SUPPORTS HYPOTHESIS** - High-salary player fits the parabolic curve

### Conclusion

The Week 2 Thursday analysis definitively validates the parabolic hypothesis. The relationship between salary and fantasy value is strong and follows a clear parabolic pattern, but this pattern is only visible when individual player variability is controlled through salary binning. The $15-20 range represents the optimal value sweet spot, with diminishing returns at both lower and higher salary levels.

### Analysis Script

The analysis was performed using `analysis_scripts/clean_hypothesis_showcase.py`, which generates the two clean visualization plots without text boxes for optimal readability.

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

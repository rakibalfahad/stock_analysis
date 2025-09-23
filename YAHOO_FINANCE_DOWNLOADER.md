# Yahoo Finance Stock Data Downloader

A comprehensive Python script that downloads various stock categories from Yahoo Finance and saves them to Excel files with date-specific naming.

## 📊 Features

### Stock Categories Available:
- **Most Active** - Stocks with highest trading volume
- **Trending Now** - Currently trending/popular stocks  
- **Top Gainers** - Biggest daily percentage gainers
- **Top Losers** - Biggest daily percentage losers
- **52 Week Gainers** - Stocks near their 52-week highs
- **52 Week Losers** - Stocks near their 52-week lows

### Data Points Collected:
- Company name, symbol, current price
- Daily change and percentage change
- Volume, average volume, market cap
- Sector, industry classification
- PE ratio, EPS, book value, price-to-book
- 52-week high/low, 52-week range percentage
- Beta, dividend yield, profit margin
- Revenue and other financial metrics

## 🚀 Quick Start

### Basic Usage
```bash
# Download all categories for today
python yahoo_finance_downloader.py

# Download specific categories
python yahoo_finance_downloader.py --categories most_active,top_gainers

# Download for a specific date
python yahoo_finance_downloader.py --date 2025-09-20

# Custom output filename
python yahoo_finance_downloader.py --output my_stocks.xlsx

# Show help
python yahoo_finance_downloader.py --help
```

### Advanced Examples
```bash
# Download only most active stocks
python yahoo_finance_downloader.py --categories most_active --output most_active_today.xlsx

# Download gainers and losers for specific date
python yahoo_finance_downloader.py --categories top_gainers,top_losers --date 2025-09-23

# Download trending stocks only
python yahoo_finance_downloader.py --categories trending --output trending_stocks.xlsx

# Download 52-week analysis
python yahoo_finance_downloader.py --categories 52_week_gainers,52_week_losers

# Custom output directory
python yahoo_finance_downloader.py --output-dir my_data
```

## 📁 Output Format

### Excel File Structure:
- **Summary Sheet** - Overview of all categories with counts and metadata
- **Individual Category Sheets** - Detailed data for each stock category
- **Date-Specific Naming** - Files named `yahoo_finance_data_YYYY-MM-DD.xlsx`

### Data Storage:
- Default directory: `data/`
- Format: Excel (.xlsx) with multiple sheets
- Comprehensive stock information in tabular format

## 🎯 Use Cases

### For Traders:
- **Daily Market Scan** - Get most active and trending stocks
- **Opportunity Identification** - Find top gainers and losers
- **Volume Analysis** - Identify high-volume stocks for liquidity

### For Investors:
- **52-Week Analysis** - Stocks near highs/lows for timing decisions
- **Sector Analysis** - Diversification across industries
- **Fundamental Screening** - PE ratios, market caps, financials

### For Analysts:
- **Market Research** - Historical trend analysis with date-specific files
- **Comparative Analysis** - Multiple categories in single Excel file
- **Data Export** - Easy integration with other analysis tools

## 📊 Sample Output

The Excel files contain detailed information like:

| Symbol | Company Name | Current Price | Change | Change % | Volume | Market Cap | Sector | PE Ratio | 52W High | 52W Low |
|--------|-------------|---------------|--------|----------|---------|------------|---------|----------|----------|---------|
| AAPL   | Apple Inc.  | 228.63       | +2.15  | +0.95%   | 45.2M   | 3.5T       | Tech    | 28.5     | 237.23   | 164.08  |
| MSFT   | Microsoft   | 509.41       | +1.22  | +0.24%   | 10.8M   | 3.8T       | Tech    | 37.4     | 468.35   | 309.45  |

## 🔧 Technical Details

### Dependencies:
- `yfinance` - Yahoo Finance API access
- `pandas` - Data manipulation and Excel export
- `openpyxl` - Excel file writing
- `requests` - HTTP requests for additional data

### Rate Limiting:
- Built-in 0.1-second delays between requests
- Handles API errors gracefully
- Skips delisted or unavailable stocks

### Error Handling:
- Comprehensive logging to console and file
- Graceful handling of network issues
- Continues processing if individual stocks fail
- Clear error messages and warnings

## 📈 Integration with Portfolio Optimizer

This downloader complements the existing portfolio optimization system:

```bash
# Download market data
python yahoo_finance_downloader.py --categories most_active,top_gainers

# Use with portfolio optimizer
python main.py --plot

# Compare with current portfolio
python portfolio_summary.py
```

## 🎉 Ready to Use!

1. **Download the script** - `yahoo_finance_downloader.py`
2. **Run examples** - `python yahoo_finance_examples.py`
3. **Start downloading** - Choose any command from the examples above
4. **Analyze data** - Open the Excel files to explore stock information

The script is designed to work seamlessly with the existing stock analysis infrastructure while providing flexible, date-specific stock data downloads for comprehensive market analysis.
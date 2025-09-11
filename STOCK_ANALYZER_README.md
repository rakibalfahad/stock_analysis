# 📊 Stock Risk vs Return Analysis Tool - Version 2.0

A comprehensive standalone Python script that generates professional **Risk vs Return analysis** and **price trend visualizations** from Excel or CSV files, featuring **52-week high/low positioning**, **multi-sheet portfolio analysis**, and **professional investment insights**.

## 🎯 Enhanced Features

✨ **Advanced Risk vs Return Scatter Plot** - Dual color coding with Sharpe ratio + 52-week positioning  
🔥 **52-Week Market Positioning** - Visual indicators: 🔥 (near high), ⚡ (mid-range), ❄️ (near low)  
📊 **Comprehensive Portfolio Analysis** - Pre-built Conservative, Moderate, and Aggressive portfolios  
📋 **Multi-Sheet Excel Support** - Analyze specific sheets with `--sheet` parameter  
📈 **Flexible Price Trends** - Configurable periods (30d, 60d, 1y) for trend analysis  
💼 **Professional Templates** - 6-sheet Excel file with detailed stock information  
📊 **Enhanced Statistics** - 52-week analysis, position tracking, and investment insights  
📁 **Multiple File Formats** - Excel (.xlsx, .xls) and CSV support  
🎨 **High-Quality Output** - 300 DPI PNG charts suitable for presentations  
🚀 **Simple Command Interface** - One-command analysis with extensive customization  

## 🚀 Quick Start Guide

### 1. Create Comprehensive Sample Files
```bash
python stock_analyzer.py --create-sample
```
**Creates:**
- `sample_stocks.xlsx` - Professional 6-sheet Excel file with detailed information
- `sample_stocks.csv` - Simple CSV version for basic analysis

### 2. Basic Analysis
```bash
# Analyze all stocks (uses 'All_Stocks' sheet automatically)
python stock_analyzer.py sample_stocks.xlsx

# Analyze from CSV file  
python stock_analyzer.py sample_stocks.csv

# Custom output filename
python stock_analyzer.py sample_stocks.xlsx --output my_analysis.png
```

### 3. Portfolio-Specific Analysis
```bash
# Conservative portfolio (low-risk, dividend stocks)
python stock_analyzer.py sample_stocks.xlsx --sheet Conservative_Portfolio

# Moderate portfolio (balanced growth stocks)
python stock_analyzer.py sample_stocks.xlsx --sheet Moderate_Portfolio

# Aggressive portfolio (high-growth, high-volatility)
python stock_analyzer.py sample_stocks.xlsx --sheet Aggressive_Portfolio
```

### 4. Advanced Analysis Options
```bash
# 2-year risk analysis with 60-day price trends
python stock_analyzer.py sample_stocks.xlsx --period 2y --price-period 60d

# Long-term analysis for aggressive portfolio
python stock_analyzer.py sample_stocks.xlsx --sheet Aggressive_Portfolio --period 5y

# Quick momentum analysis
python stock_analyzer.py sample_stocks.xlsx --period 6mo --price-period 1mo
```

## � Ticker-Only Excel Files - Complete Compatibility Guide

The **Stock Analyzer is designed to work seamlessly with simple Excel files containing only ticker symbols**. No additional data is required - the tool automatically fetches all market data!

### 🎯 **Automatic Column Detection**

The analyzer intelligently searches for ticker symbols using this priority system:

**✅ Recognized Column Names (Case-Insensitive):**
```
symbol, symbols, stock, stocks, ticker, tickers
Symbol, Symbols, Stock, Stocks, Ticker, Tickers
Code, code
```

**🔄 Fallback Strategy:**
If no standard column name is found, it automatically uses the **first column** in your file.

### 📊 **Simple Excel File Examples**

**Example 1: Standard Format**
```
Symbol
AAPL
MSFT
GOOGL
TSLA
NVDA
```

**Example 2: Alternative Column Name**
```
Ticker
AMZN
META
NFLX
SPOT
UBER
```

**Example 3: Generic Column Name**
```
Stock
ORCL
CRM
ADBE
NOW
ZM
```

**Example 4: Any Column Name (Auto-Detection)**
```
My_Stocks
SHOP
SQU
PLTR
SNOW
ROKU
```

### 🚀 **What Happens Automatically**

When you provide just ticker symbols, the analyzer automatically:

1. **📊 Fetches Real-Time Data**:
   - Current stock prices
   - Historical price data (1 year for risk analysis)
   - 30-day price trends
   - Trading volumes

2. **📈 Calculates 52-Week Analysis**:
   - 52-week high and low prices
   - Current position in 52-week range
   - Visual indicators (🔥⚡❄️)

3. **🧮 Computes Financial Metrics**:
   - Expected returns (annualized)
   - Risk/volatility measures
   - Sharpe ratios
   - Market cap proxies

4. **🎨 Generates Professional Charts**:
   - Risk vs Return scatter plot
   - 30-day price trend comparison
   - Comprehensive statistics table

### 💡 **Usage with Ticker-Only Files**

```bash
# Create a simple ticker file and analyze
echo -e "Symbol\nAAPL\nMSFT\nGOOGL" > my_stocks.csv
python stock_analyzer.py my_stocks.csv

# Works with Excel too
python stock_analyzer.py my_tickers.xlsx

# Custom output for ticker-only analysis
python stock_analyzer.py simple_tickers.xlsx --output ticker_analysis.png
```

### 📋 **Console Output Example**

When processing a ticker-only file, you'll see:

```
📊 Loading stock symbols from my_stocks.xlsx...
   📋 Available sheets: Sheet1
   🎯 Using first sheet: Sheet1
   📊 Loaded data: 5 rows, 1 columns
   ✅ Found symbol column: 'Symbol'
   ✅ Successfully loaded 5 stock symbols: AAPL, MSFT, GOOGL, TSLA, NVDA

🧮 Fetching market data for 5 stocks...
   - Risk/Return data (1y period)...
   - Price trend data (30d period)...
   - 52-week high/low data...
✅ Successfully fetched data for 5/5 stocks

🧮 Calculating risk and return metrics...
✅ Calculated metrics for 5 stocks

📊 Creating visualizations...
✅ Analysis saved as stock_analysis.png
```

### ⚠️ **File Format Requirements**

**✅ Supported Formats:**
- Excel files: `.xlsx`, `.xls`
- CSV files: `.csv`

**✅ Minimal Requirements:**
- At least one column with ticker symbols
- Valid stock ticker symbols (1-10 characters)
- No empty rows between symbols

**❌ Invalid Formats:**
- Empty files
- Files without any recognizable ticker symbols
- Symbols longer than 10 characters

### 🎯 **Best Practices for Ticker-Only Files**

1. **📝 Use Standard Headers**: `Symbol` or `Ticker` for clarity
2. **🧹 Clean Data**: Remove empty rows and invalid symbols
3. **📊 Reasonable Size**: 3-20 stocks for optimal visualization
4. **✅ Verify Symbols**: Ensure tickers are valid and actively traded
5. **💾 Save as .xlsx**: Excel format supports better error handling

### 🔧 **Troubleshooting Ticker-Only Files**

**Problem**: "No standard symbol column found"
**Solution**: The tool will use the first column automatically - this is normal!

**Problem**: "No data for [SYMBOL]"
**Solution**: Check if the ticker symbol is valid and actively traded

**Problem**: "Error loading file"
**Solution**: Ensure file exists and is not corrupted, try CSV format

### 💼 **Professional Use Cases**

- **📊 Quick Portfolio Analysis**: Analyze your current holdings
- **🔍 Stock Screening**: Evaluate potential investments
- **📈 Sector Analysis**: Compare stocks within an industry
- **⚡ Momentum Trading**: Identify 52-week positioning opportunities
- **💰 Value Investing**: Find stocks near 52-week lows

## �📁 Comprehensive Excel File Structure (Sample Files)

The enhanced `sample_stocks.xlsx` contains **6 professional sheets**:

### 📊 Sheet 1: All_Stocks (Main Dataset)
**11 detailed columns:**
- **Symbol**: Stock ticker for trading
- **Company**: Full company name
- **Sector**: Business sector classification
- **Industry**: Specific industry within sector
- **Market_Cap**: Market capitalization category
- **Description**: Detailed business description
- **Country**: Country of incorporation
- **Exchange**: Stock exchange (NASDAQ, NYSE)
- **Currency**: Trading currency
- **Risk_Level**: Professional risk assessment
- **Dividend**: Dividend-paying status

### 🛡️ Sheet 2: Conservative_Portfolio
**Low-risk investments (2 stocks):**
- Stable, established companies
- Dividend-paying stocks
- Lower volatility profiles
- Suitable for risk-averse investors

### ⚖️ Sheet 3: Moderate_Portfolio  
**Balanced investments (7 stocks):**
- Growing companies with moderate volatility
- Mix of dividend and growth stocks
- Balanced risk-return profiles
- Suitable for most investors

### 🚀 Sheet 4: Aggressive_Portfolio
**High-growth investments (7 stocks):**
- Fast-growing companies
- Higher volatility, higher potential returns
- Innovation and disruption leaders
- Suitable for risk-tolerant investors

### 📈 Sheet 5: Sector_Analysis
**Sector breakdown and statistics:**
- Stock count by sector
- Sector diversification metrics
- Industry concentration analysis

### 📚 Sheet 6: Instructions
**Complete usage guide:**
- Command examples for all scenarios
- Column descriptions and meanings
- Risk level explanations
- Diversification tips and strategies

## 🔥 52-Week Analysis Features

### 📊 Enhanced Risk vs Return Visualization

**Dual Color Coding System:**
- **🎨 Fill Colors**: Based on Sharpe ratio performance
  - 🟢 Green: Excellent risk-adjusted returns (Sharpe > 1.5)
  - 🟡 Yellow: Good risk-adjusted returns (Sharpe 0.5-1.5)
  - 🔴 Red: Poor risk-adjusted returns (Sharpe < 0.5)

- **🔥 Border Colors**: Based on 52-week position
  - 🟢 Dark Green: Near 52-week high (>80% of range)
  - 🟠 Orange: Mid-range position (50-80% of range)
  - 🔴 Red: Near 52-week low (<50% of range)

**Visual Indicators:**
- **🔥 Fire emoji**: Stocks near 52-week highs (momentum plays)
- **⚡ Lightning emoji**: Stocks in mid-range (balanced position)
- **❄️ Snowflake emoji**: Stocks near 52-week lows (value opportunities)

### 💰 Comprehensive Statistics with 52-Week Data

```
Symbol Current Price 52W High 52W Low 52W Position Expected Return Risk (Volatility) Sharpe Ratio
  AAPL       $236.23  $259.18 $168.80      74.6% ⚡           12.3%             32.2%         0.32
 GOOGL       $238.70  $238.76 $140.23      99.9% 🔥           53.2%             31.9%         1.60
  MSFT       $499.07  $554.54 $343.59      73.7% ⚡           24.7%             24.9%         0.91
  NVDA       $168.13  $184.48  $86.61      83.3% 🔥           79.2%             50.8%         1.52

🎯 KEY INSIGHTS:
🏆 Best Expected Return: SHOP (93.5%)
📊 Best Sharpe Ratio: NFLX (2.03)
🛡️ Lowest Risk: MSFT (24.9%)

🔥 52-WEEK ANALYSIS:
🔥 Near 52W High (>80%): GOOGL, NVDA, META, NFLX, SPOT, SHOP
❄️ Near 52W Low (<20%): CRM, ADBE
📏 Widest 52W Range: SPOT (143.5% range)

💡 LEGEND: 🔥 = Near High | ⚡ = Mid-Range | ❄️ = Near Low
```

## ⚙️ Command Line Options

| Option | Description | Default | Example |
|--------|-------------|---------|---------|
| `file` | Excel/CSV file with stock symbols | Required | `stocks.xlsx` |
| `--output` | Output PNG filename | `stock_analysis.png` | `--output my_chart.png` |
| `--period` | Historical period for risk/return | `1y` | `--period 2y` |
| `--price-period` | Period for price trends | `30d` | `--price-period 60d` |
| `--sheet` | Excel sheet to analyze | `All_Stocks` (auto) | `--sheet Conservative_Portfolio` |
| `--create-sample` | Create sample files | - | `--create-sample` |

### Period Options:
- **Short term**: `1d`, `5d`, `1mo`, `3mo`
- **Medium term**: `6mo`, `1y` (default)  
- **Long term**: `2y`, `5y`, `10y`
- **Special**: `ytd` (year to date), `max` (maximum available)

## 📈 Understanding the Analysis

### 🎯 Risk vs Return Plot Interpretation

**Quadrant Analysis:**
- **Top-right**: High return, high risk (growth stocks like NVDA, TSLA)
- **Top-left**: High return, low risk (ideal investments - rare!)
- **Bottom-right**: Low return, high risk (avoid these)
- **Bottom-left**: Low return, low risk (stable stocks like MSFT)

**Visual Elements:**
- **Bubble Size**: Larger bubbles = higher market cap proxy
- **Fill Color**: Green = excellent Sharpe ratio, Red = poor Sharpe ratio
- **Border Color**: Green = near 52W high, Red = near 52W low
- **Emoji Indicators**: 🔥 = momentum stocks, ❄️ = value opportunities

### 📊 52-Week Position Strategy Guide

**🔥 Near 52-Week High (>80%):**
- **Momentum Strategy**: Stocks with strong upward momentum
- **Considerations**: May be overbought, higher volatility risk
- **Suitable for**: Trend followers, momentum investors

**⚡ Mid-Range (50-80%):**
- **Balanced Position**: Stocks with room to move in either direction
- **Considerations**: Good balance of risk and opportunity
- **Suitable for**: Most investors, balanced portfolios

**❄️ Near 52-Week Low (<50%):**
- **Value Strategy**: Potentially undervalued opportunities
- **Considerations**: May be oversold, fundamental analysis recommended
- **Suitable for**: Value investors, contrarian strategies

## 🧮 Key Metrics Explained

- **Expected Return**: Annualized expected return based on historical performance
- **Risk (Volatility)**: Annualized standard deviation of returns  
- **Sharpe Ratio**: Risk-adjusted return metric (higher = better)
- **52-Week High/Low**: Highest and lowest prices in past 52 weeks
- **52-Week Position**: Current price position within 52-week range (percentage)
- **Current Price**: Latest market price
- **Market Cap Proxy**: Estimated relative market size based on volume

## 🔧 Technical Implementation - How Ticker-Only Files Work

### 📊 **Smart Column Detection Algorithm**

The stock analyzer uses sophisticated logic to find ticker symbols in your file:

```python
# Priority-based column search
possible_columns = ['symbol', 'symbols', 'stock', 'stocks', 'ticker', 'tickers', 
                  'Symbol', 'Symbols', 'Stock', 'Stocks', 'Ticker', 'Tickers', 'Code', 'code']

# Automatic fallback to first column
if symbol_column is None:
    symbol_column = df.columns[0]
    print(f"⚠️ No standard symbol column found, using first column: '{symbol_column}'")
```

### 🚀 **Automatic Data Enrichment Process**

**Step 1: Symbol Extraction**
```python
# Clean and validate symbols
symbols = df[symbol_column].dropna().astype(str).str.strip().str.upper()
self.stock_symbols = [s for s in symbols if s and s != 'NAN' and len(s) <= 10]
```

**Step 2: Market Data Fetching**
```python
# Fetch comprehensive market data
risk_data = yf.download(symbols, period='1y', interval='1d')      # Risk analysis
price_data = yf.download(symbols, period='30d', interval='1d')    # Price trends  
week52_data = yf.download(symbols, period='1y', interval='1d')    # 52-week range
```

**Step 3: Metrics Calculation**
```python
# Calculate comprehensive metrics from ticker symbols alone
expected_return = returns.mean() * 252                           # Annualized return
volatility = returns.std() * np.sqrt(252)                       # Annualized volatility
sharpe_ratio = (expected_return - 0.02) / volatility           # Risk-adjusted return
current_position = (current_price - week52_low) / week52_range  # 52-week position
```

### 📈 **Data Sources and Validation**

**Automatic Data Sources:**
- **Yahoo Finance API**: Real-time prices, historical data, volumes
- **52-Week Calculations**: Automatic high/low identification
- **Market Cap Proxy**: Volume-based estimation
- **Sector Information**: Fetched when available in Yahoo Finance data

**Built-in Validation:**
- Symbol length validation (1-10 characters)
- Data availability checks
- Empty data handling
- Network error recovery

### 🎯 **Why Ticker-Only Files Are Powerful**

1. **🔄 Always Current**: Data is fetched in real-time
2. **📊 Comprehensive**: Full analysis from minimal input
3. **🚀 Fast Setup**: No manual data entry required
4. **✅ Accurate**: Direct from financial data providers
5. **📈 Professional**: Same quality as expensive tools

## 🎨 Professional Chart Output

### Side-by-Side Layout:

**📈 Left Panel: Risk vs Return Analysis**
- Comprehensive scatter plot with all visual indicators
- Efficient frontier approximation
- Professional legend with 52-week position guide
- Color-coded performance metrics

**📊 Right Panel: Price Trend Comparison**  
- Normalized price trends starting at 100
- Individual stock performance lines
- Percentage change annotations
- Date range customization

**Chart Specifications:**
- **Resolution**: 300 DPI (print quality)
- **Format**: PNG with transparent background option
- **Size**: Optimized for presentations (20x10 inches)
- **Styling**: Professional business-ready appearance

## 💼 Investment Use Cases

### 🛡️ Conservative Portfolio Analysis
```bash
python stock_analyzer.py sample_stocks.xlsx --sheet Conservative_Portfolio --period 2y
```
**Perfect for:**
- Retirement portfolios
- Risk-averse investors
- Income-focused strategies
- Capital preservation goals

### 🚀 Growth Portfolio Analysis
```bash
python stock_analyzer.py sample_stocks.xlsx --sheet Aggressive_Portfolio --period 5y
```
**Perfect for:**
- Young investors
- High-risk tolerance
- Long-term growth goals
- Technology sector focus

### 📊 Sector Comparison
```bash
python stock_analyzer.py sample_stocks.xlsx --output sector_analysis.png --period 1y
```
**Perfect for:**
- Diversification analysis
- Sector rotation strategies
- Market timing decisions
- Portfolio rebalancing

### 💹 Market Timing Analysis
```bash
python stock_analyzer.py sample_stocks.xlsx --period 6mo --price-period 1mo
```
**Perfect for:**
- Short-term trading
- Momentum strategies
- Technical analysis
- Market entry/exit timing

## 🛠️ Dependencies

The script automatically reuses code from the main investment optimizer system:
- `yfinance` - Real-time stock data
- `pandas` - Data manipulation  
- `numpy` - Numerical computations
- `matplotlib` - Plotting and visualization
- `seaborn` - Statistical visualization
- `openpyxl` - Excel file support

## 🎯 Professional Features

- **📊 Institutional-Grade Analysis**: Based on Modern Portfolio Theory principles
- **🔍 Comprehensive Research**: 52-week positioning for market timing
- **📋 Portfolio Templates**: Pre-built risk-based portfolio allocations
- **📈 Flexible Analysis**: Multiple time periods and customization options
- **🎨 Presentation Ready**: High-resolution charts suitable for client meetings
- **📊 Detailed Reporting**: Professional statistics and investment insights
- **🚀 Easy to Use**: Simple command-line interface with extensive help

---

## 📝 Sample Analysis Commands

```bash
# 🏁 GETTING STARTED
python stock_analyzer.py --create-sample
python stock_analyzer.py sample_stocks.xlsx

# � TICKER-ONLY FILE ANALYSIS
echo -e "Symbol\nAAPL\nMSFT\nGOOGL\nTSLA" > my_tickers.csv
python stock_analyzer.py my_tickers.csv

# Simple Excel with just tickers
python stock_analyzer.py my_simple_tickers.xlsx

# �🛡️ CONSERVATIVE ANALYSIS
python stock_analyzer.py sample_stocks.xlsx --sheet Conservative_Portfolio --period 2y

# 🚀 AGGRESSIVE ANALYSIS  
python stock_analyzer.py sample_stocks.xlsx --sheet Aggressive_Portfolio --period 1y

# 📊 COMPREHENSIVE ANALYSIS
python stock_analyzer.py sample_stocks.xlsx --period 5y --price-period 1y --output full_analysis.png

# 💹 SHORT-TERM ANALYSIS
python stock_analyzer.py sample_stocks.xlsx --period 6mo --price-period 1mo --output momentum_analysis.png

# 🔍 CUSTOM ANALYSIS
python stock_analyzer.py my_stocks.xlsx --sheet My_Portfolio --output custom_analysis.png
```

## 🎯 Quick Reference - Ticker-Only Files

| File Type | Example Content | Command |
|-----------|----------------|---------|
| **Simple CSV** | `Symbol\nAAPL\nMSFT` | `python stock_analyzer.py tickers.csv` |
| **Simple Excel** | Column: `Ticker`, Rows: `GOOGL, AMZN` | `python stock_analyzer.py tickers.xlsx` |
| **Any Column Name** | Column: `My_Stocks`, Rows: `NVDA, META` | `python stock_analyzer.py stocks.xlsx` |
| **Multiple Sheets** | Use `--sheet SheetName` | `python stock_analyzer.py file.xlsx --sheet Sheet2` |

### ✅ **Ticker-Only File Checklist**

- [ ] File contains at least one column with stock symbols
- [ ] Symbols are valid ticker codes (AAPL, MSFT, etc.)
- [ ] No empty rows between symbols  
- [ ] File format is .xlsx, .xls, or .csv
- [ ] Internet connection available for data fetching
- [ ] Ready to analyze! 🚀

**Created by the Investment Management System team - September 2025**

🎯 **Perfect for:** Financial advisors, portfolio managers, individual investors, and anyone seeking professional-grade stock analysis with comprehensive 52-week market context - **especially powerful with simple ticker-only input files!**
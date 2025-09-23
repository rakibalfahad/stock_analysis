# 🚀 Investment Portfolio Optimizer - Complete User Guide

> A sophisticated, modular investment portfolio optimization system using Modern Portfolio Theory, featuring intelligent stock analysis, real-time monitoring, and comprehensive trading tools.

## 🌟 System Overview

### 🎯 **What This System Does**
Transform your investment strategy with professional-grade portfolio optimization tools that automatically analyze stocks, optimize allocations, and provide real-time insights for smarter investment decisions.

### ⚡ **Key Highlights**
- **📊 Advanced Analytics**: Risk/return analysis with Sharpe ratios, volatility metrics, and 52-week positioning
- **🤖 Smart Automation**: Intelligent stock filtering, automated rebalancing, and continuous monitoring
- **📈 Real-Time Data**: Live Yahoo Finance integration, market news, and price tracking
- **📋 Professional Reports**: Multi-sheet Excel exports, interactive dashboards, and comprehensive analysis
- **🛡️ Risk Management**: Sophisticated filtering system prevents high-risk investments
- **📱 Multiple Interfaces**: Command-line tools, interactive HTML dashboards, and Excel integration

### 🏆 **Perfect For**
- **Individual Investors** seeking data-driven portfolio optimization
- **Financial Advisors** requiring client portfolio analysis tools  
- **Quantitative Analysts** needing Modern Portfolio Theory implementation
- **Traders** wanting risk-adjusted position sizing and monitoring
- **Students/Researchers** learning quantitative finance concepts

## 📋 Table of Contents

### 🚀 **Getting Started**
1. [Quick Start & Installation](#-getting-started)
2. [Basic Usage & Commands](#-basic-usage)
3. [Core Features Overview](#-core-features)

### 📊 **Core Analysis Tools**
4. [Portfolio Summary Dashboard](#-portfolio-summary-dashboard)
5. [Stock Risk Analysis Tool](#-stock-risk-analysis-tool)
6. [Yahoo Finance Data Downloader](#-yahoo-finance-stock-data-downloader)
7. [Financial Metrics & Calculations](#-financial-metrics-and-calculations)

### ⚙️ **Portfolio Management**
8. [Configuration Guide](#-configuration-guide)
9. [Portfolio Optimization](#-portfolio-optimization)
10. [Stock Comparison System](#-stock-comparison-system)
11. [Intelligent Stock Filtering](#-intelligent-stock-filtering-system)

### 📈 **Trading & Monitoring**
12. [Short Trading Mode](#-short-trading-mode)
13. [Real-Time Monitoring](#-real-time-portfolio-monitoring)
14. [Live Market News Fetcher](#-live-stock-market-news-fetcher)

### 🔧 **Advanced & Technical**
15. [Advanced Features](#-advanced-features)
16. [Troubleshooting](#-troubleshooting)
17. [Development & Technical](#-development--technical)

---

## 🚀 Getting Started

### ⚡ **Quick Start** (5 minutes)

```bash
# 1. Setup environment
python -m venv stock_env && source stock_env/bin/activate  # Linux/macOS
pip install -r requirements.txt

# 2. Instant portfolio overview
python portfolio_summary.py

# 3. Analyze any stocks from Excel/CSV
python stock_analyzer.py your_stocks.xlsx

# 4. Download latest market data
python yahoo_finance_downloader.py
```

### 🛠️ **System Requirements**
- **Python 3.9+** | **Cross-platform** (Linux, macOS, Windows)
- **Internet connection** for real-time market data
- **Dependencies**: All handled by `requirements.txt`

### 🎯 **First Time? Try This:**

```bash
# Get comprehensive portfolio dashboard
python portfolio_summary.py

# Download trending stocks and analyze them
python yahoo_finance_downloader.py --categories most_active,top_gainers
python stock_analyzer.py data/yahoo_finance_data_*.xlsx

# Compare specific stocks
python main.py --compare AAPL MSFT GOOGL --plot
```

**You'll get:** Excel reports, interactive charts, and actionable investment insights!

---

## 📖 Basic Usage

### 🎯 **Common Workflows**

#### 📊 **Portfolio Analysis & Overview**
```bash
# Get comprehensive dashboard (RECOMMENDED FIRST)
python portfolio_summary.py

# Optimize current portfolio with risk filtering
python main.py --plot

# Monitor portfolio in real-time
python main.py --quick-monitor --plot
```

#### 📈 **Stock Research & Analysis**
```bash
# Download latest market data
python yahoo_finance_downloader.py

# Analyze downloaded stocks
python stock_analyzer.py data/yahoo_finance_data_*.xlsx

# Compare specific stocks
python main.py --compare AAPL MSFT --plot
```

#### 💰 **Trading & Monitoring**
```bash
# Short trading with live monitoring
python main.py --short-trading

# Continuous portfolio monitoring
python main.py --monitor --plot --interval 300
```

### 📋 **What You Get**
- **📊 Excel Reports**: Multi-sheet analysis with all metrics
- **� Interactive Charts**: Risk/return plots, price trends, allocations  
- **� Actionable Insights**: Buy/sell recommendations with position sizes
- **�️ Risk Analysis**: Sharpe ratios, volatility, 52-week positioning
- **📱 Professional Dashboards**: HTML dashboards with zoom/pan features

---

## ✨ Core Features

### 🎯 **Investment Analysis Suite**
| Feature | Benefit | Output |
|---------|---------|---------|
| **📊 Portfolio Dashboard** | Complete holdings overview | Interactive HTML + Excel |
| **🧮 Risk/Return Analysis** | Sharpe ratios, volatility metrics | Professional charts |
| **📈 Stock Comparison** | Side-by-side analysis | Scoring & recommendations |
| **🛡️ Intelligent Filtering** | Automated risk management | Conservative/Aggressive modes |

### � **Data & Research Tools**
| Feature | Benefit | Output |
|---------|---------|---------|
| **� Yahoo Finance Downloader** | Latest market data | 6 categories, Excel format |
| **� Live News Fetcher** | Market sentiment analysis | Real-time alerts & exports |
| **📋 Excel Integration** | Professional reporting | Multi-sheet comprehensive analysis |
| **⚡ Real-Time Monitoring** | Live portfolio tracking | Continuous updates |

### � **Advanced Capabilities**
- **🧮 Modern Portfolio Theory**: Mathematical optimization with efficient frontier
- **🤖 Machine Learning**: Intelligent stock scoring and risk assessment  
- **📈 Multiple Asset Classes**: Stocks, ETFs, indices, and custom portfolios
- **🌐 Cross-Platform**: Windows, macOS, Linux compatibility
- **⚡ Real-Time Data**: Live Yahoo Finance integration with API rate limiting
- **🔄 Automated Rebalancing**: Smart buy/sell recommendations with position sizing

---

## 📊 Portfolio Summary Dashboard

### Overview

The Portfolio Summary Dashboard provides a comprehensive, at-a-glance view of your entire investment portfolio. This is the **recommended starting point** for understanding your current financial position.

### Key Features

- **📊 Investment Targets & Configuration** - Shows your budget, targets, and risk profile
- **💰 Current Holdings Analysis** - Live P&L tracking with real-time market prices
- **📈 Trading History** - Complete record of sold positions and performance metrics
- **⚖️ Portfolio Allocation** - How much of your budget is invested vs available cash
- **🛡️ Risk Analysis** - Concentration risk, diversification, and position sizing warnings
- **🎯 Smart Recommendations** - Actionable insights based on your portfolio state

### Quick Start

```bash
# Run the complete portfolio dashboard
python portfolio_summary.py
```

### Dashboard Sections

#### 🎯 Investment Configuration & Targets
```
💰 Total Investment Budget: $3,000
📈 Target Gain Percentage: 25%
🛑 Maximum Loss Tolerance: 5%
⚖️ Risk Profile: Conservative (Reward:Risk = 5.0:1)
```

#### 📊 Current Active Holdings
```
Symbol   Shares   Buy Price    Current      Investment   Current Value  P&L $        P&L %
VERI     473      $3.26        $3.73        $1,541.98    $1,764.29      +$222.31     +14.4%
BW       291      $2.46        $2.78        $715.86      $808.98        +$93.12      +13.0%
RAPP     31       $22.80       $23.76       $706.80      $736.56        +$29.76      +4.2%
```

#### 💸 Sold Positions History
```
Symbol   Sale Price   Sale Date    P&L Amount   P&L %      Performance
ASST     $9.50        2025-09-11   +$1.60       +3.5%      ✅ PROFIT
BW       $2.50        2025-09-11   +$4.00       +1.6%      ✅ PROFIT
```

#### ⚖️ Portfolio Allocation Analysis
```
💰 Investment Budget: $3,000.00
📊 Current Allocation: $2,964.64 (98.8%)
💵 Available Cash: $35.36 (1.2%)
📊 Allocation: [██████████████████████████████████████████████░] 98.8%
```

#### 🛡️ Risk Analysis
```
📊 Portfolio Concentration:
   VERI: $1,541.98 (52.0% - HIGH RISK)
   BW: $715.86 (24.1% - MODERATE)
   RAPP: $706.80 (23.8% - MODERATE)
```

### When to Use the Dashboard

- **📅 Daily Check-ins** - Quick overview of portfolio performance
- **🎯 Before Making Trades** - Understand current allocation and risk
- **📊 Portfolio Rebalancing** - Identify concentration risks and opportunities
- **📈 Performance Review** - Track realized vs unrealized gains
- **🛡️ Risk Management** - Monitor position sizes and diversification

### Integration with Other Tools

The dashboard reads from both configuration files and integrates with:
- `main.py --plot` - Portfolio optimization recommendations
- `main.py --short-trading` - Real-time position monitoring
- `main.py --compare` - Stock-by-stock analysis

---

## ⚙️ Configuration Guide

### Portfolio Configuration (`investments.txt`)

This is your main configuration file for portfolio optimization:

```plaintext
# investments.txt - Your investment preferences
total_investment = 3000                    # Total capital to invest
target_gain_percentage = 25                # Annual target return (%)
maximum_loss_percentage = 5                # Maximum acceptable loss (%)
preferred_stocks = AAPL,MSFT,GOOGL,AMZN,TSLA,NVDA,META,NFLX
```

### Short Trading Configuration (`short_trading.txt`)

Separate configuration for active trading positions:

```plaintext
# short_trading.txt - Active trading settings
target_gain_percentage = 25         # Alert when stock gains 25%
maximum_loss_percentage = 5         # Alert when stock loses 5%

# Add positions using any of these formats:
# Format 1: Single position
buy_stocks = AAPL,10,220.50,2025-09-10

# Format 2: Multiple positions (pipe-separated)
# buy_stocks = AAPL,10,220.50,2025-09-10|MSFT,5,415.75,2025-09-11

# Format 3: Numbered entries
# buy_stocks_1 = TSLA,12,250.00,2025-09-10
# buy_stocks_2 = NVDA,20,135.50,2025-09-11
```

### 📁 Project Structure

```
📦 stock_analysis/
├── 🐍 main.py                          # Main entry point
├── 📊 portfolio_summary.py             # **Portfolio Dashboard** - Complete overview
├── 📊 stock_analyzer.py                # Standalone risk analysis tool
├── 📁 src/                             # Source code modules
│   ├── 📁 portfolio/                   # Portfolio optimization
│   ├── 📁 visualization/               # Dashboard and plotting
│   └── 📁 utils/                       # Utilities and helpers
├── ⚙️ investments.txt                  # Portfolio configuration
├── 💰 short_trading.txt                # Trading configuration
├── 📊 *.png                           # Generated dashboards
└── 📦 requirements.txt                 # Dependencies
```

---

## 📈 Portfolio Optimization

### How It Works

The system uses **Modern Portfolio Theory** to:
1. **Analyze your preferred stocks** from `investments.txt`
2. **Calculate optimal allocation** based on risk/return profiles
3. **Generate buy/sell recommendations** within your budget
4. **Provide risk assessments** and expected returns
5. **Create visual dashboards** for easy understanding

### Basic Portfolio Optimization

```bash
# Single optimization with dashboard
python main.py --plot

# Optimization without saving dashboard
python main.py --plot --no-save

# Custom target return (30% annually)
python main.py --plot --target-return 0.30
```

## ⚡ Real-Time Portfolio Monitoring

**⚠️ IMPORTANT**: `--interval` only works with `--monitor` flag!

```bash
# Quick monitoring (15-minute intervals) - RECOMMENDED
python main.py --quick-monitor --plot

# Custom interval monitoring (5 minutes)
python main.py --monitor --plot --interval 300

# Hourly monitoring
python main.py --monitor --plot

# Active monitoring (every minute)
python main.py --monitor --plot --interval 60
```

### Understanding Recommendations

```
🍎 AAPL: 🛍️ BUY RECOMMENDATION
   💰 Current Price: $228.63
   📈 Recommended: +10 shares ($2,286.30)
   📊 Portfolio Weight: 17.9% (optimal)
   🎯 Expected Return: 12.5%
   🛡️ Risk Level: Moderate
```

---

## 🧠 Intelligent Stock Filtering System

### Overview

The **Intelligent Stock Filtering System** is a sophisticated risk management tool that automatically analyzes and filters stocks based on multiple financial criteria. This prevents the optimizer from investing in potentially risky stocks that don't meet your risk tolerance.

### How It Works

The system analyzes each stock in your `preferred_stocks` list and assigns a recommendation:
- ✅ **BUY** - Stocks that pass all criteria and are recommended for investment
- ⏸️ **HOLD** - Stocks with mixed signals that may be worth holding but not buying
- ⚠️ **AVOID** - Stocks that fail some criteria due to elevated risk factors
- 🛑 **STRONG_AVOID** - Stocks that fail multiple criteria and should be avoided

### Filtering Modes

Choose your risk tolerance level:

```bash
# Conservative filtering (most restrictive - safest stocks only)
python main.py --plot --filtering-mode conservative

# Moderate filtering (balanced approach - default until recently)
python main.py --plot --filtering-mode moderate

# Aggressive filtering (least restrictive - allows higher risk stocks)
python main.py --plot --filtering-mode aggressive

# No filtering (use ALL configured stocks regardless of risk)
python main.py --plot --no-filter
```

### Key Filtering Criteria

| Criteria | Conservative | Moderate | Aggressive |
|----------|-------------|----------|------------|
| **P/E Ratio** | < 25 | < 35 | < 45 |
| **Volatility** | < 20% | < 35% | < 50% |
| **Market Cap** | > $10B | > $1B | > $500M |
| **Beta** | < 1.2 | < 1.5 | < 2.0 |
| **Debt/Equity** | < 50% | < 100% | < 150% |

### Adaptive Thresholds

The system automatically calculates optimal thresholds based on your stock universe:

```
🧮 ADAPTIVE THRESHOLDS DETERMINED (AGGRESSIVE MODE)
============================================================
📊 Max P/E Ratio: 46.2 (based on 7 stocks)
📈 Max Volatility: 44.5% (based on 8 stocks)
⚖️  Max Beta: 1.53
🏢 Min Market Cap: $1.0B
💧 Min Daily Volume: $1.0M
```

### Sample Filtering Output

```
📊 STOCK FILTERING RESULTS
======================================================================

✅ AMZN - BUY
   💰 Price: $231.62 | 📊 Score: +15 | Confidence: 75%
   ✅ Positives: Adequate market cap: $2470.2B, Good liquidity: $8375.2M daily

⚠️ NVDA - AVOID
   💰 Price: $170.29 | 📊 Score: -45 | Confidence: 90%
   ⚠️ Concerns: High P/E ratio: 48.4 (max: 46.2), High volatility: 49.8% (max: 44.5%)

📊 FILTERING SUMMARY
✅ Recommended to BUY: 2 stocks (MSFT, AMZN)
⚠️ Recommended to AVOID: 3 stocks (NFLX, NVDA, TSLA)
```

### Automatic Relaxation

If too few stocks pass filtering, the system automatically relaxes criteria to ensure diversification:

```
⚠️ Only 1 stocks passed strict filtering!
Relaxing criteria to ensure at least 5 stocks for diversification...
🧮 Relaxing filtering criteria...
   📊 P/E: 36.9 → 40.0
   📈 Volatility: 34.3% → 44.5%
   ⚖️ Beta: 1.50 → 1.80
```

### When to Use Each Mode

- **Conservative**: For retirement accounts, risk-averse investors, or market uncertainty
- **Moderate**: Balanced approach for most investors (previous default)
- **Aggressive**: For growth-focused portfolios, younger investors, or bull markets (current default)
- **No Filter**: For experienced investors who want complete control over their stock selection

### Why Filtering Was Added

Without filtering, the optimizer might allocate significant capital to high-risk stocks (high volatility, excessive P/E ratios, or overleveraged companies), which could lead to substantial losses during market downturns.

---

## ⚡ Stock Comparison System

### Overview

Compare any two stocks with intelligent, strategy-based analysis that uses your investment configuration for personalized recommendations.

### Basic Comparison

```bash
# Basic comparison with balanced strategy
python main.py --compare AAPL MSFT

# Growth-focused comparison with charts
python main.py --compare AAPL GOOGL --strategy growth --plot

# Value investing comparison
python main.py --compare BRK.B JPM --strategy value --plot
```

### Available Strategies

| Strategy | Focus | Best For |
|----------|-------|----------|
| `balanced` | Equal weighting across all metrics | General investing |
| `growth` | Growth metrics and momentum | Growth investors |
| `value` | Valuation and financial health | Value investors |
| `income` | Dividends and stability | Income seekers |
| `conservative` | Risk management focus | Conservative investors |
| `aggressive` | High growth potential | Risk-tolerant investors |

### Comparison Output

```
⚡ STOCK COMPARISON: AAPL vs MSFT
======================================================================
🏢 Company Information:
   AAPL: Apple Inc. (Technology)
   MSFT: Microsoft Corporation (Technology)

🎯 Category Analysis (Growth Strategy):
   Valuation (Weight: 15%):     🥇 AAPL: 0.62  🥉 MSFT: 0.38
   Growth (Weight: 35%):        🥉 AAPL: 0.07  🥇 MSFT: 0.93
   Financial Health (Weight: 20%): 🥉 AAPL: 0.00  🥇 MSFT: 1.00

🚀 RECOMMENDATION: BUY MSFT (Confidence: 90%)
   💪 Key Advantages:
      • Stronger revenue growth (18.1% vs 9.6%)
      • Better financial health (D/E: 32.7% vs 154.5%)
      • Higher dividend yield (0.66% vs 0.45%)
```

---

## 💰 Short Trading Mode

### Overview

Real-time profit/loss monitoring for active trading positions with automatic alerts and professional display.

### Quick Start

```bash
# Start monitoring with default 1-minute updates
python main.py --short-trading

# Day trading mode (30-second updates)
python main.py --short-trading --interval 30

# Ultra-fast monitoring (5-second updates)
python main.py --short-trading --interval 5
```

### Adding Positions

Choose any format in `short_trading.txt`:

**Single Position:**
```plaintext
buy_stocks = AAPL,10,220.50,2025-09-10
```

**Multiple Positions (Pipe-separated):**
```plaintext
buy_stocks = AAPL,10,220.50,2025-09-10|MSFT,5,415.75,2025-09-11|GOOGL,8,185.25,2025-09-09
```

**Numbered Entries:**
```plaintext
buy_stocks_1 = TSLA,12,250.00,2025-09-10
buy_stocks_2 = NVDA,20,135.50,2025-09-11
buy_stocks_3 = META,7,560.75,2025-09-09
```

### Live Monitoring Display

```
================================================================================
📊 SHORT TRADING PORTFOLIO STATUS - 2025-09-12 14:30:15
================================================================================
Symbol   Shares   Buy Price    Current      P&L $        P&L %      Status
--------------------------------------------------------------------------------
AAPL     10       $220.50      $226.78      +$62.80      +2.8%     ✅ HOLD
MSFT     5        $415.75      $422.15      +$32.00      +1.5%     ✅ HOLD
AMZN     8        $185.25      $179.80      -$43.60      -2.9%     ⚠️ WATCH
--------------------------------------------------------------------------------
TOTAL                                       +$51.20                   
================================================================================
```

### Alert System

**🎯 Target Gain Alert:**
```
🚨 SELL ALERT: AAPL reached target gain of 25%! 🚨
💰 Current: $275.63 | Buy Price: $220.50
💡 Gain: +$551.30 (+25.0%)
⭐ RECOMMENDATION: Consider taking profits
```

**🛡️ Stop Loss Alert:**
```
🚨 SELL ALERT: AMZN hit stop loss threshold! 🚨
📉 Current: $176.00 | Buy Price: $185.25
💸 Loss: -$74.00 (-5.0%)
🛡️ RECOMMENDATION: Consider cutting losses
```

---

## 📊 Stock Risk Analysis Tool

### Overview

Comprehensive stock analysis system with **dual output options**: professional visualization charts and detailed Excel reports. Performs risk vs return analysis with 52-week positioning, sector analysis, and performance metrics.

### 🆕 **Two Analysis Tools Available:**

#### **📊 Visual Charts (`stock_analyzer.py`)**
- **Professional PNG charts** with risk vs return scatter plots
- **52-week positioning indicators** (🔥 Near High, ⚡ Mid-Range, ❄️ Near Low)
- **Dual color coding** for Sharpe ratios and market positioning
- **Side-by-side visualizations** with comprehensive statistics

#### **📈 Excel Reports (`stock_analyzer_excel.py`)**
- **Multi-sheet Excel workbooks** with detailed analysis
- **7 comprehensive sheets**: Analysis, Summary, Sectors, Top Performers, High Risk, Near Highs, Errors
- **Sortable and filterable data** for in-depth analysis
- **Complete metrics** including company info, sectors, and market caps

### Quick Start

#### **For Visual Analysis (PNG Charts):**
```bash
# Create sample files
python stock_analyzer.py --create-sample

# Analyze stocks from your Excel file
python stock_analyzer.py your_stocks.xlsx

# Custom chart output name
python stock_analyzer.py your_stocks.xlsx --output my_analysis.png

# 2-year analysis period
python stock_analyzer.py your_stocks.xlsx --period 2y
```

#### **For Excel Reports (Detailed Data):**
```bash
# Generate comprehensive Excel report
python stock_analyzer_excel.py your_stocks.xlsx

# Custom Excel output name
python stock_analyzer_excel.py your_stocks.xlsx --output detailed_analysis.xlsx

# Analyze specific sheet
python stock_analyzer_excel.py your_stocks.xlsx --sheet Portfolio1

# Different analysis period
python stock_analyzer_excel.py your_stocks.xlsx --period 2y --output results.xlsx
```

#### **For Complete Analysis (Both Outputs):**
```bash
# Generate both chart and Excel report
python stock_analyzer.py your_stocks.xlsx --output visual_analysis.png
python stock_analyzer_excel.py your_stocks.xlsx --output data_analysis.xlsx
```

### Sample Excel Structure

The system includes 6 professional analysis sheets:

1. **📊 All_Stocks** - Complete dataset (16 stocks)
2. **🛡️ Conservative_Portfolio** - Low-risk, dividend stocks
3. **⚖️ Moderate_Portfolio** - Balanced growth stocks  
4. **🚀 Aggressive_Portfolio** - High-growth stocks
5. **📈 Sector_Analysis** - Sector breakdown
6. **📚 Instructions** - Usage guide

### Analysis Output

```
🎯 KEY INSIGHTS:
🏆 Best Expected Return: SHOP (93.5%)
📊 Best Sharpe Ratio: NFLX (2.03)
🛡️ Lowest Risk: MSFT (24.9%)

🔥 52-WEEK ANALYSIS:
🔥 Near 52W High (>80%): GOOGL, NVDA, META, NFLX
❄️ Near 52W Low (<20%): CRM, ADBE
📏 Widest 52W Range: SPOT (143.5% range)
```

---

## 📡 Live Stock Market News Fetcher

### Overview

A comprehensive **free, unlimited** stock market news fetcher that monitors live market news across all sectors and automatically identifies affected stocks. Features multiple news sources, intelligent stock detection, sentiment analysis, and continuous monitoring capabilities.

### 🆕 **Key Features:**

- **🆓 Free & No Limits**: Uses public RSS feeds and free APIs without restrictions
- **🌍 Generalized Market Coverage**: Monitors all sectors, not just specific stocks  
- **🎯 Smart Stock Detection**: Automatically identifies affected stocks in headlines
- **📊 Three Operating Modes**: General, Major Sectors, and Specific Stocks
- **💡 Sentiment Analysis**: Classifies news as positive/negative/neutral
- **🏷️ News Categorization**: Earnings, mergers, analyst reports, regulatory, etc.
- **📊 CSV Export**: Automatic data export for analysis
- **⏰ Continuous Monitoring**: Real-time updates with customizable intervals
- **🌐 Multiple Sources**: Yahoo Finance, MarketWatch, YFinance API
- **💾 Smart Caching**: Prevents duplicate fetches and maintains history

### 🚀 **Quick Start**

```bash
# Install additional dependencies
pip install feedparser requests python-dateutil

# General market news (RECOMMENDED - all sectors)
python stock_news_fetcher.py --general

# Major market sectors (84+ symbols across all sectors)
python stock_news_fetcher.py

# Monitor specific stocks only
python stock_news_fetcher.py --stocks AAPL GOOGL TSLA NVDA

# Show limited results
python stock_news_fetcher.py --general --limit 10
```

### 📊 **Three Operating Modes**

#### **1. 🌍 General Mode (--general) - RECOMMENDED**
```bash
python stock_news_fetcher.py --general
```
- **✅ Best for**: Comprehensive market intelligence
- **📊 Coverage**: ALL market news across sectors
- **🎯 Detection**: Automatically finds any stock symbols in headlines
- **📈 Includes**: Indices (SPY, QQQ), crypto (BTC-USD, ETH-USD), commodities (GLD, USO)
- **🔍 Smart Filtering**: Focuses on real ticker symbols, filters noise

#### **2. 📊 Major Sectors Mode (Default)**
```bash
python stock_news_fetcher.py
```
- **✅ Best for**: Broad market sector coverage
- **📊 Coverage**: 84+ major market symbols across sectors:
  - **Indices & ETFs**: SPY, QQQ, DIA, IWM, VTI, VOO, VEA, VWO
  - **Technology**: AAPL, GOOGL, MSFT, AMZN, META, NVDA, TSLA, NFLX
  - **Healthcare**: JNJ, PFE, UNH, ABBV, BMY, MRK, LLY, TMO
  - **Financial**: JPM, BAC, WFC, GS, MS, BRK-B, V, MA, COIN
  - **Energy**: XOM, CVX, COP, SLB, EOG, NEE, DUK, SO
  - **Consumer**: WMT, TGT, HD, LOW, NKE, SBUX, MCD, DIS
  - **Industrial**: CAT, BA, GE, MMM, HON, UPS, FDX, LMT
  - **Commodities**: GLD, SLV, USO, UNG, GOLD, NEM, FCX, AA
  - **Crypto**: BTC-USD, ETH-USD, COIN, MSTR, RIOT, MARA
  - **Bonds**: TLT, IEF, SHY, HYG, LQD, TIP

#### **3. 🎯 Specific Stocks Mode (--stocks)**
```bash
python stock_news_fetcher.py --stocks AAPL GOOGL TSLA NVDA
```
- **✅ Best for**: Focused portfolio monitoring
- **📊 Coverage**: Only specified symbols
- **🎯 Perfect for**: Tracking specific positions or watchlists

### ⏰ **Continuous Monitoring**

```bash
# General mode with continuous monitoring (every 60 minutes)
python stock_news_fetcher.py --general --continuous

# Quick updates every 30 minutes, show top 5 items
python stock_news_fetcher.py --general --continuous --interval 30 --limit 5

# Day trading mode (every 5 minutes), top 3 news items
python stock_news_fetcher.py --general --continuous --interval 5 --limit 3

# Run for specific number of updates then stop
python stock_news_fetcher.py --general --continuous --iterations 10 --limit 8
```

### 📊 **Sample Output**

```
🚀 Stock Market News Fetcher Initialized
📊 General market news monitoring (all sectors and symbols)
🗞️ Using 5 news sources

🗞️ LATEST STOCK MARKET NEWS (8 items)
====================================================================================================

1. 📈 💰 Federal Reserve Policy Decision Pending
   🏢 Affected Stocks: TLT
   📅 2025-09-17 12:29 | 🌐 Market News (General)
   📊 Sentiment: Positive | 📂 Category: Regulatory
   📄 Financial markets await central bank announcement affecting bonds TLT and equities

2. ➡️ 📰 Stock Market Indices Hit Record Highs  
   🏢 Affected Stocks: SPY, QQQ, DIA
   📅 2025-09-17 12:29 | 🌐 Market News (General)
   📊 Sentiment: Neutral | 📂 Category: General
   📄 Major indices SPY, QQQ, and DIA reach new peaks amid investor optimism

3. ➡️ 📰 Cryptocurrency Market Shows Volatility
   🏢 Affected Stocks: BTC-USD, ETH-USD
   📅 2025-09-17 12:29 | 🌐 Market News (General)
   📊 Sentiment: Neutral | 📂 Category: General
   📄 Bitcoin BTC-USD and Ethereum ETH-USD experience significant price swings

📊 STOCK MENTION STATISTICS
==================================================
 1. SPY: 3 mentions
    ➡️ Stock Market Indices Hit Record Highs...
    ➡️ S&P 500 Reaches New All-Time High on Tech Rally...
 2. QQQ: 2 mentions
    ➡️ Stock Market Indices Hit Record Highs...
    ➡️ S&P 500 Reaches New All-Time High on Tech Rally...
```

### 💾 **Data Export & Caching**

#### **CSV Export (On Demand)**
CSV files are only created when explicitly requested:
```bash
# Export to custom file
python stock_news_fetcher.py --general --export my_market_news.csv

# No CSV files created by default
python stock_news_fetcher.py --general  # Clean run, no files
```

#### **Smart Caching**
- `news_cache.json` - Prevents duplicate API calls
- Maintains news history between runs
- Automatic cache updates with timestamps

### 🔄 **Integration with Trading Systems**

The news fetcher complements your existing tools:

```bash
# Morning routine: Check news + portfolio
python stock_news_fetcher.py --general --limit 15
python portfolio_summary.py

# Pre-market analysis
python stock_news_fetcher.py --general --continuous --interval 30 &
python main.py --quick-monitor --plot

# Active trading monitoring
python stock_news_fetcher.py --general --continuous --interval 5 &
python main.py --short-trading --interval 30
```

### 🎯 **News Categories & Sentiment**

#### **📂 Categories Detected:**
- **💰 Earnings**: Revenue, profits, quarterly reports, guidance
- **🤝 Merger**: Acquisitions, takeovers, corporate deals  
- **⚖️ Lawsuit**: Legal issues, court cases, settlements
- **🚀 Product**: Launches, innovations, patents, releases
- **🤜 Partnership**: Collaborations, agreements, contracts
- **📊 Analyst**: Upgrades, downgrades, price targets, ratings
- **🏛️ Regulatory**: FDA approvals, investigations, compliance
- **💵 Financial**: Dividends, buybacks, debt, financing, IPOs

#### **📊 Sentiment Analysis:**
- **📈 Positive**: "surge", "gain", "beat", "strong", "growth", "approval"
- **📉 Negative**: "drop", "decline", "miss", "weak", "concern", "warning"  
- **➡️ Neutral**: Balanced or purely factual headlines



### 📋 **Complete Command Reference**

```bash
# Basic Operations
python stock_news_fetcher.py --general                    # General market news
python stock_news_fetcher.py                              # Major sectors (84+ symbols)
python stock_news_fetcher.py --stocks AAPL GOOGL TSLA     # Specific stocks

# Continuous Monitoring  
python stock_news_fetcher.py --general --continuous       # Every 60 minutes
python stock_news_fetcher.py --general --continuous --interval 30  # Every 30 minutes
python stock_news_fetcher.py --general --continuous --iterations 5 # 5 updates then stop

# Output Control
python stock_news_fetcher.py --general --limit 15         # Show 15 latest items
python stock_news_fetcher.py --general --export news.csv  # Export to CSV file
python stock_news_fetcher.py --general --continuous --interval 30 --limit 5  # Continuous with limit

# Advanced Options
python stock_news_fetcher.py --general --cache my_cache.json       # Custom cache file
python stock_news_fetcher.py --help                               # Show all options
```

### 🎯 **Use Cases**

#### **📈 For Active Traders:**
```bash
# Pre-market news scan (no files created)
python stock_news_fetcher.py --general --limit 20

# Continuous day trading alerts (clean monitoring)  
python stock_news_fetcher.py --general --continuous --interval 5 --limit 3
```

#### **💼 For Portfolio Managers:**
```bash
# Daily market intelligence (clean monitoring)
python stock_news_fetcher.py --general --continuous --interval 60 --limit 10

# Sector-specific monitoring
python stock_news_fetcher.py --stocks SPY QQQ DIA VTI --continuous --limit 8
```

#### **🔍 For Market Researchers:**
```bash
# Comprehensive data collection with export
python stock_news_fetcher.py --general --continuous --interval 60 --export research_data.csv

# Historical news analysis (export when needed)
python stock_news_fetcher.py --general --iterations 20 --interval 30 --export historical.csv
```


### 📁 Generated Files

- **`news_cache.json`** — Cached news data and timestamps (always created for performance)
- **Custom CSV files** — Only created when using `--export filename.csv`
- **🚫 No automatic files** — Clean workspace by default

---

## 🔧 Advanced Features

### File Management

```bash
# Keep timestamped files for history
python main.py --plot --keep-timestamp

# Clean up old files (keep 5 latest)
python main.py --cleanup 5
```

### Custom Parameters

```bash
# Custom target return (30%)
python main.py --plot --target-return 0.30

# Lower risk per trade (1%)
python main.py --plot --risk-per-trade 0.01
```

### Dual System Operation

Run both systems simultaneously for comprehensive coverage:

```bash
# Terminal 1: Long-term portfolio monitoring
python main.py --monitor --plot --interval 300

# Terminal 2: Short-term active trading
python main.py --short-trading --interval 30
```

### Integration Workflow

1. **Get Recommendations**: Run portfolio optimizer
2. **Execute Trades**: Buy through your broker
3. **Record Positions**: Add to `short_trading.txt`
4. **Monitor Live**: Start short trading mode

---

## 🔧 Troubleshooting

### Common Issues

#### Wrong Interval Usage
```
⚠️ WARNING: --interval ignored in single-run mode
💡 Use --monitor flag to enable interval-based monitoring
```

**Solution:** Add `--monitor` flag:
```bash
# ❌ Wrong
python main.py --plot --interval 300

# ✅ Correct  
python main.py --monitor --plot --interval 300
```

#### Invalid Stock Symbol
```
❌ WARNING: Symbol 'XYZ' not found
🔄 Skipping invalid symbol, continuing with others
```

**Solution:** Check `investments.txt` for valid ticker symbols.

#### Network Issues
```
❌ ERROR: Failed to fetch data for MSFT
🌐 Network issue detected - retrying in 30 seconds...
```

**Solution:** Check internet connection; system will auto-retry.

### Performance Notes

- **Memory Usage**: 50-500MB depending on portfolio size
- **CPU Usage**: Brief spikes during optimization (2-5 seconds)
- **Disk Usage**: 1-3MB per dashboard image

### Expected Warnings (Normal)

Font warnings are cosmetic only:
```
UserWarning: Glyph missing from font(s) DejaVu Sans.
```
All functionality remains intact.

---

## 👨‍💻 Development & Technical

### Testing Modules

```bash
# Test individual components
python -c "from src.utils.constants import EMOJIS; print(f'Loaded {len(EMOJIS)} emojis')"

python -c "from src.portfolio.optimizer import InvestmentOptimizer; print('Portfolio module loaded')"
```

### Dependencies

**Core Requirements:**
- `yfinance>=0.2.18` - Real-time stock data
- `pandas>=2.0.0` - Data manipulation  
- `numpy>=1.24.0` - Numerical computations
- `scipy>=1.10.0` - Scientific computing
- `matplotlib>=3.7.0` - Plotting
- `seaborn>=0.12.0` - Statistical visualization
- `openpyxl>=3.1.0` - Excel support

### Module Architecture

- **Portfolio Module**: Core optimization logic
- **Visualization Module**: Dashboard generation  
- **Utils Module**: Constants and helpers
- **Main Entry**: Command-line interface

### Migration from V1.0

If upgrading from the monolithic version:

1. **Backup data**: Copy `investments.txt` and dashboards
2. **Use new entry**: Run `main.py` instead of old script
3. **Same functionality**: All features preserved with improvements
4. **Clean up**: Use `--cleanup` for old files

---

## 📜 License

Investment Management System - September 2025

---

## 🎯 Quick Reference

### Most Used Commands
```bash
# Portfolio overview dashboard (START HERE)
python portfolio_summary.py

# Portfolio optimization
python main.py --plot

# Live market news (general mode - all sectors)
python stock_news_fetcher.py --general

# Stock comparison  
python main.py --compare AAPL MSFT --plot

# Continuous monitoring
python main.py --quick-monitor --plot

# Short trading
python main.py --short-trading

# Continuous news monitoring (every 30 minutes)
python stock_news_fetcher.py --general --continuous --interval 30

# Help
python main.py --help
```

### Key Files
- `portfolio_summary.py` - **Comprehensive portfolio dashboard**
- `stock_news_fetcher.py` - **Live market news fetcher** (free, unlimited, all sectors)
- `yahoo_finance_downloader.py` - **Yahoo Finance stock data downloader**
- `investments.txt` - Portfolio optimization settings
- `short_trading.txt` - Active trading positions
- `main.py` - Core system entry point

### Output Files
- `portfolio_dashboard.png` - Latest optimization results
- `stock_comparison_*.png` - Comparison charts
- `stock_news_*.csv` - Market news exports with timestamps
- `news_cache.json` - Cached news data and history
- `yahoo_finance_data_*.xlsx` - Yahoo Finance stock data exports
- `sample_stocks.xlsx` - Example data

---

## 📊 Yahoo Finance Stock Data Downloader

### Overview

The **Yahoo Finance Stock Data Downloader** is a comprehensive tool that downloads and organizes stock data from Yahoo Finance into Excel files. It provides access to 6 different stock categories, making it easy to analyze market trends and discover investment opportunities.

### Available Stock Categories

1. **📈 Most Active** - Stocks with highest trading volume
2. **🔥 Trending Now** - Currently trending stocks
3. **🚀 Top Gainers** - Best performing stocks today
4. **📉 Top Losers** - Worst performing stocks today
5. **🏆 52 Week Gainers** - Best performers over the past year
6. **⬇️ 52 Week Losers** - Worst performers over the past year

### Quick Usage

```bash
# Download all categories for today
python yahoo_finance_downloader.py

# Download specific categories
python yahoo_finance_downloader.py --categories most_active trending gainers

# Download for a specific date
python yahoo_finance_downloader.py --date 2024-01-15

# Custom output directory
python yahoo_finance_downloader.py --output-dir /path/to/your/data/folder
```

### Features

- **📊 Multi-Sheet Excel Files** - Each category gets its own sheet
- **📅 Date-Specific Naming** - Files named by download date (`yahoo_finance_data_2024-01-15.xlsx`)
- **🔄 Progress Tracking** - Real-time download progress with stock counts
- **⚡ Rate Limiting** - Respects Yahoo Finance API limits
- **🛡️ Error Handling** - Robust error recovery and logging
- **📈 Rich Data** - Includes price, volume, market cap, and performance metrics
- **💰 Smart Formatting** - Volume in millions, Market Cap in billions for easy reading
- **📍 52W Range Position** - Shows current price position in 52-week range as percentage
- **🎯 Comprehensive Data** - 14+ data fields per stock including sector, industry, P/E ratio

### Data Fields Included

Each stock entry contains:
- **Symbol** - Stock ticker symbol
- **Company Name** - Full company name
- **Current Price** - Current stock price
- **Change** - Price change from previous close
- **Change %** - Percentage change from previous close
- **Volume (M)** - Trading volume in millions
- **Average Volume (M)** - Average trading volume in millions
- **Market Cap (B)** - Market capitalization in billions
- **52 Week High** - Highest price in past 52 weeks
- **52 Week Low** - Lowest price in past 52 weeks
- **52W Range Position %** - Current position in 52-week range (0-100%)
- **P/E Ratio** - Price-to-earnings ratio
- **Sector** - Industry sector
- **Industry** - Specific industry

### Integration with Portfolio System

The downloaded data can be used with the main portfolio optimization system:

```bash
# Use downloaded stocks for analysis
python main.py --analyze-file data/yahoo_finance_data_2024-01-15.xlsx

# Import trending stocks into your portfolio
python portfolio_summary.py --import-yahoo-data data/yahoo_finance_data_2024-01-15.xlsx
```

### Examples

```bash
# Market research workflow
python yahoo_finance_downloader.py --categories most_active trending
python main.py --compare-stocks --source data/yahoo_finance_data_*.xlsx

# Weekly analysis
python yahoo_finance_downloader.py --categories gainers losers_52w gainers_52w
python portfolio_summary.py --weekly-analysis --data-source yahoo
```

### Output Structure

```
data/
├── yahoo_finance_data_2024-01-15.xlsx
│   ├── Most Active (50+ stocks)
│   ├── Trending Now (25+ stocks)  
│   ├── Top Gainers (25+ stocks)
│   ├── Top Losers (25+ stocks)
│   ├── 52 Week Gainers (25+ stocks)
│   └── 52 Week Losers (25+ stocks)
```

---

## 📊 Financial Metrics and Calculations

### Overview

The stock analysis system calculates comprehensive financial metrics for each stock using Modern Portfolio Theory and quantitative finance principles. All calculations are based on historical price data and market information retrieved from Yahoo Finance.

### Core Metrics Explained

#### 📈 **Expected Return (%)**
**Formula:** `Expected Return = Mean Daily Return × 252`

- **Calculation:** Average of daily percentage price changes over the analysis period (default: 1 year)
- **Annualization:** Multiplied by 252 (average trading days per year)
- **Interpretation:** Projected annual return based on historical performance
- **Example:** If daily returns average 0.08%, expected annual return = 0.08% × 252 = 20.16%

#### 📊 **Risk/Volatility (%)**
**Formula:** `Volatility = Standard Deviation of Daily Returns × √252`

- **Calculation:** Standard deviation of daily percentage price changes
- **Annualization:** Multiplied by square root of 252 for proper volatility scaling
- **Interpretation:** Measure of price fluctuation risk - higher values indicate more volatile stocks
- **Example:** Daily volatility of 2% = Annual volatility of 2% × √252 ≈ 31.75%

#### ⚡ **Sharpe Ratio**
**Formula:** `Sharpe Ratio = (Expected Return - Risk-Free Rate) / Volatility`

- **Risk-Free Rate:** 2% annually (configurable, represents treasury bond yield)
- **Calculation:** Excess return per unit of risk
- **Interpretation:** 
  - **> 1.0:** Excellent risk-adjusted return
  - **0.5 - 1.0:** Good risk-adjusted return  
  - **< 0.5:** Poor risk-adjusted return
  - **Negative:** Returns below risk-free rate
- **Example:** (15% return - 2% risk-free) / 20% volatility = 0.65 Sharpe ratio

#### 💰 **Market Cap Proxy**
**Formula:** `Market Cap Proxy = Current Price × Average Volume (30 days) / 1,000,000`

- **Purpose:** Approximate market capitalization in millions
- **Calculation:** Uses trading volume as liquidity indicator
- **Limitations:** Simplified proxy, not actual market cap
- **Usage:** Bubble size in risk/return visualizations

#### 📍 **52-Week Range Position (%)**
**Formula:** `Position = (Current Price - 52W Low) / (52W High - 52W Low) × 100`

- **Range:** 0% (at 52-week low) to 100% (at 52-week high)
- **Interpretation:**
  - **80-100%:** 🔥 Near 52-week high (momentum/strength)
  - **20-80%:** ⚡ Mid-range (neutral position)
  - **0-20%:** ❄️ Near 52-week low (potential value/risk)

### Advanced Metrics

#### 📉 **Maximum Drawdown**
**Formula:** `Max Drawdown = Max((Peak - Trough) / Peak)`

- **Calculation:** Largest peak-to-trough decline over the analysis period
- **Purpose:** Measures worst-case historical loss
- **Usage:** Risk assessment and position sizing

#### 📊 **Daily Returns Calculation**
**Formula:** `Daily Return = (Price[t] - Price[t-1]) / Price[t-1]`

- **Method:** Percentage change between consecutive trading days
- **Requirements:** Minimum 30 days of data for statistical validity
- **Preprocessing:** Outliers and gaps handled automatically

### Data Requirements and Quality

#### **Minimum Data Standards**
- **Historical Period:** 1 year default (configurable: 1d to 10y)
- **Minimum Days:** 30 trading days for statistical validity
- **Data Sources:** Yahoo Finance API with real-time updates
- **Quality Checks:** Automatic detection of insufficient or corrupted data

#### **Calculation Periods**
- **Risk/Return Analysis:** 1 year historical data (252 trading days)
- **Price Trends:** 30 days for visualization (configurable)
- **Volume Averaging:** 30-day rolling average for market cap proxy
- **52-Week Range:** Trailing 252 trading days

### Statistical Assumptions

#### **Modern Portfolio Theory Framework**
- **Normal Distribution:** Daily returns assumed normally distributed
- **Stationarity:** Historical patterns expected to continue
- **Liquidity:** All positions can be entered/exited at market prices
- **No Transaction Costs:** Pure theoretical returns

#### **Risk-Free Rate**
- **Default:** 2% annually (US Treasury benchmark)
- **Purpose:** Sharpe ratio calculation baseline
- **Adjustable:** Can be modified for different economic environments

### Interpretation Guidelines

#### **Portfolio Construction**
- **High Sharpe Ratio (>1.0):** Priority candidates for portfolio inclusion
- **Balanced Risk-Return:** Target 8-15% expected return with <25% volatility
- **Position Sizing:** Use volatility for risk-adjusted position weights
- **Diversification:** Combine low-correlation assets across sectors

#### **Risk Assessment**
- **Volatility Buckets:**
  - Low Risk: <20% volatility
  - Medium Risk: 20-40% volatility  
  - High Risk: >40% volatility
- **52-Week Position:** Near highs suggest momentum, near lows suggest value opportunities

#### **Performance Evaluation**
- **Benchmark Comparison:** Compare Sharpe ratios to market indices
- **Risk-Adjusted Returns:** Focus on return per unit of risk
- **Drawdown Analysis:** Assess maximum potential losses

### Example Calculation

**Stock Example: AAPL**
```
Historical Data: 252 days of closing prices
Daily Returns: [-0.5%, +1.2%, +0.8%, -0.3%, ...] 
Mean Daily Return: 0.068%
Daily Volatility: 1.87%

Calculations:
Expected Return = 0.068% × 252 = 17.1%
Volatility = 1.87% × √252 = 29.7%
Sharpe Ratio = (17.1% - 2.0%) / 29.7% = 0.51
52W Position = (254.43 - 168.80) / (259.18 - 168.80) = 94.7%
```

### Technical Implementation

The calculations are implemented in the `calculate_risk_return_metrics()` method of the `StockAnalyzer` class, ensuring:

- **Numerical Stability:** Proper handling of division by zero and edge cases
- **Data Validation:** Automatic screening for insufficient or corrupted data
- **Performance Optimization:** Vectorized operations using NumPy and Pandas
- **Error Handling:** Graceful degradation when data is unavailable

**🚀 Ready to optimize your investment portfolio? Start with the Quick Start section above!**
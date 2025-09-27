# 🚀 Investment Portfolio Optimizer

> **Professional-grade portfolio optimization system** using Modern Portfolio Theory with intelligent stock analysis, real-time monitoring, and comprehensive trading tools.

## ⚡ Quick Start (5 minutes)

```bash
# 1. Setup environment
python -m venv stock_env && source stock_env/bin/activate  # Linux/macOS
pip install -r requirements.txt

# 2. Portfolio overview dashboard (START HERE)
python portfolio_summary.py

# 3. Portfolio optimization with visualization
python main.py --plot

# 4. Trading horizons analysis
python main.py --horizons --plot

# 5. Live Yahoo Finance analyzer
python yahoo_finance_data_analyzer.py
```

## 🌟 What This System Does

Transform your investment strategy with **professional-grade portfolio optimization** that automatically:
- ✅ **Analyzes stocks** using Modern Portfolio Theory with 17+ financial metrics
- ✅ **Optimizes allocations** based on risk/return profiles within your budget  
- ✅ **Generates recommendations** with buy/sell signals and position sizing
- ✅ **Monitors real-time** with live Yahoo Finance data and market news
- ✅ **Categorizes by trading horizons** (Long-term/Short-term/Day trading)
- ✅ **Creates professional dashboards** with interactive charts and Excel reports

### 🏆 Perfect For
- **📈 Individual Investors**: Data-driven portfolio optimization and risk management
- **💼 Financial Advisors**: Professional client portfolio analysis and reporting tools
- **🧮 Quantitative Analysts**: Modern Portfolio Theory implementation with customizable parameters
- **📊 Active Traders**: Risk-adjusted position sizing and real-time monitoring systems
- **🎓 Students/Researchers**: Learning quantitative finance with practical applications

## 📋 Navigation

| **🚀 Core Tools** | **📊 Analysis** | **⚙️ Configuration** | **📈 Advanced** |
|-------------------|-----------------|----------------------|-----------------|
| [Portfolio Overview](#-portfolio-overview) | [Trading Horizons](#-trading-horizons-analysis) | [Setup Guide](#-system-setup) | [Live Data Analyzer](#-live-yahoo-finance-analyzer) |
| [Optimization](#-portfolio-optimization) | [Stock Comparison](#-stock-comparison) | [Configuration](#-configuration) | [Market News](#-market-news-fetcher) |
| [Risk Analysis](#-risk-analysis-tool) | [Filtering System](#-intelligent-filtering) | [Troubleshooting](#-troubleshooting) | [Technical Details](#-technical-reference) |

---

## 🏠 System Setup

### 🛠️ Requirements
- **Python 3.9+** | **Cross-platform** (Linux, macOS, Windows)
- **Internet connection** for real-time market data
- **Dependencies**: All handled by `requirements.txt`

### 📁 Project Structure
```
📦 stock_analysis/
├── 🐍 main.py                          # Main entry point
├── 📊 portfolio_summary.py             # Portfolio dashboard
├── 📊 yahoo_finance_data_analyzer.py   # Live market analyzer
├── 📊 stock_analyzer.py                # Risk analysis tool
├── 📰 stock_news_fetcher.py            # Market news fetcher
├── 📁 src/                             # Source modules
├── ⚙️ investments.txt                  # Portfolio configuration
├── 💰 short_trading.txt                # Trading configuration
└── 📦 requirements.txt                 # Dependencies
```

### 🎯 First-Time Setup
```bash
# Complete setup in 3 steps
git clone https://github.com/rakibalfahad/stock_analysis.git
cd stock_analysis
python -m venv stock_env && source stock_env/bin/activate  # Linux/macOS
pip install -r requirements.txt

# Test installation
python portfolio_summary.py
```

## � Portfolio Overview

The **Portfolio Summary Dashboard** is your command center - providing a comprehensive view of your entire investment portfolio with real-time tracking and professional analysis.

### � Quick Start
```bash
# Complete portfolio dashboard (START HERE)
python portfolio_summary.py

# Portfolio optimization with visualization
python main.py --plot

# Trading horizons analysis (Long/Short/Day trading)
python main.py --horizons --plot

# Real-time monitoring
python main.py --quick-monitor --plot
```

### � What You Get
- **� Investment Configuration**: Budget, targets, and risk profile
- **📈 Holdings Analysis**: Live P&L tracking with current market prices
- **💸 Trading History**: Complete record of sold positions and performance
- **⚖️ Portfolio Allocation**: Investment vs available cash with visual charts
- **🛡️ Risk Analysis**: Concentration risk and diversification warnings
- **🎯 Smart Recommendations**: Actionable insights based on portfolio state

### 📋 Sample Output
```
💰 Total Investment Budget: $3,000
📊 Current Allocation: $2,964.64 (98.8%)
💵 Available Cash: $35.36 (1.2%)

Symbol   Investment   Current Value  P&L $        P&L %      Status
VERI     $1,541.98    $1,764.29      +$222.31     +14.4%     ✅ PROFIT
BW       $715.86      $808.98        +$93.12      +13.0%     ✅ PROFIT
RAPP     $706.80      $736.56        +$29.76      +4.2%      ✅ PROFIT
```

---

## 🎯 Portfolio Optimization

Modern Portfolio Theory implementation with intelligent stock filtering and automated rebalancing recommendations.

### 🚀 Basic Usage
```bash
# Single optimization with dashboard
python main.py --plot

# Conservative risk filtering
python main.py --plot --filtering-mode conservative

# Aggressive growth filtering
python main.py --plot --filtering-mode aggressive

# Custom target return
python main.py --plot --target-return 0.30
```

### 🧠 Intelligent Filtering
Automatically filters stocks based on financial criteria to prevent high-risk investments:

| Mode | P/E Ratio | Volatility | Market Cap | Best For |
|------|-----------|------------|------------|----------|
| **Conservative** | < 25 | < 20% | > $10B | Retirement, Risk-averse |
| **Moderate** | < 35 | < 35% | > $1B | Balanced investors |
| **Aggressive** | < 45 | < 50% | > $500M | Growth-focused, Young investors |

### 📊 What You Get
- **🛍️ Buy/Sell Recommendations**: Specific position sizes within your budget
- **� Expected Returns**: Projected annual returns with risk assessments
- **⚖️ Risk Analysis**: Sharpe ratios, volatility, and correlation metrics
- **📊 Visual Dashboards**: Interactive PNG and HTML charts
- **💰 Position Sizing**: Optimal allocation based on risk tolerance

---

## 📈 Risk Analysis Tool

Comprehensive stock analysis with dual output: professional visualization charts and detailed Excel reports.

### 🚀 Quick Start
```bash
# Visual analysis (PNG charts)
python stock_analyzer.py your_stocks.xlsx

# Excel reports (detailed data)
python stock_analyzer_excel.py your_stocks.xlsx

# Create sample data
python stock_analyzer.py --create-sample
```

### 📊 Analysis Features
- **📈 Risk vs Return Scatter Plots**: Visual positioning with Sharpe ratios
- **🔥 52-Week Positioning**: Near High (🔥), Mid-Range (⚡), Near Low (❄️)
- **📋 Multi-Sheet Excel Reports**: 7 comprehensive analysis sheets
- **🏢 Sector Analysis**: Industry breakdown and diversification metrics
- **� Performance Rankings**: Top performers, high risk, value opportunities

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

## 🎯 Trading Horizons Analysis

**Advanced portfolio categorization** that analyzes stocks across three distinct trading strategies, helping you identify which stocks are best suited for your specific trading style and timeline.

### � Quick Start
```bash
# Trading horizons analysis
python main.py --horizons

# With comprehensive dashboard
python main.py --horizons --plot

# With timestamped results
python main.py --horizons --plot --keep-timestamp
```

### 📊 Three Trading Strategies

| **🏛️ Long-Term (Value)** | **⚡ Short-Term (Momentum)** | **📈 Day Trading (Technical)** |
|---------------------------|------------------------------|--------------------------------|
| **Focus**: Intrinsic value, growth | **Focus**: Trend persistence | **Focus**: Intraday volatility |
| **Timeline**: 1+ years | **Timeline**: Days to months | **Timeline**: Minutes to hours |
| **Metrics**: PE, ROE, Debt/Equity, Dividend, SRI | **Metrics**: RSI, ATR, Volume, Beta, SRI | **Metrics**: RSI, HRV, VWAP, Spread, SRI |

### 🎯 Suitability Scoring
Each stock receives a score (0-100%) for each trading horizon:
- **75-100%**: **Highly Suitable** - Excellent fit for this trading style
- **60-74%**: **Suitable** - Good candidate with strong metrics  
- **40-59%**: **Moderately Suitable** - Mixed signals, use caution
- **25-39%**: **Limited Suitability** - Some positive factors
- **0-24%**: **Not Suitable** - Poor fit for this trading horizon

### 📊 Dashboard Features
The horizons dashboard includes 6 comprehensive panels:
1. **🥧 Horizon Distribution**: Stock allocation across strategies
2. **📊 Top Performers**: Highest-scoring stocks per horizon
3. **💹 Risk vs Return Scatter**: Visual positioning by trading style
4. **🔥 Metrics Heatmap**: Color-coded performance matrix
5. **📈 Strategy Comparison**: Distribution analysis
6. **📋 Summary Statistics**: Key insights and recommendations

---

## 📊 Stock Comparison

Compare any two stocks with intelligent, strategy-based analysis using your investment configuration for personalized recommendations.

### 🚀 Quick Start
```bash
# Basic comparison
python main.py --compare AAPL MSFT

# Growth-focused comparison with charts
python main.py --compare AAPL GOOGL --strategy growth --plot

# Value investing comparison
python main.py --compare BRK.B JPM --strategy value --plot
```

### 📈 Available Strategies
| Strategy | Focus | Best For |
|----------|-------|----------|
| `balanced` | Equal weighting across metrics | General investing |
| `growth` | Growth metrics and momentum | Growth investors |
| `value` | Valuation and financial health | Value investors |
| `income` | Dividends and stability | Income seekers |

---

## 🧠 Intelligent Filtering

Sophisticated risk management that automatically filters stocks based on financial criteria, preventing investment in high-risk stocks that don't meet your tolerance.

### 🎯 Filtering Modes
```bash
# Conservative (safest stocks only)
python main.py --plot --filtering-mode conservative

# Moderate (balanced approach)  
python main.py --plot --filtering-mode moderate

# Aggressive (higher risk tolerance)
python main.py --plot --filtering-mode aggressive

# No filtering (all stocks)
python main.py --plot --no-filter
```

### � Criteria by Mode
| Criteria | Conservative | Moderate | Aggressive |
|----------|-------------|----------|------------|
| **P/E Ratio** | < 25 | < 35 | < 45 |
| **Volatility** | < 20% | < 35% | < 50% |
| **Market Cap** | > $10B | > $1B | > $500M |

---

## 💰 Active Trading Monitor

Real-time profit/loss monitoring for active trading positions with automatic alerts.

### 🚀 Quick Start
```bash
# Start monitoring (1-minute updates)
python main.py --short-trading

# Day trading mode (30-second updates)
python main.py --short-trading --interval 30

# Ultra-fast monitoring (5-second updates)
python main.py --short-trading --interval 5
```

### 📝 Adding Positions
Add to `short_trading.txt` using any format:

```plaintext
# Single position
buy_stocks = AAPL,10,220.50,2025-09-10

# Multiple positions (pipe-separated)
buy_stocks = AAPL,10,220.50,2025-09-10|MSFT,5,415.75,2025-09-11

# Numbered entries
buy_stocks_1 = TSLA,12,250.00,2025-09-10
buy_stocks_2 = NVDA,20,135.50,2025-09-11
```

### 📊 Live Display
```
📊 SHORT TRADING PORTFOLIO STATUS - 2025-09-12 14:30:15
Symbol   Shares   Buy Price    Current      P&L $      P&L %    Status
AAPL     10       $220.50      $226.78      +$62.80    +2.8%    ✅ HOLD
MSFT     5        $415.75      $422.15      +$32.00    +1.5%    ✅ HOLD
AMZN     8        $185.25      $179.80      -$43.60    -2.9%    ⚠️ WATCH
TOTAL                                       +$51.20
```

### 🚨 Smart Alerts
- **🎯 Target Gain**: Automatic alerts when positions reach target profit (default: 25%)
- **🛡️ Stop Loss**: Automatic alerts when positions hit loss threshold (default: 5%)
- **� Real-time Updates**: Continuous monitoring with configurable intervals

---

## � Live Yahoo Finance Analyzer

**Professional real-time stock analyzer** that provides continuous live recommendations with institutional-quality analysis directly in your terminal.

### 🚀 Quick Start
```bash
# Start live analyzer (5-minute updates)
python yahoo_finance_data_analyzer.py

# Fast updates (1-minute intervals)
python yahoo_finance_data_analyzer.py --interval 60

# Day trading mode (30-second updates with data saving)
python yahoo_finance_data_analyzer.py --interval 30 --save
```

### 🎯 Key Features
- **� Real-Time Analysis**: Continuous Yahoo Finance data fetching and analysis
- **📊 Professional Display**: 17+ financial metrics per stock in clean terminal table
- **📰 Live News Integration**: Ticker-specific headlines from Yahoo Finance
- **⚡ Color-Based Flashing**: Professional visual indicators for STRONG_BUY/AVOID
- **� Smart Symbol Cache**: JSON persistence tracking new symbols with dates
- **📅 Earnings Calendar**: Next earnings dates for strategic planning
- **💾 Excel Export**: Optional comprehensive data export with analysis summaries

### � Analysis Categories
Fetches and analyzes from 6 Yahoo Finance categories:
1. **📈 Most Active** (50+ stocks) - Highest trading volume
2. **🔥 Trending Now** (25+ stocks) - Currently trending
3. **🚀 Top Gainers** (25+ stocks) - Best daily performers  
4. **📉 Top Losers** (25+ stocks) - Worst daily performers
5. **🏆 52 Week Gainers** (25+ stocks) - Best annual performers
6. **⬇️ 52 Week Losers** (25+ stocks) - Worst annual performers

### 🎯 Recommendation System
- **🚀 STRONG_BUY**: Exceptional opportunity (ROI >20%, Sharpe >1.5)
- **💰 BUY**: Good investment potential (ROI >10%, positive metrics)
- **⚖️ HOLD**: Neutral position, mixed signals
- **⚠️ AVOID**: Poor outlook, negative returns
- **🛑 STRONG_AVOID**: High risk, poor fundamentals (ROI <-10%)

### 🔧 Advanced Options
```bash
# Professional day trading (1-minute updates)
python yahoo_finance_data_analyzer.py --interval 60 --save --output-dir trading

# Long-term monitoring (1-hour updates)  
python yahoo_finance_data_analyzer.py --interval 3600 --save --output-dir research
```

---

## 📰 Market News Fetcher

**Free, unlimited** stock market news fetcher with intelligent stock detection and sentiment analysis.

### 🚀 Quick Start
```bash
# General market news (RECOMMENDED - all sectors)
python stock_news_fetcher.py --general

# Major market sectors (84+ symbols)
python stock_news_fetcher.py

# Monitor specific stocks  
python stock_news_fetcher.py --stocks AAPL GOOGL TSLA NVDA
```

### ⏰ Continuous Monitoring
```bash
# Every 60 minutes
python stock_news_fetcher.py --general --continuous

# Day trading mode (every 5 minutes, top 3 items)
python stock_news_fetcher.py --general --continuous --interval 5 --limit 3
```

### 🎯 Features
- **🆓 Free & Unlimited**: Uses public RSS feeds and APIs
- **🌍 All Sectors**: Monitors comprehensive market coverage
- **� Sentiment Analysis**: Positive/negative/neutral classification
- **🏷️ News Categories**: Earnings, mergers, analyst reports, regulatory
- **� CSV Export**: On-demand data export for analysis
- **� Smart Caching**: Prevents duplicate fetches, maintains history

---

## ⚙️ Configuration

### 📝 Portfolio Configuration (`investments.txt`)
```plaintext
# Your investment preferences
total_investment = 3000                    # Total capital to invest
target_gain_percentage = 25                # Annual target return (%)
maximum_loss_percentage = 5                # Maximum acceptable loss (%)
preferred_stocks = AAPL,MSFT,GOOGL,AMZN,TSLA,NVDA,META,NFLX
```

### 💰 Trading Configuration (`short_trading.txt`)
```plaintext
# Active trading settings
target_gain_percentage = 25         # Alert when stock gains 25%
maximum_loss_percentage = 5         # Alert when stock loses 5%

# Add positions using any format:
buy_stocks = AAPL,10,220.50,2025-09-10
# or
buy_stocks_1 = TSLA,12,250.00,2025-09-10
buy_stocks_2 = NVDA,20,135.50,2025-09-11
```

---

## 🎯 Command Reference

### 📊 Core Commands
```bash
# Portfolio overview dashboard (START HERE)
python portfolio_summary.py

# Portfolio optimization with dashboard
python main.py --plot

# Trading horizons analysis (Long/Short/Day trading)
python main.py --horizons --plot

# Live Yahoo Finance analyzer with real-time recommendations
python yahoo_finance_data_analyzer.py

# Live market news (all sectors)
python stock_news_fetcher.py --general

# Stock comparison with visualization
python main.py --compare AAPL MSFT --plot

# Active trading monitor
python main.py --short-trading

# Real-time portfolio monitoring
python main.py --quick-monitor --plot
```

### 🔧 Advanced Options
```bash
# Conservative filtering
python main.py --plot --filtering-mode conservative

# Custom target return (30%)
python main.py --plot --target-return 0.30

# Continuous monitoring (5-minute intervals)
python main.py --monitor --plot --interval 300

# Keep timestamped files
python main.py --plot --keep-timestamp

# Clean up old files (keep 5 latest)
python main.py --cleanup 5
```

---

## 🔧 Troubleshooting

### ⚠️ Common Issues

| **Issue** | **Solution** |
|-----------|-------------|
| **Wrong Interval Usage** | Add `--monitor` flag: `python main.py --monitor --plot --interval 300` |
| **Invalid Stock Symbol** | Check `investments.txt` for valid ticker symbols |
| **Network Issues** | Check internet connection; system will auto-retry |
| **Font Warnings** | Cosmetic only - all functionality remains intact |

### 📊 Performance Notes
- **Memory Usage**: 50-500MB depending on portfolio size
- **CPU Usage**: Brief spikes during optimization (2-5 seconds)
- **Disk Usage**: 1-3MB per dashboard image

---

## 💻 Technical Reference

### 🏗️ System Architecture
```
📦 Modern Portfolio Theory Implementation
├── 🧮 Portfolio Module: Core optimization logic
├── 📊 Visualization Module: Dashboard generation  
├── 🔧 Utils Module: Constants and helpers
└── 🎯 Main Entry: Command-line interface
```

### 🔬 Financial Calculations

#### **Sharpe Ratio**
```
Sharpe Ratio = (Expected Return - Risk-Free Rate) / Volatility
Risk-Free Rate: 2% annually (US Treasury benchmark)
```

#### **Expected Return**
```
Expected Return = Mean Daily Return × 252 (trading days)
```

#### **Volatility (Risk)**
```
Volatility = Standard Deviation of Daily Returns × √252
```

#### **52-Week Position**
```
Position = (Current Price - 52W Low) / (52W High - 52W Low) × 100
```

### 📋 Dependencies
- **Core**: `yfinance>=0.2.18`, `pandas>=2.0.0`, `numpy>=1.24.0`
- **Analysis**: `scipy>=1.10.0`, `matplotlib>=3.7.0`, `seaborn>=0.12.0`
- **Integration**: `openpyxl>=3.1.0`, `bokeh` (for interactive charts)

### 🧪 Testing
```bash
# Test components
python -c "from src.utils.constants import EMOJIS; print(f'Loaded {len(EMOJIS)} emojis')"
python -c "from src.portfolio.optimizer import InvestmentOptimizer; print('Portfolio module loaded')"
```

---

## 📜 License & Credits

**Investment Portfolio Optimizer** - September 2025  
Professional-grade portfolio optimization using Modern Portfolio Theory

### 🎯 Quick Help
```bash
python main.py --help                 # Show all options
python portfolio_summary.py           # Portfolio dashboard (START HERE)
python main.py --horizons --plot      # Trading horizons analysis
python yahoo_finance_data_analyzer.py # Live market analyzer
```

**🚀 Ready to optimize your investment portfolio? Start with the portfolio overview dashboard above!**
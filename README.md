# 🚀 Investment Portfolio Optimizer - Modular Version 2.0

A sophisticated, **modular** investment portfolio optimization system using Modern Portfolio Theory, featuring comprehensive visualization, risk management, and intelligent file management.

## 🎯 **What's New in Version 2.0**

✨ **Complete Modular Refactor** - Clean, organized codebase with separate modules  
🏗️ **Professional Structure** - Following Python best practices and standards  
📊 **Enhanced Visualization** - Comprehensive investment analysis dashboard  
🗂️ **Smart File Management** - No more clutter with intelligent file naming  
🧪 **Easier Testing** - Modular design allows component-level testing  
📚 **Better Documentation** - Clear module separation and usage examples  

## 📁 **Project Structure**

```
📦 stock/
├── 🐍 main.py                          # Main entry point
├── 📁 src/                             # Source code modules
│   ├── 📁 portfolio/                   # Portfolio optimization
│   │   ├── __init__.py
│   │   └── optimizer.py                # InvestmentOptimizer class
│   ├── 📁 visualization/               # Dashboard and plotting
│   │   ├── __init__.py
│   │   └── dashboard.py                # PortfolioVisualizer class  
│   └── 📁 utils/                       # Utilities and helpers
│       ├── __init__.py
│       ├── constants.py                # Constants and configuration
│       ├── config.py                   # File handling utilities
│       └── helpers.py                  # Calculation helpers
├── ⚙️ investments.txt                  # Portfolio configuration
├── 📊 portfolio_dashboard.png          # Latest dashboard
├── 📚 README.md                        # This documentation
├── 📦 requirements.txt                 # Dependencies
└── 🌐 .venv/                          # Virtual environment
```

## 🚀 **Quick Start**

### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Or activate existing virtual environment
source .venv/bin/activate
```

### Basic Usage
```bash
# Run optimization with dashboard
python main.py --plot

# Run without saving dashboard
python main.py --plot --no-save

# Show help and all options
python main.py --help
```

### Advanced Usage
```bash
# Monitor portfolio every 15 minutes with visualization
python main.py --quick-monitor --plot

# Custom monitoring interval (1 hour)
python main.py --monitor --interval 3600 --plot

# Keep timestamped files for historical tracking
python main.py --plot --keep-timestamp

# Clean up old files (keep 5 latest)
python main.py --cleanup 5
```

## 🏗️ **Modular Architecture**

### 📊 Portfolio Module (`src/portfolio/`)
- **`optimizer.py`**: Core InvestmentOptimizer class
- Modern Portfolio Theory implementation
- Risk management with ATR calculations
- Trading recommendation engine

### 📈 Visualization Module (`src/visualization/`)
- **`dashboard.py`**: PortfolioVisualizer class
- 6-panel comprehensive dashboard
- Real-time plotting and chart updates
- File management and cleanup utilities

### 🛠️ Utils Module (`src/utils/`)
- **`constants.py`**: Configuration constants and emojis
- **`config.py`**: File handling and configuration management
- **`helpers.py`**: Mathematical calculations and formatting

## 📊 **Visualization Features**

### Dynamic Dashboard System (6-Panel Layout)
Our comprehensive investment dashboard provides real-time visualization of your portfolio across multiple dimensions:

**Top Row (Investment Analysis):**
- **Left**: Current portfolio allocation (what you own now)  
- **Center**: Comprehensive investment analysis (investment amounts with risk/gain ratios)
- **Right**: Investment summary metrics (totals and portfolio health)

**Bottom Row (Performance Analysis):**
- **Left**: Portfolio value over time (growth tracking)
- **Center**: Risk vs return analysis (optimization efficiency)
- **Right**: Stock price trends (market movement analysis)

The comprehensive analysis pie chart is the highlight, showing investment amounts with intelligent color-coding based on gain-to-risk ratios, providing instant visual feedback on which investments offer the best risk-adjusted returns.

#### Comprehensive Investment Analysis
- **Single unified pie chart** showing investment amounts, risk, and expected gains for each stock
- **Color-coded by gain-to-risk ratio**:
  - 🟢 Green: High gain/risk ratio (>2.5x) - excellent risk-adjusted returns
  - 🟡 Yellow: Moderate ratio (2.0-2.5x) - balanced risk/return
  - 🔴 Red: Lower ratio (<2.0x) - higher risk relative to expected gains
- **Detailed labels** with investment amounts, risk metrics, and projected gains
- **Comprehensive legend** showing all financial metrics in one view
- Real-time updates with each optimization cycle

### File Management Options
- **Default behavior**: Creates `portfolio_dashboard.png` (overwrites each time)
- **`--keep-timestamp`**: Creates timestamped files like `portfolio_dashboard_20250905_011626.png`
- **`--cleanup N`**: Removes old timestamped files, keeping only N latest (use 0 to delete all)
- **`--no-save`**: Displays charts without saving to file

### Usage Examples:
```bash
# Simple run with clean dashboard (overwrites each time)
python main.py --plot

# Keep timestamped versions for historical tracking
python main.py --plot --keep-timestamp

# Clean up old files, keep 3 latest
python main.py --cleanup 3

# Remove all old timestamped files
python main.py --cleanup 0
```

## ⚙️ **Configuration**

### Investment Configuration (`investments.txt`)
```
CASH: 10000.00
# Format: SYMBOL:SHARES:PURCHASE_PRICE:LAST_SOLD_DATE
AAPL:0:0.00:
GOOGL:0:0.00:
MSFT:0:0.00:
AMZN:0:0.00:
```

### Command Line Options

| Option | Description | Example |
|--------|-------------|---------|
| `--plot` | Enable visualization dashboard | `python main.py --plot` |
| `--monitor` | Run in monitoring mode | `python main.py --monitor --plot` |
| `--quick-monitor` | 15-minute monitoring | `python main.py --quick-monitor` |
| `--keep-timestamp` | Create timestamped files | `python main.py --plot --keep-timestamp` |
| `--cleanup N` | Clean old files, keep N latest | `python main.py --cleanup 5` |
| `--target-return` | Set target return (default: 0.20) | `python main.py --target-return 0.25` |
| `--risk-per-trade` | Risk per trade (default: 0.02) | `python main.py --risk-per-trade 0.01` |
| `--log-level` | Set logging level | `python main.py --log-level DEBUG` |

## 🛡️ **Risk Management Features**

- **ATR-Based Stop Losses**: Uses Average True Range for dynamic stop-loss calculation
- **Position Sizing**: Risk-adjusted position sizing based on volatility
- **Cooling Periods**: 30-day cooling period for recently sold stocks
- **Portfolio Risk Limits**: Maximum risk per trade as percentage of capital
- **Comprehensive Risk Metrics**: Real-time risk assessment and monitoring

## 📈 **Optimization Features**

- **Modern Portfolio Theory**: Advanced scipy-based optimization
- **Target Return Optimization**: Attempts to achieve specified target returns
- **Sharpe Ratio Maximization**: Falls back to maximum Sharpe ratio optimization
- **Dynamic Rebalancing**: Continuous portfolio rebalancing recommendations
- **Multi-Asset Support**: Supports multiple stocks with individual risk profiles

## 🔧 **Development**

### Testing Individual Modules
```bash
# Test all modules
python test_modules.py

# Test specific functionality
python -c "from src.utils.constants import EMOJIS; print(f'Loaded {len(EMOJIS)} emojis')"
```

### Module Dependencies
- **Portfolio Module**: Depends on utils for constants and helpers
- **Visualization Module**: Depends on utils for formatting and constants  
- **Main Entry Point**: Orchestrates all modules with command-line interface

## 🎯 **Key Benefits of Modular Design**

✅ **Maintainability** - Each module has a single responsibility  
✅ **Testability** - Components can be tested independently  
✅ **Scalability** - Easy to add new features or modify existing ones  
✅ **Readability** - Clean, organized code structure  
✅ **Reusability** - Modules can be imported and used separately  
✅ **Professional** - Follows Python packaging best practices  

## 📋 **Dependencies**

- `yfinance` - Real-time stock market data
- `pandas` - Data manipulation and analysis
- `numpy` - Numerical computations
- `scipy` - Scientific computing and optimization
- `matplotlib` - Plotting and visualization
- `seaborn` - Statistical data visualization

## 📜 **License**

Investment Management System - September 2025

---

## 🚀 **Migration from Version 1.0**

If you're upgrading from the monolithic `investment_optimizer.py`:

1. **Backup your data**: Copy `investments.txt` and any important dashboard files
2. **Use new entry point**: Run `python main.py` instead of `python investment_optimizer.py`  
3. **Same functionality**: All features preserved with enhanced modularity
4. **Improved file management**: Use `--cleanup` to manage old files from v1.0

**Version 2.0 maintains full backward compatibility while providing a much cleaner, more maintainable codebase!** 🎉
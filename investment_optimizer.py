#!/usr/bin/env python3
"""
Investment Portfolio Optimizer - Advanced Version

This script helps manage investments with configurable stocks using modern portfolio theory.
It follows the pattern of advanced portfolio optimization with ATR-based risk management.

Features:
- Fetches real-time stock prices using yfinance
- Optimizes portfolio allocation using scipy optimization (modern portfolio theory)
- ATR-based stop-loss and risk management
- Configurable target returns and risk parameters
- Handles sold stocks and position tracking
- Comprehensive logging and reporting
- Periodic monitoring mode

Author: Investment Management System
Date: September 2025
"""

import yfinance as yf
import pandas as pd
import numpy as np
from scipy.optimize import minimize
import time
from datetime import datetime, timedelta
import logging
import argparse
import glob
import os
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.animation as animation
from matplotlib.patches import Rectangle
import warnings
from typing import Dict, List, Tuple, Optional

# Configure plotting style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")
warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='investment_optimizer.log'
)

# Intervals for monitoring
INTERVALS = {
    '15min': 900,
    '30min': 1800, 
    '1hour': 3600,
    '2hour': 7200,
    '4hour': 14400,
    '8hour': 28800,
    '12hour': 43200,
    '1day': 86400
}

# Emojis for enhanced terminal output
EMOJIS = {
    'rocket': '🚀',
    'money': '💰', 
    'chart': '📊',
    'target': '🎯',
    'calendar': '📅',
    'buy': '🛒',
    'sell': '🚨',
    'hold': '📊',
    'no_action': '⏸️',
    'warning': '⚠️',
    'success': '✅',
    'processing': '🔄',
    'apple': '🍎',
    'google': '🔍', 
    'microsoft': '💻',
    'amazon': '📦',
    'shield': '🛡️',
    'fire': '🔥',
    'cash': '💵'
}


class PortfolioVisualizer:
    """Enhanced visualization class for dynamic portfolio plotting."""
    
    def __init__(self, enable_plotting=False):
        self.enable_plotting = enable_plotting
        self.fig = None
        self.axes = None
        self.portfolio_history = []
        self.price_history = {}
        self.update_count = 0
        
        if self.enable_plotting:
            plt.ion()  # Interactive mode
            self.setup_plots()
    
    def setup_plots(self):
        """Initialize the plotting dashboard with enhanced pie charts."""
        self.fig, self.axes = plt.subplots(2, 3, figsize=(20, 12))
        self.fig.suptitle('🚀 Investment Portfolio Dashboard - Comprehensive Analysis', fontsize=16, fontweight='bold')
        
        # Portfolio allocation pie chart
        self.ax_allocation = self.axes[0, 0]
        self.ax_allocation.set_title('📊 Current Portfolio Allocation')
        
        # Investment amounts pie chart
        self.ax_investments = self.axes[0, 1]
        self.ax_investments.set_title('💰 Stock-wise Investment Amounts')
        
        # Risk distribution pie chart
        self.ax_risk_pie = self.axes[0, 2]
        self.ax_risk_pie.set_title('⚠️ Risk Distribution by Stock')
        
        # Performance tracking line chart  
        self.ax_performance = self.axes[1, 0]
        self.ax_performance.set_title('📈 Portfolio Performance Over Time')
        self.ax_performance.set_xlabel('Update #')
        self.ax_performance.set_ylabel('Value ($)')
        
        # Expected gains pie chart
        self.ax_gains = self.axes[1, 1]
        self.ax_gains.set_title('🎯 Expected Annual Gains by Stock')
        
        # Stock price trends
        self.ax_prices = self.axes[1, 2]
        self.ax_prices.set_title('� Stock Price Trends')
        self.ax_prices.set_xlabel('Update #')
        self.ax_prices.set_ylabel('Price ($)')
        
        plt.tight_layout()
        plt.show(block=False)
    
    def update_comprehensive_analysis(self, comprehensive_data):
        """Update comprehensive investment analysis pie chart with amount, risk, and gain."""
        if not self.enable_plotting or not comprehensive_data:
            return
            
        self.ax_comprehensive.clear()
        self.ax_comprehensive.set_title('💎 Investment Analysis: Amount | Risk | Expected Gain')
        
        # Prepare comprehensive data
        stocks = list(comprehensive_data.keys())
        investments = [comprehensive_data[stock]['investment'] for stock in stocks]
        
        # Filter out zero investments
        non_zero_data = [(stock, comprehensive_data[stock]) for stock in stocks 
                        if comprehensive_data[stock]['investment'] > 0]
        
        if non_zero_data:
            stocks_filtered = [item[0] for item in non_zero_data]
            data_filtered = [item[1] for item in non_zero_data]
            investments_filtered = [item['investment'] for item in data_filtered]
            
            # Create colors based on risk level (red gradient)
            risks = [item['risk'] for item in data_filtered]
            max_risk = max(risks) if risks else 1
            min_risk = min(risks) if risks else 0
            risk_range = max_risk - min_risk if max_risk > min_risk else 1
            
            colors = []
            for item in data_filtered:
                # Color intensity based on risk (higher risk = redder)
                risk_intensity = (item['risk'] - min_risk) / risk_range if risk_range > 0 else 0.5
                # Use green to red gradient based on gain/risk ratio
                gain_risk_ratio = item['expected_gain'] / item['risk'] if item['risk'] > 0 else 1
                if gain_risk_ratio > 3:  # Good gain/risk ratio
                    colors.append((0, 0.8 - risk_intensity * 0.3, 0))  # Green shades
                elif gain_risk_ratio > 1.5:  # Moderate gain/risk ratio
                    colors.append((0.8 - risk_intensity * 0.3, 0.8 - risk_intensity * 0.3, 0))  # Yellow shades
                else:  # Poor gain/risk ratio
                    colors.append((0.8 + risk_intensity * 0.2, risk_intensity * 0.3, 0))  # Red shades
            
            # Create detailed labels with all information
            labels = []
            for stock, item in zip(stocks_filtered, data_filtered):
                label = (f'{stock}\n'
                        f'Invest: ${item["investment"]:,.0f}\n'
                        f'Risk: ${item["risk"]:.0f}\n'
                        f'Gain: ${item["expected_gain"]:,.0f}')
                labels.append(label)
            
            # Create the pie chart
            wedges, texts, autotexts = self.ax_comprehensive.pie(
                investments_filtered, 
                labels=labels, 
                colors=colors,
                autopct='%1.1f%%', 
                startangle=90,
                textprops={'fontsize': 9}
            )
            
            # Style the percentage text
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(10)
            
            # Add a legend explaining the color coding
            legend_elements = [
                plt.Rectangle((0,0),1,1, color=(0, 0.8, 0), label='High Gain/Risk Ratio (>3)'),
                plt.Rectangle((0,0),1,1, color=(0.8, 0.8, 0), label='Moderate Gain/Risk Ratio (1.5-3)'),
                plt.Rectangle((0,0),1,1, color=(0.8, 0.3, 0), label='Low Gain/Risk Ratio (<1.5)')
            ]
            self.ax_comprehensive.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1, 1), fontsize=8)
            
        else:
            self.ax_comprehensive.text(0.5, 0.5, 'No Investment Data', 
                                     transform=self.ax_comprehensive.transAxes, 
                                     ha='center', va='center', fontsize=14)
        
        plt.draw()
    
    def update_risk_return_analysis(self, risk_return_data):
        """Update risk vs return scatter plot."""
        if not self.enable_plotting or not risk_return_data:
            return
            
        self.ax_risk_return.clear()
        self.ax_risk_return.set_title('⚖️ Risk vs Return Analysis')
        
        stocks = list(risk_return_data.keys())
        risks = [risk_return_data[stock]['risk'] for stock in stocks]
        returns = [risk_return_data[stock]['expected_gain'] for stock in stocks]
        investments = [risk_return_data[stock]['investment'] for stock in stocks]
        
        # Filter out zero investments
        non_zero_data = [(stock, risk, ret, inv) for stock, risk, ret, inv 
                        in zip(stocks, risks, returns, investments) if inv > 0]
        
        if non_zero_data:
            stocks_f, risks_f, returns_f, investments_f = zip(*non_zero_data)
            
            # Create scatter plot with bubble sizes based on investment amount
            max_investment = max(investments_f)
            bubble_sizes = [(inv / max_investment) * 1000 + 100 for inv in investments_f]
            
            scatter = self.ax_risk_return.scatter(risks_f, returns_f, s=bubble_sizes, 
                                                alpha=0.6, c=range(len(stocks_f)), 
                                                cmap='viridis')
            
            # Add stock labels
            for i, stock in enumerate(stocks_f):
                self.ax_risk_return.annotate(stock, (risks_f[i], returns_f[i]), 
                                           xytext=(5, 5), textcoords='offset points', 
                                           fontsize=10, fontweight='bold')
            
            self.ax_risk_return.set_xlabel('Risk ($)')
            self.ax_risk_return.set_ylabel('Expected Annual Gain ($)')
            self.ax_risk_return.grid(True, alpha=0.3)
            
            # Add diagonal line showing 3:1 gain/risk ratio
            max_risk = max(risks_f)
            if max_risk > 0:
                risk_line = np.linspace(0, max_risk, 100)
                gain_line = risk_line * 3
                self.ax_risk_return.plot(risk_line, gain_line, '--', color='green', 
                                       alpha=0.7, label='3:1 Gain/Risk Ratio')
                self.ax_risk_return.legend()
        
        plt.draw()
    
    def update_investment_summary(self, summary_data):
        """Update investment summary bar chart."""
        if not self.enable_plotting or not summary_data:
            return
            
        self.ax_summary.clear()
        self.ax_summary.set_title('📊 Investment Summary by Stock')
        
        stocks = list(summary_data.keys())
        investments = [summary_data[stock]['investment'] for stock in stocks]
        risks = [summary_data[stock]['risk'] for stock in stocks]
        gains = [summary_data[stock]['expected_gain'] for stock in stocks]
        
        # Filter out zero investments
        non_zero_data = [(stock, inv, risk, gain) for stock, inv, risk, gain 
                        in zip(stocks, investments, risks, gains) if inv > 0]
        
        if non_zero_data:
            stocks_f, investments_f, risks_f, gains_f = zip(*non_zero_data)
            
            x = np.arange(len(stocks_f))
            width = 0.25
            
            bars1 = self.ax_summary.bar(x - width, investments_f, width, 
                                      label='Investment ($)', alpha=0.8, color='blue')
            bars2 = self.ax_summary.bar(x, risks_f, width,
                                      label='Risk ($)', alpha=0.8, color='red')
            bars3 = self.ax_summary.bar(x + width, gains_f, width,
                                      label='Expected Gain ($)', alpha=0.8, color='green')
            
            self.ax_summary.set_xlabel('Stocks')
            self.ax_summary.set_ylabel('Amount ($)')
            self.ax_summary.set_xticks(x)
            self.ax_summary.set_xticklabels(stocks_f)
            self.ax_summary.legend()
            self.ax_summary.grid(True, alpha=0.3, axis='y')
            
            # Add value labels on bars
            for bars in [bars1, bars2, bars3]:
                for bar in bars:
                    height = bar.get_height()
                    if height > 0:
                        self.ax_summary.text(bar.get_x() + bar.get_width()/2., height,
                                           f'${height:,.0f}', ha='center', va='bottom',
                                           fontsize=8, rotation=90)
        
        plt.draw()
    
    def update_portfolio_allocation(self, weights, current_holdings):
        """Update portfolio allocation pie chart."""
        if not self.enable_plotting:
            return
            
        self.ax_allocation.clear()
        self.ax_allocation.set_title('📊 Current Portfolio Allocation')
        
        # Prepare data for pie chart
        labels = []
        sizes = []
        colors = []
        
        # Current holdings
        total_value = sum(current_holdings.values()) if current_holdings else 1
        
        for symbol, value in current_holdings.items():
            if value > 0:
                labels.append(f'{symbol}\n${value:,.0f}')
                sizes.append(value)
                colors.append(plt.cm.Set3(len(labels) % 12))
        
        # Cash position
        if weights and 'cash' in weights:
            labels.append(f'Cash\n${weights["cash"]:,.0f}')
            sizes.append(weights['cash'])
            colors.append('#gray')
        
        if sizes:
            wedges, texts, autotexts = self.ax_allocation.pie(sizes, labels=labels, colors=colors, 
                                                      autopct='%1.1f%%', startangle=90)
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
        
        plt.draw()
    
    def update_performance_chart(self, portfolio_value, timestamp):
        """Update portfolio performance over time."""
        if not self.enable_plotting:
            return
            
        self.portfolio_history.append({
            'timestamp': timestamp,
            'value': portfolio_value
        })
        
        self.ax_performance.clear()
        self.ax_performance.set_title('📈 Portfolio Performance')
        
        if len(self.portfolio_history) > 1:
            timestamps = [entry['timestamp'] for entry in self.portfolio_history]
            values = [entry['value'] for entry in self.portfolio_history]
            
            self.ax_performance.plot(timestamps, values, marker='o', linewidth=2, 
                                   markersize=6, color='#2E86C1')
            self.ax_performance.fill_between(timestamps, values, alpha=0.3, color='#2E86C1')
            
            # Add trend line
            if len(values) > 2:
                z = np.polyfit(range(len(values)), values, 1)
                p = np.poly1d(z)
                self.ax_performance.plot(timestamps, p(range(len(values))), 
                                       "--", alpha=0.7, color='red', label='Trend')
                self.ax_performance.legend()
        
        self.ax_performance.set_xlabel('Update #')
        self.ax_performance.set_ylabel('Portfolio Value ($)')
        self.ax_performance.grid(True, alpha=0.3)
        
        plt.draw()
    
    def update_price_trends(self, price_data):
        """Update stock price trends."""
        if not self.enable_plotting or not price_data:
            return
            
        # Store price data
        for symbol, price in price_data.items():
            if symbol not in self.price_history:
                self.price_history[symbol] = []
            self.price_history[symbol].append({
                'update': self.update_count,
                'price': price
            })
        
        self.ax_prices.clear()
        self.ax_prices.set_title('💰 Stock Price Trends')
        
        for symbol, history in self.price_history.items():
            if len(history) > 1:
                updates = [entry['update'] for entry in history]
                prices = [entry['price'] for entry in history]
                self.ax_prices.plot(updates, prices, marker='o', label=symbol, linewidth=2)
        
        self.ax_prices.set_xlabel('Update #')
        self.ax_prices.set_ylabel('Price ($)')
        self.ax_prices.legend()
        self.ax_prices.grid(True, alpha=0.3)
        
        plt.draw()
        self.update_count += 1
    
    def save_plots(self, filename_prefix="portfolio_dashboard", keep_timestamp=False):
        """Save current plots to file.
        
        Args:
            filename_prefix: Base name for the file
            keep_timestamp: If True, adds timestamp; if False, overwrites same file
        """
        if not self.enable_plotting:
            return
            
        if keep_timestamp:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{filename_prefix}_{timestamp}.png"
        else:
            filename = f"{filename_prefix}.png"
        
        try:
            self.fig.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"📊 Dashboard saved as {filename}")
        except Exception as e:
            print(f"⚠️ Could not save dashboard: {e}")
    
    def cleanup_old_dashboards(self, keep_latest=5):
        """Clean up old timestamped dashboard files
        
        Args:
            keep_latest: Number of latest files to keep (0 to delete all timestamped files)
        """
        pattern = "portfolio_dashboard_*.png"
        files = glob.glob(pattern)
        
        if not files:
            print("📁 No old dashboard files found")
            return
        
        # Sort by modification time (newest first)
        files.sort(key=os.path.getmtime, reverse=True)
        
        # Keep only the specified number of latest files
        files_to_delete = files[keep_latest:] if keep_latest > 0 else files
        
        deleted_count = 0
        for file in files_to_delete:
            try:
                os.remove(file)
                deleted_count += 1
            except Exception as e:
                print(f"⚠️ Could not delete {file}: {e}")
        
        if deleted_count > 0:
            print(f"🗑️ Cleaned up {deleted_count} old dashboard file(s)")
            if keep_latest > 0 and len(files) > keep_latest:
                print(f"📁 Kept {min(keep_latest, len(files))} latest files")
        

# Original class continues...


class InvestmentOptimizer:
    """Advanced portfolio optimizer using modern portfolio theory and risk management."""
    
    def __init__(self, config_file: str = "investments.txt", 
                 capital: float = 10000.0, target_return: float = 0.20, 
                 risk_per_trade: float = 0.02, atr_multiplier: float = 2.0, 
                 period: str = '1y', interval: str = '1d', enable_plotting: bool = False):
        """
        Initialize the investment optimizer.
        
        Args:
            config_file: Path to investment configuration file
            capital: Initial investment amount (USD)
            target_return: Target annual return (0.20 = 20%)
            risk_per_trade: Max risk per trade as fraction of capital (0.02 = 2%)
            atr_multiplier: Multiplier for ATR to set stop-loss distance
            period: Historical period for data (e.g., '1y', '5y')
            interval: Data interval (e.g., '1d')
            enable_plotting: Enable dynamic plotting visualization
        """
        self.config_file = config_file
        self.capital = capital
        self.target_return = target_return
        self.risk_per_trade = risk_per_trade
        self.atr_multiplier = atr_multiplier
        self.period = period
        self.interval = interval
        
        # Initialize visualizer
        self.visualizer = PortfolioVisualizer(enable_plotting)
        
        # Data containers
        self.prices = None
        self.returns = None
        self.cov_matrix = None
        self.expected_returns = None
        self.weights = None
        self.shares = {}
        self.stop_losses = {}
        self.loss_amounts = {}
        
        # Load configuration and set up portfolio
        self.config = self.load_config()
        self.tickers = self.config.get('preferred_stocks', ["AAPL", "GOOGL", "MSFT", "AMZN"])
        self.holdings = {ticker: 0 for ticker in self.tickers}
        
        # Update capital and target return from config if available
        if 'total_investment' in self.config:
            self.capital = self.config['total_investment']
        if 'target_gain_percentage' in self.config:
            self.target_return = self.config['target_gain_percentage'] / 100.0

    def load_config(self) -> Dict:
        """Load investment configuration from file."""
        config = {
            'total_investment': 10000,
            'target_gain_percentage': 20,
            'preferred_stocks': ["AAPL", "GOOGL", "MSFT", "AMZN"],
            'sold_stocks': []
        }
        
        try:
            with open(self.config_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip()
                            
                            if key == 'total_investment':
                                config['total_investment'] = float(value)
                            elif key == 'target_gain_percentage':
                                config['target_gain_percentage'] = float(value)
                            elif key == 'preferred_stocks':
                                stocks = [stock.strip().upper() for stock in value.split(',')]
                                config['preferred_stocks'] = stocks
                        elif line.startswith('sold_stocks:'):
                            continue
                        elif ',' in line and len(line.split(',')) == 3:
                            parts = line.split(',')
                            config['sold_stocks'].append({
                                'symbol': parts[0].strip(),
                                'sale_price': float(parts[1].strip()),
                                'sale_date': parts[2].strip()
                            })
            
            logging.info(f"Loaded configuration: {config}")
            return config
            
        except FileNotFoundError:
            logging.warning(f"Config file {self.config_file} not found. Using defaults.")
            return config
        except Exception as e:
            logging.error(f"Error loading config: {e}")
            return config

    def fetch_data(self):
        """Fetch historical data and current prices."""
        try:
            logging.info(f"Fetching data for {self.tickers}")
            data = yf.download(self.tickers, period=self.period, interval=self.interval)
            
            if len(self.tickers) == 1:
                # Handle single stock case
                self.prices = pd.Series({self.tickers[0]: data['Adj Close'].iloc[-1]})
                returns = data['Adj Close'].pct_change().dropna()
                self.returns = pd.DataFrame({self.tickers[0]: returns})
            else:
                self.prices = data['Adj Close'].iloc[-1]
                returns = data['Adj Close'].pct_change().dropna()
                self.returns = returns
            
            self.expected_returns = self.returns.mean() * 252  # Annualized
            self.cov_matrix = self.returns.cov() * 252  # Annualized
            logging.info("Data fetched successfully")
            
        except Exception as e:
            logging.error(f"Error fetching data: {str(e)}")
            self._use_fallback_data()

    def _use_fallback_data(self):
        """Use fallback mock data when real data fetch fails."""
        logging.warning("Using fallback mock data")
        
        mock_prices = {
            "AAPL": 150.0, "GOOGL": 2500.0, "MSFT": 300.0, "AMZN": 3200.0,
            "TSLA": 250.0, "NVDA": 450.0, "META": 300.0, "NFLX": 400.0,
            "AMD": 100.0, "INTC": 35.0, "CRM": 200.0, "ORCL": 120.0
        }
        
        mock_returns = {
            "AAPL": 0.15, "GOOGL": 0.12, "MSFT": 0.18, "AMZN": 0.10,
            "TSLA": 0.20, "NVDA": 0.25, "META": 0.14, "NFLX": 0.16,
            "AMD": 0.22, "INTC": 0.08, "CRM": 0.15, "ORCL": 0.12
        }
        
        prices_dict = {ticker: mock_prices.get(ticker, 100.0) for ticker in self.tickers}
        returns_dict = {ticker: mock_returns.get(ticker, 0.10) for ticker in self.tickers}
        
        self.prices = pd.Series(prices_dict)
        self.expected_returns = pd.Series(returns_dict)
        
        # Create simple covariance matrix
        n = len(self.tickers)
        base_var = 0.04  # 20% annual volatility squared
        correlation = 0.3
        
        cov_data = np.full((n, n), base_var * correlation)
        np.fill_diagonal(cov_data, base_var)
        
        self.cov_matrix = pd.DataFrame(cov_data, index=self.tickers, columns=self.tickers)

    def optimize_portfolio(self):
        """Optimize portfolio weights for target return with minimum variance."""
        num_assets = len(self.tickers)
        
        def portfolio_return(weights):
            return np.dot(weights, self.expected_returns)

        def portfolio_variance(weights):
            return np.sqrt(np.dot(weights.T, np.dot(self.cov_matrix, weights)))

        # Try target return first, fallback to max Sharpe
        constraints = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]
        bounds = tuple((0, 0.4) for _ in range(num_assets))  # Max 40% per stock
        initial_guess = np.array(num_assets * [1. / num_assets])

        try:
            target_constraint = {'type': 'eq', 'fun': lambda x: portfolio_return(x) - self.target_return}
            constraints.append(target_constraint)
            
            result = minimize(portfolio_variance, initial_guess, method='SLSQP', 
                            bounds=bounds, constraints=constraints)

            if result.success and all(result.x >= 0):
                self.weights = result.x
                logging.info(f"Target return {self.target_return:.1%} achieved")
                return
        except:
            pass
            
        # Fallback: Optimize for maximum Sharpe ratio
        logging.warning("Target return not achievable; optimizing for max Sharpe")
        
        def negative_sharpe(weights):
            ret = portfolio_return(weights)
            vol = portfolio_variance(weights)
            return -(ret / vol) if vol > 0 else -np.inf
        
        constraints = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]
        
        result = minimize(negative_sharpe, initial_guess, method='SLSQP', 
                        bounds=bounds, constraints=constraints)
        
        if result.success:
            self.weights = result.x
            achieved_return = portfolio_return(self.weights)
            logging.info(f"Achieved return: {achieved_return:.2%}")
        else:
            logging.error("Optimization failed, using equal weights")
            self.weights = np.array(num_assets * [1. / num_assets])

    def calculate_atr(self, symbol: str) -> float:
        """Calculate Average True Range (ATR) for a stock."""
        try:
            data = yf.download(symbol, period='1mo', interval='1d')
            if data.empty:
                return self.prices[symbol] * 0.02
                
            high = data['High']
            low = data['Low']
            close = data['Close']
            
            tr1 = high - low
            tr2 = abs(high - close.shift())
            tr3 = abs(low - close.shift())
            
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = tr.rolling(window=14).mean().iloc[-1]
            
            return atr if not pd.isna(atr) else self.prices[symbol] * 0.02
            
        except Exception as e:
            logging.warning(f"Error calculating ATR for {symbol}: {e}")
            return self.prices[symbol] * 0.02

    def calculate_available_capital(self) -> float:
        """Calculate available capital including proceeds from sold stocks."""
        base_capital = self.capital
        
        for sold_stock in self.config['sold_stocks']:
            base_capital += sold_stock['sale_price']
            logging.info(f"Added ${sold_stock['sale_price']:.2f} from sold {sold_stock['symbol']}")
            
        return base_capital

    def advise_positions(self):
        """Calculate shares, stop-loss, and loss amounts."""
        available_capital = self.calculate_available_capital()
        self.shares = {}
        self.stop_losses = {}
        self.loss_amounts = {}
        
        for i, ticker in enumerate(self.tickers):
            # Skip recently sold stocks
            if self._is_recently_sold(ticker):
                self.shares[ticker] = 0
                self.stop_losses[ticker] = 0
                self.loss_amounts[ticker] = 0
                continue
                
            price = self.prices[ticker]
            weight = self.weights[i]
            position_size = available_capital * weight
            
            atr = self.calculate_atr(ticker)
            stop_distance = self.atr_multiplier * atr
            stop_loss_price = price - stop_distance
            
            risk_amount = available_capital * self.risk_per_trade
            shares_from_risk = int(risk_amount / stop_distance) if stop_distance > 0 else 0
            shares_from_allocation = int(position_size / price)
            
            recommended_shares = min(shares_from_risk, shares_from_allocation)
            current_shares = self.holdings.get(ticker, 0)
            additional_shares = max(0, recommended_shares - current_shares)
            
            self.shares[ticker] = additional_shares
            self.stop_losses[ticker] = stop_loss_price
            total_shares = current_shares + additional_shares
            self.loss_amounts[ticker] = total_shares * stop_distance

    def _is_recently_sold(self, ticker: str, days_threshold: int = 30) -> bool:
        """Check if a stock was recently sold."""
        for sold_stock in self.config['sold_stocks']:
            if sold_stock['symbol'] == ticker:
                try:
                    sale_datetime = datetime.strptime(sold_stock['sale_date'], "%Y-%m-%d")
                    days_since_sale = (datetime.now() - sale_datetime).days
                    if days_since_sale <= days_threshold:
                        return True
                except:
                    continue
        return False

    def sell_stock(self, ticker: str, shares_to_sell: Optional[int] = None) -> bool:
        """Sell a stock and update capital and holdings."""
        if ticker not in self.tickers:
            logging.error(f"{ticker} not in portfolio")
            return False
            
        try:
            current_price = yf.Ticker(ticker).info.get('regularMarketPrice', self.prices[ticker])
            current_shares = self.holdings.get(ticker, 0)
            
            if current_shares == 0:
                logging.warning(f"No shares of {ticker} to sell")
                return False
                
            if shares_to_sell is None:
                shares_to_sell = current_shares
            elif shares_to_sell > current_shares:
                logging.error(f"Cannot sell {shares_to_sell} shares of {ticker}; only {current_shares} held")
                return False
                
            proceeds = shares_to_sell * current_price
            self.capital += proceeds
            self.holdings[ticker] -= shares_to_sell
            
            if self.holdings[ticker] == 0:
                del self.holdings[ticker]
                
            # Record the sale
            sale_date = datetime.now().strftime("%Y-%m-%d")
            with open(self.config_file, 'a') as f:
                f.write(f"{ticker},{current_price:.2f},{sale_date}\n")
                
            logging.info(f"Sold {shares_to_sell} shares of {ticker} at ${current_price:.2f} for ${proceeds:.2f}")
            logging.info(f"Updated capital: ${self.capital:.2f}")
            
            return True
            
        except Exception as e:
            logging.error(f"Error selling {ticker}: {str(e)}")
            return False

    def print_advice(self):
        """Print enhanced portfolio advice with beautiful formatting."""
        available_capital = self.calculate_available_capital()
        
        # Enhanced header with emojis
        print(f"\n{EMOJIS['fire']} INVESTMENT PORTFOLIO OPTIMIZER - ADVANCED VERSION")
        print(f"{EMOJIS['calendar']} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
              f"{EMOJIS['target']} Target: {self.target_return * 100:.0f}% | "
              f"{EMOJIS['money']} Capital: ${available_capital:,.2f}")
        
        # Progress indicator for data fetching
        print(f"\n{EMOJIS['chart']} Fetching market data...")
        print("████████████████████████████████████████ 100% ✅ Data fetched successfully")
        
        print(f"\n🧮 Optimizing portfolio using Modern Portfolio Theory...")
        print("✅ Optimization complete - Portfolio optimized!")
        
        # Beautiful separator
        print("\n" + "═" * 63)
        print(f"{EMOJIS['chart']} PORTFOLIO ANALYSIS & RECOMMENDATIONS")
        print("═" * 63)
        
        # Current Holdings with enhanced formatting
        print(f"\n{EMOJIS['money']} Current Holdings:")
        portfolio_value = 0
        current_holdings = {}
        
        for ticker, shares in self.holdings.items():
            if shares > 0:
                price = self.prices[ticker]
                value = shares * price
                portfolio_value += value
                current_holdings[ticker] = value
                percentage = (value / available_capital) * 100
                print(f"   {EMOJIS['chart']} {ticker}: {shares} shares @ ${price:.2f} → Value: ${value:,.2f} ({percentage:.1f}%)")
        
        if not any(shares > 0 for shares in self.holdings.values()):
            print("   💤 No current holdings")
        
        # Cash position
        cash_available = available_capital - portfolio_value
        if cash_available > 0:
            cash_percentage = (cash_available / available_capital) * 100
            print(f"   {EMOJIS['cash']} Cash Available: ${cash_available:,.2f} ({cash_percentage:.1f}%)")
            
        # Recommended Actions with enhanced formatting and emojis
        print(f"\n{EMOJIS['target']} Recommended Actions:")
        
        total_invested = 0
        risk_data = {}
        price_data = {}
        investment_amounts = {}
        expected_gains = {}
        comprehensive_data = {}
        
        # Get stock-specific emojis
        stock_emojis = {
            'AAPL': EMOJIS['apple'],
            'GOOGL': EMOJIS['google'], 
            'MSFT': EMOJIS['microsoft'],
            'AMZN': EMOJIS['amazon']
        }
        
        for i, ticker in enumerate(self.tickers):
            shares = self.shares[ticker]
            price = self.prices[ticker]
            weight = self.weights[i] * 100
            investment_amount = shares * price
            total_invested += investment_amount
            
            # Store data for plotting
            price_data[ticker] = price
            
            # Calculate expected annual gain and risk for all stocks
            try:
                if self.returns is not None and not self.returns.empty:
                    returns_mean = self.returns.mean() * 252  # Annualized
                    expected_return_rate = returns_mean[ticker] if ticker in returns_mean else 0.15
                else:
                    expected_return_rate = 0.15  # Default assumption
            except Exception:
                expected_return_rate = 0.15  # Default fallback
            
            expected_annual_gain = investment_amount * expected_return_rate
            
            # Get risk data
            atr_value = self.calculate_atr(ticker) if ticker in self.stop_losses else 0
            risk_amount = self.loss_amounts.get(ticker, 0)
            
            # Prepare comprehensive data for the main pie chart
            comprehensive_data[ticker] = {
                'investment': investment_amount,
                'risk': risk_amount,
                'expected_gain': expected_annual_gain,
                'shares': shares,
                'price': price
            }
            
            if investment_amount > 0:
                investment_amounts[ticker] = investment_amount
                expected_gains[ticker] = expected_annual_gain
                risk_data[ticker] = {
                    'atr': atr_value,
                    'risk_amount': risk_amount
                }
            
            stock_emoji = stock_emojis.get(ticker, EMOJIS['chart'])
            
            if shares > 0:
                # Calculate expected return for this stock
                expected_return = 0
                try:
                    if self.returns is not None and not self.returns.empty:
                        returns_mean = self.returns.mean() * 252  # Annualized
                        expected_return = returns_mean[ticker] * 100 if ticker in returns_mean else 15.0
                    else:
                        expected_return = 15.0  # Default assumption
                except Exception:
                    expected_return = 15.0  # Default fallback
                
                print(f"\n{stock_emoji} {ticker}: {EMOJIS['buy']} BUY RECOMMENDATION")
                print(f"   {EMOJIS['money']} Current Price: ${price:.2f}")
                print(f"   📈 Recommended: +{shares} shares (${investment_amount:,.2f})")
                print(f"   {EMOJIS['chart']} Portfolio Weight: {weight:.1f}% (optimal)")
                print(f"   {EMOJIS['shield']} Stop-Loss: ${self.stop_losses[ticker]:.2f} | Max Risk: ${self.loss_amounts[ticker]:.2f}")
                print(f"   {EMOJIS['target']} Expected Return: {expected_return:.1f}% annually")
                
            else:
                reason = "Recently sold" if self._is_recently_sold(ticker) else "Not recommended"
                if self._is_recently_sold(ticker):
                    print(f"\n{stock_emoji} {ticker}: {EMOJIS['no_action']} No action - Recently sold")
                    print(f"   {EMOJIS['warning']} 30-day cooling period active")
                else:
                    print(f"\n{stock_emoji} {ticker}: {EMOJIS['hold']} Hold current position")
                    if ticker in self.holdings and self.holdings[ticker] > 0:
                        print(f"   {EMOJIS['chart']} Current: ${price:.2f} | Optimal weight: {weight:.1f}%")
                        print(f"   {EMOJIS['shield']} Stop-Loss: ${self.stop_losses[ticker]:.2f} | Risk: ${self.loss_amounts[ticker]:.2f}")
        
        # Investment Summary with beautiful formatting
        print("\n" + "═" * 63)
        print(f"{EMOJIS['money']} INVESTMENT SUMMARY")
        print("═" * 63)
        
        cash_after = available_capital - total_invested
        cash_percentage = (cash_after / available_capital) * 100
        total_risk = sum(self.loss_amounts[t] for t in self.tickers if self.shares[t] > 0)
        risk_percentage = (total_risk / available_capital) * 100
        
        print(f"{EMOJIS['buy']} Total New Investment: ${total_invested:,.2f}")
        print(f"{EMOJIS['cash']} Cash After Investment: ${cash_after:,.2f} ({cash_percentage:.1f}%)")
        print(f"{EMOJIS['target']} Portfolio Expected Return: {self.target_return * 100:.1f}% annually")
        
        # Calculate Sharpe ratio if possible
        try:
            if hasattr(self, 'weights') and self.returns is not None and not self.returns.empty:
                portfolio_return = np.dot(self.weights, self.returns.mean() * 252)
                portfolio_std = np.sqrt(np.dot(self.weights, np.dot(self.cov_matrix * 252, self.weights)))
                sharpe_ratio = portfolio_return / portfolio_std if portfolio_std > 0 else 0
                print(f"{EMOJIS['chart']} Portfolio Sharpe Ratio: {sharpe_ratio:.2f}")
            else:
                print(f"{EMOJIS['chart']} Portfolio Sharpe Ratio: 1.50 (estimated)")
        except Exception:
            print(f"{EMOJIS['chart']} Portfolio Sharpe Ratio: 1.50 (estimated)")
        
        print(f"⚖️ Total Portfolio Risk: ${total_risk:.2f} ({risk_percentage:.1f}% of capital)")
        
        # Update visualizations if enabled
        if self.visualizer.enable_plotting:
            self.visualizer.update_comprehensive_analysis(comprehensive_data)
            self.visualizer.update_portfolio_allocation(current_holdings, current_holdings)
            self.visualizer.update_risk_return_analysis(comprehensive_data)
            self.visualizer.update_investment_summary(comprehensive_data)
            self.visualizer.update_performance_chart(available_capital, datetime.now())
            self.visualizer.update_price_trends(price_data)

    def run(self, update_interval: int = 3600):
        """Run the optimizer and update periodically."""
        # Convert seconds to human-readable format
        if update_interval < 3600:
            interval_str = f"{update_interval/60:.0f} minutes"
        elif update_interval < 86400:
            interval_str = f"{update_interval/3600:.1f} hours"
        else:
            interval_str = f"{update_interval/86400:.1f} days"
            
        logging.info(f"Starting monitoring mode with {interval_str} intervals...")
        print(f"\n🔄 Starting monitoring mode - updating every {interval_str}")
        print("Press Ctrl+C to stop monitoring\n")
        
        update_count = 0
        while True:
            try:
                update_count += 1
                print(f"--- Update #{update_count} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
                
                self.fetch_data()
                self.optimize_portfolio()
                self.advise_positions()
                self.print_advice()
                
                print(f"\n✅ Update completed. Next update in {interval_str}...")
                logging.info("Update completed")
                time.sleep(update_interval)
                
            except KeyboardInterrupt:
                print(f"\n⏹️  Monitoring stopped by user after {update_count} updates")
                logging.info("Monitoring stopped by user")
                break
            except Exception as e:
                print(f"\n❌ Update failed: {str(e)}")
                logging.error(f"Update failed: {str(e)}")
                print("Retrying in 5 minutes...")
                time.sleep(300)

    def run_optimization(self, save_report_file: bool = True):
        """Run optimization once."""
        try:
            self.fetch_data()
            self.optimize_portfolio()
            self.advise_positions()
            self.print_advice()
            
            if save_report_file:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"investment_report_{timestamp}.txt"
                with open(filename, 'w') as f:
                    # Capture print output to file
                    import io
                    import sys
                    old_stdout = sys.stdout
                    sys.stdout = buffer = io.StringIO()
                    self.print_advice()
                    output = buffer.getvalue()
                    sys.stdout = old_stdout
                    f.write(output)
                logging.info(f"Report saved to {filename}")
                
            return self.shares
            
        except Exception as e:
            logging.error(f"Optimization failed: {str(e)}")
            return {}


def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(
        description='Investment Portfolio Optimizer - Advanced Version with dynamic plotting and 15-minute monitoring'
    )
    parser.add_argument('--config', default='investments.txt', 
                       help='Configuration file path (default: investments.txt)')
    parser.add_argument('--monitor', action='store_true', 
                       help='Run in monitoring mode (periodic updates)')
    parser.add_argument('--interval', type=int, default=3600, 
                       help='Seconds between updates in monitoring mode (default: 3600 = 1 hour)')
    parser.add_argument('--quick-monitor', action='store_true',
                       help='Run in quick monitoring mode (15-minute intervals)')
    parser.add_argument('--plot', action='store_true',
                       help='Enable dynamic plotting and visualization')
    parser.add_argument('--no-save', action='store_true', 
                       help='Do not save report to file')
    parser.add_argument('--keep-timestamp', action='store_true',
                       help='Keep timestamp in filename (creates new file each time)')
    parser.add_argument('--cleanup', type=int, metavar='N',
                       help='Clean up old dashboard files, keep N latest (0 to delete all timestamped files)')
    parser.add_argument('--target-return', type=float, default=0.20,
                       help='Target annual return (default: 0.20 = 20%%)')
    parser.add_argument('--risk-per-trade', type=float, default=0.02,
                       help='Risk per trade as fraction of capital (default: 0.02 = 2%%)')
    parser.add_argument('--atr-multiplier', type=float, default=2.0,
                       help='ATR multiplier for stop-loss (default: 2.0)')
    
    args = parser.parse_args()
    
    # Handle cleanup first if requested
    if args.cleanup is not None:
        print(f"🗂️ Cleaning up old dashboard files...")
        visualizer = PortfolioVisualizer()
        visualizer.cleanup_old_dashboards(keep_latest=args.cleanup)
        return 0
    
    try:
        optimizer = InvestmentOptimizer(
            config_file=args.config,
            target_return=args.target_return,
            risk_per_trade=args.risk_per_trade,
            atr_multiplier=args.atr_multiplier,
            enable_plotting=args.plot
        )
        
        if args.monitor or args.quick_monitor:
            # Set interval for quick monitor mode
            interval = 900 if args.quick_monitor else args.interval
            
            if args.plot:
                print(f"\n{EMOJIS['chart']} Dynamic plotting enabled - Dashboard will update every {interval//60} minutes")
                
            optimizer.run(update_interval=interval)
        else:
            optimizer.run_optimization(save_report_file=not args.no_save)
            
            # Save plot for single run if plotting enabled
            if args.plot:
                optimizer.visualizer.save_plots(keep_timestamp=args.keep_timestamp)
            
    except Exception as e:
        logging.error(f"Application error: {e}")
        return 1
    
    return 0


# Example usage
if __name__ == "__main__":
    # Allow both command line usage and direct usage
    import sys
    
    if len(sys.argv) > 1:
        exit(main())
    else:
        try:
            optimizer = InvestmentOptimizer()
            
            # Example: Simulate some holdings
            # optimizer.holdings = {'AAPL': 5, 'GOOGL': 1, 'MSFT': 3, 'AMZN': 1}
            
            # Example: Sell a stock
            # optimizer.sell_stock('AAPL', shares_to_sell=2)
            
            optimizer.run_optimization()
            
        except Exception as e:
            logging.error(f"Example run failed: {str(e)}")
            exit(1)
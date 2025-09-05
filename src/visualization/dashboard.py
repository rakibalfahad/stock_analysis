"""
Portfolio visualization and dashboard system
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import yfinance as yf
import glob
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

from ..utils.constants import EMOJIS, COLORS, DASHBOARD_FILE
from ..utils.config import format_currency, format_percentage, get_color_for_gain_risk_ratio
from ..utils.helpers import calculate_atr

# Set style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class PortfolioVisualizer:
    """
    Portfolio visualization and dashboard system
    """
    
    def __init__(self, enable_plotting: bool = True):
        """
        Initialize the visualizer
        
        Args:
            enable_plotting: Whether to enable plotting functionality
        """
        self.enable_plotting = enable_plotting
        self.fig = None
        self.axes = None
        
        if enable_plotting:
            self.setup_plots()
    
    def setup_plots(self) -> None:
        """Setup the plotting environment"""
        if not self.enable_plotting:
            return
        
        try:
            # Create figure with 2x3 subplot grid
            self.fig, self.axes = plt.subplots(2, 3, figsize=(18, 12))
            self.fig.suptitle(
                f'{EMOJIS["chart"]} Investment Portfolio Dashboard - {datetime.now().strftime("%Y-%m-%d %H:%M")}',
                fontsize=16, fontweight='bold'
            )
            
            plt.tight_layout()
            
        except Exception as e:
            logging.warning(f"Could not setup plots: {e}")
            self.enable_plotting = False
    
    def update_portfolio_allocation(self, config: Dict[str, Any], 
                                  current_prices: Dict[str, float]) -> None:
        """Update current portfolio allocation chart"""
        if not self.enable_plotting or self.axes is None:
            return
        
        try:
            ax = self.axes[0, 0]
            ax.clear()
            
            # Calculate current portfolio values
            holdings = {}
            total_value = 0
            
            for symbol, data in config['stocks'].items():
                if data['shares'] > 0:
                    value = data['shares'] * current_prices.get(symbol, 0)
                    holdings[symbol] = value
                    total_value += value
            
            # Add cash
            cash = config['cash']
            if cash > 0:
                holdings['Cash'] = cash
                total_value += cash
            
            if holdings:
                labels = list(holdings.keys())
                sizes = list(holdings.values())
                colors = plt.cm.Set3(np.linspace(0, 1, len(labels)))
                
                wedges, texts, autotexts = ax.pie(
                    sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                    startangle=90, explode=[0.05] * len(labels)
                )
                
                for autotext in autotexts:
                    autotext.set_color('white')
                    autotext.set_fontweight('bold')
            else:
                ax.text(0.5, 0.5, 'No Current Holdings', 
                       horizontalalignment='center', verticalalignment='center',
                       transform=ax.transAxes, fontsize=14)
            
            ax.set_title(f'{EMOJIS["money_bag"]} Current Portfolio\nTotal: {format_currency(total_value)}', 
                        fontweight='bold')
            
        except Exception as e:
            logging.warning(f"Error updating portfolio allocation: {e}")
    
    def update_comprehensive_analysis(self, recommendations: Dict[str, Dict[str, Any]], 
                                    config: Dict[str, Any]) -> None:
        """Update comprehensive investment analysis chart"""
        if not self.enable_plotting or self.axes is None:
            return
        
        try:
            ax = self.axes[0, 1]
            ax.clear()
            
            # Collect investment data
            investments = []
            risks = []
            gains = []
            labels = []
            
            for symbol, rec in recommendations.items():
                if rec['action'] == 'BUY':
                    investment = rec['shares'] * rec['current_price']
                    risk = rec.get('details', {}).get('max_risk', 0)
                    expected_return = rec.get('details', {}).get('expected_return', 0)
                    gain = investment * expected_return
                    
                    investments.append(investment)
                    risks.append(risk)
                    gains.append(gain)
                    labels.append(symbol)
            
            if investments:
                # Calculate gain-to-risk ratios for color coding
                gain_risk_ratios = [g/r if r > 0 else 0 for g, r in zip(gains, risks)]
                colors = [get_color_for_gain_risk_ratio(ratio) for ratio in gain_risk_ratios]
                
                # Create pie chart
                wedges, texts, autotexts = ax.pie(
                    investments, labels=labels, colors=colors,
                    autopct='%1.1f%%', startangle=90,
                    explode=[0.05] * len(investments)
                )
                
                for autotext in autotexts:
                    autotext.set_color('white')
                    autotext.set_fontweight('bold')
                
                # Add legend with detailed information
                legend_labels = []
                for i, symbol in enumerate(labels):
                    legend_labels.append(
                        f"{symbol}: {format_currency(investments[i])}\n"
                        f"Risk: {format_currency(risks[i])}, Gain: {format_currency(gains[i])}\n"
                        f"Ratio: {gain_risk_ratios[i]:.1f}x"
                    )
                
                ax.legend(wedges, legend_labels, title="Investment Details",
                         loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
            else:
                ax.text(0.5, 0.5, 'No New Investments', 
                       horizontalalignment='center', verticalalignment='center',
                       transform=ax.transAxes, fontsize=14)
            
            ax.set_title(f'{EMOJIS["chart"]} Comprehensive Analysis\nInvestment • Risk • Gain', 
                        fontweight='bold')
            
        except Exception as e:
            logging.warning(f"Error updating comprehensive analysis: {e}")
    
    def update_investment_summary(self, recommendations: Dict[str, Dict[str, Any]],
                                config: Dict[str, Any]) -> None:
        """Update investment summary metrics"""
        if not self.enable_plotting or self.axes is None:
            return
        
        try:
            ax = self.axes[0, 2]
            ax.clear()
            ax.axis('off')
            
            # Calculate summary metrics
            total_investment = sum(
                rec['shares'] * rec['current_price'] 
                for rec in recommendations.values() 
                if rec['action'] == 'BUY'
            )
            
            total_risk = sum(
                rec.get('details', {}).get('max_risk', 0)
                for rec in recommendations.values()
            )
            
            total_expected_gain = sum(
                rec['shares'] * rec['current_price'] * rec.get('details', {}).get('expected_return', 0)
                for rec in recommendations.values()
                if rec['action'] == 'BUY'
            )
            
            cash_after = config['cash'] - total_investment
            total_capital = config['cash']
            
            # Create summary text
            summary_text = f"""
{EMOJIS['money_bag']} INVESTMENT SUMMARY

{EMOJIS['shopping_cart']} New Investment:
{format_currency(total_investment)}

{EMOJIS['cash']} Remaining Cash:
{format_currency(cash_after)}
({format_percentage(cash_after/total_capital * 100)})

{EMOJIS['shield']} Total Risk:
{format_currency(total_risk)}
({format_percentage(total_risk/total_capital * 100)})

{EMOJIS['up_trend']} Expected Gain:
{format_currency(total_expected_gain)}

{EMOJIS['scales']} Risk/Reward Ratio:
{total_expected_gain/total_risk:.2f}x
""" if total_risk > 0 else f"""
{EMOJIS['money_bag']} INVESTMENT SUMMARY

{EMOJIS['shopping_cart']} New Investment:
{format_currency(total_investment)}

{EMOJIS['cash']} Remaining Cash:
{format_currency(cash_after)}
({format_percentage(cash_after/total_capital * 100)})

{EMOJIS['up_trend']} Expected Gain:
{format_currency(total_expected_gain)}
"""
            
            ax.text(0.05, 0.95, summary_text, transform=ax.transAxes,
                   fontsize=12, verticalalignment='top', fontfamily='monospace',
                   bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.7))
            
        except Exception as e:
            logging.warning(f"Error updating investment summary: {e}")
    
    def update_portfolio_performance(self, config: Dict[str, Any]) -> None:
        """Update portfolio performance over time"""
        if not self.enable_plotting or self.axes is None:
            return
        
        try:
            ax = self.axes[1, 0]
            ax.clear()
            
            # Create mock performance data (in real implementation, load historical data)
            dates = pd.date_range(start=datetime.now() - timedelta(days=180), 
                                 end=datetime.now(), freq='D')
            
            # Simple growth simulation
            initial_value = 10000
            values = [initial_value]
            for i in range(1, len(dates)):
                change = np.random.normal(0.001, 0.02)  # Daily change
                values.append(values[-1] * (1 + change))
            
            ax.plot(dates, values, linewidth=2, color=COLORS['primary'])
            ax.fill_between(dates, values, alpha=0.3, color=COLORS['primary'])
            
            ax.set_title(f'{EMOJIS["up_trend"]} Portfolio Value Over Time', fontweight='bold')
            ax.set_xlabel('Date')
            ax.set_ylabel('Portfolio Value ($)')
            ax.grid(True, alpha=0.3)
            
            # Format y-axis as currency
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
            
        except Exception as e:
            logging.warning(f"Error updating portfolio performance: {e}")
    
    def update_risk_return_analysis(self, expected_returns: Dict[str, float],
                                  volatilities: Dict[str, float]) -> None:
        """Update risk vs return scatter plot"""
        if not self.enable_plotting or self.axes is None:
            return
        
        try:
            ax = self.axes[1, 1]
            ax.clear()
            
            if expected_returns and volatilities:
                symbols = list(expected_returns.keys())
                returns = [expected_returns[symbol] * 100 for symbol in symbols]  # Convert to percentage
                risks = [volatilities[symbol] * 100 for symbol in symbols]  # Convert to percentage
                
                colors = plt.cm.viridis(np.linspace(0, 1, len(symbols)))
                
                scatter = ax.scatter(risks, returns, c=colors, s=100, alpha=0.7)
                
                for i, symbol in enumerate(symbols):
                    ax.annotate(symbol, (risks[i], returns[i]), 
                               xytext=(5, 5), textcoords='offset points',
                               fontsize=10, fontweight='bold')
                
                ax.set_xlabel('Risk (Volatility %)')
                ax.set_ylabel('Expected Return (%)')
                ax.grid(True, alpha=0.3)
            else:
                ax.text(0.5, 0.5, 'No Risk/Return Data', 
                       horizontalalignment='center', verticalalignment='center',
                       transform=ax.transAxes, fontsize=14)
            
            ax.set_title(f'{EMOJIS["scales"]} Risk vs Return Analysis', fontweight='bold')
            
        except Exception as e:
            logging.warning(f"Error updating risk return analysis: {e}")
    
    def update_stock_trends(self, tickers: List[str]) -> None:
        """Update stock price trends"""
        if not self.enable_plotting or self.axes is None:
            return
        
        try:
            ax = self.axes[1, 2]
            ax.clear()
            
            # Fetch recent price data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            colors = plt.cm.tab10(np.linspace(0, 1, len(tickers)))
            
            for i, ticker in enumerate(tickers):
                try:
                    data = yf.download(ticker, start=start_date, end=end_date, interval='1d')
                    if not data.empty:
                        # Normalize prices to show percentage change
                        normalized = (data['Close'] / data['Close'].iloc[0] - 1) * 100
                        ax.plot(normalized.index, normalized, label=ticker, 
                               color=colors[i], linewidth=2)
                except Exception as e:
                    logging.warning(f"Could not fetch trend data for {ticker}: {e}")
            
            ax.set_title(f'{EMOJIS["up_trend"]} Stock Price Trends (30 days)', fontweight='bold')
            ax.set_xlabel('Date')
            ax.set_ylabel('Price Change (%)')
            ax.legend()
            ax.grid(True, alpha=0.3)
            ax.axhline(y=0, color='black', linestyle='-', alpha=0.5)
            
        except Exception as e:
            logging.warning(f"Error updating stock trends: {e}")
    
    def update_all_plots(self, optimizer) -> None:
        """Update all plots with current data"""
        if not self.enable_plotting:
            return
        
        try:
            recommendations = optimizer.get_trading_recommendations()
            
            self.update_portfolio_allocation(optimizer.config, optimizer.current_prices)
            self.update_comprehensive_analysis(recommendations, optimizer.config)
            self.update_investment_summary(recommendations, optimizer.config)
            self.update_portfolio_performance(optimizer.config)
            self.update_risk_return_analysis(optimizer.expected_returns, optimizer.volatilities)
            self.update_stock_trends(optimizer.tickers)
            
            plt.tight_layout()
            
        except Exception as e:
            logging.warning(f"Error updating plots: {e}")
    
    def save_plots(self, filename_prefix: str = "portfolio_dashboard", 
                   keep_timestamp: bool = False) -> Optional[str]:
        """Save current plots to file"""
        if not self.enable_plotting or self.fig is None:
            return None
        
        try:
            if keep_timestamp:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{filename_prefix}_{timestamp}.png"
            else:
                filename = f"{filename_prefix}.png"
            
            self.fig.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"{EMOJIS['chart']} Dashboard saved as {filename}")
            return filename
            
        except Exception as e:
            logging.warning(f"Could not save dashboard: {e}")
            return None
    
    def cleanup_old_dashboards(self, keep_latest: int = 5) -> None:
        """Clean up old timestamped dashboard files"""
        pattern = "portfolio_dashboard_*.png"
        files = glob.glob(pattern)
        
        if not files:
            print(f"{EMOJIS['folder']} No old dashboard files found")
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
                logging.warning(f"Could not delete {file}: {e}")
        
        if deleted_count > 0:
            print(f"{EMOJIS['trash']} Cleaned up {deleted_count} old dashboard file(s)")
            if keep_latest > 0 and len(files) > keep_latest:
                print(f"{EMOJIS['folder']} Kept {min(keep_latest, len(files))} latest files")
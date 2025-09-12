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
import warnings
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

# Suppress specific warnings
warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')
warnings.filterwarnings('ignore', category=FutureWarning, module='yfinance')
warnings.filterwarnings('ignore', message='.*missing from font.*')
warnings.filterwarnings('ignore', message='.*auto_adjust.*')

# Configure matplotlib to handle missing fonts gracefully
plt.rcParams['font.family'] = ['DejaVu Sans', 'Arial', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

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
            # Use simple text instead of emojis for title to avoid font warnings
            self.fig.suptitle(
                f'Investment Portfolio Dashboard - {datetime.now().strftime("%Y-%m-%d %H:%M")}',
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
            
            ax.set_title(f'Current Portfolio\nTotal: {format_currency(total_value)}', 
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
            
            ax.set_title(f'Comprehensive Analysis\nInvestment • Risk • Gain', 
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
            
            # Create summary text without emojis
            summary_text = f"""
INVESTMENT SUMMARY

New Investment:
{format_currency(total_investment)}

Remaining Cash:
{format_currency(cash_after)}
({format_percentage(cash_after/total_capital * 100)})

Total Risk:
{format_currency(total_risk)}
({format_percentage(total_risk/total_capital * 100)})

Expected Gain:
{format_currency(total_expected_gain)}

Risk/Reward Ratio:
{total_expected_gain/total_risk:.2f}x
""" if total_risk > 0 else f"""
INVESTMENT SUMMARY

New Investment:
{format_currency(total_investment)}

Remaining Cash:
{format_currency(cash_after)}
({format_percentage(cash_after/total_capital * 100)})

Expected Gain:
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
            
            ax.set_title('Portfolio Value Over Time', fontweight='bold')
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
            
            ax.set_title('Risk vs Return Analysis', fontweight='bold')
            
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
                    # Suppress yfinance warnings
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        data = yf.download(ticker, start=start_date, end=end_date, interval='1d', progress=False)
                    if not data.empty:
                        # Normalize prices to show percentage change
                        normalized = (data['Close'] / data['Close'].iloc[0] - 1) * 100
                        ax.plot(normalized.index, normalized, label=ticker, 
                               color=colors[i], linewidth=2)
                except Exception as e:
                    logging.warning(f"Could not fetch trend data for {ticker}: {e}")
            
            ax.set_title('Stock Price Trends (30 days)', fontweight='bold')
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
    
    def create_comparison_dashboard(self, comparison_result: Dict[str, Any], save_file: bool = True) -> Optional[str]:
        """
        Create a visual comparison dashboard for two stocks
        
        Args:
            comparison_result: Result from StockComparator.compare_stocks()
            save_file: Whether to save the dashboard as a file
            
        Returns:
            Filename if saved, None otherwise
        """
        if not self.enable_plotting or comparison_result.get('error'):
            return None
        
        try:
            # Extract data
            symbol1 = comparison_result['symbol1']
            symbol2 = comparison_result['symbol2']
            stock1_data = comparison_result['stock1_data']
            stock2_data = comparison_result['stock2_data']
            scores = comparison_result['scores']
            category_scores = comparison_result['category_scores']
            rec = comparison_result['recommendation']
            strategy = comparison_result['strategy']
            
            # Create figure with subplots
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle(f'Stock Comparison Dashboard: {symbol1} vs {symbol2}\n'
                        f'{strategy.title()} Strategy | Recommendation: {rec["choice"]} ({rec["confidence"]:.0%} confidence)',
                        fontsize=16, fontweight='bold', y=0.95)
            
            # 1. Overall Scores Comparison (Top Left)
            scores_data = [scores['stock1'], scores['stock2']]
            colors = ['#2E8B57' if scores['stock1'] > scores['stock2'] else '#CD5C5C',
                     '#2E8B57' if scores['stock2'] > scores['stock1'] else '#CD5C5C']
            
            bars = ax1.bar([symbol1, symbol2], scores_data, color=colors, alpha=0.8)
            ax1.set_title('Overall Weighted Scores', fontweight='bold')
            ax1.set_ylabel('Score')
            ax1.set_ylim(0, 1)
            
            # Add score labels on bars
            for bar, score in zip(bars, scores_data):
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                        f'{score:.3f}', ha='center', va='bottom', fontweight='bold')
            
            # 2. Category Breakdown (Top Right)
            categories = list(category_scores.keys())
            stock1_cat_scores = [category_scores[cat][0] for cat in categories]
            stock2_cat_scores = [category_scores[cat][1] for cat in categories]
            
            x = np.arange(len(categories))
            width = 0.35
            
            ax2.bar(x - width/2, stock1_cat_scores, width, label=symbol1, alpha=0.8, color='#1f77b4')
            ax2.bar(x + width/2, stock2_cat_scores, width, label=symbol2, alpha=0.8, color='#ff7f0e')
            
            ax2.set_title('Category Score Breakdown', fontweight='bold')
            ax2.set_ylabel('Category Score')
            ax2.set_xticks(x)
            ax2.set_xticklabels([cat.replace('_', '\n').title() for cat in categories], rotation=45, ha='right')
            ax2.legend()
            ax2.set_ylim(0, 1)
            
            # 3. Key Metrics Comparison (Bottom Left)
            key_metrics = {
                'P/E Ratio': (stock1_data.get('pe_ratio'), stock2_data.get('pe_ratio')),
                'ROE': (stock1_data.get('roe'), stock2_data.get('roe')),
                'Revenue Growth': (stock1_data.get('revenue_growth'), stock2_data.get('revenue_growth')),
                'Debt/Equity': (stock1_data.get('debt_to_equity'), stock2_data.get('debt_to_equity')),
                'Beta': (stock1_data.get('beta'), stock2_data.get('beta'))
            }
            
            # Filter out None values and create comparison
            valid_metrics = {k: v for k, v in key_metrics.items() if v[0] is not None and v[1] is not None}
            
            if valid_metrics:
                metric_names = list(valid_metrics.keys())
                metric_values1 = [valid_metrics[m][0] for m in metric_names]
                metric_values2 = [valid_metrics[m][1] for m in metric_names]
                
                # Normalize values for visualization (0-1 scale)
                normalized_vals1 = []
                normalized_vals2 = []
                
                for i, metric in enumerate(metric_names):
                    val1, val2 = metric_values1[i], metric_values2[i]
                    
                    # Handle negative values and normalization
                    if val1 <= 0 or val2 <= 0:
                        normalized_vals1.append(0.5)
                        normalized_vals2.append(0.5)
                    else:
                        max_val = max(val1, val2)
                        min_val = min(val1, val2)
                        range_val = max_val - min_val if max_val != min_val else 1
                        
                        # For metrics where lower is better (P/E, Debt/Equity, Beta)
                        if metric in ['P/E Ratio', 'Debt/Equity', 'Beta']:
                            norm1 = 1 - (val1 - min_val) / range_val
                            norm2 = 1 - (val2 - min_val) / range_val
                        else:
                            norm1 = (val1 - min_val) / range_val
                            norm2 = (val2 - min_val) / range_val
                        
                        normalized_vals1.append(norm1)
                        normalized_vals2.append(norm2)
                
                x_pos = np.arange(len(metric_names))
                ax3.bar(x_pos - 0.2, normalized_vals1, 0.4, label=symbol1, alpha=0.8, color='#1f77b4')
                ax3.bar(x_pos + 0.2, normalized_vals2, 0.4, label=symbol2, alpha=0.8, color='#ff7f0e')
                
                ax3.set_title('Key Metrics Comparison (Normalized)', fontweight='bold')
                ax3.set_ylabel('Relative Performance (0-1)')
                ax3.set_xticks(x_pos)
                ax3.set_xticklabels(metric_names, rotation=45, ha='right')
                ax3.legend()
                ax3.set_ylim(0, 1)
            
            # 4. Price Performance Chart (Bottom Right)
            try:
                # Get recent price data for both stocks
                end_date = datetime.now()
                start_date = end_date - timedelta(days=180)  # 6 months
                
                stock1_hist = yf.download(symbol1, start=start_date, end=end_date, progress=False)['Close']
                stock2_hist = yf.download(symbol2, start=start_date, end=end_date, progress=False)['Close']
                
                if not stock1_hist.empty and not stock2_hist.empty:
                    # Normalize to starting price (percentage change)
                    stock1_norm = (stock1_hist / stock1_hist.iloc[0] - 1) * 100
                    stock2_norm = (stock2_hist / stock2_hist.iloc[0] - 1) * 100
                    
                    ax4.plot(stock1_norm.index, stock1_norm.values, label=f'{symbol1}', color='#1f77b4', linewidth=2)
                    ax4.plot(stock2_norm.index, stock2_norm.values, label=f'{symbol2}', color='#ff7f0e', linewidth=2)
                    
                    ax4.set_title('6-Month Price Performance', fontweight='bold')
                    ax4.set_ylabel('Return (%)')
                    ax4.legend()
                    ax4.grid(True, alpha=0.3)
                    ax4.axhline(y=0, color='black', linestyle='-', alpha=0.5)
                    
                    # Add current return annotations
                    final_return1 = stock1_norm.iloc[-1]
                    final_return2 = stock2_norm.iloc[-1]
                    ax4.text(0.02, 0.98, f'{symbol1}: {final_return1:+.1f}%', 
                            transform=ax4.transAxes, va='top', bbox=dict(boxstyle='round', facecolor='#1f77b4', alpha=0.2))
                    ax4.text(0.02, 0.90, f'{symbol2}: {final_return2:+.1f}%',
                            transform=ax4.transAxes, va='top', bbox=dict(boxstyle='round', facecolor='#ff7f0e', alpha=0.2))
                
            except Exception as e:
                logging.warning(f"Could not create price chart: {e}")
                ax4.text(0.5, 0.5, 'Price chart unavailable', ha='center', va='center', transform=ax4.transAxes)
                ax4.set_title('Price Performance Chart', fontweight='bold')
            
            # Add recommendation box
            rec_text = f"RECOMMENDATION: {rec['choice']}\nConfidence: {rec['confidence']:.0%}\nStrategy: {strategy.title()}"
            fig.text(0.02, 0.02, rec_text, fontsize=12, fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgreen' if rec['choice'] != 'NEUTRAL' else 'lightyellow', alpha=0.8))
            
            plt.tight_layout()
            plt.subplots_adjust(top=0.90, bottom=0.15)
            
            if save_file:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"stock_comparison_{symbol1}_vs_{symbol2}_{timestamp}.png"
                plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
                plt.show()
                return filename
            else:
                plt.show()
                return None
                
        except Exception as e:
            logging.error(f"Error creating comparison dashboard: {e}")
            print(f"{EMOJIS['warning']} Could not create comparison dashboard: {e}")
            return None
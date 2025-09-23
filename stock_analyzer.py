#!/usr/bin/env python3
"""
Stock Risk vs Return Analysis Tool

A standalone script that reads stock symbols from an Excel file, fetches market data,
and generates side-by-side plots of:
1. Risk vs Return Analysis (scatter plot with bubble sizes, Sharpe ratio colors, and 52-week position indicators)
2. 30-Day Stock Price Trends (normalized comparison)

Features:
- Reads stock symbols from Excel or CSV files
- Fetches real-time market data including 52-week high/low
- Calculates comprehensive risk and return metrics
- Visual indicators for 52-week price position
- Generates professional side-by-side visualizations
- Saves high-quality PNG output
- Detailed statistics with 52-week analysis

Author: Investment Management System
Date: September 2025
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from bokeh.plotting import figure, output_file as bokeh_output_file, save as bokeh_save
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.resources import CDN
import yfinance as yf
import warnings
from datetime import datetime
import argparse

warnings.filterwarnings('ignore', category=FutureWarning, module='yfinance')
warnings.filterwarnings('ignore', message='.*auto_adjust.*')
warnings.filterwarnings('ignore', message='.*Glyph.*missing.*')
warnings.filterwarnings('ignore', message='.*findfont.*')

plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

EMOJIS = {
    'chart': '📊',
    'money': '💰',
    'rocket': '🚀',
    'target': '🎯',
    'fire': '🔥',
    'warning': '⚠️',
    'check': '✅',
    'calendar': '📅',
    'computer': '🧮'
}

class StockAnalyzer:
    """
    Stock Risk vs Return analyzer with 30-day price trend visualization
    """
    
    def __init__(self, excel_file: str, period: str = '1y', price_period: str = '30d', sheet_name: str = None):
        """
        Initialize the analyzer.
        Args:
            excel_file: Path to Excel file containing stock symbols
            period: Period for risk/return calculation (default: 1y)
            price_period: Period for price trends (default: 30d)
            sheet_name: Specific Excel sheet to read (default: first sheet or 'All_Stocks')
        """
        self.excel_file = excel_file
        self.period = period
        self.price_period = price_period
        self.sheet_name = sheet_name
        self.stock_symbols = []
        self.stock_data = {}
        self.risk_return_data = {}
        self.price_trend_data = {}
        
        print(f"{EMOJIS['rocket']} Stock Risk vs Return Analysis Tool")
        print(f"{EMOJIS['calendar']} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    def load_stock_symbols(self) -> bool:
        """
        Load stock symbols from Excel or CSV file with sheet selection.
        Returns True if successful, False otherwise.
        """
        try:
            print(f"\n{EMOJIS['chart']} Loading stock symbols from {self.excel_file}...")
            
            # Detect file type and load accordingly
            file_ext = os.path.splitext(self.excel_file)[1].lower()
            
            if file_ext in ['.xlsx', '.xls']:
                # For Excel files, handle sheet selection
                try:
                    # First, get available sheets
                    excel_file = pd.ExcelFile(self.excel_file)
                    available_sheets = excel_file.sheet_names
                    print(f"   📋 Available sheets: {', '.join(available_sheets)}")
                    
                    # Determine which sheet to use
                    if self.sheet_name:
                        if self.sheet_name in available_sheets:
                            sheet_to_use = self.sheet_name
                            print(f"   🎯 Using specified sheet: {sheet_to_use}")
                        else:
                            print(f"   {EMOJIS['warning']} Sheet '{self.sheet_name}' not found, using first sheet")
                            sheet_to_use = available_sheets[0]
                    else:
                        # Default priority: All_Stocks > first sheet
                        if 'All_Stocks' in available_sheets:
                            sheet_to_use = 'All_Stocks'
                            print(f"   🎯 Using default sheet: {sheet_to_use}")
                        else:
                            sheet_to_use = available_sheets[0]
                            print(f"   🎯 Using first sheet: {sheet_to_use}")
                    
                    df = pd.read_excel(self.excel_file, sheet_name=sheet_to_use)
                    
                except Exception as e:
                    print(f"   {EMOJIS['warning']} Error reading Excel sheets: {e}")
                    df = pd.read_excel(self.excel_file)  # Fallback to default
                    
            elif file_ext == '.csv':
                df = pd.read_csv(self.excel_file)
            else:
                # Try both Excel and CSV
                try:
                    df = pd.read_excel(self.excel_file)
                except:
                    df = pd.read_csv(self.excel_file)
            
            # Display file information
            print(f"   📊 Loaded data: {len(df)} rows, {len(df.columns)} columns")
            if len(df.columns) > 1:
                print(f"   📋 Columns: {', '.join(df.columns.tolist())}")
            
            # Look for stock symbols in common column names
            possible_columns = ['symbol', 'symbols', 'stock', 'stocks', 'ticker', 'tickers', 
                              'Symbol', 'Symbols', 'Stock', 'Stocks', 'Ticker', 'Tickers', 'Code', 'code']
            
            symbol_column = None
            for col in possible_columns:
                if col in df.columns:
                    symbol_column = col
                    break
            
            if symbol_column is None:
                # If no named column found, try first column
                symbol_column = df.columns[0]
                print(f"   {EMOJIS['warning']} No standard symbol column found, using first column: '{symbol_column}'")
            else:
                print(f"   ✅ Found symbol column: '{symbol_column}'")
            
            # Extract symbols and clean them
            symbols = df[symbol_column].dropna().astype(str).str.strip().str.upper()
            self.stock_symbols = [s for s in symbols if s and s != 'NAN' and len(s) <= 10]  # Basic validation
            
            # Show additional information if available
            if 'Company' in df.columns or 'company' in df.columns:
                company_col = 'Company' if 'Company' in df.columns else 'company'
                companies = df[company_col].dropna().head(5).tolist()
                print(f"   🏢 Sample companies: {', '.join([str(c)[:20] + '...' if len(str(c)) > 20 else str(c) for c in companies])}")
            
            if 'Sector' in df.columns or 'sector' in df.columns:
                sector_col = 'Sector' if 'Sector' in df.columns else 'sector'
                sectors = df[sector_col].value_counts().head(3)
                print(f"   🏭 Top sectors: {', '.join([f'{k} ({v})' for k, v in sectors.items()])}")
            
            print(f"   {EMOJIS['check']} Successfully loaded {len(self.stock_symbols)} stock symbols: {', '.join(self.stock_symbols)}")
            
            # Store source data for Excel export
            self.source_data = df
            
            return True
            
        except Exception as e:
            print(f"{EMOJIS['warning']} Error loading file: {e}")
            print(f"Please ensure the file exists and contains a column with stock symbols")
            print(f"Supported formats: .xlsx, .xls, .csv")
            return False
    
    def fetch_market_data(self) -> bool:
        """
        Fetch market data for all stocks.
        Returns True if successful, False otherwise.
        """
        try:
            print(f"\n{EMOJIS['computer']} Fetching market data for {len(self.stock_symbols)} stocks...")
            
            # Fetch data for risk/return analysis
            print(f"   - Risk/Return data ({self.period} period)...")
            risk_data = yf.download(self.stock_symbols, period=self.period, interval='1d', progress=False)
            
            # Fetch data for price trends  
            print(f"   - Price trend data ({self.price_period} period)...")
            price_data = yf.download(self.stock_symbols, period=self.price_period, interval='1d', progress=False)
            
            # Fetch 52-week high/low data
            print(f"   - 52-week high/low data...")
            week52_data = yf.download(self.stock_symbols, period='1y', interval='1d', progress=False)
            
            if risk_data.empty or price_data.empty or week52_data.empty:
                print(f"{EMOJIS['warning']} No data retrieved")
                return False
            
            # Process data for single vs multiple stocks
            if len(self.stock_symbols) == 1:
                symbol = self.stock_symbols[0]
                self.stock_data[symbol] = risk_data
                self.price_trend_data[symbol] = price_data
                # Store 52-week high/low separately
                self.stock_data[symbol].attrs['52_week_high'] = float(week52_data['High'].max())
                self.stock_data[symbol].attrs['52_week_low'] = float(week52_data['Low'].min())
            else:
                for symbol in self.stock_symbols:
                    try:
                        # Extract data for each symbol
                        symbol_risk_data = pd.DataFrame({
                            'Open': risk_data['Open'][symbol] if 'Open' in risk_data.columns else risk_data['Open'],
                            'High': risk_data['High'][symbol] if 'High' in risk_data.columns else risk_data['High'],
                            'Low': risk_data['Low'][symbol] if 'Low' in risk_data.columns else risk_data['Low'],
                            'Close': risk_data['Close'][symbol] if 'Close' in risk_data.columns else risk_data['Close'],
                            'Volume': risk_data['Volume'][symbol] if 'Volume' in risk_data.columns else risk_data['Volume']
                        }).dropna()
                        
                        symbol_price_data = pd.DataFrame({
                            'Close': price_data['Close'][symbol] if 'Close' in price_data.columns else price_data['Close']
                        }).dropna()
                        
                        # Calculate 52-week high/low for this symbol
                        try:
                            symbol_52week_high = week52_data['High'][symbol].max() if 'High' in week52_data.columns else week52_data['High'].max()
                            symbol_52week_low = week52_data['Low'][symbol].min() if 'Low' in week52_data.columns else week52_data['Low'].min()
                        except:
                            symbol_52week_high = symbol_risk_data['High'].max()
                            symbol_52week_low = symbol_risk_data['Low'].min()
                        
                        if not symbol_risk_data.empty and not symbol_price_data.empty:
                            self.stock_data[symbol] = symbol_risk_data
                            self.price_trend_data[symbol] = symbol_price_data
                            # Store 52-week data as attributes
                            self.stock_data[symbol].attrs['52_week_high'] = float(symbol_52week_high)
                            self.stock_data[symbol].attrs['52_week_low'] = float(symbol_52week_low)
                        else:
                            print(f"{EMOJIS['warning']} No data for {symbol}")
                            
                    except Exception as e:
                        print(f"{EMOJIS['warning']} Error processing {symbol}: {e}")
            
            successful_symbols = len(self.stock_data)
            print(f"{EMOJIS['check']} Successfully fetched data for {successful_symbols}/{len(self.stock_symbols)} stocks")
            return successful_symbols > 0
            
        except Exception as e:
            print(f"{EMOJIS['warning']} Error fetching market data: {e}")
            return False
    
    def calculate_risk_return_metrics(self) -> None:
        """
        Calculate risk and return metrics for each stock.
        """
        print(f"\n{EMOJIS['computer']} Calculating risk and return metrics...")
        
        for symbol, data in self.stock_data.items():
            try:
                # Calculate daily returns
                returns = data['Close'].pct_change().dropna()
                
                if len(returns) < 30:  # Need sufficient data
                    print(f"{EMOJIS['warning']} Insufficient data for {symbol}")
                    continue
                
                # Calculate metrics
                expected_return = returns.mean() * 252  # Annualized
                volatility = returns.std() * np.sqrt(252)  # Annualized
                current_price = data['Close'].iloc[-1]
                
                # Try to get market cap (approximate using price and volume)
                try:
                    avg_volume = data['Volume'].tail(30).mean()
                    market_cap_proxy = current_price * avg_volume / 1000000  # Simplified proxy
                except:
                    market_cap_proxy = 1000  # Default value
                
                # Calculate additional metrics
                sharpe_ratio = (expected_return - 0.02) / volatility if volatility > 0 else 0  # Assuming 2% risk-free rate
                max_drawdown = self._calculate_max_drawdown(data['Close'])
                
                # Get 52-week high/low data - access from attributes
                try:
                    week52_high = data.attrs.get('52_week_high', float(data['High'].max()))
                    week52_low = data.attrs.get('52_week_low', float(data['Low'].min()))
                except:
                    # Fallback calculation
                    week52_high = float(data['High'].max())
                    week52_low = float(data['Low'].min())
                
                # Calculate position relative to 52-week range
                week52_range = week52_high - week52_low
                current_position = (current_price - week52_low) / week52_range if week52_range > 0 else 0.5
                
                self.risk_return_data[symbol] = {
                    'expected_return': expected_return,
                    'volatility': volatility,
                    'current_price': current_price,
                    'market_cap_proxy': market_cap_proxy,
                    'sharpe_ratio': sharpe_ratio,
                    'max_drawdown': max_drawdown,
                    'return_percentage': expected_return * 100,
                    'risk_percentage': volatility * 100,
                    '52_week_high': week52_high,
                    '52_week_low': week52_low,
                    '52_week_position': current_position * 100  # Percentage position in 52-week range
                }
                
            except Exception as e:
                print(f"{EMOJIS['warning']} Error calculating metrics for {symbol}: {e}")
        
        print(f"{EMOJIS['check']} Calculated metrics for {len(self.risk_return_data)} stocks")
        
        # Create analysis_results DataFrame for Excel export
        analysis_data = []
        for symbol, metrics in self.risk_return_data.items():
            analysis_data.append({
                'symbol': symbol,
                'expected_return': metrics['expected_return'],
                'volatility': metrics['volatility'],
                'sharpe_ratio': metrics['sharpe_ratio'],
                'market_cap_proxy': metrics['market_cap_proxy'],
                'current_price': metrics['current_price'],
                '52_week_high': metrics['52_week_high'],
                '52_week_low': metrics['52_week_low'],
                '52_week_position': metrics['52_week_position']
            })
        
        self.analysis_results = pd.DataFrame(analysis_data)
    
    def _calculate_max_drawdown(self, prices: pd.Series) -> float:
        """
        Calculate maximum drawdown.
        """
        try:
            cumulative = (1 + prices.pct_change()).cumprod()
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max
            return abs(drawdown.min())
        except:
            return 0.0
    
    def create_visualizations(self, output_file: str = 'stock_analysis.png') -> bool:
        """
        Create side-by-side risk vs return and price trend plots (PNG and interactive HTML).
        Returns True if successful, False otherwise.
        """
        try:
            print(f"\n{EMOJIS['chart']} Creating visualizations...")
            
            # Always create PNG version first
            png_file = output_file if output_file.lower().endswith('.png') else output_file.replace('.html', '.png')
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))
            fig.suptitle(f'Stock Market Analysis Dashboard - {datetime.now().strftime("%Y-%m-%d")}', 
                        fontsize=16, fontweight='bold')
            self._create_risk_return_plot(ax1)
            self._create_price_trend_plot(ax2)
            plt.tight_layout()
            plt.savefig(png_file, dpi=300, bbox_inches='tight', facecolor='white')
            print(f"{EMOJIS['check']} Static analysis saved as {png_file}")
            plt.show()
            
            # Also create interactive HTML version
            html_file = png_file.replace('.png', '.html')
            self._create_bokeh_visualizations(html_file)
            print(f"{EMOJIS['check']} Interactive analysis saved as {html_file}")
            print(f"\n{EMOJIS['computer']} Generated both formats:")
            print(f"   📊 Static PNG: {png_file}")
            print(f"   🔍 Interactive HTML: {html_file} (with zoom/reset tools)")
            
            return True
        except Exception as e:
            print(f"{EMOJIS['warning']} Error creating visualizations: {e}")
            return False

    def _create_bokeh_visualizations(self, output_file: str):
        """
        Create highly informative interactive Bokeh HTML visualizations optimized for many stocks.
        """
        from bokeh.layouts import column
        from bokeh.models import LegendItem, Legend, Span, Label, DataTable, TableColumn, Div
        from bokeh.palettes import Category20, Set3
        from bokeh.plotting import show
        import itertools
        
        # Prepare comprehensive risk/return data
        symbols = list(self.risk_return_data.keys())
        risks = [self.risk_return_data[s]['risk_percentage'] for s in symbols]
        returns = [self.risk_return_data[s]['return_percentage'] for s in symbols]
        market_caps = [self.risk_return_data[s]['market_cap_proxy'] for s in symbols]
        week52_positions = [self.risk_return_data[s]['52_week_position'] for s in symbols]
        sharpe_ratios = [self.risk_return_data[s]['sharpe_ratio'] for s in symbols]
        current_prices = [self.risk_return_data[s]['current_price'] for s in symbols]
        week52_highs = [self.risk_return_data[s]['52_week_high'] for s in symbols]
        week52_lows = [self.risk_return_data[s]['52_week_low'] for s in symbols]
        max_drawdowns = [self.risk_return_data[s]['max_drawdown'] for s in symbols]

        # Generate color palette for many stocks
        if len(symbols) <= 20:
            color_palette = Category20[20] if len(symbols) > 10 else Category20[max(3, len(symbols))]
        else:
            # For more than 20 stocks, cycle through multiple palettes
            color_palette = list(itertools.islice(itertools.cycle(Category20[20] + Set3[12]), len(symbols)))

        # Normalize bubble sizes with better scaling
        if market_caps:
            max_cap = max(market_caps)
            min_cap = min(market_caps)
            cap_range = max_cap - min_cap if max_cap > min_cap else 1
            bubble_sizes = [(cap - min_cap) / cap_range * 40 + 12 for cap in market_caps]
        else:
            bubble_sizes = [20] * len(symbols)

        # Enhanced border color and styling for 52-week position
        def border_color(pos):
            if pos > 80:
                return 'darkgreen'
            elif pos > 50:
                return 'orange' 
            else:
                return 'red'

        def position_icon(pos):
            if pos > 80:
                return '🔥'
            elif pos > 50:
                return '⚡'
            else:
                return '❄️'

        borders = [border_color(pos) for pos in week52_positions]
        position_icons = [position_icon(pos) for pos in week52_positions]

        TOOLS = 'xwheel_zoom,xbox_zoom,box_zoom,reset,hover,save,pan,crosshair'

        # Create informative header
        header_html = f"""
        <div style="text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; padding: 20px; border-radius: 10px; margin: 10px;">
            <h1>📊 Stock Analysis Dashboard</h1>
            <h3>Comprehensive Risk vs Return Analysis with 52-Week Position Indicators</h3>
            <p><strong>Analysis Date:</strong> {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}</p>
            <p><strong>Stocks Analyzed:</strong> {len(symbols)} | <strong>Period:</strong> {self.period} | 
               <strong>Price Trends:</strong> {self.price_period}</p>
            <div style="margin-top: 15px;">
                <span style="background: darkgreen; padding: 5px 10px; border-radius: 5px; margin: 5px;">
                    🔥 Near 52W High (>80%)</span>
                <span style="background: orange; padding: 5px 10px; border-radius: 5px; margin: 5px;">
                    ⚡ Mid-Range (50-80%)</span>
                <span style="background: red; padding: 5px 10px; border-radius: 5px; margin: 5px;">
                    ❄️ Near 52W Low (<50%)</span>
            </div>
        </div>
        """
        header_div = Div(text=header_html, width=1000, height=200)

        # Risk vs Return scatter plot with comprehensive information
        p1 = figure(title='📈 Risk vs Return Analysis with Market Cap & 52-Week Position', 
                   width=1000, height=700, tools=TOOLS,
                   title_location="above")
        
        # Add market statistics as reference lines
        avg_risk = sum(risks) / len(risks)
        avg_return = sum(returns) / len(returns)
        
        # Add reference lines with labels
        risk_line = Span(location=avg_risk, dimension='height', line_color='blue', 
                        line_dash='dashed', line_width=2, line_alpha=0.7)
        return_line = Span(location=avg_return, dimension='width', line_color='green', 
                          line_dash='dashed', line_width=2, line_alpha=0.7)
        p1.add_layout(risk_line)
        p1.add_layout(return_line)
        
        # Add labels for reference lines
        risk_label = Label(x=avg_risk+1, y=max(returns)*0.9, text=f'Avg Risk: {avg_risk:.1f}%',
                          text_color='blue', text_font_size='10pt')
        return_label = Label(x=max(risks)*0.1, y=avg_return+1, text=f'Avg Return: {avg_return:.1f}%',
                           text_color='green', text_font_size='10pt')
        p1.add_layout(risk_label)
        p1.add_layout(return_label)
        
        # Create individual scatter points with comprehensive data
        scatter_renderers = []
        for i, symbol in enumerate(symbols):
            source = ColumnDataSource(data=dict(
                x=[risks[i]],
                y=[returns[i]],
                size=[bubble_sizes[i]],
                border=[borders[i]],
                symbol=[symbol],
                sharpe=[sharpe_ratios[i]],
                week52=[week52_positions[i]],
                current_price=[current_prices[i]],
                week52_high=[week52_highs[i]],
                week52_low=[week52_lows[i]],
                market_cap=[market_caps[i]],
                max_drawdown=[max_drawdowns[i]],
                position_icon=[position_icons[i]],
                performance_rating=[
                    'Excellent' if sharpe_ratios[i] > 1.5 else
                    'Good' if sharpe_ratios[i] > 1.0 else
                    'Fair' if sharpe_ratios[i] > 0.5 else
                    'Poor'
                ]
            ))
            
            renderer = p1.scatter('x', 'y', size='size', color=color_palette[i], 
                                line_color='border', line_width=3, alpha=0.8, source=source)
            scatter_renderers.append((f"{symbol} {position_icons[i]}", [renderer]))

        # Enhanced hover tool with comprehensive information
        hover1 = HoverTool(tooltips=[
            ("🏢 Symbol", "@symbol"),
            ("📊 Performance", "@performance_rating"),  
            ("💰 Current Price", "$@current_price{0.00}"),
            ("📈 Expected Return", "@y{0.2f}%"),
            ("⚖️ Risk (Volatility)", "@x{0.2f}%"),
            ("🎯 Sharpe Ratio", "@sharpe{0.3f}"),
            ("📏 52W Position", "@week52{0.1f}% @position_icon"),
            ("🔝 52W High", "$@week52_high{0.00}"),
            ("🔻 52W Low", "$@week52_low{0.00}"),
            ("💼 Market Cap Proxy", "@market_cap{0.0} M"),
            ("📉 Max Drawdown", "@max_drawdown{0.2%}")
        ])
        p1.add_tools(hover1)
        
        p1.xaxis.axis_label = 'Risk (Volatility %) → Higher Risk →'
        p1.yaxis.axis_label = '← Higher Return ← Expected Return (%)'
        
        # Create toggleable legend with position indicators
        legend_items = [LegendItem(label=label, renderers=renderers) for label, renderers in scatter_renderers]
        legend1 = Legend(items=legend_items, location='top_left', click_policy="hide", label_text_font_size="9pt")
        p1.add_layout(legend1)
        p1.grid.grid_line_alpha = 0.3

        # Add informative subtitle
        p1.add_layout(Label(x=max(risks)*0.02, y=max(returns)*0.95, 
                           text=f"Bubble Size = Market Cap | Border Color = 52W Position | Click Legend to Toggle",
                           text_font_size="10pt", text_color="gray"))

        # Price trends plot with enhanced information
        p2 = figure(title='📈 30-Day Price Trends (Normalized to Starting Price = 100)', 
                   width=1000, height=600, tools=TOOLS, x_axis_type='datetime',
                   title_location="above")
        
        # Add 0% reference line
        zero_line = Span(location=100, dimension='width', line_color='black', 
                        line_dash='solid', line_width=1, line_alpha=0.8)
        p2.add_layout(zero_line)
        
        # Create individual line plots with performance data
        line_renderers = []
        performance_summary = []
        
        for i, (symbol, data) in enumerate(self.price_trend_data.items()):
            prices = data['Close'].dropna()
            if len(prices) > 5:
                norm_prices = (prices / prices.iloc[0]) * 100
                dates = prices.index.to_pydatetime()
                
                # Calculate additional metrics
                price_change = ((prices.iloc[-1] / prices.iloc[0]) - 1) * 100
                max_gain = ((norm_prices.max() / 100) - 1) * 100
                max_loss = ((norm_prices.min() / 100) - 1) * 100
                volatility = norm_prices.std()
                
                performance_summary.append({
                    'symbol': symbol,
                    'change': price_change,
                    'max_gain': max_gain,
                    'max_loss': max_loss,
                    'volatility': volatility
                })
                
                source = ColumnDataSource(data=dict(
                    x=dates,
                    y=norm_prices.values,
                    symbol=[symbol] * len(dates),
                    raw_price=[prices.iloc[j] for j in range(len(dates))],
                    change_pct=[((norm_prices.iloc[j] / 100) - 1) * 100 for j in range(len(dates))],
                    date_str=[d.strftime('%Y-%m-%d') for d in dates]
                ))
                
                line_renderer = p2.line('x', 'y', line_width=3, color=color_palette[i], 
                                      alpha=0.8, source=source)
                circle_renderer = p2.scatter('x', 'y', size=6, color=color_palette[i], 
                                           alpha=0.9, source=source)
                
                # Add final value annotation
                final_change = f"{price_change:+.1f}%"
                final_label = Label(x=dates[-1], y=norm_prices.iloc[-1], 
                                  text=f"{symbol}: {final_change}",
                                  text_font_size="9pt", text_color=color_palette[i])
                p2.add_layout(final_label)
                
                line_renderers.append((f"{symbol} ({final_change})", [line_renderer, circle_renderer]))

        # Enhanced hover for price trends
        hover2 = HoverTool(tooltips=[
            ("📅 Date", "@date_str"),
            ("🏢 Symbol", "@symbol"),  
            ("💰 Price", "$@raw_price{0.00}"),
            ("📊 Normalized", "@y{0.1f}"),
            ("📈 Change", "@change_pct{0.2f}%")
        ])
        p2.add_tools(hover2)

        p2.xaxis.axis_label = 'Date'
        p2.yaxis.axis_label = 'Normalized Price (Starting Price = 100)'
        
        # Create toggleable legend for price trends
        if line_renderers:
            legend_items2 = [LegendItem(label=label, renderers=renderers) for label, renderers in line_renderers]
            legend2 = Legend(items=legend_items2, location='top_left', click_policy="hide", label_text_font_size="9pt")
            p2.add_layout(legend2)
            
        p2.grid.grid_line_alpha = 0.3

        # Add performance statistics table
        if performance_summary:
            perf_df = pd.DataFrame(performance_summary)
            
            # Create summary statistics
            best_performer = perf_df.loc[perf_df['change'].idxmax()]
            worst_performer = perf_df.loc[perf_df['change'].idxmin()]
            most_volatile = perf_df.loc[perf_df['volatility'].idxmax()]
            least_volatile = perf_df.loc[perf_df['volatility'].idxmin()]
            
            stats_html = f"""
            <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; 
                        padding: 20px; border-radius: 10px; margin: 10px;">
                <h3>📊 30-Day Performance Summary</h3>
                <div style="display: flex; flex-wrap: wrap; justify-content: space-around;">
                    <div style="margin: 10px; padding: 10px; background: rgba(255,255,255,0.2); border-radius: 5px;">
                        <h4>🏆 Best Performer</h4>
                        <p><strong>{best_performer['symbol']}</strong>: <span style="color: #4ade80;">{best_performer['change']:+.2f}%</span></p>
                    </div>
                    <div style="margin: 10px; padding: 10px; background: rgba(255,255,255,0.2); border-radius: 5px;">
                        <h4>📉 Worst Performer</h4>
                        <p><strong>{worst_performer['symbol']}</strong>: <span style="color: #f87171;">{worst_performer['change']:+.2f}%</span></p>
                    </div>
                    <div style="margin: 10px; padding: 10px; background: rgba(255,255,255,0.2); border-radius: 5px;">
                        <h4>🌊 Most Volatile</h4>
                        <p><strong>{most_volatile['symbol']}</strong>: {most_volatile['volatility']:.2f} std</p>
                    </div>
                    <div style="margin: 10px; padding: 10px; background: rgba(255,255,255,0.2); border-radius: 5px;">
                        <h4>🎯 Most Stable</h4>
                        <p><strong>{least_volatile['symbol']}</strong>: {least_volatile['volatility']:.2f} std</p>
                    </div>
                </div>
                <div style="margin-top: 15px; text-align: center;">
                    <p><strong>Average Return:</strong> {perf_df['change'].mean():.2f}% | 
                       <strong>Market Volatility:</strong> {perf_df['volatility'].mean():.2f}</p>
                </div>
            </div>
            """
            stats_div = Div(text=stats_html, width=1000, height=300)
        else:
            stats_div = Div(text="<p>No performance data available</p>", width=1000, height=50)

        # Create comprehensive footer with analysis insights
        footer_html = f"""
        <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; 
                    padding: 20px; border-radius: 10px; margin: 10px;">
            <h3>🎯 Key Investment Insights</h3>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                <div>
                    <h4>📊 Risk Analysis</h4>
                    <p>• <strong>Avg Portfolio Risk:</strong> {avg_risk:.1f}%</p>
                    <p>• <strong>Risk Range:</strong> {min(risks):.1f}% - {max(risks):.1f}%</p>
                    <p>• <strong>Best Sharpe Ratio:</strong> {max(sharpe_ratios):.2f}</p>
                </div>
                <div>
                    <h4>💰 Return Analysis</h4>
                    <p>• <strong>Avg Expected Return:</strong> {avg_return:.1f}%</p>
                    <p>• <strong>Return Range:</strong> {min(returns):.1f}% - {max(returns):.1f}%</p>
                    <p>• <strong>Stocks Near 52W High:</strong> {sum(1 for pos in week52_positions if pos > 80)}</p>
                </div>
            </div>
            <div style="margin-top: 15px; padding: 10px; background: rgba(255,255,255,0.2); border-radius: 5px;">
                <p><strong>💡 Tips:</strong> Click legend items to hide/show stocks • Use zoom tools for detailed analysis • 
                   Hover over points for comprehensive data • Larger bubbles = Higher market cap</p>
            </div>
        </div>
        """
        footer_div = Div(text=footer_html, width=1000, height=250)

        # Use column layout for comprehensive vertical information display
        layout = column(header_div, p1, stats_div, p2, footer_div)
        
        bokeh_output_file(output_file, title="Comprehensive Stock Analysis Dashboard")
        bokeh_save(layout, resources=CDN)
    
    def _create_risk_return_plot(self, ax) -> None:
        """
        Create risk vs return scatter plot.
        """
        ax.set_title('Risk vs Return Analysis', fontsize=14, fontweight='bold')
        
        if not self.risk_return_data:
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center', 
                   transform=ax.transAxes, fontsize=12)
            return
        
        # Extract data for plotting
        symbols = list(self.risk_return_data.keys())
        risks = [self.risk_return_data[s]['risk_percentage'] for s in symbols]
        returns = [self.risk_return_data[s]['return_percentage'] for s in symbols]
        market_caps = [self.risk_return_data[s]['market_cap_proxy'] for s in symbols]
        week52_positions = [self.risk_return_data[s]['52_week_position'] for s in symbols]
        
        # Normalize bubble sizes
        if market_caps:
            max_cap = max(market_caps)
            min_cap = min(market_caps)
            cap_range = max_cap - min_cap if max_cap > min_cap else 1
            bubble_sizes = [(cap - min_cap) / cap_range * 1000 + 100 for cap in market_caps]
        else:
            bubble_sizes = [200] * len(symbols)
        
        # Create color map based on Sharpe ratio and 52-week position
        sharpe_ratios = [self.risk_return_data[s]['sharpe_ratio'] for s in symbols]
        
        # Primary color: Sharpe ratio (performance)
        sharpe_colors = plt.cm.RdYlGn([max(0, min(1, (sr + 2) / 4)) for sr in sharpe_ratios])
        
        # Secondary indicator: 52-week position (add border color based on position)
        border_colors = ['darkgreen' if pos > 80 else 'orange' if pos > 50 else 'red' for pos in week52_positions]
        
        # Create scatter plot with enhanced styling
        scatter = ax.scatter(risks, returns, s=bubble_sizes, c=sharpe_colors, alpha=0.7, 
                           edgecolors=border_colors, linewidth=2)
        
        # Add stock labels with 52-week position info
        for i, symbol in enumerate(symbols):
            week52_pos = week52_positions[i]
            pos_indicator = "🔥" if week52_pos > 80 else "⚡" if week52_pos > 50 else "❄️"
            
            ax.annotate(f'{symbol} {pos_indicator}', (risks[i], returns[i]), 
                       xytext=(5, 5), textcoords='offset points', 
                       fontsize=10, fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7))
        
        # Add reference lines
        ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5, label='Zero Return')
        ax.axvline(x=0, color='gray', linestyle='--', alpha=0.5)
        
        # Efficient Frontier approximation (simplified)
        if len(risks) > 1:
            risk_range = np.linspace(min(risks), max(risks), 100)
            efficient_returns = [max(returns) * (r / max(risks))**0.5 for r in risk_range]
            ax.plot(risk_range, efficient_returns, 'r--', alpha=0.5, label='Efficient Frontier (approx)')
        
        ax.set_xlabel('Risk (Volatility %)', fontsize=12)
        ax.set_ylabel('Expected Return (%)', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        # Enhanced legend
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='gray', 
                      markersize=8, label='Zero Return', linestyle='--'),
            plt.Line2D([0], [0], color='red', linestyle='--', alpha=0.5, label='Efficient Frontier (approx)'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='lightgreen', 
                      markeredgecolor='darkgreen', markersize=8, linewidth=2, 
                      label='🔥 Near 52W High (>80%)'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='lightyellow', 
                      markeredgecolor='orange', markersize=8, linewidth=2, 
                      label='⚡ Mid-Range (50-80%)'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='lightcoral', 
                      markeredgecolor='red', markersize=8, linewidth=2, 
                      label='❄️ Near 52W Low (<50%)')
        ]
        ax.legend(handles=legend_elements, loc='upper left')
        
        # Add colorbar for Sharpe ratio
        cbar = plt.colorbar(scatter, ax=ax, fraction=0.046, pad=0.04)
        cbar.set_label('Sharpe Ratio\n(Fill Color)', rotation=270, labelpad=20)
    
    def _create_price_trend_plot(self, ax) -> None:
        """
        Create 30-day price trend plot.
        """
        ax.set_title('30-Day Price Trends (Normalized)', fontsize=14, fontweight='bold')
        
        if not self.price_trend_data:
            ax.text(0.5, 0.5, 'No price data available', ha='center', va='center', 
                   transform=ax.transAxes, fontsize=12)
            return
        
        # Plot normalized price trends
        colors = plt.cm.tab10(np.linspace(0, 1, len(self.price_trend_data)))
        
        for i, (symbol, data) in enumerate(self.price_trend_data.items()):
            try:
                prices = data['Close'].dropna()
                if len(prices) > 5:  # Need minimum data points
                    # Normalize prices to start at 100
                    normalized_prices = (prices / prices.iloc[0]) * 100
                    
                    ax.plot(normalized_prices.index, normalized_prices.values, 
                           color=colors[i], linewidth=2, label=symbol, marker='o', markersize=3)
                    
                    # Add current value annotation
                    current_change = ((prices.iloc[-1] / prices.iloc[0]) - 1) * 100
                    ax.annotate(f'{symbol}: {current_change:+.1f}%', 
                              xy=(normalized_prices.index[-1], normalized_prices.iloc[-1]),
                              xytext=(10, 0), textcoords='offset points',
                              fontsize=9, fontweight='bold',
                              bbox=dict(boxstyle='round,pad=0.3', facecolor=colors[i], alpha=0.7))
            except Exception as e:
                print(f"{EMOJIS['warning']} Error plotting {symbol}: {e}")
        
        # Add reference line at 100 (starting point)
        ax.axhline(y=100, color='gray', linestyle='--', alpha=0.5, label='Starting Point (100)')
        
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Normalized Price (Starting Point = 100)', fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # Format x-axis dates
        ax.tick_params(axis='x', rotation=45)
    
    def print_summary_statistics(self) -> None:
        """
        Print summary statistics with 52-week high/low information.
        """
        print(f"\n{EMOJIS['money']} SUMMARY STATISTICS WITH 52-WEEK DATA")
        print("=" * 100)
        
        if not self.risk_return_data:
            print("No data available for analysis")
            return
        
        # Create summary DataFrame with 52-week data
        summary_data = []
        for symbol, metrics in self.risk_return_data.items():
            week52_indicator = "🔥" if metrics['52_week_position'] > 80 else "⚡" if metrics['52_week_position'] > 50 else "❄️"
            
            summary_data.append({
                'Symbol': symbol,
                'Current Price': f"${metrics['current_price']:.2f}",
                '52W High': f"${metrics['52_week_high']:.2f}",
                '52W Low': f"${metrics['52_week_low']:.2f}",
                '52W Position': f"{metrics['52_week_position']:.1f}% {week52_indicator}",
                'Expected Return': f"{metrics['return_percentage']:.1f}%",
                'Risk (Volatility)': f"{metrics['risk_percentage']:.1f}%",
                'Sharpe Ratio': f"{metrics['sharpe_ratio']:.2f}"
            })
        
        df = pd.DataFrame(summary_data)
        
        # Improved formatting with better alignment
        print(df.to_string(index=False, justify='center', col_space=15, max_colwidth=20))
        
        # Best performers with 52-week analysis
        if len(self.risk_return_data) > 1:
            best_return = max(self.risk_return_data.items(), key=lambda x: x[1]['expected_return'])
            best_sharpe = max(self.risk_return_data.items(), key=lambda x: x[1]['sharpe_ratio'])
            lowest_risk = min(self.risk_return_data.items(), key=lambda x: x[1]['volatility'])
            
            # 52-week specific insights
            near_high = [s for s, m in self.risk_return_data.items() if m['52_week_position'] > 80]
            near_low = [s for s, m in self.risk_return_data.items() if m['52_week_position'] < 20]
            
            print(f"\n{EMOJIS['target']} KEY INSIGHTS:")
            print(f"🏆 Best Expected Return: {best_return[0]} ({best_return[1]['return_percentage']:.1f}%)")
            print(f"📊 Best Sharpe Ratio: {best_sharpe[0]} ({best_sharpe[1]['sharpe_ratio']:.2f})")
            print(f"🛡️ Lowest Risk: {lowest_risk[0]} ({lowest_risk[1]['risk_percentage']:.1f}%)")
            
            print(f"\n{EMOJIS['fire']} 52-WEEK ANALYSIS:")
            if near_high:
                print(f"🔥 Near 52W High (>80%): {', '.join(near_high)}")
            if near_low:
                print(f"❄️ Near 52W Low (<20%): {', '.join(near_low)}")
            
            # Price range analysis
            max_range_stock = max(self.risk_return_data.items(), 
                                key=lambda x: (x[1]['52_week_high'] - x[1]['52_week_low']) / x[1]['52_week_low'])
            price_range_pct = ((max_range_stock[1]['52_week_high'] - max_range_stock[1]['52_week_low']) / max_range_stock[1]['52_week_low']) * 100
            print(f"📏 Widest 52W Range: {max_range_stock[0]} ({price_range_pct:.1f}% range)")
            
            print(f"\n💡 LEGEND: 🔥 = Near High | ⚡ = Mid-Range | ❄️ = Near Low")
    
    def export_to_excel(self, output_file: str) -> None:
        """
        Export analysis results to Excel file with multiple sheets.
        """
        try:
            # Create Excel filename from the output file
            excel_filename = output_file.replace('.png', '_analysis.xlsx').replace('.html', '_analysis.xlsx')
            if not excel_filename.endswith('.xlsx'):
                excel_filename = 'stock_analysis_results.xlsx'
            
            print(f"\n{EMOJIS['chart']} Exporting analysis to Excel: {excel_filename}")
            
            with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
                # Main analysis results
                if hasattr(self, 'analysis_results') and not self.analysis_results.empty:
                    # Prepare comprehensive analysis data
                    export_data = []
                    
                    for _, row in self.analysis_results.iterrows():
                        symbol = row['symbol']
                        
                        # Get additional data if available
                        current_price = self.stock_data.get(symbol, {}).get('current_price', 'N/A')
                        week_52_high = self.stock_data.get(symbol, {}).get('52_week_high', 'N/A')
                        week_52_low = self.stock_data.get(symbol, {}).get('52_week_low', 'N/A')
                        week_52_position = self.stock_data.get(symbol, {}).get('52_week_position', 'N/A')
                        
                        # Format position indicator
                        if isinstance(week_52_position, (int, float)):
                            if week_52_position >= 80:
                                position_indicator = "🔥 Near High"
                            elif week_52_position <= 20:
                                position_indicator = "❄️ Near Low"
                            else:
                                position_indicator = "⚡ Mid-Range"
                        else:
                            position_indicator = "N/A"
                        
                        export_data.append({
                            'Symbol': symbol,
                            'Current Price': current_price,
                            '52 Week High': week_52_high,
                            '52 Week Low': week_52_low,
                            '52W Position %': week_52_position,
                            'Position Indicator': position_indicator,
                            'Expected Return (%)': round(row['expected_return'] * 100, 2) if pd.notna(row['expected_return']) else 'N/A',
                            'Risk/Volatility (%)': round(row['volatility'] * 100, 2) if pd.notna(row['volatility']) else 'N/A',
                            'Sharpe Ratio': round(row['sharpe_ratio'], 3) if pd.notna(row['sharpe_ratio']) else 'N/A',
                            'Market Cap Proxy': round(row['market_cap_proxy'], 2) if pd.notna(row['market_cap_proxy']) else 'N/A',
                            'Analysis Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        })
                    
                    analysis_df = pd.DataFrame(export_data)
                    analysis_df.to_excel(writer, sheet_name='Stock Analysis', index=False)
                    
                    # Summary statistics sheet
                    summary_stats = {
                        'Metric': [
                            'Total Stocks Analyzed',
                            'Best Expected Return (%)',
                            'Best Sharpe Ratio',
                            'Lowest Risk/Volatility (%)',
                            'Stocks Near 52W High (>80%)',
                            'Stocks Near 52W Low (<20%)',
                            'Analysis Period',
                            'Price Trend Period',
                            'Generated Date'
                        ],
                        'Value': [
                            len(self.analysis_results),
                            f"{self.analysis_results['expected_return'].max() * 100:.1f}%" if not self.analysis_results.empty else 'N/A',
                            f"{self.analysis_results['sharpe_ratio'].max():.2f}" if not self.analysis_results.empty else 'N/A',
                            f"{self.analysis_results['volatility'].min() * 100:.1f}%" if not self.analysis_results.empty else 'N/A',
                            len([s for s in self.stock_data.values() if isinstance(s.get('52_week_position'), (int, float)) and s.get('52_week_position', 0) >= 80]),
                            len([s for s in self.stock_data.values() if isinstance(s.get('52_week_position'), (int, float)) and s.get('52_week_position', 100) <= 20]),
                            self.period,
                            self.price_period,
                            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        ]
                    }
                    
                    summary_df = pd.DataFrame(summary_stats)
                    summary_df.to_excel(writer, sheet_name='Summary Statistics', index=False)
                    
                    # Top performers sheet
                    if not self.analysis_results.empty:
                        top_return = self.analysis_results.nlargest(10, 'expected_return')[['symbol', 'expected_return', 'sharpe_ratio', 'volatility']].copy()
                        top_return['expected_return'] = (top_return['expected_return'] * 100).round(2)
                        top_return['volatility'] = (top_return['volatility'] * 100).round(2)
                        top_return['sharpe_ratio'] = top_return['sharpe_ratio'].round(3)
                        top_return.columns = ['Symbol', 'Expected Return (%)', 'Sharpe Ratio', 'Risk/Volatility (%)']
                        top_return.to_excel(writer, sheet_name='Top Performers', index=False)
                        
                        # Low risk stocks sheet
                        low_risk = self.analysis_results.nsmallest(10, 'volatility')[['symbol', 'expected_return', 'sharpe_ratio', 'volatility']].copy()
                        low_risk['expected_return'] = (low_risk['expected_return'] * 100).round(2)
                        low_risk['volatility'] = (low_risk['volatility'] * 100).round(2)
                        low_risk['sharpe_ratio'] = low_risk['sharpe_ratio'].round(3)
                        low_risk.columns = ['Symbol', 'Expected Return (%)', 'Sharpe Ratio', 'Risk/Volatility (%)']
                        low_risk.to_excel(writer, sheet_name='Low Risk Stocks', index=False)
                
                # Source data sheet (from the original input)
                if hasattr(self, 'source_data') and not self.source_data.empty:
                    self.source_data.to_excel(writer, sheet_name='Source Data', index=False)
                
            print(f"{EMOJIS['check']} Excel export complete: {excel_filename}")
            
        except Exception as e:
            print(f"{EMOJIS['warning']} Error exporting to Excel: {e}")
    
    def analyze(self, output_file: str = 'stock_analysis.png') -> bool:
        """
        Run complete analysis.
        Returns True if successful, False otherwise.
        """
        try:
            # Load symbols
            if not self.load_stock_symbols():
                return False
            
            if not self.stock_symbols:
                print(f"{EMOJIS['warning']} No stock symbols found in Excel file")
                return False
            
            # Fetch data
            if not self.fetch_market_data():
                return False
            
            # Calculate metrics
            self.calculate_risk_return_metrics()
            
            # Create visualizations
            if not self.create_visualizations(output_file):
                return False
            
            # Print summary
            self.print_summary_statistics()
            
            # Export to Excel
            self.export_to_excel(output_file)
            
            print(f"\n{EMOJIS['check']} Analysis complete! Output saved as {output_file}")
            return True
            
        except Exception as e:
            print(f"{EMOJIS['warning']} Error in analysis: {e}")
            return False

def create_sample_excel_file(filename: str = 'sample_stocks.xlsx') -> None:
    """
    Create a comprehensive sample Excel file with detailed stock information.
    """
    print(f"\n{EMOJIS['rocket']} Creating comprehensive sample Excel file...")
    
    # Diverse portfolio across sectors with detailed information
    sample_data = [
        # Technology Giants
        {'Symbol': 'AAPL', 'Company': 'Apple Inc.', 'Sector': 'Technology', 'Industry': 'Consumer Electronics', 
         'Market_Cap': 'Large Cap', 'Description': 'Leading technology company known for iPhone, iPad, Mac computers and services',
         'Country': 'USA', 'Exchange': 'NASDAQ', 'Currency': 'USD', 'Risk_Level': 'Medium', 'Dividend': 'Yes'},
        
        {'Symbol': 'GOOGL', 'Company': 'Alphabet Inc.', 'Sector': 'Technology', 'Industry': 'Internet Services', 
         'Market_Cap': 'Large Cap', 'Description': 'Parent company of Google, leader in search, advertising, and cloud services',
         'Country': 'USA', 'Exchange': 'NASDAQ', 'Currency': 'USD', 'Risk_Level': 'Medium', 'Dividend': 'No'},
        
        {'Symbol': 'MSFT', 'Company': 'Microsoft Corporation', 'Sector': 'Technology', 'Industry': 'Software', 
         'Market_Cap': 'Large Cap', 'Description': 'Leading software company with Windows, Office, Azure cloud services',
         'Country': 'USA', 'Exchange': 'NASDAQ', 'Currency': 'USD', 'Risk_Level': 'Low', 'Dividend': 'Yes'},
        
        {'Symbol': 'NVDA', 'Company': 'NVIDIA Corporation', 'Sector': 'Technology', 'Industry': 'Semiconductors', 
         'Market_Cap': 'Large Cap', 'Description': 'Leading AI and graphics processing unit (GPU) manufacturer',
         'Country': 'USA', 'Exchange': 'NASDAQ', 'Currency': 'USD', 'Risk_Level': 'High', 'Dividend': 'Yes'},
        
        # E-commerce & Consumer
        {'Symbol': 'AMZN', 'Company': 'Amazon.com Inc.', 'Sector': 'Consumer Discretionary', 'Industry': 'E-commerce', 
         'Market_Cap': 'Large Cap', 'Description': 'Leading e-commerce platform and cloud computing provider (AWS)',
         'Country': 'USA', 'Exchange': 'NASDAQ', 'Currency': 'USD', 'Risk_Level': 'Medium', 'Dividend': 'No'},
        
        {'Symbol': 'SHOP', 'Company': 'Shopify Inc.', 'Sector': 'Technology', 'Industry': 'E-commerce Software', 
         'Market_Cap': 'Mid Cap', 'Description': 'E-commerce platform enabling businesses to create online stores',
         'Country': 'Canada', 'Exchange': 'NYSE', 'Currency': 'USD', 'Risk_Level': 'High', 'Dividend': 'No'},
        
        # Automotive & Transportation
        {'Symbol': 'TSLA', 'Company': 'Tesla Inc.', 'Sector': 'Consumer Discretionary', 'Industry': 'Electric Vehicles', 
         'Market_Cap': 'Large Cap', 'Description': 'Leading electric vehicle manufacturer and clean energy company',
         'Country': 'USA', 'Exchange': 'NASDAQ', 'Currency': 'USD', 'Risk_Level': 'Very High', 'Dividend': 'No'},
        
        {'Symbol': 'UBER', 'Company': 'Uber Technologies Inc.', 'Sector': 'Technology', 'Industry': 'Transportation', 
         'Market_Cap': 'Mid Cap', 'Description': 'Ride-sharing and food delivery platform',
         'Country': 'USA', 'Exchange': 'NYSE', 'Currency': 'USD', 'Risk_Level': 'High', 'Dividend': 'No'},
        
        # Social Media & Communication
        {'Symbol': 'META', 'Company': 'Meta Platforms Inc.', 'Sector': 'Communication Services', 'Industry': 'Social Media', 
         'Market_Cap': 'Large Cap', 'Description': 'Owner of Facebook, Instagram, WhatsApp, and metaverse technologies',
         'Country': 'USA', 'Exchange': 'NASDAQ', 'Currency': 'USD', 'Risk_Level': 'High', 'Dividend': 'Yes'},
        
        {'Symbol': 'SPOT', 'Company': 'Spotify Technology S.A.', 'Sector': 'Communication Services', 'Industry': 'Music Streaming', 
         'Market_Cap': 'Mid Cap', 'Description': 'Leading music streaming and podcast platform',
         'Country': 'Sweden', 'Exchange': 'NYSE', 'Currency': 'USD', 'Risk_Level': 'High', 'Dividend': 'No'},
        
        # Entertainment
        {'Symbol': 'NFLX', 'Company': 'Netflix Inc.', 'Sector': 'Communication Services', 'Industry': 'Streaming', 
         'Market_Cap': 'Large Cap', 'Description': 'Leading streaming entertainment service with global reach',
         'Country': 'USA', 'Exchange': 'NASDAQ', 'Currency': 'USD', 'Risk_Level': 'Medium', 'Dividend': 'No'},
        
        # Enterprise Software
        {'Symbol': 'CRM', 'Company': 'Salesforce Inc.', 'Sector': 'Technology', 'Industry': 'Enterprise Software', 
         'Market_Cap': 'Large Cap', 'Description': 'Leading customer relationship management (CRM) software provider',
         'Country': 'USA', 'Exchange': 'NYSE', 'Currency': 'USD', 'Risk_Level': 'Medium', 'Dividend': 'No'},
        
        {'Symbol': 'NOW', 'Company': 'ServiceNow Inc.', 'Sector': 'Technology', 'Industry': 'Enterprise Software', 
         'Market_Cap': 'Large Cap', 'Description': 'Cloud-based platform for digital workflow automation',
         'Country': 'USA', 'Exchange': 'NYSE', 'Currency': 'USD', 'Risk_Level': 'Medium', 'Dividend': 'No'},
        
        {'Symbol': 'ORCL', 'Company': 'Oracle Corporation', 'Sector': 'Technology', 'Industry': 'Database Software', 
         'Market_Cap': 'Large Cap', 'Description': 'Enterprise software company specializing in database management',
         'Country': 'USA', 'Exchange': 'NYSE', 'Currency': 'USD', 'Risk_Level': 'Low', 'Dividend': 'Yes'},
        
        # Creative Software
        {'Symbol': 'ADBE', 'Company': 'Adobe Inc.', 'Sector': 'Technology', 'Industry': 'Creative Software', 
         'Market_Cap': 'Large Cap', 'Description': 'Creative software suite including Photoshop, Illustrator, and PDF',
         'Country': 'USA', 'Exchange': 'NASDAQ', 'Currency': 'USD', 'Risk_Level': 'Medium', 'Dividend': 'No'},
        
        # Communication & Collaboration
        {'Symbol': 'ZM', 'Company': 'Zoom Video Communications', 'Sector': 'Technology', 'Industry': 'Video Conferencing', 
         'Market_Cap': 'Mid Cap', 'Description': 'Video conferencing and communication platform',
         'Country': 'USA', 'Exchange': 'NASDAQ', 'Currency': 'USD', 'Risk_Level': 'High', 'Dividend': 'No'},
    ]
    
    # Create the main stocks DataFrame
    df_stocks = pd.DataFrame(sample_data)
    
    # Create portfolio suggestions by risk level
    conservative_stocks = df_stocks[df_stocks['Risk_Level'] == 'Low'][['Symbol', 'Company', 'Sector', 'Description']]
    moderate_stocks = df_stocks[df_stocks['Risk_Level'] == 'Medium'][['Symbol', 'Company', 'Sector', 'Description']]
    aggressive_stocks = df_stocks[df_stocks['Risk_Level'].isin(['High', 'Very High'])][['Symbol', 'Company', 'Sector', 'Description']]
    
    # Create sector analysis
    sector_summary = df_stocks.groupby('Sector').agg({
        'Symbol': 'count',
        'Company': lambda x: ', '.join(x.str.split().str[0])  # First word of company names
    }).rename(columns={'Symbol': 'Stock_Count', 'Company': 'Companies'})
    sector_summary.reset_index(inplace=True)
    
    # Create Excel file with multiple informative sheets
    excel_file = filename
    csv_file = filename.replace('.xlsx', '.csv').replace('.xls', '.csv')
    
    try:
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            # Sheet 1: All Stocks (main data)
            df_stocks.to_excel(writer, sheet_name='All_Stocks', index=False)
            
            # Sheet 2: Conservative Portfolio
            conservative_stocks.to_excel(writer, sheet_name='Conservative_Portfolio', index=False)
            
            # Sheet 3: Moderate Portfolio  
            moderate_stocks.to_excel(writer, sheet_name='Moderate_Portfolio', index=False)
            
            # Sheet 4: Aggressive Portfolio
            aggressive_stocks.to_excel(writer, sheet_name='Aggressive_Portfolio', index=False)
            
            # Sheet 5: Sector Analysis
            sector_summary.to_excel(writer, sheet_name='Sector_Analysis', index=False)
            
            # Sheet 6: Instructions and Usage Guide
            instructions_data = [
                ['How to Use This File', ''],
                ['', ''],
                ['1. BASIC ANALYSIS', 'Use the "All_Stocks" sheet for comprehensive analysis'],
                ['Command Example', 'python stock_analyzer.py sample_stocks.xlsx'],
                ['', ''],
                ['2. PORTFOLIO-BASED ANALYSIS', 'Use specific portfolio sheets based on risk tolerance'],
                ['Conservative (Low Risk)', 'python stock_analyzer.py sample_stocks.xlsx --sheet Conservative_Portfolio'],
                ['Moderate (Medium Risk)', 'python stock_analyzer.py sample_stocks.xlsx --sheet Moderate_Portfolio'],
                ['Aggressive (High Risk)', 'python stock_analyzer.py sample_stocks.xlsx --sheet Aggressive_Portfolio'],
                ['', ''],
                ['3. TIME PERIOD OPTIONS', 'Adjust analysis periods for different insights'],
                ['Short-term Analysis', 'python stock_analyzer.py sample_stocks.xlsx --period 6mo --price-period 1mo'],
                ['Long-term Analysis', 'python stock_analyzer.py sample_stocks.xlsx --period 5y --price-period 1y'],
                ['', ''],
                ['4. COLUMN DESCRIPTIONS', ''],
                ['Symbol', 'Stock ticker symbol for trading'],
                ['Company', 'Full company name'],
                ['Sector', 'Business sector classification'],
                ['Industry', 'Specific industry within sector'],
                ['Market_Cap', 'Market capitalization category'],
                ['Description', 'Brief business description'],
                ['Country', 'Country of incorporation'],
                ['Exchange', 'Stock exchange where traded'],
                ['Currency', 'Trading currency'],
                ['Risk_Level', 'Investment risk assessment'],
                ['Dividend', 'Whether company pays dividends'],
                ['', ''],
                ['5. RISK LEVEL GUIDE', ''],
                ['Low Risk', 'Stable, established companies with consistent performance'],
                ['Medium Risk', 'Growing companies with moderate volatility'],
                ['High Risk', 'Fast-growing companies with higher volatility'],
                ['Very High Risk', 'Emerging or disruptive companies with significant volatility'],
                ['', ''],
                ['6. DIVERSIFICATION TIPS', ''],
                ['Sector Diversification', 'Choose stocks from different sectors'],
                ['Geographic Diversification', 'Include international stocks'],
                ['Risk Diversification', 'Mix different risk levels'],
                ['Market Cap Diversification', 'Include large, mid, and small cap stocks'],
            ]
            
            instructions_df = pd.DataFrame(instructions_data, columns=['Category', 'Description'])
            instructions_df.to_excel(writer, sheet_name='Instructions', index=False)
        
        print(f"{EMOJIS['check']} Comprehensive Excel file created: {excel_file}")
        print(f"   📊 Sheets created: All_Stocks, Conservative_Portfolio, Moderate_Portfolio, Aggressive_Portfolio, Sector_Analysis, Instructions")
        
    except Exception as e:
        print(f"{EMOJIS['warning']} Could not create Excel file: {e}")
    
    # Also create a simple CSV version
    try:
        df_stocks.to_csv(csv_file, index=False)
        print(f"{EMOJIS['check']} CSV file created: {csv_file}")
    except Exception as e:
        print(f"{EMOJIS['warning']} Could not create CSV file: {e}")
    
    print(f"\n{EMOJIS['computer']} Sample files contain {len(sample_data)} carefully selected stocks")
    print(f"{EMOJIS['target']} Portfolio breakdown:")
    print(f"   🛡️ Conservative (Low Risk): {len(conservative_stocks)} stocks")
    print(f"   ⚖️ Moderate (Medium Risk): {len(moderate_stocks)} stocks") 
    print(f"   🚀 Aggressive (High Risk): {len(aggressive_stocks)} stocks")
    print(f"\n{EMOJIS['fire']} Sector diversification:")
    for _, row in sector_summary.iterrows():
        print(f"   📈 {row['Sector']}: {row['Stock_Count']} stocks")
    print(f"\n💡 Tip: Open the Excel file to see all sheets and detailed instructions!")

def main():
    """
    Main function with command line interface.
    """
    parser = argparse.ArgumentParser(
        description='Stock Risk vs Return Analysis Tool - Generate professional stock analysis charts',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python stock_analyzer.py stocks.xlsx                      # Analyze stocks (generates PNG + HTML)
  python stock_analyzer.py stocks.csv                       # Analyze stocks from CSV (generates PNG + HTML)
  python stock_analyzer.py stocks.xlsx --output analysis.png # Custom output filename (generates both formats)
  python stock_analyzer.py --create-sample                  # Create sample files
  python stock_analyzer.py stocks.xlsx --period 2y          # Use 2-year historical data
  python stock_analyzer.py stocks.xlsx --price-period 60d   # Show 60-day price trends
  python stock_analyzer.py stocks.xlsx --sheet Conservative_Portfolio  # Analyze specific sheet
  python stock_analyzer.py stocks.xlsx --sheet Aggressive_Portfolio --period 1y  # Portfolio-specific analysis

File Format:
  Excel/CSV files should contain a column with stock symbols (ticker codes).
  Common column names: Symbol, Symbols, Stock, Stocks, Ticker, Tickers
  
  Example:
  Symbol  | Company
  --------|--------
  AAPL    | Apple
  GOOGL   | Google
  MSFT    | Microsoft

Output:
  Creates professional side-by-side charts in BOTH formats:
  • PNG: High-quality static image for presentations/reports
  • HTML: Interactive version with zoom/reset tools for detailed analysis
  
  Charts include:
  1. Risk vs Return scatter plot with:
     - Bubble sizes representing market cap proxy
     - Fill colors showing Sharpe ratio (green=excellent, red=poor)
     - Border colors indicating 52-week position (green=near high, red=near low)
     - Emojis showing position: 🔥=near 52W high, ⚡=mid-range, ❄️=near 52W low
  2. 30-day normalized price trend comparison
  
  Plus comprehensive statistics table with 52-week high/low analysis.
        """
    )
    
    parser.add_argument('file', nargs='?', help='Excel (.xlsx, .xls) or CSV (.csv) file containing stock symbols')
    parser.add_argument('--output', '-o', default='stock_analysis.png', 
                       help='Output file name (generates both PNG and HTML versions, default: stock_analysis.png)')
    parser.add_argument('--period', default='1y', 
                       help='Period for risk/return analysis: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max (default: 1y)')
    parser.add_argument('--price-period', default='30d',
                       help='Period for price trends: 1d, 5d, 1mo, 3mo, 6mo, 1y (default: 30d)')
    parser.add_argument('--sheet', '-s', default=None,
                       help='Excel sheet name to read (default: "All_Stocks" if available, otherwise first sheet)')
    parser.add_argument('--create-sample', action='store_true',
                       help='Create sample Excel and CSV files with popular tech stocks')
    
    args = parser.parse_args()
    
    # Create sample file if requested
    if args.create_sample:
        create_sample_excel_file()
        return 0
    
    # Validate input
    if not args.file:
        print(f"{EMOJIS['warning']} Error: Input file is required")
        print("Use --help for usage information or --create-sample to create sample files")
        return 1
    
    if not os.path.exists(args.file):
        print(f"{EMOJIS['warning']} Error: File '{args.file}' not found")
        print("Use --create-sample to create sample files")
        return 1
    
    try:
        # Run analysis
        analyzer = StockAnalyzer(
            excel_file=args.file,
            period=args.period,
            price_period=args.price_period,
            sheet_name=args.sheet
        )
        
        success = analyzer.analyze(args.output)
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print(f"\n{EMOJIS['warning']} Analysis interrupted by user")
        return 1
    except Exception as e:
        print(f"{EMOJIS['warning']} Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
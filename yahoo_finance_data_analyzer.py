#!/usr/bin/env python3
"""
Yahoo Finance L# Terminal colors and formatting
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    BLINK = '\033[5m'
    DIM = '\033[2m'
    END = '\033[0m'lyzer & Recommendation Engine
========================================================

Real-time stock analysis and recommendation system that:
- Fetches live data from 6 Yahoo Finance categories
- Applies Stock Risk Analysis Tool calculations
- Displays continuous live recommendations in terminal
- Shows top 50 tickers with buying recommendations
- Includes current price, 52-week range, risk metrics
- Animated terminal display with emojis and colors
- Option to save analysis data to Excel

Categories analyzed:
- Most Active, Trending Now, Top Gainers, Top Losers
- 52 Week Gainers, 52 Week Losers

Author: Investment Management System
Date: September 2025
"""

import os
import sys
import time
import re
import argparse
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import yfinance as yf
from pathlib import Path
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import json
import time

# Import existing modules
try:
    from yahoo_finance_downloader import YahooFinanceDownloader
    from stock_analyzer import StockAnalyzer
except ImportError as e:
    print(f"❌ Error importing required modules: {e}")
    print("💡 Make sure yahoo_finance_downloader.py and stock_analyzer.py are available")
    sys.exit(1)

# Terminal colors and formatting
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    BLINK = '\033[5m'

# Emojis for recommendations
RECOMMENDATION_EMOJIS = {
    'STRONG_BUY': '🚀',
    'BUY': '💰',
    'HOLD': '⚖️',
    'AVOID': '⚠️',
    'STRONG_AVOID': '🛑'
}

RISK_EMOJIS = {
    'LOW': '🟢',
    'MEDIUM': '🟡',
    'HIGH': '🔴'
}

POSITION_EMOJIS = {
    'NEAR_HIGH': '🔥',
    'MID_RANGE': '⚡',
    'NEAR_LOW': '❄️'
}

class YahooFinanceLiveAnalyzer:
    """
    Live Yahoo Finance data analyzer with continuous recommendations
    """
    
    def __init__(self, update_interval: int = 300, save_data: bool = False, output_dir: str = "live_analysis"):
        """
        Initialize the live analyzer
        
        Args:
            update_interval: Seconds between updates (default: 5 minutes)
            save_data: Whether to save analysis data to Excel
            output_dir: Directory for saved data
        """
        self.update_interval = update_interval
        self.save_data = save_data
        self.output_dir = Path(output_dir)
        self.cache_file = self.output_dir / "symbols_cache.json" if save_data else Path("symbols_cache.json")
        if save_data:
            self.output_dir.mkdir(exist_ok=True)
        
        # Initialize components
        self.downloader = YahooFinanceDownloader("temp_data")
        self.analyzer = None
        self.current_data = {}
        self.recommendations = []
        
        print(f"{Colors.BOLD}{Colors.CYAN}🚀 Yahoo Finance Live Analyzer Initialized{Colors.END}")
        print(f"{Colors.GREEN}⏰ Update interval: {update_interval} seconds{Colors.END}")
        if save_data:
            print(f"{Colors.BLUE}💾 Data saving enabled: {output_dir}{Colors.END}")
        print()

    def fetch_live_data(self) -> Dict[str, pd.DataFrame]:
        """
        Fetch live data from all Yahoo Finance categories with improved error handling
        
        Returns:
            Dictionary with category data
        """
        print(f"{Colors.YELLOW}📡 Fetching live data from Yahoo Finance...{Colors.END}")
        
        try:
            # Get data from all categories with timeout protection
            categories_data = {}
            
            # Configure session with shorter timeouts for faster processing
            if hasattr(self.downloader, 'session'):
                self.downloader.session.timeout = 8  # 8 second timeout
            
            # Fetch each category with improved error handling
            categories = {
                'most_active': self.downloader.get_most_active_stocks,
                'trending': self.downloader.get_trending_stocks,
                'top_gainers': self.downloader.get_top_gainers,
                'top_losers': self.downloader.get_top_losers,
                '52_week_gainers': self.downloader.get_52_week_gainers,
                '52_week_losers': self.downloader.get_52_week_losers
            }
            
            for category_name, fetch_func in categories.items():
                try:
                    print(f"   🔄 Fetching {category_name.replace('_', ' ').title()}...")
                    data = fetch_func(limit=40)  # Reduced limit for faster processing
                    
                    if data is not None and not data.empty:
                        categories_data[category_name] = data
                        print(f"   ✅ {category_name.replace('_', ' ').title()}: {len(data)} stocks")
                    else:
                        print(f"   ⚠️ {category_name.replace('_', ' ').title()}: No data available")
                        
                except requests.exceptions.Timeout:
                    print(f"   ⏰ {category_name.replace('_', ' ').title()}: Timeout, skipping")
                    continue
                    
                except requests.exceptions.SSLError as ssl_e:
                    print(f"   🔒 {category_name.replace('_', ' ').title()}: SSL error, skipping")
                    continue
                    
                except requests.exceptions.ConnectionError:
                    print(f"   🌐 {category_name.replace('_', ' ').title()}: Connection error, skipping")
                    continue
                    
                except Exception as e:
                    error_msg = str(e)[:40] + '...' if len(str(e)) > 40 else str(e)
                    print(f"   ❌ {category_name.replace('_', ' ').title()}: {error_msg}")
                    continue
            
            print(f"{Colors.GREEN}✅ Successfully fetched {len(categories_data)} categories{Colors.END}")
            return categories_data
            
        except Exception as e:
            print(f"{Colors.RED}❌ Error fetching data: {e}{Colors.END}")
            return {}

    def combine_and_deduplicate_data(self, categories_data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Combine all category data and remove duplicates
        
        Args:
            categories_data: Dictionary of category DataFrames
            
        Returns:
            Combined DataFrame with unique stocks
        """
        if not categories_data:
            return pd.DataFrame()
        
        # Combine all dataframes
        all_data = []
        for category, df in categories_data.items():
            if not df.empty:
                df_copy = df.copy()
                df_copy['Source_Category'] = category.replace('_', ' ').title()
                all_data.append(df_copy)
        
        if not all_data:
            return pd.DataFrame()
        
        # Concatenate all data
        combined_df = pd.concat(all_data, ignore_index=True)
        
        # Remove duplicates based on Symbol, keeping first occurrence
        unique_df = combined_df.drop_duplicates(subset=['Symbol'], keep='first')
        
        print(f"{Colors.GREEN}📊 Combined data: {len(combined_df)} total, {len(unique_df)} unique stocks{Colors.END}")
        
        return unique_df

    def analyze_stocks_with_risk_tool(self, combined_data: pd.DataFrame) -> pd.DataFrame:
        """
        Analyze combined stock data using the existing Stock Risk Analysis Tool
        
        Args:
            combined_data: Combined stock data
            
        Returns:
            DataFrame with analysis results and recommendations
        """
        if combined_data.empty:
            return pd.DataFrame()
        
        print(f"{Colors.YELLOW}🧮 Analyzing stocks with Risk Analysis Tool...{Colors.END}")
        
        try:
            # Create a temporary CSV file for the analyzer
            temp_file = "temp_analysis_data.csv"
            combined_data[['Symbol']].to_csv(temp_file, index=False)
            
            # Initialize the Stock Analyzer
            analyzer = StockAnalyzer(temp_file, period='1y', price_period='30d')
            
            # Load symbols and fetch market data
            if not analyzer.load_stock_symbols():
                return pd.DataFrame()
            
            if not analyzer.fetch_market_data():
                return pd.DataFrame()
            
            # Calculate risk/return metrics
            analyzer.calculate_risk_return_metrics()
            
            # Get the analysis results
            if hasattr(analyzer, 'analysis_results') and not analyzer.analysis_results.empty:
                analysis_df = analyzer.analysis_results.copy()
                
                # Merge with original data to get current prices and company names
                merged_df = analysis_df.merge(
                    combined_data[['Symbol', 'Company Name', 'Current Price', 'Volume (M)', 
                                 'Market Cap (B)', 'Sector', 'Source_Category']].drop_duplicates(subset=['Symbol']),
                    left_on='symbol', 
                    right_on='Symbol', 
                    how='left'
                )
                
                # Clean up temporary file
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                
                return merged_df
            
        except Exception as e:
            print(f"{Colors.RED}❌ Error in stock analysis: {e}{Colors.END}")
            # Clean up temporary file
            if os.path.exists("temp_analysis_data.csv"):
                os.remove("temp_analysis_data.csv")
        
        return pd.DataFrame()

    def generate_recommendations(self, analysis_df: pd.DataFrame) -> List[Dict]:
        """
        Generate buying recommendations based on analysis
        
        Args:
            analysis_df: Analysis results DataFrame
            
        Returns:
            List of recommendation dictionaries
        """
        if analysis_df.empty:
            return []
        
        recommendations = []
        
        for _, row in analysis_df.iterrows():
            try:
                symbol = row['symbol']
                expected_return = row.get('expected_return', 0) * 100  # Convert to percentage
                volatility = row.get('volatility', 0) * 100  # Convert to percentage
                sharpe_ratio = row.get('sharpe_ratio', 0)
                current_price = row.get('Current Price', 0)
                range_position = row.get('52_week_position', 50)  # Percentage in 52-week range
                company_name = row.get('Company Name', symbol)
                sector = row.get('Sector', 'N/A')
                source_category = row.get('Source_Category', 'Unknown')
                
                # Generate recommendation based on multiple factors
                recommendation = self.calculate_recommendation(
                    expected_return, volatility, sharpe_ratio, range_position
                )
                
                # Determine risk level
                risk_level = self.calculate_risk_level(volatility)
                
                # Determine position indicator
                position_indicator = self.get_position_indicator(range_position)
                
                # Fetch additional market data and news with improved error handling
                try:
                    ticker = yf.Ticker(symbol)
                    
                    # Set session with timeout
                    session = requests.Session()
                    session.timeout = 5  # 5 second timeout
                    ticker.session = session
                    
                    info = ticker.info
                    
                    # Fix change percentage calculation with validation
                    current_price_val = float(current_price) if current_price else 0
                    
                    # Method 1: Try to get proper change percentage
                    raw_change_pct = info.get('regularMarketChangePercent', 0)
                    if raw_change_pct:
                        change_percent = raw_change_pct * 100
                        # Validate daily change (should be reasonable, max ±50%)
                        if abs(change_percent) > 50:
                            # Calculate manually without printing error message
                            prev_close = info.get('previousClose', info.get('regularMarketPreviousClose', 0))
                            if prev_close and prev_close > 0 and current_price_val > 0:
                                change_percent = ((current_price_val - prev_close) / prev_close) * 100
                                if abs(change_percent) > 50:  # Still unreasonable
                                    change_percent = 0
                            else:
                                change_percent = 0
                    else:
                        # Method 3: Calculate from available price data
                        prev_close = info.get('previousClose', info.get('regularMarketPreviousClose', 0))
                        if prev_close and prev_close > 0 and current_price_val > 0:
                            change_percent = ((current_price_val - prev_close) / prev_close) * 100
                            # Cap at reasonable daily movement
                            if abs(change_percent) > 50:
                                change_percent = 0
                        else:
                            change_percent = 0
                    
                    # Get other market data with validation
                    volume = max(0, info.get('regularMarketVolume', info.get('volume', 0)))
                    avg_volume = max(0, info.get('averageVolume', info.get('averageVolume10days', 0)))
                    market_cap = max(0, info.get('marketCap', 0))
                    pe_ratio = info.get('trailingPE', info.get('forwardPE', 0))
                    
                    # Validate P/E ratio (reasonable range)
                    if pe_ratio and (pe_ratio <= 0 or pe_ratio > 500):
                        pe_ratio = 0
                    
                    # Get short news with timeout protection
                    try:
                        news_short = self.get_stock_news_short(symbol)
                    except:
                        news_short = f"{info.get('sector', 'Market')[:15]} stock"
                    
                    # Calculate adjusted ROI
                    roi = self.calculate_adjusted_roi(current_price, expected_return, volatility)
                    
                    # Get next earnings date
                    next_earnings = self.get_next_earnings_date(symbol)
                    
                except requests.exceptions.Timeout:
                    print(f"   ⏰ Timeout for {symbol}, using defaults")
                    change_percent = 0
                    volume = 0
                    avg_volume = 0
                    market_cap = 0
                    pe_ratio = 0
                    news_short = 'Data timeout'
                    roi = 0.0
                    next_earnings = 'N/A'
                    
                except requests.exceptions.SSLError:
                    print(f"   🔒 SSL error for {symbol}, trying alternative method")
                    # Try alternative approach with different SSL settings
                    try:
                        # Create session with relaxed SSL verification for corporate networks
                        session = requests.Session()
                        session.verify = False  # Disable SSL verification as fallback
                        session.timeout = 10
                        
                        # Disable SSL warnings
                        import urllib3
                        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                        
                        # Try to get basic data from a different endpoint or method
                        alt_ticker = yf.Ticker(symbol)
                        alt_ticker.session = session
                        info = alt_ticker.info
                        
                        change_percent = 0  # Default for SSL issues
                        volume = max(0, info.get('regularMarketVolume', info.get('volume', 0)))
                        avg_volume = max(0, info.get('averageVolume', 0))
                        market_cap = max(0, info.get('marketCap', 0))
                        pe_ratio = info.get('trailingPE', 0)
                        
                        if pe_ratio and (pe_ratio <= 0 or pe_ratio > 500):
                            pe_ratio = 0
                        
                        news_short = f"{info.get('sector', 'Tech')[:15]} sector"
                        roi = self.calculate_adjusted_roi(current_price, expected_return, volatility)
                        next_earnings = 'SSL-err'
                        
                    except Exception as alt_error:
                        print(f"   🔒 Alternative SSL method failed for {symbol}")
                        change_percent = 0
                        volume = 0
                        avg_volume = 0
                        market_cap = 0
                        pe_ratio = 0
                        news_short = 'SSL connection error'
                        roi = 0.0
                        next_earnings = 'N/A'
                    
                except Exception as data_error:
                    print(f"   ❌ Data error for {symbol}: {str(data_error)[:30]}")
                    # Use defaults if additional data fetch fails
                    change_percent = 0
                    volume = 0
                    avg_volume = 0
                    market_cap = 0
                    pe_ratio = 0
                    news_short = 'Data unavailable'
                    roi = 0.0
                    next_earnings = 'N/A'
                
                recommendations.append({
                    'Symbol': symbol,
                    'Company': company_name[:25] + '...' if len(company_name) > 25 else company_name,
                    'Price': current_price,
                    'Change_Percent': change_percent,
                    'Volume': volume,
                    'Average_Volume': avg_volume,
                    'Market_Cap': market_cap,
                    'PE_Ratio': pe_ratio,
                    'Expected_Return': expected_return,
                    'Volatility': volatility,
                    'Sharpe_Ratio': sharpe_ratio,
                    'Range_Position': range_position,
                    'Recommendation': recommendation,
                    'Risk_Level': risk_level,
                    'Position_Indicator': position_indicator,
                    'Sector': sector,
                    'Source': source_category,
                    'News': news_short,
                    'ROI': roi,
                    'Next_Earnings': next_earnings,
                    'Score': self.calculate_score(expected_return, volatility, sharpe_ratio, range_position)
                })
                
            except Exception as e:
                print(f"   ⚠️ Error processing {row.get('symbol', 'Unknown')}: {e}")
                continue
        
        # Sort by score (best recommendations first)
        recommendations.sort(key=lambda x: x['Score'], reverse=True)
        
        return recommendations

    def calculate_recommendation(self, expected_return: float, volatility: float, 
                               sharpe_ratio: float, range_position: float) -> str:
        """
        Calculate recommendation based on multiple factors
        """
        score = 0
        
        # Expected return scoring
        if expected_return > 20:
            score += 3
        elif expected_return > 10:
            score += 2
        elif expected_return > 5:
            score += 1
        elif expected_return < -10:
            score -= 2
        
        # Sharpe ratio scoring
        if sharpe_ratio > 1.5:
            score += 3
        elif sharpe_ratio > 1.0:
            score += 2
        elif sharpe_ratio > 0.5:
            score += 1
        elif sharpe_ratio < 0:
            score -= 2
        
        # Volatility penalty
        if volatility > 50:
            score -= 2
        elif volatility > 35:
            score -= 1
        
        # 52-week position consideration
        if 75 <= range_position <= 90:  # Sweet spot - momentum but not overextended
            score += 1
        elif range_position > 95:  # Too close to highs
            score -= 1
        elif range_position < 10:  # Too close to lows - risky
            score -= 1
        
        # Generate recommendation
        if score >= 4:
            return 'STRONG_BUY'
        elif score >= 2:
            return 'BUY'
        elif score >= 0:
            return 'HOLD'
        elif score >= -2:
            return 'AVOID'
        else:
            return 'STRONG_AVOID'

    def calculate_risk_level(self, volatility: float) -> str:
        """Calculate risk level based on volatility"""
        if volatility < 25:
            return 'LOW'
        elif volatility < 40:
            return 'MEDIUM'
        else:
            return 'HIGH'

    def get_position_indicator(self, range_position: float) -> str:
        """Get position indicator based on 52-week range position"""
        if range_position >= 80:
            return 'NEAR_HIGH'
        elif range_position <= 20:
            return 'NEAR_LOW'
        else:
            return 'MID_RANGE'

    def calculate_score(self, expected_return: float, volatility: float, 
                       sharpe_ratio: float, range_position: float) -> float:
        """Calculate numerical score for sorting"""
        base_score = (expected_return * 0.3) + (sharpe_ratio * 20) - (volatility * 0.2)
        
        # Position bonus/penalty
        if 70 <= range_position <= 85:
            base_score += 5
        elif range_position > 95:
            base_score -= 5
        elif range_position < 10:
            base_score -= 3
        
        return base_score

    def display_recommendations_table(self, recommendations: List[Dict], flash: bool = False, cycle_count: int = 0):
        """
        Display recommendations in a formatted terminal table
        
        Args:
            recommendations: List of recommendation dictionaries
            flash: Whether to add flashing effect
            cycle_count: Current analysis cycle for flashing logic
        """
        if not recommendations:
            print(f"{Colors.RED}❌ No recommendations available{Colors.END}")
            return
        
        # Identify new symbols
        current_symbols = [rec['Symbol'] for rec in recommendations]
        new_symbols, cache = self.identify_new_symbols(current_symbols)
        
        # Filter new symbols data for separate table
        new_symbol_recs = [rec for rec in recommendations if rec['Symbol'] in new_symbols]
        
        # Clear screen
        os.system('clear' if os.name == 'posix' else 'cls')
        
        # Header with enhanced flashing detection
        has_flash_rows = any(self.should_flash_row(rec, cycle_count) for rec in recommendations[:50])
        flash_effect = Colors.BLINK if flash or has_flash_rows else ""
        print(f"{flash_effect}{Colors.BOLD}{Colors.CYAN}")
        print("=" * 170)
        print("🚀 YAHOO FINANCE LIVE STOCK ANALYZER - TOP 50 RECOMMENDATIONS")
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 🔄 Next update in {self.update_interval}s")
        if has_flash_rows:
            print(f"{Colors.BLINK}{Colors.YELLOW}⚡ FLASHING: STRONG RECOMMENDATIONS & EXTREME CHANGES >5% ⚡{Colors.END}")
        print("=" * 170)
        print(f"{Colors.END}")
        
        # Clean table header with optimized column widths to prevent wrapping
        print(f"{Colors.BOLD}{Colors.WHITE}")
        header = (f"{'#':<4} {'Symbol':<7} {'Company':<20} {'Price':<9} {'Chg%':<7} "
                 f"{'Vol(M)':<7} {'Ret%':<7} {'Vol%':<7} {'SR':<6} {'Pos%':<6} "
                 f"{'Risk':<7} {'MCap':<7} {'PE':<5} {'ROI%':<6} "
                 f"{'Earn':<8} {'Sector':<12} {'Recommendation':<15} {'News':<25}")
        print(header)
        print("─" * 170)
        print(f"{Colors.END}")
        
        # Display top 50 recommendations with enhanced flashing
        for i, rec in enumerate(recommendations[:50], 1):
            # Color coding based on recommendation
            if rec['Recommendation'] == 'STRONG_BUY':
                color = Colors.GREEN + Colors.BOLD
                flash_color = Colors.GREEN + Colors.BOLD if self.should_flash_row(rec, cycle_count) else color
            elif rec['Recommendation'] == 'BUY':
                color = Colors.GREEN
                flash_color = color  
            elif rec['Recommendation'] == 'HOLD':
                color = Colors.YELLOW
                flash_color = color
            elif rec['Recommendation'] == 'AVOID':
                color = Colors.MAGENTA
                flash_color = color
            else:  # STRONG_AVOID
                color = Colors.RED + Colors.BOLD
                flash_color = Colors.RED + Colors.BOLD if self.should_flash_row(rec, cycle_count) else color
            
            # Add visual flash indicators
            flash_prefix = ""
            flash_suffix = ""
            if self.should_flash_row(rec, cycle_count):
                flash_prefix = "⚡⚡ "
                flash_suffix = " ⚡⚡"
                flash_color = Colors.YELLOW + Colors.BOLD  # Bright yellow for attention
            
            # Check for extreme price changes flashing
            change_pct = rec.get('Change_Percent', 0)
            if abs(change_pct) > 5.0 and cycle_count % 3 == 0:
                flash_prefix = "🔥🔥 "
                flash_suffix = " 🔥🔥"
                flash_color = Colors.CYAN + Colors.BOLD  # Bright cyan for extreme changes
            
            # Get emojis for risk display only
            risk_emoji = RISK_EMOJIS.get(rec['Risk_Level'], '❓')
            
                        # Format data with proper alignment (removed Rec column)
            price_str = f"${rec['Price']:.2f}"
            change_pct = rec.get('Change_Percent', 0.0)
            
            # Handle invalid change percentages silently
            if change_pct == 0 or abs(change_pct) > 50:  # Cap extreme values
                if abs(change_pct) > 50:
                    # Silently use a reasonable estimate for extreme values
                    change_pct = 0.0
                change_str = "  0.0%"
            else:
                change_str = f"{change_pct:+5.1f}%"[:8]  # Limit to 8 chars max
            volume_str = f"{rec.get('Volume', 0)/1e6:.1f}" if rec.get('Volume', 0) > 0 else "N/A"
            ret_str = f"{rec['Expected_Return']:.1f}%"
            vol_str = f"{rec['Volatility']:.1f}%"
            sharpe_str = f"{rec['Sharpe_Ratio']:.2f}"
            pos_str = f"{rec['Range_Position']:.1f}%"
            risk_str = f"{risk_emoji}{rec['Risk_Level'][:3]}"
            mcap_str = f"{rec.get('Market_Cap', 0)/1e9:.1f}B" if rec.get('Market_Cap', 0) > 0 else "N/A"
            pe_str = f"{rec.get('PE_Ratio', 0):.1f}" if rec.get('PE_Ratio', 0) > 0 and rec.get('PE_Ratio', 0) < 1000 else "N/A"
            roi_str = f"{rec.get('ROI', 0):.1f}%" if rec.get('ROI', 0) != 0 else "N/A"
            earn_str = rec.get('Next_Earnings', 'N/A')
            sector_str = rec['Sector'][:12] + '..' if len(rec['Sector']) > 12 else rec['Sector']
            company_str = rec['Company'][:18] + '..' if len(rec['Company']) > 18 else rec['Company']
            
            # Get news for the stock (shorter format for table fit)
            news_str = rec.get('News', self.get_stock_news_short(rec['Symbol']))
            if len(news_str) > 23:
                news_str = news_str[:20] + "..."
            
            # Use flashing color for qualifying rows
            display_color = flash_color
            
            # Get recommendation text for display
            rec_text = rec['Recommendation'].replace('_', ' ')
            
            # Print clean row format with flash indicators
            row = (f"{flash_prefix}{i:<4} {rec['Symbol']:<7} {company_str:<20} {price_str:<9} {change_str:<7} "
                  f"{volume_str:<7} {ret_str:<7} {vol_str:<7} {sharpe_str:<6} {pos_str:<6} "
                  f"{risk_str:<7} {mcap_str:<7} {pe_str:<5} {roi_str:<6} "
                  f"{earn_str:<8} {sector_str:<12} {rec_text:<15} {news_str:<25}{flash_suffix}")
            
            print(f"{display_color}{row}{Colors.END}")
        
        print("─" * 170)
        
        # Brief visual pause for flashing cycles
        if cycle_count % 3 == 0:
            time.sleep(0.3)  # Brief pause to enhance flashing visibility
        
        # Display new symbols table if any (but limit to 25 for readability)
        if new_symbol_recs and len(new_symbol_recs) <= 50:
            self.display_new_symbols_table(new_symbol_recs, cache)
        
        # Enhanced compact legend with better descriptions and ranges
        print()
        legend_color = Colors.BOLD + Colors.CYAN
        print(f"{legend_color}📊 COMPREHENSIVE QUICK REFERENCE:{Colors.END}")
        
        # Recommendation types with explanations
        print(f"🎯 {Colors.GREEN}🚀STRONG_BUY{Colors.END}(Best picks) {Colors.GREEN}💰BUY{Colors.END}(Good buys) "
              f"{Colors.YELLOW}⚖️HOLD{Colors.END}(Wait&watch) {Colors.MAGENTA}⚠️AVOID{Colors.END}(Skip) {Colors.RED}🛑STRONG_AVOID{Colors.END}(Dangerous)")
        
        # Risk levels and metrics with ranges
        print(f"⚖️ Risk: {Colors.GREEN}🟢LOW{Colors.END}(<20% vol) {Colors.YELLOW}🟡MED{Colors.END}(20-40% vol) "
              f"{Colors.RED}🔴HIGH{Colors.END}(>40% vol) | ⚡Vol%: {Colors.GREEN}<20{Colors.END}(stable) "
              f"{Colors.YELLOW}20-40{Colors.END}(moderate) {Colors.RED}>40{Colors.END}(volatile)")
        
        print(f"📈 Sharpe: {Colors.RED}<0.5{Colors.END}(poor) {Colors.YELLOW}0.5-1.0{Colors.END}(fair) "
              f"{Colors.GREEN}1.0-2.0{Colors.END}(good) {Colors.GREEN}>2.0{Colors.END}(excellent)")
        
        # Enhanced column explanations for clean header format
        print(f"{Colors.CYAN}📋 Columns: Price(USD) Chg%(daily) Vol(M/daily) Ret%(annual) Vol%(risk) "
              f"SR(risk-adj) Pos%(52W-range) Risk MCap(B) PE(ratio) "
              f"ROI%(adj-return) Earn(next-date) Sector Recommendation News(recent) {Colors.END}")
        
        if has_flash_rows:
            print(f"{Colors.BLINK}{Colors.BOLD}{Colors.YELLOW}⚡ FLASHING: STRONG BUY/AVOID & EXTREME CHANGES >5% ⚡{Colors.END}")
        
        stats_color = Colors.BOLD + Colors.YELLOW
        print(f"{stats_color}📊 {len(recommendations)} stocks analyzed | Top 50 displayed{Colors.END}", end="")
        if self.save_data:
            print(f" | {Colors.BLUE}💾 Auto-saved to {self.output_dir}{Colors.END}")
        else:
            print()
        
        if new_symbol_recs:
            print(f"{Colors.CYAN}🆕 {len(new_symbol_recs)} new symbols detected today{Colors.END}")
            if len(new_symbol_recs) > 25:
                print(f"{Colors.YELLOW}⚠️ Showing first 25 new symbols in table above{Colors.END}")

    def display_new_symbols_table(self, new_symbol_recs: List[Dict], cache: Dict[str, str]):
        """Display table of new symbols detected today"""
        if not new_symbol_recs:
            return
            
        print(f"\\n{Colors.BOLD}{Colors.CYAN}🆕 NEW SYMBOLS DETECTED TODAY ({len(new_symbol_recs)} symbols){Colors.END}")
        print("─" * 170)
        
        # Compact header for new symbols
        print(f"{Colors.BOLD}{Colors.WHITE}")
        header = (f"{'#':<4} {'Symbol':<7} {'Company':<20} {'Price':<9} {'Chg%':<7} "
                 f"{'Recommendation':<15} {'Risk':<7} {'ROI%':<6} {'First Seen':<12} {'News':<25}")
        print(header)
        print("─" * 170)
        print(f"{Colors.END}")
        
        # Display new symbols (limit to 25 for readability)
        for i, rec in enumerate(new_symbol_recs[:25], 1):
            # Color coding with flashing for strong recommendations
            if rec['Recommendation'] == 'STRONG_BUY':
                color = Colors.BLINK + Colors.GREEN + Colors.BOLD
            elif rec['Recommendation'] == 'BUY':
                color = Colors.GREEN
            elif rec['Recommendation'] == 'STRONG_AVOID':
                color = Colors.BLINK + Colors.RED + Colors.BOLD
            elif rec['Recommendation'] == 'AVOID':
                color = Colors.RED
            else:
                color = Colors.YELLOW
            
            # Format data
            price_str = f"${rec['Price']:.2f}"
            change_pct = rec.get('Change_Percent', 0.0)
            if abs(change_pct) > 50:
                change_str = "  N/A%"
            else:
                change_str = f"{change_pct:+5.1f}%"[:7]
            
            company_str = rec['Company'][:18] + '..' if len(rec['Company']) > 18 else rec['Company']
            rec_text = rec['Recommendation'].replace('_', ' ')
            risk_emoji = RISK_EMOJIS.get(rec['Risk_Level'], '❓')
            risk_str = f"{risk_emoji}{rec['Risk_Level'][:3]}"
            roi_str = f"{rec.get('ROI', 0):.1f}%" if rec.get('ROI', 0) != 0 else "N/A"
            first_seen = cache.get(rec['Symbol'], 'Today')
            
            news_str = rec.get('News', 'No recent news')
            if len(news_str) > 23:
                news_str = news_str[:20] + "..."
            
            # Print row
            row = (f"{i:<4} {rec['Symbol']:<7} {company_str:<20} {price_str:<9} {change_str:<7} "
                  f"{rec_text:<15} {risk_str:<7} {roi_str:<6} {first_seen:<12} {news_str:<25}")
            
            print(f"{color}{row}{Colors.END}")
        
        print("─" * 170)
        print(f"{Colors.CYAN}📅 Symbols cache: {len(cache)} total symbols tracked{Colors.END}")
        
        if len(new_symbol_recs) > 25:
            remaining = len(new_symbol_recs) - 25
            print(f"{Colors.YELLOW}⚠️ Showing first 25 new symbols ({remaining} more detected){Colors.END}")

    def run_single_analysis(self):
        """Run a single analysis cycle"""
        print("\\n📊 Running single analysis cycle...")
        
        # Get all recommendations
        recommendations = self.get_all_recommendations()
        
        if recommendations:
            # Single run - no flashing, cycle count = 1
            self.display_recommendations_table(recommendations, flash=False, cycle_count=1)
            
            # Save data if enabled
            if self.save_data:
                self.save_analysis_data(recommendations)
                
            print(f"\\n✅ Analysis complete! Analyzed {len(recommendations)} stocks")
            print(f"📊 Cache file: {self.cache_file}")
            if self.save_data:
                print(f"💾 Data saved to: {self.output_dir}")
        else:
            print("❌ No data available for analysis")

    def calculate_adjusted_roi(self, current_price: float, expected_return: float, volatility: float) -> float:
        """
        Calculate adjusted ROI based on expected return and risk
        
        Args:
            current_price: Current stock price
            expected_return: Expected annual return percentage
            volatility: Stock volatility percentage
            
        Returns:
            Adjusted ROI percentage
        """
        try:
            # Adjust return based on volatility (risk-adjusted)
            risk_adjustment = max(0.1, 1 - (volatility / 100))  # Higher volatility reduces ROI
            adjusted_roi = expected_return * risk_adjustment
            
            # Cap ROI between -50% and 100%
            return max(-50.0, min(100.0, adjusted_roi))
            
        except Exception:
            return 0.0

    def get_next_earnings_date(self, symbol: str) -> str:
        """
        Get next earnings reporting date for a stock
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Next earnings date as string (MM-DD format or 'N/A')
        """
        try:
            ticker = yf.Ticker(symbol)
            
            # Try to get earnings calendar from info
            info = ticker.info
            earnings_date = info.get('earningsDate', None)
            
            if earnings_date:
                # Handle different date formats
                if isinstance(earnings_date, list) and len(earnings_date) > 0:
                    # Take the first date if it's a list
                    next_date = earnings_date[0]
                elif isinstance(earnings_date, (int, float)):
                    next_date = earnings_date
                else:
                    next_date = earnings_date
                
                # Convert timestamp to readable date
                if isinstance(next_date, (int, float)):
                    date_obj = datetime.fromtimestamp(next_date)
                    return date_obj.strftime('%m-%d')
                
            # Fallback: try to get from earnings history
            try:
                earnings = ticker.earnings_dates
                if earnings is not None and not earnings.empty:
                    # Get the next future date
                    future_dates = earnings.index[earnings.index > datetime.now()]
                    if len(future_dates) > 0:
                        return future_dates[0].strftime('%m-%d')
            except:
                pass
            
            return 'N/A'
            
        except Exception:
            return 'N/A'

    def load_symbols_cache(self) -> Dict[str, str]:
        """Load cached symbols with their first seen dates"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        return {}
    
    def save_symbols_cache(self, cache: Dict[str, str]):
        """Save symbols cache to file"""
        try:
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.cache_file, 'w') as f:
                json.dump(cache, f, indent=2)
        except Exception as e:
            print(f"⚠️ Warning: Could not save cache file: {e}")
    
    def identify_new_symbols(self, current_symbols: List[str]) -> Tuple[List[str], Dict[str, str]]:
        """Identify new symbols not seen before today"""
        cache = self.load_symbols_cache()
        today = datetime.now().strftime('%Y-%m-%d')
        new_symbols = []
        
        for symbol in current_symbols:
            if symbol not in cache:
                cache[symbol] = today
                new_symbols.append(symbol)
            # Don't consider symbols as "new" if they were first seen today in previous runs
            elif cache[symbol] != today:
                # Symbol exists but from previous days - not new for today
                pass
        
        # Save updated cache
        self.save_symbols_cache(cache)
        
        return new_symbols, cache
    
    def should_flash_row(self, rec: dict, cycle_count: int = 0) -> bool:
        """Determine if a row should flash based on criteria"""
        # Flash every 3 cycles for visibility
        if cycle_count % 3 != 0:
            return False
            
        # Flash STRONG_BUY and STRONG_AVOID
        if rec['Recommendation'] in ['STRONG_BUY', 'STRONG_AVOID']:
            return True
        
        # Flash extreme price changes (>5% up or down)
        change_pct = rec.get('Change_Percent', 0)
        if abs(change_pct) > 5.0:
            return True
            
        return False

    def get_stock_news_short(self, symbol: str) -> str:
        """
        Get short breaking news for a specific stock symbol using real news data
        
        Args:
            symbol: Stock symbol to get news for
            
        Returns:
            Short news string (max 33 chars) or "No recent news"
        """
        try:
            ticker = yf.Ticker(symbol)
            news = ticker.news
            
            if news and len(news) > 0:
                # Get the most recent news item
                latest_news = news[0]
                
                # Handle nested content structure from yfinance
                title = ''
                pub_time = 0
                
                if isinstance(latest_news, dict):
                    # Try to get title from nested content structure
                    if 'content' in latest_news and isinstance(latest_news['content'], dict):
                        title = latest_news['content'].get('title', '')
                        # Try to get publish time from content or root level
                        pub_time = latest_news['content'].get('pubDate', latest_news.get('providerPublishTime', 0))
                        
                        # Convert pubDate string to timestamp if needed
                        if isinstance(pub_time, str):
                            try:
                                from dateutil import parser
                                pub_time = parser.parse(pub_time).timestamp()
                            except:
                                pub_time = 0
                    else:
                        # Fallback to direct fields
                        title = latest_news.get('title', '')
                        pub_time = latest_news.get('providerPublishTime', 0)
                
                if title and pub_time > 0:
                    # Check if news is recent (within 24 hours)
                    try:
                        news_date = datetime.fromtimestamp(pub_time)
                        today = datetime.now()
                        
                        # If news is older than 1 day, show "No recent news"
                        if (today - news_date).days > 0:
                            return 'No recent news'
                    except:
                        # If date parsing fails, assume it's recent
                        pass
                    
                    # Clean and format the title
                    title = title.replace(symbol, '').replace(symbol.upper(), '').strip()
                    title = title.replace(symbol.lower(), '').strip()
                    title = re.sub(r'^\W+', '', title)  # Remove leading punctuation
                    title = re.sub(r'\s+', ' ', title)  # Normalize spaces
                    
                    # Remove common prefixes
                    prefixes_to_remove = [
                        'Stock News:', 'Breaking:', 'UPDATE:', 'ALERT:', 
                        'News Alert:', 'Stock Alert:', symbol + ':', symbol.upper() + ':'
                    ]
                    for prefix in prefixes_to_remove:
                        if title.startswith(prefix):
                            title = title[len(prefix):].strip()
                    
                    # Truncate to fit column width
                    if len(title) > 32:
                        title = title[:29] + '...'
                    
                    # Only return if we have meaningful content
                    if title and len(title.strip()) > 3:
                        return title
            
            return 'No recent news'
                
        except Exception as e:
            # Return a more informative message for common errors
            error_msg = str(e).lower()
            if 'timeout' in error_msg or 'connection' in error_msg:
                return 'News fetch timeout'
            elif 'not found' in error_msg or '404' in error_msg:
                return 'Ticker not found'
            else:
                return 'No recent news'

    def get_live_recommendations(self) -> List[Dict]:
        """
        Get live recommendations by running the full analysis pipeline
        
        Returns:
            List of recommendation dictionaries
        """
        try:
            # Fetch live data
            categories_data = self.fetch_live_data()
            
            if not categories_data:
                return []
            
            # Combine and deduplicate
            combined_data = self.combine_and_deduplicate_data(categories_data)
            
            if combined_data.empty:
                return []
            
            # Analyze with risk tool
            analysis_results = self.analyze_stocks_with_risk_tool(combined_data)
            
            if analysis_results.empty:
                return []
            
            # Generate and return recommendations
            recommendations = self.generate_recommendations(analysis_results)
            
            # Store latest recommendations for saving
            self.latest_recommendations = recommendations
            
            return recommendations
            
        except Exception as e:
            print(f"{Colors.RED}❌ Error getting live recommendations: {str(e)}{Colors.END}")
            return []

    def save_analysis_data(self, recommendations: List[Dict]):
        """
        Save analysis data to Excel file
        
        Args:
            recommendations: List of recommendation dictionaries
        """
        if not self.save_data or not recommendations:
            return
        
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = self.output_dir / f"yahoo_live_analysis_{timestamp}.xlsx"
            
            # Convert to DataFrame
            df = pd.DataFrame(recommendations)
            
            # Create Excel with multiple sheets
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # Main recommendations
                df.to_excel(writer, sheet_name='Live_Recommendations', index=False)
                
                # Summary statistics
                summary_data = {
                    'Metric': [
                        'Total Stocks Analyzed',
                        'Strong Buy Recommendations',
                        'Buy Recommendations', 
                        'Hold Recommendations',
                        'Avoid Recommendations',
                        'Strong Avoid Recommendations',
                        'Average Expected Return (%)',
                        'Average Volatility (%)',
                        'Average Sharpe Ratio',
                        'Analysis Timestamp'
                    ],
                    'Value': [
                        len(recommendations),
                        len([r for r in recommendations if r['Recommendation'] == 'STRONG_BUY']),
                        len([r for r in recommendations if r['Recommendation'] == 'BUY']),
                        len([r for r in recommendations if r['Recommendation'] == 'HOLD']),
                        len([r for r in recommendations if r['Recommendation'] == 'AVOID']),
                        len([r for r in recommendations if r['Recommendation'] == 'STRONG_AVOID']),
                        f"{np.mean([r['Expected_Return'] for r in recommendations]):.2f}%",
                        f"{np.mean([r['Volatility'] for r in recommendations]):.2f}%",
                        f"{np.mean([r['Sharpe_Ratio'] for r in recommendations]):.3f}",
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    ]
                }
                
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary_Stats', index=False)
            
            print(f"{Colors.GREEN}💾 Analysis data saved: {filename}{Colors.END}")
            
        except Exception as e:
            print(f"{Colors.RED}❌ Error saving data: {e}{Colors.END}")

    def run_continuous_analysis(self):
        """
        Main loop for continuous analysis and display
        """
        print(f"{Colors.BOLD}{Colors.GREEN}🚀 Starting continuous analysis...{Colors.END}")
        print(f"{Colors.YELLOW}Press Ctrl+C to stop{Colors.END}")
        print(f"{Colors.BLUE}⚡ Flashing effects will occur every 3rd cycle{Colors.END}")
        print()
        
        cycle_count = 0
        
        try:
            while True:
                cycle_count += 1
                start_time = time.time()
                
                # Alternate flashing every 2nd cycle for more visibility
                use_flash = (cycle_count % 2 == 0)
                
                flash_indicator = "⚡ FLASH" if use_flash else "📊 STEADY"
                print(f"{Colors.BOLD}{Colors.BLUE}🔄 Analysis Cycle #{cycle_count} {flash_indicator}{Colors.END}")
                
                # Fetch live data
                categories_data = self.fetch_live_data()
                
                if categories_data:
                    # Combine and deduplicate
                    combined_data = self.combine_and_deduplicate_data(categories_data)
                    
                    if not combined_data.empty:
                        # Analyze with risk tool
                        analysis_results = self.analyze_stocks_with_risk_tool(combined_data)
                        
                        if not analysis_results.empty:
                            # Generate recommendations
                            recommendations = self.generate_recommendations(analysis_results)
                            
                            if recommendations:
                                # Display recommendations with cycle count for flashing logic
                                self.display_recommendations_table(recommendations, flash=use_flash, cycle_count=cycle_count)
                                
                                # Save data if enabled
                                self.save_analysis_data(recommendations)
                                
                                if recommendations:
                                    # Display recommendations with cycle count for flashing logic
                                    self.display_recommendations_table(recommendations, flash=use_flash, cycle_count=cycle_count)
                                
                                # Save data if enabled
                                self.save_analysis_data(recommendations)
                                
                                # Show cycle status
                                if cycle_count % 3 == 0:
                                    print(f"\\n{Colors.BLINK}{Colors.BOLD}{Colors.YELLOW}⚡ FLASH CYCLE #{cycle_count} - STRONG RECOMMENDATIONS & EXTREME CHANGES HIGHLIGHTED ⚡{Colors.END}")
                                else:
                                    print(f"\\n{Colors.BOLD}{Colors.CYAN}📊 CYCLE #{cycle_count} COMPLETE{Colors.END}")
                                
                            else:
                                print(f"{Colors.RED}❌ No valid recommendations generated{Colors.END}")
                        else:
                            print(f"{Colors.RED}❌ No analysis results available{Colors.END}")
                    else:
                        print(f"{Colors.RED}❌ No valid stock data available{Colors.END}")
                else:
                    print(f"{Colors.RED}❌ Failed to fetch data from Yahoo Finance{Colors.END}")
                
                # Calculate sleep time and show countdown
                elapsed_time = time.time() - start_time
                sleep_time = max(0, self.update_interval - elapsed_time)
                
                if sleep_time > 0:
                    countdown_color = Colors.BLINK + Colors.YELLOW if use_flash else Colors.CYAN
                    print(f"{countdown_color}⏰ Waiting {sleep_time:.1f}s for next update...{Colors.END}")
                    
                    # Simplified countdown for better UX  
                    if sleep_time > 10:  # Only show countdown for longer waits
                        for remaining in range(int(sleep_time), 0, -10):  # Show every 10 seconds
                            if remaining <= sleep_time:
                                countdown_flash = Colors.BLINK if use_flash else ""
                                print(f"\r{countdown_flash}{Colors.YELLOW}⏳ Next analysis in: {remaining:4d}s{Colors.END}", 
                                      end='', flush=True)
                                time.sleep(min(10, remaining))
                        print()  # New line after countdown
                    else:
                        time.sleep(sleep_time)
                
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}🛑 Analysis stopped by user{Colors.END}")
            print(f"{Colors.CYAN}📊 Total cycles completed: {cycle_count}{Colors.END}")
            print(f"{Colors.GREEN}✨ Thank you for using Yahoo Finance Live Analyzer!{Colors.END}")
        except Exception as e:
            print(f"\n{Colors.RED}❌ Unexpected error: {e}{Colors.END}")

def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(
        description='Yahoo Finance Live Data Analyzer & Recommendation Engine',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python yahoo_finance_data_analyzer.py                     # Default 5-minute updates
  python yahoo_finance_data_analyzer.py --interval 60       # 1-minute updates  
  python yahoo_finance_data_analyzer.py --interval 300 --save  # 5-min updates with data saving
  python yahoo_finance_data_analyzer.py --save --output-dir my_analysis  # Custom save location
        """
    )
    
    parser.add_argument(
        '--interval', 
        type=int, 
        default=300,
        help='Update interval in seconds (default: 300 = 5 minutes)'
    )
    
    parser.add_argument(
        '--save',
        action='store_true',
        help='Save analysis data to Excel files'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='live_analysis',
        help='Directory for saved analysis data (default: live_analysis)'
    )
    
    args = parser.parse_args()
    
    # Validate interval
    if args.interval < 30:
        print(f"⚠️ Warning: Update interval of {args.interval}s is very frequent. Consider >= 60s to avoid API limits.")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            return
    
    # Create and run analyzer
    analyzer = YahooFinanceLiveAnalyzer(
        update_interval=args.interval,
        save_data=args.save,
        output_dir=args.output_dir
    )
    
    analyzer.run_continuous_analysis()

if __name__ == "__main__":
    main()
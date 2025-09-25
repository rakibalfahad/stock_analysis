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
import argparse
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import yfinance as yf
from pathlib import Path

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
        Fetch live data from all Yahoo Finance categories
        
        Returns:
            Dictionary with category data
        """
        print(f"{Colors.YELLOW}📡 Fetching live data from Yahoo Finance...{Colors.END}")
        
        try:
            # Get data from all categories
            categories_data = {}
            
            # Fetch each category
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
                    data = fetch_func(limit=50)  # Get more data for better analysis
                    if not data.empty:
                        categories_data[category_name] = data
                        print(f"   ✅ {category_name.replace('_', ' ').title()}: {len(data)} stocks")
                    else:
                        print(f"   ⚠️ {category_name.replace('_', ' ').title()}: No data")
                except Exception as e:
                    print(f"   ❌ {category_name.replace('_', ' ').title()}: Error - {e}")
            
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
                
                # Fetch additional market data
                try:
                    ticker = yf.Ticker(symbol)
                    info = ticker.info
                    
                    change_percent = info.get('regularMarketChangePercent', 0) * 100 if info.get('regularMarketChangePercent') else 0
                    volume = info.get('regularMarketVolume', 0)
                    avg_volume = info.get('averageVolume', 0)
                    market_cap = info.get('marketCap', 0)
                    pe_ratio = info.get('trailingPE', 0)
                    
                except Exception as data_error:
                    # Use defaults if additional data fetch fails
                    change_percent = 0
                    volume = 0
                    avg_volume = 0
                    market_cap = 0
                    pe_ratio = 0
                
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

    def display_recommendations_table(self, recommendations: List[Dict], flash: bool = False):
        """
        Display recommendations in a formatted terminal table
        
        Args:
            recommendations: List of recommendation dictionaries
            flash: Whether to add flashing effect
        """
        if not recommendations:
            print(f"{Colors.RED}❌ No recommendations available{Colors.END}")
            return
        
        # Clear screen
        os.system('clear' if os.name == 'posix' else 'cls')
        
        # Header with flashing effect
        flash_effect = Colors.BLINK if flash else ""
        print(f"{flash_effect}{Colors.BOLD}{Colors.CYAN}")
        print("=" * 180)
        print("🚀 YAHOO FINANCE LIVE STOCK ANALYZER - TOP 50 RECOMMENDATIONS")
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 🔄 Next update in {self.update_interval}s")
        print("=" * 180)
        print(f"{Colors.END}")
        
        # Table with borders - Header (fixed alignment)
        print(f"{Colors.BOLD}{Colors.WHITE}")
        # Define consistent column widths
        col_widths = [4, 3, 8, 26, 11, 8, 9, 8, 8, 7, 7, 9, 6, 9, 7, 19, 13]
        
        # Top border
        border_top = "┌" + "┬".join("─" * w for w in col_widths) + "┐"
        print(border_top)
        
        # Header row with perfect alignment
        headers = ["#", "📊", "Symbol", "Company", "💰Price", "📈Chg%", "📊Vol(M)", 
                  "🎯Ret%", "⚡Vol%", "📈SR", "🔥Pos%", "⚖️Risk", "📍52W", "💹MCap", 
                  "📊PE", "🏢Sector", "Rec"]
        
        header_row = "│" + "│".join(f"{h:^{w}}" for h, w in zip(headers, col_widths)) + "│"
        print(header_row)
        
        # Separator
        border_sep = "├" + "┼".join("─" * w for w in col_widths) + "┤"
        print(border_sep)
        print(f"{Colors.END}")
        
        # Display top 50 recommendations with borders and perfect alignment
        for i, rec in enumerate(recommendations[:50], 1):
            # Color coding based on recommendation
            if rec['Recommendation'] == 'STRONG_BUY':
                color = Colors.GREEN + Colors.BOLD
                flash_color = Colors.BLINK + Colors.GREEN + Colors.BOLD if flash and i <= 10 else color
            elif rec['Recommendation'] == 'BUY':
                color = Colors.GREEN
                flash_color = Colors.BLINK + Colors.GREEN if flash and i <= 10 else color
            elif rec['Recommendation'] == 'HOLD':
                color = Colors.YELLOW
                flash_color = color
            elif rec['Recommendation'] == 'AVOID':
                color = Colors.MAGENTA
                flash_color = color
            else:  # STRONG_AVOID
                color = Colors.RED
                flash_color = color
            
            # Get emojis
            rec_emoji = RECOMMENDATION_EMOJIS.get(rec['Recommendation'], '❓')
            risk_emoji = RISK_EMOJIS.get(rec['Risk_Level'], '❓')
            pos_emoji = POSITION_EMOJIS.get(rec['Position_Indicator'], '❓')
            
            # Format data with consistent column widths
            data_values = [
                str(i),  # Rank
                rec_emoji,  # Recommendation emoji
                rec['Symbol'],  # Symbol
                rec['Company'][:24] + '..' if len(rec['Company']) > 24 else rec['Company'],  # Company
                f"${rec['Price']:.2f}",  # Price
                f"{rec.get('Change_Percent', 0):+.1f}%" if rec.get('Change_Percent', 0) != 0 else "0.0%",  # Change %
                f"{rec.get('Volume', 0)/1e6:.1f}" if rec.get('Volume', 0) > 0 else "N/A",  # Volume
                f"{rec['Expected_Return']:.1f}%",  # Expected Return
                f"{rec['Volatility']:.1f}%",  # Volatility
                f"{rec['Sharpe_Ratio']:.2f}",  # Sharpe Ratio
                f"{rec['Range_Position']:.1f}%",  # Position
                f"{risk_emoji}{rec['Risk_Level'][:3]}",  # Risk
                pos_emoji,  # Position indicator
                f"{rec.get('Market_Cap', 0)/1e9:.1f}B" if rec.get('Market_Cap', 0) > 0 else "N/A",  # Market Cap
                f"{rec.get('PE_Ratio', 0):.1f}" if rec.get('PE_Ratio', 0) > 0 and rec.get('PE_Ratio', 0) < 1000 else "N/A",  # PE Ratio
                rec['Sector'][:17] + '..' if len(rec['Sector']) > 17 else rec['Sector'],  # Sector
                f"{rec_emoji}{rec['Recommendation'][:8]}"  # Recommendation
            ]
            
            # Use flashing color for top 10 recommendations
            display_color = flash_color if i <= 10 and flash else color
            
            # Create perfectly aligned row
            data_row = "│" + "│".join(f"{val:^{w}}" for val, w in zip(data_values, col_widths)) + "│"
            print(f"{display_color}{data_row}{Colors.END}")
        
        # Bottom border
        print(f"{Colors.BOLD}{Colors.WHITE}")
        border_bottom = "└" + "┴".join("─" * w for w in col_widths) + "┘"
        print(border_bottom)
        print(f"{Colors.END}")
        
        # Enhanced compact legend with better descriptions and ranges
        print()
        legend_color = Colors.BLINK + Colors.BOLD + Colors.CYAN if flash else Colors.BOLD + Colors.CYAN
        print(f"{legend_color}📊 COMPREHENSIVE QUICK REFERENCE:{Colors.END}")
        
        # Recommendation types with explanations
        print(f"🎯 {Colors.GREEN}🚀STRONG_BUY{Colors.END}(Best picks) {Colors.GREEN}💰BUY{Colors.END}(Good buys) "
              f"{Colors.YELLOW}⚖️HOLD{Colors.END}(Wait&watch) {Colors.MAGENTA}⚠️AVOID{Colors.END}(Skip) {Colors.RED}🛑STRONG_AVOID{Colors.END}(Dangerous)")
        
        # Risk levels and metrics with ranges
        print(f"⚖️ Risk: {Colors.GREEN}🟢LOW{Colors.END}(<20% vol) {Colors.YELLOW}🟡MED{Colors.END}(20-40% vol) "
              f"{Colors.RED}🔴HIGH{Colors.END}(>40% vol) | ⚡Vol%: {Colors.GREEN}<20{Colors.END}(stable) "
              f"{Colors.YELLOW}20-40{Colors.END}(moderate) {Colors.RED}>40{Colors.END}(volatile)")
        
        print(f"📈 Sharpe: {Colors.RED}<0.5{Colors.END}(poor) {Colors.YELLOW}0.5-1.0{Colors.END}(fair) "
              f"{Colors.GREEN}1.0-2.0{Colors.END}(good) {Colors.GREEN}>2.0{Colors.END}(excellent) | "
              f"52W: {Colors.RED}🔥{Colors.END}(80-100%) {Colors.YELLOW}⚡{Colors.END}(20-80%) {Colors.CYAN}❄️{Colors.END}(0-20%)")
        
        # Enhanced column explanations with new metrics
        print(f"{Colors.CYAN}📋 Columns: 💰Price 📈Chg%(daily) 📊Vol(M/daily) 🎯Ret%(annual) ⚡Vol%(risk) "
              f"📈SR(risk-adj) 🔥Pos%(52W) 💹MCap(B) 📊PE(ratio) 🏢Sector{Colors.END}")
        
        if flash:
            print(f"{Colors.BLINK}{Colors.BOLD}{Colors.YELLOW}⚡ FLASH MODE - TOP 10 RECOMMENDATIONS HIGHLIGHTED ⚡{Colors.END}")
        
        stats_color = Colors.BOLD + Colors.YELLOW if flash else Colors.YELLOW
        print(f"{stats_color}📊 {len(recommendations)} stocks analyzed | Top 50 displayed{Colors.END}", end="")
        if self.save_data:
            print(f" | {Colors.BLUE}💾 Auto-saved to {self.output_dir}{Colors.END}")
        else:
            print()
        
        # Add extra visual effect for flashing
        if flash:
            time.sleep(0.2)  # Brief pause for visual effect

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
        print(f"{Colors.BLUE}⚡ Flashing effects will occur every 2nd cycle{Colors.END}")
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
                                # Display recommendations with flashing
                                self.display_recommendations_table(recommendations, use_flash)
                                
                                # Save data if enabled
                                self.save_analysis_data(recommendations)
                                
                                # Show flash status
                                if use_flash:
                                    print(f"\n{Colors.BLINK}{Colors.BOLD}{Colors.YELLOW}⚡ FLASH CYCLE #{cycle_count} COMPLETE ⚡{Colors.END}")
                                else:
                                    print(f"\n{Colors.BOLD}{Colors.CYAN}📊 STEADY CYCLE #{cycle_count} COMPLETE{Colors.END}")
                                
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
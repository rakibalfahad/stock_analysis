#!/usr/bin/env python3
"""
Yahoo Finance Live Data Analyzer & Recommendation Engine
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
                
                recommendations.append({
                    'Symbol': symbol,
                    'Company': company_name[:25] + '...' if len(company_name) > 25 else company_name,
                    'Price': current_price,
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
        
        # Header
        flash_effect = Colors.BLINK if flash else ""
        print(f"{flash_effect}{Colors.BOLD}{Colors.CYAN}")
        print("=" * 150)
        print("🚀 YAHOO FINANCE LIVE STOCK ANALYZER - TOP 50 RECOMMENDATIONS")
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 🔄 Next update in {self.update_interval}s")
        print("=" * 150)
        print(f"{Colors.END}")
        
        # Table header
        print(f"{Colors.BOLD}{Colors.WHITE}")
        print(f"{'#':<3} {'📊':<2} {'Symbol':<6} {'Company':<28} {'💰Price':<10} {'🎯Ret%':<8} {'⚡Vol%':<8} {'📈SR':<6} {'🔥Pos%':<6} {'⚖️Risk':<6} {'📍52W':<4} {'🏢Sector':<15} {'Rec':<12}")
        print("-" * 150)
        print(f"{Colors.END}")
        
        # Display top 50 recommendations
        for i, rec in enumerate(recommendations[:50], 1):
            # Color coding based on recommendation
            if rec['Recommendation'] == 'STRONG_BUY':
                color = Colors.GREEN + Colors.BOLD
            elif rec['Recommendation'] == 'BUY':
                color = Colors.GREEN
            elif rec['Recommendation'] == 'HOLD':
                color = Colors.YELLOW
            elif rec['Recommendation'] == 'AVOID':
                color = Colors.MAGENTA
            else:  # STRONG_AVOID
                color = Colors.RED
            
            # Get emojis
            rec_emoji = RECOMMENDATION_EMOJIS.get(rec['Recommendation'], '❓')
            risk_emoji = RISK_EMOJIS.get(rec['Risk_Level'], '❓')
            pos_emoji = POSITION_EMOJIS.get(rec['Position_Indicator'], '❓')
            
            print(f"{color}{i:<3} {rec_emoji:<2} {rec['Symbol']:<6} {rec['Company']:<28} "
                  f"${rec['Price']:<9.2f} {rec['Expected_Return']:<7.1f} {rec['Volatility']:<7.1f} "
                  f"{rec['Sharpe_Ratio']:<5.2f} {rec['Range_Position']:<5.1f} {risk_emoji}{rec['Risk_Level']:<5} "
                  f"{pos_emoji:<4} {rec['Sector']:<15} {rec_emoji}{rec['Recommendation']:<11}{Colors.END}")
        
        # Footer with legend
        print()
        print(f"{Colors.BOLD}{Colors.CYAN}📊 LEGEND:{Colors.END}")
        print(f"🚀 STRONG_BUY | 💰 BUY | ⚖️ HOLD | ⚠️ AVOID | 🛑 STRONG_AVOID")
        print(f"🟢 LOW RISK | 🟡 MEDIUM RISK | 🔴 HIGH RISK")
        print(f"🔥 Near 52W High | ⚡ Mid-Range | ❄️ Near 52W Low")
        print()
        print(f"{Colors.YELLOW}📊 Total analyzed: {len(recommendations)} stocks | Showing top 50{Colors.END}")
        if self.save_data:
            print(f"{Colors.BLUE}💾 Data auto-saved to: {self.output_dir}{Colors.END}")

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
        print()
        
        cycle_count = 0
        
        try:
            while True:
                cycle_count += 1
                start_time = time.time()
                
                print(f"{Colors.BOLD}{Colors.BLUE}🔄 Analysis Cycle #{cycle_count}{Colors.END}")
                
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
                                # Display recommendations
                                flash = (cycle_count % 4 == 0)  # Flash every 4th cycle
                                self.display_recommendations_table(recommendations, flash)
                                
                                # Save data if enabled
                                self.save_analysis_data(recommendations)
                            else:
                                print(f"{Colors.RED}❌ No valid recommendations generated{Colors.END}")
                        else:
                            print(f"{Colors.RED}❌ No analysis results available{Colors.END}")
                    else:
                        print(f"{Colors.RED}❌ No valid stock data available{Colors.END}")
                else:
                    print(f"{Colors.RED}❌ Failed to fetch data from Yahoo Finance{Colors.END}")
                
                # Calculate sleep time
                elapsed_time = time.time() - start_time
                sleep_time = max(0, self.update_interval - elapsed_time)
                
                if sleep_time > 0:
                    print(f"{Colors.CYAN}⏰ Waiting {sleep_time:.1f}s for next update...{Colors.END}")
                    time.sleep(sleep_time)
                
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}🛑 Analysis stopped by user{Colors.END}")
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
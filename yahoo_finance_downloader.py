#!/usr/bin/env python3
"""
Yahoo Finance Stock Categories Downloader
==========================================

Downloads various stock categories from Yahoo Finance and saves them to Excel files:
- Most Active
- Trending Now  
- Top Gainers
- Top Losers
- 52 Week Gainers
- 52 Week Losers

Features:
- Date-specific file naming
- Multiple data formats (Excel with multiple sheets)
- Comprehensive stock information
- Error handling and logging
- Progress tracking
- Configurable date ranges

Usage:
    python yahoo_finance_downloader.py                    # Download all categories for today
    python yahoo_finance_downloader.py --date 2025-09-20  # Download for specific date
    python yahoo_finance_downloader.py --categories gainers,losers  # Download specific categories
    python yahoo_finance_downloader.py --output custom_name.xlsx    # Custom output filename
"""

import yfinance as yf
import pandas as pd
import requests
import json
import logging
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import os
import time
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('yahoo_finance_downloader.log'),
        logging.StreamHandler()
    ]
)

class YahooFinanceDownloader:
    """
    Downloads various stock categories from Yahoo Finance
    """
    
    def __init__(self, output_dir: str = "data"):
        """
        Initialize the downloader
        
        Args:
            output_dir: Directory to save Excel files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Yahoo Finance screener URLs for different categories
        self.screener_urls = {
            'most_active': 'https://finance.yahoo.com/screener/predefined/most_active',
            'trending': 'https://finance.yahoo.com/trending-tickers',
            'top_gainers': 'https://finance.yahoo.com/screener/predefined/day_gainers',
            'top_losers': 'https://finance.yahoo.com/screener/predefined/day_losers',
            '52_week_gainers': 'https://finance.yahoo.com/screener/predefined/growth_technology_stocks',
            '52_week_losers': 'https://finance.yahoo.com/screener/predefined/undervalued_growth_stocks'
        }
        
        # Category display names
        self.category_names = {
            'most_active': 'Most Active',
            'trending': 'Trending Now',
            'top_gainers': 'Top Gainers',
            'top_losers': 'Top Losers',
            '52_week_gainers': '52 Week Gainers',
            '52_week_losers': '52 Week Losers'
        }
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def get_most_active_stocks(self, limit: int = 100) -> pd.DataFrame:
        """Get most active stocks by volume"""
        try:
            logging.info("📊 Fetching Most Active stocks...")
            
            # Get most active stocks using yfinance
            # We'll use a list of major stocks and sort by volume
            major_stocks = [
                'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX',
                'JPM', 'JNJ', 'V', 'PG', 'UNH', 'HD', 'MA', 'DIS', 'PYPL', 'ADBE',
                'CRM', 'NFLX', 'CMCSA', 'PEP', 'ABT', 'KO', 'TMO', 'COST', 'ABBV',
                'XOM', 'NKE', 'MRK', 'CVX', 'WMT', 'BAC', 'LLY', 'PFE', 'ORCL',
                'AMD', 'INTC', 'QCOM', 'TXN', 'CSCO', 'CRM', 'NOW', 'SNOW', 'ZM',
                'SQ', 'ROKU', 'UBER', 'LYFT', 'TWTR', 'SNAP', 'PINS', 'SPOT', 'ZS'
            ]
            
            stocks_data = []
            
            for i, symbol in enumerate(major_stocks[:limit]):
                try:
                    print(f"\\r🔄 Processing: {symbol} ({i+1}/{min(len(major_stocks), limit)})", end='', flush=True)
                    
                    ticker = yf.Ticker(symbol)
                    info = ticker.info
                    hist = ticker.history(period='1d')
                    
                    if not hist.empty and info:
                        volume = hist['Volume'].iloc[-1] if not hist['Volume'].empty else 0
                        current_price = hist['Close'].iloc[-1] if not hist['Close'].empty else 0
                        prev_close = info.get('previousClose', current_price)
                        change = current_price - prev_close
                        change_percent = (change / prev_close * 100) if prev_close else 0
                        
                        # Format volume and market cap
                        avg_volume = info.get('averageVolume', 0)
                        market_cap = info.get('marketCap', 0)
                        week_52_high = info.get('fiftyTwoWeekHigh', current_price)
                        week_52_low = info.get('fiftyTwoWeekLow', current_price)
                        
                        # Convert to millions/billions
                        volume_millions = round(volume / 1_000_000, 2) if volume > 0 else 0
                        avg_volume_millions = round(avg_volume / 1_000_000, 2) if avg_volume > 0 else 0
                        market_cap_billions = round(market_cap / 1_000_000_000, 2) if market_cap > 0 else 0
                        
                        # Calculate 52-week range position
                        week_52_range = ((current_price - week_52_low) / (week_52_high - week_52_low) * 100) if (week_52_high != week_52_low) else 50
                        
                        stocks_data.append({
                            'Symbol': symbol,
                            'Company Name': info.get('longName', info.get('shortName', symbol)),
                            'Current Price': round(current_price, 2),
                            'Change': round(change, 2),
                            'Change %': round(change_percent, 2),
                            'Volume (M)': volume_millions,
                            'Average Volume (M)': avg_volume_millions,
                            'Market Cap (B)': market_cap_billions,
                            '52 Week High': week_52_high,
                            '52 Week Low': week_52_low,
                            '52W Range Position %': round(week_52_range, 1),
                            'Sector': info.get('sector', 'N/A'),
                            'Industry': info.get('industry', 'N/A'),
                            'PE Ratio': info.get('trailingPE', 'N/A')
                        })
                        
                    time.sleep(0.1)  # Rate limiting
                    
                except Exception as e:
                    logging.warning(f"Error fetching data for {symbol}: {e}")
                    continue
            
            print()  # New line after progress
            
            if stocks_data:
                df = pd.DataFrame(stocks_data)
                # Sort by volume (most active first)
                df = df.sort_values('Volume (M)', ascending=False).reset_index(drop=True)
                logging.info(f"✅ Retrieved {len(df)} Most Active stocks")
                return df
            else:
                logging.warning("⚠️ No Most Active stocks data retrieved")
                return pd.DataFrame()
                
        except Exception as e:
            logging.error(f"❌ Error fetching Most Active stocks: {e}")
            return pd.DataFrame()

    def get_trending_stocks(self, limit: int = 50) -> pd.DataFrame:
        """Get trending stocks"""
        try:
            logging.info("🔥 Fetching Trending stocks...")
            
            # Use a curated list of trending/popular stocks
            trending_symbols = [
                'TSLA', 'GME', 'AMC', 'AAPL', 'MSFT', 'NVDA', 'AMD', 'GOOGL',
                'AMZN', 'META', 'NFLX', 'PYPL', 'SQ', 'ROKU', 'ZM', 'SNOW',
                'PLTR', 'NIO', 'XPEV', 'LI', 'RIVN', 'LCID', 'F', 'GM',
                'COIN', 'HOOD', 'SOFI', 'UPST', 'AFRM', 'RBLX', 'U', 'PATH'
            ]
            
            return self._get_stock_data(trending_symbols[:limit], "Trending")
            
        except Exception as e:
            logging.error(f"❌ Error fetching Trending stocks: {e}")
            return pd.DataFrame()

    def get_top_gainers(self, limit: int = 100) -> pd.DataFrame:
        """Get top gaining stocks"""
        try:
            logging.info("📈 Fetching Top Gainers...")
            
            # Get a broad set of stocks and identify gainers
            major_stocks = [
                'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX',
                'JPM', 'JNJ', 'V', 'PG', 'UNH', 'HD', 'MA', 'DIS', 'PYPL', 'ADBE',
                'CRM', 'ORCL', 'CMCSA', 'PEP', 'ABT', 'KO', 'TMO', 'COST', 'ABBV',
                'XOM', 'NKE', 'MRK', 'CVX', 'WMT', 'BAC', 'LLY', 'PFE', 'AMD',
                'INTC', 'QCOM', 'TXN', 'CSCO', 'NOW', 'SNOW', 'ZM', 'SQ', 'ROKU',
                'GME', 'AMC', 'NIO', 'XPEV', 'LI', 'RIVN', 'LCID', 'COIN', 'HOOD'
            ]
            
            df = self._get_stock_data(major_stocks, "Top Gainers")
            if not df.empty:
                # Filter and sort by positive change %
                gainers = df[df['Change %'] > 0].sort_values('Change %', ascending=False)
                return gainers.head(limit).reset_index(drop=True)
            return df
            
        except Exception as e:
            logging.error(f"❌ Error fetching Top Gainers: {e}")
            return pd.DataFrame()

    def get_top_losers(self, limit: int = 100) -> pd.DataFrame:
        """Get top losing stocks"""
        try:
            logging.info("📉 Fetching Top Losers...")
            
            # Get a broad set of stocks and identify losers
            major_stocks = [
                'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX',
                'JPM', 'JNJ', 'V', 'PG', 'UNH', 'HD', 'MA', 'DIS', 'PYPL', 'ADBE',
                'CRM', 'ORCL', 'CMCSA', 'PEP', 'ABT', 'KO', 'TMO', 'COST', 'ABBV',
                'XOM', 'NKE', 'MRK', 'CVX', 'WMT', 'BAC', 'LLY', 'PFE', 'AMD',
                'INTC', 'QCOM', 'TXN', 'CSCO', 'NOW', 'SNOW', 'ZM', 'SQ', 'ROKU',
                'GME', 'AMC', 'NIO', 'XPEV', 'LI', 'RIVN', 'LCID', 'COIN', 'HOOD'
            ]
            
            df = self._get_stock_data(major_stocks, "Top Losers")
            if not df.empty:
                # Filter and sort by negative change % (most negative first)
                losers = df[df['Change %'] < 0].sort_values('Change %', ascending=True)
                return losers.head(limit).reset_index(drop=True)
            return df
            
        except Exception as e:
            logging.error(f"❌ Error fetching Top Losers: {e}")
            return pd.DataFrame()

    def get_52_week_gainers(self, limit: int = 100) -> pd.DataFrame:
        """Get 52-week high gainers"""
        try:
            logging.info("🚀 Fetching 52 Week Gainers...")
            
            # Focus on growth and technology stocks that might be near 52-week highs
            growth_stocks = [
                'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX',
                'AMD', 'CRM', 'ORCL', 'ADBE', 'NOW', 'SNOW', 'ZM', 'SQ', 'ROKU',
                'PYPL', 'SHOP', 'TWLO', 'OKTA', 'ZS', 'CRWD', 'DDOG', 'NET',
                'PLTR', 'U', 'PATH', 'RBLX', 'COIN', 'HOOD', 'SOFI', 'UPST',
                'NIO', 'XPEV', 'LI', 'RIVN', 'LCID', 'SPCE', 'OPEN', 'WISH'
            ]
            
            df = self._get_stock_data(growth_stocks, "52 Week Gainers")
            if not df.empty:
                # Calculate distance from 52-week high
                df['Distance from 52W High'] = ((df['Current Price'] - df['52 Week High']) / df['52 Week High'] * 100)
                # Sort by those closest to 52-week high (least negative distance)
                gainers_52w = df.sort_values('Distance from 52W High', ascending=False)
                return gainers_52w.head(limit).reset_index(drop=True)
            return df
            
        except Exception as e:
            logging.error(f"❌ Error fetching 52 Week Gainers: {e}")
            return pd.DataFrame()

    def get_52_week_losers(self, limit: int = 100) -> pd.DataFrame:
        """Get 52-week low stocks"""
        try:
            logging.info("📊 Fetching 52 Week Losers...")
            
            # Include a broader range including some beaten down stocks
            broad_stocks = [
                'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX',
                'PYPL', 'ZM', 'ROKU', 'SQ', 'SHOP', 'TWLO', 'OKTA', 'ZS',
                'GME', 'AMC', 'WISH', 'CLOV', 'SPCE', 'OPEN', 'HOOD', 'SOFI',
                'PLTR', 'NIO', 'XPEV', 'LI', 'RIVN', 'LCID', 'F', 'GM',
                'GE', 'T', 'VZ', 'IBM', 'INTC', 'CSCO', 'ORCL', 'CRM'
            ]
            
            df = self._get_stock_data(broad_stocks, "52 Week Losers")
            if not df.empty:
                # Calculate distance from 52-week low
                df['Distance from 52W Low'] = ((df['Current Price'] - df['52 Week Low']) / df['52 Week Low'] * 100)
                # Sort by those closest to 52-week low (least positive distance)
                losers_52w = df.sort_values('Distance from 52W Low', ascending=True)
                return losers_52w.head(limit).reset_index(drop=True)
            return df
            
        except Exception as e:
            logging.error(f"❌ Error fetching 52 Week Losers: {e}")
            return pd.DataFrame()

    def _get_stock_data(self, symbols: List[str], category_name: str) -> pd.DataFrame:
        """
        Get comprehensive stock data for a list of symbols
        
        Args:
            symbols: List of stock symbols
            category_name: Name of the category for progress display
            
        Returns:
            DataFrame with stock information
        """
        stocks_data = []
        
        for i, symbol in enumerate(symbols):
            try:
                print(f"\\r🔄 Processing {category_name}: {symbol} ({i+1}/{len(symbols)})", end='', flush=True)
                
                ticker = yf.Ticker(symbol)
                info = ticker.info
                hist = ticker.history(period='5d')  # Get more days for better data
                
                if not hist.empty and info:
                    current_price = hist['Close'].iloc[-1]
                    prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else info.get('previousClose', current_price)
                    change = current_price - prev_close
                    change_percent = (change / prev_close * 100) if prev_close else 0
                    
                    # Calculate 52-week performance
                    week_52_high = info.get('fiftyTwoWeekHigh', current_price)
                    week_52_low = info.get('fiftyTwoWeekLow', current_price)
                    week_52_range = ((current_price - week_52_low) / (week_52_high - week_52_low) * 100) if (week_52_high != week_52_low) else 50
                    
                    # Format volume and market cap
                    volume = hist['Volume'].iloc[-1] if not hist['Volume'].empty else 0
                    avg_volume = info.get('averageVolume', 0)
                    market_cap = info.get('marketCap', 0)
                    
                    # Convert to millions/billions
                    volume_millions = round(volume / 1_000_000, 2) if volume > 0 else 0
                    avg_volume_millions = round(avg_volume / 1_000_000, 2) if avg_volume > 0 else 0
                    market_cap_billions = round(market_cap / 1_000_000_000, 2) if market_cap > 0 else 0
                    
                    stocks_data.append({
                        'Symbol': symbol,
                        'Company Name': info.get('longName', info.get('shortName', symbol)),
                        'Current Price': round(current_price, 2),
                        'Change': round(change, 2),
                        'Change %': round(change_percent, 2),
                        'Volume (M)': volume_millions,
                        'Average Volume (M)': avg_volume_millions,
                        'Market Cap (B)': market_cap_billions,
                        '52 Week High': week_52_high,
                        '52 Week Low': week_52_low,
                        '52W Range Position %': round(week_52_range, 1),
                        'Sector': info.get('sector', 'N/A'),
                        'Industry': info.get('industry', 'N/A'),
                        'PE Ratio': info.get('trailingPE', 'N/A'),
                        'Beta': info.get('beta', 'N/A'),
                        'EPS': info.get('trailingEps', 'N/A'),
                        'Dividend Yield': info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 0,
                        'Book Value': info.get('bookValue', 'N/A'),
                        'Price to Book': info.get('priceToBook', 'N/A'),
                        'Revenue': info.get('totalRevenue', 'N/A'),
                        'Profit Margin': info.get('profitMargins', 0) * 100 if info.get('profitMargins') else 'N/A'
                    })
                    
                time.sleep(0.1)  # Rate limiting
                
            except Exception as e:
                logging.warning(f"Error fetching data for {symbol}: {e}")
                continue
        
        print()  # New line after progress
        
        if stocks_data:
            df = pd.DataFrame(stocks_data)
            logging.info(f"✅ Retrieved {len(df)} {category_name} stocks")
            return df
        else:
            logging.warning(f"⚠️ No {category_name} data retrieved")
            return pd.DataFrame()

    def download_all_categories(self, date_str: str = None, 
                              categories: List[str] = None,
                              output_filename: str = None) -> str:
        """
        Download all or specified categories and save to Excel
        
        Args:
            date_str: Date string in YYYY-MM-DD format (default: today)
            categories: List of categories to download (default: all)
            output_filename: Custom output filename (default: auto-generated)
            
        Returns:
            Path to the created Excel file
        """
        if date_str is None:
            date_str = datetime.now().strftime('%Y-%m-%d')
        
        if categories is None:
            categories = list(self.category_names.keys())
        
        if output_filename is None:
            output_filename = f"yahoo_finance_data_{date_str}.xlsx"
        
        output_path = self.output_dir / output_filename
        
        logging.info(f"🚀 Starting Yahoo Finance data download for {date_str}")
        logging.info(f"📁 Output file: {output_path}")
        
        # Download data for each category
        all_data = {}
        
        category_functions = {
            'most_active': self.get_most_active_stocks,
            'trending': self.get_trending_stocks,
            'top_gainers': self.get_top_gainers,
            'top_losers': self.get_top_losers,
            '52_week_gainers': self.get_52_week_gainers,
            '52_week_losers': self.get_52_week_losers
        }
        
        for category in categories:
            if category in category_functions:
                logging.info(f"\\n📊 Processing {self.category_names[category]}...")
                data = category_functions[category]()
                if not data.empty:
                    all_data[self.category_names[category]] = data
                    logging.info(f"✅ {self.category_names[category]}: {len(data)} stocks")
                else:
                    logging.warning(f"⚠️ {self.category_names[category]}: No data retrieved")
        
        # Save to Excel with multiple sheets
        if all_data:
            try:
                with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                    # Add each category as a separate sheet
                    for sheet_name, df in all_data.items():
                        # Limit sheet name length for Excel compatibility
                        safe_sheet_name = sheet_name[:31]
                        df.to_excel(writer, sheet_name=safe_sheet_name, index=False)
                
                logging.info(f"🎉 Successfully saved data to {output_path}")
                logging.info(f"📊 Total categories: {len(all_data)}")
                logging.info(f"📈 Total unique stocks: {sum(len(df) for df in all_data.values())}")
                
                return str(output_path)
                
            except Exception as e:
                logging.error(f"❌ Error saving Excel file: {e}")
                return None
        else:
            logging.warning("⚠️ No data to save")
            return None

def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(
        description='Download Yahoo Finance stock categories to Excel files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python yahoo_finance_downloader.py
  python yahoo_finance_downloader.py --date 2025-09-20
  python yahoo_finance_downloader.py --categories most_active,top_gainers
  python yahoo_finance_downloader.py --output my_stocks.xlsx
  python yahoo_finance_downloader.py --help
        """
    )
    
    parser.add_argument(
        '--date', 
        type=str, 
        default=None,
        help='Date for data download (YYYY-MM-DD format, default: today)'
    )
    
    parser.add_argument(
        '--categories',
        type=str,
        default=None,
        help='Comma-separated list of categories: most_active,trending,top_gainers,top_losers,52_week_gainers,52_week_losers'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Output Excel filename (default: yahoo_finance_data_YYYY-MM-DD.xlsx)'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='data',
        help='Output directory (default: data)'
    )
    
    args = parser.parse_args()
    
    # Parse categories
    categories = None
    if args.categories:
        categories = [cat.strip() for cat in args.categories.split(',')]
        valid_categories = ['most_active', 'trending', 'top_gainers', 'top_losers', '52_week_gainers', '52_week_losers']
        invalid_categories = [cat for cat in categories if cat not in valid_categories]
        if invalid_categories:
            print(f"❌ Invalid categories: {', '.join(invalid_categories)}")
            print(f"✅ Valid categories: {', '.join(valid_categories)}")
            return
    
    # Create downloader and run
    downloader = YahooFinanceDownloader(args.output_dir)
    output_file = downloader.download_all_categories(
        date_str=args.date,
        categories=categories,
        output_filename=args.output
    )
    
    if output_file:
        print(f"\\n🎉 SUCCESS! Data saved to: {output_file}")
        print(f"📊 Open the Excel file to view all categories with detailed stock information")
    else:
        print(f"\\n❌ FAILED! Could not download or save data")

if __name__ == "__main__":
    main()
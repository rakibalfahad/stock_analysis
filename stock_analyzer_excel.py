#!/usr/bin/env python3
"""
Stock Analysis to Excel Exporter

Extends the stock_analyzer.py functionality to export analysis data to Excel format.
This script analyzes stocks and saves the results as both PNG charts and Excel spreadsheets.

Usage: python stock_analyzer_excel.py input_file.xlsx [--output results.xlsx]
"""

import os
import sys
import pandas as pd
import yfinance as yf
import numpy as np
from datetime import datetime
import argparse
from typing import Dict, List, Tuple, Optional

def load_symbols_from_file(file_path: str, sheet_name: Optional[str] = None) -> List[str]:
    """Load stock symbols from Excel or CSV file"""
    print(f"📊 Loading stock symbols from {file_path}...")
    
    # Get file extension
    file_ext = os.path.splitext(file_path)[1].lower()
    
    try:
        if file_ext in ['.xlsx', '.xls']:
            # Load Excel file
            if sheet_name:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                print(f"   🎯 Using specified sheet: {sheet_name}")
            else:
                # Get all sheet names
                xl_file = pd.ExcelFile(file_path)
                sheet_names = xl_file.sheet_names
                print(f"   📋 Available sheets: {', '.join(sheet_names)}")
                
                # Use first sheet
                sheet_name = sheet_names[0]
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                print(f"   🎯 Using first sheet: {sheet_name}")
                
        elif file_ext == '.csv':
            df = pd.read_csv(file_path)
            print(f"   📋 Loaded CSV file")
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
        
        print(f"   📊 Loaded data: {len(df)} rows, {len(df.columns)} columns")
        
        # Find symbol column
        symbol_columns = ['Symbol', 'Symbols', 'Stock', 'Stocks', 'Ticker', 'Tickers']
        symbol_col = None
        
        for col in symbol_columns:
            if col in df.columns:
                symbol_col = col
                break
        
        if symbol_col is None:
            # Try case-insensitive search
            for col in df.columns:
                if col.lower() in [s.lower() for s in symbol_columns]:
                    symbol_col = col
                    break
        
        if symbol_col is None:
            # Use first column if no standard name found
            symbol_col = df.columns[0]
            print(f"   ⚠️  Using first column as symbols: {symbol_col}")
        else:
            print(f"   ✅ Found symbol column: '{symbol_col}'")
        
        # Extract symbols
        symbols = df[symbol_col].dropna().astype(str).str.strip().str.upper().tolist()
        symbols = [s for s in symbols if s and s != 'NAN']  # Remove empty and NaN
        
        print(f"   ✅ Successfully loaded {len(symbols)} stock symbols: {', '.join(symbols[:10])}")
        if len(symbols) > 10:
            print(f"      ... and {len(symbols) - 10} more")
        
        return symbols
        
    except Exception as e:
        print(f"❌ Error loading symbols from {file_path}: {e}")
        return []

def fetch_stock_data(symbols: List[str], period: str = '1y') -> Dict:
    """Fetch stock data and calculate metrics"""
    print(f"🧮 Fetching market data for {len(symbols)} stocks...")
    
    results = {
        'symbols': [],
        'current_prices': [],
        'expected_returns': [],
        'volatilities': [],
        'sharpe_ratios': [],
        'week52_highs': [],
        'week52_lows': [],
        'week52_positions': [],
        'market_caps': [],
        'company_names': [],
        'sectors': [],
        'errors': []
    }
    
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            
            # Get historical data for risk/return calculation
            hist = ticker.history(period=period)
            if hist.empty:
                results['errors'].append(f"{symbol}: No historical data")
                continue
            
            # Get current price
            current_price = float(hist['Close'].iloc[-1])
            
            # Calculate returns
            returns = hist['Close'].pct_change().dropna()
            if len(returns) < 10:  # Need minimum data points
                results['errors'].append(f"{symbol}: Insufficient data")
                continue
            
            # Calculate metrics
            daily_return = returns.mean()
            volatility = returns.std()
            annual_return = ((1 + daily_return) ** 252) - 1  # Annualized
            annual_volatility = volatility * np.sqrt(252)
            
            # Sharpe ratio (assuming 0% risk-free rate)
            sharpe_ratio = annual_return / annual_volatility if annual_volatility > 0 else 0
            
            # 52-week high/low
            week52_high = float(hist['High'].max())
            week52_low = float(hist['Low'].min())
            week52_position = ((current_price - week52_low) / (week52_high - week52_low)) * 100
            
            # Get company info
            info = ticker.info
            company_name = info.get('longName', symbol)
            sector = info.get('sector', 'Unknown')
            market_cap = info.get('marketCap', 0)
            
            # Store results
            results['symbols'].append(symbol)
            results['current_prices'].append(current_price)
            results['expected_returns'].append(annual_return * 100)  # Convert to percentage
            results['volatilities'].append(annual_volatility * 100)  # Convert to percentage
            results['sharpe_ratios'].append(sharpe_ratio)
            results['week52_highs'].append(week52_high)
            results['week52_lows'].append(week52_low)
            results['week52_positions'].append(week52_position)
            results['market_caps'].append(market_cap)
            results['company_names'].append(company_name)
            results['sectors'].append(sector)
            
        except Exception as e:
            results['errors'].append(f"{symbol}: {str(e)}")
    
    print(f"✅ Successfully analyzed {len(results['symbols'])}/{len(symbols)} stocks")
    if results['errors']:
        print(f"⚠️  Errors encountered: {len(results['errors'])}")
        for error in results['errors'][:5]:  # Show first 5 errors
            print(f"   - {error}")
        if len(results['errors']) > 5:
            print(f"   ... and {len(results['errors']) - 5} more")
    
    return results

def create_excel_report(data: Dict, output_file: str) -> bool:
    """Create comprehensive Excel report"""
    print(f"📊 Creating Excel report: {output_file}")
    
    try:
        # Create main DataFrame
        df = pd.DataFrame({
            'Symbol': data['symbols'],
            'Company Name': data['company_names'],
            'Sector': data['sectors'],
            'Current Price': data['current_prices'],
            'Expected Return (%)': data['expected_returns'],
            'Volatility (%)': data['volatilities'],
            'Sharpe Ratio': data['sharpe_ratios'],
            '52W High': data['week52_highs'],
            '52W Low': data['week52_lows'],
            '52W Position (%)': data['week52_positions'],
            'Market Cap': data['market_caps']
        })
        
        # Round numeric columns
        numeric_columns = ['Current Price', 'Expected Return (%)', 'Volatility (%)', 
                          'Sharpe Ratio', '52W High', '52W Low', '52W Position (%)']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = df[col].round(2)
        
        # Add position indicators
        def get_position_indicator(pos):
            if pos > 80:
                return "🔥 Near High"
            elif pos > 50:
                return "⚡ Mid-Range"
            else:
                return "❄️ Near Low"
        
        df['52W Position Status'] = df['52W Position (%)'].apply(get_position_indicator)
        
        # Create Excel writer
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Main analysis sheet
            df.to_excel(writer, sheet_name='Stock Analysis', index=False)
            
            # Summary statistics sheet
            summary_stats = {
                'Metric': [
                    'Total Stocks Analyzed',
                    'Best Expected Return',
                    'Best Sharpe Ratio', 
                    'Lowest Risk (Volatility)',
                    'Near 52W High (>80%)',
                    'Near 52W Low (<20%)',
                    'Average Expected Return',
                    'Average Volatility',
                    'Average Sharpe Ratio'
                ],
                'Value': [
                    len(df),
                    f"{df['Expected Return (%)'].max():.1f}% ({df.loc[df['Expected Return (%)'].idxmax(), 'Symbol']})",
                    f"{df['Sharpe Ratio'].max():.2f} ({df.loc[df['Sharpe Ratio'].idxmax(), 'Symbol']})",
                    f"{df['Volatility (%)'].min():.1f}% ({df.loc[df['Volatility (%)'].idxmin(), 'Symbol']})",
                    len(df[df['52W Position (%)'] > 80]),
                    len(df[df['52W Position (%)'] < 20]),
                    f"{df['Expected Return (%)'].mean():.1f}%",
                    f"{df['Volatility (%)'].mean():.1f}%",
                    f"{df['Sharpe Ratio'].mean():.2f}"
                ]
            }
            
            summary_df = pd.DataFrame(summary_stats)
            summary_df.to_excel(writer, sheet_name='Summary Statistics', index=False)
            
            # Sector analysis
            if 'Sector' in df.columns:
                sector_analysis = df.groupby('Sector').agg({
                    'Symbol': 'count',
                    'Expected Return (%)': 'mean',
                    'Volatility (%)': 'mean',
                    'Sharpe Ratio': 'mean'
                }).round(2)
                sector_analysis.rename(columns={'Symbol': 'Count'})
                sector_analysis.to_excel(writer, sheet_name='Sector Analysis')
            
            # Top performers
            top_performers = df.nlargest(10, 'Expected Return (%)')[['Symbol', 'Company Name', 'Expected Return (%)', 'Sharpe Ratio', '52W Position Status']]
            top_performers.to_excel(writer, sheet_name='Top Performers', index=False)
            
            # High risk stocks
            high_risk = df.nlargest(10, 'Volatility (%)')[['Symbol', 'Company Name', 'Volatility (%)', 'Expected Return (%)', '52W Position Status']]
            high_risk.to_excel(writer, sheet_name='High Risk Stocks', index=False)
            
            # Near 52W highs
            near_highs = df[df['52W Position (%)'] > 80].sort_values('52W Position (%)', ascending=False)[['Symbol', 'Company Name', '52W Position (%)', 'Expected Return (%)']]
            near_highs.to_excel(writer, sheet_name='Near 52W Highs', index=False)
            
            # Errors sheet (if any)
            if data['errors']:
                error_df = pd.DataFrame({'Errors': data['errors']})
                error_df.to_excel(writer, sheet_name='Errors', index=False)
        
        print(f"✅ Excel report saved successfully: {output_file}")
        print(f"📊 Contains {len(df)} stocks across {len(df['Sector'].unique())} sectors")
        return True
        
    except Exception as e:
        print(f"❌ Error creating Excel report: {e}")
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Stock Analysis to Excel Exporter')
    parser.add_argument('input_file', help='Input Excel or CSV file with stock symbols')
    parser.add_argument('--output', '-o', default='stock_analysis_results.xlsx', 
                       help='Output Excel file name (default: stock_analysis_results.xlsx)')
    parser.add_argument('--sheet', '-s', help='Excel sheet name to read')
    parser.add_argument('--period', default='1y', 
                       help='Analysis period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y (default: 1y)')
    
    args = parser.parse_args()
    
    print(f"🚀 Stock Analysis to Excel Exporter")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Input: {args.input_file}")
    print(f"📊 Output: {args.output}")
    print("="*60)
    
    # Check if input file exists
    if not os.path.exists(args.input_file):
        print(f"❌ Error: Input file '{args.input_file}' not found")
        return 1
    
    # Load symbols
    symbols = load_symbols_from_file(args.input_file, args.sheet)
    if not symbols:
        print("❌ No symbols loaded. Exiting.")
        return 1
    
    # Fetch data and analyze
    data = fetch_stock_data(symbols, args.period)
    if not data['symbols']:
        print("❌ No valid stock data obtained. Exiting.")
        return 1
    
    # Create Excel report
    success = create_excel_report(data, args.output)
    if not success:
        return 1
    
    print("\n" + "="*60)
    print(f"🎉 Analysis complete!")
    print(f"📊 Excel report: {args.output}")
    print(f"📈 Analyzed: {len(data['symbols'])} stocks")
    print("💡 Open the Excel file to view detailed analysis across multiple sheets")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
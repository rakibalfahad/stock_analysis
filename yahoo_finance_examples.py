#!/usr/bin/env python3
"""
Yahoo Finance Downloader - Usage Examples
==========================================

This script demonstrates various ways to use the Yahoo Finance downloader.
"""

import subprocess
import sys
from datetime import datetime, timedelta
import os

def run_command(cmd, description):
    """Run a command and display the description"""
    print(f"\n{'='*60}")
    print(f"🔄 {description}")
    print(f"📝 Command: {cmd}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ SUCCESS!")
            print(result.stdout)
        else:
            print("❌ ERROR!")
            print(result.stderr)
    except Exception as e:
        print(f"❌ Exception: {e}")

def main():
    """Demonstrate various usage scenarios"""
    
    print("🚀 Yahoo Finance Downloader - Usage Examples")
    print("=" * 60)
    
    # Ensure we're in the right directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    python_cmd = "/home/ralfahad/projects/stock_env/bin/python"
    
    examples = [
        {
            "cmd": f"{python_cmd} yahoo_finance_downloader.py --help",
            "desc": "Show help and available options"
        },
        {
            "cmd": f"{python_cmd} yahoo_finance_downloader.py --categories most_active --output most_active_today.xlsx",
            "desc": "Download only Most Active stocks for today"
        },
        {
            "cmd": f"{python_cmd} yahoo_finance_downloader.py --categories top_gainers,top_losers --date 2025-09-23",
            "desc": "Download Gainers and Losers for a specific date"
        },
        {
            "cmd": f"{python_cmd} yahoo_finance_downloader.py --categories trending --output trending_stocks.xlsx",
            "desc": "Download only Trending stocks"
        },
        {
            "cmd": f"{python_cmd} yahoo_finance_downloader.py --categories 52_week_gainers,52_week_losers",
            "desc": "Download 52-week Gainers and Losers"
        }
    ]
    
    print("🎯 Available Categories:")
    print("  • most_active - Stocks with highest trading volume")
    print("  • trending - Currently trending/popular stocks")
    print("  • top_gainers - Biggest daily percentage gainers")
    print("  • top_losers - Biggest daily percentage losers")
    print("  • 52_week_gainers - Stocks near their 52-week highs")
    print("  • 52_week_losers - Stocks near their 52-week lows")
    
    print(f"\n📁 Output Directory: data/")
    print(f"📊 Output Format: Excel (.xlsx) with multiple sheets")
    print(f"📅 Default Date: Today ({datetime.now().strftime('%Y-%m-%d')})")
    
    # Run a simple example
    run_command(examples[0]["cmd"], examples[0]["desc"])
    
    print("\n🎯 Other Usage Examples:")
    for example in examples[1:]:
        print(f"\n📝 {example['desc']}")
        print(f"   {example['cmd']}")
    
    print(f"\n{'='*60}")
    print("🎉 Ready to use! Choose any command above to download stock data.")
    print("📊 Each Excel file will contain detailed information including:")
    print("   • Company name, symbol, current price")
    print("   • Daily change and percentage change")
    print("   • Volume, market cap, sector, industry")
    print("   • PE ratio, 52-week high/low, beta")
    print("   • EPS, dividend yield, profit margin")
    print("   • And much more!")

if __name__ == "__main__":
    main()
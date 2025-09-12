#!/usr/bin/env python3
"""
Investment Portfolio Optimizer - Main Entry Point

Clean, modular investment portfolio optimization system using Modern Portfolio Theory.

Usage:
    python main.py --plot                    # Run with visualization
    python main.py --monitor                 # Run in monitoring mode
    python main.py --quick-monitor           # 15-minute monitoring
    python main.py --cleanup 5               # Clean old files, keep 5 latest
    python main.py --help                    # Show all options

Author: Investment Management System
Version: 2.0.0 (Modular)
Date: September 2025
"""

import sys
import os
import argparse
import time
import logging
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.portfolio.optimizer import InvestmentOptimizer
from src.portfolio.short_trading import ShortTradingManager
from src.portfolio.stock_comparator import StockComparator
from src.visualization.dashboard import PortfolioVisualizer
from src.utils.constants import (
    DEFAULT_TARGET_RETURN, DEFAULT_RISK_PER_TRADE, 
    DEFAULT_ATR_MULTIPLIER, EMOJIS, CONFIG_FILE
)
from src.utils.config import setup_logging

def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser"""
    parser = argparse.ArgumentParser(
        description='Investment Portfolio Optimizer - Modular Version with dynamic plotting and monitoring',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --plot                    # Run optimization with intelligent filtering & dashboard
  python main.py --monitor --plot          # Monitor with visualization & filtering 
  python main.py --quick-monitor           # 15-minute monitoring mode with filtering
  python main.py --no-filter --plot        # Run without filtering (analyze all stocks)
  python main.py --filtering-mode conservative  # Conservative risk filtering
  python main.py --filtering-mode aggressive    # More aggressive filtering (higher risk tolerance)
  python main.py --compare AAPL MSFT       # Compare two stocks with balanced strategy
  python main.py --compare TSLA NVDA --strategy growth  # Compare with growth-focused weighting
  python main.py --compare JNJ PG --strategy income     # Compare dividend stocks
  python main.py --short-trading           # Short trading mode with P&L alerts (uses short_trading.txt)
  python main.py --short-trading --interval 30      # Short trading with 30-sec updates
  python main.py --cleanup 5               # Keep 5 latest dashboard files
  python main.py --keep-timestamp --plot   # Create timestamped files

Intelligent Stock Filtering:
  The system automatically analyzes all stocks in investments.txt and determines optimal
  P/E ratio and volatility thresholds based on market conditions. It then recommends only
  the best stocks based on comprehensive financial metrics. Use --filtering-mode to adjust
  risk tolerance: conservative (low risk), moderate (balanced), aggressive (higher risk).

Stock Comparison:
  Compare any two stocks using normalized metrics and strategy-based weighting. The system
  evaluates valuation, profitability, growth, financial health, risk, and dividends to
  provide a clear recommendation. Choose from investment strategies: growth (focuses on
  growth metrics), value (emphasizes valuation), income (prioritizes dividends), stability
  (emphasizes financial health), or balanced (equal weighting).
        """
    )
    
    # Configuration options
    parser.add_argument('--config', default=CONFIG_FILE,
                       help=f'Configuration file path (default: {CONFIG_FILE})')
    
    # Monitoring options
    parser.add_argument('--monitor', action='store_true',
                       help='Run in monitoring mode (periodic updates)')
    parser.add_argument('--interval', type=int, default=3600, 
                       help='Seconds between updates in monitoring mode (default: 3600 = 1 hour)')
    parser.add_argument('--quick-monitor', action='store_true',
                       help='Run in quick monitoring mode (15-minute intervals)')
    parser.add_argument('--short-trading', action='store_true',
                       help='Enable short trading mode with real-time P&L monitoring and alerts (uses separate short_trading.txt config file)')
    parser.add_argument('--compare', nargs=2, metavar=('STOCK1', 'STOCK2'),
                       help='Compare two stocks and get recommendation (e.g., --compare AAPL MSFT)')
    parser.add_argument('--strategy', choices=['growth', 'value', 'income', 'stability', 'balanced'],
                       default='balanced', help='Investment strategy for comparison weighting (default: balanced)')
    
    # Visualization options
    parser.add_argument('--plot', action='store_true',
                       help='Enable dynamic plotting and visualization')
    parser.add_argument('--no-save', action='store_true', 
                       help='Do not save dashboard to file')
    parser.add_argument('--keep-timestamp', action='store_true',
                       help='Keep timestamp in filename (creates new file each time)')
    
    # File management
    parser.add_argument('--cleanup', type=int, metavar='N',
                       help='Clean up old dashboard files, keep N latest (0 to delete all timestamped files)')
    
    # Portfolio parameters
    parser.add_argument('--target-return', type=float, default=DEFAULT_TARGET_RETURN,
                       help=f'Target annual return (default: {DEFAULT_TARGET_RETURN} = {DEFAULT_TARGET_RETURN*100:.0f}%%)')
    parser.add_argument('--risk-per-trade', type=float, default=DEFAULT_RISK_PER_TRADE,
                       help=f'Risk per trade as fraction of capital (default: {DEFAULT_RISK_PER_TRADE} = {DEFAULT_RISK_PER_TRADE*100:.0f}%%)')
    parser.add_argument('--atr-multiplier', type=float, default=DEFAULT_ATR_MULTIPLIER,
                       help=f'ATR multiplier for stop-loss (default: {DEFAULT_ATR_MULTIPLIER})')
    parser.add_argument('--no-filter', action='store_true',
                       help='Disable intelligent stock filtering (analyze all stocks from config)')
    
    # Filtering criteria (advanced)
    parser.add_argument('--min-market-cap', type=float, default=1.0,
                       help='Minimum market cap in billions (default: 1.0B)')
    parser.add_argument('--filtering-mode', choices=['conservative', 'moderate', 'aggressive'], 
                       default='moderate', help='Risk tolerance for stock filtering (default: moderate)')
    
    # Logging
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
                       default='INFO', help='Set logging level')
    
    return parser

def run_monitoring_mode(optimizer: InvestmentOptimizer, 
                       visualizer: PortfolioVisualizer, 
                       interval: int,
                       keep_timestamp: bool = False) -> None:
    """Run the optimizer in monitoring mode"""
    print(f"\n{EMOJIS['rocket']} Starting monitoring mode...")
    print(f"{EMOJIS['calendar']} Update interval: {interval} seconds" if interval < 60 else f"{EMOJIS['calendar']} Update interval: {interval//60} minutes")
    
    if visualizer.enable_plotting:
        time_str = f"{interval} seconds" if interval < 60 else f"{interval//60} minutes"
        print(f"{EMOJIS['chart']} Dynamic plotting enabled - Dashboard will update every {time_str}")
    
    try:
        iteration = 0
        while True:
            iteration += 1
            print(f"\n{'='*50}")
            print(f"{EMOJIS['magnifying_glass']} Monitoring Iteration #{iteration}")
            print(f"{EMOJIS['calendar']} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*50}")
            
            # Run optimization
            success = optimizer.run_optimization()
            
            if success and visualizer.enable_plotting:
                # Update visualization
                visualizer.update_all_plots(optimizer)
                
                # Save dashboard with timestamp in monitoring mode
                visualizer.save_plots(keep_timestamp=keep_timestamp)
            
            if not success:
                print(f"{EMOJIS['warning']} Optimization failed, will retry next cycle")
            
            time_str = f"{interval} seconds" if interval < 60 else f"{interval//60} minutes"
            print(f"\n{EMOJIS['calendar']} Next update in {time_str}...")
            print(f"{EMOJIS['pause']} Press Ctrl+C to stop monitoring")
            
            # Sleep until next iteration
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print(f"\n\n{EMOJIS['check']} Monitoring stopped by user")
    except Exception as e:
        logging.error(f"Error in monitoring mode: {e}")
        print(f"{EMOJIS['warning']} Monitoring stopped due to error: {e}")

def main() -> int:
    """Main entry point"""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    
    # Handle cleanup first if requested
    if args.cleanup is not None:
        print(f"{EMOJIS['folder']} Cleaning up old dashboard files...")
        visualizer = PortfolioVisualizer()
        visualizer.cleanup_old_dashboards(keep_latest=args.cleanup)
        return 0
    
    try:
        # Initialize components
        print(f"{EMOJIS['computer']} Initializing Investment Portfolio Optimizer v2.0...")
        
        optimizer = InvestmentOptimizer(
            config_file=args.config,
            target_return=args.target_return,
            risk_per_trade=args.risk_per_trade,
            atr_multiplier=args.atr_multiplier,
            enable_filtering=not args.no_filter,
            filtering_mode=args.filtering_mode
        )
        
        # Update basic filtering criteria if provided
        if not args.no_filter and hasattr(optimizer, 'stock_filter') and optimizer.stock_filter:
            optimizer.stock_filter.min_market_cap = args.min_market_cap * 1e9  # Convert to actual value
        
        visualizer = PortfolioVisualizer(enable_plotting=args.plot)
        
        if args.monitor or args.quick_monitor:
            # Monitoring mode
            interval = 900 if args.quick_monitor else args.interval  # 15 minutes for quick mode
            run_monitoring_mode(optimizer, visualizer, interval, args.keep_timestamp)
            
        elif args.compare:
            # Stock Comparison mode
            try:
                print(f"{EMOJIS['vs']} Stock Comparison Mode")
                stock1, stock2 = args.compare
                
                # Initialize stock comparator
                comparator = StockComparator(investment_strategy=args.strategy)
                
                # Perform comparison
                result = comparator.compare_stocks(stock1, stock2)
                
                # Print results
                comparator.print_comparison_results(result)
                
                # Create detailed metrics table
                if not result.get('error'):
                    metrics_df = comparator.get_detailed_metrics_comparison(result)
                    if not metrics_df.empty:
                        print(f"\n{EMOJIS['chart']} DETAILED METRICS TABLE:")
                        print("=" * 70)
                        print(metrics_df.to_string(index=False))
                    
                    # Create visual comparison dashboard if plotting enabled
                    if args.plot or args.compare:
                        visualizer = PortfolioVisualizer(enable_plotting=True)
                        dashboard_file = visualizer.create_comparison_dashboard(result, save_file=not args.no_save)
                        if dashboard_file:
                            print(f"\n{EMOJIS['chart']} Comparison dashboard saved as {dashboard_file}")
                
                return 0
                
            except Exception as e:
                logging.error(f"Stock comparison error: {e}")
                print(f"{EMOJIS['warning']} Comparison error: {e}")
                return 1
        
        elif args.short_trading:
            # Short Trading mode
            try:
                print(f"{EMOJIS['chart']} Starting Short Trading Mode...")
                print("Real-time P&L monitoring with alerts enabled")
                print("Using separate short_trading.txt configuration file")
                print("Press Ctrl+C to stop monitoring\n")
                
                # Use shorter interval for short trading if not specified
                if args.interval == 3600:  # If using default
                    trading_interval = 60  # 1 minute for short trading
                else:
                    trading_interval = args.interval
                
                # Read target gain and max loss from short trading config file
                short_config_file = 'short_trading.txt'
                config_data = {}
                
                # Create default config file if it doesn't exist
                if not os.path.exists(short_config_file):
                    default_content = """# Short Trading Configuration
# Format: key = value

# Trading thresholds
target_gain_percentage = 25
maximum_loss_percentage = 5

# Current positions for short trading (format: symbol,buy_price,buy_date)
# Add ONE position at a time - system will process and clear automatically
# Example: AAPL,220.50,2025-09-10
buy_stocks = 

# Trading history (automatically maintained by system)
# Format: symbol,sale_price,sale_date,gain_loss,gain_loss_percent
sold_positions = 

# Notes:
# - Add new positions to buy_stocks one at a time
# - System automatically processes and clears buy_stocks after adding to portfolio
# - All gains/losses are tracked in sold_positions
# - This file is separate from investments.txt to avoid conflicts"""
                    
                    with open(short_config_file, 'w') as f:
                        f.write(default_content)
                    print(f"✅ Created {short_config_file} with default settings")
                
                # Parse config file
                try:
                    with open(short_config_file, 'r') as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#') and '=' in line:
                                key, value = line.split('=', 1)
                                config_data[key.strip()] = value.strip()
                except Exception as e:
                    print(f"⚠️  Error reading {short_config_file}: {e}")
                    print("Using default values: 25% target gain, 5% stop loss")

                target_gain = float(config_data.get('target_gain_percentage', 25))
                max_loss = float(config_data.get('maximum_loss_percentage', 5))
                    
                short_trader = ShortTradingManager(target_gain, max_loss, short_config_file)
                short_trader.run_monitoring_loop(trading_interval)
                
            except KeyboardInterrupt:
                print(f"\n{EMOJIS['check']} Short trading monitoring stopped by user")
                logging.info("Short trading monitoring stopped by user")
            except Exception as e:
                logging.error(f"Short trading error: {e}")
                print(f"{EMOJIS['warning']} Short trading error: {e}")
                return 1
            
        else:
            # Single run mode
            print(f"{EMOJIS['rocket']} Running single optimization...")
            
            success = optimizer.run_optimization()
            
            if not success:
                print(f"{EMOJIS['warning']} Optimization failed")
                return 1
            
            # Handle visualization for single run
            if args.plot:
                visualizer.update_all_plots(optimizer)
                
                if not args.no_save:
                    filename = visualizer.save_plots(keep_timestamp=args.keep_timestamp)
                    if filename:
                        print(f"{EMOJIS['check']} Analysis complete! Dashboard saved as {filename}")
                else:
                    print(f"{EMOJIS['check']} Analysis complete! Dashboard displayed (not saved)")
            else:
                print(f"{EMOJIS['check']} Analysis complete!")
        
        return 0
        
    except FileNotFoundError as e:
        print(f"{EMOJIS['warning']} Configuration file not found: {e}")
        print(f"Create {args.config} with your stock holdings and cash amount.")
        return 1
        
    except Exception as e:
        logging.error(f"Application error: {e}")
        print(f"{EMOJIS['warning']} Application error: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
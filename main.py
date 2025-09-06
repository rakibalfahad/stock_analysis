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
  python main.py --plot                    # Run optimization with dashboard
  python main.py --monitor --plot          # Monitor with visualization  
  python main.py --quick-monitor           # 15-minute monitoring mode
  python main.py --cleanup 5               # Keep 5 latest dashboard files
  python main.py --keep-timestamp --plot   # Create timestamped files
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
            atr_multiplier=args.atr_multiplier
        )
        
        visualizer = PortfolioVisualizer(enable_plotting=args.plot)
        
        if args.monitor or args.quick_monitor:
            # Monitoring mode
            interval = 900 if args.quick_monitor else args.interval  # 15 minutes for quick mode
            run_monitoring_mode(optimizer, visualizer, interval, args.keep_timestamp)
            
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
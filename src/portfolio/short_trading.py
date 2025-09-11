#!/usr/bin/env python3
"""
Short Trading Module

Handles short-term trading operations with real-time monitoring,
automatic portfolio updates, and profit/loss alerts.

Features:
- Real-time price monitoring
- Automatic buy order processing
- Profit/loss threshold alerts
- Blinking warning messages
- Portfolio synchronization

Author: Investment Management System
Date: September 2025
"""

import os
import sys
import time
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import colorama
from colorama import Fore, Back, Style
import threading

# Initialize colorama for colored output
colorama.init()

class ShortTradingManager:
    """Manage short-term trading operations with real-time monitoring"""
    
    def __init__(self, target_gain_pct: float, max_loss_pct: float, config_file: str = 'short_trading.txt'):
        """
        Initialize short trading manager
        
        Args:
            target_gain_pct: Target gain percentage to trigger sell alert
            max_loss_pct: Maximum loss percentage to trigger sell alert
            config_file: Path to short trading configuration file (default: short_trading.txt)
        """
        self.config_file = config_file
        self.target_gain_pct = target_gain_pct / 100  # Convert to decimal
        self.max_loss_pct = max_loss_pct / 100
        self.holdings = {}  # {symbol: {'buy_price': float, 'buy_date': str, 'current_price': float}}
        self.blink_thread = None
        self.stop_blinking = False
        
    def parse_config_file(self) -> Dict:
        """Parse the short trading configuration file"""
        config = {
            'target_gain_percentage': 25,
            'maximum_loss_percentage': 5,
            'buy_stocks': '',
            'sold_positions': ''
        }
        
        if not os.path.exists(self.config_file):
            print(f"⚠️  Short trading config file {self.config_file} not found. Using defaults.")
            return config
            
        try:
            with open(self.config_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        config[key.strip()] = value.strip()
        except Exception as e:
            print(f"❌ Error reading config file: {e}")
            
        return config
    
    def update_config_file(self, updates: Dict[str, str]) -> bool:
        """Update the short trading configuration file with new values"""
        try:
            # Read current config
            lines = []
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    lines = f.readlines()
            
            # Update specified keys
            updated_lines = []
            updated_keys = set()
            
            for line in lines:
                stripped = line.strip()
                if stripped and not stripped.startswith('#') and '=' in stripped:
                    key, value = stripped.split('=', 1)
                    key = key.strip()
                    if key in updates:
                        updated_lines.append(f"{key} = {updates[key]}\n")
                        updated_keys.add(key)
                    else:
                        updated_lines.append(line)
                else:
                    updated_lines.append(line)
            
            # Add any new keys that weren't in the file
            for key, value in updates.items():
                if key not in updated_keys:
                    updated_lines.append(f"{key} = {value}\n")
            
            # Write back to file
            with open(self.config_file, 'w') as f:
                f.writelines(updated_lines)
                
            return True
                
        except Exception as e:
            print(f"❌ Error updating config file: {e}")
            return False
    
    def process_buy_orders(self) -> bool:
        """Process any new buy orders from buy_stocks configuration"""
        config = self.parse_config_file()
        
        # Collect all buy orders from different formats
        buy_orders = []
        
        # Format 1: Single or pipe-separated in buy_stocks
        buy_stocks = config.get('buy_stocks', '').strip()
        if buy_stocks:
            if '|' in buy_stocks:
                # Multiple orders separated by pipe
                orders = [order.strip() for order in buy_stocks.split('|')]
                buy_orders.extend(orders)
            else:
                # Single order
                buy_orders.append(buy_stocks)
        
        # Format 2: Multiple buy_stocks_N entries
        for key, value in config.items():
            if key.startswith('buy_stocks_') and value.strip():
                buy_orders.append(value.strip())
        
        if not buy_orders:
            return False
        
        print(f"\n💰 Processing {len(buy_orders)} buy order(s)...")
        
        processed_count = 0
        failed_count = 0
        
        for i, buy_order in enumerate(buy_orders, 1):
            try:
                print(f"\n📋 Order {i}/{len(buy_orders)}: {buy_order}")
                
                # Parse buy order: symbol,shares,price_per_share,date
                parts = buy_order.split(',')
                if len(parts) != 4:
                    print(f"❌ Invalid format. Expected: SYMBOL,SHARES,PRICE_PER_SHARE,DATE")
                    failed_count += 1
                    continue
                
                symbol, shares, buy_price, buy_date = [part.strip() for part in parts]
                shares = int(shares)
                buy_price = float(buy_price)
                total_investment = shares * buy_price
                
                # Check if symbol already exists in holdings
                if symbol in self.holdings:
                    print(f"⚠️  {symbol} already in holdings. Skipping duplicate.")
                    failed_count += 1
                    continue
                
                # Add to holdings
                self.holdings[symbol] = {
                    'shares': shares,
                    'buy_price': buy_price,
                    'buy_date': buy_date,
                    'current_price': buy_price,
                    'total_investment': total_investment
                }
                
                print(f"✅ {symbol}: {shares} shares @ ${buy_price:.2f} = ${total_investment:.2f} on {buy_date}")
                processed_count += 1
                
            except Exception as e:
                print(f"❌ Error processing order {i}: {e}")
                failed_count += 1
        
        # Clear all buy order fields after processing
        updates = {'buy_stocks': ''}
        
        # Clear any buy_stocks_N fields
        for key in config.keys():
            if key.startswith('buy_stocks_'):
                updates[key] = ''
        
        if self.update_config_file(updates):
            print(f"\n🎯 Summary: {processed_count} positions added, {failed_count} failed")
            if processed_count > 0:
                symbols = list(self.holdings.keys())
                print(f"📊 Active positions: {', '.join(symbols)}")
        else:
            print(f"⚠️  Positions added but failed to clear buy order fields")
        
        return processed_count > 0
    
    def get_current_prices(self) -> Dict[str, float]:
        """Fetch current prices for all holdings"""
        if not self.holdings:
            return {}
        
        symbols = list(self.holdings.keys())
        try:
            # Fetch current prices
            current_prices = {}
            
            for symbol in symbols:
                # Fetch each symbol individually to avoid DataFrame structure issues
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period='1d')
                if not hist.empty and 'Close' in hist.columns:
                    current_prices[symbol] = float(hist['Close'].iloc[-1])
                else:
                    print(f"⚠️  Warning: Could not fetch price for {symbol}")
            
            # Update holdings with current prices
            for symbol, price in current_prices.items():
                if symbol in self.holdings:
                    self.holdings[symbol]['current_price'] = price
            
            return current_prices
            
        except Exception as e:
            print(f"❌ Error fetching current prices: {e}")
            return {}
    
    def calculate_pnl(self, symbol: str) -> Tuple[float, float]:
        """Calculate P&L for a symbol"""
        if symbol not in self.holdings:
            return 0.0, 0.0
        
        holding = self.holdings[symbol]
        shares = holding['shares']
        buy_price = holding['buy_price']
        current_price = holding['current_price']
        
        # P&L calculation with shares
        total_buy_value = shares * buy_price
        total_current_value = shares * current_price
        
        pnl_amount = total_current_value - total_buy_value
        pnl_percentage = (pnl_amount / total_buy_value) * 100
        
        return pnl_amount, pnl_percentage
    
    def check_alerts(self) -> List[Dict]:
        """Check for profit/loss alerts"""
        alerts = []
        
        for symbol in self.holdings:
            pnl_amount, pnl_percentage = self.calculate_pnl(symbol)
            pnl_decimal = pnl_percentage / 100
            
            alert_type = None
            message = ""
            
            # Get holding info for better alerts
            holding = self.holdings[symbol]
            shares = holding['shares']
            
            # Check for target gain
            if pnl_decimal >= self.target_gain_pct:
                alert_type = "TARGET_REACHED"
                message = f"🎯 TARGET GAIN REACHED! {symbol} ({shares} shares): +{pnl_percentage:.1f}% (${pnl_amount:.2f})"
            
            # Check for maximum loss
            elif pnl_decimal <= -self.max_loss_pct:
                alert_type = "STOP_LOSS"
                message = f"🛑 STOP LOSS TRIGGERED! {symbol} ({shares} shares): -{abs(pnl_percentage):.1f}% (${pnl_amount:.2f})"
            
            # Check for any loss (warning)
            elif pnl_amount < 0:
                alert_type = "WARNING"
                message = f"⚠️  LOSS WARNING: {symbol} ({shares} shares): -{abs(pnl_percentage):.1f}% (${pnl_amount:.2f})"
            
            if alert_type:
                alerts.append({
                    'symbol': symbol,
                    'type': alert_type,
                    'message': message,
                    'pnl_amount': pnl_amount,
                    'pnl_percentage': pnl_percentage
                })
        
        return alerts
    
    def blink_message(self, message: str, color: str = Fore.RED):
        """Display blinking message in a separate thread"""
        def blink():
            while not self.stop_blinking:
                print(f"\r{color}{Style.BRIGHT}{message}{Style.RESET_ALL}", end='', flush=True)
                time.sleep(0.5)
                if not self.stop_blinking:
                    print(f"\r{' ' * len(message)}", end='', flush=True)
                    time.sleep(0.5)
        
        if self.blink_thread and self.blink_thread.is_alive():
            self.stop_blinking = True
            self.blink_thread.join()
        
        self.stop_blinking = False
        self.blink_thread = threading.Thread(target=blink)
        self.blink_thread.daemon = True
        self.blink_thread.start()
    
    def stop_blink(self):
        """Stop the blinking message"""
        self.stop_blinking = True
        if self.blink_thread and self.blink_thread.is_alive():
            self.blink_thread.join()
        print()  # New line
    
    def display_portfolio_status(self):
        """Display current portfolio status"""
        if not self.holdings:
            print("📈 No active short trading positions")
            return
        
        print(f"\n{'='*80}")
        print(f"📊 SHORT TRADING PORTFOLIO STATUS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*90}")
        print(f"{'Symbol':<8} {'Shares':<8} {'Buy Price':<12} {'Current':<12} {'Total Value':<12} {'P&L $':<12} {'P&L %':<10} {'Status'}")
        print(f"{'-'*90}")
        
        total_pnl = 0
        total_investment = 0
        total_current_value = 0
        
        for symbol in self.holdings:
            holding = self.holdings[symbol]
            shares = holding['shares']
            buy_price = holding['buy_price']
            current_price = holding['current_price']
            buy_date = holding['buy_date']
            
            # Calculate values
            investment_amount = shares * buy_price
            current_value = shares * current_price
            pnl_amount, pnl_percentage = self.calculate_pnl(symbol)
            
            total_pnl += pnl_amount
            total_investment += investment_amount
            total_current_value += current_value
            
            # Determine status and color
            if pnl_percentage >= self.target_gain_pct * 100:
                status = f"{Fore.GREEN}🎯 SELL!{Style.RESET_ALL}"
            elif pnl_percentage <= -self.max_loss_pct * 100:
                status = f"{Fore.RED}🛑 SELL!{Style.RESET_ALL}"
            elif pnl_amount < 0:
                status = f"{Fore.YELLOW}⚠️  WATCH{Style.RESET_ALL}"
            else:
                status = f"{Fore.GREEN}✅ HOLD{Style.RESET_ALL}"
            
            # Format P&L with colors
            pnl_color = Fore.GREEN if pnl_amount >= 0 else Fore.RED
            pnl_sign = "+" if pnl_amount >= 0 else ""
            
            print(f"{symbol:<8} {shares:<8} ${buy_price:<11.2f} ${current_price:<11.2f} "
                  f"${current_value:<11.2f} {pnl_color}{pnl_sign}${pnl_amount:<11.2f}{Style.RESET_ALL} "
                  f"{pnl_color}{pnl_sign}{pnl_percentage:<9.1f}%{Style.RESET_ALL} {status}")
        
        print(f"{'-'*90}")
        total_color = Fore.GREEN if total_pnl >= 0 else Fore.RED
        total_sign = "+" if total_pnl >= 0 else ""
        print(f"{'TOTAL':<8} {'':<8} {'':<12} {'':<12} "
              f"${total_current_value:<11.2f} {total_color}{total_sign}${total_pnl:<11.2f}{Style.RESET_ALL} {'':<10} ")
        print(f"📊 Total Invested: ${total_investment:.2f} | Current Value: ${total_current_value:.2f}")
        print(f"{'='*90}")
    
    def monitor_positions(self) -> List[Dict]:
        """Monitor all positions and return alerts"""
        # Process any new buy orders first
        self.process_buy_orders()
        
        # Get current prices
        current_prices = self.get_current_prices()
        
        if not current_prices:
            return []
        
        # Display portfolio status
        self.display_portfolio_status()
        
        # Check for alerts
        alerts = self.check_alerts()
        
        # Display alerts
        critical_alerts = []
        for alert in alerts:
            if alert['type'] in ['TARGET_REACHED', 'STOP_LOSS']:
                critical_alerts.append(alert)
                print(f"\n{Fore.RED}{Style.BRIGHT}{'='*60}{Style.RESET_ALL}")
                print(f"{Fore.RED}{Style.BRIGHT}{alert['message']}{Style.RESET_ALL}")
                print(f"{Fore.RED}{Style.BRIGHT}{'='*60}{Style.RESET_ALL}")
            elif alert['type'] == 'WARNING':
                print(f"\n{Fore.YELLOW}{alert['message']}{Style.RESET_ALL}")
        
        return alerts
    
    def run_monitoring_loop(self, interval: int = 60):
        """Run continuous monitoring loop"""
        print(f"\n🚀 Starting short trading monitoring...")
        print(f"⏱️  Update interval: {interval} seconds")
        print(f"🎯 Target gain: {self.target_gain_pct*100:.1f}%")
        print(f"🛑 Stop loss: {self.max_loss_pct*100:.1f}%")
        print(f"⌨️  Press Ctrl+C to stop monitoring")
        
        try:
            iteration = 0
            critical_alert_active = False
            
            while True:
                iteration += 1
                print(f"\n{'='*50}")
                print(f"🔄 Monitoring Cycle #{iteration}")
                print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"{'='*50}")
                
                # Monitor positions
                alerts = self.monitor_positions()
                
                # Handle critical alerts with blinking
                critical_alerts = [a for a in alerts if a['type'] in ['TARGET_REACHED', 'STOP_LOSS']]
                
                if critical_alerts and not critical_alert_active:
                    # Start blinking for critical alerts
                    alert_messages = [alert['message'] for alert in critical_alerts]
                    combined_message = " | ".join(alert_messages)
                    self.blink_message(f"🚨 SELL ALERT: {combined_message} 🚨")
                    critical_alert_active = True
                elif not critical_alerts and critical_alert_active:
                    # Stop blinking if no more critical alerts
                    self.stop_blink()
                    critical_alert_active = False
                
                # Wait for next iteration
                print(f"\n⏳ Next update in {interval} seconds...")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print(f"\n\n✅ Short trading monitoring stopped by user")
            if critical_alert_active:
                self.stop_blink()
        except Exception as e:
            print(f"\n❌ Error in monitoring loop: {e}")
            if critical_alert_active:
                self.stop_blink()
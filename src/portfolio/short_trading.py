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
        self.holdings = {}  # {symbol: {'shares': int, 'buy_price': float, 'buy_date': str, 'current_price': float, 'total_investment': float}}
        self.blink_thread = None
        self.stop_blinking = False
        
        # Load existing holdings on startup
        self.load_existing_holdings()
        
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
                        key = key.strip()
                        value = value.strip()
                        config[key] = value  # Store all key-value pairs, not just predefined ones
        except Exception as e:
            print(f"❌ Error reading config file: {e}")
            
        return config
    
    def load_existing_holdings(self):
        """Load existing holdings from configuration file"""
        config = self.parse_config_file()
        current_holdings = config.get('current_holdings', '').strip()
        
        if not current_holdings:
            return
            
        print(f"\n📊 Loading existing holdings...")
        
        try:
            # Parse current holdings: symbol,shares,price,date|symbol,shares,price,date
            holdings_list = [holding.strip() for holding in current_holdings.split('|')]
            
            loaded_count = 0
            for holding in holdings_list:
                if not holding:
                    continue
                    
                parts = holding.split(',')
                if len(parts) != 4:
                    print(f"⚠️  Invalid holding format: {holding}. Expected: SYMBOL,SHARES,PRICE,DATE")
                    continue
                
                symbol, shares, buy_price, buy_date = [part.strip() for part in parts]
                shares = int(shares)
                buy_price = float(buy_price)
                total_investment = shares * buy_price
                
                self.holdings[symbol] = {
                    'shares': shares,
                    'buy_price': buy_price,
                    'buy_date': buy_date,
                    'current_price': buy_price,  # Will be updated with real prices
                    'total_investment': total_investment
                }
                
                print(f"📈 Loaded: {symbol} - {shares} shares @ ${buy_price:.2f} = ${total_investment:.2f} (bought {buy_date})")
                loaded_count += 1
            
            if loaded_count > 0:
                print(f"✅ Loaded {loaded_count} existing position(s) from configuration")
            
        except Exception as e:
            print(f"❌ Error loading existing holdings: {e}")
    
    def update_current_holdings(self):
        """Update current_holdings field with all positions for persistence"""
        try:
            # Build current_holdings string from all holdings
            holdings_list = []
            for symbol, holding in self.holdings.items():
                shares = holding['shares']
                buy_price = holding['buy_price']
                buy_date = holding['buy_date']
                holdings_list.append(f"{symbol},{shares},{buy_price},{buy_date}")
            
            # Create pipe-separated string
            current_holdings_str = '|'.join(holdings_list)
            
            # Update the config file
            self.update_config_file({'current_holdings': current_holdings_str})
            
        except Exception as e:
            print(f"❌ Error updating current_holdings: {e}")
    
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
        
        # Update current_holdings with new positions (persist them)
        if processed_count > 0:
            self.update_current_holdings()
        
        if self.update_config_file(updates):
            print(f"\n🎯 Summary: {processed_count} positions added, {failed_count} failed")
            if processed_count > 0:
                symbols = list(self.holdings.keys())
                print(f"📊 Active positions: {', '.join(symbols)}")
                print(f"💾 Positions saved to current_holdings for persistence")
        else:
            print(f"⚠️  Positions added but failed to clear buy order fields")
        
        return processed_count > 0
    
    def process_sold_stocks(self) -> bool:
        """Process any sold stock transactions from sell_stocks configuration"""
        config = self.parse_config_file()
        
        # Collect all sell orders from different formats
        sell_orders = []
        
        # Format 1: Single or pipe-separated in sell_stocks
        sell_stocks = config.get('sell_stocks', '').strip()
        if sell_stocks:
            if '|' in sell_stocks:
                # Multiple orders separated by pipe
                orders = [order.strip() for order in sell_stocks.split('|')]
                sell_orders.extend(orders)
            else:
                # Single order
                sell_orders.append(sell_stocks)
        
        # Format 2: Multiple sell_stocks_N entries
        for key, value in config.items():
            if key.startswith('sell_stocks_') and value.strip():
                sell_orders.append(value.strip())
        
        if not sell_orders:
            return False
        
        print(f"\n💸 Processing {len(sell_orders)} sell order(s)...")
        
        processed_count = 0
        failed_count = 0
        
        for i, sell_order in enumerate(sell_orders, 1):
            try:
                print(f"\n📋 Sell Order {i}/{len(sell_orders)}: {sell_order}")
                
                # Parse sell order: symbol,shares_sold,price_per_share,date
                parts = sell_order.split(',')
                if len(parts) != 4:
                    print(f"❌ Invalid format for sell order {i}. Expected: SYMBOL,SHARES,PRICE,DATE")
                    failed_count += 1
                    continue
                
                symbol = parts[0].strip().upper()
                shares_sold = int(parts[1].strip())
                sale_price = float(parts[2].strip())
                sale_date = parts[3].strip()
                
                # Check if we own this stock
                if symbol not in self.holdings:
                    print(f"❌ Cannot sell {symbol}: Not found in current holdings")
                    failed_count += 1
                    continue
                
                # Check if we have enough shares to sell
                current_shares = self.holdings[symbol]['shares']
                if shares_sold > current_shares:
                    print(f"❌ Cannot sell {shares_sold} shares of {symbol}: Only own {current_shares} shares")
                    failed_count += 1
                    continue
                
                # Calculate P&L for this sale
                buy_price = self.holdings[symbol]['buy_price']
                total_sale_value = shares_sold * sale_price
                total_cost_basis = shares_sold * buy_price
                gain_loss = total_sale_value - total_cost_basis
                gain_loss_percent = (gain_loss / total_cost_basis) * 100
                
                # Update holdings
                if shares_sold == current_shares:
                    # Selling entire position - remove from holdings
                    del self.holdings[symbol]
                    print(f"✅ SOLD ENTIRE POSITION: {symbol} - {shares_sold} shares @ ${sale_price:.2f}")
                else:
                    # Partial sale - update remaining shares
                    remaining_shares = current_shares - shares_sold
                    self.holdings[symbol]['shares'] = remaining_shares
                    # Update total investment for remaining shares
                    self.holdings[symbol]['total_investment'] = remaining_shares * buy_price
                    print(f"✅ PARTIAL SALE: {symbol} - Sold {shares_sold} shares @ ${sale_price:.2f}, {remaining_shares} shares remaining")
                
                # Record the sale in sold_positions
                sale_record = f"{symbol},{sale_price},{sale_date},{gain_loss:.2f},{gain_loss_percent:.1f}"
                
                # Update sold_positions in config
                current_sold = config.get('sold_positions', '').strip()
                if current_sold:
                    new_sold = f"{current_sold}|{sale_record}"
                else:
                    new_sold = sale_record
                
                # Update config with new sold position
                config['sold_positions'] = new_sold
                
                print(f"💰 P&L: ${gain_loss:.2f} ({gain_loss_percent:.1f}%) on {shares_sold} shares")
                
                processed_count += 1
                
            except (ValueError, IndexError) as e:
                print(f"❌ Error processing sell order {i}: {e}")
                failed_count += 1
        
        print(f"\n🎯 Sell Summary: {processed_count} transactions completed, {failed_count} failed")
        
        if processed_count > 0:
            # Save updated holdings and sold positions
            self.update_current_holdings()
            
            # Clear sell order fields
            updates = {'sell_stocks': ''}
            
            # Clear any sell_stocks_N fields and update sold_positions
            for key in config.keys():
                if key.startswith('sell_stocks_'):
                    updates[key] = ''
            
            # Update sold_positions
            updates['sold_positions'] = config.get('sold_positions', '')
            
            if self.update_config_file(updates):
                print(f"💾 Holdings updated and sell orders cleared")
            else:
                print(f"⚠️  Transactions completed but failed to clear sell order fields")
        
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
        
        print(f"\n{'='*105}")
        print(f"📊 SHORT TRADING PORTFOLIO STATUS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*105}")
        print(f"{'Symbol':<8} {'Shares':<8} {'Buy Price':<12} {'Current':<12} {'Total Value':<12} {'P&L $':<12} {'P&L %':<10} {'Purchase Date':<12} {'Status'}")
        print(f"{'-'*105}")
        
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
                  f"{pnl_color}{pnl_sign}{pnl_percentage:<9.1f}%{Style.RESET_ALL} {buy_date:<12} {status}")
        
        print(f"{'-'*105}")
        total_color = Fore.GREEN if total_pnl >= 0 else Fore.RED
        total_sign = "+" if total_pnl >= 0 else ""
        total_pnl_pct = (total_pnl/total_investment*100) if total_investment > 0 else 0
        print(f"{'TOTAL':<8} {'':<8} {'':<12} {'':<12} "
              f"${total_current_value:<11.2f} {total_color}{total_sign}${total_pnl:<11.2f}{Style.RESET_ALL} "
              f"{total_color}{total_sign}{total_pnl_pct:<9.1f}%{Style.RESET_ALL} {'':<12}")
        print(f"📊 Total Invested: ${total_investment:.2f} | Current Value: ${total_current_value:.2f} | Portfolio P&L: {total_color}{total_sign}${total_pnl:.2f}{Style.RESET_ALL}")
        print(f"{'='*105}")
    
    def monitor_positions(self) -> List[Dict]:
        """Monitor all positions and return alerts"""
        # Process any new buy orders first
        self.process_buy_orders()
        
        # Process any sold stock transactions
        self.process_sold_stocks()
        
        # If no holdings yet, show message and return
        if not self.holdings:
            print("📊 No active positions to monitor")
            print("💡 Add positions to 'current_holdings' or 'buy_stocks' in short_trading.txt")
            return []
        
        # Get current prices for existing holdings
        current_prices = self.get_current_prices()
        
        if not current_prices:
            print("⚠️  Unable to fetch current prices. Displaying last known values.")
        
        # Display portfolio status (even with stale prices)
        self.display_portfolio_status()
        
        # Check for alerts (only if we have current prices)
        alerts = []
        if current_prices:
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
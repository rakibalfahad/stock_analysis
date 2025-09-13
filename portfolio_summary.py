#!/usr/bin/env python3
"""
Portfolio Summary Dashboard

A comprehensive view of your investment portfolio including:
- Current holdings from short_trading.txt
- Sold positions and P&L history
- Investment targets and risk management
- Portfolio performance overview

Usage: python portfolio_summary.py
"""

import os
import sys
from datetime import datetime
from typing import Dict, List, Tuple
import yfinance as yf
import colorama
from colorama import Fore, Back, Style

# Initialize colorama for colored output
colorama.init()

class PortfolioSummary:
    def __init__(self):
        self.investments_file = 'investments.txt'
        self.short_trading_file = 'short_trading.txt'
        self.investments_config = {}
        self.short_trading_config = {}
        
    def parse_config_file(self, filename: str) -> Dict:
        """Parse configuration file and return key-value pairs"""
        config = {}
        
        if not os.path.exists(filename):
            print(f"⚠️  Configuration file {filename} not found.")
            return config
            
        try:
            with open(filename, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        config[key] = value
        except Exception as e:
            print(f"❌ Error reading {filename}: {e}")
            
        return config
    
    def load_configurations(self):
        """Load both configuration files"""
        print(f"📊 Loading portfolio configurations...")
        self.investments_config = self.parse_config_file(self.investments_file)
        self.short_trading_config = self.parse_config_file(self.short_trading_file)
        print(f"✅ Configuration files loaded")
    
    def get_current_prices(self, symbols: List[str]) -> Dict[str, float]:
        """Fetch current prices for given symbols"""
        if not symbols:
            return {}
            
        print(f"📡 Fetching current market prices for {len(symbols)} symbols...")
        current_prices = {}
        
        try:
            for symbol in symbols:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period='1d')
                if not hist.empty and 'Close' in hist.columns:
                    current_prices[symbol] = float(hist['Close'].iloc[-1])
                else:
                    print(f"⚠️  Warning: Could not fetch price for {symbol}")
        except Exception as e:
            print(f"❌ Error fetching prices: {e}")
            
        return current_prices
    
    def display_investment_targets(self):
        """Display investment configuration and targets"""
        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"🎯 INVESTMENT CONFIGURATION & TARGETS")
        print(f"{'='*80}{Style.RESET_ALL}")
        
        # Investment targets from investments.txt
        total_investment = self.investments_config.get('total_investment', 'Not set')
        target_gain = self.investments_config.get('target_gain_percentage', 'Not set')
        max_loss = self.investments_config.get('maximum_loss_percentage', 'Not set')
        preferred_stocks = self.investments_config.get('preferred_stocks', 'Not set')
        
        print(f"💰 Total Investment Budget: ${total_investment}" if total_investment != 'Not set' else f"💰 Total Investment Budget: {total_investment}")
        print(f"📈 Target Gain Percentage: {target_gain}%" if target_gain != 'Not set' else f"📈 Target Gain Percentage: {target_gain}")
        print(f"🛑 Maximum Loss Tolerance: {max_loss}%" if max_loss != 'Not set' else f"🛑 Maximum Loss Tolerance: {max_loss}")
        
        # Risk assessment
        if target_gain != 'Not set' and max_loss != 'Not set':
            try:
                target_val = float(target_gain)
                loss_val = float(max_loss)
                risk_ratio = target_val / loss_val
                
                if risk_ratio >= 5:
                    risk_profile = f"{Fore.GREEN}Conservative{Style.RESET_ALL}"
                elif risk_ratio >= 3:
                    risk_profile = f"{Fore.YELLOW}Moderate{Style.RESET_ALL}"
                else:
                    risk_profile = f"{Fore.RED}Aggressive{Style.RESET_ALL}"
                    
                print(f"⚖️  Risk Profile: {risk_profile} (Reward:Risk = {risk_ratio:.1f}:1)")
            except:
                print(f"⚖️  Risk Profile: Unable to calculate")
        
        # Short trading thresholds
        st_target = self.short_trading_config.get('target_gain_percentage', 'Not set')
        st_loss = self.short_trading_config.get('maximum_loss_percentage', 'Not set')
        
        print(f"\n📊 Short Trading Thresholds:")
        print(f"   🎯 Target Gain Alert: {st_target}%" if st_target != 'Not set' else f"   🎯 Target Gain Alert: {st_target}")
        print(f"   🛑 Stop Loss Alert: {st_loss}%" if st_loss != 'Not set' else f"   🛑 Stop Loss Alert: {st_loss}")
        
        # Preferred stocks
        if preferred_stocks != 'Not set':
            stocks_list = [stock.strip() for stock in preferred_stocks.split(',')]
            print(f"\n🌟 Preferred Stocks Portfolio ({len(stocks_list)} stocks):")
            # Display in rows of 6
            for i in range(0, len(stocks_list), 6):
                row = stocks_list[i:i+6]
                print(f"   {' | '.join(row)}")
    
    def display_current_holdings(self):
        """Display current active holdings from short_trading.txt"""
        print(f"\n{Fore.GREEN}{'='*120}")
        print(f"📊 CURRENT ACTIVE HOLDINGS")
        print(f"{'='*120}{Style.RESET_ALL}")
        
        current_holdings = self.short_trading_config.get('current_holdings', '').strip()
        
        if not current_holdings:
            print(f"{Fore.YELLOW}📈 No active holdings found{Style.RESET_ALL}")
            print(f"💡 Add positions to 'current_holdings' or 'buy_stocks' in {self.short_trading_file}")
            return
        
        # Parse holdings
        holdings_list = [holding.strip() for holding in current_holdings.split('|')]
        holdings_data = []
        symbols_for_prices = []
        
        for holding in holdings_list:
            if not holding:
                continue
                
            parts = holding.split(',')
            if len(parts) == 4:
                symbol, shares, buy_price, buy_date = [part.strip() for part in parts]
                try:
                    shares = int(shares)
                    buy_price = float(buy_price)
                    holdings_data.append({
                        'symbol': symbol,
                        'shares': shares,
                        'buy_price': buy_price,
                        'buy_date': buy_date,
                        'total_investment': shares * buy_price
                    })
                    symbols_for_prices.append(symbol)
                except ValueError:
                    print(f"⚠️  Invalid holding format: {holding}")
        
        if not holdings_data:
            print(f"{Fore.YELLOW}📈 No valid holdings found{Style.RESET_ALL}")
            return
        
        # Get current prices
        current_prices = self.get_current_prices(symbols_for_prices)
        
        # Display table header
        print(f"{'Symbol':<8} {'Shares':<8} {'Buy Price':<12} {'Current':<12} {'Investment':<12} {'Current Value':<14} {'P&L $':<12} {'P&L %':<10} {'Buy Date':<12} {'Status'}")
        print(f"{'-'*120}")
        
        total_investment = 0
        total_current_value = 0
        total_pnl = 0
        
        # Get thresholds for alerts
        try:
            target_gain_pct = float(self.short_trading_config.get('target_gain_percentage', 25))
            max_loss_pct = float(self.short_trading_config.get('maximum_loss_percentage', 5))
        except:
            target_gain_pct = 25
            max_loss_pct = 5
        
        for holding in holdings_data:
            symbol = holding['symbol']
            shares = holding['shares']
            buy_price = holding['buy_price']
            buy_date = holding['buy_date']
            investment = holding['total_investment']
            
            # Get current price
            current_price = current_prices.get(symbol, buy_price)
            current_value = shares * current_price
            pnl_amount = current_value - investment
            pnl_percentage = (pnl_amount / investment) * 100 if investment > 0 else 0
            
            # Determine status and color
            if pnl_percentage >= target_gain_pct:
                status = f"{Fore.GREEN}🎯 SELL!{Style.RESET_ALL}"
            elif pnl_percentage <= -max_loss_pct:
                status = f"{Fore.RED}🛑 SELL!{Style.RESET_ALL}"
            elif pnl_amount < 0:
                status = f"{Fore.YELLOW}⚠️  WATCH{Style.RESET_ALL}"
            else:
                status = f"{Fore.GREEN}✅ HOLD{Style.RESET_ALL}"
            
            # Format P&L with colors
            pnl_color = Fore.GREEN if pnl_amount >= 0 else Fore.RED
            pnl_sign = "+" if pnl_amount >= 0 else ""
            
            print(f"{symbol:<8} {shares:<8} ${buy_price:<11.2f} ${current_price:<11.2f} "
                  f"${investment:<11.2f} ${current_value:<13.2f} "
                  f"{pnl_color}{pnl_sign}${pnl_amount:<11.2f}{Style.RESET_ALL} "
                  f"{pnl_color}{pnl_sign}{pnl_percentage:<9.1f}%{Style.RESET_ALL} "
                  f"{buy_date:<12} {status}")
            
            total_investment += investment
            total_current_value += current_value
            total_pnl += pnl_amount
        
        # Display totals
        print(f"{'-'*120}")
        total_color = Fore.GREEN if total_pnl >= 0 else Fore.RED
        total_sign = "+" if total_pnl >= 0 else ""
        total_pnl_pct = (total_pnl/total_investment*100) if total_investment > 0 else 0
        
        print(f"{'TOTAL':<8} {'':<8} {'':<12} {'':<12} "
              f"${total_investment:<11.2f} ${total_current_value:<13.2f} "
              f"{total_color}{total_sign}${total_pnl:<11.2f}{Style.RESET_ALL} "
              f"{total_color}{total_sign}{total_pnl_pct:<9.1f}%{Style.RESET_ALL}")
        
        print(f"\n💼 Portfolio Summary:")
        print(f"   💰 Total Invested: ${total_investment:,.2f}")
        print(f"   📊 Current Value: ${total_current_value:,.2f}")
        print(f"   📈 Total P&L: {total_color}{total_sign}${total_pnl:,.2f} ({total_sign}{total_pnl_pct:.1f}%){Style.RESET_ALL}")
    
    def display_sold_positions(self):
        """Display historical sold positions"""
        print(f"\n{Fore.MAGENTA}{'='*100}")
        print(f"💸 SOLD POSITIONS HISTORY")
        print(f"{'='*100}{Style.RESET_ALL}")
        
        sold_positions = self.short_trading_config.get('sold_positions', '').strip()
        
        if not sold_positions:
            print(f"{Fore.YELLOW}📊 No sold positions found{Style.RESET_ALL}")
            print(f"💡 Completed sales will appear here automatically")
            return
        
        # Parse sold positions
        sales_list = [sale.strip() for sale in sold_positions.split('|')]
        sales_data = []
        
        for sale in sales_list:
            if not sale:
                continue
                
            parts = sale.split(',')
            if len(parts) == 5:
                symbol, sale_price, sale_date, gain_loss, gain_loss_pct = [part.strip() for part in parts]
                try:
                    sale_price = float(sale_price)
                    gain_loss = float(gain_loss)
                    gain_loss_pct = float(gain_loss_pct)
                    sales_data.append({
                        'symbol': symbol,
                        'sale_price': sale_price,
                        'sale_date': sale_date,
                        'gain_loss': gain_loss,
                        'gain_loss_pct': gain_loss_pct
                    })
                except ValueError:
                    print(f"⚠️  Invalid sale format: {sale}")
        
        if not sales_data:
            print(f"{Fore.YELLOW}📊 No valid sold positions found{Style.RESET_ALL}")
            return
        
        # Display table header
        print(f"{'Symbol':<8} {'Sale Price':<12} {'Sale Date':<12} {'P&L Amount':<12} {'P&L %':<10} {'Performance'}")
        print(f"{'-'*70}")
        
        total_realized_pnl = 0
        winning_trades = 0
        losing_trades = 0
        
        for sale in sales_data:
            symbol = sale['symbol']
            sale_price = sale['sale_price']
            sale_date = sale['sale_date']
            gain_loss = sale['gain_loss']
            gain_loss_pct = sale['gain_loss_pct']
            
            # Color coding for performance
            if gain_loss > 0:
                pnl_color = Fore.GREEN
                performance = f"{Fore.GREEN}✅ PROFIT{Style.RESET_ALL}"
                winning_trades += 1
            else:
                pnl_color = Fore.RED
                performance = f"{Fore.RED}❌ LOSS{Style.RESET_ALL}"
                losing_trades += 1
            
            pnl_sign = "+" if gain_loss >= 0 else ""
            
            print(f"{symbol:<8} ${sale_price:<11.2f} {sale_date:<12} "
                  f"{pnl_color}{pnl_sign}${gain_loss:<11.2f}{Style.RESET_ALL} "
                  f"{pnl_color}{pnl_sign}{gain_loss_pct:<9.1f}%{Style.RESET_ALL} "
                  f"{performance}")
            
            total_realized_pnl += gain_loss
        
        # Display summary
        print(f"{'-'*70}")
        total_color = Fore.GREEN if total_realized_pnl >= 0 else Fore.RED
        total_sign = "+" if total_realized_pnl >= 0 else ""
        win_rate = (winning_trades / len(sales_data) * 100) if sales_data else 0
        
        print(f"{'TOTAL':<8} {'':<12} {'':<12} "
              f"{total_color}{total_sign}${total_realized_pnl:<11.2f}{Style.RESET_ALL}")
        
        print(f"\n📊 Trading Performance:")
        print(f"   💰 Total Realized P&L: {total_color}{total_sign}${total_realized_pnl:,.2f}{Style.RESET_ALL}")
        print(f"   📈 Winning Trades: {Fore.GREEN}{winning_trades}{Style.RESET_ALL}")
        print(f"   📉 Losing Trades: {Fore.RED}{losing_trades}{Style.RESET_ALL}")
        print(f"   🎯 Win Rate: {Fore.GREEN if win_rate >= 50 else Fore.RED}{win_rate:.1f}%{Style.RESET_ALL}")
        print(f"   📊 Total Trades: {len(sales_data)}")
    
    def display_portfolio_allocation(self):
        """Display how current portfolio compares to investment targets"""
        print(f"\n{Fore.BLUE}{'='*80}")
        print(f"⚖️  PORTFOLIO ALLOCATION ANALYSIS")
        print(f"{'='*80}{Style.RESET_ALL}")
        
        # Get total investment budget
        try:
            total_budget = float(self.investments_config.get('total_investment', 0))
        except:
            total_budget = 0
        
        if total_budget == 0:
            print(f"{Fore.YELLOW}⚠️  No investment budget set in investments.txt{Style.RESET_ALL}")
            return
        
        # Calculate current allocation
        current_holdings = self.short_trading_config.get('current_holdings', '').strip()
        
        if not current_holdings:
            print(f"💰 Investment Budget: ${total_budget:,.2f}")
            print(f"📊 Current Allocation: $0.00 (0.0%)")
            print(f"💵 Available Cash: ${total_budget:,.2f} (100.0%)")
            return
        
        # Calculate total invested
        holdings_list = [holding.strip() for holding in current_holdings.split('|')]
        total_invested = 0
        
        for holding in holdings_list:
            if not holding:
                continue
            parts = holding.split(',')
            if len(parts) == 4:
                try:
                    shares = int(parts[1].strip())
                    buy_price = float(parts[2].strip())
                    total_invested += shares * buy_price
                except ValueError:
                    continue
        
        # Calculate allocation percentages
        allocation_pct = (total_invested / total_budget) * 100 if total_budget > 0 else 0
        available_cash = total_budget - total_invested
        cash_pct = (available_cash / total_budget) * 100 if total_budget > 0 else 0
        
        print(f"💰 Investment Budget: ${total_budget:,.2f}")
        print(f"📊 Current Allocation: ${total_invested:,.2f} ({allocation_pct:.1f}%)")
        print(f"💵 Available Cash: ${available_cash:,.2f} ({cash_pct:.1f}%)")
        
        # Visual allocation bar
        if allocation_pct > 0:
            bar_length = 50
            filled_length = int(bar_length * allocation_pct / 100)
            bar = '█' * filled_length + '░' * (bar_length - filled_length)
            
            color = Fore.GREEN if allocation_pct <= 80 else Fore.YELLOW if allocation_pct <= 95 else Fore.RED
            print(f"📊 Allocation: {color}[{bar}] {allocation_pct:.1f}%{Style.RESET_ALL}")
        
        # Recommendations
        if allocation_pct > 95:
            print(f"{Fore.RED}⚠️  Portfolio is nearly fully allocated. Consider taking profits or adding capital.{Style.RESET_ALL}")
        elif allocation_pct < 50:
            print(f"{Fore.YELLOW}💡 Significant cash available. Consider additional investments.{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}✅ Portfolio allocation looks balanced.{Style.RESET_ALL}")
    
    def display_risk_analysis(self):
        """Display risk analysis based on current positions"""
        print(f"\n{Fore.RED}{'='*80}")
        print(f"🛡️  RISK ANALYSIS")
        print(f"{'='*80}{Style.RESET_ALL}")
        
        current_holdings = self.short_trading_config.get('current_holdings', '').strip()
        
        if not current_holdings:
            print(f"{Fore.YELLOW}📊 No positions to analyze{Style.RESET_ALL}")
            return
        
        # Parse holdings for risk analysis
        holdings_list = [holding.strip() for holding in current_holdings.split('|')]
        symbols = []
        position_sizes = {}
        
        total_portfolio_value = 0
        
        for holding in holdings_list:
            if not holding:
                continue
            parts = holding.split(',')
            if len(parts) == 4:
                try:
                    symbol = parts[0].strip()
                    shares = int(parts[1].strip())
                    buy_price = float(parts[2].strip())
                    position_value = shares * buy_price
                    
                    symbols.append(symbol)
                    position_sizes[symbol] = position_value
                    total_portfolio_value += position_value
                except ValueError:
                    continue
        
        if not symbols:
            print(f"{Fore.YELLOW}📊 No valid positions to analyze{Style.RESET_ALL}")
            return
        
        # Portfolio concentration analysis
        print(f"📊 Portfolio Concentration:")
        sorted_positions = sorted(position_sizes.items(), key=lambda x: x[1], reverse=True)
        
        for symbol, value in sorted_positions:
            percentage = (value / total_portfolio_value) * 100 if total_portfolio_value > 0 else 0
            
            if percentage > 30:
                risk_color = Fore.RED
                risk_level = "HIGH RISK"
            elif percentage > 20:
                risk_color = Fore.YELLOW  
                risk_level = "MODERATE"
            else:
                risk_color = Fore.GREEN
                risk_level = "BALANCED"
                
            print(f"   {symbol}: ${value:,.2f} ({risk_color}{percentage:.1f}% - {risk_level}{Style.RESET_ALL})")
        
        # Risk metrics
        max_loss_pct = float(self.short_trading_config.get('maximum_loss_percentage', 5))
        max_portfolio_loss = (total_portfolio_value * max_loss_pct) / 100
        
        print(f"\n🛡️  Risk Metrics:")
        print(f"   💰 Total Portfolio Value: ${total_portfolio_value:,.2f}")
        print(f"   📊 Number of Positions: {len(symbols)}")
        print(f"   🛑 Max Loss Tolerance: {max_loss_pct}% (${max_portfolio_loss:,.2f})")
        
        # Diversification score
        if len(symbols) >= 5:
            diversification = f"{Fore.GREEN}Good (5+ positions){Style.RESET_ALL}"
        elif len(symbols) >= 3:
            diversification = f"{Fore.YELLOW}Moderate (3-4 positions){Style.RESET_ALL}"
        else:
            diversification = f"{Fore.RED}Poor (<3 positions){Style.RESET_ALL}"
            
        print(f"   🎯 Diversification: {diversification}")
        
        # Check for over-concentration
        largest_position_pct = (max(position_sizes.values()) / total_portfolio_value) * 100 if position_sizes else 0
        if largest_position_pct > 40:
            print(f"\n{Fore.RED}⚠️  WARNING: Largest position exceeds 40% of portfolio. Consider rebalancing.{Style.RESET_ALL}")
        elif largest_position_pct > 25:
            print(f"\n{Fore.YELLOW}💡 Consider monitoring largest position (>{largest_position_pct:.1f}% of portfolio).{Style.RESET_ALL}")
    
    def generate_summary(self):
        """Generate complete portfolio summary"""
        print(f"\n{Style.BRIGHT}{Fore.CYAN}")
        print("=" * 100)
        print("🚀 INVESTMENT PORTFOLIO DASHBOARD")
        print(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 100)
        print(Style.RESET_ALL)
        
        # Load configurations
        self.load_configurations()
        
        # Display all sections
        self.display_investment_targets()
        self.display_current_holdings()
        self.display_sold_positions()
        self.display_portfolio_allocation()
        self.display_risk_analysis()
        
        # Footer
        print(f"\n{Style.BRIGHT}{Fore.CYAN}")
        print("=" * 100)
        print("💡 TIP: Run 'python main.py --short-trading' for real-time monitoring")
        print("📊 TIP: Use 'python main.py --compare SYMBOL1 SYMBOL2 --plot' for stock analysis")
        print("=" * 100)
        print(Style.RESET_ALL)

def main():
    """Main function to run the portfolio summary"""
    try:
        dashboard = PortfolioSummary()
        dashboard.generate_summary()
    except KeyboardInterrupt:
        print(f"\n\n✅ Portfolio summary interrupted by user")
    except Exception as e:
        print(f"\n❌ Error generating portfolio summary: {e}")

if __name__ == "__main__":
    main()
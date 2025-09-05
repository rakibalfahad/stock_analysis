"""
Portfolio optimization using Modern Portfolio Theory
"""

import yfinance as yf
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Tuple, Any, Optional

from ..utils.constants import (
    DEFAULT_PERIOD, DEFAULT_INTERVAL, DEFAULT_TARGET_RETURN,
    DEFAULT_RISK_PER_TRADE, DEFAULT_ATR_MULTIPLIER, EMOJIS
)
from ..utils.config import load_config, save_config, format_currency, format_percentage
from ..utils.helpers import (
    calculate_atr, calculate_returns, calculate_expected_return,
    calculate_volatility, portfolio_performance, is_in_cooling_period,
    format_recommendation, progress_bar
)

class InvestmentOptimizer:
    """
    Investment portfolio optimizer using Modern Portfolio Theory
    """
    
    def __init__(self, 
                 config_file: str = 'investments.txt',
                 target_return: float = DEFAULT_TARGET_RETURN,
                 risk_per_trade: float = DEFAULT_RISK_PER_TRADE,
                 atr_multiplier: float = DEFAULT_ATR_MULTIPLIER,
                 period: str = DEFAULT_PERIOD,
                 interval: str = DEFAULT_INTERVAL):
        """
        Initialize the optimizer
        
        Args:
            config_file: Path to configuration file
            target_return: Target annual return
            risk_per_trade: Risk per trade as fraction of capital
            atr_multiplier: ATR multiplier for stop-loss
            period: Data period for analysis
            interval: Data interval
        """
        self.config_file = config_file
        self.target_return = target_return
        self.risk_per_trade = risk_per_trade
        self.atr_multiplier = atr_multiplier
        self.period = period
        self.interval = interval
        
        # Load configuration
        self.config = load_config(config_file)
        self.tickers = list(self.config['stocks'].keys())
        
        # Market data storage
        self.data = None
        self.current_prices = {}
        self.atr_values = {}
        self.expected_returns = {}
        self.volatilities = {}
        
        # Optimization results
        self.optimal_weights = None
        self.portfolio_return = None
        self.portfolio_volatility = None
        
        logging.info(f"Optimizer initialized with {len(self.tickers)} stocks")
    
    def fetch_market_data(self) -> bool:
        """Fetch market data for all stocks"""
        try:
            print(f"\n{EMOJIS['chart']} Fetching market data...")
            
            # Download data for all tickers
            self.data = yf.download(self.tickers, period=self.period, interval=self.interval)
            
            if self.data.empty:
                logging.error("No market data retrieved")
                return False
            
            # Handle single vs multiple tickers
            if len(self.tickers) == 1:
                self.data = pd.DataFrame(self.data)
                self.data.columns = pd.MultiIndex.from_tuples(
                    [(col, self.tickers[0]) for col in self.data.columns]
                )
            
            # Calculate current prices and ATR values
            for ticker in self.tickers:
                try:
                    close_prices = self.data['Close'][ticker].dropna()
                    if not close_prices.empty:
                        self.current_prices[ticker] = float(close_prices.iloc[-1])
                        
                        # Calculate ATR
                        ticker_data = pd.DataFrame({
                            'High': self.data['High'][ticker],
                            'Low': self.data['Low'][ticker], 
                            'Close': self.data['Close'][ticker]
                        })
                        atr = calculate_atr(ticker_data)
                        self.atr_values[ticker] = float(atr.iloc[-1]) if not atr.empty else 0.0
                        
                except Exception as e:
                    logging.warning(f"Error processing {ticker}: {e}")
                    self.current_prices[ticker] = 0.0
                    self.atr_values[ticker] = 0.0
            
            print(f"{progress_bar(100, 100)} {EMOJIS['check']} Data fetched successfully")
            return True
            
        except Exception as e:
            logging.error(f"Error fetching market data: {e}")
            return False
    
    def calculate_portfolio_metrics(self) -> bool:
        """Calculate expected returns and volatilities"""
        try:
            for ticker in self.tickers:
                try:
                    returns = calculate_returns(
                        pd.DataFrame({'Close': self.data['Close'][ticker]})
                    )
                    
                    if not returns.empty:
                        self.expected_returns[ticker] = calculate_expected_return(returns)
                        self.volatilities[ticker] = calculate_volatility(returns)
                    else:
                        self.expected_returns[ticker] = 0.0
                        self.volatilities[ticker] = 0.1  # Default volatility
                        
                except Exception as e:
                    logging.warning(f"Error calculating metrics for {ticker}: {e}")
                    self.expected_returns[ticker] = 0.0
                    self.volatilities[ticker] = 0.1
            
            return True
            
        except Exception as e:
            logging.error(f"Error calculating portfolio metrics: {e}")
            return False
    
    def optimize_portfolio(self) -> bool:
        """Optimize portfolio using Modern Portfolio Theory"""
        try:
            print(f"{EMOJIS['computer']} Optimizing portfolio using Modern Portfolio Theory...")
            
            if not self.expected_returns or not self.volatilities:
                logging.error("Portfolio metrics not calculated")
                return False
            
            # Prepare data for optimization
            returns_array = np.array([self.expected_returns[ticker] for ticker in self.tickers])
            volatilities_array = np.array([self.volatilities[ticker] for ticker in self.tickers])
            
            # Create covariance matrix (simplified)
            cov_matrix = np.diag(volatilities_array ** 2)
            
            # Initial guess (equal weights)
            n_assets = len(self.tickers)
            initial_weights = np.array([1.0 / n_assets] * n_assets)
            
            # Constraints
            constraints = [
                {'type': 'eq', 'fun': lambda x: np.sum(x) - 1.0},  # Weights sum to 1
                {'type': 'ineq', 'fun': lambda x: np.dot(x, returns_array) - self.target_return}  # Target return
            ]
            
            # Bounds (0 to 1 for each weight)
            bounds = tuple((0, 1) for _ in range(n_assets))
            
            # Objective function (minimize portfolio variance)
            def objective(weights):
                return np.dot(weights.T, np.dot(cov_matrix, weights))
            
            # Optimize
            result = minimize(
                objective,
                initial_weights,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints
            )
            
            if result.success:
                self.optimal_weights = result.x
                self.portfolio_return, self.portfolio_volatility = portfolio_performance(
                    self.optimal_weights, returns_array, cov_matrix
                )
                print(f"{EMOJIS['check']} Optimization complete - Portfolio optimized!")
                return True
            else:
                logging.error(f"Optimization failed: {result.message}")
                return False
                
        except Exception as e:
            logging.error(f"Error in portfolio optimization: {e}")
            return False
    
    def get_trading_recommendations(self) -> Dict[str, Dict[str, Any]]:
        """Get trading recommendations based on optimization"""
        recommendations = {}
        total_capital = self.config['cash']
        
        for i, ticker in enumerate(self.tickers):
            current_holdings = self.config['stocks'][ticker]
            current_price = self.current_prices.get(ticker, 0)
            optimal_weight = self.optimal_weights[i] if self.optimal_weights is not None else 0
            
            # Check cooling period
            if is_in_cooling_period(current_holdings['last_sold']):
                recommendations[ticker] = {
                    'action': 'NO_ACTION_COOLING',
                    'current_price': current_price,
                    'details': {}
                }
                continue
            
            # Calculate optimal investment amount
            target_investment = total_capital * optimal_weight
            target_shares = int(target_investment / current_price) if current_price > 0 else 0
            current_shares = current_holdings['shares']
            
            # Determine action
            if target_shares > current_shares:
                # Buy recommendation
                shares_to_buy = target_shares - current_shares
                investment_amount = shares_to_buy * current_price
                
                # Calculate risk metrics
                atr = self.atr_values.get(ticker, 0)
                stop_loss = current_price - (self.atr_multiplier * atr)
                max_risk = shares_to_buy * (current_price - stop_loss)
                
                recommendations[ticker] = {
                    'action': 'BUY',
                    'shares': shares_to_buy,
                    'current_price': current_price,
                    'details': {
                        'stop_loss': stop_loss,
                        'max_risk': max_risk,
                        'expected_return': self.expected_returns.get(ticker, 0),
                        'portfolio_weight': optimal_weight
                    }
                }
            else:
                # Hold current position
                recommendations[ticker] = {
                    'action': 'HOLD',
                    'current_price': current_price,
                    'details': {}
                }
        
        return recommendations
    
    def print_analysis(self, recommendations: Dict[str, Dict[str, Any]]) -> None:
        """Print comprehensive portfolio analysis"""
        print("\n" + "=" * 70)
        print(f"{EMOJIS['chart']} PORTFOLIO ANALYSIS & RECOMMENDATIONS")
        print("=" * 70)
        
        # Current holdings
        print(f"\n{EMOJIS['money_bag']} Current Holdings:")
        total_value = 0
        has_holdings = False
        
        for ticker, data in self.config['stocks'].items():
            if data['shares'] > 0:
                current_price = self.current_prices.get(ticker, 0)
                value = data['shares'] * current_price
                total_value += value
                print(f"   {ticker}: {data['shares']} shares @ {format_currency(current_price)} = {format_currency(value)}")
                has_holdings = True
        
        if not has_holdings:
            print(f"   {EMOJIS['sleeping']} No current holdings")
        
        cash = self.config['cash']
        total_capital = cash + total_value
        print(f"   {EMOJIS['cash']} Cash Available: {format_currency(cash)} ({format_percentage(cash/total_capital * 100)})")
        
        # Recommendations
        print(f"\n{EMOJIS['dart']} Recommended Actions:")
        total_investment = 0
        
        for ticker, rec in recommendations.items():
            print(format_recommendation(
                ticker, 
                rec['action'], 
                rec['current_price'],
                rec.get('shares', 0),
                rec.get('details', {})
            ))
            
            if rec['action'] == 'BUY':
                total_investment += rec['shares'] * rec['current_price']
        
        # Investment summary
        print("\n" + "=" * 70)
        print(f"{EMOJIS['money_bag']} INVESTMENT SUMMARY")
        print("=" * 70)
        print(f"{EMOJIS['shopping_cart']} Total New Investment: {format_currency(total_investment)}")
        print(f"{EMOJIS['cash']} Cash After Investment: {format_currency(cash - total_investment)} ({format_percentage((cash - total_investment)/total_capital * 100)})")
        
        if self.portfolio_return and self.portfolio_volatility:
            sharpe = (self.portfolio_return - 0.02) / self.portfolio_volatility if self.portfolio_volatility > 0 else 0
            print(f"{EMOJIS['dart']} Portfolio Expected Return: {format_percentage(self.portfolio_return * 100)} annually")
            print(f"{EMOJIS['chart']} Portfolio Sharpe Ratio: {sharpe:.2f} (estimated)")
        
        # Calculate total risk
        total_risk = sum(
            rec.get('details', {}).get('max_risk', 0) 
            for rec in recommendations.values()
        )
        print(f"{EMOJIS['scales']} Total Portfolio Risk: {format_currency(total_risk)} ({format_percentage(total_risk/total_capital * 100)} of capital)")
    
    def run_optimization(self) -> bool:
        """Run complete optimization process"""
        try:
            # Display header
            print(f"\n{EMOJIS['fire']} INVESTMENT PORTFOLIO OPTIMIZER - MODULAR VERSION")
            print(f"{EMOJIS['calendar']} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {EMOJIS['dart']} Target: {format_percentage(self.target_return * 100)} | {EMOJIS['money_bag']} Capital: {format_currency(self.config['cash'])}")
            
            # Fetch data
            if not self.fetch_market_data():
                return False
            
            # Calculate metrics
            if not self.calculate_portfolio_metrics():
                return False
            
            # Optimize
            if not self.optimize_portfolio():
                return False
            
            # Get recommendations
            recommendations = self.get_trading_recommendations()
            
            # Print analysis
            self.print_analysis(recommendations)
            
            return True
            
        except Exception as e:
            logging.error(f"Error in optimization process: {e}")
            return False
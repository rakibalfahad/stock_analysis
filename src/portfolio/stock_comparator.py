"""
Stock Comparison Optimizer
Compares two stocks using normalized metrics and weighted scoring to recommend the better investment choice.
"""

import yfinance as yf
import pandas as pd
import numpy as np
import logging
import warnings
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta

# Suppress yfinance warnings
warnings.filterwarnings('ignore', category=FutureWarning, module='yfinance')
warnings.filterwarnings('ignore', message='.*auto_adjust.*')

from ..utils.constants import EMOJIS
from ..utils.config import format_currency, format_percentage, load_config

class StockComparator:
    """
    Advanced stock comparison system that evaluates two stocks across multiple dimensions:
    - Financial Health (P/E, EPS, ROE, debt ratios)
    - Growth Metrics (revenue growth, earnings growth)
    - Risk Assessment (beta, volatility)
    - Market Performance (price trends, momentum)
    - Dividend Analysis (yield, payout ratio)
    """
    
    def __init__(self, investment_strategy: str = 'balanced', config_file: str = 'investments.txt'):
        """
        Initialize stock comparator with investment strategy and configuration
        
        Args:
            investment_strategy: 'growth', 'value', 'income', 'stability', or 'balanced'
            config_file: Path to investment configuration file
        """
        self.investment_strategy = investment_strategy.lower()
        self.config_file = config_file
        
        # Load investment configuration
        self.config = load_config(config_file)
        self.total_investment = self.config.get('cash', 3000)
        self.target_gain = self.config.get('target_gain_percentage', 25) / 100.0
        self.max_loss = self.config.get('maximum_loss_percentage', 5) / 100.0
        self.preferred_stocks = list(self.config.get('stocks', {}).keys())
        
        # Adjust strategy based on risk tolerance from config
        risk_tolerance = self._determine_risk_tolerance()
        
        # Define key metrics to compare
        self.metrics = {
            'valuation': ['pe_ratio', 'pb_ratio', 'ps_ratio', 'peg_ratio'],
            'profitability': ['roe', 'roa', 'profit_margin', 'eps'],
            'growth': ['revenue_growth', 'earnings_growth', 'eps_growth'],
            'financial_health': ['debt_to_equity', 'current_ratio', 'quick_ratio'],
            'risk': ['beta', 'volatility'],
            'dividend': ['dividend_yield', 'payout_ratio'],
            'momentum': ['price_momentum_3m', 'price_momentum_1y', 'rsi']
        }
        
        # Strategy-based weights for different investment approaches
        self.strategy_weights = {
            'growth': {
                'valuation': 0.15, 'profitability': 0.20, 'growth': 0.35,
                'financial_health': 0.10, 'risk': 0.15, 'dividend': 0.05, 'momentum': 0.00
            },
            'value': {
                'valuation': 0.30, 'profitability': 0.25, 'growth': 0.15,
                'financial_health': 0.15, 'risk': 0.10, 'dividend': 0.05, 'momentum': 0.00
            },
            'income': {
                'valuation': 0.15, 'profitability': 0.20, 'growth': 0.10,
                'financial_health': 0.20, 'risk': 0.10, 'dividend': 0.25, 'momentum': 0.00
            },
            'stability': {
                'valuation': 0.15, 'profitability': 0.20, 'growth': 0.10,
                'financial_health': 0.25, 'risk': 0.20, 'dividend': 0.10, 'momentum': 0.00
            },
            'balanced': {
                'valuation': 0.20, 'profitability': 0.20, 'growth': 0.20,
                'financial_health': 0.15, 'risk': 0.15, 'dividend': 0.10, 'momentum': 0.00
            }
        }
        
        # Get base weights and adjust based on config
        base_weights = self.strategy_weights.get(investment_strategy, self.strategy_weights['balanced'])
        self.weights = self._adjust_weights_for_config(base_weights, risk_tolerance)
        self.comparisons = {}
        
        logging.info(f"Stock comparator initialized with '{investment_strategy}' strategy")
        logging.info(f"Config: ${self.total_investment:,.0f} investment, {self.target_gain:.0%} target gain, {self.max_loss:.0%} max loss")
        logging.info(f"Available stocks from config: {', '.join(self.preferred_stocks) if self.preferred_stocks else 'None'}")
    
    def _determine_risk_tolerance(self) -> str:
        """
        Determine risk tolerance based on investment configuration
        
        Returns:
            'conservative', 'moderate', or 'aggressive'
        """
        # Risk tolerance based on max loss percentage
        if self.max_loss <= 0.03:  # 3% or less
            return 'conservative'
        elif self.max_loss <= 0.07:  # 7% or less
            return 'moderate'
        else:  # More than 7%
            return 'aggressive'
    
    def _adjust_weights_for_config(self, base_weights: Dict[str, float], risk_tolerance: str) -> Dict[str, float]:
        """
        Adjust strategy weights based on investment configuration
        
        Args:
            base_weights: Base strategy weights
            risk_tolerance: Determined risk tolerance level
            
        Returns:
            Adjusted weights dictionary
        """
        adjusted_weights = base_weights.copy()
        
        # Adjust based on target gain (high target = more focus on growth)
        if self.target_gain >= 0.30:  # 30% or higher target
            adjusted_weights['growth'] = min(0.40, adjusted_weights['growth'] + 0.10)
            adjusted_weights['valuation'] = max(0.05, adjusted_weights['valuation'] - 0.05)
        elif self.target_gain <= 0.15:  # 15% or lower target
            adjusted_weights['financial_health'] = min(0.30, adjusted_weights['financial_health'] + 0.05)
            adjusted_weights['dividend'] = min(0.20, adjusted_weights['dividend'] + 0.05)
        
        # Adjust based on risk tolerance
        if risk_tolerance == 'conservative':
            adjusted_weights['risk'] = min(0.25, adjusted_weights['risk'] + 0.05)
            adjusted_weights['financial_health'] = min(0.30, adjusted_weights['financial_health'] + 0.05)
            adjusted_weights['growth'] = max(0.10, adjusted_weights['growth'] - 0.05)
        elif risk_tolerance == 'aggressive':
            adjusted_weights['growth'] = min(0.35, adjusted_weights['growth'] + 0.05)
            adjusted_weights['momentum'] = min(0.10, adjusted_weights['momentum'] + 0.05)
            adjusted_weights['risk'] = max(0.05, adjusted_weights['risk'] - 0.05)
        
        # Normalize weights to sum to 1.0
        total_weight = sum(adjusted_weights.values())
        if total_weight > 0:
            adjusted_weights = {k: v/total_weight for k, v in adjusted_weights.items()}
        
        return adjusted_weights
    
    def get_stock_data(self, symbol: str, period: str = "1y") -> Dict[str, Any]:
        """
        Fetch comprehensive stock data for analysis
        
        Args:
            symbol: Stock symbol
            period: Data period for analysis
            
        Returns:
            Dictionary containing all relevant metrics
        """
        try:
            print(f"📊 Fetching data for {symbol}...")
            
            # Get stock object and basic info
            stock = yf.Ticker(symbol)
            info = stock.info
            hist = stock.history(period=period)
            
            if hist.empty:
                raise ValueError(f"No historical data available for {symbol}")
            
            # Initialize metrics dictionary
            metrics = {
                'symbol': symbol,
                'company_name': info.get('longName', symbol),
                'sector': info.get('sector', 'Unknown'),
                'current_price': float(hist['Close'].iloc[-1]),
                'market_cap': info.get('marketCap', 0),
                'timestamp': datetime.now()
            }
            
            # Valuation metrics
            metrics.update({
                'pe_ratio': info.get('trailingPE', info.get('forwardPE')),
                'pb_ratio': info.get('priceToBook'),
                'ps_ratio': info.get('priceToSalesTrailing12Months'),
                'peg_ratio': info.get('pegRatio')
            })
            
            # Profitability metrics
            metrics.update({
                'roe': info.get('returnOnEquity'),
                'roa': info.get('returnOnAssets'),
                'profit_margin': info.get('profitMargins'),
                'eps': info.get('trailingEps', info.get('forwardEps'))
            })
            
            # Growth metrics
            metrics.update({
                'revenue_growth': info.get('revenueGrowth'),
                'earnings_growth': info.get('earningsGrowth'),
                'eps_growth': self._calculate_eps_growth(stock)
            })
            
            # Financial health metrics
            metrics.update({
                'debt_to_equity': info.get('debtToEquity'),
                'current_ratio': info.get('currentRatio'),
                'quick_ratio': info.get('quickRatio')
            })
            
            # Risk metrics
            returns = hist['Close'].pct_change().dropna()
            metrics.update({
                'beta': info.get('beta'),
                'volatility': returns.std() * np.sqrt(252) if len(returns) > 1 else None
            })
            
            # Dividend metrics
            metrics.update({
                'dividend_yield': info.get('dividendYield'),
                'payout_ratio': info.get('payoutRatio')
            })
            
            # Momentum metrics
            current_price = metrics['current_price']
            if len(hist) >= 63:  # 3 months of data
                price_3m_ago = hist['Close'].iloc[-63]
                metrics['price_momentum_3m'] = (current_price - price_3m_ago) / price_3m_ago
            else:
                metrics['price_momentum_3m'] = None
            
            if len(hist) >= 252:  # 1 year of data
                price_1y_ago = hist['Close'].iloc[-252]
                metrics['price_momentum_1y'] = (current_price - price_1y_ago) / price_1y_ago
            else:
                metrics['price_momentum_1y'] = None
            
            # RSI calculation
            if len(hist) >= 15:
                delta = hist['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
                metrics['rsi'] = float(rsi.iloc[-1]) if not rsi.empty else None
            else:
                metrics['rsi'] = None
            
            return metrics
            
        except Exception as e:
            logging.error(f"Error fetching data for {symbol}: {e}")
            return {
                'symbol': symbol,
                'error': str(e),
                'timestamp': datetime.now()
            }
    
    def _calculate_eps_growth(self, stock) -> Optional[float]:
        """Calculate EPS growth rate"""
        try:
            financials = stock.financials
            if financials.empty:
                return None
            
            # Get EPS data if available
            eps_data = []
            for col in financials.columns[:2]:  # Last 2 years
                try:
                    net_income = financials.loc['Net Income', col]
                    # Basic calculation - would need shares outstanding for accurate EPS
                    eps_data.append(net_income)
                except (KeyError, IndexError):
                    continue
            
            if len(eps_data) >= 2:
                return (eps_data[0] - eps_data[1]) / abs(eps_data[1]) if eps_data[1] != 0 else None
            
            return None
            
        except Exception as e:
            logging.debug(f"Could not calculate EPS growth: {e}")
            return None
    
    def normalize_metrics(self, stock1_data: Dict[str, Any], stock2_data: Dict[str, Any]) -> Tuple[Dict[str, float], Dict[str, float]]:
        """
        Normalize metrics to 0-1 scale for fair comparison
        
        Returns:
            Tuple of normalized metrics for both stocks
        """
        normalized_1 = {}
        normalized_2 = {}
        
        for category, metric_list in self.metrics.items():
            for metric in metric_list:
                val1 = stock1_data.get(metric)
                val2 = stock2_data.get(metric)
                
                # Skip if either value is missing
                if val1 is None or val2 is None:
                    normalized_1[metric] = 0.5  # Neutral score
                    normalized_2[metric] = 0.5
                    continue
                
                # Handle special cases and normalization
                norm1, norm2 = self._normalize_metric_pair(metric, val1, val2)
                normalized_1[metric] = norm1
                normalized_2[metric] = norm2
        
        return normalized_1, normalized_2
    
    def _normalize_metric_pair(self, metric: str, val1: float, val2: float) -> Tuple[float, float]:
        """
        Normalize a pair of metric values
        
        Returns higher score for better metric value
        """
        try:
            # Metrics where lower is better
            lower_is_better = [
                'pe_ratio', 'pb_ratio', 'ps_ratio', 'peg_ratio',
                'debt_to_equity', 'beta', 'volatility', 'payout_ratio'
            ]
            
            # Special handling for specific metrics
            if metric == 'rsi':
                # RSI: 30-70 range is ideal, penalize extremes
                ideal_rsi = 50
                score1 = 1 - abs(val1 - ideal_rsi) / 50
                score2 = 1 - abs(val2 - ideal_rsi) / 50
                return max(0, score1), max(0, score2)
            
            elif metric in ['dividend_yield']:
                # For dividend yield, moderate values are often better than extreme high
                if val1 == 0 and val2 == 0:
                    return 0.5, 0.5
                elif val1 == 0:
                    return 0.2, 0.8
                elif val2 == 0:
                    return 0.8, 0.2
                # Normalize with preference for reasonable dividend yields (2-6%)
                optimal_range = (0.02, 0.06)
                score1 = 1 if optimal_range[0] <= val1 <= optimal_range[1] else 0.7
                score2 = 1 if optimal_range[0] <= val2 <= optimal_range[1] else 0.7
                if val1 > val2:
                    return min(1, score1 * 1.1), score2
                else:
                    return score1, min(1, score2 * 1.1)
            
            # Handle negative values specially
            if val1 < 0 or val2 < 0:
                if val1 < 0 and val2 < 0:
                    # Both negative - less negative is better
                    if metric in lower_is_better:
                        return (0.3, 0.7) if val1 < val2 else (0.7, 0.3)
                    else:
                        return (0.7, 0.3) if val1 > val2 else (0.3, 0.7)
                elif val1 < 0:
                    return 0.2, 0.8  # Negative is bad
                else:
                    return 0.8, 0.2  # Negative is bad
            
            # Standard normalization for positive values
            if val1 == val2:
                return 0.5, 0.5
            
            if metric in lower_is_better:
                # Lower value gets higher score
                min_val, max_val = min(val1, val2), max(val1, val2)
                range_val = max_val - min_val
                if range_val == 0:
                    return 0.5, 0.5
                score1 = 1 - (val1 - min_val) / range_val
                score2 = 1 - (val2 - min_val) / range_val
            else:
                # Higher value gets higher score
                min_val, max_val = min(val1, val2), max(val1, val2)
                range_val = max_val - min_val
                if range_val == 0:
                    return 0.5, 0.5
                score1 = (val1 - min_val) / range_val
                score2 = (val2 - min_val) / range_val
            
            return score1, score2
            
        except Exception as e:
            logging.debug(f"Error normalizing {metric}: {e}")
            return 0.5, 0.5
    
    def calculate_scores(self, normalized_1: Dict[str, float], normalized_2: Dict[str, float]) -> Tuple[float, float, Dict[str, Tuple[float, float]]]:
        """
        Calculate weighted scores for both stocks
        
        Returns:
            Tuple of (score1, score2, category_scores)
        """
        total_score_1 = 0
        total_score_2 = 0
        category_scores = {}
        
        for category, weight in self.weights.items():
            if weight == 0:
                continue
                
            metrics_in_category = self.metrics[category]
            category_score_1 = 0
            category_score_2 = 0
            valid_metrics = 0
            
            for metric in metrics_in_category:
                if metric in normalized_1 and metric in normalized_2:
                    category_score_1 += normalized_1[metric]
                    category_score_2 += normalized_2[metric]
                    valid_metrics += 1
            
            if valid_metrics > 0:
                # Average the metrics in this category
                category_score_1 /= valid_metrics
                category_score_2 /= valid_metrics
                
                # Apply category weight
                total_score_1 += category_score_1 * weight
                total_score_2 += category_score_2 * weight
                
                category_scores[category] = (category_score_1, category_score_2)
        
        return total_score_1, total_score_2, category_scores
    
    def get_recommended_stocks(self, min_stocks: int = 2) -> List[str]:
        """
        Get list of stocks to compare from preferred stocks or fallback
        
        Args:
            min_stocks: Minimum number of stocks needed
            
        Returns:
            List of stock tickers to analyze
        """
        stocks = []
        
        # First try preferred stocks from config
        if self.preferred_stocks and len(self.preferred_stocks) >= min_stocks:
            stocks = self.preferred_stocks[:10]  # Limit to first 10
            logging.info(f"Using preferred stocks from config: {', '.join(stocks)}")
        else:
            # Fallback to default popular stocks
            fallback_stocks = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX']
            stocks = fallback_stocks[:max(min_stocks, 5)]
            if self.preferred_stocks:
                logging.warning(f"Not enough preferred stocks ({len(self.preferred_stocks)}), using fallback: {', '.join(stocks)}")
            else:
                logging.info(f"No preferred stocks configured, using popular stocks: {', '.join(stocks)}")
        
        return stocks
    
    def _meets_investment_criteria(self, stock_data: Dict[str, Any], stock: str) -> bool:
        """
        Check if stock meets investment criteria from config
        
        Args:
            stock_data: Stock data dictionary
            stock: Stock ticker
            
        Returns:
            True if stock meets criteria
        """
        try:
            # Check volatility against max loss
            volatility = stock_data.get('volatility', 0)
            if volatility and volatility > self.max_loss * 2:  # Conservative threshold
                return False
            
            # Check if stock has reasonable fundamentals
            pe_ratio = stock_data.get('pe_ratio', 0)
            if pe_ratio and (pe_ratio <= 0 or pe_ratio > 50):  # Avoid negative or extremely high P/E
                return False
            
            return True
            
        except Exception as e:
            logging.warning(f"Error checking investment criteria for {stock}: {str(e)}")
            return True  # Default to allow if check fails

    def compare_stocks(self, symbol1: str, symbol2: str) -> Dict[str, Any]:
        """
        Perform comprehensive comparison between two stocks
        
        Returns:
            Detailed comparison results with recommendation
        """
        print(f"\n{EMOJIS['magnifying_glass']} STOCK COMPARISON: {symbol1.upper()} vs {symbol2.upper()}")
        print("=" * 70)
        
        # Check if stocks are in preferred list (if configured)
        if self.preferred_stocks:
            for stock in [symbol1, symbol2]:
                if stock.upper() not in [s.upper() for s in self.preferred_stocks]:
                    print(f"{EMOJIS['warning']} {stock.upper()} not in preferred list: {', '.join(self.preferred_stocks)}")
        
        # Fetch data for both stocks
        stock1_data = self.get_stock_data(symbol1)
        stock2_data = self.get_stock_data(symbol2)
        
        # Check for errors
        if 'error' in stock1_data or 'error' in stock2_data:
            error_msg = []
            if 'error' in stock1_data:
                error_msg.append(f"{symbol1}: {stock1_data['error']}")
            if 'error' in stock2_data:
                error_msg.append(f"{symbol2}: {stock2_data['error']}")
            return {
                'error': ' | '.join(error_msg),
                'timestamp': datetime.now()
            }
        
        # Apply investment criteria checks
        stock1_meets_criteria = self._meets_investment_criteria(stock1_data, symbol1)
        stock2_meets_criteria = self._meets_investment_criteria(stock2_data, symbol2)
        
        if not stock1_meets_criteria:
            print(f"{EMOJIS['warning']} {symbol1.upper()} doesn't meet investment criteria (max loss: {self.max_loss:.1%})")
        if not stock2_meets_criteria:
            print(f"{EMOJIS['warning']} {symbol2.upper()} doesn't meet investment criteria (max loss: {self.max_loss:.1%})")
        
        # Normalize metrics
        print(f"\n{EMOJIS['computer']} Normalizing metrics for fair comparison...")
        normalized_1, normalized_2 = self.normalize_metrics(stock1_data, stock2_data)
        
        # Calculate scores
        print(f"{EMOJIS['dart']} Calculating weighted scores based on '{self.investment_strategy}' strategy...")
        score1, score2, category_scores = self.calculate_scores(normalized_1, normalized_2)
        
        # Determine recommendation
        if abs(score1 - score2) < 0.05:  # Very close scores
            recommendation = "NEUTRAL"
            confidence = 0.6
            winner = None
        elif score1 > score2:
            recommendation = symbol1.upper()
            confidence = min(0.9, 0.7 + (score1 - score2))
            winner = 1
        else:
            recommendation = symbol2.upper()
            confidence = min(0.9, 0.7 + (score2 - score1))
            winner = 2
        
        # Calculate position size based on total investment
        position_size = self.total_investment / 2  # Simple 50/50 split for comparison
        
        # Compile results
        comparison_result = {
            'symbol1': symbol1.upper(),
            'symbol2': symbol2.upper(),
            'stock1_data': stock1_data,
            'stock2_data': stock2_data,
            'normalized_metrics': {
                'stock1': normalized_1,
                'stock2': normalized_2
            },
            'scores': {
                'stock1': score1,
                'stock2': score2,
                'difference': abs(score1 - score2)
            },
            'category_scores': category_scores,
            'recommendation': {
                'choice': recommendation,
                'confidence': confidence,
                'winner': winner
            },
            'strategy': self.investment_strategy,
            'weights_used': self.weights,
            'investment_config': {
                'total_investment': self.total_investment,
                'target_gain': self.target_gain,
                'max_loss': self.max_loss,
                'position_size': position_size,
                'risk_tolerance': self._determine_risk_tolerance(),
                'meets_criteria': {
                    'stock1': stock1_meets_criteria,
                    'stock2': stock2_meets_criteria
                }
            },
            'timestamp': datetime.now()
        }
        
        self.comparisons[f"{symbol1}_{symbol2}"] = comparison_result
        return comparison_result
    
    def print_comparison_results(self, comparison_result: Dict[str, Any]) -> None:
        """Print detailed comparison results"""
        if 'error' in comparison_result:
            print(f"{EMOJIS['warning']} Comparison Error: {comparison_result['error']}")
            return
        
        symbol1 = comparison_result['symbol1']
        symbol2 = comparison_result['symbol2']
        stock1_data = comparison_result['stock1_data']
        stock2_data = comparison_result['stock2_data']
        scores = comparison_result['scores']
        category_scores = comparison_result['category_scores']
        rec = comparison_result['recommendation']
        
        print(f"\n{EMOJIS['chart']} DETAILED COMPARISON RESULTS")
        print("=" * 70)
        
        # Basic info
        print(f"\n{EMOJIS['building']} Company Information:")
        print(f"   {symbol1}: {stock1_data.get('company_name', 'N/A')} ({stock1_data.get('sector', 'Unknown')})")
        print(f"   {symbol2}: {stock2_data.get('company_name', 'N/A')} ({stock2_data.get('sector', 'Unknown')})")
        
        # Current prices and market caps
        print(f"\n{EMOJIS['money_bag']} Market Data:")
        print(f"   {symbol1}: {format_currency(stock1_data['current_price'])} | Market Cap: ${stock1_data.get('market_cap', 0)/1e9:.1f}B")
        print(f"   {symbol2}: {format_currency(stock2_data['current_price'])} | Market Cap: ${stock2_data.get('market_cap', 0)/1e9:.1f}B")
        
        # Category scores
        print(f"\n{EMOJIS['dart']} Category Analysis ({self.investment_strategy.title()} Strategy):")
        for category, (score1, score2) in category_scores.items():
            weight = self.weights[category]
            if weight > 0:
                winner_emoji = "🥇" if score1 > score2 else "🥈" if score1 == score2 else "🥉"
                loser_emoji = "🥉" if score1 > score2 else "🥈" if score1 == score2 else "🥇"
                
                print(f"   {category.title().replace('_', ' ')} (Weight: {weight:.0%}):")
                print(f"      {winner_emoji if score1 >= score2 else loser_emoji} {symbol1}: {score1:.2f}")
                print(f"      {loser_emoji if score1 >= score2 else winner_emoji} {symbol2}: {score2:.2f}")
        
        # Final scores
        print(f"\n{EMOJIS['trophy']} FINAL SCORES:")
        print(f"   🎯 {symbol1}: {scores['stock1']:.3f}")
        print(f"   🎯 {symbol2}: {scores['stock2']:.3f}")
        print(f"   📊 Score Difference: {scores['difference']:.3f}")
        
        # Investment configuration
        if 'investment_config' in comparison_result:
            config = comparison_result['investment_config']
            print(f"\n{EMOJIS['money_bag']} INVESTMENT CONFIGURATION:")
            print(f"   💰 Total Investment: ${config['total_investment']:,.0f}")
            print(f"   📈 Target Gain: {config['target_gain']:.1%}")
            print(f"   🛡️ Max Loss Tolerance: {config['max_loss']:.1%}")
            print(f"   ⚖️ Risk Tolerance: {config['risk_tolerance'].title()}")
            print(f"   💵 Position Size (per stock): ${config['position_size']:,.0f}")
            
            # Investment criteria check
            criteria = config['meets_criteria']
            print(f"\n{EMOJIS['checkmark']} INVESTMENT CRITERIA:")
            print(f"   {symbol1}: {'✅ MEETS CRITERIA' if criteria['stock1'] else '❌ FAILS CRITERIA'}")
            print(f"   {symbol2}: {'✅ MEETS CRITERIA' if criteria['stock2'] else '❌ FAILS CRITERIA'}")
        
        # Recommendation
        print(f"\n{EMOJIS['rocket']} RECOMMENDATION:")
        if rec['choice'] == 'NEUTRAL':
            print(f"   🤝 Both stocks are very similar ({rec['confidence']:.0%} confidence)")
            print(f"   💡 Consider other factors like your portfolio balance or personal preference")
        else:
            confidence_emoji = "🔥" if rec['confidence'] > 0.8 else "✅" if rec['confidence'] > 0.7 else "⚖️"
            print(f"   {confidence_emoji} BUY {rec['choice']} (Confidence: {rec['confidence']:.0%})")
            
            winner_data = stock1_data if rec['winner'] == 1 else stock2_data
            loser_symbol = symbol2 if rec['winner'] == 1 else symbol1
            
            # Key advantages
            print(f"   💪 Key Advantages of {rec['choice']}:")
            advantages = self._identify_key_advantages(comparison_result)
            for advantage in advantages[:3]:  # Top 3 advantages
                print(f"      • {advantage}")
    
    def _identify_key_advantages(self, comparison_result: Dict[str, Any]) -> List[str]:
        """Identify key advantages of the winning stock"""
        advantages = []
        
        winner = comparison_result['recommendation']['winner']
        if winner is None:
            return advantages
        
        symbol1 = comparison_result['symbol1']
        symbol2 = comparison_result['symbol2']
        stock1_data = comparison_result['stock1_data']
        stock2_data = comparison_result['stock2_data']
        
        winner_data = stock1_data if winner == 1 else stock2_data
        winner_symbol = symbol1 if winner == 1 else symbol2
        loser_data = stock2_data if winner == 1 else stock1_data
        
        # Check key metrics for advantages
        if winner_data.get('pe_ratio') and loser_data.get('pe_ratio'):
            if winner_data['pe_ratio'] < loser_data['pe_ratio'] * 0.8:
                advantages.append(f"Better valuation (P/E: {winner_data['pe_ratio']:.1f} vs {loser_data['pe_ratio']:.1f})")
        
        if winner_data.get('roe') and loser_data.get('roe'):
            if winner_data['roe'] > loser_data['roe'] * 1.2:
                advantages.append(f"Higher profitability (ROE: {winner_data['roe']:.1%} vs {loser_data['roe']:.1%})")
        
        if winner_data.get('revenue_growth') and loser_data.get('revenue_growth'):
            if winner_data['revenue_growth'] > loser_data['revenue_growth'] * 1.5:
                advantages.append(f"Stronger growth (Revenue: {winner_data['revenue_growth']:.1%} vs {loser_data['revenue_growth']:.1%})")
        
        if winner_data.get('debt_to_equity') and loser_data.get('debt_to_equity'):
            if winner_data['debt_to_equity'] < loser_data['debt_to_equity'] * 0.7:
                advantages.append(f"Better financial health (D/E: {winner_data['debt_to_equity']:.1f}% vs {loser_data['debt_to_equity']:.1f}%)")
        
        if winner_data.get('dividend_yield') and loser_data.get('dividend_yield'):
            if winner_data['dividend_yield'] > loser_data['dividend_yield'] * 1.3:
                advantages.append(f"Higher dividend income ({winner_data['dividend_yield']:.1%} vs {loser_data['dividend_yield']:.1%})")
        
        if not advantages:
            advantages.append("More balanced overall performance across all metrics")
        
        return advantages
    
    def get_detailed_metrics_comparison(self, comparison_result: Dict[str, Any]) -> pd.DataFrame:
        """
        Generate a detailed metrics comparison table
        
        Returns:
            DataFrame with side-by-side metric comparison
        """
        if 'error' in comparison_result:
            return pd.DataFrame()
        
        stock1_data = comparison_result['stock1_data']
        stock2_data = comparison_result['stock2_data']
        symbol1 = comparison_result['symbol1']
        symbol2 = comparison_result['symbol2']
        
        comparison_data = []
        
        for category, metric_list in self.metrics.items():
            for metric in metric_list:
                val1 = stock1_data.get(metric)
                val2 = stock2_data.get(metric)
                
                # Format values appropriately
                if val1 is not None and val2 is not None:
                    if 'ratio' in metric or 'margin' in metric or 'yield' in metric or 'growth' in metric:
                        val1_str = f"{val1:.1%}" if isinstance(val1, (int, float)) else str(val1)
                        val2_str = f"{val2:.1%}" if isinstance(val2, (int, float)) else str(val2)
                    elif metric == 'eps':
                        val1_str = f"${val1:.2f}" if isinstance(val1, (int, float)) else str(val1)
                        val2_str = f"${val2:.2f}" if isinstance(val2, (int, float)) else str(val2)
                    else:
                        val1_str = f"{val1:.2f}" if isinstance(val1, (int, float)) else str(val1)
                        val2_str = f"{val2:.2f}" if isinstance(val2, (int, float)) else str(val2)
                else:
                    val1_str = "N/A" if val1 is None else str(val1)
                    val2_str = "N/A" if val2 is None else str(val2)
                
                comparison_data.append({
                    'Category': category.title().replace('_', ' '),
                    'Metric': metric.title().replace('_', ' '),
                    symbol1: val1_str,
                    symbol2: val2_str
                })
        
        return pd.DataFrame(comparison_data)
"""
Helper functions for calculations and data processing
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any
from datetime import datetime, timedelta

def calculate_atr(data: pd.DataFrame, period: int = 14) -> pd.Series:
    """Calculate Average True Range (ATR)"""
    high = data['High']
    low = data['Low'] 
    close = data['Close']
    
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = true_range.rolling(window=period).mean()
    
    return atr

def calculate_returns(data: pd.DataFrame) -> pd.Series:
    """Calculate daily returns"""
    return data['Close'].pct_change().dropna()

def calculate_expected_return(returns: pd.Series, method: str = 'mean') -> float:
    """Calculate expected return"""
    if method == 'mean':
        return returns.mean() * 252  # Annualized
    elif method == 'geometric':
        return (1 + returns).prod() ** (252 / len(returns)) - 1
    else:
        return returns.mean() * 252

def calculate_volatility(returns: pd.Series) -> float:
    """Calculate annualized volatility"""
    return returns.std() * np.sqrt(252)

def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.02) -> float:
    """Calculate Sharpe ratio"""
    excess_returns = returns.mean() * 252 - risk_free_rate
    volatility = calculate_volatility(returns)
    return excess_returns / volatility if volatility > 0 else 0

def portfolio_performance(weights: np.ndarray, 
                         expected_returns: np.ndarray, 
                         cov_matrix: np.ndarray) -> Tuple[float, float]:
    """Calculate portfolio expected return and volatility"""
    portfolio_return = np.sum(weights * expected_returns)
    portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
    return portfolio_return, portfolio_volatility

def is_in_cooling_period(last_sold_date: datetime.date, 
                        cooling_days: int = 30) -> bool:
    """Check if stock is in cooling period"""
    if last_sold_date is None:
        return False
    
    days_since_sold = (datetime.now().date() - last_sold_date).days
    return days_since_sold < cooling_days

def format_recommendation(symbol: str, action: str, 
                         current_price: float, 
                         shares: int = 0, 
                         details: Dict[str, Any] = None) -> str:
    """Format trading recommendation"""
    from .constants import EMOJIS
    from .config import format_currency, format_percentage
    
    if details is None:
        details = {}
    
    emoji_map = {
        'AAPL': EMOJIS['apple'],
        'GOOGL': EMOJIS['google'], 
        'MSFT': EMOJIS['microsoft'],
        'AMZN': EMOJIS['amazon']
    }
    
    emoji = emoji_map.get(symbol, EMOJIS['chart'])
    
    if action == 'BUY':
        investment_amount = shares * current_price
        stop_loss = details.get('stop_loss', 0)
        max_risk = details.get('max_risk', 0)
        expected_return = details.get('expected_return', 0)
        portfolio_weight = details.get('portfolio_weight', 0)
        
        return f"""
{emoji} {symbol}: {EMOJIS['shopping_cart']} BUY RECOMMENDATION
   {EMOJIS['money_bag']} Current Price: {format_currency(current_price)}
   {EMOJIS['up_trend']} Recommended: +{shares} shares ({format_currency(investment_amount)})
   {EMOJIS['chart']} Portfolio Weight: {format_percentage(portfolio_weight * 100)} (optimal)
   {EMOJIS['shield']} Stop-Loss: {format_currency(stop_loss)} | Max Risk: {format_currency(max_risk)}
   {EMOJIS['dart']} Expected Return: {format_percentage(expected_return * 100)} annually"""
    
    elif action == 'HOLD':
        return f"{emoji} {symbol}: {EMOJIS['hold']} Hold current position"
    
    elif action == 'NO_ACTION_COOLING':
        return f"""
{emoji} {symbol}: {EMOJIS['pause']} No action - Recently sold
   {EMOJIS['warning']} 30-day cooling period active"""
    
    else:
        return f"{emoji} {symbol}: No recommendation available"

def progress_bar(current: int, total: int, width: int = 40) -> str:
    """Create a progress bar"""
    progress = current / total
    filled = int(width * progress)
    bar = '█' * filled + ' ' * (width - filled)
    percentage = int(progress * 100)
    return f"{bar} {percentage}%"
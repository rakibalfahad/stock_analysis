"""
Constants and configuration for the investment optimizer
"""

# Emoji constants for terminal output
EMOJIS = {
    'fire': '🔥',
    'calendar': '📅',
    'target': '🎯',
    'money_bag': '💰',
    'chart': '📊',
    'computer': '🧮',
    'check': '✅',
    'warning': '⚠️',
    'apple': '🍎',
    'google': '🔍',
    'microsoft': '💻',
    'amazon': '📦',
    'pause': '⏸️',
    'shopping_cart': '🛒',
    'up_trend': '📈',
    'shield': '🛡️',
    'dart': '🎯',
    'sleeping': '💤',
    'cash': '💵',
    'hold': '📊',
    'rocket': '🚀',
    'scales': '⚖️',
    'green_circle': '🟢',
    'yellow_circle': '🟡',
    'red_circle': '🔴',
    'folder': '📁',
    'trash': '🗑️',
    'magnifying_glass': '🔍'
}

# Default stock configuration
DEFAULT_STOCKS = {
    'AAPL': {'shares': 0, 'purchase_price': 0.0, 'last_sold': None},
    'GOOGL': {'shares': 0, 'purchase_price': 0.0, 'last_sold': None}, 
    'MSFT': {'shares': 0, 'purchase_price': 0.0, 'last_sold': None},
    'AMZN': {'shares': 0, 'purchase_price': 0.0, 'last_sold': None}
}

# Market data configuration
DEFAULT_PERIOD = '6mo'
DEFAULT_INTERVAL = '1d'

# Optimization parameters
DEFAULT_TARGET_RETURN = 0.20
DEFAULT_RISK_PER_TRADE = 0.02
DEFAULT_ATR_MULTIPLIER = 2.0
DEFAULT_COOLING_PERIOD_DAYS = 30

# File names
CONFIG_FILE = 'investments.txt'
DASHBOARD_FILE = 'portfolio_dashboard.png'

# Colors for visualization
COLORS = {
    'high_gain': '#2E8B57',    # Green - high gain/risk ratio
    'moderate_gain': '#FFD700',  # Yellow - moderate gain/risk ratio  
    'low_gain': '#CD5C5C',     # Red - lower gain/risk ratio
    'primary': '#1f77b4',
    'secondary': '#ff7f0e', 
    'success': '#2ca02c',
    'warning': '#d62728',
    'info': '#9467bd'
}

# Gain-to-risk ratio thresholds
GAIN_RISK_THRESHOLDS = {
    'high': 2.5,
    'moderate': 2.0
}
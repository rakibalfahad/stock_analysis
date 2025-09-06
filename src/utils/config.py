"""
Configuration and file handling utilities
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from .constants import DEFAULT_STOCKS, CONFIG_FILE

def setup_logging(log_level: str = 'INFO') -> None:
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('investment_optimizer.log'),
            logging.StreamHandler()
        ]
    )

def load_config(config_file: str = CONFIG_FILE) -> Dict[str, Any]:
    """Load configuration from file"""
    config = {
        'cash': 10000.0,
        'stocks': DEFAULT_STOCKS.copy()
    }
    
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                lines = f.readlines()
                
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Handle new format: key = value
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    if key == 'total_investment':
                        config['cash'] = float(value)
                    elif key == 'target_gain_percentage':
                        # Store target gain percentage for potential use
                        config['target_gain_percentage'] = float(value)
                    elif key == 'preferred_stocks':
                        # Update stocks based on preferred list
                        stock_symbols = [s.strip() for s in value.split(',')]
                        config['stocks'] = {}
                        for symbol in stock_symbols:
                            config['stocks'][symbol] = {
                                'shares': 0,
                                'purchase_price': 0.0,
                                'last_sold': None
                            }
                
                # Handle old format: CASH: value
                elif line.startswith('CASH:'):
                    config['cash'] = float(line.split(':')[1].strip())
                elif ':' in line and not line.startswith('sold_stocks'):
                    parts = line.split(':')
                    if len(parts) >= 3:
                        symbol = parts[0].strip()
                        shares = int(parts[1].strip())
                        price = float(parts[2].strip())
                        last_sold = parts[3].strip() if len(parts) > 3 and parts[3].strip() else None
                        
                        if last_sold:
                            try:
                                last_sold = datetime.strptime(last_sold, '%Y-%m-%d').date()
                            except ValueError:
                                last_sold = None
                        
                        config['stocks'][symbol] = {
                            'shares': shares,
                            'purchase_price': price,
                            'last_sold': last_sold
                        }
                
                # Handle sold_stocks section
                elif line.startswith('sold_stocks:'):
                    # Process sold stocks that follow
                    continue
                elif line and ',' in line and len(line.split(',')) >= 3:
                    # This might be a sold stock entry: SYMBOL,PRICE,DATE
                    parts = line.split(',')
                    if len(parts) >= 3:
                        symbol = parts[0].strip()
                        if symbol in config['stocks']:
                            try:
                                # Update last_sold date for this stock
                                sold_date = datetime.strptime(parts[2].strip(), '%Y-%m-%d').date()
                                config['stocks'][symbol]['last_sold'] = sold_date
                            except ValueError:
                                pass  # Invalid date format, ignore
                        
        except Exception as e:
            logging.warning(f"Error loading config file {config_file}: {e}")
    
    return config

def save_config(config: Dict[str, Any], config_file: str = CONFIG_FILE) -> None:
    """Save configuration to file"""
    try:
        with open(config_file, 'w') as f:
            f.write(f"CASH: {config['cash']:.2f}\n")
            f.write("# Format: SYMBOL:SHARES:PURCHASE_PRICE:LAST_SOLD_DATE\n")
            
            for symbol, data in config['stocks'].items():
                last_sold = data['last_sold'].strftime('%Y-%m-%d') if data['last_sold'] else ''
                f.write(f"{symbol}:{data['shares']}:{data['purchase_price']:.2f}:{last_sold}\n")
                
        logging.info(f"Configuration saved to {config_file}")
    except Exception as e:
        logging.error(f"Error saving config file {config_file}: {e}")

def format_currency(amount: float) -> str:
    """Format currency with commas"""
    return f"${amount:,.2f}"

def format_percentage(value: float) -> str:
    """Format percentage"""
    return f"{value:.1f}%"

def get_color_for_gain_risk_ratio(ratio: float) -> str:
    """Get color based on gain-to-risk ratio"""
    from .constants import COLORS, GAIN_RISK_THRESHOLDS
    
    if ratio > GAIN_RISK_THRESHOLDS['high']:
        return COLORS['high_gain']
    elif ratio > GAIN_RISK_THRESHOLDS['moderate']:
        return COLORS['moderate_gain']
    else:
        return COLORS['low_gain']
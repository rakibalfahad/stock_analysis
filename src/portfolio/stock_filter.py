"""
Stock filtering and recommendation system based on financial metrics
Analyzes stocks and provides buy/avoid recommendations based on various criteria
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
from ..utils.config import format_currency, format_percentage

class StockFilter:
    """
    Advanced stock filtering system that analyzes stocks based on multiple criteria:
    - Risk metrics (volatility, beta)
    - Valuation (P/E ratio, P/B ratio)
    - Financial health (debt ratios, profitability)
    - Market dynamics (volume, float, liquidity)
    - Technical indicators (momentum, trend)
    """
    
    def __init__(self, 
                 filtering_mode: str = 'moderate',
                 min_market_cap: float = 1e9,   # $1B
                 min_volume: float = 1e6,       # $1M daily volume
                 max_debt_to_equity: float = 1.0):
        """
        Initialize adaptive stock filter
        
        Args:
            filtering_mode: Risk tolerance - 'conservative', 'moderate', or 'aggressive'
            min_market_cap: Minimum market capitalization
            min_volume: Minimum daily trading volume (in dollars)
            max_debt_to_equity: Maximum debt-to-equity ratio
        """
        self.filtering_mode = filtering_mode.lower()
        self.min_market_cap = min_market_cap
        self.min_volume = min_volume
        self.max_debt_to_equity = max_debt_to_equity
        
        # Adaptive thresholds - will be determined after analyzing stocks
        self.max_pe_ratio = None
        self.max_volatility = None
        self.max_beta = None
        
        # Mode-specific base parameters
        self.mode_params = {
            'conservative': {
                'pe_percentile': 40,      # Use 40th percentile as max
                'vol_percentile': 40,     # Use 40th percentile as max
                'beta_max': 1.2,
                'min_stocks_target': 3    # Aim to select at least 3 stocks
            },
            'moderate': {
                'pe_percentile': 60,      # Use 60th percentile as max
                'vol_percentile': 60,     # Use 60th percentile as max
                'beta_max': 1.5,
                'min_stocks_target': 5    # Aim to select at least 5 stocks
            },
            'aggressive': {
                'pe_percentile': 80,      # Use 80th percentile as max
                'vol_percentile': 80,     # Use 80th percentile as max
                'beta_max': 2.0,
                'min_stocks_target': 7    # Aim to select at least 7 stocks
            }
        }
        
        self.stock_analyses = {}
        
        logging.info(f"Adaptive stock filter initialized in '{filtering_mode}' mode")
        logging.info(f"  Min Market Cap: ${min_market_cap/1e9:.1f}B")
        logging.info(f"  Thresholds will be determined automatically based on available stocks")
    
    def analyze_stock(self, symbol: str, period: str = "1y", quick_mode: bool = False) -> Dict[str, Any]:
        """
        Comprehensive analysis of a single stock
        
        Args:
            symbol: Stock symbol to analyze
            period: Data period for analysis
            quick_mode: If True, skip detailed analysis for initial data gathering
            
        Returns:
            Dictionary containing all analysis metrics and recommendation
        """
        try:
            if not quick_mode:
                print(f"{EMOJIS['magnifying_glass']} Analyzing {symbol}...")
            
            # Get stock data
            stock = yf.Ticker(symbol)
            
            # Get historical data
            hist = stock.history(period=period)
            if hist.empty:
                return self._create_failed_analysis(symbol, "No historical data available")
            
            # Get stock info
            try:
                info = stock.info
            except Exception:
                info = {}
            
            # Calculate metrics
            analysis = {
                'symbol': symbol,
                'current_price': float(hist['Close'].iloc[-1]) if not hist.empty else 0,
                'timestamp': datetime.now()
            }
            
            # Price and market data
            analysis.update(self._analyze_price_metrics(hist, info))
            
            # Fundamental analysis
            analysis.update(self._analyze_fundamentals(info))
            
            # Technical analysis
            analysis.update(self._analyze_technical_indicators(hist))
            
            # Risk analysis
            analysis.update(self._analyze_risk_metrics(hist, info))
            
            # Volume and liquidity analysis
            analysis.update(self._analyze_liquidity(hist, info))
            
            # Generate overall recommendation (skip in quick mode, will be done later)
            if not quick_mode:
                analysis['recommendation'] = self._generate_recommendation(analysis)
                analysis['risk_score'] = self._calculate_risk_score(analysis)
                analysis['opportunity_score'] = self._calculate_opportunity_score(analysis)
            else:
                # Placeholder values for quick mode
                analysis['recommendation'] = {'action': 'PENDING', 'score': 0, 'confidence': 0.5, 'reasons': [], 'warnings': []}
                analysis['risk_score'] = 50
                analysis['opportunity_score'] = 50
            
            self.stock_analyses[symbol] = analysis
            return analysis
            
        except Exception as e:
            logging.error(f"Error analyzing {symbol}: {e}")
            return self._create_failed_analysis(symbol, str(e))
    
    def _analyze_price_metrics(self, hist: pd.DataFrame, info: Dict) -> Dict[str, Any]:
        """Analyze price-related metrics"""
        metrics = {}
        
        if not hist.empty:
            current_price = float(hist['Close'].iloc[-1])
            high_52w = float(hist['Close'].max())
            low_52w = float(hist['Close'].min())
            
            # Calculate price metrics with safety checks
            price_range = high_52w - low_52w if high_52w > low_52w else 1  # Avoid division by zero
            
            metrics.update({
                'price_52w_high': high_52w,
                'price_52w_low': low_52w,
                'price_from_52w_high': (current_price - high_52w) / high_52w if high_52w > 0 else 0,
                'price_from_52w_low': (current_price - low_52w) / low_52w if low_52w > 0 else 0,
                'price_range_position': (current_price - low_52w) / price_range if price_range > 0 else 0.5
            })
        
        return metrics
    
    def _analyze_fundamentals(self, info: Dict) -> Dict[str, Any]:
        """Analyze fundamental financial metrics"""
        metrics = {}
        
        # Valuation metrics
        metrics['pe_ratio'] = info.get('trailingPE', info.get('forwardPE', None))
        metrics['pb_ratio'] = info.get('priceToBook', None)
        metrics['ps_ratio'] = info.get('priceToSalesTrailing12Months', None)
        metrics['peg_ratio'] = info.get('pegRatio', None)
        
        # Market metrics
        metrics['market_cap'] = info.get('marketCap', 0)
        metrics['enterprise_value'] = info.get('enterpriseValue', None)
        metrics['shares_outstanding'] = info.get('sharesOutstanding', 0)
        metrics['float_shares'] = info.get('floatShares', 0)
        
        # Financial health
        metrics['debt_to_equity'] = info.get('debtToEquity', None)
        metrics['current_ratio'] = info.get('currentRatio', None)
        metrics['quick_ratio'] = info.get('quickRatio', None)
        metrics['roe'] = info.get('returnOnEquity', None)
        metrics['roa'] = info.get('returnOnAssets', None)
        
        # Growth metrics
        metrics['revenue_growth'] = info.get('revenueGrowth', None)
        metrics['earnings_growth'] = info.get('earningsGrowth', None)
        
        # Dividend info
        metrics['dividend_yield'] = info.get('dividendYield', None)
        metrics['payout_ratio'] = info.get('payoutRatio', None)
        
        return metrics
    
    def _analyze_technical_indicators(self, hist: pd.DataFrame) -> Dict[str, Any]:
        """Analyze technical indicators"""
        metrics = {}
        
        if hist.empty or len(hist) < 50:
            return metrics
        
        close = hist['Close']
        
        # Moving averages
        metrics['sma_20'] = close.rolling(20).mean().iloc[-1]
        metrics['sma_50'] = close.rolling(50).mean().iloc[-1]
        metrics['sma_200'] = close.rolling(200).mean().iloc[-1] if len(close) >= 200 else None
        
        current_price = close.iloc[-1]
        
        # Price relative to moving averages
        metrics['price_vs_sma20'] = (current_price - metrics['sma_20']) / metrics['sma_20']
        metrics['price_vs_sma50'] = (current_price - metrics['sma_50']) / metrics['sma_50']
        if metrics['sma_200']:
            metrics['price_vs_sma200'] = (current_price - metrics['sma_200']) / metrics['sma_200']
        
        # RSI calculation
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        metrics['rsi'] = 100 - (100 / (1 + rs)).iloc[-1]
        
        # Momentum (recent performance)
        if len(close) >= 30:
            metrics['momentum_1m'] = (close.iloc[-1] - close.iloc[-21]) / close.iloc[-21]
        if len(close) >= 90:
            metrics['momentum_3m'] = (close.iloc[-1] - close.iloc[-63]) / close.iloc[-63]
        if len(close) >= 252:
            metrics['momentum_1y'] = (close.iloc[-1] - close.iloc[-252]) / close.iloc[-252]
        
        return metrics
    
    def _analyze_risk_metrics(self, hist: pd.DataFrame, info: Dict) -> Dict[str, Any]:
        """Analyze risk-related metrics"""
        metrics = {}
        
        if not hist.empty and len(hist) > 1:
            returns = hist['Close'].pct_change().dropna()
            
            # Volatility
            metrics['volatility_daily'] = returns.std()
            metrics['volatility_annualized'] = returns.std() * np.sqrt(252)
            
            # Downside metrics
            negative_returns = returns[returns < 0]
            if len(negative_returns) > 0:
                metrics['downside_volatility'] = negative_returns.std() * np.sqrt(252)
                metrics['max_drawdown'] = self._calculate_max_drawdown(hist['Close'])
            
            # VaR (Value at Risk) - 5% confidence level
            metrics['var_5pct'] = np.percentile(returns, 5)
            
        # Market risk (Beta)
        metrics['beta'] = info.get('beta', None)
        
        return metrics
    
    def _analyze_liquidity(self, hist: pd.DataFrame, info: Dict) -> Dict[str, Any]:
        """Analyze liquidity and trading metrics"""
        metrics = {}
        
        if not hist.empty and 'Volume' in hist.columns:
            volume = hist['Volume']
            close = hist['Close']
            
            # Average volume metrics
            metrics['avg_volume_30d'] = volume.tail(30).mean()
            metrics['avg_volume_90d'] = volume.tail(90).mean() if len(volume) >= 90 else None
            
            # Dollar volume (liquidity)
            dollar_volume = volume * close
            metrics['avg_dollar_volume_30d'] = dollar_volume.tail(30).mean()
            
            # Volume trend
            if len(volume) >= 10:
                recent_vol = volume.tail(10).mean()
                older_vol = volume.iloc[-20:-10].mean() if len(volume) >= 20 else recent_vol
                metrics['volume_trend'] = (recent_vol - older_vol) / older_vol if older_vol > 0 else 0
        
        # Float and institutional ownership
        metrics['avg_daily_volume'] = info.get('averageDailyVolume10Day', 0)
        metrics['institutional_ownership'] = info.get('heldPercentInstitutions', None)
        
        return metrics
    
    def _calculate_max_drawdown(self, price_series: pd.Series) -> float:
        """Calculate maximum drawdown"""
        peak = price_series.expanding().max()
        drawdown = (price_series - peak) / peak
        return drawdown.min()
    
    def _generate_recommendation(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate buy/avoid recommendation based on analysis"""
        recommendation = {
            'action': 'ANALYZE',  # Default
            'confidence': 0.5,
            'reasons': [],
            'warnings': [],
            'score': 0
        }
        
        # Check fundamental criteria
        pe_ratio = analysis.get('pe_ratio')
        if pe_ratio is not None:
            if pe_ratio > self.max_pe_ratio:
                recommendation['warnings'].append(f"High P/E ratio: {pe_ratio:.1f} (max: {self.max_pe_ratio})")
                recommendation['score'] -= 20
            elif pe_ratio < 15:
                recommendation['reasons'].append(f"Reasonable P/E ratio: {pe_ratio:.1f}")
                recommendation['score'] += 10
        
        # Check volatility
        vol = analysis.get('volatility_annualized')
        if vol is not None:
            if vol > self.max_volatility:
                recommendation['warnings'].append(f"High volatility: {vol:.1%} (max: {self.max_volatility:.1%})")
                recommendation['score'] -= 25
            elif vol < 0.20:  # Low volatility is good
                recommendation['reasons'].append(f"Low volatility: {vol:.1%}")
                recommendation['score'] += 15
        
        # Check market cap
        market_cap = analysis.get('market_cap', 0)
        if market_cap < self.min_market_cap:
            recommendation['warnings'].append(f"Small market cap: ${market_cap/1e9:.1f}B (min: ${self.min_market_cap/1e9:.1f}B)")
            recommendation['score'] -= 15
        else:
            recommendation['reasons'].append(f"Adequate market cap: ${market_cap/1e9:.1f}B")
            recommendation['score'] += 5
        
        # Check liquidity
        dollar_volume = analysis.get('avg_dollar_volume_30d', 0)
        if dollar_volume < self.min_volume:
            recommendation['warnings'].append(f"Low liquidity: ${dollar_volume/1e6:.1f}M daily (min: ${self.min_volume/1e6:.1f}M)")
            recommendation['score'] -= 20
        else:
            recommendation['reasons'].append(f"Good liquidity: ${dollar_volume/1e6:.1f}M daily")
            recommendation['score'] += 10
        
        # Check beta
        beta = analysis.get('beta')
        if beta is not None:
            if beta > self.max_beta:
                recommendation['warnings'].append(f"High market sensitivity: β={beta:.2f} (max: {self.max_beta})")
                recommendation['score'] -= 15
            elif beta < 1.2:
                recommendation['reasons'].append(f"Moderate market sensitivity: β={beta:.2f}")
                recommendation['score'] += 5
        
        # Check debt levels
        debt_to_equity = analysis.get('debt_to_equity')
        if debt_to_equity is not None:
            if debt_to_equity > self.max_debt_to_equity * 100:  # yfinance returns percentage
                recommendation['warnings'].append(f"High debt: D/E={debt_to_equity:.1f}% (max: {self.max_debt_to_equity*100:.0f}%)")
                recommendation['score'] -= 10
        
        # Technical analysis
        rsi = analysis.get('rsi')
        if rsi is not None:
            if rsi > 70:
                recommendation['warnings'].append(f"Overbought: RSI={rsi:.1f}")
                recommendation['score'] -= 10
            elif rsi < 30:
                recommendation['reasons'].append(f"Oversold opportunity: RSI={rsi:.1f}")
                recommendation['score'] += 15
        
        # Price position analysis
        price_pos = analysis.get('price_range_position')
        if price_pos is not None and not (np.isnan(price_pos) if isinstance(price_pos, float) else False):
            try:
                if price_pos < 0.3:  # Near 52-week low
                    recommendation['reasons'].append(f"Near 52-week low (good entry point)")
                    recommendation['score'] += 10
                elif price_pos > 0.9:  # Near 52-week high
                    recommendation['warnings'].append(f"Near 52-week high (potential overvaluation)")
                    recommendation['score'] -= 10
            except (TypeError, ValueError):
                # Skip price position analysis if data is invalid
                pass
        
        # Final recommendation based on score
        if recommendation['score'] >= 30:
            recommendation['action'] = 'STRONG_BUY'
            recommendation['confidence'] = 0.9
        elif recommendation['score'] >= 15:
            recommendation['action'] = 'BUY'
            recommendation['confidence'] = 0.75
        elif recommendation['score'] >= 0:
            recommendation['action'] = 'HOLD'
            recommendation['confidence'] = 0.6
        elif recommendation['score'] >= -20:
            recommendation['action'] = 'AVOID'
            recommendation['confidence'] = 0.7
        else:
            recommendation['action'] = 'STRONG_AVOID'
            recommendation['confidence'] = 0.9
        
        return recommendation
    
    def _calculate_risk_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate overall risk score (0-100, higher = riskier)"""
        try:
            risk_score = 50  # Base score
            
            # Volatility risk
            vol = analysis.get('volatility_annualized', 0.2)
            if vol is not None and vol > 0:
                risk_score += min(vol * 100, 30)  # Up to 30 points for volatility
            
            # Beta risk
            beta = analysis.get('beta')
            if beta is not None and beta > 0:
                risk_score += min(abs(beta - 1) * 20, 15)  # Up to 15 points for beta deviation
            
            # Debt risk
            debt_to_equity = analysis.get('debt_to_equity')
            if debt_to_equity and debt_to_equity > 0:
                risk_score += min(debt_to_equity / 10, 10)  # Up to 10 points for debt
            
            # Liquidity risk
            dollar_volume = analysis.get('avg_dollar_volume_30d', 0)
            if dollar_volume and dollar_volume < self.min_volume:
                risk_score += 15  # Illiquid stocks are risky
            
            return min(max(risk_score, 0), 100)  # Clamp between 0-100
            
        except Exception as e:
            logging.error(f"Error calculating risk score: {e}")
            return 75  # Default high risk score
    
    def _calculate_opportunity_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate opportunity score (0-100, higher = better opportunity)"""
        try:
            opp_score = 50  # Base score
            
            # Valuation opportunity
            pe_ratio = analysis.get('pe_ratio')
            if pe_ratio and pe_ratio > 0 and pe_ratio < 15:
                opp_score += 15
            elif pe_ratio and pe_ratio > 25:
                opp_score -= 10
            
            # Technical opportunity
            rsi = analysis.get('rsi')
            if rsi and rsi < 30:
                opp_score += 20  # Oversold
            elif rsi and rsi > 70:
                opp_score -= 15  # Overbought
            
            # Momentum opportunity
            momentum_3m = analysis.get('momentum_3m')
            if momentum_3m is not None and momentum_3m < -0.1:
                opp_score += 10  # Potential rebound
            
            # Position in range
            price_pos = analysis.get('price_range_position')
            if price_pos is not None:
                try:
                    if price_pos < 0.3:
                        opp_score += 15  # Good entry point
                    elif price_pos > 0.9:
                        opp_score -= 10  # Expensive
                except (TypeError, ValueError):
                    pass  # Skip if invalid data
            
            return min(max(opp_score, 0), 100)
            
        except Exception as e:
            logging.error(f"Error calculating opportunity score: {e}")
            return 50  # Default neutral score
    
    def _create_failed_analysis(self, symbol: str, error: str) -> Dict[str, Any]:
        """Create analysis result for failed stocks"""
        return {
            'symbol': symbol,
            'current_price': 0,
            'timestamp': datetime.now(),
            'error': error,
            'recommendation': {
                'action': 'SKIP',
                'confidence': 0.9,
                'reasons': [],
                'warnings': [f"Analysis failed: {error}"],
                'score': -100
            },
            'risk_score': 100,
            'opportunity_score': 0
        }
    
    def _determine_adaptive_thresholds(self, analyses: Dict[str, Dict[str, Any]]) -> None:
        """
        Determine optimal filtering thresholds based on available stocks
        """
        try:
            # Collect valid metrics from all stocks
            pe_ratios = []
            volatilities = []
            betas = []
            
            for symbol, analysis in analyses.items():
                if analysis.get('error'):
                    continue
                    
                pe = analysis.get('pe_ratio')
                vol = analysis.get('volatility_annualized')
                beta = analysis.get('beta')
                
                if pe is not None and pe > 0 and pe < 200:  # Reasonable P/E range
                    pe_ratios.append(pe)
                if vol is not None and vol > 0 and vol < 3.0:  # Reasonable volatility range
                    volatilities.append(vol)
                if beta is not None and beta > 0 and beta < 5.0:  # Reasonable beta range
                    betas.append(beta)
            
            params = self.mode_params[self.filtering_mode]
            
            # Determine P/E threshold
            if pe_ratios:
                pe_percentile = np.percentile(pe_ratios, params['pe_percentile'])
                # Ensure reasonable bounds
                self.max_pe_ratio = max(15, min(pe_percentile, 50))
            else:
                self.max_pe_ratio = 25  # Default fallback
            
            # Determine volatility threshold
            if volatilities:
                vol_percentile = np.percentile(volatilities, params['vol_percentile'])
                # Ensure reasonable bounds
                self.max_volatility = max(0.20, min(vol_percentile, 0.80))
            else:
                self.max_volatility = 0.35  # Default fallback
            
            # Determine beta threshold
            if betas:
                beta_median = np.median(betas)
                self.max_beta = min(params['beta_max'], max(1.0, beta_median * 1.2))
            else:
                self.max_beta = params['beta_max']
            
            print(f"\n{EMOJIS['computer']} ADAPTIVE THRESHOLDS DETERMINED ({self.filtering_mode.upper()} MODE)")
            print("=" * 60)
            print(f"📊 Max P/E Ratio: {self.max_pe_ratio:.1f} (based on {len(pe_ratios)} stocks)")
            print(f"📈 Max Volatility: {self.max_volatility:.1%} (based on {len(volatilities)} stocks)")
            print(f"⚖️  Max Beta: {self.max_beta:.2f}")
            print(f"🏢 Min Market Cap: ${self.min_market_cap/1e9:.1f}B")
            print(f"💧 Min Daily Volume: ${self.min_volume/1e6:.1f}M")
            
            logging.info(f"Adaptive thresholds set - P/E: {self.max_pe_ratio:.1f}, "
                        f"Vol: {self.max_volatility:.1%}, Beta: {self.max_beta:.2f}")
                        
        except Exception as e:
            logging.error(f"Error determining adaptive thresholds: {e}")
            # Set conservative defaults
            self.max_pe_ratio = 25
            self.max_volatility = 0.35
            self.max_beta = 1.5

    def filter_stocks(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Filter a list of stocks with adaptive thresholds
        
        Returns:
            Dictionary with symbol as key and analysis as value
        """
        results = {}
        
        print(f"\n{EMOJIS['magnifying_glass']} INTELLIGENT ADAPTIVE STOCK FILTERING")
        print("=" * 60)
        print(f"Analyzing {len(symbols)} stocks to determine optimal filtering criteria...")
        
        # First pass: analyze all stocks to gather metrics
        print(f"\n{EMOJIS['chart']} Phase 1: Gathering market data and metrics...")
        for i, symbol in enumerate(symbols, 1):
            print(f"[{i}/{len(symbols)}] Analyzing {symbol}...", end=" ")
            analysis = self.analyze_stock(symbol, quick_mode=True)
            results[symbol] = analysis
            print("✅" if not analysis.get('error') else "❌")
        
        # Determine adaptive thresholds based on gathered data
        self._determine_adaptive_thresholds(results)
        
        # Second pass: re-evaluate recommendations with adaptive thresholds
        print(f"\n{EMOJIS['dart']} Phase 2: Applying adaptive filtering criteria...")
        for symbol in symbols:
            if symbol in results and not results[symbol].get('error'):
                try:
                    # Recalculate recommendation with new thresholds
                    results[symbol]['recommendation'] = self._generate_recommendation(results[symbol])
                    results[symbol]['risk_score'] = self._calculate_risk_score(results[symbol])
                    results[symbol]['opportunity_score'] = self._calculate_opportunity_score(results[symbol])
                except Exception as e:
                    logging.error(f"Error re-evaluating {symbol}: {e}")
                    results[symbol]['recommendation'] = {
                        'action': 'SKIP', 'confidence': 0.9, 'reasons': [], 
                        'warnings': [f"Re-evaluation failed: {str(e)}"], 'score': -100
                    }
        
        return results
    
    def print_filtering_results(self, analyses: Dict[str, Dict[str, Any]]) -> None:
        """Print comprehensive filtering results"""
        print(f"\n{EMOJIS['chart']} STOCK FILTERING RESULTS")
        print("=" * 70)
        
        # Sort by recommendation score
        sorted_stocks = sorted(
            analyses.items(), 
            key=lambda x: x[1]['recommendation']['score'], 
            reverse=True
        )
        
        buy_stocks = []
        avoid_stocks = []
        
        for symbol, analysis in sorted_stocks:
            rec = analysis['recommendation']
            action = rec['action']
            score = rec['score']
            confidence = rec['confidence']
            
            print(f"\n{self._get_action_emoji(action)} {symbol} - {action}")
            print(f"   💰 Price: {format_currency(analysis.get('current_price', 0))}")
            print(f"   📊 Score: {score:+d} | Confidence: {confidence:.0%}")
            print(f"   ⚖️  Risk: {analysis.get('risk_score', 0):.0f}/100")
            print(f"   🎯 Opportunity: {analysis.get('opportunity_score', 0):.0f}/100")
            
            # Show key metrics
            if analysis.get('pe_ratio'):
                print(f"   📈 P/E: {analysis['pe_ratio']:.1f}")
            if analysis.get('volatility_annualized'):
                print(f"   📊 Volatility: {analysis['volatility_annualized']:.1%}")
            if analysis.get('market_cap'):
                print(f"   🏢 Market Cap: ${analysis['market_cap']/1e9:.1f}B")
            
            # Show top reasons/warnings
            if rec['reasons']:
                print(f"   ✅ Positives: {', '.join(rec['reasons'][:2])}")
            if rec['warnings']:
                print(f"   ⚠️  Concerns: {', '.join(rec['warnings'][:2])}")
            
            if action in ['BUY', 'STRONG_BUY']:
                buy_stocks.append(symbol)
            elif action in ['AVOID', 'STRONG_AVOID']:
                avoid_stocks.append(symbol)
        
        # Summary
        print(f"\n{EMOJIS['chart']} FILTERING SUMMARY")
        print("=" * 50)
        print(f"✅ Recommended to BUY: {len(buy_stocks)} stocks")
        if buy_stocks:
            print(f"   {', '.join(buy_stocks)}")
        
        print(f"⚠️  Recommended to AVOID: {len(avoid_stocks)} stocks")
        if avoid_stocks:
            print(f"   {', '.join(avoid_stocks)}")
        
        print(f"📊 Total analyzed: {len(analyses)} stocks")
    
    def _get_action_emoji(self, action: str) -> str:
        """Get emoji for recommendation action"""
        emoji_map = {
            'STRONG_BUY': '🚀',
            'BUY': '✅',
            'HOLD': '⏸️',
            'AVOID': '⚠️',
            'STRONG_AVOID': '🛑',
            'SKIP': '❌'
        }
        return emoji_map.get(action, '❓')
    
    def get_filtered_recommendations(self, symbols: List[str]) -> Tuple[List[str], List[str]]:
        """
        Get lists of stocks to buy and avoid
        
        Returns:
            Tuple of (buy_list, avoid_list)
        """
        analyses = self.filter_stocks(symbols)
        
        buy_list = []
        avoid_list = []
        
        for symbol, analysis in analyses.items():
            action = analysis['recommendation']['action']
            if action in ['BUY', 'STRONG_BUY']:
                buy_list.append(symbol)
            elif action in ['AVOID', 'STRONG_AVOID', 'SKIP']:
                avoid_list.append(symbol)
        
        return buy_list, avoid_list
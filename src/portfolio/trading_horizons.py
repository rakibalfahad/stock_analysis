"""
Trading Horizon Categorization System

Categorizes stocks based on different trading horizons and strategies:
- Long-Term: Value Investing (focus on intrinsic value, growth)
- Short-Term: Momentum Trading (focus on trend persistence)  
- Day Trading: Technical Analysis (focus on intraday volatility)

Each horizon has specific metrics and thresholds optimized for that trading style.
"""

import pandas as pd
import numpy as np
import yfinance as yf
import os
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import logging
import os

class TradingHorizon(Enum):
    """Trading horizon categories"""
    LONG_TERM = "Long-Term"
    SHORT_TERM = "Short-Term"
    DAY_TRADING = "Day Trading"

@dataclass
class MetricThreshold:
    """Threshold configuration for a metric"""
    poor_threshold: float
    good_range: Tuple[float, float]
    excellent_threshold: float
    higher_is_better: bool = True
    description: str = ""

@dataclass
class HorizonConfig:
    """Configuration for a specific trading horizon"""
    horizon: TradingHorizon
    theory: str
    focus: str
    metrics: Dict[str, MetricThreshold]

class TradingHorizonAnalyzer:
    """
    Analyzes stocks and categorizes them by optimal trading horizon
    """
    
    def __init__(self):
        self.configurations = self._initialize_configurations()
        
    def _initialize_configurations(self) -> Dict[TradingHorizon, HorizonConfig]:
        """Initialize trading horizon configurations with proper thresholds"""
        
        configs = {}
        
        # Long-Term Trading Configuration (Value Investing)
        configs[TradingHorizon.LONG_TERM] = HorizonConfig(
            horizon=TradingHorizon.LONG_TERM,
            theory="Value Investing",
            focus="Intrinsic value, growth",
            metrics={
                "sharpe_ratio": MetricThreshold(
                    poor_threshold=1.0, good_range=(1.0, 2.0), excellent_threshold=2.0,
                    higher_is_better=True, description="Sharpe Ratio: Risk-Adjusted, Poor < 1, Good 1–2, Excellent > 2"
                ),
                "pe_ratio": MetricThreshold(
                    poor_threshold=25.0, good_range=(15.0, 25.0), excellent_threshold=15.0,
                    higher_is_better=False, description="Price-to-Earnings Ratio: Valuation, Poor > 25, Good 15–25, Excellent < 15"
                ),
                "roe": MetricThreshold(
                    poor_threshold=10.0, good_range=(10.0, 20.0), excellent_threshold=20.0,
                    higher_is_better=True, description="Return on Equity: Profitability, Poor < 10%, Good 10–20%, Excellent > 20%"
                ),
                "debt_to_equity": MetricThreshold(
                    poor_threshold=2.0, good_range=(0.5, 2.0), excellent_threshold=0.5,
                    higher_is_better=False, description="Debt-to-Equity Ratio: Financial Health, Poor > 2, Good 0.5–2, Excellent < 0.5"
                ),
                "dividend_yield": MetricThreshold(
                    poor_threshold=1.0, good_range=(1.0, 3.0), excellent_threshold=3.0,
                    higher_is_better=True, description="Dividend Yield: Income, Poor < 1%, Good 1–3%, Excellent > 3%"
                )
            }
        )
        
        # Short-Term Trading Configuration (Momentum Trading)
        configs[TradingHorizon.SHORT_TERM] = HorizonConfig(
            horizon=TradingHorizon.SHORT_TERM,
            theory="Momentum Trading", 
            focus="Trend persistence",
            metrics={
                "sharpe_ratio": MetricThreshold(
                    poor_threshold=0.8, good_range=(0.8, 1.5), excellent_threshold=1.5,
                    higher_is_better=True, description="Sharpe Ratio: Risk-Adjusted, Poor < 0.8, Good 0.8–1.5, Excellent > 1.5"
                ),
                "rsi": MetricThreshold(
                    poor_threshold=70.0, good_range=(30.0, 70.0), excellent_threshold=30.0,
                    higher_is_better=False, description="Relative Strength Index: Momentum, Poor > 70 or < 30, Good 30–70, Excellent 40–60"
                ),
                "atr": MetricThreshold(
                    poor_threshold=1.0, good_range=(1.0, 3.0), excellent_threshold=3.0,
                    higher_is_better=True, description="Average True Range: Volatility, Poor < 1%, Good 1–3%, Excellent > 3%"
                ),
                "volume": MetricThreshold(
                    poor_threshold=100000, good_range=(100000, 1000000), excellent_threshold=1000000,
                    higher_is_better=True, description="Average Daily Volume: Liquidity, Poor < 100K shares, Good 100K–1M, Excellent > 1M"
                ),
                "beta": MetricThreshold(
                    poor_threshold=1.5, good_range=(0.5, 1.5), excellent_threshold=0.5,
                    higher_is_better=False, description="Market Sensitivity: Risk, Poor > 1.5 or < 0.5, Good 0.5–1.5, Excellent 0.8–1.2"
                )
            }
        )
        
        # Day Trading Configuration (Technical Analysis)
        configs[TradingHorizon.DAY_TRADING] = HorizonConfig(
            horizon=TradingHorizon.DAY_TRADING,
            theory="Technical Analysis (Dow/Elliott)",
            focus="Intraday volatility",
            metrics={
                "sharpe_ratio": MetricThreshold(
                    poor_threshold=0.5, good_range=(0.5, 1.0), excellent_threshold=1.0,
                    higher_is_better=True, description="Sharpe Ratio: Risk-Adjusted, Poor < 0.5, Good 0.5–1, Excellent > 1"
                ),
                "rsi": MetricThreshold(
                    poor_threshold=80.0, good_range=(20.0, 80.0), excellent_threshold=20.0,
                    higher_is_better=False, description="Relative Strength Index: Momentum, Poor > 80 or < 20, Good 20–80, Excellent 30–70"
                ),
                "high_relative_volume": MetricThreshold(
                    poor_threshold=1.5, good_range=(1.5, 3.0), excellent_threshold=3.0,
                    higher_is_better=True, description="High Relative Volume: Activity, Poor < 1.5x, Good 1.5–3x, Excellent > 3x"
                ),
                "vwap_deviation": MetricThreshold(
                    poor_threshold=2.0, good_range=(0.5, 2.0), excellent_threshold=0.5,
                    higher_is_better=False, description="Volume-Weighted Average Price: Trend, Poor > ±2%, Good ±0.5–2%, Excellent < ±0.5%"
                ),
                "bid_ask_spread": MetricThreshold(
                    poor_threshold=0.5, good_range=(0.1, 0.5), excellent_threshold=0.1,
                    higher_is_better=False, description="Bid-Ask Spread: Liquidity, Poor > 0.5%, Good 0.1–0.5%, Excellent < 0.1%"
                )
            }
        )
        
        return configs
    
    def analyze_stock_for_horizons(self, symbol: str, stock_data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Analyze a single stock across all trading horizons
        
        Args:
            symbol: Stock ticker symbol
            stock_data: Optional pre-fetched stock data
            
        Returns:
            Dictionary with analysis results for each horizon
        """
        try:
            # Fetch stock data if not provided
            if stock_data is None:
                stock_data = self._fetch_stock_data(symbol)
            
            if not stock_data:
                return {"error": f"Could not fetch data for {symbol}"}
            
            results = {
                "symbol": symbol,
                "company_name": stock_data.get("company_name", symbol),
                "current_price": stock_data.get("current_price", 0),
                "horizons": {}
            }
            
            # Analyze for each trading horizon
            for horizon, config in self.configurations.items():
                horizon_result = self._analyze_for_horizon(symbol, stock_data, config)
                results["horizons"][horizon.value] = horizon_result
            
            # Determine best horizon recommendation
            results["recommended_horizon"] = self._determine_best_horizon(results["horizons"])
            
            return results
            
        except Exception as e:
            logging.error(f"Error analyzing {symbol} for horizons: {e}")
            return {"error": f"Analysis error for {symbol}: {str(e)}"}
    
    def _fetch_stock_data(self, symbol: str) -> Optional[Dict]:
        """Fetch comprehensive stock data for horizon analysis"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            hist = ticker.history(period="1y")
            
            if hist.empty:
                return None
            
            # Calculate basic metrics
            current_price = hist['Close'].iloc[-1]
            returns = hist['Close'].pct_change().dropna()
            
            # Calculate technical indicators
            rsi = self._calculate_rsi(hist['Close'])
            atr = self._calculate_atr(hist)
            beta = info.get('beta', 1.0)
            
            # Get fundamental data
            pe_ratio = info.get('trailingPE', info.get('forwardPE', 0))
            roe = info.get('returnOnEquity', 0)
            debt_to_equity = info.get('debtToEquity', 0) / 100 if info.get('debtToEquity') else 0
            dividend_yield = info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 0
            
            # Calculate Sharpe ratio (assuming 2% risk-free rate)
            excess_returns = returns - 0.02/252
            sharpe_ratio = excess_returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0
            
            # Volume metrics
            avg_volume = hist['Volume'].mean()
            current_volume = hist['Volume'].iloc[-1]
            relative_volume = current_volume / avg_volume if avg_volume > 0 else 1
            
            # VWAP calculation (simplified for last 20 days)
            recent_data = hist.tail(20)
            vwap = (recent_data['Close'] * recent_data['Volume']).sum() / recent_data['Volume'].sum()
            vwap_deviation = abs(current_price - vwap) / vwap * 100
            
            # Bid-ask spread (approximated from daily range)
            daily_range = (hist['High'] - hist['Low']) / hist['Close']
            avg_spread = daily_range.mean() * 100  # Convert to percentage
            
            return {
                "symbol": symbol,
                "company_name": info.get('longName', symbol),
                "current_price": current_price,
                "sharpe_ratio": sharpe_ratio,
                "pe_ratio": pe_ratio,
                "roe": roe * 100 if roe else 0,  # Convert to percentage
                "debt_to_equity": debt_to_equity,
                "dividend_yield": dividend_yield,
                "rsi": rsi,
                "atr": atr,
                "beta": beta,
                "avg_volume": avg_volume,
                "relative_volume": relative_volume,
                "vwap_deviation": vwap_deviation,
                "bid_ask_spread": avg_spread
            }
            
        except Exception as e:
            logging.error(f"Error fetching data for {symbol}: {e}")
            return None
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        """Calculate Relative Strength Index"""
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi.iloc[-1] if not rsi.empty else 50.0
        except Exception:
            return 50.0
    
    def _calculate_atr(self, hist: pd.DataFrame, period: int = 14) -> float:
        """Calculate Average True Range"""
        try:
            high_low = hist['High'] - hist['Low']
            high_close = np.abs(hist['High'] - hist['Close'].shift())
            low_close = np.abs(hist['Low'] - hist['Close'].shift())
            
            true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            atr = true_range.rolling(period).mean()
            
            # Convert to percentage
            atr_pct = (atr / hist['Close']) * 100
            return atr_pct.iloc[-1] if not atr_pct.empty else 2.0
        except Exception:
            return 2.0
    
    def _analyze_for_horizon(self, symbol: str, stock_data: Dict, config: HorizonConfig) -> Dict[str, Any]:
        """Analyze stock for a specific trading horizon"""
        try:
            metrics_scores = {}
            total_score = 0
            max_possible_score = 0
            
            for metric_name, threshold in config.metrics.items():
                # Get metric value from stock data
                value = self._get_metric_value(stock_data, metric_name)
                
                if value is not None:
                    # Score the metric
                    score = self._score_metric(value, threshold)
                    metrics_scores[metric_name] = {
                        "value": value,
                        "score": score,
                        "rating": self._get_rating(score),
                        "threshold": threshold
                    }
                    total_score += score
                    max_possible_score += 3  # Max score is 3 (excellent)
                else:
                    metrics_scores[metric_name] = {
                        "value": None,
                        "score": 0,
                        "rating": "No Data",
                        "threshold": threshold
                    }
                    max_possible_score += 3
            
            # Calculate overall suitability score
            suitability_score = (total_score / max_possible_score * 100) if max_possible_score > 0 else 0
            
            return {
                "horizon": config.horizon.value,
                "theory": config.theory,
                "focus": config.focus,
                "metrics": metrics_scores,
                "suitability_score": suitability_score,
                "recommendation": self._get_horizon_recommendation(suitability_score),
                "total_score": total_score,
                "max_score": max_possible_score
            }
            
        except Exception as e:
            logging.error(f"Error analyzing {symbol} for {config.horizon.value}: {e}")
            return {"error": str(e)}
    
    def _get_metric_value(self, stock_data: Dict, metric_name: str) -> Optional[float]:
        """Extract metric value from stock data"""
        metric_mapping = {
            "sharpe_ratio": "sharpe_ratio",
            "pe_ratio": "pe_ratio", 
            "roe": "roe",
            "debt_to_equity": "debt_to_equity",
            "dividend_yield": "dividend_yield",
            "rsi": "rsi",
            "atr": "atr",
            "volume": "avg_volume",
            "beta": "beta",
            "high_relative_volume": "relative_volume",
            "vwap_deviation": "vwap_deviation",
            "bid_ask_spread": "bid_ask_spread"
        }
        
        data_key = metric_mapping.get(metric_name)
        if data_key and data_key in stock_data:
            return stock_data[data_key]
        return None
    
    def _score_metric(self, value: float, threshold: MetricThreshold) -> int:
        """Score a metric value against thresholds (0=poor, 1=fair, 2=good, 3=excellent)"""
        if threshold.higher_is_better:
            if value >= threshold.excellent_threshold:
                return 3  # Excellent
            elif value >= threshold.good_range[0]:
                return 2  # Good
            elif value >= threshold.poor_threshold:
                return 1  # Fair
            else:
                return 0  # Poor
        else:
            if value <= threshold.excellent_threshold:
                return 3  # Excellent  
            elif value <= threshold.good_range[1]:
                return 2  # Good
            elif value <= threshold.poor_threshold:
                return 1  # Fair
            else:
                return 0  # Poor
    
    def _get_rating(self, score: int) -> str:
        """Convert numeric score to rating"""
        ratings = {0: "Poor", 1: "Fair", 2: "Good", 3: "Excellent"}
        return ratings.get(score, "Unknown")
    
    def _get_horizon_recommendation(self, suitability_score: float) -> str:
        """Get recommendation based on suitability score"""
        if suitability_score >= 75:
            return "Highly Suitable"
        elif suitability_score >= 60:
            return "Suitable" 
        elif suitability_score >= 40:
            return "Moderately Suitable"
        elif suitability_score >= 25:
            return "Limited Suitability"
        else:
            return "Not Suitable"
    
    def _determine_best_horizon(self, horizons: Dict[str, Any]) -> Dict[str, Any]:
        """Determine the best trading horizon for the stock"""
        best_horizon = None
        best_score = -1
        
        for horizon_name, horizon_data in horizons.items():
            if "error" not in horizon_data:
                score = horizon_data.get("suitability_score", 0)
                if score > best_score:
                    best_score = score
                    best_horizon = horizon_name
        
        if best_horizon:
            return {
                "horizon": best_horizon,
                "score": best_score,
                "recommendation": self.configurations[TradingHorizon(best_horizon)].theory
            }
        else:
            return {"horizon": "Unable to determine", "score": 0, "recommendation": "Insufficient data"}
    
    def analyze_portfolio_horizons(self, symbols: List[str]) -> Dict[str, Any]:
        """
        Analyze multiple stocks and categorize by trading horizons
        
        Args:
            symbols: List of stock ticker symbols
            
        Returns:
            Comprehensive analysis with horizon categorization
        """
        try:
            results = {
                "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_stocks": len(symbols),
                "stocks": {},
                "horizon_summary": {
                    "Long-Term": [],
                    "Short-Term": [], 
                    "Day Trading": []
                },
                "recommendations": []
            }
            
            # Analyze each stock
            for symbol in symbols:
                print(f"Analyzing {symbol} for trading horizons...")
                stock_analysis = self.analyze_stock_for_horizons(symbol)
                results["stocks"][symbol] = stock_analysis
                
                # Categorize by best horizon
                if "error" not in stock_analysis:
                    best_horizon = stock_analysis.get("recommended_horizon", {}).get("horizon")
                    if best_horizon:
                        results["horizon_summary"][best_horizon].append({
                            "symbol": symbol,
                            "score": stock_analysis["recommended_horizon"]["score"],
                            "company": stock_analysis.get("company_name", symbol)
                        })
            
            # Generate recommendations for each horizon
            for horizon in ["Long-Term", "Short-Term", "Day Trading"]:
                stocks_in_horizon = results["horizon_summary"][horizon]
                if stocks_in_horizon:
                    # Sort by score (best first)
                    stocks_in_horizon.sort(key=lambda x: x["score"], reverse=True)
                    
                    # Take top stocks for this horizon
                    top_stocks = stocks_in_horizon[:5]  # Top 5 per horizon
                    
                    results["recommendations"].append({
                        "horizon": horizon,
                        "theory": self.configurations[TradingHorizon(horizon)].theory,
                        "count": len(stocks_in_horizon),
                        "top_picks": top_stocks
                    })
            
            return results
            
        except Exception as e:
            logging.error(f"Error in portfolio horizon analysis: {e}")
            return {"error": str(e)}
    
    def print_horizon_analysis(self, analysis_results: Dict[str, Any]) -> None:
        """Print comprehensive horizon analysis results"""
        if "error" in analysis_results:
            print(f"❌ Analysis Error: {analysis_results['error']}")
            return
        
        print("\n" + "="*80)
        print("🎯 PORTFOLIO TRADING HORIZON ANALYSIS")
        print("="*80)
        print(f"📅 Analysis Date: {analysis_results['analysis_date']}")
        print(f"📊 Total Stocks Analyzed: {analysis_results['total_stocks']}")
        
        # Summary by horizon
        print(f"\n📈 HORIZON DISTRIBUTION:")
        print("-"*50)
        for horizon, stocks in analysis_results["horizon_summary"].items():
            count = len(stocks)
            theory = self.configurations[TradingHorizon(horizon)].theory
            print(f"• {horizon:12} ({theory:20}): {count:2} stocks")
        
        # Detailed recommendations
        print(f"\n🚀 TOP RECOMMENDATIONS BY HORIZON:")
        print("="*80)
        
        for rec in analysis_results["recommendations"]:
            print(f"\n📊 {rec['horizon'].upper()} - {rec['theory']}")
            print(f"   Strategy Focus: {self.configurations[TradingHorizon(rec['horizon'])].focus}")
            print(f"   Suitable Stocks: {rec['count']}")
            print("   Top Picks:")
            
            for i, stock in enumerate(rec["top_picks"], 1):
                score_bar = "█" * int(stock["score"] / 10) + "░" * (10 - int(stock["score"] / 10))
                print(f"   {i}. {stock['symbol']:6} {stock['company'][:25]:25} "
                      f"Score: {stock['score']:5.1f}% [{score_bar}]")
        
        # Detailed stock analysis for top picks
        print(f"\n📋 DETAILED METRICS FOR TOP PERFORMERS:")
        print("="*80)
        
        for rec in analysis_results["recommendations"]:
            if rec["top_picks"]:
                top_stock = rec["top_picks"][0]
                symbol = top_stock["symbol"]
                stock_data = analysis_results["stocks"][symbol]
                
                print(f"\n🥇 {symbol} - Best for {rec['horizon']} ({rec['theory']})")
                print("-"*60)
                
                horizon_data = stock_data["horizons"][rec["horizon"]]
                for metric_name, metric_data in horizon_data["metrics"].items():
                    value = metric_data["value"]
                    rating = metric_data["rating"]
                    
                    if value is not None:
                        print(f"   {metric_name:20}: {value:8.2f} ({rating})")
                    else:
                        print(f"   {metric_name:20}: {'N/A':>8} ({rating})")
    
    def export_to_excel(self, analysis_results: Dict[str, Any], filename: Optional[str] = None) -> str:
        """
        Export complete trading horizons analysis to Excel with all matrices and recommendations.
        
        Args:
            analysis_results: Results from analyze_portfolio_horizons()
            filename: Optional custom filename (default: auto-generated with timestamp)
            
        Returns:
            str: Path to created Excel file
        """
        try:
            # Generate filename if not provided
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"trading_horizons_analysis_{timestamp}.xlsx"
            
            # Ensure .xlsx extension
            if not filename.endswith('.xlsx'):
                filename += '.xlsx'
            
            print(f"📊 Exporting Trading Horizons Analysis to {filename}...")
            
            # Create Excel writer
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                
                # Sheet 1: Summary & Recommendations
                self._create_summary_sheet(analysis_results, writer)
                
                # Sheet 2: Detailed Stock Metrics - Long Term
                self._create_detailed_metrics_sheet(analysis_results, writer, "Long-Term", "LongTerm_Metrics")
                
                # Sheet 3: Detailed Stock Metrics - Short Term  
                self._create_detailed_metrics_sheet(analysis_results, writer, "Short-Term", "ShortTerm_Metrics")
                
                # Sheet 4: Detailed Stock Metrics - Day Trading
                self._create_detailed_metrics_sheet(analysis_results, writer, "Day Trading", "DayTrading_Metrics")
                
                # Sheet 5: Stock Rankings by Horizon
                self._create_rankings_sheet(analysis_results, writer)
                
                # Sheet 6: Raw Data & Scores
                self._create_raw_data_sheet(analysis_results, writer)
            
            print(f"✅ Excel file created successfully: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Error creating Excel file: {e}")
            return ""
    
    def _create_summary_sheet(self, analysis_results: Dict[str, Any], writer: pd.ExcelWriter) -> None:
        """Create summary sheet with recommendations overview."""
        
        # Summary data
        summary_data = []
        for rec in analysis_results["recommendations"]:
            summary_data.append({
                'Trading_Horizon': rec['horizon'],
                'Strategy_Theory': rec['theory'],
                'Suitable_Stocks_Count': rec['count'],
                'Top_Stock_Symbol': rec['top_picks'][0]['symbol'] if rec['top_picks'] else 'None',
                'Top_Stock_Company': rec['top_picks'][0]['company'] if rec['top_picks'] else 'None',
                'Top_Stock_Score': f"{rec['top_picks'][0]['score']:.1f}%" if rec['top_picks'] else 'N/A'
            })
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Top picks for each horizon
        top_picks_data = []
        for rec in analysis_results["recommendations"]:
            for i, stock in enumerate(rec["top_picks"][:5], 1):  # Top 5 per horizon
                # Get the stock's data for this horizon
                stock_data = analysis_results["stocks"][stock['symbol']]
                horizon_data = stock_data["horizons"][rec['horizon']]
                
                top_picks_data.append({
                    'Rank': i,
                    'Trading_Horizon': rec['horizon'],
                    'Symbol': stock['symbol'],
                    'Company': stock['company'],
                    'Score': f"{stock['score']:.1f}%",
                    'Recommendation': horizon_data['recommendation']
                })
        
        top_picks_df = pd.DataFrame(top_picks_data)
        top_picks_df.to_excel(writer, sheet_name='Top_Recommendations', index=False)
    
    def _create_detailed_metrics_sheet(self, analysis_results: Dict[str, Any], writer: pd.ExcelWriter, 
                                     horizon_name: str, sheet_name: str) -> None:
        """Create detailed metrics sheet for a specific trading horizon."""
        
        detailed_data = []
        stocks_data = analysis_results.get("stocks", {})
        
        for symbol, stock_data in stocks_data.items():
            if horizon_name in stock_data.get("horizons", {}):
                horizon_data = stock_data["horizons"][horizon_name]
                
                row_data = {
                    'Symbol': symbol,
                    'Company': stock_data.get('company_name', 'N/A'),
                    'Overall_Score': f"{horizon_data.get('suitability_score', 0):.1f}%",
                    'Recommendation': horizon_data.get('recommendation', 'N/A')
                }
                
                # Add all metrics for this horizon
                for metric_name, metric_data in horizon_data.get("metrics", {}).items():
                    value = metric_data.get("value")
                    rating = metric_data.get("rating", "N/A")
                    
                    if value is not None:
                        if isinstance(value, float):
                            row_data[f'{metric_name}_Value'] = f"{value:.2f}"
                        else:
                            row_data[f'{metric_name}_Value'] = str(value)
                    else:
                        row_data[f'{metric_name}_Value'] = 'N/A'
                    
                    row_data[f'{metric_name}_Rating'] = rating
                
                detailed_data.append(row_data)
        
        # Sort by score (descending)
        detailed_data.sort(key=lambda x: float(x['Overall_Score'].replace('%', '')), reverse=True)
        
        detailed_df = pd.DataFrame(detailed_data)
        detailed_df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    def _create_rankings_sheet(self, analysis_results: Dict[str, Any], writer: pd.ExcelWriter) -> None:
        """Create rankings comparison sheet showing all stocks across all horizons."""
        
        rankings_data = []
        stocks_data = analysis_results.get("stocks", {})
        
        for symbol, stock_data in stocks_data.items():
            company = stock_data.get('info', {}).get('company', 'N/A')
            
            row_data = {
                'Symbol': symbol,
                'Company': company,
                'Best_Horizon': stock_data.get('best_horizon', {}).get('horizon', 'N/A'),
                'Best_Score': f"{stock_data.get('best_horizon', {}).get('score', 0):.1f}%"
            }
            
            # Add scores for each horizon
            for horizon_name in ["Long-Term", "Short-Term", "Day Trading"]:
                if horizon_name in stock_data.get("horizons", {}):
                    score = stock_data["horizons"][horizon_name].get('suitability_score', 0)
                    recommendation = stock_data["horizons"][horizon_name].get('recommendation', 'N/A')
                    row_data[f'{horizon_name.replace("-", "")}_Score'] = f"{score:.1f}%"
                    row_data[f'{horizon_name.replace("-", "")}_Recommendation'] = recommendation
                else:
                    row_data[f'{horizon_name.replace("-", "")}_Score'] = 'N/A'
                    row_data[f'{horizon_name.replace("-", "")}_Recommendation'] = 'N/A'
            
            rankings_data.append(row_data)
        
        # Sort by best score (descending)
        rankings_data.sort(key=lambda x: float(x['Best_Score'].replace('%', '')), reverse=True)
        
        rankings_df = pd.DataFrame(rankings_data)
        rankings_df.to_excel(writer, sheet_name='Stock_Rankings', index=False)
    
    def _create_raw_data_sheet(self, analysis_results: Dict[str, Any], writer: pd.ExcelWriter) -> None:
        """Create raw data sheet with all calculated values and metadata."""
        
        raw_data = []
        stocks_data = analysis_results.get("stocks", {})
        
        for symbol, stock_data in stocks_data.items():
            for horizon_name, horizon_data in stock_data.get("horizons", {}).items():
                for metric_name, metric_data in horizon_data.get("metrics", {}).items():
                    raw_data.append({
                        'Symbol': symbol,
                        'Company': stock_data.get('info', {}).get('company', 'N/A'),
                        'Trading_Horizon': horizon_name,
                        'Metric_Name': metric_name,
                        'Value': metric_data.get("value"),
                        'Score': metric_data.get("score", 0),
                        'Rating': metric_data.get("rating", "N/A"),
                        'Description': metric_data.get("description", "N/A")
                    })
        
        raw_df = pd.DataFrame(raw_data)
        raw_df.to_excel(writer, sheet_name='Raw_Data', index=False)
        
        # Analysis metadata
        metadata = {
            'Analysis_Date': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            'Total_Stocks_Analyzed': [len(stocks_data)],
            'Analysis_Summary': [analysis_results.get('summary', 'Trading Horizons Analysis Complete')]
        }
        
        metadata_df = pd.DataFrame(metadata)
        metadata_df.to_excel(writer, sheet_name='Analysis_Metadata', index=False)
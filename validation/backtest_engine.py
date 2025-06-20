#!/usr/bin/env python3
"""
Backtesting engine to validate Stock Forecaster ratings against historical performance.
Tests if our BUY/SELL/RISKY_BUY signals actually predict profitable moves.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import sys
import os

# Add parent directory to path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.analyzer import analyze_technical
from core.data_fetcher import fetch_stock_data

class BacktestEngine:
    """
    Validates our trading signals against historical data.
    
    Tests whether our ratings actually predict profitable moves:
    - BUY signals: Should show positive returns in following days
    - SELL signals: Should show negative returns or avoid losses
    - RISKY_BUY signals: Should show higher volatility but potential gains
    """
    
    def __init__(self):
        self.results = {
            'BUY': {'trades': [], 'hit_rate': 0, 'avg_return': 0},
            'SELL': {'trades': [], 'hit_rate': 0, 'avg_return': 0},
            'RISKY_BUY': {'trades': [], 'hit_rate': 0, 'avg_return': 0},
            'HOLD': {'trades': [], 'hit_rate': 0, 'avg_return': 0}
        }
    
    def backtest_stock(self, ticker: str, days_back: int = 60, hold_days: int = 5) -> Dict:
        """
        Backtest our analysis on historical data for a single stock.
        
        Args:
            ticker: Stock symbol to test
            days_back: How many days back to test signals
            hold_days: How many days to hold position after signal
            
        Returns:
            Dictionary with backtest results
        """
        print(f"📊 Backtesting {ticker} over {days_back} days...")
        
        try:
            # Get extended historical data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back + hold_days + 30)  # Extra buffer
            
            stock = yf.Ticker(ticker)
            hist = stock.history(start=start_date, end=end_date)
            
            if hist.empty or len(hist) < 30:
                print(f"❌ Insufficient data for {ticker}")
                return {}
            
            stock_results = []
            
            # Test signals on each day (sliding window)
            for i in range(30, len(hist) - hold_days):
                test_date = hist.index[i]
                
                # Create historical data up to test date (what our system would have seen)
                historical_data = hist.iloc[:i+1]
                
                # Convert to our StockData format
                stock_data = self._convert_to_stock_data(ticker, historical_data)
                
                if not stock_data:
                    continue
                
                # Get our system's analysis for this point in time
                analysis = analyze_technical(stock_data)
                
                # Calculate actual returns over next N days
                entry_price = historical_data['Close'].iloc[-1]
                future_prices = hist['Close'].iloc[i+1:i+1+hold_days]
                
                if len(future_prices) == hold_days:
                    exit_price = future_prices.iloc[-1]
                    actual_return = (exit_price - entry_price) / entry_price * 100
                    
                    # Record the trade
                    trade_result = {
                        'date': test_date,
                        'ticker': ticker,
                        'rating': analysis.rating,
                        'confidence': analysis.confidence,
                        'entry_price': entry_price,
                        'exit_price': exit_price,
                        'actual_return': actual_return,
                        'predicted_return': self._expected_return_from_rating(analysis.rating),
                        'correct_direction': self._is_direction_correct(analysis.rating, actual_return),
                        'reasoning': analysis.reasoning[:2]  # Top 2 reasons
                    }
                    
                    stock_results.append(trade_result)
                    self.results[analysis.rating]['trades'].append(trade_result)
            
            print(f"✅ Completed {len(stock_results)} signal tests for {ticker}")
            return {'ticker': ticker, 'trades': stock_results}
            
        except Exception as e:
            print(f"❌ Error backtesting {ticker}: {str(e)}")
            return {}
    
    def _convert_to_stock_data(self, ticker: str, hist_data: pd.DataFrame):
        """Convert yfinance data to our StockData format."""
        try:
            from core.models import StockData
            
            prices = hist_data['Close'].tolist()
            volumes = hist_data['Volume'].tolist()
            dates = [d.to_pydatetime() for d in hist_data.index]
            
            current_price = prices[-1]
            daily_change = prices[-1] - prices[-2] if len(prices) > 1 else 0
            daily_change_percent = (daily_change / prices[-2] * 100) if len(prices) > 1 and prices[-2] != 0 else 0
            
            return StockData(
                ticker=ticker,
                prices=prices,
                volumes=volumes,
                dates=dates,
                current_price=current_price,
                daily_change=daily_change,
                daily_change_percent=daily_change_percent
            )
        except Exception as e:
            print(f"❌ Error converting data for {ticker}: {str(e)}")
            return None
    
    def _expected_return_from_rating(self, rating: str) -> float:
        """What return direction we expect from each rating."""
        expectations = {
            'BUY': 3.0,        # Expect 3%+ gains
            'RISKY_BUY': 5.0,  # Expect 5%+ gains (higher risk/reward)
            'HOLD': 0.0,       # Expect neutral
            'SELL': -2.0       # Expect 2%+ losses (or protection from them)
        }
        return expectations.get(rating, 0.0)
    
    def _is_direction_correct(self, rating: str, actual_return: float) -> bool:
        """Check if our rating correctly predicted direction."""
        if rating == 'BUY' and actual_return > 0:
            return True
        elif rating == 'RISKY_BUY' and actual_return > 0:
            return True
        elif rating == 'SELL' and actual_return < 0:
            return True
        elif rating == 'HOLD' and abs(actual_return) < 2.0:  # Stayed relatively flat
            return True
        return False
    
    def calculate_performance_metrics(self) -> Dict:
        """Calculate overall performance statistics."""
        metrics = {}
        
        for rating, data in self.results.items():
            if not data['trades']:
                continue
                
            trades = data['trades']
            returns = [t['actual_return'] for t in trades]
            correct_predictions = [t['correct_direction'] for t in trades]
            
            metrics[rating] = {
                'total_signals': len(trades),
                'hit_rate': sum(correct_predictions) / len(correct_predictions) * 100,
                'avg_return': np.mean(returns),
                'best_return': max(returns) if returns else 0,
                'worst_return': min(returns) if returns else 0,
                'std_deviation': np.std(returns) if returns else 0,
                'profitable_trades': len([r for r in returns if r > 0]),
                'profit_percentage': len([r for r in returns if r > 0]) / len(returns) * 100 if returns else 0
            }
        
        return metrics
    
    def generate_validation_report(self, metrics: Dict) -> str:
        """Generate a comprehensive validation report."""
        report = """
🔍 STOCK FORECASTER VALIDATION REPORT
=====================================

This report validates our analysis against real historical data to ensure
our ratings are based on solid analytical foundations, not hallucinations.

METHODOLOGY:
- Tested signals on historical data using sliding window approach
- Simulated real-world trading: analysis → wait → measure actual results
- Measured both direction accuracy and magnitude of returns

"""
        
        for rating, stats in metrics.items():
            if stats['total_signals'] == 0:
                continue
                
            # Determine if performance meets expectations
            meets_expectations = self._validate_rating_performance(rating, stats)
            status = "✅ VALIDATED" if meets_expectations else "⚠️ NEEDS REVIEW"
            
            report += f"""
{rating} SIGNALS - {status}
{'=' * (len(rating) + 20)}
Total Signals Tested: {stats['total_signals']}
Direction Accuracy: {stats['hit_rate']:.1f}%
Average Return: {stats['avg_return']:+.2f}%
Best Trade: {stats['best_return']:+.2f}%
Worst Trade: {stats['worst_return']:+.2f}%
Volatility (Std Dev): {stats['std_deviation']:.2f}%
Profitable Trades: {stats['profitable_trades']}/{stats['total_signals']} ({stats['profit_percentage']:.1f}%)

ANALYSIS:
{self._get_rating_analysis(rating, stats)}
"""
        
        # Overall assessment
        overall_quality = self._assess_overall_quality(metrics)
        report += f"""

OVERALL ASSESSMENT: {overall_quality['status']}
{'=' * 40}
{overall_quality['summary']}

CONFIDENCE LEVEL: {overall_quality['confidence']}/5
REAL-WORLD VALIDITY: {overall_quality['validity']}

🎯 CONCLUSION: {overall_quality['conclusion']}
"""
        
        return report
    
    def _validate_rating_performance(self, rating: str, stats: Dict) -> bool:
        """Validate if a rating type performs as expected."""
        if rating == 'BUY':
            # BUY should have >60% hit rate and positive average return
            return stats['hit_rate'] >= 60 and stats['avg_return'] > 0
        elif rating == 'RISKY_BUY':
            # RISKY_BUY should have >50% hit rate but higher returns when right
            return stats['hit_rate'] >= 50 and stats['best_return'] > 3.0
        elif rating == 'SELL':
            # SELL should protect from losses (negative returns expected)
            return stats['hit_rate'] >= 55 and stats['avg_return'] < 1.0
        elif rating == 'HOLD':
            # HOLD should be neutral (avoid big moves either way)
            return stats['hit_rate'] >= 50 and abs(stats['avg_return']) < 2.0
        return False
    
    def _get_rating_analysis(self, rating: str, stats: Dict) -> str:
        """Provide detailed analysis for each rating type."""
        if rating == 'BUY':
            if stats['hit_rate'] >= 60:
                return "Strong predictive power. BUY signals reliably identify upward moves."
            else:
                return "Needs improvement. BUY threshold may be too aggressive."
                
        elif rating == 'RISKY_BUY':
            if stats['hit_rate'] >= 50 and stats['avg_return'] > 2:
                return "Risk/reward profile validated. Higher volatility but profitable when correct."
            else:
                return "Risk assessment may need refinement. Monitor volatility vs. returns."
                
        elif rating == 'SELL':
            if stats['avg_return'] < 0:
                return "Effective at identifying downtrends and protecting capital."
            else:
                return "SELL criteria may need tightening to better identify bearish conditions."
                
        elif rating == 'HOLD':
            if abs(stats['avg_return']) < 2:
                return "Correctly identifies sideways markets and neutral conditions."
            else:
                return "HOLD criteria may need adjustment to better capture neutral sentiment."
        
        return "Insufficient data for analysis."
    
    def _assess_overall_quality(self, metrics: Dict) -> Dict:
        """Assess overall quality of the analysis system."""
        total_signals = sum(stats['total_signals'] for stats in metrics.values())
        weighted_hit_rate = sum(stats['hit_rate'] * stats['total_signals'] for stats in metrics.values()) / total_signals
        
        if weighted_hit_rate >= 65:
            status = "🟢 EXCELLENT"
            confidence = 5
            validity = "HIGH"
        elif weighted_hit_rate >= 55:
            status = "🟡 GOOD"
            confidence = 4
            validity = "MODERATE-HIGH"
        elif weighted_hit_rate >= 45:
            status = "🟠 FAIR"
            confidence = 3
            validity = "MODERATE"
        else:
            status = "🔴 POOR"
            confidence = 2
            validity = "LOW"
        
        return {
            'status': status,
            'confidence': confidence,
            'validity': validity,
            'summary': f"Overall directional accuracy: {weighted_hit_rate:.1f}% across {total_signals} historical signals",
            'conclusion': "Analysis system demonstrates solid analytical foundation" if weighted_hit_rate >= 55 else "Analysis system requires calibration improvements"
        }


def main():
    """Run validation tests on multiple stocks."""
    print("🔍 STARTING STOCK FORECASTER VALIDATION")
    print("=" * 50)
    
    # Test stocks across different sectors and market caps
    test_stocks = [
        'AAPL',    # Large cap tech
        'TSLA',    # High volatility growth
        'JPM',     # Financial sector
        'JNJ',     # Defensive healthcare
        'RIOT',    # High volatility crypto
        'PFE',     # Pharma
        'XOM',     # Energy sector
        'NVDA'     # AI/chip momentum
    ]
    
    backtest = BacktestEngine()
    
    # Run backtests
    for ticker in test_stocks:
        backtest.backtest_stock(ticker, days_back=45, hold_days=3)
    
    # Calculate performance metrics
    metrics = backtest.calculate_performance_metrics()
    
    # Generate validation report
    report = backtest.generate_validation_report(metrics)
    
    # Save report
    with open('validation_report.txt', 'w') as f:
        f.write(report)
    
    print(report)
    print(f"\n📄 Full report saved to: validation_report.txt")
    
    return metrics

if __name__ == "__main__":
    main()
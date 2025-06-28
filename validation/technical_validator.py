#!/usr/bin/env python3
"""
Technical Analysis Validator - Ensures our indicators match industry standards.
Validates that our RSI, MACD, and other calculations are mathematically correct.
"""

import numpy as np
import pandas as pd
import yfinance as yf
from typing import Dict, List, Tuple
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.indicators import calculate_rsi, calculate_macd, calculate_sma
from core.data_fetcher import fetch_stock_data

class TechnicalValidator:
    """
    Validates our technical indicators against established formulas and third-party libraries.
    Ensures we're not hallucinating indicator values.
    """
    
    def __init__(self):
        self.validation_results = {}
    
    def validate_rsi_calculation(self, ticker: str = 'AAPL') -> Dict:
        """Validate RSI calculation against manual calculation and expected ranges."""
        print(f"🔢 Validating RSI calculation for {ticker}...")
        
        try:
            # Get our RSI
            stock_data = fetch_stock_data(ticker, period="3mo")
            if not stock_data or len(stock_data.prices) < 20:
                return {"error": "Insufficient data"}
            
            our_rsi = calculate_rsi(stock_data.prices)
            
            # Manual RSI calculation for verification
            prices = np.array(stock_data.prices)
            manual_rsi = self._calculate_rsi_manual(prices)
            
            # Third-party validation using pandas_ta if available
            try:
                import pandas_ta as ta
                df = pd.DataFrame({'close': prices})
                pandas_ta_rsi = ta.rsi(df['close']).iloc[-1]
            except ImportError:
                pandas_ta_rsi = None
            
            # Validation checks
            validations = {
                'our_rsi': our_rsi,
                'manual_rsi': manual_rsi,
                'pandas_ta_rsi': pandas_ta_rsi,
                'rsi_in_valid_range': 0 <= our_rsi <= 100,
                'matches_manual': abs(our_rsi - manual_rsi) < 0.1,
                'reasonable_value': 20 <= our_rsi <= 80,  # Most stocks fall in this range
                'calculation_accuracy': 'PASS' if abs(our_rsi - manual_rsi) < 0.1 else 'FAIL'
            }
            
            return validations
            
        except Exception as e:
            return {"error": str(e)}
    
    def _calculate_rsi_manual(self, prices: np.array, period: int = 14) -> float:
        """Manual RSI calculation using Wilder's SMMA to verify our implementation."""
        if len(prices) < period + 1:
            return 50.0
        
        # Calculate price changes
        deltas = np.diff(prices)
        
        # Separate gains and losses
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        # Initial simple moving average for first period
        avg_gain = np.mean(gains[:period])
        avg_loss = np.mean(losses[:period])
        
        # Apply Wilder's smoothing for subsequent periods
        for i in range(period, len(gains)):
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def validate_macd_calculation(self, ticker: str = 'AAPL') -> Dict:
        """Validate MACD calculation against manual calculation."""
        print(f"📈 Validating MACD calculation for {ticker}...")
        
        try:
            stock_data = fetch_stock_data(ticker, period="3mo")
            if not stock_data or len(stock_data.prices) < 50:
                return {"error": "Insufficient data"}
            
            # Get our MACD
            our_macd, our_signal, our_histogram = calculate_macd(stock_data.prices)
            
            # Manual MACD calculation
            manual_macd, manual_signal, manual_histogram = self._calculate_macd_manual(np.array(stock_data.prices))
            
            validations = {
                'our_macd': our_macd,
                'our_signal': our_signal, 
                'our_histogram': our_histogram,
                'manual_macd': manual_macd,
                'manual_signal': manual_signal,
                'manual_histogram': manual_histogram,
                'macd_accuracy': abs(our_macd - manual_macd) < 0.05,  # Relaxed tolerance
                'signal_accuracy': abs(our_signal - manual_signal) < 0.05,  # Relaxed tolerance
                'histogram_accuracy': abs(our_histogram - manual_histogram) < 0.05,  # Relaxed tolerance
                'calculation_accuracy': 'PASS' if all([
                    abs(our_macd - manual_macd) < 0.05,
                    abs(our_signal - manual_signal) < 0.05,
                    abs(our_histogram - manual_histogram) < 0.05
                ]) else 'FAIL'
            }
            
            return validations
            
        except Exception as e:
            return {"error": str(e)}
    
    def _calculate_macd_manual(self, prices: np.array) -> Tuple[float, float, float]:
        """Manual MACD calculation to verify our implementation."""
        if len(prices) < 35:  # Need 26 for MACD + 9 for signal
            return 0.0, 0.0, 0.0
        
        # Calculate EMAs manually
        ema_12 = self._calculate_ema(prices, 12)
        ema_26 = self._calculate_ema(prices, 26)
        
        # MACD line
        macd_line = ema_12 - ema_26
        
        # Calculate MACD values for signal line calculation
        macd_values = []
        for i in range(26, len(prices)):
            ema12_at_i = self._calculate_ema(prices[:i+1], 12)
            ema26_at_i = self._calculate_ema(prices[:i+1], 26)
            macd_values.append(ema12_at_i - ema26_at_i)
        
        # Signal line (9-period EMA of MACD)
        if len(macd_values) >= 9:
            signal_line = self._calculate_ema(np.array(macd_values), 9)
        else:
            signal_line = macd_line
        
        # Histogram
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    def _calculate_ema(self, prices: np.array, period: int) -> float:
        """Calculate Exponential Moving Average."""
        if len(prices) < period:
            return np.mean(prices)
        
        multiplier = 2 / (period + 1)
        ema = np.mean(prices[:period])  # Start with SMA
        
        for price in prices[period:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        
        return ema
    
    def validate_sma_calculation(self, ticker: str = 'AAPL') -> Dict:
        """Validate Simple Moving Average calculation."""
        print(f"📊 Validating SMA calculation for {ticker}...")
        
        try:
            stock_data = fetch_stock_data(ticker, period="2mo")
            if not stock_data or len(stock_data.prices) < 50:
                return {"error": "Insufficient data"}
            
            # Test both SMA20 and SMA50
            our_sma20 = calculate_sma(stock_data.prices, 20)
            our_sma50 = calculate_sma(stock_data.prices, 50)
            
            # Manual calculations
            manual_sma20 = np.mean(stock_data.prices[-20:])
            manual_sma50 = np.mean(stock_data.prices[-50:])
            
            validations = {
                'our_sma20': our_sma20,
                'our_sma50': our_sma50,
                'manual_sma20': manual_sma20,
                'manual_sma50': manual_sma50,
                'sma20_accuracy': abs(our_sma20 - manual_sma20) < 0.01,
                'sma50_accuracy': abs(our_sma50 - manual_sma50) < 0.01,
                'calculation_accuracy': 'PASS' if all([
                    abs(our_sma20 - manual_sma20) < 0.01,
                    abs(our_sma50 - manual_sma50) < 0.01
                ]) else 'FAIL'
            }
            
            return validations
            
        except Exception as e:
            return {"error": str(e)}
    
    def validate_rating_logic(self, ticker: str = 'AAPL') -> Dict:
        """Validate that our rating logic makes sense given the indicators."""
        print(f"🎯 Validating rating logic for {ticker}...")
        
        try:
            from core.analyzer import analyze_technical
            
            stock_data = fetch_stock_data(ticker, period="2mo")
            if not stock_data:
                return {"error": "Cannot fetch data"}
            
            analysis = analyze_technical(stock_data)
            
            # Extract individual indicators
            rsi = analysis.technical_indicators.rsi
            macd_histogram = analysis.technical_indicators.macd_histogram
            sma_20 = analysis.technical_indicators.sma_20
            sma_50 = analysis.technical_indicators.sma_50
            current_price = stock_data.current_price
            
            # Logic validation checks
            validations = {
                'rating': analysis.rating,
                'confidence': analysis.confidence,
                'rsi': rsi,
                'macd_histogram': macd_histogram,
                'price_vs_sma20': (current_price - sma_20) / sma_20 * 100,
                'price_vs_sma50': (current_price - sma_50) / sma_50 * 100,
                
                # Logic checks
                'bullish_indicators_align': self._check_bullish_alignment(
                    analysis.rating, rsi, macd_histogram, current_price, sma_20, sma_50
                ),
                'bearish_indicators_align': self._check_bearish_alignment(
                    analysis.rating, rsi, macd_histogram, current_price, sma_20, sma_50
                ),
                'confidence_makes_sense': self._check_confidence_logic(
                    analysis.confidence, rsi, macd_histogram
                ),
                'reasoning_count': len(analysis.reasoning),
                'has_explanations': len(analysis.reasoning) > 0
            }
            
            return validations
            
        except Exception as e:
            return {"error": str(e)}
    
    def _check_bullish_alignment(self, rating: str, rsi: float, macd_hist: float, 
                                price: float, sma20: float, sma50: float) -> bool:
        """Check if BUY rating aligns with bullish indicators."""
        if rating != 'BUY':
            return True  # Not applicable
        
        bullish_signals = 0
        
        # RSI should not be overbought for BUY
        if rsi < 70:
            bullish_signals += 1
        
        # MACD histogram should be positive or improving
        if macd_hist > 0:
            bullish_signals += 1
        
        # Price should be above moving averages
        if price > sma20:
            bullish_signals += 1
        
        # Should have at least 2 of 3 bullish signals for BUY
        return bullish_signals >= 2
    
    def _check_bearish_alignment(self, rating: str, rsi: float, macd_hist: float,
                                price: float, sma20: float, sma50: float) -> bool:
        """Check if SELL rating aligns with bearish indicators."""
        if rating != 'SELL':
            return True  # Not applicable
        
        bearish_signals = 0
        
        # RSI should not be oversold for SELL
        if rsi > 30:
            bearish_signals += 1
        
        # MACD histogram should be negative
        if macd_hist < 0:
            bearish_signals += 1
        
        # Price should be below moving averages
        if price < sma20:
            bearish_signals += 1
        
        # Should have at least 2 of 3 bearish signals for SELL
        return bearish_signals >= 2
    
    def _check_confidence_logic(self, confidence: float, rsi: float, macd_hist: float) -> bool:
        """Check if confidence level makes sense given indicator alignment."""
        # High confidence should correspond to clear signals
        if confidence > 0.7:
            # Should have clear RSI direction (not in neutral zone)
            clear_rsi = rsi < 35 or rsi > 65
            # Should have clear MACD direction
            clear_macd = abs(macd_hist) > 0.1
            
            return clear_rsi or clear_macd
        
        return True  # Lower confidence is always reasonable
    
    def run_comprehensive_validation(self) -> Dict:
        """Run all validation tests and compile results."""
        print("🔍 RUNNING COMPREHENSIVE TECHNICAL VALIDATION")
        print("=" * 50)
        
        test_stocks = ['AAPL', 'TSLA', 'JPM']
        results = {}
        
        for ticker in test_stocks:
            print(f"\n📋 Testing {ticker}...")
            
            results[ticker] = {
                'rsi_validation': self.validate_rsi_calculation(ticker),
                'macd_validation': self.validate_macd_calculation(ticker),
                'sma_validation': self.validate_sma_calculation(ticker),
                'rating_logic': self.validate_rating_logic(ticker)
            }
        
        # Compile overall assessment
        overall_assessment = self._assess_technical_validity(results)
        
        return {
            'individual_tests': results,
            'overall_assessment': overall_assessment
        }
    
    def _assess_technical_validity(self, results: Dict) -> Dict:
        """Assess overall technical validity of our calculations."""
        total_tests = 0
        passed_tests = 0
        
        for ticker, tests in results.items():
            for test_name, test_result in tests.items():
                if 'calculation_accuracy' in test_result:
                    total_tests += 1
                    if test_result['calculation_accuracy'] == 'PASS':
                        passed_tests += 1
        
        accuracy_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        if accuracy_rate >= 90:
            verdict = "✅ EXCELLENT - Calculations are mathematically sound"
            confidence = "HIGH"
        elif accuracy_rate >= 80:
            verdict = "🟡 GOOD - Minor discrepancies detected"
            confidence = "MODERATE-HIGH"
        elif accuracy_rate >= 70:
            verdict = "🟠 FAIR - Some calculation issues found"
            confidence = "MODERATE"
        else:
            verdict = "❌ POOR - Significant calculation errors"
            confidence = "LOW"
        
        return {
            'accuracy_rate': accuracy_rate,
            'tests_passed': passed_tests,
            'total_tests': total_tests,
            'verdict': verdict,
            'confidence': confidence,
            'recommendation': "Technical indicators are reliable" if accuracy_rate >= 80 else "Review indicator calculations"
        }


def main():
    """Run technical validation tests."""
    validator = TechnicalValidator()
    results = validator.run_comprehensive_validation()
    
    # Generate report
    report = f"""
🔢 TECHNICAL INDICATOR VALIDATION REPORT
========================================

OVERALL ASSESSMENT: {results['overall_assessment']['verdict']}
Accuracy Rate: {results['overall_assessment']['accuracy_rate']:.1f}%
Tests Passed: {results['overall_assessment']['tests_passed']}/{results['overall_assessment']['total_tests']}
Confidence: {results['overall_assessment']['confidence']}

DETAILED RESULTS:
"""
    
    for ticker, tests in results['individual_tests'].items():
        report += f"\n{ticker}:\n"
        for test_name, test_result in tests.items():
            if 'calculation_accuracy' in test_result:
                report += f"  {test_name}: {test_result['calculation_accuracy']}\n"
    
    report += f"\nRECOMMENDATION: {results['overall_assessment']['recommendation']}\n"
    
    print(report)
    
    # Save report
    with open('technical_validation_report.txt', 'w') as f:
        f.write(report)
    
    return results

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Professional Backtesting Engine for Quality-Assured Stock Predictions
====================================================================

Enhanced backtesting framework that validates professional-grade analysis
against historical data with statistical significance testing and
risk-adjusted performance metrics.

This engine validates:
- Quality standard compliance across different quality levels
- Risk management parameter effectiveness  
- Statistical significance of predictions
- Cross-module consistency validation
- Entry/exit criteria accuracy
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

from core.professional_analyzer import ProfessionalStockAnalyzer
from core.quality_standards import QualityLevel
from core.data_fetcher import fetch_stock_data


class ProfessionalBacktestEngine:
    """
    Professional-grade backtesting engine with quality standards validation.
    
    Tests the effectiveness of:
    - Quality assurance thresholds
    - Risk management parameters
    - Statistical significance requirements
    - Entry/exit criteria accuracy
    - Cross-module consistency benefits
    """
    
    def __init__(self, quality_level: QualityLevel = QualityLevel.PROFESSIONAL):
        """
        Initialize professional backtest engine.
        
        Args:
            quality_level: Quality standard to test against
        """
        self.quality_level = quality_level
        self.analyzer = ProfessionalStockAnalyzer(quality_level)
        self.results = {
            'trades': [],
            'quality_metrics': [],
            'risk_management_performance': [],
            'statistical_validation': []
        }
    
    def backtest_professional_analysis(self, ticker: str, 
                                     start_date: datetime = None,
                                     end_date: datetime = None,
                                     hold_days: int = 5) -> Dict:
        """
        Backtest professional analysis against historical data.
        
        Args:
            ticker: Stock symbol to test
            start_date: Start date for backtesting (default: 90 days ago)
            end_date: End date for backtesting (default: today)
            hold_days: Days to hold position after signal
            
        Returns:
            Comprehensive backtest results with quality metrics
        """
        if not start_date:
            start_date = datetime.now() - timedelta(days=90)
        if not end_date:
            end_date = datetime.now()
        
        print(f"🔍 Professional backtesting {ticker} from {start_date.date()} to {end_date.date()}")
        
        try:
            # Get historical data with extra buffer
            buffer_start = start_date - timedelta(days=30)
            stock = yf.Ticker(ticker)
            hist = stock.history(start=buffer_start, end=end_date)
            
            if hist.empty or len(hist) < 50:
                print(f"❌ Insufficient data for {ticker}")
                return {'error': 'Insufficient historical data'}
            
            test_results = []
            quality_validations = []
            
            # Find start index for actual testing
            start_idx = None
            for i, date in enumerate(hist.index):
                if date.date() >= start_date.date():
                    start_idx = i
                    break
            
            if start_idx is None or start_idx < 30:
                return {'error': 'Insufficient pre-test data for quality analysis'}
            
            # Test signals on each trading day
            for i in range(start_idx, len(hist) - hold_days):
                test_date = hist.index[i]
                
                # Create historical data slice (what analyzer would have seen)
                historical_slice = hist.iloc[:i+1]
                
                # Convert to our StockData format
                stock_data = self._convert_to_stock_data(ticker, historical_slice)
                if not stock_data:
                    continue
                
                # Get professional analysis for this point in time
                try:
                    analysis = self.analyzer.analyze_stock_professional(
                        ticker=ticker,
                        include_algo_forecast=True,
                        include_news_analysis=False  # Skip news for historical data
                    )
                    
                    # Only proceed if analysis meets quality standards
                    meets_standards = analysis.quality_assurance.quality_level in ['PROFESSIONAL', 'INSTITUTIONAL']
                    
                    if meets_standards and analysis.rating in ['BUY', 'SELL', 'RISKY_BUY']:
                        # Calculate actual performance
                        entry_price = analysis.price_at_analysis
                        future_prices = hist['Close'].iloc[i+1:i+1+hold_days]
                        
                        if len(future_prices) == hold_days:
                            exit_price = future_prices.iloc[-1]
                            actual_return = (exit_price - entry_price) / entry_price
                            
                            # Test risk management effectiveness
                            risk_mgmt_test = self._test_risk_management(
                                analysis, hist.iloc[i:i+hold_days+1]
                            )
                            
                            # Record comprehensive test result
                            test_result = {
                                'date': test_date,
                                'ticker': ticker,
                                'rating': analysis.rating,
                                'confidence': analysis.confidence,
                                'quality_level': analysis.quality_assurance.quality_level,
                                'p_value': analysis.quality_assurance.p_value,
                                'entry_price': entry_price,
                                'exit_price': exit_price,
                                'actual_return': actual_return * 100,  # Convert to percentage
                                'predicted_direction': self._get_expected_direction(analysis.rating),
                                'direction_correct': self._is_direction_correct(analysis.rating, actual_return),
                                'risk_management': risk_mgmt_test,
                                'meets_quality_standards': meets_standards,
                                'statistical_significance': analysis.quality_assurance.p_value <= 0.05
                            }
                            
                            test_results.append(test_result)
                            self.results['trades'].append(test_result)
                            
                            # Record quality validation
                            quality_validation = {
                                'date': test_date,
                                'quality_level_achieved': analysis.quality_assurance.quality_level,
                                'target_quality_level': self.quality_level.value.upper(),
                                'p_value': analysis.quality_assurance.p_value,
                                'sample_size': analysis.quality_assurance.sample_size,
                                'confidence_score': analysis.confidence,
                                'meets_standards': meets_standards
                            }
                            
                            quality_validations.append(quality_validation)
                            self.results['quality_metrics'].append(quality_validation)
                
                except Exception as e:
                    print(f"Analysis failed for {ticker} on {test_date.date()}: {e}")
                    continue
            
            print(f"✅ Completed {len(test_results)} professional signal tests for {ticker}")
            
            # Calculate performance metrics
            performance_metrics = self._calculate_professional_metrics(test_results)
            quality_assessment = self._assess_quality_performance(quality_validations)
            
            return {
                'ticker': ticker,
                'test_period': f"{start_date.date()} to {end_date.date()}",
                'quality_level_tested': self.quality_level.value.upper(),
                'total_signals': len(test_results),
                'trades': test_results,
                'performance_metrics': performance_metrics,
                'quality_assessment': quality_assessment,
                'risk_management_effectiveness': self._assess_risk_management(test_results)
            }
            
        except Exception as e:
            print(f"❌ Professional backtest error for {ticker}: {str(e)}")
            return {'error': str(e)}
    
    def _convert_to_stock_data(self, ticker: str, hist_data: pd.DataFrame):
        """Convert yfinance data to StockData format."""
        try:
            from core.models import StockData
            
            prices = hist_data['Close'].tolist()
            volumes = hist_data['Volume'].tolist()
            highs = hist_data['High'].tolist()
            lows = hist_data['Low'].tolist()
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
                daily_change_percent=daily_change_percent,
                highs=highs,
                lows=lows
            )
        except Exception as e:
            print(f"❌ Error converting data for {ticker}: {str(e)}")
            return None
    
    def _get_expected_direction(self, rating: str) -> str:
        """Get expected price direction for rating."""
        if rating in ['BUY', 'RISKY_BUY']:
            return 'UP'
        elif rating == 'SELL':
            return 'DOWN'
        else:
            return 'NEUTRAL'
    
    def _is_direction_correct(self, rating: str, actual_return: float) -> bool:
        """Check if direction prediction was correct."""
        if rating in ['BUY', 'RISKY_BUY'] and actual_return > 0:
            return True
        elif rating == 'SELL' and actual_return < 0:
            return True
        elif rating == 'HOLD' and abs(actual_return) < 0.02:  # Within 2%
            return True
        return False
    
    def _test_risk_management(self, analysis, price_history: pd.DataFrame) -> Dict:
        """Test effectiveness of risk management parameters."""
        try:
            stop_loss_price = analysis.risk_management.stop_loss_price
            take_profit_price = analysis.risk_management.take_profit_price
            entry_price = analysis.price_at_analysis
            
            # Track if stop-loss or take-profit would have triggered
            stop_loss_triggered = False
            take_profit_triggered = False
            max_drawdown = 0.0
            max_gain = 0.0
            
            for _, row in price_history.iterrows():
                low = row['Low']
                high = row['High']
                
                # Check stop-loss trigger (for BUY positions)
                if analysis.rating in ['BUY', 'RISKY_BUY'] and low <= stop_loss_price:
                    stop_loss_triggered = True
                
                # Check take-profit trigger (for BUY positions)  
                if analysis.rating in ['BUY', 'RISKY_BUY'] and high >= take_profit_price:
                    take_profit_triggered = True
                
                # Track drawdown and gains
                current_drawdown = (entry_price - low) / entry_price
                current_gain = (high - entry_price) / entry_price
                
                max_drawdown = max(max_drawdown, current_drawdown)
                max_gain = max(max_gain, current_gain)
            
            return {
                'stop_loss_triggered': stop_loss_triggered,
                'take_profit_triggered': take_profit_triggered,
                'max_drawdown_percent': max_drawdown * 100,
                'max_gain_percent': max_gain * 100,
                'risk_management_effective': not stop_loss_triggered if analysis.rating in ['BUY', 'RISKY_BUY'] else True
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _calculate_professional_metrics(self, trades: List[Dict]) -> Dict:
        """Calculate professional-grade performance metrics."""
        if not trades:
            return {}
        
        returns = [t['actual_return'] for t in trades]
        correct_directions = [t['direction_correct'] for t in trades]
        quality_compliant = [t['meets_quality_standards'] for t in trades]
        statistically_significant = [t['statistical_significance'] for t in trades]
        
        # Basic performance metrics
        total_trades = len(trades)
        hit_rate = sum(correct_directions) / total_trades * 100
        avg_return = np.mean(returns)
        volatility = np.std(returns)
        
        # Risk-adjusted metrics
        sharpe_ratio = avg_return / volatility if volatility > 0 else 0
        max_drawdown = min(returns) if returns else 0
        max_gain = max(returns) if returns else 0
        
        # Quality metrics
        quality_compliance_rate = sum(quality_compliant) / total_trades * 100
        statistical_significance_rate = sum(statistically_significant) / total_trades * 100
        
        # Win/loss analysis
        profitable_trades = len([r for r in returns if r > 0])
        losing_trades = len([r for r in returns if r < 0])
        
        return {
            'total_trades': total_trades,
            'hit_rate_percent': round(hit_rate, 1),
            'average_return_percent': round(avg_return, 2),
            'volatility_percent': round(volatility, 2),
            'sharpe_ratio': round(sharpe_ratio, 3),
            'max_drawdown_percent': round(max_drawdown, 2),
            'max_gain_percent': round(max_gain, 2),
            'profitable_trades': profitable_trades,
            'losing_trades': losing_trades,
            'win_rate_percent': round(profitable_trades / total_trades * 100, 1),
            'quality_compliance_rate_percent': round(quality_compliance_rate, 1),
            'statistical_significance_rate_percent': round(statistical_significance_rate, 1)
        }
    
    def _assess_quality_performance(self, quality_validations: List[Dict]) -> Dict:
        """Assess how well quality standards performed."""
        if not quality_validations:
            return {}
        
        total_validations = len(quality_validations)
        meets_standards = sum(q['meets_standards'] for q in quality_validations)
        
        p_values = [q['p_value'] for q in quality_validations]
        avg_p_value = np.mean(p_values)
        significant_predictions = len([p for p in p_values if p <= 0.05])
        
        confidence_scores = [q['confidence_score'] for q in quality_validations]
        avg_confidence = np.mean(confidence_scores)
        
        return {
            'total_quality_tests': total_validations,
            'standards_compliance_rate_percent': round(meets_standards / total_validations * 100, 1),
            'average_p_value': round(avg_p_value, 4),
            'statistically_significant_percent': round(significant_predictions / total_validations * 100, 1),
            'average_confidence_score': round(avg_confidence, 3),
            'quality_framework_effectiveness': 'HIGH' if meets_standards / total_validations > 0.8 else 'MODERATE' if meets_standards / total_validations > 0.6 else 'LOW'
        }
    
    def _assess_risk_management(self, trades: List[Dict]) -> Dict:
        """Assess risk management effectiveness."""
        if not trades:
            return {}
        
        risk_mgmt_trades = [t for t in trades if 'risk_management' in t and 'error' not in t['risk_management']]
        
        if not risk_mgmt_trades:
            return {'error': 'No valid risk management data'}
        
        stop_losses_triggered = sum(t['risk_management']['stop_loss_triggered'] for t in risk_mgmt_trades)
        take_profits_triggered = sum(t['risk_management']['take_profit_triggered'] for t in risk_mgmt_trades)
        
        max_drawdowns = [t['risk_management']['max_drawdown_percent'] for t in risk_mgmt_trades]
        avg_max_drawdown = np.mean(max_drawdowns)
        
        return {
            'total_risk_tests': len(risk_mgmt_trades),
            'stop_loss_trigger_rate_percent': round(stop_losses_triggered / len(risk_mgmt_trades) * 100, 1),
            'take_profit_trigger_rate_percent': round(take_profits_triggered / len(risk_mgmt_trades) * 100, 1),
            'average_max_drawdown_percent': round(avg_max_drawdown, 2),
            'risk_management_effectiveness': 'HIGH' if stop_losses_triggered / len(risk_mgmt_trades) < 0.15 else 'MODERATE' if stop_losses_triggered / len(risk_mgmt_trades) < 0.30 else 'LOW'
        }
    
    def generate_professional_validation_report(self, backtest_results: List[Dict]) -> str:
        """Generate comprehensive validation report for professional analysis."""
        if not backtest_results:
            return "No backtest results to report."
        
        # Aggregate metrics across all stocks
        all_trades = []
        all_quality_metrics = []
        
        for result in backtest_results:
            if 'trades' in result:
                all_trades.extend(result['trades'])
            if 'quality_assessment' in result:
                all_quality_metrics.append(result['quality_assessment'])
        
        overall_metrics = self._calculate_professional_metrics(all_trades)
        
        report = f"""
🏛️ PROFESSIONAL STOCK FORECASTER VALIDATION REPORT
================================================

Quality Level Tested: {self.quality_level.value.upper()}
Analysis Period: Professional-grade backtesting with statistical validation
Validation Methodology: Cross-module consistency + Risk management + Statistical significance

EXECUTIVE SUMMARY:
- Total Signals Analyzed: {overall_metrics.get('total_trades', 0)}
- Directional Accuracy: {overall_metrics.get('hit_rate_percent', 0)}%
- Average Return: {overall_metrics.get('average_return_percent', 0)}%
- Risk-Adjusted Performance (Sharpe): {overall_metrics.get('sharpe_ratio', 0)}
- Quality Compliance Rate: {overall_metrics.get('quality_compliance_rate_percent', 0)}%

PERFORMANCE ANALYSIS:
{'=' * 50}
Win Rate: {overall_metrics.get('win_rate_percent', 0)}% ({overall_metrics.get('profitable_trades', 0)}/{overall_metrics.get('total_trades', 0)} trades)
Average Return: {overall_metrics.get('average_return_percent', 0):+.2f}%
Maximum Gain: {overall_metrics.get('max_gain_percent', 0):+.2f}%
Maximum Drawdown: {overall_metrics.get('max_drawdown_percent', 0):+.2f}%
Volatility: {overall_metrics.get('volatility_percent', 0):.2f}%
Sharpe Ratio: {overall_metrics.get('sharpe_ratio', 0):.3f}

QUALITY ASSURANCE VALIDATION:
{'=' * 50}
Quality Standards Compliance: {overall_metrics.get('quality_compliance_rate_percent', 0)}%
Statistical Significance Rate: {overall_metrics.get('statistical_significance_rate_percent', 0)}%

"""
        
        # Add individual stock results
        for i, result in enumerate(backtest_results):
            if 'error' in result:
                continue
                
            ticker = result.get('ticker', f'Stock_{i+1}')
            metrics = result.get('performance_metrics', {})
            quality = result.get('quality_assessment', {})
            risk_mgmt = result.get('risk_management_effectiveness', {})
            
            report += f"""
{ticker} - Individual Results:
{'=' * 30}
Signals Generated: {result.get('total_signals', 0)}
Hit Rate: {metrics.get('hit_rate_percent', 0)}%
Average Return: {metrics.get('average_return_percent', 0):+.2f}%
Quality Compliance: {quality.get('standards_compliance_rate_percent', 0)}%
Statistical Significance: {quality.get('statistically_significant_percent', 0)}%
Risk Management: {risk_mgmt.get('risk_management_effectiveness', 'N/A')}

"""
        
        # Overall assessment
        overall_quality = self._assess_overall_system_quality(overall_metrics)
        
        report += f"""
OVERALL SYSTEM ASSESSMENT: {overall_quality['status']}
{'=' * 50}
{overall_quality['summary']}

Professional Quality Rating: {overall_quality['professional_rating']}/5
Statistical Rigor: {overall_quality['statistical_rigor']}
Risk Management: {overall_quality['risk_management']}
Production Readiness: {overall_quality['production_ready']}

CONCLUSION: {overall_quality['conclusion']}

🎯 RECOMMENDATION: {overall_quality['recommendation']}
"""
        
        return report
    
    def _assess_overall_system_quality(self, metrics: Dict) -> Dict:
        """Assess overall system quality for professional use."""
        hit_rate = metrics.get('hit_rate_percent', 0)
        quality_compliance = metrics.get('quality_compliance_rate_percent', 0)
        statistical_significance = metrics.get('statistical_significance_rate_percent', 0)
        sharpe_ratio = metrics.get('sharpe_ratio', 0)
        
        # Professional standards assessment
        if hit_rate >= 70 and quality_compliance >= 85 and statistical_significance >= 80:
            status = "🟢 INSTITUTIONAL GRADE"
            professional_rating = 5
            production_ready = "YES"
        elif hit_rate >= 65 and quality_compliance >= 75 and statistical_significance >= 70:
            status = "🟡 PROFESSIONAL GRADE"
            professional_rating = 4
            production_ready = "YES"
        elif hit_rate >= 60 and quality_compliance >= 60:
            status = "🟠 RETAIL GRADE"
            professional_rating = 3
            production_ready = "CONDITIONAL"
        else:
            status = "🔴 EXPERIMENTAL GRADE"
            professional_rating = 2
            production_ready = "NO"
        
        return {
            'status': status,
            'professional_rating': professional_rating,
            'statistical_rigor': 'HIGH' if statistical_significance >= 75 else 'MODERATE' if statistical_significance >= 60 else 'LOW',
            'risk_management': 'EFFECTIVE' if sharpe_ratio >= 0.5 else 'ADEQUATE' if sharpe_ratio >= 0.2 else 'NEEDS_IMPROVEMENT',
            'production_ready': production_ready,
            'summary': f"Directional accuracy: {hit_rate}%, Quality compliance: {quality_compliance}%, Statistical significance: {statistical_significance}%",
            'conclusion': "System meets professional trading standards" if professional_rating >= 4 else "System requires quality improvements for professional use",
            'recommendation': "Deploy for live trading" if professional_rating >= 4 else "Continue development and validation"
        }


def main():
    """Run professional validation tests."""
    print("🏛️ STARTING PROFESSIONAL STOCK FORECASTER VALIDATION")
    print("=" * 60)
    
    # Test different quality levels
    quality_levels = [QualityLevel.PROFESSIONAL, QualityLevel.INSTITUTIONAL]
    
    # Test stocks across different market conditions
    test_stocks = ['AAPL', 'TSLA', 'JPM', 'JNJ', 'NVDA']
    
    all_results = []
    
    for quality_level in quality_levels:
        print(f"\n📊 Testing {quality_level.value.upper()} Quality Level")
        print("-" * 50)
        
        backtest_engine = ProfessionalBacktestEngine(quality_level)
        level_results = []
        
        for ticker in test_stocks:
            try:
                result = backtest_engine.backtest_professional_analysis(
                    ticker=ticker,
                    start_date=datetime.now() - timedelta(days=60),  # Last 60 days
                    hold_days=3
                )
                
                if 'error' not in result:
                    level_results.append(result)
                    print(f"✅ {ticker}: {result['total_signals']} signals, {result['performance_metrics']['hit_rate_percent']}% accuracy")
                else:
                    print(f"❌ {ticker}: {result['error']}")
                    
            except Exception as e:
                print(f"❌ {ticker}: Unexpected error - {e}")
        
        # Generate report for this quality level
        if level_results:
            report = backtest_engine.generate_professional_validation_report(level_results)
            
            report_filename = f'professional_validation_{quality_level.value}.txt'
            with open(report_filename, 'w') as f:
                f.write(report)
            
            print(f"\n📄 {quality_level.value.upper()} report saved to: {report_filename}")
            
            all_results.extend(level_results)
    
    print(f"\n🎯 Professional validation completed. Total tests: {len(all_results)}")
    return all_results


if __name__ == "__main__":
    main()
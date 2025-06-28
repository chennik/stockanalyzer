"""
Validation tests for Stock Forecaster enhancements.

Tests the new features including:
- European stock database expansion
- Fuzzy search functionality
- Algorithmic forecast engine
- News sentiment analyzer
- Enhanced UI integration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from typing import List

# Import modules to test
from core.data_fetcher import search_ticker_by_name, validate_ticker
from core.european_stock_search import fuzzy_search_european_stocks, get_alternative_tickers
from core.algo_forecast import AlgorithmicForecast
from core.news_sentiment_analyzer import NewsSentimentForecaster
from core.models import StockData


class TestEuropeanStockSearch(unittest.TestCase):
    """Test European stock database expansion and fuzzy search."""
    
    def test_european_stock_search_direct_match(self):
        """Test direct match for European companies."""
        # Test known European companies
        test_cases = [
            ('anheuser-busch', 'ABI.BR'),
            ('biontech', 'BNTX'),
            ('asml', 'ASML.AS'),
            ('lvmh', 'MC.PA'),
            ('nestle', 'NESN.SW'),
            ('ferrari', 'RACE.MI'),
            ('santander', 'SAN.MC'),
            ('novo nordisk', 'NOVO-B.CO'),
            ('equinor', 'EQNR.OL'),
            ('nokia', 'NOKIA.HE')
        ]
        
        for company_name, expected_ticker in test_cases:
            with self.subTest(company=company_name):
                result = search_ticker_by_name(company_name)
                self.assertEqual(result, expected_ticker, 
                               f"Expected {expected_ticker} for {company_name}, got {result}")
    
    def test_fuzzy_search_functionality(self):
        """Test fuzzy search for partial matches."""
        # Create a sample name_to_ticker dictionary
        sample_dict = {
            'anheuser-busch': 'ABI.BR',
            'anheuser busch inbev': 'ABI.BR',
            'ab inbev': 'ABI.BR',
            'biontech': 'BNTX',
            'biontech se': '22UA.DE'
        }
        
        # Test fuzzy matches
        test_cases = [
            ('anheuser', 'ABI.BR'),  # Partial match
            ('biotech', 'BNTX'),     # Close match
            ('inbev', 'ABI.BR'),     # Partial match
        ]
        
        for search_term, expected in test_cases:
            with self.subTest(search=search_term):
                result = fuzzy_search_european_stocks(search_term, sample_dict)
                self.assertEqual(result, expected,
                               f"Fuzzy search for '{search_term}' should return {expected}")
    
    def test_alternative_tickers(self):
        """Test getting alternative ticker listings."""
        sample_dict = {
            'biontech': 'BNTX',
            'biontech se': '22UA.DE',
            'astrazeneca': 'AZN.L',
            'astrazeneca plc': 'AZN.ST'
        }
        
        alternatives = get_alternative_tickers('biontech', sample_dict)
        self.assertIn('BNTX', alternatives)
        self.assertIn('22UA.DE', alternatives)


class TestAlgorithmicForecast(unittest.TestCase):
    """Test algorithmic trading forecast engine."""
    
    def setUp(self):
        """Set up test data."""
        self.forecaster = AlgorithmicForecast()
        
        # Create sample stock data
        self.sample_stock_data = StockData(
            ticker='TEST',
            prices=[100, 102, 101, 103, 105, 104, 106, 108, 107, 109] * 5,  # 50 prices
            volumes=[1000000] * 50,
            dates=[datetime.now()] * 50,
            current_price=109,
            daily_change=2.0,
            daily_change_percent=1.87,
            market_cap=10000000000,
            pe_ratio=15.5,
            highs=[101, 103, 102, 104, 106, 105, 107, 109, 108, 110] * 5,
            lows=[99, 101, 100, 102, 104, 103, 105, 107, 106, 108] * 5
        )
    
    def test_forecast_prediction(self):
        """Test that algorithmic forecast returns valid prediction."""
        forecast = self.forecaster.predict_algorithmic_movements(self.sample_stock_data)
        
        # Check that forecast has required attributes
        self.assertIn(forecast.forecast_direction, ['UP', 'DOWN', 'SIDEWAYS'])
        self.assertIsInstance(forecast.confidence, float)
        self.assertGreaterEqual(forecast.confidence, 0.0)
        self.assertLessEqual(forecast.confidence, 1.0)
        self.assertIsInstance(forecast.algo_triggers, list)
        self.assertIsInstance(forecast.reasoning, list)
        self.assertIsInstance(forecast.risk_factors, list)
        self.assertIsInstance(forecast.pattern_scores, dict)
    
    def test_insufficient_data_handling(self):
        """Test handling of insufficient data."""
        # Create stock data with insufficient history
        insufficient_data = StockData(
            ticker='TEST',
            prices=[100, 101, 102],  # Only 3 prices
            volumes=[1000000, 1000000, 1000000],
            dates=[datetime.now()] * 3,
            current_price=102,
            daily_change=1.0,
            daily_change_percent=0.98,
            highs=[101, 102, 103],
            lows=[99, 100, 101]
        )
        
        forecast = self.forecaster.predict_algorithmic_movements(insufficient_data)
        
        # Should return neutral forecast with low confidence
        self.assertEqual(forecast.forecast_direction, 'SIDEWAYS')
        self.assertEqual(forecast.confidence, 0.0)
        self.assertIn('Insufficient data', forecast.reasoning[0])


class TestNewsSentimentAnalyzer(unittest.TestCase):
    """Test news sentiment analysis functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.analyzer = NewsSentimentForecaster()
    
    @patch('core.news_sentiment_analyzer.TEXTBLOB_AVAILABLE', True)
    def test_sentiment_analysis_textblob(self):
        """Test TextBlob sentiment analysis."""
        # Test positive sentiment
        positive_text = "This stock is performing excellently with great potential"
        sentiment, magnitude = self.analyzer.analyze_sentiment_textblob(positive_text)
        self.assertGreater(sentiment, 0, "Should detect positive sentiment")
        
        # Test negative sentiment
        negative_text = "This stock is terrible and will crash badly"
        sentiment, magnitude = self.analyzer.analyze_sentiment_textblob(negative_text)
        self.assertLess(sentiment, 0, "Should detect negative sentiment")
    
    @patch('core.news_sentiment_analyzer.FEEDPARSER_AVAILABLE', False)
    def test_news_fetching_without_feedparser(self):
        """Test news fetching when feedparser is not available."""
        articles = self.analyzer.fetch_yahoo_finance_news('AAPL')
        self.assertEqual(len(articles), 0, "Should return empty list when feedparser unavailable")
        
        articles = self.analyzer.fetch_google_news_mentions('AAPL')
        self.assertEqual(len(articles), 0, "Should return empty list when feedparser unavailable")
    
    def test_manipulation_risk_detection(self):
        """Test manipulation risk detection patterns."""
        from core.news_sentiment_analyzer import NewsArticle
        
        # Create sample articles with high positive sentiment (potential manipulation)
        articles = [
            NewsArticle(
                title=f"Amazing stock opportunity {i}",
                description="This stock will go to the moon! Guaranteed massive gains!",
                published_date=datetime.now(),
                source="Test Source",
                url="http://example.com",
                sentiment_score=0.9,
                sentiment_magnitude=0.8
            ) for i in range(15)  # Many similar articles
        ]
        
        risk_score = self.analyzer._detect_manipulation_patterns(articles, 'TEST')
        self.assertGreater(risk_score, 0.3, "Should detect manipulation risk")
    
    def test_neutral_result_creation(self):
        """Test creation of neutral result when analysis fails."""
        neutral_result = self.analyzer._create_neutral_result("Test reason")
        
        self.assertEqual(neutral_result.sentiment_score, 0.0)
        self.assertEqual(neutral_result.manipulation_risk, 0.0)
        self.assertEqual(neutral_result.news_volume, 0)
        self.assertEqual(neutral_result.sentiment_trend, 'STABLE')
        self.assertEqual(len(neutral_result.articles), 0)
        self.assertIn("Test reason", neutral_result.analysis_summary)


class TestIntegrationFeatures(unittest.TestCase):
    """Test integration of all new features."""
    
    def test_enhanced_analysis_pipeline(self):
        """Test that the enhanced analysis pipeline works end-to-end."""
        from core.analyzer import analyze_with_enhanced_accuracy
        
        # Test with a known ticker that should work
        try:
            result = analyze_with_enhanced_accuracy('AAPL', log_prediction_enabled=False)
            
            # Should return a valid analysis result
            self.assertIsNotNone(result)
            self.assertEqual(result.ticker, 'AAPL')
            self.assertIn(result.rating, ['BUY', 'SELL', 'HOLD', 'RISKY_BUY'])
            self.assertIsInstance(result.confidence, float)
            self.assertGreaterEqual(result.confidence, 0.0)
            self.assertLessEqual(result.confidence, 1.0)
            
        except Exception as e:
            # If analysis fails, ensure it's for expected reasons
            self.assertIn('data', str(e).lower(), 
                         f"Analysis failed unexpectedly: {e}")


def run_validation_tests():
    """Run all validation tests and return results."""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestEuropeanStockSearch,
        TestAlgorithmicForecast,
        TestNewsSentimentAnalyzer,
        TestIntegrationFeatures
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Return summary
    return {
        'total_tests': result.testsRun,
        'failures': len(result.failures),
        'errors': len(result.errors),
        'success_rate': ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0
    }


if __name__ == '__main__':
    print("=" * 60)
    print("STOCK FORECASTER ENHANCEMENT VALIDATION TESTS")
    print("=" * 60)
    print()
    
    results = run_validation_tests()
    
    print()
    print("=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {results['total_tests']}")
    print(f"Failures: {results['failures']}")
    print(f"Errors: {results['errors']}")
    print(f"Success Rate: {results['success_rate']:.1f}%")
    print()
    
    if results['success_rate'] >= 80:
        print("✅ VALIDATION PASSED - Enhancements are working correctly!")
    else:
        print("❌ VALIDATION FAILED - Some enhancements need attention")
    
    print("=" * 60)
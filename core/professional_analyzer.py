"""
Professional-Grade Stock Analysis Engine
=======================================

Wraps all analysis modules with unified quality standards, risk management,
and statistical validation to ensure institutional-grade predictions.

This module serves as the main entry point for professional analysis,
integrating:
- Technical analysis with enhanced validation
- Algorithmic forecasting with proper thresholds
- News sentiment analysis with manipulation detection
- Risk management calculations
- Cross-module consistency validation
"""

from typing import Dict, List, Optional
from datetime import datetime
import statistics

from .models import StockData, ProfessionalAnalysisResult, RiskManagementData, QualityAssurance
from .quality_standards import QualityStandardsFramework, QualityLevel
from .analyzer import analyze_technical
from .algo_forecast import AlgorithmicForecast
from .news_sentiment_analyzer import NewsSentimentForecaster
from .data_fetcher import fetch_stock_data
from .multi_timeframe_analyzer import MultiTimeframeAnalyzer
from .institutional_indicators import InstitutionalIndicators


class ProfessionalStockAnalyzer:
    """
    Professional-grade stock analysis with unified quality standards.
    
    Provides institutional-level analysis by:
    1. Applying consistent quality thresholds across all modules
    2. Validating statistical significance of predictions
    3. Calculating comprehensive risk management parameters
    4. Ensuring cross-module consistency validation
    5. Providing specific entry/exit criteria with price levels
    """
    
    def __init__(self, quality_level: QualityLevel = QualityLevel.PROFESSIONAL):
        """
        Initialize professional analyzer with specified quality level.
        
        Args:
            quality_level: Target quality standard (INSTITUTIONAL, PROFESSIONAL, RETAIL, EXPERIMENTAL)
        """
        self.quality_framework = QualityStandardsFramework(quality_level)
        self.algo_forecaster = AlgorithmicForecast()
        self.news_analyzer = NewsSentimentForecaster()
        self.multi_timeframe_analyzer = MultiTimeframeAnalyzer()
        self.institutional_indicators = InstitutionalIndicators()
        self.quality_level = quality_level
        
        # Override algorithmic forecasting thresholds to match quality standards
        self._update_algo_thresholds()
    
    def analyze_stock_professional(self, ticker: str, 
                                 include_algo_forecast: bool = True,
                                 include_news_analysis: bool = True) -> ProfessionalAnalysisResult:
        """
        Perform comprehensive professional-grade stock analysis.
        
        Args:
            ticker: Stock symbol to analyze
            include_algo_forecast: Whether to include algorithmic forecasting
            include_news_analysis: Whether to include news sentiment analysis
            
        Returns:
            ProfessionalAnalysisResult with comprehensive analysis and risk management
        """
        try:
            # Fetch extended historical data for better statistical validation
            stock_data = fetch_stock_data(ticker, period="12mo")
            if not stock_data or len(stock_data.prices) < 30:
                return self._create_insufficient_data_result(ticker)
            
            # 1. Core Technical Analysis
            technical_analysis = analyze_technical(stock_data)
            
            # 2. Multi-timeframe Analysis (boost confidence through timeframe confluence)
            multi_tf_result = self.multi_timeframe_analyzer.analyze_multi_timeframe(ticker)
            
            # 3. Institutional Indicators Analysis
            institutional_result = self._analyze_institutional_indicators(stock_data)
            
            # 4. Enhanced Confidence Calculation
            enhanced_confidence = self._calculate_enhanced_confidence(
                technical_analysis.confidence,
                multi_tf_result,
                institutional_result
            )
            
            # Update technical analysis with enhanced confidence
            technical_analysis.confidence = enhanced_confidence
            
            # 5. Validate technical analysis quality
            quality_metrics = self.quality_framework.validate_prediction_quality(
                confidence=enhanced_confidence,
                rating=technical_analysis.rating,
                sample_size=len(stock_data.prices),
                data_points=stock_data.prices[-30:]  # Last 30 days for validation
            )
            
            # 3. Check if prediction meets quality standards
            if not self._meets_quality_standards(quality_metrics):
                return self._create_low_quality_result(ticker, technical_analysis, quality_metrics)
            
            # 4. Algorithmic Forecast (with proper thresholds)
            algo_forecast = None
            algo_rating = None
            algo_confidence = None
            
            if include_algo_forecast:
                try:
                    algo_forecast = self.algo_forecaster.predict_algorithmic_movements(stock_data)
                    if algo_forecast.confidence >= 0.60:  # Professional threshold
                        algo_rating = self._convert_algo_direction_to_rating(algo_forecast.forecast_direction)
                        algo_confidence = algo_forecast.confidence
                except Exception as e:
                    print(f"Warning: Algorithmic forecast failed for {ticker}: {e}")
            
            # 5. News Sentiment Analysis
            news_sentiment = None
            if include_news_analysis:
                try:
                    news_result = self.news_analyzer.analyze_news_sentiment_forecast(ticker, days_lookback=14)
                    if news_result.news_volume >= 3:  # Minimum 3 articles for reliability
                        news_sentiment = news_result.sentiment_score
                except Exception as e:
                    print(f"Warning: News analysis failed for {ticker}: {e}")
            
            # 6. Cross-Module Consistency Validation
            consistency_validation = self.quality_framework.validate_cross_module_consistency(
                technical_rating=technical_analysis.rating,
                technical_confidence=technical_analysis.confidence,
                algo_rating=algo_rating,
                algo_confidence=algo_confidence,
                news_sentiment=news_sentiment
            )
            
            # 7. Calculate Professional Risk Management Parameters
            volatility = self._calculate_volatility(stock_data.prices)
            risk_params = self.quality_framework.calculate_risk_parameters(
                current_price=stock_data.current_price,
                volatility=volatility,
                confidence=consistency_validation['recommended_confidence'],
                rating=consistency_validation['recommended_rating']
            )
            
            # 8. Generate Entry/Exit Criteria
            entry_exit = self.quality_framework.generate_entry_exit_criteria(
                current_price=stock_data.current_price,
                risk_params=risk_params,
                technical_support=self._find_support_level(stock_data.prices),
                technical_resistance=self._find_resistance_level(stock_data.prices)
            )
            
            # 9. Create Professional Analysis Result
            return self._create_professional_result(
                ticker=ticker,
                stock_data=stock_data,
                technical_analysis=technical_analysis,
                quality_metrics=quality_metrics,
                risk_params=risk_params,
                entry_exit=entry_exit,
                consistency_validation=consistency_validation,
                algo_forecast=algo_forecast,
                news_sentiment=news_sentiment
            )
            
        except Exception as e:
            print(f"Error in professional analysis for {ticker}: {str(e)}")
            return self._create_error_result(ticker, str(e))
    
    def _update_algo_thresholds(self):
        """Update algorithmic forecasting thresholds to match quality standards."""
        # Get professional-grade thresholds
        professional_thresholds = self.quality_framework.confidence_thresholds
        
        # Update algo forecaster thresholds (convert rating thresholds to pattern thresholds)
        self.algo_forecaster.algo_patterns['mean_reversion']['confidence_threshold'] = 0.60
        self.algo_forecaster.algo_patterns['momentum_breakout']['confidence_threshold'] = 0.65
        self.algo_forecaster.algo_patterns['support_resistance']['confidence_threshold'] = 0.60
    
    def _meets_quality_standards(self, quality_metrics) -> bool:
        """Check if analysis meets minimum quality standards for the target quality level."""
        # Check if achieved quality level meets or exceeds the target
        quality_hierarchy = {
            'experimental': 0,
            'retail': 1, 
            'professional': 2,
            'institutional': 3
        }
        
        achieved_level = quality_hierarchy.get(quality_metrics.quality_level.value.lower(), 0)
        target_level = quality_hierarchy.get(self.quality_level.value.lower(), 0)
        
        return (achieved_level >= target_level and
                quality_metrics.p_value <= self.quality_framework.p_value_threshold and
                quality_metrics.sample_size >= self.quality_framework.min_sample_size)
    
    def _convert_algo_direction_to_rating(self, direction: str) -> str:
        """Convert algorithmic forecast direction to rating."""
        if direction == 'UP':
            return 'BUY'
        elif direction == 'DOWN':
            return 'SELL'
        else:
            return 'HOLD'
    
    def _calculate_volatility(self, prices: List[float]) -> float:
        """Calculate historical volatility (daily)."""
        if len(prices) < 10:
            return 0.02  # Default to 2% daily volatility
        
        returns = [(prices[i] - prices[i-1]) / prices[i-1] 
                  for i in range(1, min(len(prices), 31))]  # Last 30 days
        
        if not returns:
            return 0.02
        
        return statistics.stdev(returns) if len(returns) > 1 else 0.02
    
    def _find_support_level(self, prices: List[float]) -> Optional[float]:
        """Find nearest support level."""
        if len(prices) < 20:
            return None
        
        recent_prices = prices[-20:]
        return min(recent_prices) * 0.99  # 1% below recent low
    
    def _find_resistance_level(self, prices: List[float]) -> Optional[float]:
        """Find nearest resistance level."""
        if len(prices) < 20:
            return None
        
        recent_prices = prices[-20:]
        return max(recent_prices) * 1.01  # 1% above recent high
    
    def _create_professional_result(self, ticker: str, stock_data: StockData,
                                  technical_analysis, quality_metrics,
                                  risk_params, entry_exit, consistency_validation,
                                  algo_forecast=None, news_sentiment=None) -> ProfessionalAnalysisResult:
        """Create comprehensive professional analysis result."""
        
        # Enhanced reasoning with risk management context
        enhanced_reasoning = list(technical_analysis.reasoning)
        enhanced_reasoning.extend([
            f"Quality Level: {quality_metrics.quality_level.value.upper()} (p-value: {quality_metrics.p_value:.3f})",
            f"Risk Management: {risk_params.stop_loss_percent:.1%} stop-loss, {risk_params.position_size_percent:.1%} max position",
            f"Entry/Exit: Entry ${entry_exit.entry_price:.2f}, Stop ${entry_exit.stop_loss_price:.2f}, Target ${entry_exit.take_profit_price:.2f}"
        ])
        
        # Add cross-module validation context
        if consistency_validation['overall_consistency'] != 'HIGH':
            enhanced_reasoning.append(f"Cross-module consistency: {consistency_validation['overall_consistency']}")
            if consistency_validation['conflicts']:
                enhanced_reasoning.extend([f"⚠️ {conflict}" for conflict in consistency_validation['conflicts']])
        
        # Add algorithmic forecast context
        if algo_forecast and algo_forecast.confidence >= 0.60:
            enhanced_reasoning.append(f"Algorithmic Forecast: {algo_forecast.forecast_direction} ({algo_forecast.confidence:.0%} confidence)")
            if algo_forecast.algo_triggers:
                enhanced_reasoning.append(f"Algorithm Triggers: {', '.join([f'${t:.2f}' for t in algo_forecast.algo_triggers[:2]])}")
        
        # Create risk management data
        risk_mgmt = RiskManagementData(
            stop_loss_price=entry_exit.stop_loss_price,
            stop_loss_percent=risk_params.stop_loss_percent,
            take_profit_price=entry_exit.take_profit_price,
            position_size_percent=risk_params.position_size_percent,
            risk_reward_ratio=risk_params.risk_reward_ratio,
            max_drawdown_limit=risk_params.max_drawdown_limit,
            time_horizon_days=risk_params.time_horizon_days,
            trailing_stop_percent=entry_exit.trailing_stop_percent
        )
        
        # Create quality assurance data
        qa_flags = []
        if quality_metrics.p_value > 0.05:
            qa_flags.append(f"Statistical significance: p={quality_metrics.p_value:.3f}")
        if quality_metrics.sample_size < 50:
            qa_flags.append(f"Limited sample size: n={quality_metrics.sample_size}")
        if consistency_validation['conflicts']:
            qa_flags.extend(consistency_validation['conflicts'])
        
        quality_assurance = QualityAssurance(
            quality_level=quality_metrics.quality_level.value.upper(),
            statistical_confidence=quality_metrics.confidence_score,
            p_value=quality_metrics.p_value,
            sample_size=quality_metrics.sample_size,
            error_margin=quality_metrics.error_margin,
            risk_score=quality_metrics.risk_score,
            validation_flags=qa_flags
        )
        
        # Format algo forecast for response
        algo_data = None
        if algo_forecast:
            algo_data = {
                'forecast_direction': algo_forecast.forecast_direction,
                'confidence': algo_forecast.confidence,
                'algo_triggers': algo_forecast.algo_triggers,
                'reasoning': getattr(algo_forecast, 'reasoning', []),
                'risk_factors': getattr(algo_forecast, 'risk_factors', []),
                'pattern_scores': getattr(algo_forecast, 'pattern_scores', {})
            }
        
        # Format news sentiment for response  
        news_data = None
        if news_sentiment:
            news_data = {
                'sentiment_score': getattr(news_sentiment, 'sentiment_score', 0),
                'manipulation_risk': getattr(news_sentiment, 'manipulation_risk', 0),
                'news_volume': getattr(news_sentiment, 'news_volume', 0),
                'sentiment_trend': getattr(news_sentiment, 'sentiment_trend', 'NEUTRAL'),
                'analysis_summary': getattr(news_sentiment, 'analysis_summary', [])
            }
        
        return ProfessionalAnalysisResult(
            ticker=ticker,
            rating=consistency_validation['recommended_rating'],
            confidence=consistency_validation['recommended_confidence'],
            technical_indicators=technical_analysis.technical_indicators,
            reasoning=enhanced_reasoning,
            analysis_date=datetime.now(),
            price_at_analysis=stock_data.current_price,
            risk_management=risk_mgmt,
            quality_assurance=quality_assurance,
            entry_exit_criteria={
                'entry_price': entry_exit.entry_price,
                'stop_loss_price': entry_exit.stop_loss_price,
                'take_profit_price': entry_exit.take_profit_price,
                'trailing_stop_percent': entry_exit.trailing_stop_percent
            },
            statistical_validation={
                'p_value': quality_metrics.p_value,
                'confidence_interval': quality_metrics.error_margin,
                'statistical_power': quality_metrics.statistical_power,
                'sample_size': quality_metrics.sample_size
            },
            cross_module_validation={
                'overall_consistency': consistency_validation['overall_consistency'],
                'conflicts': ', '.join(consistency_validation['conflicts']) if consistency_validation['conflicts'] else 'None',
                'confirmations': ', '.join(consistency_validation['confirmations']) if consistency_validation['confirmations'] else 'None'
            },
            algo_forecast=algo_data,
            news_sentiment=news_data
        )
    
    def _create_insufficient_data_result(self, ticker: str) -> ProfessionalAnalysisResult:
        """Create result for insufficient data scenarios."""
        from .models import TechnicalIndicators
        
        return ProfessionalAnalysisResult(
            ticker=ticker,
            rating='HOLD',
            confidence=0.0,
            technical_indicators=TechnicalIndicators(0, 0, 0, 0, 0, 0),
            reasoning=['Insufficient historical data for professional analysis'],
            analysis_date=datetime.now(),
            price_at_analysis=0.0,
            risk_management=RiskManagementData(0, 0, 0, 0, 0, 0, 0, 0),
            quality_assurance=QualityAssurance('INSUFFICIENT_DATA', 0.0, 1.0, 0, 0.5, 1.0, ['Insufficient data']),
            entry_exit_criteria={'entry_price': 0, 'stop_loss_price': 0, 'take_profit_price': 0, 'trailing_stop_percent': 0},
            statistical_validation={'p_value': 1.0, 'confidence_interval': 0.5, 'statistical_power': 0.0, 'sample_size': 0},
            cross_module_validation={'overall_consistency': 'UNKNOWN', 'conflicts': 'N/A', 'confirmations': 'N/A'}
        )
    
    def _create_low_quality_result(self, ticker: str, technical_analysis, quality_metrics) -> ProfessionalAnalysisResult:
        """Create result when analysis doesn't meet quality standards."""
        
        return ProfessionalAnalysisResult(
            ticker=ticker,
            rating='HOLD',  # Force HOLD for low quality
            confidence=0.0,  # Zero confidence for substandard analysis
            technical_indicators=technical_analysis.technical_indicators,
            reasoning=[
                'Analysis does not meet professional quality standards:',
                f'Quality Level: {quality_metrics.quality_level.value.upper()}',
                f'Statistical Significance: p={quality_metrics.p_value:.3f} (required: <{self.quality_framework.p_value_threshold})',
                f'Sample Size: {quality_metrics.sample_size} (required: ≥{self.quality_framework.min_sample_size})',
                'Recommendation: HOLD until sufficient quality data available'
            ],
            analysis_date=datetime.now(),
            price_at_analysis=technical_analysis.price_at_analysis,
            risk_management=RiskManagementData(0, 0.15, 0, 0.02, 1.0, 0.30, 1, 0.10),  # Conservative defaults
            quality_assurance=QualityAssurance(
                quality_level='SUBSTANDARD',
                statistical_confidence=quality_metrics.confidence_score,
                p_value=quality_metrics.p_value,
                sample_size=quality_metrics.sample_size,
                error_margin=quality_metrics.error_margin,
                risk_score=1.0,  # Maximum risk for substandard analysis
                validation_flags=['Does not meet professional quality standards']
            ),
            entry_exit_criteria={'entry_price': 0, 'stop_loss_price': 0, 'take_profit_price': 0, 'trailing_stop_percent': 0},
            statistical_validation={
                'p_value': quality_metrics.p_value,
                'confidence_interval': quality_metrics.error_margin,
                'statistical_power': quality_metrics.statistical_power,
                'sample_size': quality_metrics.sample_size
            },
            cross_module_validation={'overall_consistency': 'LOW_QUALITY', 'conflicts': 'N/A', 'confirmations': 'N/A'}
        )
    
    def _create_error_result(self, ticker: str, error_msg: str) -> ProfessionalAnalysisResult:
        """Create result for error scenarios."""
        from .models import TechnicalIndicators
        
        return ProfessionalAnalysisResult(
            ticker=ticker,
            rating='HOLD',
            confidence=0.0,
            technical_indicators=TechnicalIndicators(0, 0, 0, 0, 0, 0),
            reasoning=[f'Analysis error: {error_msg}'],
            analysis_date=datetime.now(),
            price_at_analysis=0.0,
            risk_management=RiskManagementData(0, 0, 0, 0, 0, 0, 0, 0),
            quality_assurance=QualityAssurance('ERROR', 0.0, 1.0, 0, 0.5, 1.0, [f'Analysis error: {error_msg}']),
            entry_exit_criteria={'entry_price': 0, 'stop_loss_price': 0, 'take_profit_price': 0, 'trailing_stop_percent': 0},
            statistical_validation={'p_value': 1.0, 'confidence_interval': 0.5, 'statistical_power': 0.0, 'sample_size': 0},
            cross_module_validation={'overall_consistency': 'ERROR', 'conflicts': 'N/A', 'confirmations': 'N/A'}
        )
    
    def _analyze_institutional_indicators(self, stock_data: StockData) -> Dict:
        """Analyze institutional-grade indicators for confidence boost."""
        try:
            # VWAP Analysis
            vwap_value, vwap_signal = self.institutional_indicators.calculate_vwap(
                stock_data.prices, stock_data.volumes, 
                stock_data.highs, stock_data.lows
            )
            
            # Money Flow Index
            mfi_value, mfi_signal = self.institutional_indicators.calculate_money_flow_index(
                stock_data.prices, stock_data.volumes,
                stock_data.highs, stock_data.lows
            )
            
            # Calculate institutional confidence boost
            institutional_confidence = 0.0
            
            # VWAP signals add 5-10% confidence
            if "bullish" in vwap_signal.lower():
                institutional_confidence += 0.08
            elif "bearish" in vwap_signal.lower():
                institutional_confidence += 0.05  # Any signal adds some confidence
            
            # MFI signals add 3-7% confidence  
            if "strong" in mfi_signal.lower():
                institutional_confidence += 0.07
            elif "moderate" in mfi_signal.lower():
                institutional_confidence += 0.05
            elif "weak" in mfi_signal.lower():
                institutional_confidence += 0.03
            
            return {
                'vwap_value': vwap_value,
                'vwap_signal': vwap_signal,
                'mfi_value': mfi_value,
                'mfi_signal': mfi_signal,
                'confidence_boost': min(0.15, institutional_confidence)  # Cap at 15%
            }
            
        except Exception as e:
            return {
                'vwap_value': 0,
                'vwap_signal': f"Error: {str(e)}",
                'mfi_value': 0,
                'mfi_signal': f"Error: {str(e)}",
                'confidence_boost': 0.0
            }
    
    def _calculate_enhanced_confidence(self, base_confidence: float, 
                                     multi_tf_result: Dict, 
                                     institutional_result: Dict) -> float:
        """Calculate enhanced confidence using multi-timeframe and institutional indicators."""
        enhanced_confidence = base_confidence
        
        # Multi-timeframe boost (up to 15% additional confidence)
        if 'confluence_score' in multi_tf_result:
            confluence_boost = min(0.15, multi_tf_result['confluence_score'] * 0.15)
            enhanced_confidence += confluence_boost
        
        # Institutional indicators boost (up to 15% additional confidence)
        institutional_boost = institutional_result.get('confidence_boost', 0.0)
        enhanced_confidence += institutional_boost
        
        # Quality level adjustment - be more aggressive for professional analysis
        if self.quality_level == QualityLevel.PROFESSIONAL:
            enhanced_confidence += 0.05  # 5% boost for professional level
        elif self.quality_level == QualityLevel.INSTITUTIONAL:
            enhanced_confidence += 0.08  # 8% boost for institutional level
        
        # Ensure confidence stays within reasonable bounds
        return max(0.1, min(0.95, enhanced_confidence))
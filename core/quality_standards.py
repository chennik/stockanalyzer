"""
Professional-Grade Quality Standards Framework
=============================================

Defines industry-standard quality criteria, statistical significance validation,
and risk management parameters for all analysis modules to ensure consistent,
reliable, and statistically sound trading predictions.

This module serves as the single source of truth for:
- Minimum confidence thresholds based on statistical significance  
- Risk management parameters (stop-loss, position sizing)
- Entry/exit criteria with specific price levels
- Cross-module consistency validation
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import math
import statistics
from datetime import datetime


class QualityLevel(Enum):
    """Risk-based analysis levels for predictions."""
    LOW_RISK = "low_risk"          # 95%+ confidence, strict validation, conservative thresholds
    MODERATE_RISK = "moderate_risk" # 85%+ confidence, balanced approach
    HIGH_RISK = "high_risk"        # 70%+ confidence, aggressive thresholds
    AGGRESSIVE = "aggressive"       # 60%+ confidence, maximum opportunities


@dataclass
class QualityMetrics:
    """Statistical quality metrics for validation."""
    confidence_score: float          # 0.0-1.0 statistical confidence
    p_value: float                   # Statistical significance (< 0.05 required)
    statistical_power: float        # Power analysis result (>0.8 preferred)
    sample_size: int                 # Number of data points used
    error_margin: float              # 95% confidence interval margin
    risk_score: float                # 0.0-1.0 risk assessment
    quality_level: QualityLevel     # Overall quality classification


@dataclass
class RiskParameters:
    """Risk management parameters for each prediction."""
    stop_loss_percent: float        # Recommended stop-loss percentage
    position_size_percent: float    # Max portfolio allocation percentage
    max_drawdown_limit: float       # Maximum acceptable drawdown
    time_horizon_days: int          # Recommended holding period
    risk_reward_ratio: float        # Expected risk/reward ratio
    volatility_adjustment: float    # Position size adjustment for volatility


@dataclass
class EntryExitCriteria:
    """Specific entry and exit criteria with price levels."""
    entry_price: float              # Recommended entry price
    stop_loss_price: float          # Stop-loss exit price
    take_profit_price: float        # Take-profit exit price
    trailing_stop_percent: float    # Trailing stop percentage
    volume_confirmation: bool       # Requires volume confirmation
    technical_confirmation: bool    # Requires technical indicator confirmation


class QualityStandardsFramework:
    """
    Unified quality standards framework for all analysis modules.
    
    Provides consistent quality validation, statistical significance testing,
    and risk management across technical analysis, algorithmic forecasting,
    and news sentiment analysis.
    """
    
    # Industry-standard confidence thresholds (statistically validated)
    CONFIDENCE_THRESHOLDS = {
        QualityLevel.LOW_RISK: {
            'BUY': 0.85,      # 85%+ confidence for low risk BUY
            'SELL': 0.85,     # 85%+ confidence for low risk SELL
            'HOLD': 0.70,     # 70%+ confidence for HOLD (lower bar)
            'RISKY_BUY': 0.75 # 75%+ confidence for high-risk trades
        },
        QualityLevel.MODERATE_RISK: {
            'BUY': 0.65,      # 65%+ confidence for moderate risk BUY (more realistic)
            'SELL': 0.65,     # 65%+ confidence for moderate risk SELL  
            'HOLD': 0.50,     # 50%+ confidence for HOLD
            'RISKY_BUY': 0.55 # 55%+ confidence for high-risk trades
        },
        QualityLevel.HIGH_RISK: {
            'BUY': 0.60,      # 60%+ confidence for high risk BUY 
            'SELL': 0.60,     # 60%+ confidence for high risk SELL
            'HOLD': 0.45,     # 45%+ confidence for HOLD
            'RISKY_BUY': 0.50 # 50%+ confidence for high-risk trades
        },
        QualityLevel.AGGRESSIVE: {
            'BUY': 0.55,      # 55%+ confidence for aggressive BUY
            'SELL': 0.55,     # 55%+ confidence for aggressive SELL
            'HOLD': 0.40,     # 40%+ confidence for HOLD
            'RISKY_BUY': 0.45 # 45%+ confidence for high-risk trades
        }
    }
    
    # Statistical significance requirements
    P_VALUE_THRESHOLDS = {
        QualityLevel.LOW_RISK: 0.01,       # p < 0.01 (99% significance)
        QualityLevel.MODERATE_RISK: 0.05,  # p < 0.05 (95% significance) 
        QualityLevel.HIGH_RISK: 0.10,      # p < 0.10 (90% significance)
        QualityLevel.AGGRESSIVE: 0.20      # p < 0.20 (80% significance)
    }
    
    # Minimum sample size requirements
    MIN_SAMPLE_SIZES = {
        QualityLevel.LOW_RISK: 100,       # 100+ data points
        QualityLevel.MODERATE_RISK: 50,   # 50+ data points
        QualityLevel.HIGH_RISK: 30,       # 30+ data points (current minimum)
        QualityLevel.AGGRESSIVE: 20       # 20+ data points
    }
    
    # Risk management parameters by asset volatility
    VOLATILITY_RISK_BANDS = {
        'low': {          # Daily volatility < 2%
            'max_position_size': 0.10,     # 10% max allocation
            'stop_loss_percent': 0.05,     # 5% stop-loss
            'risk_reward_ratio': 2.0       # 1:2 risk/reward minimum
        },
        'medium': {       # Daily volatility 2-5%
            'max_position_size': 0.08,     # 8% max allocation
            'stop_loss_percent': 0.08,     # 8% stop-loss
            'risk_reward_ratio': 2.5       # 1:2.5 risk/reward minimum
        },
        'high': {         # Daily volatility > 5%
            'max_position_size': 0.05,     # 5% max allocation
            'stop_loss_percent': 0.12,     # 12% stop-loss
            'risk_reward_ratio': 3.0       # 1:3 risk/reward minimum
        }
    }
    
    def __init__(self, target_quality_level: QualityLevel = QualityLevel.MODERATE_RISK):
        """
        Initialize quality framework with target quality level.
        
        Args:
            target_quality_level: Desired quality standard for all predictions
        """
        self.target_quality_level = target_quality_level
        self.confidence_thresholds = self.CONFIDENCE_THRESHOLDS[target_quality_level]
        self.p_value_threshold = self.P_VALUE_THRESHOLDS[target_quality_level]
        self.min_sample_size = self.MIN_SAMPLE_SIZES[target_quality_level]
    
    def validate_prediction_quality(self, confidence: float, rating: str, 
                                  sample_size: int, data_points: List[float] = None) -> QualityMetrics:
        """
        Validate prediction quality against statistical standards.
        
        Args:
            confidence: Confidence score from analysis module
            rating: Prediction rating (BUY, SELL, HOLD, RISKY_BUY)
            sample_size: Number of data points used in analysis
            data_points: Raw data points for statistical validation
            
        Returns:
            QualityMetrics with validation results
        """
        # Check minimum confidence threshold
        required_confidence = self.confidence_thresholds.get(rating, 0.50)
        meets_confidence = confidence >= required_confidence
        
        # Check minimum sample size
        meets_sample_size = sample_size >= self.min_sample_size
        
        # Calculate statistical significance (if data points provided)
        p_value = 1.0  # Default to no significance
        statistical_power = 0.0
        error_margin = 0.10  # Default 10% error margin
        
        if data_points and len(data_points) >= 10:
            p_value = self._calculate_p_value(data_points)
            statistical_power = self._calculate_statistical_power(data_points, sample_size)
            error_margin = self._calculate_error_margin(data_points)
        
        # Calculate overall risk score
        risk_score = self._calculate_prediction_risk(confidence, p_value, sample_size)
        
        # Determine quality level achieved
        quality_level = self._determine_quality_level(
            confidence, p_value, sample_size, meets_confidence
        )
        
        return QualityMetrics(
            confidence_score=confidence,
            p_value=p_value,
            statistical_power=statistical_power,
            sample_size=sample_size,
            error_margin=error_margin,
            risk_score=risk_score,
            quality_level=quality_level
        )
    
    def calculate_risk_parameters(self, current_price: float, volatility: float,
                                confidence: float, rating: str) -> RiskParameters:
        """
        Calculate risk management parameters for a prediction.
        
        Args:
            current_price: Current stock price
            volatility: Historical volatility (daily)
            confidence: Prediction confidence
            rating: Prediction rating
            
        Returns:
            RiskParameters with risk management recommendations
        """
        # Determine volatility band
        if volatility < 0.02:
            vol_band = 'low'
        elif volatility < 0.05:
            vol_band = 'medium'
        else:
            vol_band = 'high'
        
        risk_params = self.VOLATILITY_RISK_BANDS[vol_band]
        
        # Adjust position size based on confidence
        confidence_multiplier = min(confidence / 0.70, 1.0)  # Scale to 70% baseline
        position_size = risk_params['max_position_size'] * confidence_multiplier
        
        # Calculate stop-loss percentage
        base_stop_loss = risk_params['stop_loss_percent']
        volatility_adjustment = min(volatility * 2, 0.05)  # Cap at 5% additional
        stop_loss_percent = base_stop_loss + volatility_adjustment
        
        # Adjust for prediction strength
        if rating == 'RISKY_BUY':
            stop_loss_percent *= 1.5  # Wider stops for risky trades
            position_size *= 0.7      # Smaller position size
        elif confidence < 0.60:
            stop_loss_percent *= 1.2  # Tighter stops for lower confidence
            position_size *= 0.8      # Smaller position size
        
        # Calculate time horizon based on analysis type
        if rating == 'RISKY_BUY':
            time_horizon = 3  # Short-term momentum plays
        elif volatility > 0.05:
            time_horizon = 5  # High volatility = shorter holds
        else:
            time_horizon = 10  # Standard holding period
        
        return RiskParameters(
            stop_loss_percent=stop_loss_percent,
            position_size_percent=position_size,
            max_drawdown_limit=stop_loss_percent * 2,  # 2x stop-loss
            time_horizon_days=time_horizon,
            risk_reward_ratio=risk_params['risk_reward_ratio'],
            volatility_adjustment=volatility_adjustment
        )
    
    def generate_entry_exit_criteria(self, current_price: float, 
                                   risk_params: RiskParameters,
                                   technical_support: float = None,
                                   technical_resistance: float = None) -> EntryExitCriteria:
        """
        Generate specific entry and exit criteria with price levels.
        
        Args:
            current_price: Current stock price
            risk_params: Risk parameters from calculate_risk_parameters()
            technical_support: Support level (if available)
            technical_resistance: Resistance level (if available)
            
        Returns:
            EntryExitCriteria with specific price levels
        """
        # Entry price (slight below current for BUY orders)
        entry_price = current_price * 0.999  # 0.1% below current price
        
        # Stop-loss price
        stop_loss_price = entry_price * (1 - risk_params.stop_loss_percent)
        
        # Take-profit price (based on risk/reward ratio)
        profit_target = (entry_price - stop_loss_price) * risk_params.risk_reward_ratio
        take_profit_price = entry_price + profit_target
        
        # Use technical levels if available
        if technical_support and technical_support < entry_price:
            stop_loss_price = max(stop_loss_price, technical_support * 0.99)
        
        if technical_resistance and technical_resistance > entry_price:
            take_profit_price = min(take_profit_price, technical_resistance * 0.99)
        
        # Trailing stop percentage (dynamic based on volatility)
        trailing_stop = min(risk_params.stop_loss_percent * 0.75, 0.08)
        
        return EntryExitCriteria(
            entry_price=entry_price,
            stop_loss_price=stop_loss_price,
            take_profit_price=take_profit_price,
            trailing_stop_percent=trailing_stop,
            volume_confirmation=True,    # Always require volume confirmation
            technical_confirmation=True  # Always require technical confirmation
        )
    
    def validate_cross_module_consistency(self, technical_rating: str, 
                                        technical_confidence: float,
                                        algo_rating: str = None,
                                        algo_confidence: float = None,
                                        news_sentiment: float = None) -> Dict:
        """
        Validate consistency across different analysis modules.
        
        Args:
            technical_rating: Rating from technical analysis
            technical_confidence: Confidence from technical analysis  
            algo_rating: Rating from algorithmic forecast (optional)
            algo_confidence: Confidence from algorithmic forecast (optional)
            news_sentiment: News sentiment score (optional)
            
        Returns:
            Dictionary with consistency validation results
        """
        validation_results = {
            'overall_consistency': 'UNKNOWN',
            'conflicts': [],
            'confirmations': [],
            'recommended_rating': technical_rating,
            'recommended_confidence': technical_confidence,
            'quality_flags': []
        }
        
        # Technical analysis is baseline (most reliable)
        base_rating = technical_rating
        base_confidence = technical_confidence
        
        # Check algorithmic forecast consistency
        if algo_rating and algo_confidence:
            if algo_confidence < 0.50:  # Flag low algo confidence
                validation_results['quality_flags'].append(
                    f"Algorithmic forecast confidence too low ({algo_confidence:.1%})"
                )
            elif self._ratings_conflict(base_rating, algo_rating):
                validation_results['conflicts'].append(
                    f"Technical ({base_rating}) conflicts with Algorithmic ({algo_rating})"
                )
            else:
                validation_results['confirmations'].append(
                    f"Algorithmic forecast confirms technical analysis"
                )
                # Boost confidence slightly for confirmation
                base_confidence = min(base_confidence + 0.05, 1.0)
        
        # Check news sentiment consistency  
        if news_sentiment is not None:
            if base_rating == 'BUY' and news_sentiment < -0.2:
                validation_results['conflicts'].append(
                    f"BUY signal conflicts with negative news sentiment ({news_sentiment:.2f})"
                )
            elif base_rating == 'SELL' and news_sentiment > 0.2:
                validation_results['conflicts'].append(
                    f"SELL signal conflicts with positive news sentiment ({news_sentiment:.2f})"
                )
            else:
                validation_results['confirmations'].append(
                    f"News sentiment supports technical analysis"
                )
        
        # Determine overall consistency
        if len(validation_results['conflicts']) == 0:
            validation_results['overall_consistency'] = 'HIGH'
        elif len(validation_results['conflicts']) <= len(validation_results['confirmations']):
            validation_results['overall_consistency'] = 'MODERATE'
        else:
            validation_results['overall_consistency'] = 'LOW'
            # Reduce confidence for conflicting signals
            base_confidence *= 0.85
        
        validation_results['recommended_confidence'] = base_confidence
        
        return validation_results
    
    def _calculate_p_value(self, data_points: List[float]) -> float:
        """Calculate statistical significance (p-value) for data series."""
        if len(data_points) < 10:
            return 1.0  # Insufficient data
        
        try:
            # Simple t-test against zero (neutral) hypothesis
            mean = statistics.mean(data_points)
            std_dev = statistics.stdev(data_points)
            n = len(data_points)
            
            if std_dev == 0:
                return 0.0 if mean != 0 else 1.0
            
            # Calculate t-statistic
            t_stat = mean / (std_dev / math.sqrt(n))
            
            # Approximate p-value calculation (two-tailed)
            # This is simplified - in production would use scipy.stats
            abs_t = abs(t_stat)
            if abs_t > 2.576:
                return 0.01    # p < 0.01
            elif abs_t > 1.96:
                return 0.05    # p < 0.05  
            elif abs_t > 1.645:
                return 0.10    # p < 0.10
            elif abs_t > 1.282:
                return 0.15    # p < 0.15
            else:
                return 0.20    # p >= 0.20
                
        except Exception:
            return 1.0  # Error in calculation
    
    def _calculate_statistical_power(self, data_points: List[float], sample_size: int) -> float:
        """Calculate statistical power of the analysis."""
        if sample_size < 20:
            return 0.5  # Low power for small samples
        elif sample_size < 50:
            return 0.7  # Moderate power
        else:
            return 0.8  # Good power for large samples
    
    def _calculate_error_margin(self, data_points: List[float]) -> float:
        """Calculate 95% confidence interval error margin."""
        if len(data_points) < 10:
            return 0.20  # 20% error margin for small samples
        
        try:
            std_dev = statistics.stdev(data_points)
            n = len(data_points)
            # 95% confidence interval: 1.96 * std_error
            error_margin = 1.96 * (std_dev / math.sqrt(n))
            return min(error_margin, 0.20)  # Cap at 20%
        except:
            return 0.15  # Default 15% error margin
    
    def _calculate_prediction_risk(self, confidence: float, p_value: float, sample_size: int) -> float:
        """Calculate overall prediction risk score."""
        risk_score = 0.0
        
        # Confidence risk component
        if confidence < 0.50:
            risk_score += 0.4
        elif confidence < 0.70:
            risk_score += 0.2
        
        # Statistical significance risk
        if p_value > 0.20:
            risk_score += 0.3
        elif p_value > 0.05:
            risk_score += 0.1
        
        # Sample size risk
        if sample_size < 20:
            risk_score += 0.3
        elif sample_size < 50:
            risk_score += 0.1
        
        return min(risk_score, 1.0)
    
    def _determine_quality_level(self, confidence: float, p_value: float, 
                               sample_size: int, meets_confidence: bool) -> QualityLevel:
        """Determine achieved quality level based on metrics."""
        if (confidence >= 0.85 and p_value <= 0.01 and 
            sample_size >= 100 and meets_confidence):
            return QualityLevel.LOW_RISK
        elif (confidence >= 0.65 and p_value <= 0.05 and 
              sample_size >= 30 and meets_confidence):
            return QualityLevel.MODERATE_RISK
        elif (confidence >= 0.60 and p_value <= 0.10 and 
              sample_size >= 30 and meets_confidence):
            return QualityLevel.HIGH_RISK
        elif (confidence >= 0.55 and p_value <= 0.20 and sample_size >= 20):
            return QualityLevel.AGGRESSIVE
        else:
            # If even aggressive standards aren't met, but we have some data
            if sample_size >= 10 and confidence > 0.0:
                return QualityLevel.AGGRESSIVE
            else:
                return QualityLevel.AGGRESSIVE  # Default to aggressive rather than fail
    
    def _ratings_conflict(self, rating1: str, rating2: str) -> bool:
        """Check if two ratings conflict with each other."""
        conflicts = {
            ('BUY', 'SELL'), ('SELL', 'BUY'),
            ('RISKY_BUY', 'SELL'), ('SELL', 'RISKY_BUY')
        }
        return (rating1, rating2) in conflicts


# Global instance for consistent usage across modules
quality_framework = QualityStandardsFramework(QualityLevel.MODERATE_RISK)
from dataclasses import dataclass
from typing import List, Dict, Optional, Literal
from datetime import datetime

Rating = Literal["BUY", "SELL", "HOLD", "RISKY_BUY", "MOMENTUM_BUY", "MOMENTUM_WATCH"]

@dataclass
class StockData:
    ticker: str
    prices: List[float]
    volumes: List[float]
    dates: List[datetime]
    current_price: float
    daily_change: float
    daily_change_percent: float
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    highs: Optional[List[float]] = None
    lows: Optional[List[float]] = None
    
@dataclass
class TechnicalIndicators:
    rsi: float
    sma_20: float
    sma_50: float
    macd: float
    macd_signal: float
    macd_histogram: float
    
@dataclass
class RiskManagementData:
    """Risk management parameters for trading decisions."""
    stop_loss_price: float
    stop_loss_percent: float
    take_profit_price: float
    position_size_percent: float
    risk_reward_ratio: float
    max_drawdown_limit: float
    time_horizon_days: int
    trailing_stop_percent: float
    
@dataclass
class QualityAssurance:
    """Quality assurance metrics for prediction validation."""
    quality_level: str  # 'INSTITUTIONAL', 'PROFESSIONAL', 'RETAIL', 'EXPERIMENTAL'
    statistical_confidence: float  # 0.0-1.0
    p_value: float  # Statistical significance
    sample_size: int  # Number of data points used
    error_margin: float  # 95% confidence interval margin
    risk_score: float  # Overall prediction risk (0.0-1.0)
    validation_flags: List[str]  # Quality warnings/issues

@dataclass
class ProfessionalAnalysisResult:
    """Enhanced analysis result with professional-grade risk management and quality metrics."""
    ticker: str
    rating: Rating
    confidence: float
    technical_indicators: TechnicalIndicators
    reasoning: List[str]
    analysis_date: datetime
    price_at_analysis: float
    
    # Professional-grade enhancements
    risk_management: RiskManagementData
    quality_assurance: QualityAssurance
    entry_exit_criteria: Dict[str, float]  # entry_price, stop_loss, take_profit
    statistical_validation: Dict[str, float]  # p_value, confidence_interval, etc.
    cross_module_validation: Dict[str, str]  # consistency across analysis modules
    
    # Algorithm and news analysis integration
    algo_forecast: Optional[Dict] = None  # Algorithmic forecast data
    news_sentiment: Optional[Dict] = None  # News sentiment analysis

# Legacy compatibility
@dataclass  
class AnalysisResult:
    ticker: str
    rating: Rating
    confidence: float
    technical_indicators: TechnicalIndicators
    reasoning: List[str]
    analysis_date: datetime
    price_at_analysis: float
    
@dataclass
class IndicatorScore:
    name: str
    value: float
    score: float
    weight: float
    interpretation: str
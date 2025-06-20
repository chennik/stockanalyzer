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
"""
News and market event detection for enhanced trading opportunities.
"""
import yfinance as yf
from typing import Dict, List, Optional
from datetime import datetime, timedelta

def detect_earnings_events(ticker: str) -> Dict:
    """Detect if earnings announcement is coming up soon."""
    try:
        stock = yf.Ticker(ticker)
        calendar = stock.calendar
        
        if calendar is not None and not calendar.empty:
            # Check if earnings are within next 7 days
            today = datetime.now().date()
            earnings_date = calendar.index[0].date() if hasattr(calendar.index[0], 'date') else None
            
            if earnings_date and (earnings_date - today).days <= 7:
                return {
                    "has_earnings": True,
                    "days_until": (earnings_date - today).days,
                    "earnings_date": earnings_date.isoformat()
                }
    except:
        pass
    
    return {"has_earnings": False, "days_until": None, "earnings_date": None}

def detect_volume_anomalies(volumes: List[float], threshold: float = 2.0) -> Dict:
    """Detect unusual volume spikes that might indicate news events."""
    if not volumes or len(volumes) < 5:
        return {"volume_anomaly": False, "volume_ratio": 1.0}
    
    recent_volume = volumes[-1]
    avg_volume = sum(volumes[-10:]) / min(10, len(volumes))
    
    volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1.0
    
    return {
        "volume_anomaly": volume_ratio >= threshold,
        "volume_ratio": volume_ratio,
        "volume_strength": "High" if volume_ratio > 3.0 else "Moderate" if volume_ratio > 1.5 else "Normal"
    }

def detect_price_gaps(prices: List[float], threshold: float = 0.03) -> Dict:
    """Detect significant price gaps that might indicate news events."""
    if not prices or len(prices) < 2:
        return {"has_gap": False, "gap_percent": 0.0}
    
    # Calculate gap from previous close
    gap_percent = abs((prices[-1] - prices[-2]) / prices[-2]) if prices[-2] != 0 else 0
    
    gap_type = "up" if prices[-1] > prices[-2] else "down"
    
    return {
        "has_gap": gap_percent >= threshold,
        "gap_percent": gap_percent * 100,
        "gap_direction": gap_type,
        "gap_strength": "Strong" if gap_percent > 0.05 else "Moderate" if gap_percent > 0.03 else "Weak"
    }

def calculate_news_sentiment_score(ticker: str, stock_data) -> float:
    """Calculate a news sentiment score based on multiple indicators."""
    try:
        # Get market indicators
        earnings_info = detect_earnings_events(ticker)
        volume_info = detect_volume_anomalies(stock_data.volumes if stock_data.volumes else [])
        gap_info = detect_price_gaps(stock_data.prices)
        
        score = 0.0
        
        # Earnings proximity boost
        if earnings_info["has_earnings"]:
            days_until = earnings_info["days_until"]
            if days_until <= 2:
                score += 0.5  # High volatility expected
            elif days_until <= 5:
                score += 0.3  # Moderate volatility expected
        
        # Volume anomaly scoring
        if volume_info["volume_anomaly"]:
            volume_ratio = volume_info["volume_ratio"]
            if volume_ratio > 3.0:
                score += 0.4
            elif volume_ratio > 1.5:
                score += 0.2
        
        # Price gap scoring
        if gap_info["has_gap"]:
            gap_percent = gap_info["gap_percent"]
            if gap_percent > 5.0:
                score += 0.4
            elif gap_percent > 3.0:
                score += 0.2
        
        # Recent volatility pattern (last 3 days)
        if len(stock_data.prices) >= 4:
            recent_volatility = 0
            for i in range(-3, 0):
                if i + 1 < len(stock_data.prices):
                    daily_change = abs((stock_data.prices[i] - stock_data.prices[i-1]) / stock_data.prices[i-1])
                    recent_volatility += daily_change
            
            avg_volatility = recent_volatility / 3
            if avg_volatility > 0.04:  # 4%+ average daily moves
                score += 0.3
        
        return min(score, 1.0)  # Cap at 1.0
    
    except Exception as e:
        print(f"Error calculating news sentiment for {ticker}: {str(e)}")
        return 0.0

def get_market_timing_factors() -> Dict:
    """Get current market timing factors that affect trading opportunities."""
    try:
        # Get current time info
        now = datetime.now()
        market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
        
        # Check if market is open
        is_market_hours = market_open <= now <= market_close and now.weekday() < 5
        
        # Check if it's power hour (last hour of trading)
        is_power_hour = market_close - timedelta(hours=1) <= now <= market_close and now.weekday() < 5
        
        # Check if it's opening hour (first hour of trading)
        is_opening_hour = market_open <= now <= market_open + timedelta(hours=1) and now.weekday() < 5
        
        return {
            "is_market_hours": is_market_hours,
            "is_power_hour": is_power_hour,
            "is_opening_hour": is_opening_hour,
            "market_factor": 1.2 if is_opening_hour or is_power_hour else 1.0 if is_market_hours else 0.8
        }
    except:
        return {
            "is_market_hours": False,
            "is_power_hour": False,
            "is_opening_hour": False,
            "market_factor": 0.8
        }
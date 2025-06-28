from typing import List, Tuple
import pandas as pd

def calculate_sma(prices: List[float], period: int) -> float:
    """Calculate Simple Moving Average for the given period."""
    if len(prices) < period:
        return prices[-1] if prices else 0.0
    return sum(prices[-period:]) / period

def calculate_rsi(prices: List[float], period: int = 14) -> float:
    """
    Calculate Relative Strength Index (RSI) using Wilder's Smoothed Moving Average.
    
    This implementation follows J. Welles Wilder Jr.'s original RSI formula from
    "New Concepts in Technical Trading Systems" (1978), ensuring compatibility
    with professional platforms like Bloomberg, Reuters, and TradingView.
    
    Args:
        prices: List of closing prices
        period: RSI period (default 14, industry standard)
        
    Returns:
        RSI value between 0 and 100
    """
    if len(prices) < period + 1:
        return 50.0
    
    # Calculate price changes
    price_changes = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    gains = [change if change > 0 else 0 for change in price_changes]
    losses = [-change if change < 0 else 0 for change in price_changes]
    
    # Initial simple moving average for first period (Wilder's method)
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    
    # Apply Wilder's smoothing for subsequent periods
    # Formula: newval = (prevval * (n-1) + newdata) / n
    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
    
    if avg_loss == 0:
        return 100.0
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(prices: List[float]) -> Tuple[float, float, float]:
    """Calculate MACD (Moving Average Convergence Divergence)."""
    if len(prices) < 26:
        return 0.0, 0.0, 0.0
    
    # Convert to pandas for easier EMA calculation
    df = pd.DataFrame({'price': prices})
    
    # Calculate EMAs
    ema_12 = df['price'].ewm(span=12, adjust=False).mean()
    ema_26 = df['price'].ewm(span=26, adjust=False).mean()
    
    # MACD line
    macd_line = ema_12 - ema_26
    
    # Signal line (9-day EMA of MACD)
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    
    # MACD histogram
    macd_histogram = macd_line - signal_line
    
    return (
        macd_line.iloc[-1],
        signal_line.iloc[-1],
        macd_histogram.iloc[-1]
    )

def identify_trend(prices: List[float], short_period: int = 20, long_period: int = 50) -> str:
    """Identify trend based on SMA crossover."""
    if len(prices) < long_period:
        return "NEUTRAL"
    
    sma_short = calculate_sma(prices, short_period)
    sma_long = calculate_sma(prices, long_period)
    current_price = prices[-1]
    
    if sma_short > sma_long and current_price > sma_short:
        return "BULLISH"
    elif sma_short < sma_long and current_price < sma_short:
        return "BEARISH"
    else:
        return "NEUTRAL"
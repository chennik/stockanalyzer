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

def calculate_mfi(prices: List[float], volumes: List[float], period: int = 14) -> float:
    """
    Calculate Money Flow Index (MFI) - combines price and volume momentum.
    
    MFI is a volume-weighted RSI that identifies overbought/oversold conditions
    by analyzing the relationship between price and volume flow.
    
    Args:
        prices: List of closing prices
        volumes: List of trading volumes
        period: MFI period (default 14)
        
    Returns:
        MFI value between 0 and 100
    """
    if len(prices) < period + 1 or len(volumes) < period + 1:
        return 50.0
    
    # Calculate typical prices (High + Low + Close) / 3
    # Since we only have closing prices, use close as typical price
    typical_prices = prices
    
    # Calculate raw money flow
    money_flows = []
    for i in range(1, len(typical_prices)):
        typical_price = typical_prices[i]
        prev_typical_price = typical_prices[i-1]
        volume = volumes[i] if i < len(volumes) else 0
        
        if typical_price > prev_typical_price:
            # Positive money flow
            money_flows.append(typical_price * volume)
        elif typical_price < prev_typical_price:
            # Negative money flow
            money_flows.append(-typical_price * volume)
        else:
            # No change
            money_flows.append(0)
    
    if len(money_flows) < period:
        return 50.0
    
    # Calculate positive and negative money flow sums
    positive_mf = sum(mf for mf in money_flows[-period:] if mf > 0)
    negative_mf = sum(-mf for mf in money_flows[-period:] if mf < 0)
    
    if negative_mf == 0:
        return 100.0
    
    money_ratio = positive_mf / negative_mf
    mfi = 100 - (100 / (1 + money_ratio))
    
    return mfi


def calculate_stochastic(highs: List[float], lows: List[float], closes: List[float], 
                        k_period: int = 14, d_period: int = 3) -> Tuple[float, float]:
    """
    Calculate Stochastic Oscillator %K and %D.
    
    The Stochastic Oscillator compares a security's closing price to its price range
    over a specific period, indicating momentum and potential reversal points.
    
    Args:
        highs: List of high prices
        lows: List of low prices  
        closes: List of closing prices
        k_period: Period for %K calculation (default 14)
        d_period: Period for %D smoothing (default 3)
        
    Returns:
        Tuple of (%K, %D) values between 0 and 100
    """
    if len(closes) < k_period or len(highs) < k_period or len(lows) < k_period:
        return 50.0, 50.0
    
    # Calculate %K values
    k_values = []
    for i in range(k_period - 1, len(closes)):
        period_high = max(highs[i-k_period+1:i+1])
        period_low = min(lows[i-k_period+1:i+1])
        current_close = closes[i]
        
        if period_high == period_low:
            k_percent = 50.0
        else:
            k_percent = 100 * (current_close - period_low) / (period_high - period_low)
        
        k_values.append(k_percent)
    
    if not k_values:
        return 50.0, 50.0
    
    # Current %K
    current_k = k_values[-1]
    
    # Calculate %D (Simple moving average of %K)
    if len(k_values) >= d_period:
        current_d = sum(k_values[-d_period:]) / d_period
    else:
        current_d = sum(k_values) / len(k_values)
    
    return current_k, current_d


def calculate_williams_r(highs: List[float], lows: List[float], closes: List[float], 
                        period: int = 14) -> float:
    """
    Calculate Williams %R momentum indicator.
    
    Williams %R is a momentum indicator that moves between 0 and -100,
    measuring overbought and oversold levels.
    
    Args:
        highs: List of high prices
        lows: List of low prices
        closes: List of closing prices
        period: Lookback period (default 14)
        
    Returns:
        Williams %R value between -100 and 0
    """
    if len(closes) < period or len(highs) < period or len(lows) < period:
        return -50.0
    
    # Get the highest high and lowest low for the period
    period_high = max(highs[-period:])
    period_low = min(lows[-period:])
    current_close = closes[-1]
    
    if period_high == period_low:
        return -50.0
    
    williams_r = -100 * (period_high - current_close) / (period_high - period_low)
    
    return williams_r


def calculate_bollinger_bands(prices: List[float], period: int = 20, std_dev: float = 2.0) -> Tuple[float, float, float]:
    """
    Calculate Bollinger Bands (Upper, Middle, Lower).
    
    Args:
        prices: List of closing prices
        period: Period for moving average (default 20)
        std_dev: Number of standard deviations (default 2.0)
        
    Returns:
        Tuple of (upper_band, middle_band, lower_band)
    """
    if len(prices) < period:
        current_price = prices[-1] if prices else 0
        return current_price, current_price, current_price
    
    # Calculate middle band (SMA)
    middle_band = calculate_sma(prices, period)
    
    # Calculate standard deviation
    recent_prices = prices[-period:]
    variance = sum((price - middle_band) ** 2 for price in recent_prices) / period
    std_deviation = variance ** 0.5
    
    # Calculate upper and lower bands
    upper_band = middle_band + (std_dev * std_deviation)
    lower_band = middle_band - (std_dev * std_deviation)
    
    return upper_band, middle_band, lower_band


def calculate_atr(highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> float:
    """
    Calculate Average True Range (ATR) for volatility measurement.
    
    Args:
        highs: List of high prices
        lows: List of low prices
        closes: List of closing prices
        period: ATR period (default 14)
        
    Returns:
        ATR value
    """
    if len(highs) < 2 or len(lows) < 2 or len(closes) < 2:
        return 0.0
    
    true_ranges = []
    
    for i in range(1, len(closes)):
        high = highs[i] if i < len(highs) else closes[i]
        low = lows[i] if i < len(lows) else closes[i]
        prev_close = closes[i-1]
        
        tr1 = high - low
        tr2 = abs(high - prev_close)
        tr3 = abs(low - prev_close)
        
        true_range = max(tr1, tr2, tr3)
        true_ranges.append(true_range)
    
    if len(true_ranges) < period:
        return sum(true_ranges) / len(true_ranges) if true_ranges else 0.0
    
    # Calculate ATR using simple moving average
    return sum(true_ranges[-period:]) / period


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
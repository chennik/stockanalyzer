#!/usr/bin/env python3
"""
Institutional Indicators Module - FREE professional-grade indicators
Implements key metrics that professional traders and institutions use.
"""

import numpy as np
from typing import List, Tuple, Dict, Optional
from datetime import datetime

class InstitutionalIndicators:
    """
    Calculates institutional-grade indicators using only price/volume data.
    All indicators are FREE and based on publicly available market data.
    """
    
    @staticmethod
    def calculate_vwap(prices: List[float], volumes: List[float], high: List[float] = None, 
                       low: List[float] = None) -> Tuple[float, str]:
        """
        Volume Weighted Average Price - Institution's average entry level.
        
        WHY institutions use it: Shows the fair value price where most volume traded.
        Institutions use VWAP as a benchmark for execution quality.
        """
        if len(prices) < 5 or len(volumes) < 5:
            return prices[-1], "Insufficient data for VWAP calculation"
        
        # Use typical price if high/low available, otherwise close price
        if high and low and len(high) == len(prices) and len(low) == len(prices):
            typical_prices = [(h + l + c) / 3 for h, l, c in zip(high, low, prices)]
        else:
            typical_prices = prices
        
        # Calculate VWAP over recent period (last 20 days)
        period = min(20, len(prices))
        recent_prices = typical_prices[-period:]
        recent_volumes = volumes[-period:]
        
        total_volume_price = sum(p * v for p, v in zip(recent_prices, recent_volumes))
        total_volume = sum(recent_volumes)
        
        if total_volume == 0:
            return prices[-1], "No volume data for VWAP"
        
        vwap = total_volume_price / total_volume
        current_price = prices[-1]
        
        # Generate institutional interpretation
        price_vs_vwap = (current_price - vwap) / vwap * 100
        
        if price_vs_vwap > 2:
            interpretation = f"Price {price_vs_vwap:+.1f}% above VWAP (${vwap:.2f}) - institutions may be selling into strength"
        elif price_vs_vwap < -2:
            interpretation = f"Price {price_vs_vwap:+.1f}% below VWAP (${vwap:.2f}) - institutions may be accumulating"
        else:
            interpretation = f"Price near VWAP (${vwap:.2f}) - balanced institutional interest"
        
        return vwap, interpretation
    
    @staticmethod
    def calculate_atr(high: List[float], low: List[float], close: List[float], 
                     period: int = 14) -> Tuple[float, str]:
        """
        Average True Range - Measures volatility for position sizing.
        
        WHY institutions use it: Determines appropriate position size based on volatility.
        Higher ATR = smaller positions, Lower ATR = larger positions.
        """
        if len(high) < period + 1 or len(low) < period + 1 or len(close) < period + 1:
            return 0.0, "Insufficient data for ATR calculation"
        
        true_ranges = []
        for i in range(1, len(close)):
            tr1 = high[i] - low[i]  # Current high - current low
            tr2 = abs(high[i] - close[i-1])  # Current high - previous close
            tr3 = abs(low[i] - close[i-1])   # Current low - previous close
            true_ranges.append(max(tr1, tr2, tr3))
        
        # Calculate ATR as average of true ranges
        if len(true_ranges) >= period:
            atr = sum(true_ranges[-period:]) / period
        else:
            atr = sum(true_ranges) / len(true_ranges)
        
        # Generate interpretation for position sizing
        current_price = close[-1]
        atr_percentage = (atr / current_price) * 100
        
        if atr_percentage > 3:
            interpretation = f"High volatility (ATR: {atr_percentage:.1f}%) - institutions use smaller positions"
        elif atr_percentage > 1.5:
            interpretation = f"Moderate volatility (ATR: {atr_percentage:.1f}%) - normal institutional position sizing"
        else:
            interpretation = f"Low volatility (ATR: {atr_percentage:.1f}%) - institutions may use larger positions"
        
        return atr, interpretation
    
    @staticmethod
    def calculate_obv(prices: List[float], volumes: List[float]) -> Tuple[float, str]:
        """
        On-Balance Volume - Tracks institutional accumulation/distribution.
        
        WHY institutions use it: Shows whether smart money is buying or selling.
        Rising OBV with rising price = institutional accumulation.
        """
        if len(prices) < 10 or len(volumes) < 10:
            return 0.0, "Insufficient data for OBV calculation"
        
        obv_values = [0]
        
        for i in range(1, len(prices)):
            if prices[i] > prices[i-1]:
                obv_values.append(obv_values[-1] + volumes[i])
            elif prices[i] < prices[i-1]:
                obv_values.append(obv_values[-1] - volumes[i])
            else:
                obv_values.append(obv_values[-1])
        
        current_obv = obv_values[-1]
        
        # Analyze OBV trend over last 10 periods
        if len(obv_values) >= 10:
            obv_10_ago = obv_values[-10]
            obv_trend = current_obv - obv_10_ago
            
            price_10_ago = prices[-10]
            price_trend = prices[-1] - price_10_ago
            
            # Check for divergence
            if obv_trend > 0 and price_trend > 0:
                interpretation = "OBV rising with price - institutional accumulation confirmed"
            elif obv_trend < 0 and price_trend < 0:
                interpretation = "OBV falling with price - institutional distribution confirmed"
            elif obv_trend > 0 and price_trend < 0:
                interpretation = "BULLISH DIVERGENCE: OBV rising while price falls - institutions accumulating"
            elif obv_trend < 0 and price_trend > 0:
                interpretation = "BEARISH DIVERGENCE: OBV falling while price rises - institutions distributing"
            else:
                interpretation = "OBV trend neutral - mixed institutional sentiment"
        else:
            interpretation = "OBV calculated - need more data for trend analysis"
        
        return current_obv, interpretation
    
    @staticmethod
    def calculate_bollinger_bands(prices: List[float], period: int = 20, 
                                std_dev: float = 2.0) -> Tuple[Dict, str]:
        """
        Bollinger Bands - Dynamic support/resistance levels.
        
        WHY institutions use it: Shows overbought/oversold conditions relative to volatility.
        Bands expand during high volatility, contract during low volatility.
        """
        if len(prices) < period:
            return {}, "Insufficient data for Bollinger Bands"
        
        # Calculate moving average
        sma = sum(prices[-period:]) / period
        
        # Calculate standard deviation
        variance = sum((price - sma) ** 2 for price in prices[-period:]) / period
        std = variance ** 0.5
        
        # Calculate bands
        upper_band = sma + (std_dev * std)
        lower_band = sma - (std_dev * std)
        
        current_price = prices[-1]
        
        # Calculate position within bands
        band_width = upper_band - lower_band
        position_in_bands = (current_price - lower_band) / band_width
        
        bands = {
            'upper': upper_band,
            'middle': sma,
            'lower': lower_band,
            'width': band_width,
            'position': position_in_bands
        }
        
        # Generate institutional interpretation
        if position_in_bands > 0.8:
            interpretation = f"Price near upper band (${upper_band:.2f}) - institutions may take profits"
        elif position_in_bands < 0.2:
            interpretation = f"Price near lower band (${lower_band:.2f}) - institutions may accumulate"
        elif 0.4 <= position_in_bands <= 0.6:
            interpretation = f"Price near middle band (${sma:.2f}) - neutral institutional sentiment"
        else:
            interpretation = f"Price within normal band range - balanced institutional activity"
        
        return bands, interpretation
    
    @staticmethod
    def calculate_relative_volume(volumes: List[float], period: int = 20) -> Tuple[float, str]:
        """
        Relative Volume - Compares current volume to average.
        
        WHY institutions use it: Unusual volume indicates institutional activity.
        Volume spikes often precede major price moves.
        """
        if len(volumes) < period + 1:
            return 1.0, "Insufficient volume data"
        
        current_volume = volumes[-1]
        avg_volume = sum(volumes[-period-1:-1]) / period  # Exclude current day
        
        if avg_volume == 0:
            return 1.0, "No historical volume data"
        
        relative_volume = current_volume / avg_volume
        
        # Generate institutional interpretation
        if relative_volume > 3.0:
            interpretation = f"Exceptional volume ({relative_volume:.1f}x average) - major institutional activity"
        elif relative_volume > 2.0:
            interpretation = f"High volume ({relative_volume:.1f}x average) - institutional interest detected"
        elif relative_volume > 1.5:
            interpretation = f"Above-average volume ({relative_volume:.1f}x) - moderate institutional activity"
        elif relative_volume < 0.5:
            interpretation = f"Low volume ({relative_volume:.1f}x average) - limited institutional interest"
        else:
            interpretation = f"Normal volume ({relative_volume:.1f}x average) - typical institutional activity"
        
        return relative_volume, interpretation
    
    @staticmethod
    def identify_support_resistance(prices: List[float], period: int = 50) -> Tuple[Dict, str]:
        """
        Support/Resistance Levels - Key psychological levels institutions watch.
        
        WHY institutions use it: These levels often hold due to institutional algorithms
        and psychological factors. Major buy/sell orders cluster around these levels.
        """
        if len(prices) < period:
            return {}, "Insufficient data for support/resistance"
        
        recent_prices = prices[-period:]
        current_price = prices[-1]
        
        # Find recent highs and lows
        highs = []
        lows = []
        
        for i in range(2, len(recent_prices) - 2):
            # Local high: price higher than surrounding 2 periods
            if (recent_prices[i] > recent_prices[i-1] and recent_prices[i] > recent_prices[i-2] and
                recent_prices[i] > recent_prices[i+1] and recent_prices[i] > recent_prices[i+2]):
                highs.append(recent_prices[i])
            
            # Local low: price lower than surrounding 2 periods  
            if (recent_prices[i] < recent_prices[i-1] and recent_prices[i] < recent_prices[i-2] and
                recent_prices[i] < recent_prices[i+1] and recent_prices[i] < recent_prices[i+2]):
                lows.append(recent_prices[i])
        
        # Find strongest levels (most tests)
        resistance = max(highs) if highs else current_price * 1.05
        support = min(lows) if lows else current_price * 0.95
        
        levels = {
            'resistance': resistance,
            'support': support,
            'distance_to_resistance': (resistance - current_price) / current_price * 100,
            'distance_to_support': (current_price - support) / current_price * 100
        }
        
        # Generate institutional interpretation
        if levels['distance_to_resistance'] < 2:
            interpretation = f"Near resistance (${resistance:.2f}) - institutions may sell"
        elif levels['distance_to_support'] < 2:
            interpretation = f"Near support (${support:.2f}) - institutions may buy"
        else:
            interpretation = f"Between support (${support:.2f}) and resistance (${resistance:.2f})"
        
        return levels, interpretation


def calculate_institutional_score(stock_data, vwap_data: Dict, atr_data: Dict, 
                                obv_data: Dict, bollinger_data: Dict) -> Tuple[float, List[str]]:
    """
    Calculate composite institutional sentiment score.
    
    Returns:
        Score (0-1) and list of institutional insights
    """
    score = 0.5  # Neutral baseline
    insights = []
    
    current_price = stock_data.current_price
    
    # VWAP analysis (20% weight)
    if 'vwap' in vwap_data:
        vwap = vwap_data['vwap']
        price_vs_vwap = (current_price - vwap) / vwap
        
        if price_vs_vwap > 0.02:  # 2% above VWAP
            score -= 0.1  # Institutions may be selling
        elif price_vs_vwap < -0.02:  # 2% below VWAP
            score += 0.1  # Institutions may be buying
    
    # Bollinger Bands analysis (15% weight)
    if bollinger_data and 'position' in bollinger_data:
        position = bollinger_data['position']
        
        if position > 0.8:  # Near upper band
            score -= 0.075
        elif position < 0.2:  # Near lower band
            score += 0.075
    
    # Volume analysis (15% weight)
    if len(stock_data.volumes) > 1:
        from .institutional_indicators import InstitutionalIndicators
        rel_vol, _ = InstitutionalIndicators.calculate_relative_volume(stock_data.volumes)
        
        if rel_vol > 2.0:  # High volume
            score += 0.05  # Institutional interest
        elif rel_vol < 0.5:  # Low volume
            score -= 0.03  # Limited institutional interest
    
    return max(0.1, min(0.9, score)), insights
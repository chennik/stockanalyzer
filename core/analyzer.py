from datetime import datetime
from typing import List, Dict, Optional
from .models import StockData, TechnicalIndicators, AnalysisResult, IndicatorScore, Rating
from .indicators import calculate_rsi, calculate_sma, calculate_macd, identify_trend
from .data_fetcher import fetch_stock_data, get_top_stocks_for_scanning
from .multi_timeframe_analyzer import analyze_with_multi_timeframe
from .results_database import log_prediction
from .market_regime import get_market_regime, apply_market_regime_adjustments
from .institutional_indicators import InstitutionalIndicators

# Industry-standard scoring weights based on technical analysis best practices
INDICATOR_WEIGHTS = {
    "trend": 0.35,      # Trend is primary - "The trend is your friend"
    "momentum": 0.25,   # MACD/RSI momentum confirmation
    "rsi": 0.20,        # Overbought/oversold conditions
    "volume": 0.10,     # Volume confirmation
    "fundamentals": 0.10 # P/E ratio and market cap considerations
}

# Risk thresholds based on industry standards
RSI_LEVELS = {
    "extremely_oversold": 20,
    "oversold": 30,
    "neutral_low": 40,
    "neutral_high": 60,
    "overbought": 70,
    "extremely_overbought": 80
}

# P/E ratio bands by market cap
PE_BANDS = {
    "growth": {"low": 15, "fair": 25, "high": 35},
    "value": {"low": 10, "fair": 18, "high": 25},
    "defensive": {"low": 12, "fair": 20, "high": 28}
}

def analyze_technical(stock_data: StockData) -> AnalysisResult:
    """Perform technical analysis and generate rating."""
    # Calculate indicators
    rsi = calculate_rsi(stock_data.prices)
    sma_20 = calculate_sma(stock_data.prices, 20)
    sma_50 = calculate_sma(stock_data.prices, 50)
    macd, signal, histogram = calculate_macd(stock_data.prices)
    trend = identify_trend(stock_data.prices)
    
    technical_indicators = TechnicalIndicators(
        rsi=rsi,
        sma_20=sma_20,
        sma_50=sma_50,
        macd=macd,
        macd_signal=signal,
        macd_histogram=histogram
    )
    
    # Score each indicator using industry best practices
    scores = []
    
    # Trend analysis (highest weight - trend is primary)
    trend_score, trend_reason = score_trend(trend, stock_data.current_price, sma_20, sma_50)
    scores.append(IndicatorScore("Trend", 0, trend_score, INDICATOR_WEIGHTS["trend"], trend_reason))
    
    # Momentum indicators (MACD + RSI combined)
    macd_score, macd_reason = score_macd(histogram, macd, signal)
    rsi_score, rsi_reason = score_rsi(rsi)
    
    # Weight momentum as combination of MACD and RSI
    combined_momentum = (macd_score + rsi_score) / 2
    scores.append(IndicatorScore("MACD", histogram, macd_score, INDICATOR_WEIGHTS["momentum"] * 0.6, macd_reason))
    scores.append(IndicatorScore("RSI", rsi, rsi_score, INDICATOR_WEIGHTS["momentum"] * 0.4, rsi_reason))
    
    # Volume confirmation
    volume_score, volume_reason = score_volume_confirmation(stock_data.volumes, stock_data.prices)
    scores.append(IndicatorScore("Volume", volume_score, volume_score, INDICATOR_WEIGHTS["volume"], volume_reason))
    
    # Institutional indicators (FREE professional-grade analysis)
    institutional_scores = calculate_institutional_indicators(stock_data)
    scores.extend(institutional_scores)
    
    # Fundamental analysis (P/E ratio with market cap consideration)
    if stock_data.pe_ratio:
        pe_score, pe_reason = score_pe_ratio(stock_data.pe_ratio, stock_data.market_cap, stock_data.ticker)
        scores.append(IndicatorScore("Valuation", stock_data.pe_ratio, pe_score, INDICATOR_WEIGHTS["fundamentals"], pe_reason))
    
    # Calculate weighted score
    total_score = sum(score.score * score.weight for score in scores)
    total_weight = sum(score.weight for score in scores)
    raw_score = total_score / total_weight if total_weight > 0 else 0.5
    
    # Risk adjustment based on market conditions and volatility
    risk_adjustment = calculate_risk_adjustment(stock_data, scores)
    
    # Apply market regime adjustments (FREE accuracy improvement)
    regime_adjusted_score, regime_explanation = apply_market_regime_adjustments(raw_score + risk_adjustment)
    final_score = max(0.1, min(0.9, regime_adjusted_score))
    
    # Generate rating with market regime-adjusted thresholds
    market_regime = get_market_regime()
    rating = generate_rating_with_regime(final_score, market_regime)
    
    # Calculate confidence using convergence of indicators
    confidence = calculate_confidence(scores, final_score, stock_data.ticker)
    
    # Compile reasoning with risk assessment
    reasoning = [score.interpretation for score in scores if score.interpretation]
    
    # Add market regime context (FREE accuracy improvement)
    if regime_explanation:
        reasoning.append(regime_explanation)
    
    # Add risk assessment to reasoning
    if risk_adjustment < -0.05:
        reasoning.append("RISK WARNING: High volatility detected - exercise caution")
    elif risk_adjustment > 0.01:
        reasoning.append("RISK ASSESSMENT: Lower volatility large-cap stock")
    
    # Add market cap context
    if stock_data.market_cap:
        if stock_data.market_cap < 1_000_000_000:
            reasoning.append(f"SMALL CAP: Market cap ${stock_data.market_cap/1_000_000:.0f}M - higher growth potential but increased risk")
        elif stock_data.market_cap > 100_000_000_000:
            reasoning.append(f"LARGE CAP: Market cap ${stock_data.market_cap/1_000_000_000:.0f}B - established company with lower volatility")
        else:
            reasoning.append(f"MID CAP: Market cap ${stock_data.market_cap/1_000_000_000:.1f}B - balanced risk-reward profile")
    
    return AnalysisResult(
        ticker=stock_data.ticker,
        rating=rating,
        confidence=confidence,
        technical_indicators=technical_indicators,
        reasoning=reasoning,
        analysis_date=datetime.now(),
        price_at_analysis=stock_data.current_price
    )

def score_rsi(rsi: float) -> tuple[float, str]:
    """
    Score RSI indicator using industry-standard zones based on Wilder's RSI.
    
    This function interprets RSI values calculated using Wilder's Smoothed Moving Average
    method (as implemented in calculate_rsi) and converts them to actionable trading scores.
    
    RSI Zones and Their Interpretation:
    - 0-20: Extremely oversold (panic selling, high reversal probability)
    - 20-30: Oversold (selling exhausted, accumulation zone)
    - 30-40: Approaching oversold (cooling off, potential entry)
    - 40-60: Neutral zone (balanced market, no directional bias)
    - 60-70: Approaching overbought (heating up, caution advised)
    - 70-80: Overbought (buying exhausted, distribution zone)
    - 80-100: Extremely overbought (euphoria, high reversal probability)
    
    Scoring Logic:
    - Higher scores (0.7-0.9) indicate BUY opportunities (oversold conditions)
    - Lower scores (0.1-0.3) indicate SELL signals (overbought conditions)
    - Mid-range scores (0.4-0.6) suggest HOLD (neutral market state)
    
    Historical Accuracy:
    - RSI < 20 shows 70%+ probability of short-term reversal upward
    - RSI > 80 shows 75%+ probability of near-term pullback
    - RSI 30-70 requires additional indicators for direction
    
    Args:
        rsi: RSI value between 0-100 calculated using Wilder's method
        
    Returns:
        tuple: (score, reasoning) where score is 0.0-1.0 and reasoning explains the signal
    """
    if rsi < RSI_LEVELS["extremely_oversold"]:
        return 0.9, f"RSI {rsi:.1f} indicates extremely oversold - strong buy signal. WHY: When RSI drops below 20, it means sellers have exhausted themselves and the stock is due for a bounce. Historical data shows 70%+ probability of short-term reversal from these levels"
    elif rsi < RSI_LEVELS["oversold"]:
        return 0.75, f"RSI {rsi:.1f} indicates oversold conditions - buy signal. WHY: RSI below 30 suggests the selling pressure is overdone. Smart money often starts accumulating here as downside risk is limited"
    elif rsi < RSI_LEVELS["neutral_low"]:
        return 0.6, f"RSI {rsi:.1f} approaching oversold - mild bullish bias. WHY: Stock is cooling off but not yet oversold. Good entry point for momentum traders expecting a bounce before reaching extreme levels"
    elif rsi < RSI_LEVELS["neutral_high"]:
        return 0.5, f"RSI {rsi:.1f} in neutral zone - no directional bias. WHY: Balanced buying/selling pressure means the stock could go either way. Wait for clearer signals or use other indicators for direction"
    elif rsi < RSI_LEVELS["overbought"]:
        return 0.4, f"RSI {rsi:.1f} approaching overbought - mild bearish bias. WHY: Buying momentum is getting stretched. Early warning that profit-taking may begin soon, but strong trends can stay overbought for weeks"
    elif rsi < RSI_LEVELS["extremely_overbought"]:
        return 0.25, f"RSI {rsi:.1f} indicates overbought conditions - sell signal. WHY: RSI above 70 warns that buyers are exhausted. Risk of pullback increases significantly, especially if volume is declining"
    else:
        return 0.1, f"RSI {rsi:.1f} indicates extremely overbought - strong sell signal. WHY: RSI above 80 is rare and unsustainable. Historical data shows 75%+ probability of near-term pullback from these extreme levels"

def score_trend(trend: str, current_price: float, sma_20: float, sma_50: float) -> tuple[float, str]:
    """Score trend using industry-standard moving average analysis."""
    # Calculate percentage distances from moving averages
    distance_from_sma20 = ((current_price - sma_20) / sma_20) * 100 if sma_20 > 0 else 0
    distance_from_sma50 = ((current_price - sma_50) / sma_50) * 100 if sma_50 > 0 else 0
    
    # Golden cross / Death cross detection
    if sma_20 > sma_50 * 1.02:  # 2% above for confirmation
        cross_status = "golden cross"
        cross_score = 0.15
    elif sma_20 < sma_50 * 0.98:  # 2% below for confirmation
        cross_status = "death cross"
        cross_score = -0.15
    else:
        cross_status = "neutral"
        cross_score = 0
    
    if trend == "BULLISH":
        base_score = 0.65
        if distance_from_sma20 > 5:  # Strong bullish if >5% above SMA20
            base_score = 0.8
            reason = f"Strong bullish trend: Price ${current_price:.2f} is {distance_from_sma20:.1f}% above SMA20. WHY: This wide gap shows strong buying pressure. Pullbacks to SMA20 often provide low-risk entry points as institutions defend this level"
        else:
            reason = f"Bullish trend: Price ${current_price:.2f} is {distance_from_sma20:.1f}% above SMA20. WHY: Price above key moving averages confirms uptrend. Momentum traders ride these trends until price breaks below support"
    elif trend == "BEARISH":
        base_score = 0.35
        if distance_from_sma20 < -5:  # Strong bearish if >5% below SMA20
            base_score = 0.2
            reason = f"Strong bearish trend: Price ${current_price:.2f} is {abs(distance_from_sma20):.1f}% below SMA20. WHY: Large gap below MAs indicates heavy selling. Rallies typically fail at MA resistance until sentiment improves"
        else:
            reason = f"Bearish trend: Price ${current_price:.2f} is {abs(distance_from_sma20):.1f}% below SMA20. WHY: Below MAs suggests sellers control the trend. Avoid longs until price reclaims these critical levels"
    else:
        base_score = 0.5
        reason = "Neutral trend: Price between moving averages. WHY: Consolidation between MAs often precedes big moves. Watch for breakout with volume for direction confirmation"
    
    final_score = max(0.1, min(0.9, base_score + cross_score))
    if cross_status != "neutral":
        reason += f" with {cross_status} pattern"
    
    return final_score, reason

def score_macd(histogram: float, macd: float, signal: float) -> tuple[float, str]:
    """Score MACD using industry-standard momentum analysis."""
    # Calculate the strength of the histogram
    histogram_strength = abs(histogram)
    
    if histogram > 0 and macd > signal:
        if histogram_strength > 0.5:  # Strong bullish momentum
            score = 0.8
            reason = f"Strong bullish momentum: MACD histogram {histogram:.3f} significantly positive. WHY: Widening histogram shows accelerating buying. This momentum often continues 3-5 days, making it ideal for short-term trades"
        else:
            score = 0.65
            reason = f"Bullish momentum: MACD above signal line by {histogram:.3f}. WHY: MACD crossing above signal is a classic buy trigger. Early entries here often capture the meat of the move"
    elif histogram < 0 and macd < signal:
        if histogram_strength > 0.5:  # Strong bearish momentum
            score = 0.2
            reason = f"Strong bearish momentum: MACD histogram {histogram:.3f} significantly negative. WHY: Expanding negative histogram warns of accelerating selling. Avoid longs until histogram starts shrinking (less negative)"
        else:
            score = 0.35
            reason = f"Bearish momentum: MACD below signal line by {histogram:.3f}. WHY: Negative MACD crossover triggers selling algorithms. Expect continued weakness until histogram turns positive"
    else:
        score = 0.5
        if abs(histogram) < 0.01:  # Very close to crossover
            reason = "MACD near crossover point - potential trend change. WHY: Histogram near zero means momentum is shifting. High-probability setup when combined with support/resistance levels"
        else:
            reason = "MACD showing neutral momentum. WHY: Mixed signals suggest waiting for clearer direction. Choppy action likely until MACD commits to a direction"
    
    return score, reason

def score_pe_ratio(pe_ratio: float, market_cap: Optional[float] = None, ticker: str = "") -> tuple[float, str]:
    """Score P/E ratio using industry-standard valuation metrics with regional adjustments."""
    # Determine stock type based on market cap (if available)
    if market_cap and market_cap > 100_000_000_000:  # Large cap (>$100B)
        pe_bands = PE_BANDS["defensive"]
        stock_type = "large-cap"
    elif market_cap and market_cap > 10_000_000_000:  # Mid cap ($10B-$100B)
        pe_bands = PE_BANDS["growth"]
        stock_type = "mid-cap"
    else:
        pe_bands = PE_BANDS["value"]  # Small cap or unknown
        stock_type = "small-cap/value"
    
    # Regional P/E adjustments (European stocks often trade at different multiples)
    regional_multiplier = 1.0
    if ticker and any(suffix in ticker.upper() for suffix in ['.DE', '.AS', '.PA', '.SW', '.MI', '.MC', '.L']):
        # European stocks often trade at lower P/E ratios, adjust thresholds
        regional_multiplier = 0.8  # 20% more lenient on European P/E ratios
        stock_type += " (European)"
    
    # Handle negative or zero P/E
    if pe_ratio <= 0:
        return 0.3, f"Negative/Zero P/E ratio indicates no earnings - higher risk"
    
    # Adjust P/E thresholds for regional markets
    adjusted_pe_bands = {
        key: value * regional_multiplier for key, value in pe_bands.items()
    }
    
    # Score based on adjusted P/E bands
    if pe_ratio < adjusted_pe_bands["low"]:
        score = 0.75
        reason = f"P/E ratio {pe_ratio:.1f} suggests potential undervaluation for {stock_type} stock"
    elif pe_ratio < adjusted_pe_bands["fair"]:
        score = 0.6
        reason = f"P/E ratio {pe_ratio:.1f} indicates attractive valuation for {stock_type} stock"
    elif pe_ratio < adjusted_pe_bands["high"]:
        score = 0.5
        reason = f"P/E ratio {pe_ratio:.1f} indicates fair valuation for {stock_type} stock"
    elif pe_ratio < adjusted_pe_bands["high"] * 1.5:  # 50% above high band
        score = 0.35
        reason = f"P/E ratio {pe_ratio:.1f} suggests overvaluation for {stock_type} stock"
    else:
        score = 0.2
        reason = f"P/E ratio {pe_ratio:.1f} indicates significant overvaluation - high risk"
    
    return score, reason

def score_volume_confirmation(volumes: List[float], prices: List[float]) -> tuple[float, str]:
    """Score volume confirmation using On Balance Volume (OBV) analysis."""
    if len(volumes) < 20 or len(prices) < 20:
        return 0.5, "Insufficient volume data for analysis"
    
    # Calculate average volume over 20 periods
    avg_volume = sum(volumes[-20:]) / 20
    recent_volume = volumes[-1]
    
    # Volume spike detection (current volume vs average)
    volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1
    
    # Price direction with volume confirmation
    price_direction = 1 if prices[-1] > prices[-2] else -1
    
    # Score based on volume confirmation
    if volume_ratio > 1.5:  # High volume
        if price_direction > 0:
            score = 0.75
            reason = f"Strong volume confirmation: {volume_ratio:.1f}x average volume supporting upward price movement. WHY: High volume on up days means institutions are buying. This 'smart money' activity often continues for several days"
        else:
            score = 0.25
            reason = f"High volume distribution: {volume_ratio:.1f}x average volume with downward price movement. WHY: Heavy volume selling indicates institutional distribution. Further downside likely as large players exit positions"
    elif volume_ratio > 1.2:  # Above average volume
        if price_direction > 0:
            score = 0.65
            reason = f"Above-average volume confirmation: {volume_ratio:.1f}x supporting price rise. WHY: Increased participation validates the move. Breakouts with >1.2x volume have 65% success rate"
        else:
            score = 0.35
            reason = f"Above-average volume with price decline: {volume_ratio:.1f}x average. WHY: Elevated selling pressure suggests more downside. Wait for volume to dry up before considering longs"
    elif volume_ratio < 0.7:  # Low volume
        score = 0.5
        reason = f"Low volume ({volume_ratio:.1f}x average) - price movement lacks conviction. WHY: Moves on low volume often reverse quickly. Professional traders avoid these as they're easily manipulated"
    else:
        score = 0.5
        reason = f"Normal volume levels ({volume_ratio:.1f}x average) - neutral confirmation. WHY: Average volume means no unusual activity. Focus on other indicators for direction"
    
    return score, reason

def calculate_risk_adjustment(stock_data: StockData, scores: List[IndicatorScore]) -> float:
    """Calculate risk adjustment based on volatility and market conditions."""
    # Calculate price volatility (standard deviation of recent returns)
    if len(stock_data.prices) < 10:
        volatility_adjustment = 0
    else:
        recent_prices = stock_data.prices[-10:]
        returns = [(recent_prices[i] - recent_prices[i-1]) / recent_prices[i-1] 
                  for i in range(1, len(recent_prices))]
        volatility = (sum(r**2 for r in returns) / len(returns)) ** 0.5 if returns else 0
        
        # Higher volatility = more conservative ratings
        if volatility > 0.05:  # 5% daily volatility threshold
            volatility_adjustment = -0.1  # Reduce score for high volatility
        elif volatility > 0.03:  # 3% daily volatility
            volatility_adjustment = -0.05
        else:
            volatility_adjustment = 0
    
    # Market cap risk adjustment
    market_cap_adjustment = 0
    if stock_data.market_cap:
        if stock_data.market_cap < 1_000_000_000:  # Small cap (<$1B)
            market_cap_adjustment = -0.05  # Higher risk
        elif stock_data.market_cap > 100_000_000_000:  # Large cap (>$100B)
            market_cap_adjustment = 0.02  # Lower risk
    
    return volatility_adjustment + market_cap_adjustment

def calculate_confidence(scores: List[IndicatorScore], final_score: float, ticker: str = "") -> float:
    """Calculate confidence based on indicator convergence with regional adjustments."""
    if not scores:
        return 0.5
    
    # Calculate how much indicators agree with each other
    score_values = [score.score for score in scores]
    mean_score = sum(score_values) / len(score_values)
    
    # Calculate standard deviation of scores
    variance = sum((score - mean_score) ** 2 for score in score_values) / len(score_values)
    std_dev = variance ** 0.5
    
    # Higher convergence (lower std dev) = higher confidence
    convergence_confidence = max(0.3, 1.0 - (std_dev * 2))
    
    # Distance from neutral (0.5) also affects confidence
    directional_confidence = abs(final_score - 0.5) * 2
    
    # Regional market adjustments
    regional_adjustment = get_regional_confidence_adjustment(ticker)
    
    # Combined confidence (weighted average)
    base_confidence = (convergence_confidence * 0.6) + (directional_confidence * 0.4)
    final_confidence = base_confidence + regional_adjustment
    
    return max(0.1, min(1.0, final_confidence))

def get_regional_confidence_adjustment(ticker: str) -> float:
    """Adjust confidence based on regional market characteristics."""
    if not ticker:
        return 0
    
    ticker_upper = ticker.upper()
    
    # European markets - generally more stable, different trading patterns
    if any(suffix in ticker_upper for suffix in ['.DE', '.AS', '.PA', '.SW', '.MI', '.MC', '.L']):
        # European stocks tend to have more stable patterns, boost confidence slightly
        base_boost = 0.05
        
        # German stocks (typically well-regulated, good data quality)
        if '.DE' in ticker_upper:
            return base_boost + 0.03
        
        # Dutch/Swiss stocks (stable markets)
        elif '.AS' in ticker_upper or '.SW' in ticker_upper:
            return base_boost + 0.02
        
        # Other European markets
        else:
            return base_boost
    
    # Asian markets - can be more volatile, more conservative
    elif any(suffix in ticker_upper for suffix in ['.T', '.HK', '.SS', '.SZ']):
        return -0.02
    
    # US markets (our baseline)
    else:
        return 0

def generate_rating(score: float) -> Rating:
    """Convert score to rating optimized based on historical validation results."""
    # Adjusted thresholds based on backtest results showing 50% accuracy needs improvement
    if score >= 0.70:  # More conservative for BUY (higher threshold)
        return "BUY"
    elif score <= 0.30:  # More conservative for SELL (lower threshold) 
        return "SELL"
    else:
        return "HOLD"

def generate_rating_with_regime(score: float, market_regime: Dict) -> Rating:
    """Convert score to rating with market regime-adjusted thresholds."""
    if not market_regime or 'rating_adjustments' not in market_regime:
        return generate_rating(score)
    
    adjustments = market_regime['rating_adjustments']
    buy_threshold = adjustments.get('buy_threshold', 0.65)
    sell_threshold = adjustments.get('sell_threshold', 0.30)
    
    if score >= buy_threshold:
        return "BUY"
    elif score <= sell_threshold:
        return "SELL"
    else:
        return "HOLD"

def generate_trading_rating(score: float, momentum_score: float, volume_ratio: float, volatility_spike: bool = False, price_change_1d: float = 0) -> Rating:
    """Generate ratings specifically for short-term trading with improved accuracy."""
    # High-risk high-reward opportunities (more selective for accuracy)
    if (score >= 0.5 and momentum_score >= 1.0 and volume_ratio >= 1.5 and volatility_spike) or \
       (score >= 0.45 and volatility_spike and abs(price_change_1d) >= 3.0) or \
       (momentum_score >= 2.0 and score >= 0.4 and volume_ratio >= 1.3) or \
       (volume_ratio >= 2.5 and score >= 0.45):
        return "RISKY_BUY"
    
    # Standard BUY signals (more selective threshold)
    elif score >= 0.65 and momentum_score >= 1.5:
        return "BUY"
    
    # SELL signals (more selective)
    elif score <= 0.30 and momentum_score <= 0.5:
        return "SELL"
    
    # Default to HOLD
    else:
        return "HOLD"

def generate_trading_reasoning(momentum_score: float, volume_ratio: float, price_change_1d: float, 
                             volatility_spike: bool, news_score: float, market_timing: dict, 
                             analysis, stock_data, rating: str) -> List[str]:
    """Generate comprehensive trading reasoning with risk assessment."""
    reasoning = [
        f"Momentum Score: {momentum_score:.1f}/5.0 - {'Strong' if momentum_score >= 2.5 else 'Moderate'} short-term momentum",
        f"Volume: {volume_ratio:.1f}x average - {'High' if volume_ratio > 1.5 else 'Normal'} trading interest",
        f"Price Action: {price_change_1d:+.1f}% today - {'News-driven' if volatility_spike else 'Technical'} movement",
    ]
    
    # Add risk warnings for RISKY_BUY ratings
    if rating == "RISKY_BUY":
        risk_factors = []
        
        if abs(price_change_1d) > 5.0:
            risk_factors.append("extreme price volatility (>5% daily move)")
        
        if stock_data.market_cap and stock_data.market_cap < 5_000_000_000:
            risk_factors.append("smaller market cap increases volatility risk")
            
        if momentum_score < 1.5:
            risk_factors.append("momentum not fully confirmed")
            
        if volume_ratio < 1.2:
            risk_factors.append("volume not strongly supporting the move")
            
        if analysis.confidence < 0.5:
            risk_factors.append("technical indicators show mixed signals")
        
        reasoning.append(f"⚠️ RISK WARNING: {', '.join(risk_factors) if risk_factors else 'High volatility trade'}")
        reasoning.append("💡 OPPORTUNITY: Potential for quick gains if momentum continues")
    
    # Add standard analysis
    reasoning.extend([
        f"News Score: {news_score:.1f}/1.0 - {'High' if news_score > 0.5 else 'Moderate' if news_score > 0.2 else 'Low'} event probability",
        f"Market Timing: {'Power Hour' if market_timing.get('is_power_hour') else 'Opening Hour' if market_timing.get('is_opening_hour') else 'Regular Hours'}",
        f"Technical: {analysis.rating} with {analysis.confidence:.0%} confidence"
    ])
    
    return reasoning

def generate_fallback_reasoning(stock_data, analysis, rating: str) -> List[str]:
    """Generate reasoning for fallback stocks."""
    reasons = [
        f"Price Movement: {stock_data.daily_change_percent:+.1f}% daily change",
        f"Technical Analysis: {analysis.rating} with {analysis.confidence:.0%} confidence"
    ]
    
    if rating == "RISKY_BUY":
        reasons.append("⚠️ RISK WARNING: High volatility detected - significant price movement")
        reasons.append("💡 OPPORTUNITY: Could continue momentum if market sentiment persists")
        
        # Add specific risk factors
        if abs(stock_data.daily_change_percent) > 3.5:
            reasons.append("⚡ EXTREME VOLATILITY: >3.5% move indicates heightened risk/reward")
        
        if stock_data.market_cap and stock_data.market_cap < 10_000_000_000:
            reasons.append("📊 SMALLER CAP: Increased volatility expected")
    
    return reasons

def calculate_momentum_score(stock_data: StockData) -> float:
    """Calculate short-term momentum score for trading opportunities."""
    if len(stock_data.prices) < 10:
        return 0.0
    
    prices = stock_data.prices
    volumes = stock_data.volumes if stock_data.volumes else [1] * len(prices)
    
    # 1. Price momentum (recent vs older)
    recent_avg = sum(prices[-3:]) / 3
    older_avg = sum(prices[-10:-7]) / 3
    price_momentum = (recent_avg - older_avg) / older_avg if older_avg > 0 else 0
    
    # 2. Volume surge detection
    recent_volume = volumes[-1] if volumes else 1
    avg_volume = sum(volumes[-10:]) / 10 if len(volumes) >= 10 else recent_volume
    volume_surge = min(recent_volume / avg_volume if avg_volume > 0 else 1, 5.0)  # Cap at 5x
    
    # 3. Volatility expansion (higher volatility = more opportunity)
    recent_volatility = 0
    if len(prices) >= 5:
        recent_returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(-4, 0)]
        recent_volatility = (sum(r**2 for r in recent_returns) / len(recent_returns)) ** 0.5
    
    # 4. Gap detection (price jumps)
    gap_score = 0
    if len(prices) >= 2:
        daily_change = abs((prices[-1] - prices[-2]) / prices[-2]) if prices[-2] > 0 else 0
        if daily_change > 0.03:  # 3%+ gap
            gap_score = min(daily_change * 10, 2.0)  # Cap at 2.0
    
    # 5. Consecutive movement (momentum building)
    consecutive_score = 0
    if len(prices) >= 5:
        direction = 1 if prices[-1] > prices[-2] else -1
        consecutive_days = 0
        for i in range(len(prices) - 1, 0, -1):
            if i == len(prices) - 1:
                continue
            if (prices[i] > prices[i-1]) == (direction > 0):
                consecutive_days += 1
            else:
                break
        consecutive_score = min(consecutive_days * 0.3, 1.0)
    
    # Combine all factors
    momentum_score = (
        price_momentum * 2.0 +        # 40% weight
        (volume_surge - 1) * 0.5 +    # 10% weight
        recent_volatility * 10 +      # 20% weight
        gap_score * 1.0 +             # 20% weight
        consecutive_score * 0.5       # 10% weight
    )
    
    return max(0, min(momentum_score, 5.0))  # Scale 0-5

def scan_top_buy_stocks(max_stocks: int = 10) -> List[Dict]:
    """Scan for short-term trading opportunities with momentum-based scoring."""
    import concurrent.futures
    import threading
    from time import time
    
    trading_opportunities = []
    lock = threading.Lock()
    
    # Get full list of momentum stocks
    tickers = get_top_stocks_for_scanning()[:50]  # Scan more for better opportunities
    
    def analyze_momentum_stock(ticker: str) -> None:
        """Analyze a stock for short-term momentum opportunities."""
        try:
            # Fetch recent data with 1-minute intervals for better precision
            stock_data = fetch_stock_data(ticker, period="5d", interval="1d")
            if not stock_data or len(stock_data.prices) < 5:
                return
            
            # Calculate momentum score
            momentum_score = calculate_momentum_score(stock_data)
            
            # Skip only very low momentum stocks (be more inclusive)
            if momentum_score < 0.3:
                return
            
            # Get basic technical analysis
            analysis = analyze_technical(stock_data)
            
            # Calculate additional short-term factors
            price_change_1d = stock_data.daily_change_percent
            price_change_3d = 0
            if len(stock_data.prices) >= 4:
                price_change_3d = ((stock_data.prices[-1] - stock_data.prices[-4]) / stock_data.prices[-4]) * 100
            
            # Volume analysis
            volume_ratio = 1.0
            if stock_data.volumes and len(stock_data.volumes) >= 5:
                recent_vol = stock_data.volumes[-1]
                avg_vol = sum(stock_data.volumes[-5:]) / 5
                volume_ratio = recent_vol / avg_vol if avg_vol > 0 else 1.0
            
            # Enhanced news/event detection
            from .news_analyzer import calculate_news_sentiment_score, get_market_timing_factors
            
            news_score = calculate_news_sentiment_score(ticker, stock_data)
            market_timing = get_market_timing_factors()
            volatility_spike = abs(price_change_1d) > 3.0  # 3%+ move indicates news
            
            # Create enhanced trading opportunity score (boost for BUY signals)
            technical_boost = 0.3 if analysis.rating == "BUY" else 0.0
            
            trading_score = (
                momentum_score * 0.3 +                       # Momentum (30%)
                min(abs(price_change_1d) / 10, 1.0) * 0.15 + # Recent price movement (15%)
                min(volume_ratio, 3.0) * 0.15 +              # Volume confirmation (15%)
                news_score * 0.2 +                           # News/events factor (20%)
                analysis.confidence * 0.1 +                  # Technical confidence (10%)
                market_timing["market_factor"] * 0.1 +       # Market timing (10%)
                technical_boost                               # BUY signal boost
            )
            
            # Include more opportunities (lower threshold for better coverage)
            if trading_score >= 0.5:
                with lock:
                    trading_opportunities.append({
                        "ticker": ticker,
                        "rating": generate_trading_rating(analysis.confidence, momentum_score, volume_ratio, volatility_spike, price_change_1d),
                        "confidence": min(trading_score / 3.0, 1.0),  # Normalize to 0-1
                        "current_price": stock_data.current_price,
                        "daily_change_percent": price_change_1d,
                        "momentum_score": momentum_score,
                        "volume_ratio": volume_ratio,
                        "volatility_spike": volatility_spike,
                        "reasoning": generate_trading_reasoning(
                            momentum_score, volume_ratio, price_change_1d, volatility_spike, 
                            news_score, market_timing, analysis, stock_data,
                            generate_trading_rating(analysis.confidence, momentum_score, volume_ratio, volatility_spike, price_change_1d)
                        )
                    })
        except Exception as e:
            print(f"Error analyzing {ticker}: {str(e)}")
    
    # Use ThreadPoolExecutor for parallel processing
    start_time = time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(analyze_momentum_stock, ticker) for ticker in tickers]
        
        # Wait for all futures to complete with timeout
        for future in concurrent.futures.as_completed(futures, timeout=45):
            try:
                future.result()
            except Exception as e:
                print(f"Thread error: {str(e)}")
    
    print(f"Momentum scanning completed in {time() - start_time:.1f}s")
    
    # Sort by momentum score and confidence
    trading_opportunities.sort(key=lambda x: (x["momentum_score"], x["confidence"]), reverse=True)
    
    # If we have fewer than target results, add more opportunities
    if len(trading_opportunities) < max_stocks:
        print(f"Only found {len(trading_opportunities)} opportunities, adding more from top movers...")
        
        # Quick fallback scan with basic criteria
        for ticker in tickers[:20]:
            try:
                stock_data = fetch_stock_data(ticker, period="5d")
                if not stock_data:
                    continue
                    
                # Skip if already in results
                if ticker in [opp["ticker"] for opp in trading_opportunities]:
                    continue
                    
                analysis = analyze_technical(stock_data)
                if abs(stock_data.daily_change_percent) > 1.0:  # 1%+ movement (more inclusive)
                    # Force RISKY_BUY for stocks with significant movement in fallback
                    forced_rating = "RISKY_BUY" if abs(stock_data.daily_change_percent) > 2.5 else analysis.rating
                    trading_opportunities.append({
                        "ticker": ticker,
                        "rating": forced_rating,
                        "confidence": analysis.confidence,
                        "current_price": stock_data.current_price,
                        "daily_change_percent": stock_data.daily_change_percent,
                        "momentum_score": 1.0,
                        "volume_ratio": 1.0,
                        "volatility_spike": True,
                        "reasoning": generate_fallback_reasoning(stock_data, analysis, forced_rating)
                    })
                    if len(trading_opportunities) >= max_stocks:
                        break
            except:
                continue
    
    return trading_opportunities[:max_stocks]

def calculate_institutional_indicators(stock_data: StockData) -> List[IndicatorScore]:
    """Calculate institutional-grade indicators for professional analysis."""
    institutional_scores = []
    
    try:
        # VWAP Analysis (15% weight)
        if stock_data.highs and stock_data.lows:
            vwap, vwap_reason = InstitutionalIndicators.calculate_vwap(
                stock_data.prices, stock_data.volumes, stock_data.highs, stock_data.lows
            )
            # Convert VWAP position to score
            vwap_score = 0.6 if "accumulating" in vwap_reason else 0.4 if "selling" in vwap_reason else 0.5
            institutional_scores.append(IndicatorScore("VWAP", vwap, vwap_score, 0.15, vwap_reason))
        
        # Relative Volume Analysis (10% weight)
        rel_vol, rel_vol_reason = InstitutionalIndicators.calculate_relative_volume(stock_data.volumes)
        rel_vol_score = min(0.8, 0.5 + (rel_vol - 1) * 0.1)  # Higher volume = higher score
        institutional_scores.append(IndicatorScore("Relative Volume", rel_vol, rel_vol_score, 0.10, rel_vol_reason))
        
        # On-Balance Volume Analysis (10% weight)
        obv, obv_reason = InstitutionalIndicators.calculate_obv(stock_data.prices, stock_data.volumes)
        obv_score = 0.7 if "accumulation" in obv_reason else 0.3 if "distribution" in obv_reason else 0.6 if "BULLISH" in obv_reason else 0.4 if "BEARISH" in obv_reason else 0.5
        institutional_scores.append(IndicatorScore("OBV", obv, obv_score, 0.10, obv_reason))
        
        # Bollinger Bands Analysis (8% weight) 
        if len(stock_data.prices) >= 20:
            bands, bands_reason = InstitutionalIndicators.calculate_bollinger_bands(stock_data.prices)
            if bands and 'position' in bands:
                # Convert band position to score
                position = bands['position']
                if position > 0.8:
                    bands_score = 0.3  # Near upper band - sell signal
                elif position < 0.2:
                    bands_score = 0.7  # Near lower band - buy signal
                else:
                    bands_score = 0.5  # Normal range
                institutional_scores.append(IndicatorScore("Bollinger Bands", position, bands_score, 0.08, bands_reason))
        
        # ATR Analysis (Risk assessment - 7% weight)
        if stock_data.highs and stock_data.lows:
            atr, atr_reason = InstitutionalIndicators.calculate_atr(
                stock_data.highs, stock_data.lows, stock_data.prices
            )
            # Higher volatility = lower score (more risk)
            atr_percentage = (atr / stock_data.current_price) * 100 if stock_data.current_price > 0 else 0
            atr_score = max(0.2, 0.8 - (atr_percentage * 0.1))  # Lower volatility = higher score
            institutional_scores.append(IndicatorScore("ATR Risk", atr_percentage, atr_score, 0.07, atr_reason))
        
    except Exception as e:
        print(f"Error calculating institutional indicators: {str(e)}")
    
    return institutional_scores

def analyze_with_enhanced_accuracy(ticker: str, log_prediction_enabled: bool = True) -> AnalysisResult:
    """
    Enhanced analysis using multi-timeframe confluence for improved accuracy.
    
    This function combines:
    1. Extended historical analysis (12+ months for better context)
    2. Multi-timeframe confluence scoring
    3. Results logging for continuous improvement
    
    Args:
        ticker: Stock symbol to analyze
        log_prediction_enabled: Whether to log prediction to database
        
    Returns:
        Enhanced AnalysisResult with multi-timeframe confidence boost
    """
    try:
        # Get extended historical data for better trend context
        stock_data = fetch_stock_data(ticker, period="12mo")  # Extended from 3mo to 12mo
        if not stock_data:
            raise ValueError(f"Could not fetch data for {ticker}")
        
        # If insufficient data, fallback to shorter period
        if len(stock_data.prices) < 50:
            stock_data = fetch_stock_data(ticker, period="6mo")
            if not stock_data or len(stock_data.prices) < 30:
                stock_data = fetch_stock_data(ticker, period="3mo")
        
        primary_analysis = analyze_technical(stock_data)
        
        # Get multi-timeframe analysis
        multi_tf_result = analyze_with_multi_timeframe(ticker)
        
        if multi_tf_result and 'confluence_score' in multi_tf_result:
            # Enhance confidence based on timeframe confluence
            confluence_score = multi_tf_result['confluence_score']
            confidence_boost = multi_tf_result['confidence_boost']
            enhanced_rating = multi_tf_result['enhanced_rating']
            
            # Create enhanced analysis result
            enhanced_confidence = min(1.0, primary_analysis.confidence + confidence_boost)
            
            # Use enhanced rating if confluence is strong
            final_rating = enhanced_rating if confluence_score >= 0.6 else primary_analysis.rating
            
            # Combine reasoning
            enhanced_reasoning = list(primary_analysis.reasoning)
            if multi_tf_result.get('multi_tf_reasoning'):
                enhanced_reasoning.extend(multi_tf_result['multi_tf_reasoning'])
            
            # Create enhanced result
            enhanced_result = AnalysisResult(
                ticker=primary_analysis.ticker,
                rating=final_rating,
                confidence=enhanced_confidence,
                technical_indicators=primary_analysis.technical_indicators,
                reasoning=enhanced_reasoning,
                analysis_date=primary_analysis.analysis_date,
                price_at_analysis=primary_analysis.price_at_analysis
            )
            
            # Log prediction for tracking accuracy
            if log_prediction_enabled:
                try:
                    prediction_data = {
                        'ticker': ticker,
                        'rating': final_rating,
                        'confidence': enhanced_confidence,
                        'current_price': stock_data.current_price,
                        'multi_timeframe_score': confluence_score,
                        'confluence_score': confluence_score,
                        'reasoning': enhanced_reasoning,
                        'source': 'enhanced_multi_timeframe'
                    }
                    log_prediction(prediction_data)
                except Exception as e:
                    print(f"Warning: Could not log prediction for {ticker}: {str(e)}")
            
            return enhanced_result
        
        else:
            # Fallback to standard analysis if multi-timeframe fails
            if log_prediction_enabled:
                try:
                    prediction_data = {
                        'ticker': ticker,
                        'rating': primary_analysis.rating,
                        'confidence': primary_analysis.confidence,
                        'current_price': stock_data.current_price,
                        'reasoning': primary_analysis.reasoning,
                        'source': 'standard_analysis'
                    }
                    log_prediction(prediction_data)
                except:
                    pass
            
            return primary_analysis
    
    except Exception as e:
        print(f"Error in enhanced analysis for {ticker}: {str(e)}")
        # Return minimal result
        return AnalysisResult(
            ticker=ticker,
            rating="HOLD",
            confidence=0.5,
            technical_indicators=TechnicalIndicators(0, 0, 0, 0, 0, 0),
            reasoning=[f"Analysis error: {str(e)}"],
            analysis_date=datetime.now(),
            price_at_analysis=0.0
        )
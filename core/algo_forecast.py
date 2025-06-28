"""
Algorithmic Trading Forecast Engine

Predicts how trading algorithms will move stocks based on technical patterns
and algorithmic trading strategies commonly used by institutions.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import statistics
from .models import StockData
from .indicators import calculate_rsi, calculate_sma, calculate_macd


@dataclass
class AlgoForecast:
    """Results from algorithmic trading forecast."""
    forecast_direction: str  # 'UP', 'DOWN', 'SIDEWAYS'
    confidence: float  # 0.0-1.0
    algo_triggers: List[float]  # Price levels where algorithms activate
    reasoning: List[str]  # Detected patterns and logic
    risk_factors: List[str]  # Risk considerations
    pattern_scores: Dict[str, float]  # Individual pattern confidence scores


class AlgorithmicForecast:
    """
    Predicts how trading algorithms will move stocks based on technical patterns.
    """
    
    def __init__(self):
        self.algo_patterns = {
            'mean_reversion': {'weight': 0.3, 'confidence_threshold': 0.2},
            'momentum_breakout': {'weight': 0.4, 'confidence_threshold': 0.25},
            'support_resistance': {'weight': 0.3, 'confidence_threshold': 0.2}
        }
    
    def predict_algorithmic_movements(self, stock_data: StockData) -> AlgoForecast:
        """
        Main prediction function that combines all algorithmic patterns.
        
        Args:
            stock_data: Stock price and volume data
            
        Returns:
            AlgoForecast with comprehensive algorithmic prediction
        """
        if not stock_data.prices or len(stock_data.prices) < 50:
            return AlgoForecast(
                forecast_direction='SIDEWAYS',
                confidence=0.0,
                algo_triggers=[],
                reasoning=['Insufficient data for algorithmic analysis'],
                risk_factors=['Limited historical data'],
                pattern_scores={}
            )
        
        # Detect individual patterns
        mean_reversion = self.detect_mean_reversion_setup(stock_data)
        momentum_breakout = self.detect_momentum_breakout(stock_data)
        support_resistance = self.identify_algo_support_resistance(stock_data)
        
        # Combine pattern scores
        pattern_scores = {
            'mean_reversion': mean_reversion['confidence'],
            'momentum_breakout': momentum_breakout['confidence'],
            'support_resistance': support_resistance['confidence']
        }
        
        # Calculate weighted forecast
        combined_score = 0.0
        total_weight = 0.0
        all_reasoning = []
        all_triggers = []
        all_risks = []
        
        # Mean reversion contribution
        if mean_reversion['confidence'] > self.algo_patterns['mean_reversion']['confidence_threshold']:
            weight = self.algo_patterns['mean_reversion']['weight']
            combined_score += mean_reversion['score'] * weight
            total_weight += weight
            all_reasoning.extend(mean_reversion['reasoning'])
            all_triggers.extend(mean_reversion['triggers'])
            all_risks.extend(mean_reversion['risks'])
        
        # Momentum breakout contribution
        if momentum_breakout['confidence'] > self.algo_patterns['momentum_breakout']['confidence_threshold']:
            weight = self.algo_patterns['momentum_breakout']['weight']
            combined_score += momentum_breakout['score'] * weight
            total_weight += weight
            all_reasoning.extend(momentum_breakout['reasoning'])
            all_triggers.extend(momentum_breakout['triggers'])
            all_risks.extend(momentum_breakout['risks'])
        
        # Support/resistance contribution
        if support_resistance['confidence'] > self.algo_patterns['support_resistance']['confidence_threshold']:
            weight = self.algo_patterns['support_resistance']['weight']
            combined_score += support_resistance['score'] * weight
            total_weight += weight
            all_reasoning.extend(support_resistance['reasoning'])
            all_triggers.extend(support_resistance['triggers'])
            all_risks.extend(support_resistance['risks'])
        
        # Determine final direction and confidence
        if total_weight > 0:
            final_score = combined_score / total_weight
            overall_confidence = total_weight
        else:
            final_score = 0.0
            overall_confidence = 0.0
        
        # Map score to direction (more sensitive thresholds)
        if final_score > 0.05:
            direction = 'UP'
        elif final_score < -0.05:
            direction = 'DOWN'
        else:
            direction = 'SIDEWAYS'
        
        # Remove duplicate triggers and sort
        unique_triggers = sorted(list(set(all_triggers)))
        
        return AlgoForecast(
            forecast_direction=direction,
            confidence=min(overall_confidence, 1.0),
            algo_triggers=unique_triggers,
            reasoning=all_reasoning[:10],  # Limit to top 10 reasons
            risk_factors=list(set(all_risks)),  # Remove duplicates
            pattern_scores=pattern_scores
        )
    
    def detect_mean_reversion_setup(self, stock_data: StockData) -> Dict:
        """
        Detect when algorithms will trigger mean reversion trades.
        
        Conditions:
        - RSI < 30 (oversold) + Bollinger Band lower touch = BUY signal
        - RSI > 70 (overbought) + Bollinger Band upper touch = SELL signal
        - Volume confirmation required
        """
        prices = stock_data.prices[-50:]  # Last 50 periods
        volumes = stock_data.volumes[-50:] if stock_data.volumes else []
        current_price = stock_data.current_price
        
        # Calculate indicators
        rsi = calculate_rsi(prices)
        sma_20 = calculate_sma(prices, 20)
        
        # Calculate Bollinger Bands
        std_dev = statistics.stdev(prices[-20:]) if len(prices) >= 20 else 0
        bollinger_upper = sma_20 + (2 * std_dev)
        bollinger_lower = sma_20 - (2 * std_dev)
        
        # Calculate volume trend
        volume_sma = sum(volumes[-10:]) / 10 if len(volumes) >= 10 else 0
        current_volume = volumes[-1] if volumes else 0
        volume_ratio = current_volume / volume_sma if volume_sma > 0 else 1
        
        reasoning = []
        triggers = []
        risks = []
        score = 0.0
        confidence = 0.0
        
        # Enhanced mean reversion detection with graduated scoring
        
        # Strong oversold setup (RSI < 30)
        if rsi < 30:
            if current_price <= bollinger_lower * 1.02:
                score += 0.4
                confidence += 0.6
                reasoning.append(f"Strong oversold: RSI {rsi:.1f} + price at Bollinger lower (${bollinger_lower:.2f})")
                triggers.append(bollinger_lower)
            else:
                score += 0.2
                confidence += 0.4
                reasoning.append(f"Oversold RSI ({rsi:.1f}) - mean reversion potential")
                
            if volume_ratio > 1.3:
                score += 0.2
                confidence += 0.2
                reasoning.append(f"High volume ({volume_ratio:.1f}x) confirms selling exhaustion")
            elif volume_ratio > 1.1:
                score += 0.1
                confidence += 0.1
                reasoning.append(f"Elevated volume ({volume_ratio:.1f}x) supports reversion")
                
        # Moderate oversold (RSI 30-40)
        elif rsi < 40:
            if current_price <= bollinger_lower * 1.05:
                score += 0.2
                confidence += 0.3
                reasoning.append(f"Moderate oversold: RSI {rsi:.1f} near lower band")
                triggers.append(bollinger_lower)
            else:
                score += 0.1
                confidence += 0.2
                reasoning.append(f"Mild oversold RSI ({rsi:.1f}) - weak reversion signal")
        
        # Strong overbought setup (RSI > 70)
        elif rsi > 70:
            if current_price >= bollinger_upper * 0.98:
                score -= 0.4
                confidence += 0.6
                reasoning.append(f"Strong overbought: RSI {rsi:.1f} + price at Bollinger upper (${bollinger_upper:.2f})")
                triggers.append(bollinger_upper)
            else:
                score -= 0.2
                confidence += 0.4
                reasoning.append(f"Overbought RSI ({rsi:.1f}) - mean reversion potential")
                
            if volume_ratio > 1.3:
                score -= 0.2
                confidence += 0.2
                reasoning.append(f"High volume ({volume_ratio:.1f}x) indicates distribution")
            elif volume_ratio > 1.1:
                score -= 0.1
                confidence += 0.1
                reasoning.append(f"Elevated volume ({volume_ratio:.1f}x) supports reversion")
        
        # Moderate overbought (RSI 60-70)
        elif rsi > 60:
            if current_price >= bollinger_upper * 0.95:
                score -= 0.2
                confidence += 0.3
                reasoning.append(f"Moderate overbought: RSI {rsi:.1f} near upper band")
                triggers.append(bollinger_upper)
            else:
                score -= 0.1
                confidence += 0.2
                reasoning.append(f"Mild overbought RSI ({rsi:.1f}) - weak reversion signal")
        
        # Neutral zone (RSI 40-60)
        else:
            # Still check for Bollinger band extremes
            if current_price <= bollinger_lower * 1.01:
                score += 0.15
                confidence += 0.25
                reasoning.append(f"Price at Bollinger lower band despite neutral RSI ({rsi:.1f})")
                triggers.append(bollinger_lower)
            elif current_price >= bollinger_upper * 0.99:
                score -= 0.15
                confidence += 0.25
                reasoning.append(f"Price at Bollinger upper band despite neutral RSI ({rsi:.1f})")
                triggers.append(bollinger_upper)
            else:
                confidence += 0.1
                reasoning.append(f"RSI in neutral zone ({rsi:.1f}) - minimal mean reversion setup")
        
        # Additional confirmation from price position
        price_position = (current_price - min(prices[-20:])) / (max(prices[-20:]) - min(prices[-20:]))
        if price_position < 0.2 and score > 0:
            score += 0.1
            reasoning.append("Price in bottom 20% of recent range supports reversion")
        elif price_position > 0.8 and score < 0:
            score -= 0.1
            reasoning.append("Price in top 20% of recent range supports reversion")
        
        return {
            'score': score,
            'confidence': confidence,
            'reasoning': reasoning,
            'triggers': triggers,
            'risks': risks
        }
    
    def detect_momentum_breakout(self, stock_data: StockData) -> Dict:
        """
        Enhanced algorithmic momentum breakout detection.
        
        Conditions:
        - MACD histogram momentum shifts + volume confirmation
        - Price breakouts with volume and follow-through
        - Consecutive higher highs/lows patterns
        - RSI momentum confirmation
        """
        prices = stock_data.prices[-50:]
        volumes = stock_data.volumes[-50:] if stock_data.volumes else []
        highs = stock_data.highs[-50:] if stock_data.highs else prices
        lows = stock_data.lows[-50:] if stock_data.lows else prices
        current_price = stock_data.current_price
        
        # Calculate indicators
        macd_line, signal_line, histogram = calculate_macd(prices)
        rsi = calculate_rsi(prices)
        
        # Find resistance/support levels
        resistance_levels = self._find_resistance_levels(highs)
        support_levels = self._find_support_levels(lows)
        
        # Enhanced volume analysis
        volume_sma_20 = sum(volumes[-20:]) / 20 if len(volumes) >= 20 else 1
        volume_sma_5 = sum(volumes[-5:]) / 5 if len(volumes) >= 5 else 1
        current_volume = volumes[-1] if volumes else 1
        
        volume_breakout = current_volume / volume_sma_20 if volume_sma_20 > 0 else 1
        volume_trend = volume_sma_5 / volume_sma_20 if volume_sma_20 > 0 else 1
        
        reasoning = []
        triggers = []
        risks = []
        score = 0.0
        confidence = 0.0
        
        # Enhanced MACD momentum analysis
        if histogram is not None:
            # Strong bullish momentum
            if histogram > 0.1:
                score += 0.3
                confidence += 0.4
                reasoning.append(f"Strong MACD bullish momentum ({histogram:.3f})")
            elif histogram > 0:
                score += 0.2
                confidence += 0.3
                reasoning.append(f"MACD histogram positive ({histogram:.3f}) - building momentum")
            # Bearish momentum
            elif histogram < -0.1:
                score -= 0.2
                confidence += 0.3
                reasoning.append(f"MACD histogram negative ({histogram:.3f}) - bearish momentum")
            elif histogram < 0:
                score -= 0.1
                confidence += 0.2
                reasoning.append(f"MACD histogram slightly negative ({histogram:.3f})")
        
        # RSI momentum confirmation
        if rsi is not None:
            if 50 < rsi < 70 and score > 0:  # RSI in bullish zone but not overbought
                score += 0.15
                confidence += 0.2
                reasoning.append(f"RSI in bullish momentum zone ({rsi:.1f})")
            elif 30 < rsi < 50 and score < 0:  # RSI in bearish zone but not oversold
                score -= 0.15
                confidence += 0.2
                reasoning.append(f"RSI in bearish momentum zone ({rsi:.1f})")
            elif rsi > 70:
                risks.append(f"RSI overbought ({rsi:.1f}) - momentum may stall")
            elif rsi < 30:
                risks.append(f"RSI oversold ({rsi:.1f}) - potential for reversal")
        
        # Price pattern analysis - consecutive higher highs/lows
        if len(prices) >= 10:
            recent_highs = highs[-5:] if len(highs) >= 5 else prices[-5:]
            recent_lows = lows[-5:] if len(lows) >= 5 else prices[-5:]
            
            # Check for ascending highs pattern
            ascending_highs = all(recent_highs[i] >= recent_highs[i-1] for i in range(1, len(recent_highs)))
            ascending_lows = all(recent_lows[i] >= recent_lows[i-1] for i in range(1, len(recent_lows)))
            
            if ascending_highs and ascending_lows:
                score += 0.25
                confidence += 0.3
                reasoning.append("Ascending highs and lows pattern - strong uptrend")
            elif ascending_highs:
                score += 0.15
                confidence += 0.2
                reasoning.append("Ascending highs pattern - building momentum")
            
            # Check for descending pattern
            descending_highs = all(recent_highs[i] <= recent_highs[i-1] for i in range(1, len(recent_highs)))
            descending_lows = all(recent_lows[i] <= recent_lows[i-1] for i in range(1, len(recent_lows)))
            
            if descending_highs and descending_lows:
                score -= 0.25
                confidence += 0.3
                reasoning.append("Descending highs and lows pattern - strong downtrend")
            elif descending_highs:
                score -= 0.15
                confidence += 0.2
                reasoning.append("Descending highs pattern - weakening momentum")
        
        # Enhanced resistance breakout analysis
        for i, resistance in enumerate(resistance_levels[:3]):
            distance_from_resistance = (current_price - resistance) / resistance
            
            if distance_from_resistance > 0.002:  # 0.2% above resistance
                breakout_strength = min(distance_from_resistance * 100, 0.4)  # Cap at 0.4
                score += breakout_strength
                confidence += 0.25
                reasoning.append(f"Resistance breakout at ${resistance:.2f} (+{distance_from_resistance*100:.1f}%)")
                triggers.append(resistance)
                
                # Volume confirmation for breakout
                if volume_breakout > 2.0:
                    score += 0.25
                    confidence += 0.3
                    reasoning.append(f"Strong volume confirmation ({volume_breakout:.1f}x normal)")
                elif volume_breakout > 1.3:
                    score += 0.15
                    confidence += 0.2
                    reasoning.append(f"Good volume confirmation ({volume_breakout:.1f}x normal)")
                else:
                    risks.append(f"Resistance breakout on low volume ({volume_breakout:.1f}x)")
                break
            elif -0.01 < distance_from_resistance <= 0.002:  # Near resistance
                confidence += 0.15
                reasoning.append(f"Approaching resistance at ${resistance:.2f}")
                triggers.append(resistance)
        
        # Support level analysis for downward momentum
        for support in support_levels[:2]:
            distance_from_support = (current_price - support) / support
            
            if distance_from_support < -0.002:  # 0.2% below support
                breakdown_strength = min(abs(distance_from_support) * 100, 0.4)
                score -= breakdown_strength
                confidence += 0.25
                reasoning.append(f"Support breakdown at ${support:.2f} ({distance_from_support*100:.1f}%)")
                triggers.append(support)
                break
        
        # Volume trend analysis
        if volume_trend > 1.3:
            score += 0.1
            confidence += 0.15
            reasoning.append(f"Increasing volume trend ({volume_trend:.1f}x)")
        elif volume_trend < 0.8:
            risks.append(f"Decreasing volume trend ({volume_trend:.1f}x)")
        
        # Momentum acceleration check
        if len(prices) >= 10:
            recent_momentum = (prices[-1] / prices[-5] - 1) * 100  # 5-day momentum
            longer_momentum = (prices[-1] / prices[-10] - 1) * 100  # 10-day momentum
            
            if recent_momentum > longer_momentum * 1.5 and recent_momentum > 2:
                score += 0.2
                confidence += 0.25
                reasoning.append(f"Accelerating momentum ({recent_momentum:.1f}% vs {longer_momentum:.1f}%)")
            elif recent_momentum < longer_momentum * 0.5 and recent_momentum < -2:
                score -= 0.2
                confidence += 0.25
                reasoning.append(f"Decelerating momentum ({recent_momentum:.1f}% vs {longer_momentum:.1f}%)")
        
        # Risk assessment
        if len(prices) >= 20:
            twenty_day_high = max(prices[-20:])
            if current_price > twenty_day_high * 0.98:
                risks.append("Price near 20-day highs - limited upside room")
            
            twenty_day_low = min(prices[-20:])
            if current_price < twenty_day_low * 1.02:
                risks.append("Price near 20-day lows - potential for further decline")
        
        if volume_breakout < 1.1 and abs(score) > 0.2:
            risks.append("Momentum move on low volume - sustainability questionable")
        
        # Ensure minimum confidence for any detected pattern
        if confidence == 0.0 and len(reasoning) == 0:
            confidence = 0.1
            reasoning.append("No clear momentum breakout patterns detected")
        
        return {
            'score': score,
            'confidence': min(confidence, 1.0),  # Cap confidence at 1.0
            'reasoning': reasoning,
            'triggers': triggers,
            'risks': risks
        }
    
    def identify_algo_support_resistance(self, stock_data: StockData) -> Dict:
        """
        Identify price levels where algorithms typically activate.
        
        Levels:
        - VWAP levels
        - Previous day high/low
        - Psychological round numbers
        - Moving average levels
        """
        prices = stock_data.prices[-50:]
        volumes = stock_data.volumes[-50:] if stock_data.volumes else []
        highs = stock_data.highs[-50:] if stock_data.highs else prices
        lows = stock_data.lows[-50:] if stock_data.lows else prices
        current_price = stock_data.current_price
        
        reasoning = []
        triggers = []
        risks = []
        score = 0.0
        confidence = 0.0
        
        # Calculate key levels
        sma_20 = calculate_sma(prices, 20)
        sma_50 = calculate_sma(prices, 50) if len(prices) >= 50 else sma_20
        
        # VWAP calculation
        if volumes:
            vwap = sum(p * v for p, v in zip(prices[-20:], volumes[-20:])) / sum(volumes[-20:])
        else:
            vwap = sma_20
        
        # Find support and resistance levels
        support_levels = self._find_support_levels(lows)
        resistance_levels = self._find_resistance_levels(highs)
        
        # Analyze current position relative to key levels
        levels = {
            'SMA 20': sma_20,
            'SMA 50': sma_50,
            'VWAP': vwap
        }
        
        # Add significant support/resistance levels
        for i, level in enumerate(support_levels[:2]):
            levels[f'Support {i+1}'] = level
        for i, level in enumerate(resistance_levels[:2]):
            levels[f'Resistance {i+1}'] = level
        
        # Analyze proximity to key levels
        for level_name, level_price in levels.items():
            distance_pct = abs(current_price - level_price) / level_price
            
            if distance_pct < 0.02:  # Within 2% of level
                triggers.append(level_price)
                confidence += 0.15
                
                if 'Support' in level_name and current_price > level_price:
                    score += 0.1
                    reasoning.append(f"Price holding above {level_name} (${level_price:.2f})")
                elif 'Resistance' in level_name and current_price < level_price:
                    score -= 0.1
                    reasoning.append(f"Price approaching {level_name} resistance (${level_price:.2f})")
                elif level_name in ['SMA 20', 'SMA 50', 'VWAP']:
                    if current_price > level_price:
                        score += 0.05
                        reasoning.append(f"Price above {level_name} (${level_price:.2f}) - bullish")
                    else:
                        score -= 0.05
                        reasoning.append(f"Price below {level_name} (${level_price:.2f}) - bearish")
        
        # Psychological levels (round numbers)
        round_numbers = self._find_psychological_levels(current_price)
        for round_num in round_numbers:
            distance_pct = abs(current_price - round_num) / round_num
            if distance_pct < 0.01:  # Within 1% of round number
                triggers.append(round_num)
                reasoning.append(f"Near psychological level ${round_num:.0f}")
                confidence += 0.1
        
        # Risk assessment
        if current_price > max(resistance_levels[:2]) if resistance_levels else False:
            risks.append("Price above major resistance - vulnerable to reversal")
        
        if current_price < min(support_levels[:2]) if support_levels else False:
            risks.append("Price below major support - potential for further decline")
        
        if not triggers:
            reasoning.append("No significant algorithmic levels nearby")
            confidence = 0.1
        
        return {
            'score': score,
            'confidence': confidence,
            'reasoning': reasoning,
            'triggers': triggers,
            'risks': risks
        }
    
    def _find_support_levels(self, lows: List[float]) -> List[float]:
        """Enhanced support level detection with strength weighting."""
        if len(lows) < 10:
            return []
        
        support_candidates = []
        window = 3  # Smaller window for more sensitivity
        
        # Find local minima
        for i in range(window, len(lows) - window):
            current_low = lows[i]
            is_local_min = all(current_low <= lows[j] for j in range(i - window, i + window + 1))
            
            if is_local_min:
                # Calculate support strength based on multiple factors
                strength = 0
                
                # Factor 1: Number of tests (touches within 2%)
                tests = sum(1 for price in lows if abs(price - current_low) / current_low < 0.02)
                strength += tests * 10
                
                # Factor 2: Bounce strength after touching support
                bounces_after = []
                for j in range(i + 1, min(i + 10, len(lows))):
                    if abs(lows[j] - current_low) / current_low < 0.02:  # Touched support
                        # Find how much it bounced in next 5 periods
                        bounce_end = min(j + 5, len(lows))
                        max_bounce = max(lows[j:bounce_end]) if j < len(lows) else current_low
                        bounce_pct = (max_bounce - current_low) / current_low
                        bounces_after.append(bounce_pct)
                
                if bounces_after:
                    avg_bounce = sum(bounces_after) / len(bounces_after)
                    strength += avg_bounce * 1000  # Weight bounce strength heavily
                
                # Factor 3: Recency (more recent supports are more relevant)
                recency_factor = (len(lows) - i) / len(lows)
                strength += recency_factor * 20
                
                # Factor 4: Volume at support level (if available)
                # Note: Would need volume data at specific points for this
                
                support_candidates.append((current_low, strength))
        
        # Sort by strength and return top levels
        support_candidates.sort(key=lambda x: x[1], reverse=True)
        
        # Filter out levels too close to each other (within 1%)
        filtered_supports = []
        for level, strength in support_candidates:
            is_unique = True
            for existing_level in filtered_supports:
                if abs(level - existing_level) / existing_level < 0.01:
                    is_unique = False
                    break
            if is_unique:
                filtered_supports.append(level)
        
        return sorted(filtered_supports)[:5]  # Return top 5 support levels
    
    def _find_resistance_levels(self, highs: List[float]) -> List[float]:
        """Enhanced resistance level detection with strength weighting."""
        if len(highs) < 10:
            return []
        
        resistance_candidates = []
        window = 3  # Smaller window for more sensitivity
        
        # Find local maxima
        for i in range(window, len(highs) - window):
            current_high = highs[i]
            is_local_max = all(current_high >= highs[j] for j in range(i - window, i + window + 1))
            
            if is_local_max:
                # Calculate resistance strength based on multiple factors
                strength = 0
                
                # Factor 1: Number of tests (touches within 2%)
                tests = sum(1 for price in highs if abs(price - current_high) / current_high < 0.02)
                strength += tests * 10
                
                # Factor 2: Rejection strength after touching resistance
                rejections_after = []
                for j in range(i + 1, min(i + 10, len(highs))):
                    if abs(highs[j] - current_high) / current_high < 0.02:  # Touched resistance
                        # Find how much it rejected in next 5 periods
                        reject_end = min(j + 5, len(highs))
                        min_reject = min(highs[j:reject_end]) if j < len(highs) else current_high
                        reject_pct = (current_high - min_reject) / current_high
                        rejections_after.append(reject_pct)
                
                if rejections_after:
                    avg_rejection = sum(rejections_after) / len(rejections_after)
                    strength += avg_rejection * 1000  # Weight rejection strength heavily
                
                # Factor 3: Recency (more recent resistance is more relevant)
                recency_factor = (len(highs) - i) / len(highs)
                strength += recency_factor * 20
                
                # Factor 4: Psychological levels get extra weight
                if self._is_psychological_level(current_high):
                    strength += 15
                
                resistance_candidates.append((current_high, strength))
        
        # Sort by strength and return top levels
        resistance_candidates.sort(key=lambda x: x[1], reverse=True)
        
        # Filter out levels too close to each other (within 1%)
        filtered_resistance = []
        for level, strength in resistance_candidates:
            is_unique = True
            for existing_level in filtered_resistance:
                if abs(level - existing_level) / existing_level < 0.01:
                    is_unique = False
                    break
            if is_unique:
                filtered_resistance.append(level)
        
        return sorted(filtered_resistance, reverse=True)[:5]  # Return top 5 resistance levels
    
    def _find_psychological_levels(self, current_price: float) -> List[float]:
        """Find nearby psychological round number levels."""
        psychological_levels = []
        
        # Find round numbers within ±10% of current price
        base_numbers = [1, 5, 10, 25, 50, 100, 250, 500, 1000]
        
        for base in base_numbers:
            # Find the appropriate magnitude
            magnitude = 1
            while base * magnitude < current_price * 0.5:
                magnitude *= 10
            
            while base * magnitude <= current_price * 1.5:
                level = base * magnitude
                if abs(level - current_price) / current_price <= 0.1:  # Within 10%
                    psychological_levels.append(level)
                magnitude *= 10
        
        return sorted(psychological_levels)
    
    def _is_psychological_level(self, price: float) -> bool:
        """Check if a price is near a psychological round number."""
        # Check for round numbers (multiples of 5, 10, 25, 50, 100, etc.)
        round_numbers = [5, 10, 25, 50, 100, 250, 500, 1000]
        
        for base in round_numbers:
            magnitude = 1
            while base * magnitude < price * 0.1:
                magnitude *= 10
            
            while base * magnitude <= price * 10:
                level = base * magnitude
                if abs(price - level) / level < 0.005:  # Within 0.5%
                    return True
                magnitude *= 10
        
        return False
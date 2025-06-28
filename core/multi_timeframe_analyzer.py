#!/usr/bin/env python3
"""
Multi-Timeframe Analysis Module
Improves accuracy by analyzing multiple timeframes and requiring confirmation.
"""

from typing import Dict, List, Tuple, Optional
from datetime import datetime
from .models import StockData, AnalysisResult, TechnicalIndicators
from .data_fetcher import fetch_stock_data
from .indicators import calculate_rsi, calculate_sma, calculate_macd

class MultiTimeframeAnalyzer:
    """
    Analyzes stocks across multiple timeframes for higher confidence signals.
    
    Timeframes used:
    - Daily (primary): Main analysis timeframe
    - 4-hour: Medium-term confirmation  
    - 1-hour: Short-term confirmation
    
    Confluence scoring: Higher confidence when multiple timeframes align.
    """
    
    def __init__(self):
        self.timeframes = {
            'daily': {'period': '3mo', 'interval': '1d', 'weight': 0.5},
            '4h': {'period': '1mo', 'interval': '4h', 'weight': 0.3},
            '1h': {'period': '5d', 'interval': '1h', 'weight': 0.2}
        }
    
    def analyze_multi_timeframe(self, ticker: str) -> Dict:
        """
        Analyze stock across multiple timeframes for enhanced accuracy.
        
        Returns:
            Dict with timeframe analysis, confluence score, and enhanced rating
        """
        timeframe_results = {}
        
        # Analyze each timeframe
        for tf_name, tf_config in self.timeframes.items():
            try:
                stock_data = fetch_stock_data(
                    ticker, 
                    period=tf_config['period'], 
                    interval=tf_config['interval']
                )
                
                if stock_data and len(stock_data.prices) >= 20:
                    # Import here to avoid circular imports
                    from .analyzer import analyze_technical
                    analysis = analyze_technical(stock_data)
                    
                    # Calculate timeframe-specific indicators
                    tf_indicators = self._calculate_timeframe_indicators(stock_data)
                    
                    timeframe_results[tf_name] = {
                        'analysis': analysis,
                        'indicators': tf_indicators,
                        'weight': tf_config['weight'],
                        'trend_strength': self._calculate_trend_strength(stock_data),
                        'momentum_quality': self._assess_momentum_quality(stock_data)
                    }
                    
            except Exception as e:
                print(f"Error analyzing {tf_name} timeframe for {ticker}: {str(e)}")
                continue
        
        # Calculate confluence and enhanced rating
        confluence_analysis = self._calculate_confluence(timeframe_results)
        enhanced_rating = self._generate_enhanced_rating(timeframe_results, confluence_analysis)
        
        return {
            'ticker': ticker,
            'timeframe_results': timeframe_results,
            'confluence_score': confluence_analysis['score'],
            'confluence_analysis': confluence_analysis,
            'enhanced_rating': enhanced_rating,
            'confidence_boost': confluence_analysis['confidence_boost'],
            'primary_analysis': timeframe_results.get('daily', {}).get('analysis'),
            'multi_tf_reasoning': self._generate_multi_tf_reasoning(timeframe_results, confluence_analysis)
        }
    
    def _calculate_timeframe_indicators(self, stock_data: StockData) -> Dict:
        """Calculate indicators specific to this timeframe."""
        if len(stock_data.prices) < 20:
            return {}
        
        # Using Wilder's SMMA RSI for professional compliance
        rsi = calculate_rsi(stock_data.prices)
        sma_20 = calculate_sma(stock_data.prices, 20)
        sma_50 = calculate_sma(stock_data.prices, 50)
        macd, signal, histogram = calculate_macd(stock_data.prices)
        
        # Price position relative to moving averages
        current_price = stock_data.current_price
        price_vs_sma20 = (current_price - sma_20) / sma_20 * 100 if sma_20 > 0 else 0
        price_vs_sma50 = (current_price - sma_50) / sma_50 * 100 if sma_50 > 0 else 0
        
        return {
            'rsi': rsi,
            'sma_20': sma_20,
            'sma_50': sma_50,
            'macd': macd,
            'macd_signal': signal,
            'macd_histogram': histogram,
            'price_vs_sma20': price_vs_sma20,
            'price_vs_sma50': price_vs_sma50,
            'rsi_zone': self._classify_rsi_zone(rsi),
            'macd_zone': self._classify_macd_zone(histogram),
            'trend_zone': self._classify_trend_zone(price_vs_sma20, price_vs_sma50)
        }
    
    def _classify_rsi_zone(self, rsi: float) -> str:
        """Classify RSI into zones for confluence analysis."""
        if rsi >= 70:
            return 'overbought'
        elif rsi >= 60:
            return 'bullish'
        elif rsi >= 40:
            return 'neutral'
        elif rsi >= 30:
            return 'bearish'
        else:
            return 'oversold'
    
    def _classify_macd_zone(self, histogram: float) -> str:
        """Classify MACD histogram for confluence analysis."""
        if histogram > 0.1:
            return 'strong_bullish'
        elif histogram > 0:
            return 'weak_bullish'
        elif histogram > -0.1:
            return 'weak_bearish'
        else:
            return 'strong_bearish'
    
    def _classify_trend_zone(self, price_vs_sma20: float, price_vs_sma50: float) -> str:
        """Classify trend based on price position vs moving averages."""
        if price_vs_sma20 > 2 and price_vs_sma50 > 2:
            return 'strong_uptrend'
        elif price_vs_sma20 > 0 and price_vs_sma50 > 0:
            return 'uptrend'
        elif price_vs_sma20 < -2 and price_vs_sma50 < -2:
            return 'strong_downtrend'
        elif price_vs_sma20 < 0 and price_vs_sma50 < 0:
            return 'downtrend'
        else:
            return 'sideways'
    
    def _calculate_trend_strength(self, stock_data: StockData) -> float:
        """Calculate trend strength (0-1 scale)."""
        if len(stock_data.prices) < 10:
            return 0.5
        
        # Calculate trend consistency
        prices = stock_data.prices[-10:]  # Last 10 periods
        ascending = 0
        descending = 0
        
        for i in range(1, len(prices)):
            if prices[i] > prices[i-1]:
                ascending += 1
            elif prices[i] < prices[i-1]:
                descending += 1
        
        # Trend strength based on consistency
        if ascending > descending:
            return ascending / (len(prices) - 1)
        else:
            return 1 - (descending / (len(prices) - 1))
    
    def _assess_momentum_quality(self, stock_data: StockData) -> str:
        """Assess the quality of momentum (accelerating, stable, weakening)."""
        if len(stock_data.prices) < 6:
            return 'insufficient_data'
        
        # Calculate recent momentum vs older momentum
        recent_momentum = (stock_data.prices[-1] - stock_data.prices[-3]) / stock_data.prices[-3]
        older_momentum = (stock_data.prices[-3] - stock_data.prices[-6]) / stock_data.prices[-6]
        
        if recent_momentum > older_momentum * 1.2:
            return 'accelerating'
        elif recent_momentum > older_momentum * 0.8:
            return 'stable'
        else:
            return 'weakening'
    
    def _calculate_confluence(self, timeframe_results: Dict) -> Dict:
        """Calculate confluence score across timeframes."""
        if not timeframe_results:
            return {'score': 0.5, 'confidence_boost': 0, 'analysis': 'insufficient_data'}
        
        # Convert ratings to numeric scores
        rating_scores = {'BUY': 1.0, 'RISKY_BUY': 0.8, 'HOLD': 0.5, 'SELL': 0.0}
        
        weighted_score = 0
        total_weight = 0
        zone_alignment = {'rsi': [], 'macd': [], 'trend': []}
        
        for tf_name, tf_data in timeframe_results.items():
            if 'analysis' not in tf_data:
                continue
                
            analysis = tf_data['analysis']
            weight = tf_data['weight']
            
            # Add rating score
            rating_score = rating_scores.get(analysis.rating, 0.5)
            weighted_score += rating_score * weight
            total_weight += weight
            
            # Collect zone classifications
            if 'indicators' in tf_data:
                indicators = tf_data['indicators']
                zone_alignment['rsi'].append(indicators.get('rsi_zone', 'neutral'))
                zone_alignment['macd'].append(indicators.get('macd_zone', 'weak_bullish'))
                zone_alignment['trend'].append(indicators.get('trend_zone', 'sideways'))
        
        # Calculate base confluence score
        base_score = weighted_score / total_weight if total_weight > 0 else 0.5
        
        # Calculate zone alignment bonus
        alignment_bonus = self._calculate_zone_alignment_bonus(zone_alignment)
        
        # Calculate trend consistency across timeframes
        trend_consistency = self._calculate_trend_consistency(timeframe_results)
        
        final_score = min(1.0, base_score + alignment_bonus + trend_consistency)
        
        # Calculate confidence boost (how much confluence improves confidence)
        confidence_boost = alignment_bonus + trend_consistency
        
        return {
            'score': final_score,
            'base_score': base_score,
            'alignment_bonus': alignment_bonus,
            'trend_consistency': trend_consistency,
            'confidence_boost': confidence_boost,
            'zone_alignment': zone_alignment,
            'analysis': self._describe_confluence(final_score, alignment_bonus, trend_consistency)
        }
    
    def _calculate_zone_alignment_bonus(self, zone_alignment: Dict) -> float:
        """Calculate bonus for aligned zones across timeframes."""
        bonus = 0
        
        # RSI alignment
        rsi_zones = zone_alignment['rsi']
        if len(set(rsi_zones)) == 1:  # All same zone
            bonus += 0.05
        elif len(set(rsi_zones)) == 2 and len(rsi_zones) >= 2:  # Mostly aligned
            bonus += 0.03
        
        # MACD alignment  
        macd_zones = zone_alignment['macd']
        bullish_macd = ['strong_bullish', 'weak_bullish']
        bearish_macd = ['strong_bearish', 'weak_bearish']
        
        if all(zone in bullish_macd for zone in macd_zones) or all(zone in bearish_macd for zone in macd_zones):
            bonus += 0.05
        
        # Trend alignment
        trend_zones = zone_alignment['trend']
        uptrend_zones = ['strong_uptrend', 'uptrend']
        downtrend_zones = ['strong_downtrend', 'downtrend']
        
        if all(zone in uptrend_zones for zone in trend_zones) or all(zone in downtrend_zones for zone in trend_zones):
            bonus += 0.1  # Trend alignment is most important
        
        return min(0.2, bonus)  # Cap at 20% bonus
    
    def _calculate_trend_consistency(self, timeframe_results: Dict) -> float:
        """Calculate trend consistency across timeframes."""
        trends = []
        for tf_data in timeframe_results.values():
            if 'trend_strength' in tf_data:
                trends.append(tf_data['trend_strength'])
        
        if len(trends) < 2:
            return 0
        
        # If all trends point in same direction (all > 0.5 or all < 0.5)
        if all(t > 0.5 for t in trends) or all(t < 0.5 for t in trends):
            avg_strength = sum(trends) / len(trends)
            return min(0.1, abs(avg_strength - 0.5) * 0.4)  # Up to 10% bonus
        
        return 0
    
    def _describe_confluence(self, score: float, alignment_bonus: float, trend_consistency: float) -> str:
        """Generate human-readable confluence description."""
        if score >= 0.8:
            return "Strong confluence across timeframes"
        elif score >= 0.7:
            return "Good timeframe alignment"
        elif score >= 0.6:
            return "Moderate confluence"
        elif score >= 0.4:
            return "Mixed signals across timeframes"
        else:
            return "Conflicting timeframe signals"
    
    def _generate_enhanced_rating(self, timeframe_results: Dict, confluence_analysis: Dict) -> str:
        """Generate enhanced rating using multi-timeframe confluence."""
        if not timeframe_results:
            return 'HOLD'
        
        # Get primary (daily) analysis
        primary_analysis = timeframe_results.get('daily', {}).get('analysis')
        if not primary_analysis:
            return 'HOLD'
        
        primary_rating = primary_analysis.rating
        confluence_score = confluence_analysis['score']
        confidence_boost = confluence_analysis['confidence_boost']
        
        # Upgrade/downgrade based on confluence
        if confluence_score >= 0.8 and confidence_boost >= 0.15:
            # Strong confluence - can upgrade HOLD to RISKY_BUY in good conditions
            if primary_rating == 'HOLD' and confluence_score >= 0.85:
                return 'RISKY_BUY'
            # Keep strong signals
            elif primary_rating in ['BUY', 'RISKY_BUY']:
                return primary_rating
            elif primary_rating == 'SELL':
                return 'SELL'
        
        elif confluence_score >= 0.6:
            # Good confluence - maintain rating
            return primary_rating
        
        elif confluence_score < 0.4:
            # Poor confluence - downgrade to HOLD for safety
            if primary_rating in ['BUY', 'RISKY_BUY', 'SELL']:
                return 'HOLD'
        
        return primary_rating
    
    def _generate_multi_tf_reasoning(self, timeframe_results: Dict, confluence_analysis: Dict) -> List[str]:
        """Generate reasoning based on multi-timeframe analysis."""
        reasoning = []
        
        if not timeframe_results:
            return ["Multi-timeframe analysis unavailable"]
        
        # Confluence summary
        confluence_score = confluence_analysis['score']
        reasoning.append(f"Multi-timeframe confluence: {confluence_score:.1%} ({confluence_analysis['analysis']})")
        
        # Individual timeframe summaries
        for tf_name, tf_data in timeframe_results.items():
            if 'analysis' not in tf_data:
                continue
                
            analysis = tf_data['analysis']
            indicators = tf_data.get('indicators', {})
            
            tf_summary = f"{tf_name.upper()} timeframe: {analysis.rating}"
            if indicators:
                tf_summary += f" (RSI: {indicators.get('rsi_zone', 'unknown')}, Trend: {indicators.get('trend_zone', 'unknown')})"
            reasoning.append(tf_summary)
        
        # Alignment analysis
        if confluence_analysis['confidence_boost'] >= 0.1:
            reasoning.append("✅ Strong timeframe alignment increases confidence")
        elif confluence_analysis['confidence_boost'] <= -0.05:
            reasoning.append("⚠️ Timeframe conflicts suggest caution")
        
        return reasoning


def analyze_with_multi_timeframe(ticker: str) -> Dict:
    """
    Convenience function to perform multi-timeframe analysis.
    
    Returns enhanced analysis with confluence scoring.
    """
    analyzer = MultiTimeframeAnalyzer()
    return analyzer.analyze_multi_timeframe(ticker)
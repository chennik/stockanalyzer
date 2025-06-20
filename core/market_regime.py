#!/usr/bin/env python3
"""
Market Regime Detection Module - FREE accuracy improvement
Uses VIX data to classify market conditions and adjust analysis accordingly.
"""

import yfinance as yf
from typing import Dict, Optional
from datetime import datetime, timedelta

class MarketRegimeDetector:
    """
    Detects market regimes using free VIX data to improve analysis accuracy.
    
    Market Regimes:
    - BULL: VIX < 20 (low fear, trending markets)
    - BEAR: VIX > 30 (high fear, volatile markets)  
    - NEUTRAL: VIX 20-30 (moderate uncertainty)
    """
    
    def __init__(self):
        self.vix_cache = None
        self.cache_time = None
        self.cache_duration = timedelta(hours=1)  # Cache VIX for 1 hour
    
    def get_current_regime(self) -> Dict:
        """
        Get current market regime based on VIX levels.
        
        Returns:
            Dict with regime classification and confidence adjustments
        """
        try:
            vix_value = self._get_vix_value()
            
            if vix_value is None:
                return self._default_regime()
            
            # Classify regime based on VIX levels
            if vix_value < 16:
                regime = "STRONG_BULL"
                confidence_adj = 0.1  # Higher confidence in trends
                volatility_adj = -0.05  # Lower volatility expected
                description = f"Strong bull market (VIX: {vix_value:.1f}) - Low fear, strong trends expected"
                
            elif vix_value < 20:
                regime = "BULL"
                confidence_adj = 0.05
                volatility_adj = 0.0
                description = f"Bull market (VIX: {vix_value:.1f}) - Moderate optimism, trending likely"
                
            elif vix_value < 25:
                regime = "NEUTRAL"
                confidence_adj = 0.0
                volatility_adj = 0.0
                description = f"Neutral market (VIX: {vix_value:.1f}) - Balanced sentiment, mixed signals"
                
            elif vix_value < 30:
                regime = "BEARISH"
                confidence_adj = -0.03
                volatility_adj = 0.05
                description = f"Bearish market (VIX: {vix_value:.1f}) - Rising fear, caution advised"
                
            else:
                regime = "BEAR"
                confidence_adj = -0.08
                volatility_adj = 0.1
                description = f"Bear market (VIX: {vix_value:.1f}) - High fear, volatile conditions"
            
            return {
                'regime': regime,
                'vix_value': vix_value,
                'confidence_adjustment': confidence_adj,
                'volatility_adjustment': volatility_adj,
                'description': description,
                'rating_adjustments': self._get_rating_adjustments(regime),
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            print(f"Error getting market regime: {str(e)}")
            return self._default_regime()
    
    def _get_vix_value(self) -> Optional[float]:
        """Get current VIX value with caching."""
        now = datetime.now()
        
        # Use cache if recent
        if (self.vix_cache is not None and 
            self.cache_time is not None and 
            now - self.cache_time < self.cache_duration):
            return self.vix_cache
        
        try:
            # Fetch VIX data
            vix = yf.Ticker("^VIX")
            hist = vix.history(period="2d")  # Get recent data
            
            if not hist.empty:
                vix_value = float(hist['Close'].iloc[-1])
                
                # Cache the result
                self.vix_cache = vix_value
                self.cache_time = now
                
                return vix_value
            
        except Exception as e:
            print(f"Error fetching VIX: {str(e)}")
        
        return None
    
    def _default_regime(self) -> Dict:
        """Default regime when VIX data unavailable."""
        return {
            'regime': 'NEUTRAL',
            'vix_value': None,
            'confidence_adjustment': 0.0,
            'volatility_adjustment': 0.0,
            'description': 'Market regime unknown (VIX data unavailable)',
            'rating_adjustments': {'buy_threshold': 0.65, 'sell_threshold': 0.30},
            'timestamp': datetime.now()
        }
    
    def _get_rating_adjustments(self, regime: str) -> Dict:
        """
        Get rating threshold adjustments based on market regime.
        
        Logic:
        - Bull markets: Lower BUY threshold (more opportunities)
        - Bear markets: Higher BUY threshold (more conservative)
        - Volatile markets: Avoid extremes (more HOLD)
        """
        base_buy = 0.65
        base_sell = 0.30
        
        if regime == "STRONG_BULL":
            return {
                'buy_threshold': base_buy - 0.1,  # 0.55 (more opportunities)
                'sell_threshold': base_sell - 0.05,  # 0.25 (less selling)
                'risky_buy_boost': 0.05  # More risk tolerance
            }
            
        elif regime == "BULL":
            return {
                'buy_threshold': base_buy - 0.05,  # 0.60
                'sell_threshold': base_sell,  # 0.30
                'risky_buy_boost': 0.02
            }
            
        elif regime == "NEUTRAL":
            return {
                'buy_threshold': base_buy,  # 0.65 (baseline)
                'sell_threshold': base_sell,  # 0.30
                'risky_buy_boost': 0.0
            }
            
        elif regime == "BEARISH":
            return {
                'buy_threshold': base_buy + 0.05,  # 0.70 (more conservative)
                'sell_threshold': base_sell + 0.05,  # 0.35 (easier selling)
                'risky_buy_boost': -0.03  # Less risk tolerance
            }
            
        else:  # BEAR
            return {
                'buy_threshold': base_buy + 0.1,  # 0.75 (very conservative)
                'sell_threshold': base_sell + 0.1,  # 0.40 (more selling)
                'risky_buy_boost': -0.05  # Avoid risky trades
            }
    
    def apply_regime_adjustments(self, base_score: float, regime_data: Dict) -> float:
        """Apply market regime adjustments to analysis score."""
        adjusted_score = base_score + regime_data['confidence_adjustment']
        
        # Add volatility-based adjustments
        if regime_data['regime'] in ['BEAR', 'BEARISH']:
            # In volatile markets, pull scores toward neutral (HOLD)
            adjusted_score = adjusted_score * 0.9 + 0.5 * 0.1
        
        return max(0.1, min(0.9, adjusted_score))


# Global instance for easy access
_regime_detector = None

def get_market_regime() -> Dict:
    """Get current market regime (singleton pattern)."""
    global _regime_detector
    if _regime_detector is None:
        _regime_detector = MarketRegimeDetector()
    return _regime_detector.get_current_regime()

def apply_market_regime_adjustments(score: float) -> tuple[float, str]:
    """Apply market regime adjustments to analysis score."""
    regime_data = get_market_regime()
    
    if not regime_data or regime_data['regime'] == 'NEUTRAL':
        return score, ""
    
    global _regime_detector
    if _regime_detector is None:
        _regime_detector = MarketRegimeDetector()
    
    adjusted_score = _regime_detector.apply_regime_adjustments(score, regime_data)
    
    # Generate explanation
    regime_explanation = f"Market regime: {regime_data['description']}"
    
    return adjusted_score, regime_explanation
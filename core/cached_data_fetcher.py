"""Cached data fetcher with retry logic and rate limit handling."""
import yfinance as yf
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import time
import json
import os
from functools import lru_cache
from .models import StockData
from .data_fetcher import fetch_stock_data

class CachedDataFetcher:
    """Data fetcher with caching and retry capabilities."""
    
    def __init__(self, cache_dir: str = ".cache/stock_data"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        self._memory_cache = {}
        self._last_api_call = 0
        self._min_call_interval = 0.2  # 200ms between calls
        
    def _get_cache_path(self, ticker: str, period: str) -> str:
        """Get cache file path for a ticker."""
        today = datetime.now().strftime("%Y%m%d")
        return os.path.join(self.cache_dir, f"{ticker}_{period}_{today}.json")
    
    def _load_from_cache(self, ticker: str, period: str) -> Optional[Dict]:
        """Load data from cache if available and fresh."""
        cache_path = self._get_cache_path(ticker, period)
        
        # Check memory cache first
        cache_key = f"{ticker}_{period}"
        if cache_key in self._memory_cache:
            cached_time = self._memory_cache[cache_key].get('timestamp', 0)
            if time.time() - cached_time < 300:  # 5 minutes
                return self._memory_cache[cache_key]['data']
        
        # Check file cache
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r') as f:
                    cached_data = json.load(f)
                    cached_time = cached_data.get('timestamp', 0)
                    # Cache valid for 1 hour
                    if time.time() - cached_time < 3600:
                        self._memory_cache[cache_key] = cached_data
                        return cached_data['data']
            except:
                pass
        
        return None
    
    def _save_to_cache(self, ticker: str, period: str, data: Dict):
        """Save data to cache."""
        cache_path = self._get_cache_path(ticker, period)
        cache_key = f"{ticker}_{period}"
        
        cache_data = {
            'timestamp': time.time(),
            'data': data
        }
        
        # Save to memory cache
        self._memory_cache[cache_key] = cache_data
        
        # Save to file cache
        try:
            with open(cache_path, 'w') as f:
                json.dump(cache_data, f)
        except:
            pass
    
    def _rate_limit_wait(self):
        """Wait if necessary to respect rate limits."""
        elapsed = time.time() - self._last_api_call
        if elapsed < self._min_call_interval:
            time.sleep(self._min_call_interval - elapsed)
        self._last_api_call = time.time()
    
    def fetch_with_retry(self, ticker: str, period: str = "3mo", max_retries: int = 3) -> Optional[StockData]:
        """Fetch stock data with caching and retry logic."""
        
        # Check cache first
        cached_data = self._load_from_cache(ticker, period)
        if cached_data:
            try:
                # Convert cached dict back to StockData
                return StockData(
                    ticker=cached_data['ticker'],
                    prices=cached_data['prices'],
                    volumes=cached_data['volumes'],
                    dates=[datetime.fromisoformat(d) for d in cached_data['dates']],
                    current_price=cached_data['current_price'],
                    daily_change=cached_data['daily_change'],
                    daily_change_percent=cached_data['daily_change_percent'],
                    market_cap=cached_data.get('market_cap'),
                    pe_ratio=cached_data.get('pe_ratio'),
                    highs=cached_data.get('highs', cached_data['prices']),
                    lows=cached_data.get('lows', cached_data['prices'])
                )
            except Exception as e:
                print(f"Cache conversion error for {ticker}: {e}")
        
        # If not in cache, fetch with retry logic
        for attempt in range(max_retries):
            try:
                # Rate limit protection
                self._rate_limit_wait()
                
                # Try to fetch
                result = fetch_stock_data(ticker, period)
                
                if result:
                    # Cache the result
                    cache_data = {
                        'ticker': result.ticker,
                        'prices': result.prices,
                        'volumes': result.volumes,
                        'dates': [d.isoformat() for d in result.dates],
                        'current_price': result.current_price,
                        'daily_change': result.daily_change,
                        'daily_change_percent': result.daily_change_percent,
                        'market_cap': result.market_cap,
                        'pe_ratio': result.pe_ratio,
                        'highs': result.highs,
                        'lows': result.lows
                    }
                    self._save_to_cache(ticker, period, cache_data)
                    return result
                
            except Exception as e:
                error_msg = str(e).lower()
                if 'rate limit' in error_msg or '401' in error_msg or 'too many' in error_msg:
                    # Exponential backoff for rate limits
                    wait_time = 2 ** attempt
                    print(f"Rate limited on {ticker}, waiting {wait_time}s...")
                    time.sleep(wait_time)
                elif attempt == max_retries - 1:
                    print(f"Failed to fetch {ticker} after {max_retries} attempts: {e}")
                    return None
                else:
                    time.sleep(0.5)  # Small delay between retries
        
        return None

# Global instance
_cached_fetcher = CachedDataFetcher()

def fetch_stock_data_cached(ticker: str, period: str = "3mo") -> Optional[StockData]:
    """Convenience function to fetch with caching."""
    return _cached_fetcher.fetch_with_retry(ticker, period)